"""Fail CI if tracked frozen release inputs diverge from approved identities."""

import hashlib
import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "deployment/azure/approved-release-manifest.json"
ENTRYPOINT_SHA256 = "2f4ae33f80e67df8729d400478d32eab54560914904a713d889e0211a7f4b082"
RELEASE_SHA256 = "65f2302cc9c4795142567296cc6b16143fad5abfe4df7b04152975748c2ec271"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    canonical = json.dumps(manifest, sort_keys=True, separators=(",", ":")).encode()
    assert hashlib.sha256(canonical).hexdigest() == RELEASE_SHA256, "approved release manifest changed"
    tracked = set(
        subprocess.check_output(["git", "ls-files"], cwd=ROOT, text=True).splitlines()
    )
    checked = 0
    for name, expected in manifest["files"].items():
        if name in tracked:
            assert digest(ROOT / name) == expected, f"frozen input changed: {name}"
            checked += 1
        elif not name.startswith("artifacts/"):
            raise AssertionError(f"approved input missing from Git: {name}")
    assert checked >= 20, "insufficient tracked release inputs"
    assert digest(ROOT / "deployment/entrypoint.py") == ENTRYPOINT_SHA256
    pin = json.loads((ROOT / "deployment/azure/cloud-deployment-pin.json").read_text())
    assert pin["action"] == "activated" and pin["active"]["release_sha256"] == RELEASE_SHA256
    print(f"Frozen source check passed for {checked} tracked inputs, entrypoint and cloud pin")


if __name__ == "__main__":
    main()
