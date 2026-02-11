#!/usr/bin/env bash
set -euo pipefail

: "${DO_CLUSTER_ID:?set DO_CLUSTER_ID (odoo-db-sgp1 cluster id)}"
: "${SUPERSET_DB_NAME:=superset}"
: "${SUPERSET_CONTAINER:=superset-prod}"

echo "== ensure database exists =="
# If db already exists, doctl returns non-zero; tolerate that safely
doctl databases db create "$DO_CLUSTER_ID" "$SUPERSET_DB_NAME" >/dev/null 2>&1 || true

echo "== run migrations =="
docker exec "$SUPERSET_CONTAINER" superset db upgrade

echo "== init superset =="
docker exec "$SUPERSET_CONTAINER" superset init

echo "OK"
