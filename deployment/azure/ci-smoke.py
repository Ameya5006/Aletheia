"""Synthetic authenticated public-URL smoke run inside the no-ingress operator."""

import time
import uuid
from datetime import UTC, datetime
from pathlib import Path

import httpx
import jwt
from cryptography.hazmat.primitives import serialization


ORIGIN = "https://frontend.whiteflower-9d03c62c.southeastasia.azurecontainerapps.io"
API = ORIGIN + "/api/v1"
RELEASE = "65f2302cc9c4795142567296cc6b16143fad5abfe4df7b04152975748c2ec271"
MODEL = "8c3a99dd8dfe20d2a3a0a721637b4be500ee1b32843f7cefc3af265f07262f7a"
EVIDENCE = "2d073fa0d0bbbd4debfdf445cd80ec478fef0f7098c7ef356dbb3edd28894ea8"


def engineer_headers() -> dict[str, str]:
    key = serialization.load_pem_private_key(
        Path("/run/secrets/smoke_signing_key.pem").read_bytes(), password=None
    )
    now = int(datetime.now(UTC).timestamp())
    token = jwt.encode(
        {
            "iss": ORIGIN,
            "sub": "synthetic-engineer",
            "aud": "aletheia-api",
            "iat": now,
            "exp": now + 840,
            "roles": ["engineer"],
            "token_use": "access",
        },
        key,
        algorithm="RS256",
        headers={"kid": "azure-showcase-20261018", "typ": "at+jwt"},
    )
    return {"Authorization": "Bearer " + token}


def main() -> None:
    with httpx.Client(timeout=60, follow_redirects=False) as client:
        assert client.get(ORIGIN + "/").status_code == 200
        for _attempt in range(6):
            if client.get(API + "/health/ready").status_code == 200:
                break
            time.sleep(5)
        else:
            raise AssertionError("API readiness after cold start")
        for name, endpoint in (
            ("api", "http://api/api/v1/health/live"),
            ("mlflow", "http://mlflow/health"),
        ):
            assert client.get(endpoint).status_code == 200, f"internal {name} health"
        assert client.get(API + "/analyses").status_code == 401
        headers = engineer_headers()
        assert client.get(API + "/admin/model-versions", headers=headers).status_code == 403
        payload = {
            "schema_version": "case-input-v1",
            "model_version": "1",
            "inputs": {
                "admission_type_id": "2", "admission_source_id": "7",
                "time_in_hospital": 5, "num_lab_procedures": 45,
                "num_procedures": 2, "num_medications": 15,
                "number_outpatient": 1, "number_emergency": 1,
                "number_inpatient": 2, "number_diagnoses": 6,
                "max_glu_serum": "Norm", "A1Cresult": ">7",
                "diabetesMed": "Yes",
            },
        }
        response = client.post(
            API + "/analyses",
            headers={**headers, "Idempotency-Key": str(uuid.uuid4())},
            json=payload,
        )
        assert response.status_code == 201, f"prediction HTTP {response.status_code}"
        result = response.json()["data"]
        assert result["release_sha256"] == RELEASE
        assert result["model_sha256"] == MODEL
        assert result["evidence_sha256"] == EVIDENCE
        assert 0 <= result["probability"] <= 1
        prediction_id = result["prediction_id"]
        saved = client.post(API + f"/analyses/{prediction_id}/save", headers=headers, json={})
        assert saved.status_code == 200 and saved.json()["data"]["saved"]
        reopened = client.get(API + f"/analyses/{prediction_id}", headers=headers)
        assert reopened.status_code == 200 and reopened.json()["data"]["saved"]
        history = client.get(API + "/analyses", headers=headers)
        assert history.status_code == 200
        assert any(row["prediction_id"] == prediction_id for row in history.json()["data"]["items"])
        audit = client.get(API + "/audit-events?limit=100", headers=headers)
        assert audit.status_code == 200
        assert any(row["event_type"] == "prediction_saved" for row in audit.json()["data"]["items"])
        print(f"smoke prediction saved and audited: probability={result['probability']:.12f}; internal health=200")


if __name__ == "__main__":
    main()
