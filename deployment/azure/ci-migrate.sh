#!/bin/sh
set -eu
umask 077

# A controlled, no-ingress Container App revision runs this one-time command.
# The owner URL remains an Azure secretRef and is never included in arguments.
if [ "$(id -u)" -eq 0 ]; then
  install -d -m 0700 -o 10001 -g 10001 /run/secrets
  exec setpriv --reuid 10001 --regid 10001 --clear-groups "$0" "$@"
fi
test -w /run/secrets
test -n "${AZURE_OWNER_DB_URL:-}"
printf '%s' "$AZURE_OWNER_DB_URL" > /run/secrets/owner_db_url
unset AZURE_OWNER_DB_URL
export ALETHEIA_MIGRATION_URL="$(cat /run/secrets/owner_db_url)"
python -m alembic upgrade head
python -m alembic current | grep -q '0004_case_input (head)'
echo 'aletheia-migration-complete 0004_case_input'
# Leave a short inspection window before the pipeline stops this revision.
sleep 600
