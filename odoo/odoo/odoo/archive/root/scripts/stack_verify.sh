#!/usr/bin/env bash
set -euo pipefail

COMPOSE_FILE="infra/stack/docker-compose.stack.yml"
ENV_FILE="infra/stack/.env"

docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" config >/dev/null

docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" up -d --build

echo "[check] containers"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | sed -n '1,200p'

echo "[check] health endpoints (local loopback through containers)"
docker exec ipai-odoo wget -qO- http://localhost:8069/web/health || true
docker exec ipai-n8n wget -qO- http://localhost:5678/healthz || true
docker exec ipai-superset wget -qO- http://localhost:8088/health || true
docker exec ipai-ocr wget -qO- http://localhost:8000/health || true

echo "[ok] stack_verify complete"
