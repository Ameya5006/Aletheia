#!/usr/bin/env bash
set -euo pipefail

group=rg-aletheia-workload-sea-01
registry=acraletheiasea1017.azurecr.io
[[ ${BACKEND_DIGEST:-} =~ ^sha256:[0-9a-f]{64}$ ]] || { echo 'Backend digest invalid' >&2; exit 1; }
[[ ${FRONTEND_DIGEST:-} =~ ^sha256:[0-9a-f]{64}$ ]] || { echo 'Frontend digest invalid' >&2; exit 1; }

python deployment/azure/ci-guard.py
name="aletheia-ci-${GITHUB_RUN_ID:-local}"
az deployment group validate -g "$group" -n "$name" -f deployment/azure/ci-plan.bicep -o none --only-show-errors
preview=$(mktemp)
trap 'rm -f "$preview"' EXIT
az deployment group what-if -g "$group" -n "$name" -f deployment/azure/ci-plan.bicep -o json --only-show-errors > "$preview"
python - "$preview" <<'PY'
import json
import sys
changes = json.load(open(sys.argv[1], encoding="utf-8")).get("changes") or []
assert all(item["changeType"] in ("NoChange", "Ignore") for item in changes), "Bicep preview changes frozen resources"
print("Existing-resource Bicep validation and what-if passed")
PY

before_api=$(az containerapp revision list -g "$group" -n api --query '[?properties.trafficWeight==`100`].name' -o tsv --only-show-errors)
before_frontend=$(az containerapp revision list -g "$group" -n frontend --query '[?properties.trafficWeight==`100`].name' -o tsv --only-show-errors)
[[ $before_api =~ ^api--[a-z0-9-]+$ && $before_frontend =~ ^frontend--[a-z0-9-]+$ ]] || { echo 'A single serving revision is required for rollback' >&2; exit 1; }
if [[ -n ${GITHUB_OUTPUT:-} ]]; then
  printf 'previous_api_revision=%s\nprevious_frontend_revision=%s\n' "$before_api" "$before_frontend" >> "$GITHUB_OUTPUT"
fi

rollback() {
  echo 'Deployment verification failed; restoring previous working traffic revisions' >&2
  az containerapp revision activate -g "$group" -n api --revision "$before_api" -o none --only-show-errors || true
  az containerapp revision activate -g "$group" -n frontend --revision "$before_frontend" -o none --only-show-errors || true
  az containerapp ingress traffic set -g "$group" -n api --revision-weight "$before_api=100" -o none --only-show-errors || true
  az containerapp ingress traffic set -g "$group" -n frontend --revision-weight "$before_frontend=100" -o none --only-show-errors || true
}
trap 'rollback; rm -f "$preview"' ERR

pwsh -NoProfile -File deployment/azure/ci-migrate.ps1 -BackendDigest "$BACKEND_DIGEST" -Task Migration
# Pin live traffic to the known-good revisions while the new revisions start.
az containerapp ingress traffic set -g "$group" -n api --revision-weight "$before_api=100" -o none --only-show-errors
az containerapp ingress traffic set -g "$group" -n frontend --revision-weight "$before_frontend=100" -o none --only-show-errors
az containerapp update -g "$group" -n api --image "$registry/backend@$BACKEND_DIGEST" -o none --only-show-errors
az containerapp update -g "$group" -n frontend --image "$registry/frontend@$FRONTEND_DIGEST" -o none --only-show-errors
python deployment/azure/ci-guard.py --backend-digest "$BACKEND_DIGEST" --frontend-digest "$FRONTEND_DIGEST"
new_api=$(az containerapp show -g "$group" -n api --query properties.latestRevisionName -o tsv --only-show-errors)
new_frontend=$(az containerapp show -g "$group" -n frontend --query properties.latestRevisionName -o tsv --only-show-errors)
[[ -n $new_api && -n $new_frontend ]] || { echo 'New revision names unavailable' >&2; exit 1; }
az containerapp ingress traffic set -g "$group" -n api --revision-weight "$new_api=100" -o none --only-show-errors
az containerapp ingress traffic set -g "$group" -n frontend --revision-weight "$new_frontend=100" -o none --only-show-errors
pwsh -NoProfile -File deployment/azure/ci-migrate.ps1 -BackendDigest "$BACKEND_DIGEST" -Task Smoke
python deployment/azure/ci-guard.py --backend-digest "$BACKEND_DIGEST" --frontend-digest "$FRONTEND_DIGEST"
trap 'rm -f "$preview"' ERR
echo 'Azure digest deployment, migration, public smoke prediction and private-ingress guard passed'
