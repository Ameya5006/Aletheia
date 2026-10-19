#!/bin/sh
set -eu
umask 077

# Run only in the stopped-by-default, no-ingress release operator app.
if [ "$(id -u)" -eq 0 ]; then
  install -d -m 0700 -o 10001 -g 10001 /run/secrets
  exec setpriv --reuid 10001 --regid 10001 --clear-groups "$0" "$@"
fi
test -w /run/secrets
test -n "${AZURE_SMOKE_SIGNING_KEY:-}"
printf '%s' "$AZURE_SMOKE_SIGNING_KEY" > /run/secrets/smoke_signing_key.pem
unset AZURE_SMOKE_SIGNING_KEY
python /app/deployment/azure/ci-smoke.py
echo 'aletheia-smoke-complete'
sleep 600
