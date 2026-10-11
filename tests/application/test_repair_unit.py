"""Portable locks and strict operator endpoint trust boundaries."""

import importlib.metadata
from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread
from types import SimpleNamespace

import pytest
from mlflow.exceptions import MlflowException
from packaging.requirements import Requirement
from pydantic import ValidationError

from aletheia.application.config import TrustedMLflowEndpoint
from aletheia.application.registry import Registry
from aletheia.application.release import (
    ReleaseError,
    durable_json,
    locked_requirements,
    verify_dependencies,
)


@pytest.mark.parametrize(
    "boundary",
    [
        "download",
        "receipt_before",
        "receipt_after",
        "run_finish",
        "run_tag",
        "version_tag",
        "alias",
    ],
)
def test_verifying_import_recovers_same_identity_after_crash(
    release, tmp_path, monkeypatch, boundary
):
    import aletheia.application.registry as module

    registry = Registry("http://127.0.0.1:5000", tmp_path / "receipts")
    result = {
        "name": module.NAME,
        "version": "1",
        "run_id": "synthetic-import",
        "release_sha256": release.digest,
        "package_sha256": "a" * 64,
    }
    mv = SimpleNamespace(
        version="1",
        run_id=result["run_id"],
        tags={
            "import_state": "verifying",
            "package_sha256": result["package_sha256"],
            "release_sha256": release.digest,
        },
    )
    run = SimpleNamespace(
        info=SimpleNamespace(status="RUNNING", run_id=mv.run_id),
        data=SimpleNamespace(
            tags={"import_state": "verifying", "release_sha256": release.digest}
        ),
    )
    calls = []

    def finish(*args):
        run.info.status = args[1]
        calls.append("run_finish")

    def run_tag(*args):
        run.data.tags[args[1]] = args[2]
        calls.append("run_tag")

    def version_tag(*args):
        if args[2] == "import_state" and args[3] == "verified":
            assert run.info.status == "FINISHED"
            assert registry._receipt(release) == result
            assert "download" in calls
        mv.tags[args[2]] = args[3]
        calls.append("version_tag")

    registry.client = SimpleNamespace(
        get_run=lambda _: run,
        get_model_version=lambda *args: mv,
        search_model_versions=lambda _: [mv],
        set_terminated=finish,
        set_tag=run_tag,
        set_model_version_tag=version_tag,
        set_registered_model_alias=lambda *args: calls.append("alias"),
    )
    durable_json(
        registry.receipts / (release.digest + ".intent.json"),
        {k: result[k] for k in ("run_id", "release_sha256", "package_sha256")},
        immutable=True,
    )

    def download(*args):
        calls.append("download")
        return result

    monkeypatch.setattr(registry, "_download", download)
    if boundary in {"receipt_before", "receipt_after"}:
        target, method = module, "durable_json"
    elif boundary == "download":
        target, method = registry, "_download"
    else:
        target, method = (
            registry.client,
            {
                "run_finish": "set_terminated",
                "run_tag": "set_tag",
                "version_tag": "set_model_version_tag",
                "alias": "set_registered_model_alias",
            }[boundary],
        )
    original = getattr(target, method)

    def crash(*args, **kwargs):
        monkeypatch.setattr(target, method, original)
        if boundary != "receipt_before":
            original(*args, **kwargs)
        raise RuntimeError("interrupted publication")

    monkeypatch.setattr(target, method, crash)
    with pytest.raises(RuntimeError):
        registry.import_release(release)
    if boundary not in {"version_tag", "alias"}:
        assert mv.tags["import_state"] == "verifying"
        with pytest.raises(ValueError):
            registry.download_verified("1", release)
    assert registry.import_release(release) == result
    assert mv.tags["import_state"] == "verified" and run.info.status == "FINISHED"
    assert registry._receipt(release) == result


@pytest.mark.parametrize(
    "problem", ["missing_intent", "conflicting_intent", "failed_run", "bad_package"]
)
def test_unverifiable_partial_import_is_quarantined(
    release, tmp_path, monkeypatch, problem
):
    registry = Registry("http://127.0.0.1:5000", tmp_path / "receipts")
    mv = SimpleNamespace(
        version="1",
        run_id="synthetic-run",
        tags={
            "import_state": "verifying",
            "package_sha256": "a" * 64,
            "release_sha256": release.digest,
        },
    )
    run = SimpleNamespace(
        info=SimpleNamespace(status="FAILED" if problem == "failed_run" else "RUNNING"),
        data=SimpleNamespace(
            tags={"import_state": "verifying", "release_sha256": release.digest}
        ),
    )

    def tag(*args):
        mv.tags[args[2]] = args[3]

    registry.client = SimpleNamespace(
        search_model_versions=lambda _: [mv],
        get_run=lambda _: run,
        set_model_version_tag=tag,
        set_tag=lambda *args: run.data.tags.update({args[1]: args[2]}),
        set_terminated=lambda *args: setattr(run.info, "status", args[1]),
    )
    if problem != "missing_intent":
        durable_json(
            registry.receipts / (release.digest + ".intent.json"),
            {
                "run_id": "other" if problem == "conflicting_intent" else mv.run_id,
                "package_sha256": "a" * 64,
                "release_sha256": release.digest,
            },
        )

    def invalid(*args):
        raise ValueError("independent package verification failed")

    monkeypatch.setattr(registry, "_download", invalid)
    with pytest.raises(ValueError, match="quarantined"):
        registry.import_release(release)
    assert mv.tags["import_state"] == "quarantined"
    assert run.info.status == "FAILED"
    assert not (registry.receipts / (release.digest + ".json")).exists()


@pytest.mark.parametrize("platform", ["linux", "win32"])
def test_platform_requirements_checked_exactly(monkeypatch, platform):
    checked = []

    def version(name):
        checked.append(name)
        return {"numpy": "2.5.3", "pywin32": "312", "gunicorn": "26.2.0"}[name]

    monkeypatch.setattr(importlib.metadata, "version", version)
    lines = [
        "numpy==2.5.3",
        'pywin32==312; sys_platform == "win32"',
        'gunicorn==26.2.0; platform_system != "Windows"',
    ]
    environment = {
        "sys_platform": platform,
        "platform_system": "Windows" if platform == "win32" else "Linux",
    }
    verify_dependencies(lines, environment)
    assert checked == (
        ["numpy", "pywin32"] if platform == "win32" else ["numpy", "gunicorn"]
    )
    assert Requirement(str(locked_requirements(lines)[1])).marker is not None
    monkeypatch.setattr(importlib.metadata, "version", lambda name: "0")
    with pytest.raises(ReleaseError, match="mismatch"):
        verify_dependencies(lines, environment)


def test_nonapplicable_package_need_not_exist(monkeypatch):
    def missing(name):
        raise importlib.metadata.PackageNotFoundError(name)

    monkeypatch.setattr(importlib.metadata, "version", missing)
    verify_dependencies(
        ['pywin32==312; sys_platform == "win32"'], {"sys_platform": "linux"}
    )
    with pytest.raises(ReleaseError, match="missing"):
        verify_dependencies(
            ['pywin32==312; sys_platform == "win32"'], {"sys_platform": "win32"}
        )


@pytest.mark.parametrize(
    "line",
    [
        "numpy>=2",
        "numpy==2.*",
        "numpy @ https://public.test/n.whl",
        "numpy==2,!=3",
        "-r other.txt",
        'numpy==2; bad_marker == "x"',
    ],
)
def test_loose_or_invalid_lock_refused(line):
    with pytest.raises(ReleaseError):
        locked_requirements([line])


@pytest.mark.parametrize("host", ["127.0.0.1", "localhost", "::1", "mlflow"])
def test_configured_private_endpoint_accepted(host):
    endpoint = TrustedMLflowEndpoint(hostname=host, port=55442)
    assert endpoint.validate_uri(endpoint.uri) == endpoint.uri


@pytest.mark.parametrize(
    "host",
    [
        "example.com",
        "mlflow.example.com",
        "169.254.169.254",
        "127.0.0.2",
        "mlflow/evil",
        "mlflow@evil",
        "",
        "MLFLOW",
    ],
)
def test_public_or_malformed_configuration_rejected(host):
    with pytest.raises(ValidationError):
        TrustedMLflowEndpoint(hostname=host)


@pytest.mark.parametrize(
    "uri",
    [
        "http://public.test:5000",
        "http://mlflow:5000",
        "https://127.0.0.1:5000",
        "http://127.0.0.1:5001",
        "http://user:pass@127.0.0.1:5000",
        "http://127.0.0.1:5000/evil",
        "http://127.0.0.1:5000?url=evil",
        "http://127.0.0.1:5000#evil",
        "http://127.0.0.1",
        "http://127.0.0.1:70000",
    ],
)
def test_unconfigured_operator_uri_rejected(uri, tmp_path):
    with pytest.raises(ValueError):
        Registry(uri, tmp_path)


def test_mlflow_redirect_is_not_followed(tmp_path):
    visited = []

    class Redirect(BaseHTTPRequestHandler):
        def do_GET(self):
            visited.append(self.path)
            self.send_response(302)
            self.send_header("Location", "/forbidden")
            self.end_headers()

        def log_message(self, *args):
            pass

    server = HTTPServer(("127.0.0.1", 0), Redirect)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        endpoint = TrustedMLflowEndpoint(port=server.server_port)
        registry = Registry(endpoint.uri, tmp_path, endpoint)
        with pytest.raises(MlflowException):
            registry.client.get_experiment_by_name("test")
        assert len(visited) == 1 and visited[0] != "/forbidden"
    finally:
        server.shutdown()
        server.server_close()
        thread.join()
