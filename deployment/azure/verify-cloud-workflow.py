"""Real Azure HTTPS workflow using only an invented demonstration case."""

import json
import time
import uuid
from pathlib import Path

import httpx


ROOT = Path("artifacts/azure-preflight")
SECRETS = ROOT / "cloud-private"
BASE = "https://frontend.whiteflower-9d03c62c.southeastasia.azurecontainerapps.io"
API = BASE + "/api/v1"
RELEASE = "65f2302cc9c4795142567296cc6b16143fad5abfe4df7b04152975748c2ec271"


def require(response: httpx.Response, status: int, label: str) -> dict:
    if response.status_code != status:
        raise AssertionError(f"{label}: HTTP {response.status_code}, expected {status}")
    return response.json() if response.content else {}


def main() -> None:
    engineer = (SECRETS / "engineer.token").read_text(encoding="ascii").strip()
    reviewer = (SECRETS / "reviewer.token").read_text(encoding="ascii").strip()
    with httpx.Client(timeout=60, follow_redirects=False) as client:
        home = client.get(BASE + "/")
        assert home.status_code == 200 and home.url.scheme == "https"
        for name in ("api", "mlflow"):
            direct = client.get(
                f"https://{name}.whiteflower-9d03c62c.southeastasia.azurecontainerapps.io/api/v1/health/live"
            )
            assert direct.status_code == 404, f"{name} public HTTP {direct.status_code}"
        for _attempt in range(8):
            live = client.get(API + "/health/live")
            ready = client.get(API + "/health/ready") if live.status_code == 200 else None
            if live.status_code == 200 and ready is not None and ready.status_code == 200:
                break
            time.sleep(5)
        else:
            raise AssertionError("liveness/readiness did not recover after cold start")
        assert client.get(API + "/analyses").status_code == 401
        h = {"Authorization": "Bearer " + engineer}
        rh = {"Authorization": "Bearer " + reviewer}
        require(client.get(API + "/analyses/schema", headers=h), 200, "intake schema")
        assert client.get(API + "/admin/model-versions", headers=h).status_code == 403
        inputs = {
            "admission_type_id": "2",
            "admission_source_id": "7",
            "time_in_hospital": 5,
            "num_lab_procedures": 45,
            "num_procedures": 2,
            "num_medications": 15,
            "number_outpatient": 1,
            "number_emergency": 1,
            "number_inpatient": 2,
            "number_diagnoses": 6,
            "max_glu_serum": "Norm",
            "A1Cresult": ">7",
            "diabetesMed": "Yes",
        }
        body = {"schema_version": "case-input-v1", "model_version": "1", "inputs": inputs}
        post = {**h, "Idempotency-Key": str(uuid.uuid4())}
        original = require(client.post(API + "/analyses", headers=post, json=body), 201, "prediction")["data"]
        assert 0 <= original["probability"] <= 1
        assert original["release_sha256"] == RELEASE
        assert original["inputs"]["number_inpatient"] == "2"
        prediction_id = original["prediction_id"]
        saved = require(client.post(API + f"/analyses/{prediction_id}/save", headers=h, json={}), 200, "save")["data"]
        assert saved["saved"] and saved["save_event_id"] != original["event_id"]
        history = require(client.get(API + "/analyses", headers=h), 200, "history")["data"]
        assert any(item["prediction_id"] == prediction_id for item in history["items"])
        reopened = require(client.get(API + f"/analyses/{prediction_id}", headers=h), 200, "reopen")["data"]
        assert reopened == saved
        changed = dict(inputs, number_inpatient=4)
        rerun = require(
            client.post(
                API + "/analyses",
                headers={**h, "Idempotency-Key": str(uuid.uuid4())},
                json={**body, "inputs": changed},
            ),
            201,
            "changed rerun",
        )["data"]
        assert rerun["prediction_id"] != prediction_id and rerun["event_id"] != original["event_id"]
        immutable = require(client.get(API + f"/analyses/{prediction_id}", headers=h), 200, "original unchanged")["data"]
        assert immutable == saved
        review = require(
            client.post(
                API + f"/predictions/{prediction_id}/reviews",
                headers={**rh, "Idempotency-Key": str(uuid.uuid4())},
                json={
                    "schema_version": "application-v1",
                    "decision": "acknowledged",
                    "reason_code": "evidence_reviewed",
                    "expected_revision": 0,
                },
            ),
            201,
            "review",
        )["data"]
        assert review["revision"] == 1
        audits = require(client.get(API + "/audit-events", headers=h), 200, "audit history")["data"]
        assert any(event["event_type"] == "prediction_created" for event in audits["items"])
        assert any(event["event_type"] == "prediction_saved" for event in audits["items"])
        result = {
            "frontend_https": 200,
            "direct_api_public": 404,
            "direct_mlflow_public": 404,
            "liveness": 200,
            "readiness": 200,
            "unauthenticated_history": 401,
            "engineer_admin_route": 403,
            "prediction_id": prediction_id,
            "prediction_probability": original["probability"],
            "model_sha256": original["model_sha256"],
            "release_sha256": original["release_sha256"],
            "evidence_sha256": original["evidence_sha256"],
            "saved": saved["saved"],
            "reopened": True,
            "rerun_id": rerun["prediction_id"],
            "original_unchanged": True,
            "review_revision": review["revision"],
            "audit_events_visible": len(audits["items"]),
        }
        (ROOT / "cloud-workflow.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
