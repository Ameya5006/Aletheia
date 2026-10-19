"""The hosted controller must bound log reads and disclose no raw credentials."""

import importlib.util
import subprocess
from pathlib import Path
from types import SimpleNamespace

SPEC = importlib.util.spec_from_file_location(
    "ci_log_marker",
    Path(__file__).resolve().parents[2] / "deployment/azure/ci-log-marker.py",
)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_completed_smoke_emits_only_marker_and_probability():
    output = (
        "unnecessary raw log\n"
        "smoke prediction saved and audited: probability=0.165468722464; "
        "private apps=404\n"
        "aletheia-smoke-complete"
    )
    result = MODULE.observe(
        "Smoke", lambda *a, **k: SimpleNamespace(returncode=0, stdout=output, stderr="")
    )
    assert result == {"status": "complete", "probability": 0.165468722464}


def test_authorization_error_reports_action_without_raw_identifiers():
    error = (
        "AuthorizationFailed: client do-not-disclose lacks "
        "Microsoft.App/containerApps/getAuthToken/action"
    )
    result = MODULE.observe(
        "Migration",
        lambda *a, **k: SimpleNamespace(returncode=1, stdout="", stderr=error),
    )
    assert result == {
        "status": "authorization_denied",
        "actions": ["Microsoft.App/containerApps/getAuthToken/action"],
    }


def test_credential_like_logs_fail_closed_without_content():
    output = "-----BEGIN " + "PRIVATE KEY-----\nnever-disclose\naletheia-smoke-complete"
    result = MODULE.observe(
        "Smoke", lambda *a, **k: SimpleNamespace(returncode=0, stdout=output, stderr="")
    )
    assert result == {"status": "credential_exposure"}


def test_log_read_has_a_finite_timeout():
    def timeout(*args, **kwargs):
        assert kwargs["timeout"] == 30
        raise subprocess.TimeoutExpired("az", 30)

    assert MODULE.observe("Migration", timeout) == {"status": "timeout"}
