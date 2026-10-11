"""Synthetic identities and disposable real PostgreSQL databases."""

import json
import os
import socket
import subprocess
import sys
import time
import uuid
from pathlib import Path

import httpx
import jwt
import pytest
import sqlalchemy as sa
from alembic import command
from alembic.config import Config
from cryptography.hazmat.primitives.asymmetric import rsa

from aletheia.application.auth import Identity, TokenVerifier
from aletheia.application.config import Settings, TrustedMLflowEndpoint
from aletheia.application.release import VerifiedRelease, build_release, durable_json
from aletheia.application.store import Store

ISSUER = "https://identity.example.test"


@pytest.fixture(scope="session")
def clean_registry(tmp_path_factory):
    """A new MLflow PostgreSQL database/registry and owned private artifact proxy."""
    from aletheia.application.registry import Registry

    url = os.environ.get("ALETHEIA_TEST_PG_ADMIN_URL")
    if not url:
        pytest.skip("real disposable PostgreSQL URL required")
    admin = sa.create_engine(url, isolation_level="AUTOCOMMIT")
    name = "mlflow_repair_" + uuid.uuid4().hex
    root = tmp_path_factory.mktemp("clean-mlflow")
    backend = sa.engine.make_url(url).set(database=name)
    with admin.connect() as conn:
        conn.execute(sa.text(f'CREATE DATABASE "{name}"'))
    with socket.socket() as reserved:
        reserved.bind(("127.0.0.1", 0))
        endpoint = TrustedMLflowEndpoint(port=reserved.getsockname()[1])
    env = dict(
        os.environ, MLFLOW_ALLOW_HTTP_REDIRECTS="false", PYTHONIOENCODING="utf-8"
    )
    process = None
    try:
        with (root / "service.log").open("wb") as log:
            process = subprocess.Popen(
                [
                    sys.executable,
                    "-m",
                    "mlflow",
                    "server",
                    "--backend-store-uri",
                    backend.render_as_string(hide_password=False),
                    "--host",
                    "127.0.0.1",
                    "--port",
                    str(endpoint.port),
                    "--workers",
                    "1",
                    "--serve-artifacts",
                    "--artifacts-destination",
                    str(root / "artifacts"),
                ],
                stdout=log,
                stderr=log,
                env=env,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
            )
            (root / "process.json").write_text(
                json.dumps({"pid": process.pid, "database": name, "uri": endpoint.uri})
            )
            for _ in range(180):
                if process.poll() is not None:
                    pytest.fail(
                        "disposable MLflow process failed; inspect ignored service.log"
                    )
                try:
                    if (
                        httpx.get(
                            endpoint.uri + "/health", timeout=0.5, trust_env=False
                        ).status_code
                        == 200
                    ):
                        break
                except httpx.HTTPError:
                    pass
                time.sleep(0.5)
            else:
                pytest.fail("disposable MLflow health deadline")
            registry = Registry(endpoint.uri, root / "receipts", endpoint)
            assert (
                registry.client.search_model_versions(
                    "name='aletheia-healthcare-readmission'"
                )
                == []
            )
            yield registry
    finally:
        try:
            if process is not None and process.poll() is None:
                if os.name == "nt":
                    stopped = subprocess.run(
                        ["taskkill", "/PID", str(process.pid), "/T", "/F"],
                        capture_output=True,
                        check=False,
                    )
                    if stopped.returncode != 0 and process.poll() is None:
                        raise RuntimeError("owned MLflow tree cleanup failed")
                else:
                    process.terminate()
                process.wait(timeout=20)
        finally:
            with admin.connect() as conn:
                conn.execute(sa.text(f'DROP DATABASE "{name}" WITH (FORCE)'))
            admin.dispose()


@pytest.fixture(scope="session")
def release(tmp_path_factory):
    dest = tmp_path_factory.mktemp("releases") / "release"
    return VerifiedRelease(dest, build_release(Path.cwd(), dest))


@pytest.fixture
def settings(release, tmp_path):
    return Settings(
        app_env="test",
        database_url="postgresql+psycopg://unused@localhost/test",
        release_root=release.root,
        release_sha256=release.digest,
        model_version="1",
        oidc_issuer=ISSUER,
        oidc_audience="aletheia-api",
        oidc_jwks_uri=ISSUER + "/jwks",
        oidc_max_token_lifetime_seconds=600,
        provider_token_lifetime_seconds=600,
        bootstrap_oidc_issuer=ISSUER,
        bootstrap_oidc_sub="synthetic-admin",
        deployment_pin_path=tmp_path / "deployment.json",
    )


@pytest.fixture
def tokens(settings):
    import time

    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    jwk = json.loads(jwt.algorithms.RSAAlgorithm.to_jwk(key.public_key()))
    jwk.update(kid="synthetic-key", alg="RS256", use="sig")
    verifier = TokenVerifier(settings, fetch=lambda: {"keys": [jwk]})

    def token(sub="synthetic-engineer", roles=None, **changes):
        now = int(time.time())
        claims = dict(
            iss=ISSUER,
            sub=sub,
            aud=settings.oidc_audience,
            iat=now,
            exp=now + 300,
            roles=roles or ["engineer"],
            token_use="access",
        )
        claims.update(changes)
        return jwt.encode(
            claims,
            key,
            algorithm="RS256",
            headers={"kid": "synthetic-key", "typ": "at+jwt"},
        )

    return token, verifier, key, jwk


@pytest.fixture
def db(monkeypatch, tmp_path):
    url = os.environ.get("ALETHEIA_TEST_PG_ADMIN_URL")
    if not url:
        pytest.skip("real disposable PostgreSQL URL required")
    admin = sa.create_engine(url, isolation_level="AUTOCOMMIT")
    database = "aletheia_test_" + uuid.uuid4().hex
    with admin.connect() as conn:
        conn.execute(sa.text(f'CREATE DATABASE "{database}"'))
        conn.execute(
            sa.text("""DO $$ BEGIN
          IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname='aletheia_test_runtime')
          THEN CREATE ROLE aletheia_test_runtime LOGIN; END IF; END $$""")
        )
    parsed = sa.engine.make_url(url).set(database=database)
    owner = Store(
        parsed.render_as_string(hide_password=False), tmp_path / "deployment.json"
    )
    monkeypatch.setenv(
        "ALETHEIA_MIGRATION_URL", parsed.render_as_string(hide_password=False)
    )
    config = Config("alembic.ini")
    command.upgrade(config, "0001_backend")
    with owner.engine.connect() as conn:
        assert (
            conn.execute(sa.text("SELECT version_num FROM alembic_version")).scalar()
            == "0001_backend"
        )
        assert (
            conn.execute(
                sa.text("SELECT to_regclass('public.deployment_state')")
            ).scalar()
            is None
        )
    command.upgrade(config, "head")
    with owner.engine.begin() as conn:
        conn.execute(sa.text("GRANT aletheia_runtime TO aletheia_test_runtime"))
    runtime_url = parsed.set(username="aletheia_test_runtime", password=None)
    runtime = Store(runtime_url.render_as_string(hide_password=False), owner.pin_path)
    yield owner, runtime
    runtime.engine.dispose()
    owner.engine.dispose()
    with admin.connect() as conn:
        conn.execute(sa.text(f'DROP DATABASE "{database}" WITH (FORCE)'))
    admin.dispose()


@pytest.fixture
def prepared(db, release):
    owner, runtime = db
    owner.bootstrap(ISSUER, "synthetic-admin")
    admin = Identity(ISSUER, "synthetic-admin", frozenset({"administrator"}))
    engineer_id = owner.grant(admin, ISSUER, "synthetic-engineer", "engineer")
    reviewer_id = owner.grant(admin, ISSUER, "synthetic-reviewer", "reviewer")
    owner.grant(admin, ISSUER, "synthetic-other", "engineer")
    owner.register(
        admin,
        release,
        {
            "name": "aletheia-healthcare-readmission",
            "version": "1",
            "run_id": "synthetic-test",
            "package_sha256": "a" * 64,
        },
    )
    eid = owner.release_action(admin, "1", release.digest, "activated")
    publish_test_pin(owner, admin, eid)
    return owner, runtime, admin, engineer_id, reviewer_id


def publish_test_pin(owner, admin, eid):
    """Store/API fixtures simulate completed publication; no registry proof claimed."""
    from aletheia.application import schema as s

    with owner.engine.begin() as conn:
        state = conn.execute(sa.select(s.deployment)).mappings().one()
        event = (
            conn.execute(
                sa.select(s.releases).where(
                    s.releases.c.id == state["release_event_id"]
                )
            )
            .mappings()
            .one()
        )
        pin = owner.deployment_pin(conn, state, event)
    durable_json(owner.pin_path, pin)
    owner.finish_publication(admin, eid, pin)
