"""Explicit private registry import; aliases never authorize deployment."""

import json
import math
import os
import shutil
import tempfile
from contextlib import contextmanager
from pathlib import Path
from types import SimpleNamespace

import mlflow
import pandas as pd
import sqlalchemy as sa
from mlflow import MlflowClient
from mlflow.models import ModelSignature
from mlflow.types import ColSpec, Schema

from . import schema as s
from .config import TrustedMLflowEndpoint
from .release import (
    VerifiedRelease,
    canonical,
    durable_json,
    inventory,
    locked_requirements,
    safe_file,
    sha,
)

NAME = "aletheia-healthcare-readmission"
EXPERIMENT = "aletheia-healthcare-frozen-import-v1"


@contextmanager
def import_lock(path):
    """Serialize cooperating local operators, with automatic crash lock release."""
    if path.is_symlink() or path.is_junction():
        raise ValueError("untrusted import lock")
    with path.open("a+b") as stream:
        stream.seek(0)
        if os.name == "nt":
            import msvcrt

            if not stream.read(1):
                stream.write(b"0")
                stream.flush()
            stream.seek(0)
            msvcrt.locking(stream.fileno(), msvcrt.LK_LOCK, 1)
        else:
            import fcntl

            fcntl.flock(stream.fileno(), fcntl.LOCK_EX)
        try:
            yield
        finally:
            stream.seek(0)
            if os.name == "nt":
                msvcrt.locking(stream.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(stream.fileno(), fcntl.LOCK_UN)


def package_inventory(root):
    return {
        name: sha(safe_file(root, name).read_bytes())
        for name in sorted(inventory(root))
    }


def verify_package(root, expected, digest, release):
    if sha(canonical(expected)) != digest or package_inventory(root) != expected:
        raise ValueError("registry package identity mismatch")
    code_hash = release.manifest["files"]["src/aletheia/application/pyfunc_model.py"]
    if code_hash not in expected.values() or release.digest not in expected.values():
        raise ValueError("reviewed code/release anchor missing")


class Registry:
    def __init__(self, tracking_uri, receipt_root=None, endpoint=None):
        # SDK URL messages contain Unicode and fail on Windows legacy consoles.
        os.environ["MLFLOW_SUPPRESS_PRINTING_URL_TO_STDOUT"] = "true"
        os.environ["MLFLOW_HTTP_REQUEST_TIMEOUT"] = "10"
        os.environ["MLFLOW_HTTP_REQUEST_MAX_RETRIES"] = "1"
        os.environ["MLFLOW_ALLOW_HTTP_REDIRECTS"] = "false"
        self.endpoint = endpoint or TrustedMLflowEndpoint()
        self.uri = self.endpoint.validate_uri(tracking_uri)
        self.receipts = Path(
            receipt_root or "artifacts/backend-import-receipts"
        ).absolute()
        if any(
            p.is_symlink() or p.is_junction()
            for p in (self.receipts, *self.receipts.parents)
        ):
            raise ValueError("untrusted import receipt root")
        self.receipts.mkdir(parents=True, exist_ok=True)
        self.client = MlflowClient(tracking_uri=self.uri, registry_uri=self.uri)

    def download_verified(self, version, release, expected_digest=None):
        mv = self.client.get_model_version(NAME, str(version))
        run = self.client.get_run(mv.run_id)
        if (
            run.info.status != "FINISHED"
            or run.data.tags.get("import_state") != "verified"
            or run.data.tags.get("release_sha256") != release.digest
        ):
            raise ValueError("failed/partial import quarantined")
        if (
            mv.tags.get("release_sha256") != release.digest
            or mv.tags.get("import_state") != "verified"
        ):
            raise ValueError("unverified registry candidate")
        receipt = self._receipt(release)
        if (
            receipt["version"] != str(version)
            or receipt["run_id"] != mv.run_id
            or (expected_digest and receipt["package_sha256"] != expected_digest)
            or mv.tags.get("package_sha256") != receipt["package_sha256"]
        ):
            raise ValueError("registry/independent receipt conflict")
        return self._download(mv, release, receipt["package_sha256"])

    def _download(self, mv, release, expected_digest):
        # Only the configured server's artifact proxy may supply executable bytes.
        source = mv.source
        if source != f"runs:/{mv.run_id}/model":
            raise ValueError("untrusted registry artifact source")
        run = self.client.get_run(mv.run_id)
        from urllib.parse import urlsplit

        artifact = urlsplit(run.info.artifact_uri)
        if artifact.scheme != "mlflow-artifacts" or artifact.netloc:
            raise ValueError("configured MLflow artifact proxy required")
        if {item.path for item in self.client.list_artifacts(mv.run_id)} != {
            "model",
            "package-inventory.json",
        }:
            raise ValueError("incomplete registry upload inventory")
        with tempfile.TemporaryDirectory(prefix="aletheia-registry-") as tmp:
            meta = self.client.download_artifacts(
                mv.run_id, "package-inventory.json", tmp
            )
            expected = json.loads(Path(meta).read_bytes())
            root = Path(self.client.download_artifacts(mv.run_id, "model", tmp))
            verify_package(root, expected, expected_digest, release)
            # Full outer package and inner release were checked before executing code.
            loaded = mlflow.pyfunc.load_model(str(root))
            result = loaded.predict(
                pd.DataFrame([release.case], columns=release.features)
            )
            score = float(result.iloc[0]["probability"])
            if (
                not math.isfinite(score)
                or not 0 <= score <= 1
                or abs(score - release.score()) > 1e-10
            ):
                raise ValueError("registry probability parity mismatch")
        return {
            "name": NAME,
            "version": str(mv.version),
            "run_id": mv.run_id,
            "release_sha256": release.digest,
            "package_sha256": expected_digest,
        }

    def import_release(self, release):
        if not isinstance(release, VerifiedRelease):
            raise ValueError("verified local release required")
        with import_lock(self.receipts / (release.digest + ".lock")):
            return self._import_release(release)

    def _import_release(self, release):
        matches = [
            m
            for m in self.client.search_model_versions(f"name='{NAME}'")
            if m.tags.get("release_sha256") == release.digest
        ]
        if matches:
            if len(matches) != 1:
                for candidate in matches:
                    self._quarantine(candidate.run_id, candidate)
                raise ValueError("conflicting/partial import quarantined")
            mv = matches[0]
            if mv.tags.get("import_state") == "verified":
                try:
                    result = self.download_verified(mv.version, release)
                    self.client.set_registered_model_alias(
                        NAME, "candidate", mv.version
                    )
                    return result
                except (ValueError, KeyError):
                    self._quarantine(mv.run_id, mv)
                    raise
            if mv.tags.get("import_state") != "verifying":
                self._quarantine(mv.run_id, mv)
                raise ValueError("conflicting/partial import quarantined")
            return self._resume(mv, release)
        exp = self.client.get_experiment_by_name(EXPERIMENT)
        expid = exp.experiment_id if exp else self.client.create_experiment(EXPERIMENT)
        runs = self.client.search_runs(
            [expid], f"tags.release_sha256 = '{release.digest}'"
        )
        if runs:
            if len(runs) == 1:
                run = runs[0]
                try:
                    intent = json.loads(
                        safe_file(
                            self.receipts, release.digest + ".intent.json"
                        ).read_bytes()
                    )
                    if (
                        run.info.status != "RUNNING"
                        or run.data.tags.get("import_state") != "verifying"
                        or intent["run_id"] != run.info.run_id
                        or intent["release_sha256"] != release.digest
                    ):
                        raise ValueError("unverifiable partial run")
                    partial = SimpleNamespace(
                        run_id=run.info.run_id,
                        version="pending",
                        source=f"runs:/{run.info.run_id}/model",
                    )
                    self._download(partial, release, intent["package_sha256"])
                    self._ensure_model()
                    mv = self.client.create_model_version(
                        NAME,
                        partial.source,
                        partial.run_id,
                        tags={
                            "release_sha256": release.digest,
                            "package_sha256": intent["package_sha256"],
                            "import_state": "verifying",
                            "approval_status": "candidate",
                        },
                    )
                    return self._resume(mv, release)
                except (ValueError, KeyError):
                    self._quarantine(run.info.run_id)
                    raise ValueError(
                        "unverifiable partial import quarantined"
                    ) from None
            for partial in runs:
                self._quarantine(partial.info.run_id)
            raise ValueError("conflicting partial imports quarantined")
        run = self.client.create_run(
            expid,
            tags={
                "release_sha256": release.digest,
                "mlflow.runName": "import-healthcare-model-v1-"
                f"{release.protocol['identity']['model_sha256'][:12]}-"
                f"{release.digest[:12]}",
                "scope": "historical-only-no-refit",
                "research_revision": release.manifest["research_revision"],
                "protocol_sha256": release.protocol["protocol_sha256"],
                "model_sha256": release.protocol["identity"]["model_sha256"],
                "selection_sha256": release.protocol["identity"]["selection_sha256"],
                "split_sha256": release.protocol["identity"]["split_lock_sha256"],
                "config_sha256": release.protocol["config_sha256"],
                "runtime": json.dumps(release.manifest["runtime"], sort_keys=True),
                "results_sha256": release.manifest["files"][
                    "artifacts/healthcare-audit-v1/results.json"
                ],
                "schema": "application-v1",
                "import_state": "verifying",
            },
        )
        mv = None
        try:
            mlflow.set_tracking_uri(self.uri)
            signature = ModelSignature(
                inputs=Schema([ColSpec("string", n) for n in release.features]),
                outputs=Schema([ColSpec("double", "probability")]),
            )
            with tempfile.TemporaryDirectory(prefix="aletheia-import-") as tmp:
                root = Path(tmp) / "model"
                # MLflow executes this file during save and may write __pycache__.
                # Run a verified byte copy outside the immutable release inventory.
                adapter = Path(tmp) / "pyfunc_model.py"
                shutil.copyfile(
                    safe_file(release.root, "src/aletheia/application/pyfunc_model.py"),
                    adapter,
                )
                mlflow.pyfunc.save_model(
                    path=str(root),
                    python_model=str(adapter),
                    artifacts={"release": str(release.root)},
                    input_example=pd.DataFrame(
                        [release.case], columns=release.features
                    ),
                    model_config={"release_digest": release.digest},
                    signature=signature,
                    pip_requirements=[
                        str(r)
                        for r in locked_requirements(
                            safe_file(release.root, "requirements.lock.txt")
                            .read_text()
                            .splitlines()
                        )
                    ],
                )
                expected = package_inventory(root)
                digest = sha(canonical(expected))
                verify_package(root, expected, digest, release)
                manifest = Path(tmp) / "package-inventory.json"
                manifest.write_bytes(canonical(expected))
                durable_json(
                    self.receipts / (release.digest + ".intent.json"),
                    {
                        "run_id": run.info.run_id,
                        "release_sha256": release.digest,
                        "package_sha256": digest,
                    },
                    immutable=True,
                )
                self.client.log_artifacts(run.info.run_id, str(root), "model")
                self.client.log_artifact(run.info.run_id, str(manifest))
            holdout = json.loads(
                safe_file(
                    release.root, "artifacts/healthcare-model-v1/holdout.json"
                ).read_bytes()
            )
            for name, value in holdout.get("metrics", {}).items():
                if isinstance(value, (int, float)) and not isinstance(value, bool):
                    self.client.log_metric(
                        run.info.run_id, f"historical_holdout_{name}", value
                    )
            self._ensure_model()
            mv = self.client.create_model_version(
                NAME,
                f"runs:/{run.info.run_id}/model",
                run.info.run_id,
                tags={
                    "release_sha256": release.digest,
                    "package_sha256": digest,
                    "import_state": "verifying",
                    "approval_status": "candidate",
                },
            )
            return self._resume(mv, release)
        except ValueError:
            self._quarantine(run.info.run_id, mv)
            raise

    def _ensure_model(self):
        try:
            self.client.get_registered_model(NAME)
        except mlflow.exceptions.MlflowException as exc:
            if exc.error_code != "RESOURCE_DOES_NOT_EXIST":
                raise
            self.client.create_registered_model(NAME)

    def _quarantine(self, run_id, mv=None):
        if mv is not None:
            self.client.set_model_version_tag(
                NAME, mv.version, "import_state", "quarantined"
            )
        self.client.set_tag(run_id, "import_state", "quarantined")
        self.client.set_terminated(run_id, "FAILED")

    def _resume(self, mv, release):
        try:
            run = self.client.get_run(mv.run_id)
            if run.info.status not in {"RUNNING", "FINISHED"} or (
                run.data.tags.get("import_state") == "quarantined"
                or run.data.tags.get("release_sha256") != release.digest
            ):
                raise ValueError("partial import quarantined")
            path = self.receipts / (release.digest + ".intent.json")
            intent = json.loads(safe_file(self.receipts, path.name).read_bytes())
            if (
                intent["release_sha256"] != release.digest
                or intent["run_id"] != mv.run_id
                or intent["package_sha256"] != mv.tags.get("package_sha256")
            ):
                raise ValueError("partial import intent conflict")
            result = self._download(mv, release, intent["package_sha256"])
            durable_json(
                self.receipts / (release.digest + ".json"), result, immutable=True
            )
            self.client.set_terminated(mv.run_id, "FINISHED")
            self.client.set_tag(mv.run_id, "import_state", "verified")
            self.client.set_model_version_tag(
                NAME, mv.version, "import_state", "verified"
            )
            self.client.set_registered_model_alias(NAME, "candidate", mv.version)
            return result
        except (ValueError, KeyError) as exc:
            self._quarantine(mv.run_id, mv)
            raise ValueError("unverifiable partial import quarantined") from exc

    def _receipt(self, release):
        try:
            path = safe_file(self.receipts, release.digest + ".json")
        except ValueError as exc:
            raise ValueError(
                "independent import receipt required; partial import quarantined"
            ) from exc
        result = json.loads(path.read_bytes())
        if result["release_sha256"] != release.digest or result["name"] != NAME:
            raise ValueError("independent receipt identity mismatch")
        return result

    def publish_approval(self, store, actor, release, identity):
        """Explicit administrator action; interrupted publication cannot activate."""
        with store.publication_lock():
            if self.download_verified(identity["version"], release) != identity:
                raise ValueError("independent approval identity conflict")
            store.register(actor, release, identity)
            return self._publish_approval(store, actor, release, identity)

    def _publish_approval(self, store, actor, release, identity):
        with store.engine.begin() as conn:
            store.authorize(conn, actor, {"administrator"})
            model = store.approved(
                conn, identity["version"], release.digest, require_active=False
            )
            if (
                model["run_id"] != identity["run_id"]
                or model["package_sha256"] != identity["package_sha256"]
            ):
                raise ValueError("registry/database identity mismatch")
            approval = conn.execute(
                sa.select(s.releases.c.audit_event_id)
                .where(
                    s.releases.c.model_version_id == model["id"],
                    s.releases.c.action == "approved",
                )
                .order_by(s.releases.c.created_at.desc())
                .limit(1)
            ).scalar_one()
        self.client.set_model_version_tag(
            NAME, identity["version"], "approval_status", "approved"
        )
        self.client.set_model_version_tag(
            NAME, identity["version"], "approver_event_id", str(approval)
        )
        self.client.set_registered_model_alias(NAME, "approved", identity["version"])
        return self.reconcile(
            store, release, identity["version"], identity["package_sha256"]
        )

    def publish_lifecycle(self, store, actor, release, identity, action):
        """Retry the same DB event through tags, aliases, pin and final projection."""
        with store.publication_lock():
            if self.download_verified(identity["version"], release) != identity:
                raise ValueError("independent lifecycle identity conflict")
            eid = store.release_action(
                actor, identity["version"], release.digest, action
            )
            with store.engine.begin() as conn:
                store.authorize(conn, actor, {"administrator"})
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
                if event["audit_event_id"] != eid:
                    raise ValueError("lifecycle event conflict")
                pin = store.deployment_pin(conn, state, event)
                previous = (
                    conn.execute(
                        sa.select(s.models).where(
                            s.models.c.id == event["previous_version_id"]
                        )
                    )
                    .mappings()
                    .first()
                )
            self.client.set_model_version_tag(
                NAME,
                identity["version"],
                "approval_status",
                "revoked" if action == "revoked" else "approved",
            )
            self.client.set_model_version_tag(
                NAME, identity["version"], "release_event_id", str(eid)
            )
            active_version = pin["active"]["version"] if pin["active"] else None
            for candidate in self.client.search_model_versions(f"name='{NAME}'"):
                if (
                    str(candidate.version) != active_version
                    and candidate.tags.get("deployment_status") == "active"
                ):
                    self.client.set_model_version_tag(
                        NAME, candidate.version, "deployment_status", "inactive"
                    )
            self.client.set_model_version_tag(
                NAME,
                identity["version"],
                "deployment_status",
                "active" if identity["version"] == active_version else "inactive",
            )
            if previous and previous["version"] != active_version:
                self.client.set_registered_model_alias(
                    NAME, "previous", previous["version"]
                )
            if active_version:
                self.client.set_registered_model_alias(NAME, "approved", active_version)
            else:
                if "approved" in self.client.get_registered_model(NAME).aliases:
                    self.client.delete_registered_model_alias(NAME, "approved")
            self._check_lifecycle(
                pin,
                identity,
                eid,
                previous["version"]
                if previous and previous["version"] != active_version
                else None,
            )
            durable_json(store.pin_path, pin)
            store.finish_publication(actor, eid, pin)
            return self.reconcile_lifecycle(store, release, identity)

    def reconcile_lifecycle(self, store, release, identity):
        if self.download_verified(identity["version"], release) != identity:
            raise ValueError("registry lifecycle package disagreement")
        with store.engine.begin() as conn:
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
            model = (
                conn.execute(
                    sa.select(s.models).where(
                        s.models.c.id == event["model_version_id"]
                    )
                )
                .mappings()
                .one()
            )
            if (
                not state["published"]
                or model["version"] != identity["version"]
                or model["release_sha256"] != release.digest
                or model["run_id"] != identity["run_id"]
                or model["package_sha256"] != identity["package_sha256"]
            ):
                raise ValueError("database lifecycle publication disagreement")
            pin = store.deployment_pin(conn, state, event)
            previous = conn.execute(
                sa.select(s.models.c.version).where(
                    s.models.c.id == event["previous_version_id"]
                )
            ).scalar()
            saved = json.loads(
                safe_file(store.pin_path.parent, store.pin_path.name).read_bytes()
            )
            if saved != pin:
                raise ValueError("explicit lifecycle pin disagreement")
        active_version = pin["active"]["version"] if pin["active"] else None
        self._check_lifecycle(
            pin,
            identity,
            event["audit_event_id"],
            previous if previous != active_version else None,
        )
        return pin

    def _check_lifecycle(self, pin, identity, eid, previous_version=None):
        registered = self.client.get_model_version(NAME, identity["version"])
        if registered.tags.get("release_event_id") != str(eid) or registered.tags.get(
            "approval_status"
        ) != ("revoked" if pin["action"] == "revoked" else "approved"):
            raise ValueError("registry lifecycle event disagreement")
        active = [
            str(m.version)
            for m in self.client.search_model_versions(f"name='{NAME}'")
            if m.tags.get("deployment_status") == "active"
        ]
        expected = pin["active"]["version"] if pin["active"] else None
        if active != ([expected] if expected else []):
            raise ValueError("contradictory registry active identities")
        aliases = self.client.get_registered_model(NAME).aliases
        if aliases.get("approved") != expected:
            raise ValueError("registry lifecycle alias disagreement")
        if previous_version is not None and aliases.get("previous") != previous_version:
            raise ValueError("registry previous alias/event disagreement")

    def reconcile(self, store, release, version, package_digest):
        identity = self.download_verified(version, release, package_digest)
        registered = self.client.get_model_version(NAME, str(version))
        with store.engine.begin() as conn:
            db = store.approved(
                conn, str(version), release.digest, require_active=False
            )
            if (
                db["run_id"] != identity["run_id"]
                or db["package_sha256"] != package_digest
            ):
                raise ValueError("registry/database/pin disagreement")
            approval = conn.execute(
                sa.select(s.releases.c.audit_event_id)
                .where(
                    s.releases.c.model_version_id == db["id"],
                    s.releases.c.action == "approved",
                )
                .order_by(s.releases.c.created_at.desc())
                .limit(1)
            ).scalar_one()
            if registered.tags.get("approver_event_id") != str(approval):
                raise ValueError("registry/database approval event disagreement")
            state = conn.execute(sa.select(s.deployment)).mappings().one()
            event = (
                conn.execute(
                    sa.select(s.releases).where(
                        s.releases.c.id == state["release_event_id"]
                    )
                )
                .mappings()
                .first()
            )
        if event and event["model_version_id"] == db["id"]:
            self.reconcile_lifecycle(store, release, identity)
        aliases = self.client.get_registered_model(NAME).aliases
        if registered.tags.get("approval_status") != "approved" or aliases.get(
            "approved"
        ) != str(version):
            raise ValueError("registry approval/alias disagreement")
        return identity
