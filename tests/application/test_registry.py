import pytest

from aletheia.application.registry import package_inventory, verify_package
from aletheia.application.release import canonical, sha


def test_package_tamper(release, tmp_path):
    root = tmp_path / "model"
    root.mkdir()
    (root / "code.py").write_text("untrusted")
    expected = package_inventory(root)
    with pytest.raises(ValueError):
        verify_package(root, expected, sha(canonical(expected)), release)
    (root / "code.py").write_text("changed")
    with pytest.raises(ValueError):
        verify_package(root, expected, sha(canonical(expected)), release)


def test_registry_real_import_download_duplicate(release, clean_registry, monkeypatch):
    registry = clean_registry
    prior = [
        m
        for m in registry.client.search_model_versions(
            "name='aletheia-healthcare-readmission'"
        )
        if m.tags.get("release_sha256") == release.digest
    ]
    assert prior == []
    create = registry.client.create_model_version
    set_tag = registry.client.set_model_version_tag
    observed = []

    def creating(*args, **kwargs):
        assert kwargs["tags"]["import_state"] == "verifying"
        version = create(*args, **kwargs)
        assert not (registry.receipts / (release.digest + ".json")).exists()
        observed.append("verifying")
        return version

    def tagging(name, version, key, value):
        if key == "import_state" and value == "verified":
            receipt = registry._receipt(release)
            assert registry.client.get_run(receipt["run_id"]).info.status == "FINISHED"
            assert receipt["version"] == str(version)
            observed.append("verified_after_receipt_and_run")
        return set_tag(name, version, key, value)

    monkeypatch.setattr(registry.client, "create_model_version", creating)
    monkeypatch.setattr(registry.client, "set_model_version_tag", tagging)
    first = registry.import_release(release)
    assert first["version"] == "1"
    assert registry.import_release(release) == first
    assert (
        registry.download_verified(first["version"], release, first["package_sha256"])
        == first
    )
    mv = registry.client.get_model_version(first["name"], first["version"])
    assert mv.tags["approval_status"] == "candidate"

    from packaging.requirements import Requirement

    receipt = registry._receipt(release)
    assert receipt == first
    run = registry.client.get_run(first["run_id"])
    assert run.info.status == "FINISHED"
    requirements = registry.client.download_artifacts(
        first["run_id"], "model/requirements.txt"
    )
    pins = [
        Requirement(line)
        for line in __import__("pathlib").Path(requirements).read_text().splitlines()
        if line and not line.startswith("#")
    ]
    assert next(r for r in pins if r.name == "pywin32").marker is not None
    assert next(r for r in pins if r.name == "gunicorn").marker is not None
    from aletheia.application.release import VerifiedRelease

    assert VerifiedRelease(release.root, release.digest).score() == release.score()
    assert observed == ["verifying", "verified_after_receipt_and_run"]
    print("registered test identity", first)


def test_registered_backend_reconciliation(
    db, release, settings, tokens, clean_registry
):
    from fastapi.testclient import TestClient

    from aletheia.application.api import create_app
    from aletheia.application.auth import Identity, ServiceError
    from aletheia.application.release import CASE

    registry = clean_registry
    identity = registry.import_release(release)
    owner, runtime = db
    issuer = settings.oidc_issuer
    owner.bootstrap(issuer, "synthetic-admin")
    admin = Identity(issuer, "synthetic-admin", frozenset({"administrator"}))
    owner.grant(admin, issuer, "synthetic-engineer", "engineer")
    owner.register(admin, release, identity)
    registry.publish_approval(owner, admin, release, identity)
    assert (
        registry.reconcile(
            owner, release, identity["version"], identity["package_sha256"]
        )
        == identity
    )
    with owner.engine.begin() as conn, pytest.raises(ServiceError):
        owner.approved(conn, identity["version"], release.digest)
    registry.publish_lifecycle(owner, admin, release, identity, "activated")
    actual = settings.model_copy(update={"model_version": identity["version"]})
    token, verifier, _, _ = tokens
    client = TestClient(create_app(actual, release, runtime, verifier))
    import uuid

    result = client.post(
        "/api/v1/predictions",
        json={
            "schema_version": "application-v1",
            "case_id": CASE,
            "model_version": identity["version"],
        },
        headers={
            "Authorization": "Bearer " + token(),
            "Idempotency-Key": str(uuid.uuid4()),
        },
    )
    assert result.status_code == 201, result.text
    assert abs(result.json()["data"]["probability"] - release.score()) <= 1e-10
    with pytest.raises(ValueError):
        registry.reconcile(owner, release, identity["version"], "0" * 64)
    registry.publish_lifecycle(owner, admin, release, identity, "revoked")
    with pytest.raises(ServiceError):
        registry.reconcile(
            owner, release, identity["version"], identity["package_sha256"]
        )


@pytest.mark.parametrize(
    "boundary",
    [
        "version_created",
        "receipt_before",
        "receipt_after",
        "run_finish",
        "version_verified",
        "candidate_alias",
    ],
)
def test_real_import_crash_recovery_reuses_run_and_version(
    release, clean_registry, tmp_path, monkeypatch, boundary
):
    import json
    import shutil

    import aletheia.application.registry as module
    from aletheia.application.release import VerifiedRelease, canonical, sha

    # Test-owned release variant: only an application comment changes its digest.
    # All frozen scientific/provenance bytes remain identical.
    root = tmp_path / "variant"
    shutil.copytree(release.root, root)
    name = "src/aletheia/application/operator.py"
    with (root / name).open("ab") as stream:
        stream.write(("\n# synthetic crash fixture: " + boundary + "\n").encode())
    manifest = json.loads((root / "release.json").read_bytes())
    manifest["files"][name] = sha((root / name).read_bytes())
    payload = canonical(manifest)
    (root / "release.json").write_bytes(payload)
    variant = VerifiedRelease(root, sha(payload))
    registry = clean_registry
    if boundary.startswith("receipt"):
        target, method = module, "durable_json"

        def predicate(args):
            return args[0].name == variant.digest + ".json"
    else:
        target, method = (
            registry.client,
            {
                "version_created": "create_model_version",
                "run_finish": "set_terminated",
                "version_verified": "set_model_version_tag",
                "candidate_alias": "set_registered_model_alias",
            }[boundary],
        )

        def predicate(args):
            return boundary != "version_verified" or args[2:] == (
                "import_state",
                "verified",
            )

    original = getattr(target, method)
    fired = False

    def crash(*args, **kwargs):
        nonlocal fired
        if not fired and predicate(args):
            fired = True
            if boundary != "receipt_before":
                original(*args, **kwargs)
            raise RuntimeError("simulated import process interruption")
        return original(*args, **kwargs)

    monkeypatch.setattr(target, method, crash)
    with pytest.raises(RuntimeError):
        registry.import_release(variant)
    versions = [
        m
        for m in registry.client.search_model_versions(f"name='{module.NAME}'")
        if m.tags.get("release_sha256") == variant.digest
    ]
    assert len(versions) == 1
    before = versions[0]
    if boundary not in {"version_verified", "candidate_alias"}:
        assert before.tags["import_state"] == "verifying"
        with pytest.raises(ValueError):
            registry.download_verified(before.version, variant)
    result = registry.import_release(variant)
    assert (
        result["version"] == str(before.version) and result["run_id"] == before.run_id
    )
    assert registry.import_release(variant) == result
    assert registry.client.get_run(result["run_id"]).info.status == "FINISHED"
    exp = registry.client.get_experiment_by_name(module.EXPERIMENT)
    assert (
        len(
            registry.client.search_runs(
                [exp.experiment_id], f"tags.release_sha256 = '{variant.digest}'"
            )
        )
        == 1
    )
