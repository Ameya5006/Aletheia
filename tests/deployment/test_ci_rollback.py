"""Run the real CI shell orchestration against controlled external commands."""

import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
pytestmark = pytest.mark.skipif(
    os.name == "nt" or shutil.which("bash") is None,
    reason="The deployment shell runs on the Linux GitHub runner",
)

HARNESS = r"""
az() {
  printf '%s\n' "$*" >> "$TRACE"
  local app=frontend
  [[ " $* " == *" -n api "* ]] && app=api
  case "$1 $2 $3" in
    'deployment group what-if')
      if [[ " $* " == *" --no-pretty-print "* ]]; then
        printf '{"changes":[]}\n'
      else
        printf 'Resource changes: no changes.\n'
      fi ;;
    'containerapp revision list')
      [[ ${NO_TRAFFIC:-0} == 1 ]] || printf '%s--working\n' "$app" ;;
    'containerapp show -g') printf '%s--candidate\n' "$app" ;;
  esac
  return 0
}
pwsh() {
  printf 'pwsh %s\n' "$*" >> "$TRACE"
  if [[ " $* " == *" -Task Smoke "* && ${FAIL_SMOKE:-0} == 1 ]]; then
    return 9
  fi
}
python() {
  if [[ $1 == deployment/azure/ci-guard.py ]]; then return 0; fi
  "$REAL_PYTHON" "$@"
}
export -f az pwsh python
bash "$CI_SCRIPT"
"""


def run_deployment(tmp_path: Path, *, fail_smoke=False, no_traffic=False):
    trace = tmp_path / "commands.log"
    env = {
        **os.environ,
        "TRACE": str(trace),
        "REAL_PYTHON": sys.executable,
        "CI_SCRIPT": str(ROOT / "deployment/azure/ci-deploy.sh"),
        "BACKEND_DIGEST": "sha256:" + "1" * 64,
        "FRONTEND_DIGEST": "sha256:" + "2" * 64,
        "FAIL_SMOKE": str(int(fail_smoke)),
        "NO_TRAFFIC": str(int(no_traffic)),
        "GITHUB_OUTPUT": str(tmp_path / "outputs.txt"),
    }
    process = subprocess.run(
        ["bash", "-c", HARNESS],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    return process, trace.read_text().splitlines()


def test_failed_smoke_restores_the_serving_revision_not_the_latest(tmp_path):
    process, commands = run_deployment(tmp_path, fail_smoke=True)
    assert process.returncode != 0
    restores = [line for line in commands if "revision activate" in line]
    assert any("--revision api--working " in line for line in restores)
    assert any("--revision frontend--working " in line for line in restores)
    assert not any("--candidate" in line for line in restores)
    traffic = [line for line in commands if "ingress traffic set" in line]
    assert "--revision-weight api--working=100 " in traffic[-2]
    assert "--revision-weight frontend--working=100 " in traffic[-1]


def test_no_single_serving_revision_stops_before_migration_or_update(tmp_path):
    process, commands = run_deployment(tmp_path, no_traffic=True)
    assert process.returncode != 0
    assert not any(
        "containerapp update" in line or line.startswith("pwsh ") for line in commands
    )


def test_success_keeps_new_traffic_without_activating_rollback(tmp_path):
    process, commands = run_deployment(tmp_path)
    assert process.returncode == 0, process.stderr
    assert not any("revision activate" in line for line in commands)
    traffic = [line for line in commands if "ingress traffic set" in line]
    assert "--revision-weight api--candidate=100 " in traffic[-2]
    assert "--revision-weight frontend--candidate=100 " in traffic[-1]
