"""Byte-preserving local releases with independently pinned manifest identity."""

import hashlib
import importlib.metadata
import json
import os
import shutil
import tempfile
import tomllib
from pathlib import Path, PurePosixPath

import pandas as pd
from packaging.requirements import InvalidRequirement, Requirement

from aletheia.domains.healthcare.experiment import load_trusted_artifact, versions
from aletheia.domains.healthcare.explain import probability

MODEL_FILES = {
    "artifact.json",
    "model.joblib",
    "selection.json",
    "nested_cv.json",
    "holdout.json",
    "holdout.claim",
}
AUDIT_FILES = {"manifest.json", "protocol.json", "results.json", "holdout.claim"}
MODEL_HASH = "8c3a99dd8dfe20d2a3a0a721637b4be500ee1b32843f7cefc3af265f07262f7a"
RESULT_HASH = "2d073fa0d0bbbd4debfdf445cd80ec478fef0f7098c7ef356dbb3edd28894ea8"
CASE = "synthetic-discharge-v1"


class ReleaseError(ValueError):
    pass


def locked_requirements(lines):
    """Parse PEP 508 without discarding platform markers or accepting loose pins."""
    requirements = []
    for line in lines:
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        try:
            requirement = Requirement(line)
        except InvalidRequirement as exc:
            raise ReleaseError("invalid application dependency lock") from exc
        pins = list(requirement.specifier)
        if (
            requirement.url
            or len(pins) != 1
            or pins[0].operator != "=="
            or "*" in pins[0].version
        ):
            raise ReleaseError("exact application dependency pin required")
        requirements.append(requirement)
    return requirements


def verify_dependencies(lines, environment=None):
    for requirement in locked_requirements(lines):
        if requirement.marker and not requirement.marker.evaluate(environment):
            continue
        try:
            installed = importlib.metadata.version(requirement.name)
        except importlib.metadata.PackageNotFoundError as exc:
            raise ReleaseError("application dependency missing") from exc
        if installed != next(iter(requirement.specifier)).version:
            raise ReleaseError("application dependency lock mismatch")


def canonical(value):
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode("utf-8")


def sha(value: bytes):
    return hashlib.sha256(value).hexdigest()


def durable_json(path, value, immutable=False):
    """Atomic replacement with file and (on POSIX) directory durability."""
    path = Path(path).absolute()
    path.parent.mkdir(parents=True, exist_ok=True)
    if any(p.is_symlink() or p.is_junction() for p in (path, *path.parents)):
        raise ReleaseError("untrusted durable record path")
    payload = canonical(value)
    if immutable and path.exists():
        if path.read_bytes() != payload:
            raise ReleaseError("durable record identity conflict")
        return
    fd, temporary = tempfile.mkstemp(dir=path.parent, prefix=".record-")
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
        if os.name != "nt":
            fd = os.open(path.parent, os.O_RDONLY)
            try:
                os.fsync(fd)
            finally:
                os.close(fd)
    finally:
        Path(temporary).unlink(missing_ok=True)


def safe_file(root: Path, relative: str) -> Path:
    parts = PurePosixPath(relative)
    if (
        not relative
        or parts.is_absolute()
        or ".." in parts.parts
        or "\\" in relative
        or ":" in relative
    ):
        raise ReleaseError("unsafe release path")
    root = root.absolute()
    path = root / relative
    if not path.resolve().is_relative_to(root.resolve()):
        raise ReleaseError("outside release root")
    for candidate in (root, *path.parents, path):
        if candidate.is_symlink() or candidate.is_junction():
            raise ReleaseError("symlink/junction refused")
    if not path.is_file():
        raise ReleaseError("missing release file")
    return path


def read(root, name):
    return json.loads(safe_file(root, name).read_bytes())


def inventory(root):
    files = set()
    for p in root.rglob("*"):
        if p.is_symlink() or p.is_junction():
            raise ReleaseError("symlink/junction refused")
        if p.is_file():
            files.add(p.relative_to(root).as_posix())
    return files


class VerifiedRelease:
    def __init__(self, root: Path, digest: str):
        self.root = root.absolute()
        raw = safe_file(self.root, "release.json").read_bytes()
        if sha(raw) != digest:
            raise ReleaseError("release anchor mismatch")
        self.manifest = json.loads(raw)
        m = self.manifest
        if m["schema"] != "aletheia-release-v1" or m["runtime"] != versions():
            raise ReleaseError("release schema/runtime mismatch")
        if inventory(self.root) != set(m["files"]) | {"release.json"}:
            raise ReleaseError("release inventory mismatch")
        for name, expected in m["files"].items():
            if sha(safe_file(self.root, name).read_bytes()) != expected:
                raise ReleaseError("release file checksum mismatch")
        verify_dependencies(
            safe_file(self.root, "requirements.lock.txt").read_text().splitlines()
        )
        self.digest = digest
        self.audit = read(self.root, "artifacts/healthcare-audit-v1/results.json")
        self.protocol = read(self.root, "artifacts/healthcare-audit-v1/protocol.json")
        artifact = read(self.root, "artifacts/healthcare-model-v1/artifact.json")
        selection = read(self.root, "artifacts/healthcare-model-v1/selection.json")
        audit_manifest = read(self.root, "artifacts/healthcare-audit-v1/manifest.json")
        if (
            artifact["sha256"] != MODEL_HASH
            or audit_manifest["results_sha256"] != RESULT_HASH
        ):
            raise ReleaseError("unapproved original evidence")
        for name, digest in audit_manifest["bindings"].items():
            if m["files"].get(name) != digest:
                raise ReleaseError("original provenance mismatch")
        if (
            self.protocol["bindings"] != audit_manifest["bindings"]
            or self.audit["identity"] != audit_manifest["identity"]
            or self.protocol["identity"] != audit_manifest["identity"]
            or sha(canonical(self.protocol["config"]))
            != audit_manifest["protocol_sha256"]
            or m["files"]["artifacts/healthcare-audit-v1/protocol.json"]
            != audit_manifest["protocol_file_sha256"]
            or m["files"]["artifacts/healthcare-audit-v1/results.json"] != RESULT_HASH
        ):
            raise ReleaseError("audit binding mismatch")
        self.features = tomllib.loads(
            safe_file(
                self.root, "configs/features/healthcare_uci296_v1.toml"
            ).read_text()
        )["roles"]["prediction"]
        self.case = self.protocol["config"]["synthetic_example"]
        if set(self.case) != set(self.features) or len(self.features) != 13:
            raise ReleaseError("synthetic feature mismatch")
        # Every byte and binding is checked before trusted deserialization.
        self.bundle = load_trusted_artifact(
            safe_file(self.root, "artifacts/healthcare-model-v1/model.joblib"),
            artifact,
            selection["protocol"],
        )
        if self.bundle.get("calibrator") is None:
            raise ReleaseError("calibrator required")
        if abs(self.score() - self.audit["synthetic_local"]["probability"]) > 1e-10:
            raise ReleaseError("synthetic calibrated probability mismatch")

    def score(self):
        frame = pd.DataFrame([self.case], columns=self.features)
        return float(probability(self.bundle, frame)[0])


def build_release(repository: Path, destination: Path) -> str:
    """Only the configured repository's approved roots; no arbitrary artifact URI."""
    from aletheia.domains.healthcare.audit import inspect

    repository = repository.absolute()
    if repository.resolve() != Path.cwd().resolve():
        raise ReleaseError("builder requires configured repository working directory")
    for folder, allowed in (
        ("healthcare-model-v1", MODEL_FILES),
        ("healthcare-audit-v1", AUDIT_FILES),
    ):
        root = repository / "artifacts" / folder
        if {p.name for p in root.iterdir()} != allowed:
            raise ReleaseError("original artifact inventory mismatch")
        for name in allowed:
            safe_file(repository, f"artifacts/{folder}/{name}")
    manifest = read(repository, "artifacts/healthcare-audit-v1/manifest.json")
    for name, expected in manifest["bindings"].items():
        if sha(safe_file(repository, name).read_bytes()) != expected:
            raise ReleaseError("original hash mismatch")
    inspect()  # Existing read-only inspector, no patient loading or runner.
    paths = set(manifest["bindings"])
    paths |= {f"artifacts/healthcare-audit-v1/{n}" for n in AUDIT_FILES}
    paths |= {
        "docs/model_cards/healthcare_readmission_v1.md",
        "requirements.lock.txt",
        "src/aletheia/application/pyfunc_model.py",
    }
    paths |= {
        p.relative_to(repository).as_posix()
        for p in (repository / "src/aletheia/application").glob("*.py")
    }
    destination = destination.absolute()
    if (
        destination.exists()
        or destination.is_symlink()
        or destination.is_relative_to(repository / "src")
    ):
        raise ReleaseError("immutable destination refused")
    destination.mkdir(parents=True, exist_ok=False)
    for name in sorted(paths):
        source = safe_file(repository, name)
        target = destination / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
    record = {
        "schema": "aletheia-release-v1",
        "runtime": versions(),
        "research_revision": read(
            repository, "artifacts/healthcare-audit-v1/protocol.json"
        )["git_head"],
        "files": {
            name: sha(safe_file(destination, name).read_bytes())
            for name in sorted(paths)
        },
    }
    payload = canonical(record)
    (destination / "release.json").write_bytes(payload)
    digest = sha(payload)
    VerifiedRelease(destination, digest)
    return digest
