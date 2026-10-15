"""Copy only tracked software and the ten frozen evidence files for offline tests."""

import hashlib
import os
import shutil
import subprocess
import zlib
from pathlib import Path

from aletheia.application.release import AUDIT_FILES, MODEL_FILES, sha

root = Path.cwd()
destination = root / os.environ.get(
    "ALETHEIA_WORKSPACE", "artifacts/stage3-verification/test-workspace"
)
destination.mkdir(parents=True, exist_ok=True)
paths = subprocess.check_output(["git", "ls-files"], text=True).splitlines()
paths += subprocess.check_output(
    ["git", "ls-files", "--others", "--exclude-standard"], text=True
).splitlines()
paths = [
    p
    for p in paths
    if p.startswith(("src/", "tests/", "configs/", "migrations/", "docs/model_cards/"))
]
paths += ["pyproject.toml", "requirements.lock.txt", "alembic.ini"]
delivery = [
    "tests/deployment/test_configuration.py",
    "tests/deployment/test_backup.py",
    "deployment/compose.yaml",
    "deployment/compose.test.yaml",
    "deployment/tests/restore.py",
    "deployment/tests/verify.py",
]
paths += delivery
paths += [f"artifacts/healthcare-model-v1/{n}" for n in MODEL_FILES]
paths += [f"artifacts/healthcare-audit-v1/{n}" for n in AUDIT_FILES]
for name in paths:
    source = root / name
    target = destination / name
    target.parent.mkdir(parents=True, exist_ok=True)
    if name in delivery:
        shutil.copyfile(source, target)
    elif target.exists():
        if sha(source.read_bytes()) != sha(target.read_bytes()):
            raise ValueError(f"existing test workspace differs: {name}")
    else:
        shutil.copyfile(source, target)
    assert sha(source.read_bytes()) == sha(target.read_bytes())
print(f"Prepared {len(paths)} byte-identical software/evidence files; no raw data.")

# Read-only detached metadata snapshot; never copy branches, parents or stash.
metadata = destination / ".git"
metadata.mkdir(exist_ok=True)
head = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
objects = {head}
tree = subprocess.check_output(["git", "rev-parse", "HEAD^{tree}"], text=True).strip()
objects.add(tree)
entries = subprocess.check_output(["git", "ls-tree", "-r", "-t", "HEAD"], text=True)
objects.update(line.split()[2] for line in entries.splitlines())
for oid in sorted(objects):
    kind = subprocess.check_output(["git", "cat-file", "-t", oid], text=True).strip()
    content = subprocess.check_output(["git", "cat-file", kind, oid])
    packed = f"{kind} {len(content)}\0".encode() + content
    assert hashlib.sha1(packed).hexdigest() == oid
    target = metadata / "objects" / oid[:2] / oid[2:]
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(zlib.compress(packed))
(metadata / "refs").mkdir(exist_ok=True)
(metadata / "HEAD").write_text(head + "\n")
(metadata / "config").write_text(
    "[core]\n\tbare = false\n\trepositoryformatversion = 0\n"
)
shutil.copyfile(root / ".git/index", metadata / "index")
print(
    f"Detached read-only Git snapshot: {len(objects)} existing HEAD objects; "
    "no stash/history/branches."
)
