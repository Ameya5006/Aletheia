"""Bind runtime observations, native inventory and every high/critical disposition."""

import json
import subprocess

from scan import IMAGES, summarize
from verify import EVIDENCE

SQLITE_SOURCE = "https://www.sqlite.org/2026/sqlite-autoconf-3540000.tar.gz"
SQLITE_SHA3 = "f5e3e724e9c9b3b5d512c76b02082091a59eeea9becd169a9fbf4d376403acce"


def observations(name):
    code = """import ctypes,hashlib,json,shutil,sqlite3,subprocess
from pathlib import Path
import _sqlite3
assert not hasattr(ctypes.CDLL('libz.so.1'),'zipOpenNewFileInZip4_64')
assert not Path('/usr/lib/systemd/systemd-homed').exists()
assert shutil.which('gcc') is None
library=Path('/usr/local/lib/libsqlite3.so').resolve()
print(json.dumps({'sqlite_version':sqlite3.sqlite_version,
 'sqlite_library':str(library),'sqlite_sha256':hashlib.sha256(library.read_bytes()).hexdigest(),
 'sqlite_linkage':subprocess.check_output(['ldd',_sqlite3.__file__],text=True),
 'git':shutil.which('git'),
 'minizip_files':[str(p) for p in Path('/usr').rglob('*minizip*')],
 'pip_vendor':Path('/usr/local/lib/python3.12/site-packages/pip/_vendor/vendor.txt').read_text(),
 'packages':subprocess.check_output(['dpkg-query','-W','-f=${binary:Package}\\t${Version}\\n'],text=True)}))
"""
    output = subprocess.check_output(
        [
            "docker",
            "run",
            "--rm",
            "--network",
            "none",
            "--read-only",
            "--user",
            "10001:10001",
            "--cap-drop",
            "ALL",
            "--security-opt",
            "no-new-privileges:true",
            "--entrypoint",
            "python",
            IMAGES[name],
            "-c",
            code,
        ],
        text=True,
        timeout=120,
    )
    value = json.loads(output)
    assert value["sqlite_version"] == "3.54.0"
    assert "/usr/local/lib/libsqlite3.so.0" in value["sqlite_linkage"]
    assert not value["minizip_files"]
    assert "libsqlite3-0" not in value["packages"]
    assert bool(value["git"]) == (name == "regression")
    return value


def disposition(issue, target, image, phase):
    cve, package = issue["VulnerabilityID"], issue["PkgName"]
    if cve == "CVE-2025-7458" or package == "libsqlite3-0":
        return (
            "Replaced by checksum-pinned upstream SQLite 3.54.0; old Debian "
            "library removed. Python linkage asserted; full regression must "
            "verify compatibility separately."
        )
    if cve == "CVE-2023-45853":
        return (
            "Retained scanner finding: Debian Bookworm zlib binary excludes "
            "affected contrib/MiniZip; no minizip files installed. No affected "
            "zip-writing API established. Debian marks source ignored; no "
            "Bookworm zlib fix. Reconsider if MiniZip is introduced."
        )
    if target.endswith("gosu"):
        return (
            "Removed unused root-switch binary; Compose enforces UID 70 "
            "directly. Associated Go findings removed from final filesystem; "
            "no root startup supported. Local verification only; cloud uses "
            "managed PostgreSQL."
        )
    if target == "Python":
        return (
            "Pip 26.2.1 vendored tooling; top-level runtime libraries are "
            "setuptools 84.0.0/urllib3 2.8.0. Latest pip remains 26.2.1; vendor "
            "fixes unavailable in a compatible released pip. No runtime pip "
            "install/cache/package-index/unpacker operation in configured "
            "API/MLflow/jobs. Build installs only pinned wheels. Residual risk "
            "if an operator invokes pip on untrusted input; do not do so."
        )
    if package in {"libssl3", "openssl"}:
        return (
            "TLS library reachable for HTTPS JWKS; advisory requires DTLS "
            "retransmission. Configured Python HTTP clients use TLS. No fixed "
            "Bookworm package reported; retain and monitor."
        )
    if package in {"libsystemd0", "libudev1"}:
        return (
            "Library present; affected systemd-homed service is absent and "
            "is not an entrypoint. No home-record processing in configured "
            "services. No fixed Bookworm package reported; retain and monitor."
        )
    if package.startswith("libncurses") or package in {
        "libtinfo6",
        "ncurses-base",
        "ncurses-bin",
    }:
        return (
            "Terminal library/tools present; no interactive terminal or "
            "untrusted terminal database in configured services. No fixed "
            "Bookworm package reported; retain."
        )
    if package.startswith(("perl", "libperl")):
        return (
            "Perl tooling present; configured Python services do not invoke "
            "Perl Archive::Tar on input. Test image Git can invoke trusted "
            "local tooling only; test image never deploys. No fixed Bookworm "
            "package reported."
        )
    if package == "gzip":
        return (
            "Compression utility present; no HTTP route executes gzip on "
            "client-controlled archives. Trusted operator backups are "
            "separately verified. No fixed Bookworm package reported; retain."
        )
    if package == "libacl1":
        return (
            "ACL library present. No untrusted filesystem/ACL ingestion "
            "through the fixed synthetic API. Library reachability through "
            "utilities is possible; no blanket non-exploitability claim. No "
            "fixed Bookworm package reported; retain."
        )
    if package == "libcurl3-gnutls":
        return (
            "Test-only Git dependency. Regression uses local detached Git "
            "objects/status, never remote clone/fetch or untrusted URLs. "
            "Private regression network has no external egress. No fixed "
            "Bookworm package reported; retain in non-deployable test image."
        )
    if package == "libldap-2.5-0":
        return (
            "Test-only Git/curl dependency; no LDAP integration or LDAP URL "
            "processing in the regression runner. Private network has no "
            "external egress. No fixed Bookworm package reported; retain "
            "in non-deployable test image."
        )
    if package == "libexpat1":
        return (
            "XML library in test-only image; no untrusted XML ingestion in "
            "offline synthetic fixtures. Library may be linked; this is "
            "an input-boundary mitigation, not proof of non-exploitability. "
            "No fixed Bookworm package reported; test image never deploys."
        )
    assert package in {
        "bsdutils",
        "libblkid1",
        "libmount1",
        "libsmartcols1",
        "libuuid1",
        "mount",
        "util-linux",
        "util-linux-extra",
    }, f"untriaged component: {package}"
    return (
        "Inherited util-linux package/library; mount/nsenter helpers are not "
        "service entrypoints and have no capabilities, privileged namespace "
        "access or caller-controlled mount inputs. Supporting libraries may "
        "be loaded; no blanket non-exploitability claim. No fixed Bookworm "
        "package reported; retain and monitor."
    )


def run():
    summarize()
    identities = json.loads((EVIDENCE / "scan-summary.json").read_text())[
        "image_identities"
    ]
    runtime = {name: observations(name) for name in ("backend", "regression")}
    rows = []
    licenses = {}
    for phase, directory in (
        ("before", EVIDENCE / "pre-repair-security"),
        ("final", EVIDENCE),
    ):
        if phase == "before" and not directory.exists():
            continue
        for name in ("backend", "postgres", "regression"):
            report = json.loads((directory / f"{name}-scan.json").read_text())
            for section in report.get("Results", []):
                for issue in section.get("Vulnerabilities") or []:
                    if issue["Severity"] not in {"CRITICAL", "HIGH"}:
                        continue
                    rows.append(
                        {
                            "phase": phase,
                            "image": name,
                            "scan_config_digest": report["Metadata"]["ImageID"],
                            "advisory": issue["VulnerabilityID"],
                            "severity": issue["Severity"],
                            "component": issue["PkgName"],
                            "installed": issue["InstalledVersion"],
                            "target": section["Target"],
                            "layer": issue.get("Layer"),
                            "fixed_version_reported": issue.get("FixedVersion") or None,
                            "advisory_url": issue.get("PrimaryURL"),
                            "reachability_mitigation_disposition": disposition(
                                issue, section["Target"], name, phase
                            ),
                            "deployment_context": "production candidate"
                            if name == "backend"
                            else "local PostgreSQL; future cloud database managed"
                            if name == "postgres"
                            else "test-only; never deploy",
                        }
                    )
    for name, identity in identities.items():
        bom = json.loads((EVIDENCE / f"{name}-sbom.json").read_text())
        props = bom["metadata"]["component"]["properties"]
        assert any(
            p["name"] == "aquasecurity:trivy:ImageID"
            and p["value"] == identity["scanned_config_digest"]
            for p in props
        )
        report = json.loads((EVIDENCE / f"{name}-scan.json").read_text())
        licenses[name] = {
            "image_identity": identity,
            "scanner_license_entries": [
                entry
                for section in report.get("Results", [])
                for entry in section.get("Licenses") or []
            ],
        }
        if name == "regression":
            licenses[name]["debian_copyright_inventory"] = json.loads(
                (EVIDENCE / "regression-license-inventory.json").read_text()
            )
            licenses[name]["python_license_inventory"] = (
                "Inherited from exact scanned backend layers; "
                "regression adds Debian Git packages only."
            )
        if name in runtime:
            component = {
                "type": "library",
                "name": "sqlite",
                "version": "3.54.0",
                "bom-ref": "aletheia-native-sqlite-3.54.0",
                "licenses": [
                    {
                        "license": {
                            "name": "Public Domain",
                            "url": "https://www.sqlite.org/copyright.html",
                        }
                    }
                ],
                "hashes": [
                    {"alg": "SHA-256", "content": runtime[name]["sqlite_sha256"]}
                ],
                "externalReferences": [{"type": "distribution", "url": SQLITE_SOURCE}],
                "properties": [
                    {
                        "name": "aletheia:inventory-source",
                        "value": "runtime supplement; not detected by Trivy",
                    },
                    {"name": "aletheia:source-sha3-256", "value": SQLITE_SHA3},
                ],
            }
            if not any(
                c.get("bom-ref") == component["bom-ref"] for c in bom["components"]
            ):
                bom["components"].append(component)
            (EVIDENCE / f"{name}-sbom.json").write_text(json.dumps(bom, indent=2))
            licenses[name]["native_sqlite"] = component
    (EVIDENCE / "repair-license-inventory.json").write_text(
        json.dumps(licenses, indent=2)
    )
    (EVIDENCE / "repair-security-disposition.json").write_text(
        json.dumps(
            {
                "image_identities": identities,
                "runtime_observations": runtime,
                "native_source": {
                    "url": SQLITE_SOURCE,
                    "sha3_256": SQLITE_SHA3,
                    "license": "Public Domain",
                },
                "advisory_sources": [
                    "https://security-tracker.debian.org/tracker/CVE-2025-7458",
                    "https://security-tracker.debian.org/tracker/CVE-2023-45853",
                ],
                "pip_release_check": {
                    "checked_date": "2026-10-14",
                    "latest_version_observed": "26.2.1",
                    "source": "https://pypi.org/pypi/pip/json",
                    "method": "separate read-only PyPI metadata request",
                },
                "findings": rows,
            },
            indent=2,
        )
    )
    print(
        f"Bound {len(rows)} before/final high/critical records and four SBOMs; "
        "native SQLite inventory supplemented explicitly."
    )


if __name__ == "__main__":
    run()
