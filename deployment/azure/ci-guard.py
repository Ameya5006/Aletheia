"""Sanitized ARM guard for the frozen existing Azure topology."""

import argparse
import json
import shutil
import subprocess
import urllib.error
import urllib.request


GROUP = "rg-aletheia-workload-sea-01"
ENVIRONMENT = "cae-aletheia-workload-sea-01"
DOMAIN = "whiteflower-9d03c62c.southeastasia.azurecontainerapps.io"
RESOURCES = {ENVIRONMENT, "frontend", "api", "mlflow", "release-operator"}


def verify_private_boundary(name, fqdn, opener=None):
    """Run from outside Azure at each app's real health route and effective host."""
    path = {"api": "/api/v1/health/live", "mlflow": "/health"}[name]
    for host in (fqdn, f"{name}.{DOMAIN}"):
        try:
            with (opener or urllib.request.urlopen)(
                f"https://{host}{path}", timeout=10
            ) as response:
                status = response.status
        except urllib.error.HTTPError as error:
            status = error.code
        assert status == 404, f"public {name} boundary: HTTP {status}"


def az(*arguments: str):
    executable = shutil.which("az") or shutil.which("az.cmd")
    assert executable, "Azure CLI unavailable"
    result = subprocess.run(
        [executable, *arguments, "-o", "json", "--only-show-errors"],
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(result.stdout)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--frontend-digest")
    parser.add_argument("--backend-digest")
    args = parser.parse_args()
    account = az("account", "show")
    assert account["name"] == "Azure for Students" and account["state"] == "Enabled"
    sid = account["id"]
    subscription = az("rest", "--method", "get", "--url", f"https://management.azure.com/subscriptions/{sid}?api-version=2022-12-01")
    assert subscription["subscriptionPolicies"]["spendingLimit"] == "On"
    environment = az("rest", "--method", "get", "--url", f"https://management.azure.com/subscriptions/{sid}/resourceGroups/{GROUP}/providers/Microsoft.App/managedEnvironments/{ENVIRONMENT}?api-version=2026-07-01")
    props = environment["properties"]
    assert props["environmentMode"] == "WorkloadProfiles" and props["provisioningState"] == "Succeeded"
    assert len(props["workloadProfiles"]) == 1 and props["workloadProfiles"][0]["workloadProfileType"] == "Consumption"
    assert not props.get("vnetConfiguration") and not props.get("appLogsConfiguration", {}).get("destination")
    inventory = az("resource", "list", "-g", GROUP)
    assert {r["name"] for r in inventory} == RESOURCES
    assert {r["type"].lower() for r in inventory} == {"microsoft.app/managedenvironments", "microsoft.app/containerapps"}
    for name in ("frontend", "api", "mlflow", "release-operator"):
        app = az("containerapp", "show", "-g", GROUP, "-n", name)
        p = app["properties"]
        assert p["managedEnvironmentId"].lower() == environment["id"].lower()
        assert p["workloadProfileName"] == "Consumption"
        scale = p["template"]["scale"]
        assert scale["maxReplicas"] == 1
        if name != "release-operator":
            assert scale["minReplicas"] == 0
            assert p["configuration"]["activeRevisionsMode"] == "Multiple"
            ingress = p["configuration"]["ingress"]
            assert ingress["external"] == (name == "frontend")
            assert (".internal." in ingress["fqdn"]) == (name != "frontend")
            assert not ingress.get("ipSecurityRestrictions")
            assert ingress["allowInsecure"] is False
            if name in {"api", "mlflow"}:
                verify_private_boundary(name, ingress["fqdn"])
        else:
            assert p["runningStatus"] == "Stopped" and p["configuration"].get("ingress") is None
        container = p["template"]["containers"][0]
        assert "@sha256:" in container["image"]
        assert all(not secret.get("value") for secret in (p["configuration"].get("secrets") or []))
        for entry in container["env"]:
            if entry["name"] in {
                "AZURE_OWNER_DB_URL", "AZURE_APP_DB_URL", "AZURE_MLFLOW_DB_URL",
                "AZURE_OPERATOR_TOKEN", "AZURE_SMOKE_SIGNING_KEY",
            }:
                assert entry.get("secretRef") and not entry.get("value"), f"{name}:{entry['name']} must use a secretRef"
        if name == "api":
            assert container["resources"]["cpu"] == 1 and container["resources"]["memory"] == "2Gi"
            assert any(e.get("name") == "MLFLOW_ENDPOINT" and '"hostname":"mlflow"' in e.get("value", "") for e in container["env"])
            if args.backend_digest:
                assert container["image"].endswith(args.backend_digest)
        if name == "frontend":
            assert any(e.get("name") == "BACKEND_HOST" and e.get("value") == "api" for e in container["env"])
            if args.frontend_digest:
                assert container["image"].endswith(args.frontend_digest)
    print("PASS student spending limit, Consumption-only ARM mode, exact inventory, internal ingress, scale and digest guard")


if __name__ == "__main__":
    main()
