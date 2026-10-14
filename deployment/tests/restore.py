"""Explicit quiesced backup and isolated restore rehearsal; never delete volumes."""

import hashlib
import io
import json
import subprocess
import tarfile
import time
import uuid

import httpx
from verify import BASE, COMPOSE, EVIDENCE, ROOT, compose, headers, refresh, wait_ready

PROJECT = "aletheia-stage3-test"
RESTORE = "aletheia-stage3-restore-" + uuid.uuid4().hex[:8]
IMAGE = PROJECT + "-backend:stage3"
ARCHIVE = """import sys,tarfile
with tarfile.open(fileobj=sys.stdout.buffer,mode='w|') as t:
    t.add('/registry',arcname='.',recursive=True)
"""
EXTRACT = """import sys,tarfile
def backup_filter(member,path):
    if not (member.isfile() or member.isdir()):
        raise ValueError('unexpected backup member type')
    safe=tarfile.data_filter(member,path)
    safe.mode=member.mode & 0o777
    return safe
with tarfile.open(fileobj=sys.stdin.buffer,mode='r|') as t:
    t.extractall('/registry',filter=backup_filter)
"""


def binary(args, data=None):
    result = subprocess.run(
        args, cwd=ROOT, input=data, capture_output=True, timeout=360
    )
    if result.returncode:
        path = EVIDENCE / ("restore-failure-" + uuid.uuid4().hex + ".log")
        path.write_bytes(result.stdout + result.stderr)
        raise RuntimeError(f"backup/restore command failed; inspect {path.name}")
    return result.stdout


def volume(project, name, code, data=None):
    return binary(
        [
            "docker",
            "run",
            "--rm",
            "-i",
            "--network",
            "none",
            "--user",
            "10001:10001",
            "--cap-drop",
            "ALL",
            "--security-opt",
            "no-new-privileges:true",
            "--read-only",
            "--mount",
            f"type=volume,source={project}_{name},target=/registry",
            "--entrypoint",
            "python",
            IMAGE,
            "-c",
            code,
        ],
        data,
    )


def contents(data):
    """Compare restored file bytes/permissions, not tar container metadata."""
    with tarfile.open(fileobj=io.BytesIO(data)) as archive:
        result = {}
        for item in archive.getmembers():
            assert item.isfile() or item.isdir(), "unexpected backup member type"
            stream = archive.extractfile(item) if item.isfile() else None
            result[item.name] = {
                "type": "file" if item.isfile() else "directory",
                "mode": item.mode,
                "sha256": hashlib.sha256(stream.read()).hexdigest() if stream else None,
            }
        return result


def run():
    destination = EVIDENCE / ("backup-" + RESTORE)
    destination.mkdir(exist_ok=False)
    refresh()
    evidence = json.loads((EVIDENCE / "e2e.json").read_text())
    route = "/api/v1/predictions/" + evidence["prediction_id"]
    with httpx.Client(timeout=15, trust_env=False) as client:
        before = client.get(BASE + route, headers=headers("engineer")).json()["data"]
    overlay = EVIDENCE / "restore-images.yaml"
    services = {
        name: {"image": IMAGE}
        for name in (
            "api",
            "mlflow",
            "identity",
            "release-import",
            "migrate",
            "release-stage",
        )
    }
    services["postgres"] = {"image": PROJECT + "-postgres:stage3"}
    services["frontend"] = {"image": PROJECT + "-frontend:stage3"}
    overlay.write_text(json.dumps({"services": services}))
    restore_command = [*COMPOSE, "--project-name", RESTORE, "-f", str(overlay)]
    # Refuse existing resources: no overwrite of earlier/user-owned rehearsals.
    existing = binary(
        [
            "docker",
            "volume",
            "ls",
            "--filter",
            "label=com.docker.compose.project=" + RESTORE,
            "-q",
        ]
    )
    if existing.strip():
        raise ValueError("existing restore project refused")
    compose("stop", "frontend", "api", "mlflow")
    inventory = {}
    try:
        for database in ("aletheia_app", "aletheia_mlflow"):
            data = binary(
                [
                    *COMPOSE,
                    "exec",
                    "-T",
                    "postgres",
                    "pg_dump",
                    "-U",
                    "postgres",
                    "-Fc",
                    database,
                ]
            )
            (destination / (database + ".dump")).write_bytes(data)
            inventory[database] = hashlib.sha256(data).hexdigest()
        for name in ("registry", "state", "release"):
            data = volume(PROJECT, name, ARCHIVE)
            (destination / (name + ".tar")).write_bytes(data)
            inventory[name] = hashlib.sha256(data).hexdigest()
    finally:
        compose("start", "mlflow", "api", "frontend")
    try:
        binary([*restore_command, "up", "-d", "--wait", "postgres", "identity"])
        for database in ("aletheia_app", "aletheia_mlflow"):
            binary(
                [
                    *restore_command,
                    "exec",
                    "-T",
                    "postgres",
                    "pg_restore",
                    "-U",
                    "postgres",
                    "--exit-on-error",
                    "-d",
                    database,
                ],
                (destination / (database + ".dump")).read_bytes(),
            )
        for name in ("registry", "state", "release"):
            volume(RESTORE, name, EXTRACT, (destination / (name + ".tar")).read_bytes())
            actual = contents(volume(RESTORE, name, ARCHIVE))
            expected = contents((destination / (name + ".tar")).read_bytes())
            if actual != expected:
                (destination / (name + "-integrity.json")).write_text(
                    json.dumps({"expected": expected, "actual": actual}, indent=2)
                )
                raise AssertionError(f"restored {name} integrity mismatch")
        # A different loopback port keeps the source stack available.
        import os

        env = dict(os.environ, LOCAL_PORT="18081")
        result = subprocess.run(
            [*restore_command, "up", "-d", "--wait", "mlflow", "api", "frontend"],
            cwd=ROOT,
            env=env,
            capture_output=True,
            timeout=360,
        )
        if result.returncode:
            raise RuntimeError("restored stack did not become healthy")
        with httpx.Client(timeout=15, trust_env=False) as client:
            for _ in range(60):
                if (
                    client.get("http://127.0.0.1:18081/api/v1/health/ready").status_code
                    == 200
                ):
                    break
                time.sleep(1)
            else:
                raise AssertionError("restored approval/audit readiness failed")
            assert (
                client.get(
                    "http://127.0.0.1:18081" + route, headers=headers("engineer")
                ).json()["data"]
                == before
            )
            assert (
                client.get(
                    "http://127.0.0.1:18081/api/v1/audit-events/"
                    + evidence["review_event_id"],
                    headers=headers("reviewer"),
                ).status_code
                == 200
            )
            refresh()
            binary(
                [
                    *restore_command,
                    "run",
                    "--rm",
                    "--no-deps",
                    "release-import",
                    "operator",
                    "revoke-release",
                    "--tracking-uri",
                    "http://mlflow:5000",
                    "--token-file",
                    "/run/secrets/operator_token",
                ]
            )
            assert (
                client.get("http://127.0.0.1:18081/api/v1/health/ready").status_code
                == 503
            )
            assert (
                client.post(
                    "http://127.0.0.1:18081/api/v1/predictions",
                    json={
                        "schema_version": "application-v1",
                        "case_id": "synthetic-discharge-v1",
                        "model_version": "1",
                    },
                    headers=headers("engineer", uuid.uuid4()),
                ).status_code
                == 503
            )
        (EVIDENCE / "restore.json").write_text(
            json.dumps(
                {
                    "restore_project": RESTORE,
                    "backup_directory": str(destination.relative_to(ROOT)),
                    "backup_sha256": inventory,
                    "volume_file_hashes_and_modes_identical": True,
                    "restored_prediction_identical": True,
                    "review_audit_link": "passed",
                    "approved_release_readiness": "passed",
                    "revoked_release_refuses_serving": "passed in isolated restore",
                },
                indent=2,
            )
        )
        print(
            "Both databases and three artifact/metadata volumes restored; "
            "prediction, audit link and readiness verified."
        )
    finally:
        binary([*restore_command, "stop"])
    with httpx.Client(timeout=15, trust_env=False) as client:
        wait_ready(client)


if __name__ == "__main__":
    run()
