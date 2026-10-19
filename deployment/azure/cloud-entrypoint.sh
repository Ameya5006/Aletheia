#!/bin/sh
set -eu
umask 077

# Express supports Azure secret-backed environment variables but no Secret
# volume. Materialize only the credentials needed by this replica into the
# existing container entrypoint's private, ephemeral file interface.
# Express mounts /run afresh, hiding directories prepared in the image. Create
# the directory as root, then execute the remainder and all long-lived Python
# code as the unprivileged application UID.
if [ "$(id -u)" -eq 0 ]; then
  install -d -m 0700 -o 10001 -g 10001 /run/secrets
  exec setpriv --reuid 10001 --regid 10001 --clear-groups "$0" "$@"
fi
test -w /run/secrets
if [ -n "${AZURE_APP_DB_URL:-}" ]; then
  printf '%s' "$AZURE_APP_DB_URL" > /run/secrets/app_db_url
fi
if [ -n "${AZURE_OWNER_DB_URL:-}" ]; then
  printf '%s' "$AZURE_OWNER_DB_URL" > /run/secrets/owner_db_url
fi
if [ -n "${AZURE_MLFLOW_DB_URL:-}" ]; then
  printf '%s' "$AZURE_MLFLOW_DB_URL" > /run/secrets/mlflow_db_url
fi
unset AZURE_APP_DB_URL AZURE_OWNER_DB_URL AZURE_MLFLOW_DB_URL
if [ "${1:-}" = mlflow ]; then
  # Workload Profiles service discovery sends Host: mlflow at port 80.
  # Keep this cloud-only host allowance out of the frozen Python application.
  exec python -m mlflow server \
    --host 0.0.0.0 --port 5000 --workers 1 \
    --backend-store-uri "$(cat /run/secrets/mlflow_db_url)" \
    --serve-artifacts --artifacts-destination /registry/artifacts \
    --allowed-hosts 'mlflow,mlflow:80,mlflow:5000,localhost:5000,127.0.0.1:5000'
fi
exec python /app/deployment/entrypoint.py "$@"
