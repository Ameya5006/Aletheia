"""Bounded, sanitized observation of the controlled Azure operator logs."""

import argparse
import json
import re
import shutil
import subprocess

MARKERS = {
    "Migration": "aletheia-migration-complete 0004_case_input",
    "Smoke": "aletheia-smoke-complete",
}


def observe(task, runner=None, revision=None):
    command = [
        shutil.which("az") or shutil.which("az.cmd") or "az",
        "containerapp",
        "logs",
        "show",
        "-g",
        "rg-aletheia-workload-sea-01",
        "-n",
        "release-operator",
        "--type",
        "console",
        "--tail",
        "60",
        "--format",
        "text",
        "--only-show-errors",
    ]
    if revision:
        assert re.fullmatch(r"release-operator--[a-z0-9-]+", revision)
        command.extend(["--revision", revision])
    try:
        process = (runner or subprocess.run)(
            command,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=30,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return {"status": "timeout"}
    content = (process.stdout or "") + (process.stderr or "")
    if re.search(
        r"BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY|postgresql(?:\+psycopg)?://|"
        r"eyJ[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}",
        content,
    ):
        return {"status": "credential_exposure"}
    if process.returncode:
        if re.search(r"AuthorizationFailed|Forbidden|\b40[13]\b", content, re.I):
            return {
                "status": "authorization_denied",
                "actions": sorted(
                    set(
                        re.findall(
                            r"Microsoft\.App/[A-Za-z0-9/]+/(?:action|read|write)",
                            content,
                        )
                    )
                ),
            }
        diagnostic = re.sub(r"\x1b\[[0-9;]*m", "", process.stderr or "")
        diagnostic = re.sub(
            r"[0-9a-fA-F]{8}(?:-[0-9a-fA-F]{4}){3}-[0-9a-fA-F]{12}",
            "<identifier>",
            diagnostic,
        )
        diagnostic = re.sub(
            r"https?://\S+|[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+", "<address>", diagnostic
        )
        diagnostic = re.sub(r"(?i)bearer\s+\S+", "Bearer <redacted>", diagnostic)
        return {"status": "cli_error", "diagnostic": diagnostic[:500]}
    if MARKERS[task] not in (process.stdout or ""):
        return {"status": "pending"}
    result = {"status": "complete"}
    probability = re.search(
        r"smoke prediction saved and audited: probability=([0-9.]+); "
        r"(?:private apps=404|internal health=200)",
        content,
    )
    if probability:
        value = float(probability[1])
        assert 0 <= value <= 1
        result["probability"] = value
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--task", choices=MARKERS, required=True)
    parser.add_argument("--revision")
    args = parser.parse_args()
    print(json.dumps(observe(args.task, revision=args.revision)))
