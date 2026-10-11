import copy
import json
import shutil
import time
from pathlib import Path

import httpx
import jwt
import pytest
from pydantic import ValidationError

from aletheia.application.auth import ServiceError, TokenVerifier
from aletheia.application.release import (
    ReleaseError,
    VerifiedRelease,
    build_release,
    canonical,
    safe_file,
    sha,
)
from aletheia.application.store import event_bytes


def test_release_parity_and_immutable(release):
    assert (
        abs(release.score() - release.audit["synthetic_local"]["probability"]) <= 1e-10
    )
    assert release.bundle["calibrator"] is not None
    with pytest.raises(ReleaseError):
        build_release(Path.cwd(), release.root)


@pytest.mark.parametrize(
    "path",
    ["../secret", "/secret", "C:/secret", "a\\secret", "", "https://example.com/model"],
)
def test_paths(release, path):
    with pytest.raises(ReleaseError):
        safe_file(release.root, path)


@pytest.mark.parametrize("damage", ["extra", "missing", "changed", "runtime", "anchor"])
def test_release_damage(release, tmp_path, damage):
    root = tmp_path / "release"
    shutil.copytree(release.root, root)
    digest = release.digest
    if damage == "extra":
        (root / "extra.txt").write_text("extra")
    elif damage == "missing":
        (root / "artifacts/healthcare-model-v1/model.joblib").unlink()
    elif damage == "changed":
        (root / "artifacts/healthcare-model-v1/model.joblib").write_bytes(b"untrusted")
    elif damage == "runtime":
        manifest = json.loads((root / "release.json").read_bytes())
        manifest["runtime"]["python"] = "0"
        payload = canonical(manifest)
        (root / "release.json").write_bytes(payload)
        digest = sha(payload)
    else:
        digest = "0" * 64
    with pytest.raises(ReleaseError):
        VerifiedRelease(root, digest)


def test_missing_calibrator(release, monkeypatch):
    import aletheia.application.release as module

    monkeypatch.setattr(
        module,
        "load_trusted_artifact",
        lambda *args: dict(release.bundle, calibrator=None),
    )
    with pytest.raises(ReleaseError, match="calibrator"):
        VerifiedRelease(release.root, release.digest)


def test_symlink_rejected(release, tmp_path):
    link = tmp_path / "link"
    try:
        link.symlink_to(release.root, target_is_directory=True)
    except OSError:
        import subprocess

        subprocess.run(
            ["cmd", "/c", "mklink", "/J", str(link), str(release.root)],
            check=True,
            capture_output=True,
        )
    with pytest.raises(ReleaseError):
        safe_file(link, "release.json")


@pytest.mark.parametrize(
    "changes",
    [
        {"app_env": "release", "development_identity": True},
        {"oidc_issuer": "http://evil.test"},
        {"oidc_jwks_uri": "http://evil.test"},
        {"oidc_max_token_lifetime_seconds": 0},
        {"clock_skew_seconds": 61},
        {"database_url": "sqlite:///test"},
        {"cors_origins": ["*"]},
        {"provider_token_lifetime_seconds": 601},
        {"model_version": "latest"},
    ],
)
def test_configuration(settings, changes):
    values = settings.model_dump()
    values.update(changes)
    with pytest.raises(ValidationError):
        type(settings).model_validate(values)


@pytest.mark.parametrize(
    "change",
    [
        "issuer",
        "audience",
        "expired",
        "lifetime",
        "future",
        "id",
        "roles",
        "key",
        "algorithm",
    ],
)
def test_jwt_rejection(tokens, change):
    token, verifier, _, _ = tokens
    now = int(time.time())
    changes = {
        "issuer": {"iss": "https://evil.test"},
        "audience": {"aud": "browser-client"},
        "expired": {"iat": now - 500, "exp": now - 100},
        "lifetime": {"exp": now + 601},
        "future": {"iat": now + 100, "exp": now + 300},
        "id": {"token_use": "id"},
        "roles": {"roles": "administrator"},
    }
    encoded = token(**changes.get(change, {}))
    if change == "key":
        from cryptography.hazmat.primitives.asymmetric import rsa

        other = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        encoded = jwt.encode(
            jwt.decode(encoded, options={"verify_signature": False}),
            other,
            algorithm="RS256",
            headers={"kid": "synthetic-key", "typ": "at+jwt"},
        )
    if change == "algorithm":
        encoded = jwt.encode(
            {"sub": "admin"},
            "not-a-valid-secret",
            algorithm="HS256",
            headers={"kid": "synthetic-key"},
        )
    with pytest.raises(ServiceError) as result:
        verifier.verify(encoded)
    assert result.value.status == 401


def test_jwks_cache_outage_unknown(tokens, settings):
    token, verifier, _, jwk = tokens
    assert verifier.verify(token()).roles == {"engineer"}

    def outage():
        raise httpx.ConnectError("unavailable")

    verifier.fetch = outage
    assert verifier.verify(token()).roles == {"engineer"}
    verifier.fetched = verifier.last_attempt = 0
    with pytest.raises(ServiceError) as exc:
        verifier.verify(token())
    assert exc.value.status == 503
    unknown = copy.deepcopy(jwk)
    unknown["kid"] = "other"
    fresh = TokenVerifier(settings, fetch=lambda: {"keys": [unknown]})
    with pytest.raises(ServiceError) as exc:
        fresh.verify(token())
    assert exc.value.status == 401


def test_canonical_golden_and_float_refusal():
    assert event_bytes(
        {"sequence": 1, "payload": {"probability": "0.25"}, "prev_hash": "0" * 64}
    ) == (
        b'{"payload":{"probability":"0.25"},"prev_hash":"'
        + b"0" * 64
        + b'","sequence":1}'
    )
    with pytest.raises(ValueError):
        event_bytes({"payload": {"probability": 0.25}})


def test_configuration_error_hides_secrets(settings):
    values = settings.model_dump()
    values.update(
        database_url="postgresql+psycopg://operator:NEVER_PRINT_PASSWORD@localhost/app",
        clock_skew_seconds=100,
    )
    with pytest.raises(ValidationError) as exc:
        type(settings).model_validate(values)
    assert "NEVER_PRINT_PASSWORD" not in str(exc.value)
