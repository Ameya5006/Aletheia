"""Offline regression runner inside a disposable isolated test network."""

import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

os.environ["ALETHEIA_TEST_PG_ADMIN_URL"] = (
    "postgresql+psycopg://postgres@regression-postgres:5432/postgres"
)
os.environ["MLFLOW_ENABLE_ARTIFACTS_PROGRESS_BAR"] = "false"
os.environ["MLFLOW_DISABLE_AGENT_HINT"] = "1"
os.environ["MLFLOW_SERVER_ENABLE_JOB_EXECUTION"] = "false"
diagnostics = Path("/diagnostics") / str(time.time_ns())
diagnostics.mkdir()


def counters():
    paths = [
        Path("/sys/fs/cgroup") / name
        for name in ("cpu.stat", "cpu.max", "memory.events", "memory.peak")
    ]
    return {p.name: p.read_text() for p in paths if p.is_file()}


before = counters()
try:
    result = subprocess.call(
        [
            sys.executable,
            "-m",
            "pytest",
            "-m",
            "not live_data",
            "-p",
            "no:cacheprovider",
            "--basetemp",
            "/tmp/regression",
        ]
    )
finally:
    (diagnostics / "cgroup.json").write_text(
        json.dumps({"before": before, "after": counters()}, indent=2)
    )
    # Only synthetic fixture service logs; never copy keys, data or model files.
    for folder in Path("/tmp/regression").glob("clean-mlflow*"):
        log = folder / "service.log"
        if folder.is_dir() and not folder.is_symlink() and log.is_file():
            shutil.copyfile(log, diagnostics / f"{folder.name}-service.log")
sys.exit(result)
