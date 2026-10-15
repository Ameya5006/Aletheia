"""Milestone verification in an explicitly named isolated Compose project.

Preserves Stage 3 evidence. Reuses its unchanged PostgreSQL/test image scans;
changed production images are rescanned. Full regression has a one-run marker.
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path.cwd()
parser = argparse.ArgumentParser()
parser.add_argument(
    "action",
    choices=("provision", "tokens", "browser", "scan", "security", "regression"),
)
parser.add_argument(
    "--evidence", default="artifacts/interactive-verification/resume-20261015b"
)
args = parser.parse_args()
evidence = (ROOT / args.evidence).resolve()
if not evidence.is_relative_to((ROOT / "artifacts/interactive-verification").resolve()):
    raise ValueError("milestone evidence root required")
local = evidence / "local"
config = dict(
    line.split("=", 1) for line in (local / "config.env").read_text().splitlines()
)
project = config["COMPOSE_PROJECT_NAME"]
if not project.startswith("aletheia-interactive-"):
    raise ValueError("isolated interactive project required")
os.environ.update(
    ALETHEIA_LOCAL=str(local),
    ALETHEIA_EVIDENCE=str(evidence),
    ALETHEIA_BACKEND_IMAGE=project + "-backend:stage3",
    ALETHEIA_FRONTEND_IMAGE=project + "-frontend:stage3",
)

import prepare  # noqa: E402
import verify  # noqa: E402

prepare.LOCAL = local
verify.COMPOSE += ["-f", str(evidence / "override.json")]


def tokens():
    prepare.tokens()


def provision():
    tokens()
    verify.operator("bootstrap-initial-administrator")
    verify.operator("import-release", "--tracking-uri", "http://mlflow:5000")
    for action in ("approve-release", "activate-release"):
        tokens()
        verify.operator(
            action,
            "--tracking-uri",
            "http://mlflow:5000",
            "--token-file",
            "/run/secrets/operator_token",
        )
    for role in ("engineer", "reviewer"):
        verify.operator(
            "grant-role",
            "--token-file",
            "/run/secrets/operator_token",
            "--issuer",
            prepare.ISSUER,
            "--subject",
            "synthetic-" + role,
            "--role",
            role,
        )
    print("Explicit bootstrap/import/approval/activation/grants complete.")


def browser():
    tokens()
    env = dict(
        os.environ,
        ALETHEIA_BROWSER_BASE_URL="http://127.0.0.1:" + config["LOCAL_PORT"],
        ALETHEIA_BROWSER_TOKEN_FILE=str(local / "secrets/engineer_token"),
        ALETHEIA_BROWSER_EVIDENCE=str(evidence / "browser.json"),
    )
    subprocess.run(
        [
            "npm.cmd" if os.name == "nt" else "npm",
            "run",
            "test:browser",
            "--",
            "browser/interactive.spec.ts",
        ],
        cwd=ROOT / "frontend",
        env=env,
        check=True,
    )


def scans():
    import scan

    # Copies retain original tag/config/layer identities; no old evidence is edited.
    old = ROOT / "artifacts/stage3-verification"
    for name in ("postgres", "regression"):
        for suffix in (".tar", "-scan.json", "-sbom.json"):
            shutil.copyfile(old / (name + suffix), evidence / (name + suffix))
    shutil.copyfile(
        old / "regression-license-inventory.json",
        evidence / "regression-license-inventory.json",
    )
    sys.argv.append("--production-changed")
    scan.run()


def regression():
    marker = evidence / "full-regression.started.json"
    started = time.time()
    with marker.open("x", encoding="utf-8") as stream:
        json.dump({"started_unix": started, "project": project}, stream)
    # Prevent serving/probe contention; retain volumes and leave other projects alone.
    verify.compose("stop", "frontend", "api", "mlflow", "identity", "postgres")
    command = [*verify.COMPOSE, "--profile", "regression", "run", "--rm", "regression"]
    with (evidence / "full-regression.log").open("wb") as log:
        result = subprocess.run(command, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT)
    (evidence / "full-regression-result.json").write_text(
        json.dumps(
            {
                "command": command,
                "exit_code": result.returncode,
                "duration_seconds": time.time() - started,
                "project": project,
            },
            indent=2,
        )
    )
    print("Complete regression exit", result.returncode, flush=True)
    if result.returncode:
        raise RuntimeError("complete regression failed; supervisor review required")


if args.action == "provision":
    provision()
elif args.action == "tokens":
    tokens()
elif args.action == "browser":
    browser()
elif args.action == "scan":
    scans()
elif args.action == "security":
    import security

    security.run()
    path = evidence / "repair-security-disposition.json"
    report = json.loads(path.read_text())
    report["verification_context"] = {
        "project": project,
        "engine_context": "desktop-linux",
        "engine_version": "29.8.2",
        "previous_engine_version": "29.7.2",
        "pip_release_check": (
            "Historical 2026-10-14 metadata; not a new latest-version check"
        ),
        "input_boundary": (
            "Strict bounded single-case JSON; no archive/filesystem ingestion"
        ),
        "reused_images": (
            "PostgreSQL and test runner only; exact digests/layers asserted"
        ),
    }
    for finding in report["findings"]:
        if finding["component"] == "libacl1":
            key = "reachability_mitigation_disposition"
            finding[key] = finding[key].replace(
                "fixed synthetic API", "bounded single-case JSON API"
            )
    path.write_text(json.dumps(report, indent=2))
else:
    regression()
