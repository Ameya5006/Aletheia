#!/bin/sh
set -eu
test "${BACKEND_HOST:-}" = api || { echo 'invalid backend hostname' >&2; exit 1; }
if [ -n "${OIDC_JWKS_PUBLIC:-}" ]; then
  printf '%s' "$OIDC_JWKS_PUBLIC" > /tmp/aletheia-public-jwks.json
else
  printf '%s' '{"keys":[]}' > /tmp/aletheia-public-jwks.json
fi
exec /docker-entrypoint.sh "$@"
