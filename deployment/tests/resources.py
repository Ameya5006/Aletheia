"""Measured local idle/bounded-workload evidence, with sanitized Docker inspection."""

import json
import subprocess
import threading
import time
import uuid

import httpx
from verify import BASE, EVIDENCE, ROOT, compose, headers, refresh, wait_ready


def docker(*args):
    return subprocess.check_output(["docker", *args], cwd=ROOT, text=True, timeout=60)


def stats(ids):
    return [
        json.loads(line)
        for line in docker(
            "stats", "--no-stream", "--format", "{{json .}}", *ids
        ).splitlines()
    ]


def run():
    refresh()
    compose("stop", "frontend", "api", "mlflow", "postgres", "identity")
    cold_start = time.monotonic()
    compose(
        "up",
        "-d",
        "--force-recreate",
        "--wait",
        "postgres",
        "identity",
        "mlflow",
        "api",
        "frontend",
    )
    with httpx.Client(timeout=15, trust_env=False) as client:
        wait_ready(client)
    cold_seconds = time.monotonic() - cold_start
    ids = compose("ps", "-q").splitlines()
    inspected = json.loads(docker("inspect", *ids))
    inspected = [
        item
        for item in inspected
        if item["Config"]["Labels"]["com.docker.compose.service"]
        in {"postgres", "identity", "mlflow", "api", "frontend"}
    ]
    ids = [item["Id"] for item in inspected]
    containers = []
    for item in inspected:
        assert item["Config"]["User"].split(":")[0] not in {"", "0", "root"}
        assert item["HostConfig"]["CapDrop"] == ["ALL"]
        containers.append(
            {
                "name": item["Name"],
                "user": item["Config"]["User"],
                "image": item["Image"],
                "cap_drop": item["HostConfig"]["CapDrop"],
                "security_opt": item["HostConfig"]["SecurityOpt"],
                "read_only": item["HostConfig"]["ReadonlyRootfs"],
                "ports": item["NetworkSettings"]["Ports"],
                "volumes": [m["Name"] for m in item["Mounts"] if m["Type"] == "volume"],
            }
        )
    image_names = sorted({item["Config"]["Image"] for item in inspected})
    images = [
        {"name": item["RepoTags"], "id": item["Id"], "size_bytes": item["Size"]}
        for item in json.loads(docker("image", "inspect", *image_names))
    ]
    # Runtime mounts hold only synthetic application state and approved evidence.
    privacy = compose(
        "exec",
        "-T",
        "api",
        "python",
        "-c",
        "from pathlib import Path; "
        "from aletheia.application.release import VerifiedRelease; import os; "
        "assert all(not Path(p).exists() for p in "
        "['/app/data','/app/tests','/app/.venv','/app/frontend','/app/.git']); "
        "assert not list(Path('/app/artifacts').iterdir()); "
        "VerifiedRelease(Path('/release/current'),os.environ['APP_RELEASE_SHA256']); "
        "print('software-only image and verified publication-safe release')",
    ).strip()
    columns = compose(
        "exec",
        "-T",
        "postgres",
        "psql",
        "-U",
        "postgres",
        "-d",
        "aletheia_app",
        "-X",
        "-Atc",
        "SELECT column_name FROM information_schema.columns "
        "WHERE table_schema='public';",
    )
    assert "patient_nbr" not in columns and "encounter_id" not in columns
    logs = compose("logs", "--no-color", "api", "frontend", "mlflow", "postgres")
    assert "patient_nbr" not in logs and "encounter_id" not in logs
    compose("exec", "-T", "api", "python", "-m", "pip", "check")
    inventory = json.loads(
        compose(
            "exec",
            "-T",
            "api",
            "python",
            "-c",
            "import json; from pathlib import Path; "
            "from importlib.metadata import version,metadata; "
            "from packaging.requirements import Requirement; "
            "pins=[Requirement(s) for s in "
            "Path('/app/requirements.lock.txt').read_text().splitlines() if s]; "
            "pins=[p for p in pins if p.marker is None or p.marker.evaluate()]; "
            "assert all(version(p.name) in p.specifier for p in pins); "
            "print(json.dumps([{'name':p.name,'version':version(p.name),"
            "'license':metadata(p.name).get('License-Expression') or "
            "metadata(p.name).get('License'),'classifiers':"
            "metadata(p.name).get_all('Classifier',[])} for p in pins]))",
        )
    )
    idle = [stats(ids) for _ in range(3)]
    samples = []
    stop = threading.Event()

    def sample():
        while not stop.is_set():
            samples.append(stats(ids))

    thread = threading.Thread(target=sample)
    elapsed = []
    thread.start()
    try:
        with httpx.Client(timeout=15, trust_env=False) as client:
            wait_ready(client)
            for _ in range(10):
                started = time.monotonic()
                response = client.post(
                    BASE + "/api/v1/predictions",
                    json={
                        "schema_version": "application-v1",
                        "case_id": "synthetic-discharge-v1",
                        "model_version": "1",
                    },
                    headers=headers("engineer", uuid.uuid4()),
                )
                assert response.status_code == 201
                elapsed.append(time.monotonic() - started)
    finally:
        stop.set()
        thread.join(timeout=65)
    assert not thread.is_alive() and samples
    result = {
        "cold_container_start_seconds": cold_seconds,
        "startup_scope": (
            "fresh containers, existing approved volumes and cached images; "
            "excludes engine boot/build/import"
        ),
        "containers": containers,
        "images": images,
        "privacy_checks": [privacy, "no patient identifier columns or logged fields"],
        "locked_dependencies_match": True,
        "dependency_license_inventory": inventory,
        "idle_samples": idle,
        "workload_samples": samples,
        "synthetic_request_seconds": elapsed,
        "workload": "10 sequential fixed synthetic predictions; one client",
        "measurement_context": (
            "Local Docker Desktop on an 8 GB laptop; other host/Docker work may "
            "be running. Samples include only the five serving/test-identity "
            "containers, not regression, restore or builder helpers."
        ),
    }
    (EVIDENCE / "resources.json").write_text(json.dumps(result, indent=2))
    print(
        "Image/runtime controls and 3 idle samples recorded; "
        "10 synthetic requests sampled."
    )


if __name__ == "__main__":
    run()
