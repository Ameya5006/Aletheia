"""Digest-pinned disposable scanner reads image archives, never the Docker socket."""

import hashlib
import json
import subprocess
import sys
import tarfile

from verify import EVIDENCE, ROOT

SCANNER = (
    "aquasec/trivy:0.75.0@sha256:"
    "af6acf9a6b85dfe389a1941505c0ce9efef52a4719635e1a962f022a3d855daa"
)
IMAGES = {
    "backend": "aletheia-stage3-test-backend:stage3",
    "frontend": "aletheia-stage3-test-frontend:stage3",
    "postgres": "aletheia-stage3-test-postgres:stage3",
    "regression": "aletheia-stage3-test-regression:stage3",
}


def regression_licenses():
    code = """import hashlib,json,re,subprocess
from pathlib import Path
rows=subprocess.check_output(
    ['dpkg-query','-W','-f=${binary:Package}\\t${Version}\\n'],text=True)
inventory=[]
for row in rows.splitlines():
    name,version=row.split('\\t')
    path=Path('/usr/share/doc')/name.split(':')[0]/'copyright'
    data=path.read_bytes() if path.is_file() else b''
    inventory.append({'name':name,'version':version,'copyright_file':str(path),
        'copyright_sha256':hashlib.sha256(data).hexdigest() if data else None,
        'license_headers':sorted(set(re.findall(r'^License:\\s*(.+)$',
            data.decode('utf-8',errors='replace'),re.M)))})
print(json.dumps(inventory))
"""
    result = subprocess.check_output(
        [
            "docker",
            "run",
            "--rm",
            "--network",
            "none",
            "--user",
            "10001:10001",
            "--cap-drop",
            "ALL",
            "--security-opt",
            "no-new-privileges:true",
            "--read-only",
            "--memory",
            "128m",
            "--cpus",
            "0.5",
            "--entrypoint",
            "python",
            IMAGES["regression"],
            "-c",
            code,
        ],
        text=True,
        timeout=120,
    )
    inventory = json.loads(result)
    assert any(p["name"] == "git" and p["copyright_sha256"] for p in inventory)
    (EVIDENCE / "regression-license-inventory.json").write_text(
        json.dumps(inventory, indent=2)
    )
    print(f"Recorded {len(inventory)} test-image Debian package/copyright records.")


def summarize():
    counts, identities = {}, {}
    for name, image in IMAGES.items():
        report = json.loads((EVIDENCE / f"{name}-scan.json").read_text())
        with tarfile.open(EVIDENCE / (name + ".tar")) as archive:
            manifest = json.load(archive.extractfile("manifest.json"))
            selected = next(item for item in manifest if image in item["RepoTags"])
            config = archive.extractfile(selected["Config"]).read()
            config_digest = "sha256:" + hashlib.sha256(config).hexdigest()
            assert config_digest == report["Metadata"]["ImageID"]
        inspected = json.loads(
            subprocess.check_output(["docker", "image", "inspect", image], text=True)
        )[0]
        assert json.loads(config)["rootfs"]["diff_ids"] == inspected["RootFS"]["Layers"]
        identities[name] = {
            "docker_index_digest": inspected["Id"],
            "scanned_config_digest": config_digest,
            "exported_layers_match_runtime": True,
        }
        severity = {}
        for section in report.get("Results", []):
            for issue in section.get("Vulnerabilities") or []:
                level = issue["Severity"]
                severity[level] = severity.get(level, 0) + 1
        counts[name] = severity
    (EVIDENCE / "scan-summary.json").write_text(
        json.dumps(
            {
                "scanner": SCANNER,
                "severity_counts": counts,
                "image_identities": identities,
            },
            indent=2,
        )
    )
    print(
        "Scanner config digests and exported runtime layers match "
        f"all {len(IMAGES)} images."
    )


def run():
    cache = EVIDENCE / "scanner-cache"
    cache.mkdir(exist_ok=True)
    cache_volume = "aletheia-stage3-scanner-cache"
    existing = subprocess.run(
        ["docker", "volume", "inspect", cache_volume],
        capture_output=True,
        text=True,
    )
    if existing.returncode == 0:
        assert (
            json.loads(existing.stdout)[0]["Labels"].get("aletheia.owner")
            == "stage3-scanner"
        )
    else:
        subprocess.run(
            [
                "docker",
                "volume",
                "create",
                "--label",
                "aletheia.owner=stage3-scanner",
                cache_volume,
            ],
            check=True,
            capture_output=True,
        )
    base = [
        "docker",
        "run",
        "--rm",
        "--user",
        "10001:10001",
        "--cap-drop",
        "ALL",
        "--security-opt",
        "no-new-privileges:true",
        "--read-only",
        "--tmpfs",
        "/tmp:rw,nosuid,size=512m",
        "--memory",
        "1g",
        "--cpus",
        "1",
        "--mount",
        f"type=bind,source={EVIDENCE.as_posix()},target=/evidence",
        "--mount",
        f"type=volume,source={cache_volume},target=/cache",
        SCANNER,
        "image",
        "--cache-dir",
        "/cache",
        "--timeout",
        "15m",
    ]
    summary = {}
    for name, image in IMAGES.items():
        if "--only-regression" in sys.argv and name != "regression":
            continue
        if "--only-changed" in sys.argv and name == "frontend":
            continue
        archive = EVIDENCE / (name + ".tar")
        subprocess.run(
            ["docker", "save", "--output", str(archive), image],
            cwd=ROOT,
            check=True,
            timeout=360,
        )
        copy_code = """from pathlib import Path
import shutil
source=Path('/evidence')
target=Path('/registry')
shutil.copyfile(source/NAME,target/NAME)
old=source/'scanner-cache/db'
if old.is_dir() and not (target/'db').exists():
    shutil.copytree(old,target/'db')
""".replace("NAME", repr(archive.name))
        subprocess.run(
            [
                "docker",
                "run",
                "--rm",
                "--network",
                "none",
                "--user",
                "10001:10001",
                "--cap-drop",
                "ALL",
                "--security-opt",
                "no-new-privileges:true",
                "--read-only",
                "--memory",
                "128m",
                "--cpus",
                "1",
                "--mount",
                f"type=bind,source={EVIDENCE.as_posix()},target=/evidence,readonly",
                "--mount",
                f"type=volume,source={cache_volume},target=/registry",
                "--entrypoint",
                "python",
                IMAGES["backend"],
                "-c",
                copy_code,
            ],
            check=True,
            timeout=360,
        )
        for kind, options in (
            (
                "scan",
                [
                    "--scanners",
                    "vuln" if name == "regression" else "vuln,license",
                    "--format",
                    "json",
                ],
            ),
            ("sbom", ["--format", "cyclonedx"]),
        ):
            result = subprocess.run(
                [
                    *base,
                    "--input",
                    "/cache/" + archive.name,
                    *options,
                    "--output",
                    f"/evidence/{name}-{kind}.json",
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
                timeout=1000,
            )
            (EVIDENCE / f"{name}-{kind}.log").write_text(
                result.stdout + result.stderr, encoding="utf-8"
            )
            if result.returncode:
                raise RuntimeError(f"{name} {kind} failed; inspect ignored scanner log")
        result = json.loads((EVIDENCE / f"{name}-scan.json").read_text())
        counts = {}
        for section in result.get("Results", []):
            for issue in section.get("Vulnerabilities") or []:
                severity = issue["Severity"]
                counts[severity] = counts.get(severity, 0) + 1
        summary[name] = counts
        print(name, counts, flush=True)
    regression_licenses()
    summarize()


if __name__ == "__main__":
    run()
