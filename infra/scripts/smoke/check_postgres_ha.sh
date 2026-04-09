#!/usr/bin/env bash
set -euo pipefail

: "${RESOURCE_GROUP:?RESOURCE_GROUP is required}"
: "${POSTGRES_SERVER_NAME:?POSTGRES_SERVER_NAME is required}"

server_json="$(
  az postgres flexible-server show \
    --resource-group "$RESOURCE_GROUP" \
    --name "$POSTGRES_SERVER_NAME" \
    -o json
)"

echo "$server_json" | jq '.highAvailability'

ha_mode="$(echo "$server_json" | jq -r '.highAvailability.mode // empty')"
if [[ -z "$ha_mode" ]]; then
  echo "High availability is not enabled or property is missing." >&2
  exit 1
fi

echo "PostgreSQL HA mode: $ha_mode"

if [[ -n "${PGHOST:-}" && -n "${PGDATABASE:-}" && -n "${PGUSER:-}" && -n "${PGPASSWORD:-}" ]]; then
  psql "sslmode=require" -c 'select 1;'
fi
