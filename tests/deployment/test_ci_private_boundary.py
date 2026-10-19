"""A real public MLflow health response must fail the outside boundary gate."""

import importlib.util
from contextlib import nullcontext
from pathlib import Path
from types import SimpleNamespace
from urllib.error import HTTPError

import pytest

SPEC = importlib.util.spec_from_file_location(
    "ci_guard", Path(__file__).resolve().parents[2] / "deployment/azure/ci-guard.py"
)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


@pytest.mark.parametrize(
    "name,path", [("api", "/api/v1/health/live"), ("mlflow", "/health")]
)
@pytest.mark.parametrize("internal_host", [False, True])
def test_real_public_application_endpoint_fails_boundary(name, path, internal_host):
    fqdn = f"{name}.internal.{MODULE.DOMAIN}"
    exposed = fqdn if internal_host else f"{name}.{MODULE.DOMAIN}"

    def opener(url, **kwargs):
        if url == f"https://{exposed}{path}":
            return nullcontext(SimpleNamespace(status=200))
        raise HTTPError(url, 404, "private edge rejection", None, None)

    with pytest.raises(AssertionError, match=f"public {name} boundary"):
        MODULE.verify_private_boundary(name, fqdn, opener)


@pytest.mark.parametrize(
    "name,path", [("api", "/api/v1/health/live"), ("mlflow", "/health")]
)
def test_actual_fqdn_and_alias_must_both_be_rejected(name, path):
    urls = []
    fqdn = f"{name}.internal.{MODULE.DOMAIN}"

    def opener(url, **kwargs):
        urls.append(url)
        raise HTTPError(url, 404, "private edge rejection", None, None)

    MODULE.verify_private_boundary(name, fqdn, opener)
    assert set(urls) == {
        f"https://{fqdn}{path}",
        f"https://{name}.{MODULE.DOMAIN}{path}",
    }


def test_operator_checks_real_same_environment_health(monkeypatch):
    spec = importlib.util.spec_from_file_location(
        "ci_smoke", Path(__file__).resolve().parents[2] / "deployment/azure/ci-smoke.py"
    )
    smoke = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(smoke)
    urls = []

    class ReachedAuthentication(Exception):
        pass

    def get(url, **kwargs):
        urls.append(url)
        if url == smoke.API + "/analyses":
            raise ReachedAuthentication
        return SimpleNamespace(status_code=200)

    client = SimpleNamespace(get=get)
    monkeypatch.setattr(smoke.httpx, "Client", lambda **kwargs: nullcontext(client))
    with pytest.raises(ReachedAuthentication):
        smoke.main()
    assert "http://api/api/v1/health/live" in urls
    assert "http://mlflow/health" in urls
