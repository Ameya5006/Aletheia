"""Verify frozen fixtures from the existing image in an ephemeral CI checkout."""

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RELEASE = "65f2302cc9c4795142567296cc6b16143fad5abfe4df7b04152975748c2ec271"


def main() -> None:
    manifest = json.loads(
        (ROOT / "deployment/azure/approved-release-manifest.json").read_text()
    )
    canonical = json.dumps(manifest, sort_keys=True, separators=(",", ":")).encode()
    assert hashlib.sha256(canonical).hexdigest() == RELEASE
    restored = []
    artifacts = 0
    for name, expected in manifest["files"].items():
        path = ROOT / name
        content = path.read_bytes()
        if hashlib.sha256(content).hexdigest() != expected:
            assert not name.startswith("artifacts/"), "Frozen fixture hash mismatch"
            original = content.replace(b"\r\n", b"\n").replace(b"\n", b"\r\n")
            assert hashlib.sha256(original).hexdigest() == expected, (
                f"Frozen source content mismatch: {name}"
            )
            # Only the disposable hosted checkout is restored to approved bytes.
            path.write_bytes(original)
            restored.append(name)
        if name.startswith("artifacts/"):
            artifacts += 1
    print(f"Verified {artifacts} frozen aggregate/model fixtures from immutable image")
    print(f"Restored approved checkout line endings for: {', '.join(restored)}")


if __name__ == "__main__":
    main()
