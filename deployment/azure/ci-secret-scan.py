"""Fail closed on credential material in deployable source and built assets."""

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TARGETS = (ROOT / ".github/workflows", ROOT / "deployment/azure", ROOT / "frontend/dist")
SUFFIXES = {".yml", ".yaml", ".json", ".py", ".ps1", ".sh", ".bicep", ".js", ".css", ".html"}
PATTERNS = {
    "private-key": re.compile(b"-----BEGIN " + b"PRIVATE KEY-----"),
    "rsa-private-key": re.compile(b"-----BEGIN RSA " + b"PRIVATE KEY-----"),
    "access-token": re.compile(rb"eyJ[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}"),
    "literal-db-password": re.compile(rb"postgresql(?:\+psycopg)?://[A-Za-z0-9_-]+:[A-Za-z0-9_-]{16,}@"),
}


def main() -> None:
    checked = 0
    findings = []
    for base in TARGETS:
        if not base.exists():
            continue
        for path in base.rglob("*"):
            if not path.is_file() or path.suffix not in SUFFIXES:
                continue
            if "__pycache__" in path.parts or path.name == Path(__file__).name:
                continue
            data = path.read_bytes()
            checked += 1
            for label, pattern in PATTERNS.items():
                if pattern.search(data):
                    findings.append((str(path.relative_to(ROOT)), label))
    assert not findings, f"Credential-like content found (paths only): {findings}"
    print(f"Credential pattern scan passed for {checked} deployable source/asset files")


if __name__ == "__main__":
    main()
