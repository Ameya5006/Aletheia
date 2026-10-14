"""Explicit test-only local setup; writes secrets and evidence only under artifacts."""

import hashlib
import ipaddress
import json
import secrets
from datetime import UTC, datetime, timedelta
from pathlib import Path

import jwt
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID

from aletheia.application.release import build_release

ROOT = Path.cwd()
LOCAL = ROOT / "artifacts/stage3-local"
ISSUER = "https://identity.test:8443"


def tokens():
    folder = LOCAL / "secrets"
    key = serialization.load_pem_private_key(
        (folder / "signing.pem").read_bytes(), password=None
    )
    now = int(datetime.now(UTC).timestamp())
    for role in ("administrator", "engineer", "reviewer"):
        subject = "synthetic-admin" if role == "administrator" else "synthetic-" + role
        token = jwt.encode(
            {
                "iss": ISSUER,
                "sub": subject,
                "aud": "aletheia-api",
                "iat": now,
                "exp": now + 600,
                "roles": [role],
                "token_use": "access",
            },
            key,
            algorithm="RS256",
            headers={"kid": "stage3-test", "typ": "at+jwt"},
        )
        (folder / (role + "_token")).write_text(token)
        if role == "administrator":
            (folder / "operator_token").write_text(token)
    print("refreshed short-lived synthetic tokens in ignored secret files")


def prepare():
    if LOCAL.exists():
        raise ValueError("existing setup refused; use tokens() for explicit refresh")
    folder = LOCAL / "secrets"
    folder.mkdir(parents=True)
    for name in ("postgres", "owner", "app", "mlflow"):
        password = secrets.token_hex(24)
        (folder / (name + "_password")).write_text(password)
        if name != "postgres":
            user = "aletheia_" + ("owner" if name == "owner" else name)
            db = "aletheia_mlflow" if name == "mlflow" else "aletheia_app"
            (folder / (name + "_db_url")).write_text(
                f"postgresql+psycopg://{user}:{password}@postgres:5432/{db}"
            )
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    pem = key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    )
    (folder / "signing.pem").write_bytes(pem)
    jwk = json.loads(jwt.algorithms.RSAAlgorithm.to_jwk(key.public_key()))
    jwk.update(kid="stage3-test", use="sig", alg="RS256")
    (folder / "jwks.json").write_text(json.dumps({"keys": [jwk]}))
    name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "Stage 3 test only")])
    now = datetime.now(UTC)
    cert = (
        x509.CertificateBuilder()
        .subject_name(name)
        .issuer_name(name)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now - timedelta(minutes=1))
        .not_valid_after(now + timedelta(days=2))
        .add_extension(x509.BasicConstraints(ca=True, path_length=None), critical=True)
        .add_extension(
            x509.SubjectAlternativeName(
                [
                    x509.DNSName("identity.test"),
                    x509.DNSName("localhost"),
                    x509.IPAddress(ipaddress.ip_address("127.0.0.1")),
                ]
            ),
            critical=False,
        )
        .sign(key, hashes.SHA256())
    )
    (folder / "identity_ca").write_bytes(cert.public_bytes(serialization.Encoding.PEM))
    digest = build_release(ROOT, LOCAL / "release")
    lines = {
        "COMPOSE_PROJECT_NAME": "aletheia-stage3-test",
        "APP_ENV": "test",
        "LOCAL_PORT": "18080",
        "SECRET_DIR": folder.as_posix(),
        "RELEASE_SOURCE": (LOCAL / "release").as_posix(),
        "APP_RELEASE_SHA256": digest,
        "APP_MODEL_VERSION": "1",
        "OIDC_ISSUER": ISSUER,
        "OIDC_JWKS_URI": ISSUER + "/jwks",
        "OIDC_AUDIENCE": "aletheia-api",
        "OIDC_MAX_TOKEN_LIFETIME_SECONDS": "600",
        "PROVIDER_TOKEN_LIFETIME_SECONDS": "600",
        "BOOTSTRAP_OIDC_ISSUER": ISSUER,
        "BOOTSTRAP_OIDC_SUB": "synthetic-admin",
    }
    (LOCAL / "config.env").write_text(
        "\n".join(f"{k}={v}" for k, v in lines.items()) + "\n"
    )
    tokens()
    print("verified release", digest)
    assert (
        hashlib.sha256((LOCAL / "release/release.json").read_bytes()).hexdigest()
        == digest
    )


if __name__ == "__main__":
    import sys

    tokens() if "--tokens" in sys.argv else prepare()
