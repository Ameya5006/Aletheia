#!/bin/sh
set -eu
# The base image's template renderer requires the output directory to exist.
mkdir -p /tmp/nginx-conf
# CSP accepts one exact HTTPS origin, never directives, wildcards or newlines.
if [ -n "${OIDC_CONNECT_SOURCE:-}" ]; then
  printf '%s' "$OIDC_CONNECT_SOURCE" | grep -Eq '^https://[A-Za-z0-9.-]+(:[0-9]{1,5})?$' || {
    echo 'OIDC_CONNECT_SOURCE must be one explicit HTTPS origin' >&2
    exit 1
  }
fi
