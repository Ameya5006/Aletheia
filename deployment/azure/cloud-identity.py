"""Local-only synthetic showcase identity material; never print tokens or keys."""

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path

import jwt
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa


PRIVATE = Path("artifacts/azure-preflight/cloud-private")
ISSUER = "https://frontend.whiteflower-9d03c62c.southeastasia.azurecontainerapps.io"
KID = "azure-showcase-20261018"


def init() -> None:
    PRIVATE.mkdir(parents=True, exist_ok=True)
    key_path = PRIVATE / "signing.pem"
    if key_path.exists():
        raise SystemExit("Signing key exists; refusing to replace it")
    key = rsa.generate_private_key(public_exponent=65537, key_size=3072)
    with key_path.open("xb") as handle:
        handle.write(key.private_bytes(
            serialization.Encoding.PEM,
            serialization.PrivateFormat.PKCS8,
            serialization.NoEncryption(),
        ))
    jwk = json.loads(jwt.algorithms.RSAAlgorithm.to_jwk(key.public_key()))
    jwk.update(kid=KID, alg="RS256", use="sig")
    (PRIVATE / "jwks.json").write_text(json.dumps({"keys": [jwk]}), encoding="utf-8")
    print("Cloud showcase signing material created in ignored local evidence directory")


def token(role: str) -> None:
    key = serialization.load_pem_private_key((PRIVATE / "signing.pem").read_bytes(), password=None)
    now = int(datetime.now(UTC).timestamp())
    subject = "synthetic-admin" if role == "administrator" else f"synthetic-{role}"
    encoded = jwt.encode(
        {
            "iss": ISSUER,
            "sub": subject,
            "aud": "aletheia-api",
            "iat": now,
            "exp": now + 840,
            "roles": [role],
            "token_use": "access",
        },
        key,
        algorithm="RS256",
        headers={"kid": KID, "typ": "at+jwt"},
    )
    path = PRIVATE / f"{role}.token"
    with path.open("w", encoding="ascii") as handle:
        handle.write(encoded)
    print(f"Short-lived synthetic {role} token refreshed in ignored local evidence directory")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=("init", "token"))
    parser.add_argument("--role", choices=("administrator", "engineer", "reviewer"))
    args = parser.parse_args()
    if args.action == "init":
        init()
    elif args.role:
        token(args.role)
    else:
        parser.error("--role is required for token")
