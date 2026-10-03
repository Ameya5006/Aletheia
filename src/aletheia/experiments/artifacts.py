"""Atomic, immutable publication of a validated Phase 4 run manifest."""

from __future__ import annotations

import json
import os
import shutil
import tempfile
from pathlib import Path

from aletheia.contracts import ArtifactError, ExperimentError
from aletheia.experiments.manifest import validate_manifest


def publish_run(
    manifest: dict,
    root: str | Path = Path("artifacts/runs"),
) -> Path:
    """Stage, validate, and atomically rename one new run directory."""
    validate_manifest(manifest)
    root_path = Path(root)
    root_path.mkdir(parents=True, exist_ok=True)
    run_id = manifest.get("run_id")
    if not isinstance(run_id, str) or not run_id or Path(run_id).name != run_id:
        raise ArtifactError("run identifier must be one safe path component")
    destination = root_path / run_id
    if destination.exists():
        raise ArtifactError(f"run identifier already exists: {run_id}")
    staging: Path | None = Path(
        tempfile.mkdtemp(prefix=".aletheia-run-", dir=root_path)
    )
    try:
        manifest_path = staging / "manifest.json"
        with manifest_path.open("w", encoding="utf-8", newline="\n") as stream:
            stream.write(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
            stream.flush()
            os.fsync(stream.fileno())
        try:
            loaded = json.loads(manifest_path.read_text(encoding="utf-8"))
            validate_manifest(loaded)
        except (
            OSError,
            UnicodeDecodeError,
            json.JSONDecodeError,
            ExperimentError,
        ) as exc:
            raise ArtifactError(f"staged manifest validation failed: {exc}") from exc
        if destination.exists():
            raise ArtifactError(f"run identifier already exists: {run_id}")
        os.replace(staging, destination)
        staging = None
        return destination
    except OSError as exc:
        raise ArtifactError(f"run could not be published atomically: {exc}") from exc
    finally:
        if staging is not None:
            shutil.rmtree(staging, ignore_errors=True)
