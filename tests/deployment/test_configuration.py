"""Deployment boundaries checked without a Docker daemon or secrets."""

from pathlib import Path

import pytest
import yaml

from aletheia.application.config import Settings

ROOT = Path(__file__).resolve().parents[2]


def topology():
    return yaml.safe_load((ROOT / "deployment/compose.yaml").read_text())


def test_private_services_and_explicit_operator_jobs():
    config = topology()
    services = config["services"]
    for name in ("postgres", "mlflow", "api"):
        assert "ports" not in services[name]
        assert services[name]["networks"] == ["private"]
    assert services["frontend"]["networks"] == ["private", "ingress"]
    assert config["networks"]["private"]["internal"] is True
    assert services["frontend"]["ports"] == [
        "127.0.0.1:${LOCAL_PORT:?explicit local port required}:8080"
    ]
    for name in ("migrate", "release-stage", "release-import"):
        assert services[name]["profiles"] == ["operator"]
        assert name not in services["api"]["depends_on"]
    for name in ("api", "frontend", "mlflow"):
        assert services[name]["cap_drop"] == ["ALL"]
        assert services[name]["read_only"] is True
        assert services[name]["user"].split(":")[0] != "0"
    assert set(config["volumes"]) == {"pgdata", "registry", "state", "release"}
    assert services["api"]["volumes"] == ["release:/release:ro", "state:/state:ro"]


def test_release_profile_cannot_enable_test_identity():
    with pytest.raises(ValueError, match="development identity forbidden"):
        Settings(
            app_env="release",
            database_url="postgresql+psycopg://unused@postgres/app",
            release_root=Path("/release/current"),
            release_sha256="a" * 64,
            model_version="1",
            oidc_issuer="https://identity.test:8443",
            oidc_audience="aletheia-api",
            oidc_jwks_uri="https://identity.test:8443/jwks",
            oidc_max_token_lifetime_seconds=600,
            provider_token_lifetime_seconds=600,
            development_identity=True,
        )


def test_regression_database_is_isolated_from_delivery():
    overlay = yaml.safe_load((ROOT / "deployment/compose.test.yaml").read_text())
    service = overlay["services"]["regression-postgres"]
    assert service["profiles"] == ["regression"]
    assert service["networks"] == ["regression"]
    assert "ports" not in service
    assert "private" not in service["networks"]
    assert (
        "POSTGRES_HOST_AUTH_METHOD"
        not in (topology()["services"]["postgres"]["environment"])
    )


def test_tmpfs_options_remain_part_of_absolute_mount_path():
    # Commas split unquoted YAML flow entries, even when Compose config accepts it.
    for filename in ("compose.yaml", "compose.test.yaml"):
        config = yaml.safe_load((ROOT / "deployment" / filename).read_text())
        for service in config["services"].values():
            for mount in service.get("tmpfs", []):
                assert mount.startswith("/"), "tmpfs options became separate mounts"
                assert ":" in mount and "size=" in mount
