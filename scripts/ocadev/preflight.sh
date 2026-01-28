#!/usr/bin/env bash
set -euo pipefail

# Prefer explicit overrides
ODOO_COMPOSE_FILE="${ODOO_COMPOSE_FILE:-}"
ODOO_SERVICE="${ODOO_SERVICE:-}"

# Auto-detect compose file if not provided
if [ -z "${ODOO_COMPOSE_FILE}" ]; then
  for f in docker/docker-compose.ce19.yml docker/docker-compose.ce19.yaml infra/docker-compose.prod.yaml infra/docker-compose.prod.yml; do
    if [ -f "$f" ]; then
      ODOO_COMPOSE_FILE="$f"
      break
    fi
  done
fi

if [ -z "${ODOO_COMPOSE_FILE}" ] || [ ! -f "${ODOO_COMPOSE_FILE}" ]; then
  echo "ERROR: Could not detect compose file. Set ODOO_COMPOSE_FILE explicitly." >&2
  exit 1
fi

# Auto-detect Odoo service name if not provided
if [ -z "${ODOO_SERVICE}" ]; then
  # Pick first service name containing "odoo"
  ODOO_SERVICE="$(docker compose -f "${ODOO_COMPOSE_FILE}" config --services | grep -i odoo | head -n 1 || true)"
fi

if [ -z "${ODOO_SERVICE}" ]; then
  echo "ERROR: Could not detect Odoo service. Set ODOO_SERVICE explicitly." >&2
  docker compose -f "${ODOO_COMPOSE_FILE}" config --services || true
  exit 1
fi

echo "OK"
echo "ODOO_COMPOSE_FILE=${ODOO_COMPOSE_FILE}"
echo "ODOO_SERVICE=${ODOO_SERVICE}"

# Print db service (best-effort)
DB_SERVICE="$(docker compose -f "${ODOO_COMPOSE_FILE}" config --services | grep -E '^(db|postgres|postgresql)' | head -n 1 || true)"
if [ -n "${DB_SERVICE}" ]; then
  echo "DB_SERVICE=${DB_SERVICE}"
fi
