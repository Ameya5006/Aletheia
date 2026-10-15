"""Bounded real Compose E2E; synthetic IDs only, no research runners or raw data."""

import json
import os
import subprocess
import time
import uuid
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[2]
LOCAL = ROOT / os.environ.get("ALETHEIA_LOCAL", "artifacts/stage3-local")
EVIDENCE = ROOT / os.environ.get("ALETHEIA_EVIDENCE", "artifacts/stage3-verification")
COMPOSE = [
    "docker",
    "compose",
    "--env-file",
    str(LOCAL / "config.env"),
    "-f",
    "deployment/compose.yaml",
    "-f",
    "deployment/compose.test.yaml",
    "--profile",
    "test",
    "--profile",
    "operator",
]
BASE = "http://127.0.0.1:18080"


def compose(*args):
    result = subprocess.run(
        [*COMPOSE, *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=360,
    )
    if result.returncode:
        # URLs/passwords/tokens are never command arguments in this harness.
        path = EVIDENCE / ("compose-failure-" + uuid.uuid4().hex + ".log")
        path.write_text(result.stdout + result.stderr, encoding="utf-8")
        raise RuntimeError(f"Compose {args[0]} failed; inspect {path.name}")
    return result.stdout


def operator(*args):
    return compose("run", "--rm", "--no-deps", "release-import", "operator", *args)


def refresh():
    subprocess.run(
        [
            str(ROOT / ".venv/Scripts/python.exe"),
            "deployment/tests/prepare.py",
            "--tokens",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
    )


def headers(role, key=None):
    value = {
        "Authorization": "Bearer " + (LOCAL / f"secrets/{role}_token").read_text(),
    }
    if key:
        value["Idempotency-Key"] = str(key)
    return value


def wait_ready(client, expected=200):
    for _ in range(60):
        try:
            response = client.get(BASE + "/api/v1/health/ready")
            if response.status_code == expected:
                return response
        except httpx.HTTPError:
            pass
        time.sleep(1)
    raise AssertionError(f"readiness did not reach {expected}")


def run():
    import sys

    refresh()
    if "--checks-only" not in sys.argv:
        if "--resume" not in sys.argv:
            operator("bootstrap-initial-administrator")
        operator("import-release", "--tracking-uri", "http://mlflow:5000")
        for action in ("approve-release", "activate-release"):
            operator(
                action,
                "--tracking-uri",
                "http://mlflow:5000",
                "--token-file",
                "/run/secrets/operator_token",
            )
        for role in ("engineer", "reviewer"):
            operator(
                "grant-role",
                "--token-file",
                "/run/secrets/operator_token",
                "--issuer",
                "https://identity.test:8443",
                "--subject",
                "synthetic-" + role,
                "--role",
                role,
            )
    checks = []
    with httpx.Client(timeout=15, trust_env=False) as client:
        wait_ready(client)
        for path in (
            "health/live",
            "models/current",
            "models/current/card",
            "demo/cases",
            "explanations/global",
            "explanations/local/synthetic-discharge-v1",
            "audits/stability",
            "audits/subgroups",
            "counterfactuals/feasibility",
        ):
            response = client.get(BASE + "/api/v1/" + path)
            assert response.status_code == 200, path
        checks.append("readiness and nine public endpoints")
        response = client.get(BASE + "/evidence/subgroups")
        assert response.status_code == 200 and '<div id="root"' in response.text
        for name in (
            "content-security-policy",
            "x-content-type-options",
            "x-frame-options",
            "referrer-policy",
            "permissions-policy",
        ):
            assert name in response.headers, name
        assert "strict-transport-security" not in response.headers
        checks.append("SPA fallback and HTTP security headers; no HTTP HSTS")
        body = {
            "schema_version": "application-v1",
            "case_id": "synthetic-discharge-v1",
            "model_version": "1",
        }
        key = uuid.uuid4()
        first = client.post(
            BASE + "/api/v1/predictions", json=body, headers=headers("engineer", key)
        )
        assert first.status_code == 201, first.status_code
        prediction = first.json()["data"]
        retry = client.post(
            BASE + "/api/v1/predictions", json=body, headers=headers("engineer", key)
        )
        assert retry.status_code == 201 and retry.json()["data"] == prediction
        pid = prediction["prediction_id"]
        assert (
            client.get(
                BASE + f"/api/v1/predictions/{pid}", headers=headers("engineer")
            ).json()["data"]
            == prediction
        )
        review = {
            "schema_version": "application-v1",
            "decision": "acknowledged",
            "reason_code": "evidence_reviewed",
            "expected_revision": 0,
        }
        url = BASE + f"/api/v1/predictions/{pid}/reviews"
        denied = client.post(
            url, json=review, headers=headers("engineer", uuid.uuid4())
        )
        assert denied.status_code == 403
        reviewed = client.post(
            url, json=review, headers=headers("reviewer", uuid.uuid4())
        )
        assert reviewed.status_code == 201
        rid = reviewed.json()["data"]["review_id"]
        event = reviewed.json()["data"]["event_id"]
        assert (
            client.get(
                BASE + "/api/v1/audit-events/" + event, headers=headers("reviewer")
            ).status_code
            == 200
        )
        assert (
            client.get(
                BASE + "/api/v1/admin/model-versions", headers=headers("administrator")
            ).status_code
            == 200
        )
        assert (
            client.get(
                BASE + "/api/v1/admin/model-versions", headers=headers("engineer")
            ).status_code
            == 403
        )
        assert client.post(BASE + "/api/v1/predictions", json=body).status_code == 401
        bad = dict(body, case_id="arbitrary-patient", patient_nbr="refused")
        assert (
            client.post(
                BASE + "/api/v1/predictions",
                json=bad,
                headers=headers("engineer", uuid.uuid4()),
            ).status_code
            == 422
        )
        checks.append(
            "persisted prediction, idempotency, reviewer/audit linkage and RBAC"
        )
        compose("stop", "mlflow")
        wait_ready(client)
        result = client.post(
            BASE + "/api/v1/predictions",
            json=body,
            headers=headers("engineer", uuid.uuid4()),
        )
        assert result.status_code == 201
        compose("start", "mlflow")
        checks.append("verified pinned serving during MLflow outage")
        compose("stop", "postgres")
        wait_ready(client, 503)
        result = client.post(
            BASE + "/api/v1/predictions",
            json=body,
            headers=headers("engineer", uuid.uuid4()),
        )
        assert result.status_code == 503
        compose("start", "postgres")
        wait_ready(client)
        checks.append("PostgreSQL outage fails closed and recovers")
        compose("stop", "api")
        try:
            # DNS refusal gives 502; a cached address timing out gives 504.
            assert client.get(BASE + "/api/v1/models/current").status_code in {502, 504}
            assert client.get(BASE + "/").status_code == 200
        finally:
            compose("start", "api")
        wait_ready(client)
        assert (
            client.get(
                BASE + f"/api/v1/predictions/{pid}", headers=headers("engineer")
            ).status_code
            == 200
        )
        checks.append(
            "API outage preserves static UI; restart preserves committed data"
        )
    EVIDENCE.mkdir(exist_ok=True)
    (EVIDENCE / "e2e.json").write_text(
        json.dumps(
            {
                "passed": checks,
                "prediction_id": pid,
                "review_id": rid,
                "review_event_id": event,
            },
            indent=2,
        )
    )
    print(json.dumps({"passed": checks}))


if __name__ == "__main__":
    run()
