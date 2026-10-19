"""Check previously saved synthetic Azure rows after restart or zero replicas."""

import argparse
import json
import time
from pathlib import Path

import httpx


ROOT = Path("artifacts/azure-preflight")
BASE = "https://frontend.whiteflower-9d03c62c.southeastasia.azurecontainerapps.io/api/v1"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("phase", choices=("restart", "scale-zero"))
    phase = parser.parse_args().phase
    reference = json.loads((ROOT / "cloud-workflow.json").read_text(encoding="utf-8"))
    browser = json.loads((ROOT / "cloud-browser.json").read_text(encoding="utf-8"))
    token = (ROOT / "cloud-private/engineer.token").read_text(encoding="ascii").strip()
    headers = {"Authorization": "Bearer " + token}
    with httpx.Client(timeout=60) as client:
        attempts = []
        for _ in range(5):
            ready = client.get(BASE + "/health/ready")
            attempts.append(ready.status_code)
            if ready.status_code == 200:
                break
            time.sleep(5)
        assert attempts[-1] == 200, f"readiness after {phase}: {attempts}"
        persisted = []
        for prediction_id, probability in (
            (reference["prediction_id"], reference["prediction_probability"]),
            (browser["original_prediction_id"], browser["probability"]),
        ):
            response = client.get(BASE + "/analyses/" + prediction_id, headers=headers)
            assert response.status_code == 200, f"persisted record HTTP {response.status_code}"
            row = response.json()["data"]
            assert row["saved"] and row["probability"] == probability
            persisted.append(prediction_id)
        history = client.get(BASE + "/analyses", headers=headers)
        assert history.status_code == 200
        history_ids = {item["prediction_id"] for item in history.json()["data"]["items"]}
        assert set(persisted).issubset(history_ids)
        audit = client.get(BASE + "/audit-events?limit=100", headers=headers)
        assert audit.status_code == 200
        events = audit.json()["data"]["items"]
        assert any(item["event_type"] == "prediction_created" for item in events)
        assert any(item["event_type"] == "prediction_saved" for item in events)
        result = {"phase": phase, "readiness_attempts": attempts, "persisted_prediction_ids": persisted,
                  "history_contains_both": True, "audit_event_count_visible": len(events)}
        (ROOT / f"cloud-persistence-{phase}.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
