#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(git rev-parse --show-toplevel)"
cd "$ROOT_DIR"

echo "=== Building CE19 EE parity image (if needed) ==="
if [ -x ./docker/build-ce19.sh ]; then
  ./docker/build-ce19.sh
else
  echo "⚠️ ./docker/build-ce19.sh not found or not executable (SKIPPING BUILD)"
fi

if [ -x ./docker/test-ce19.sh ]; then
  echo
  echo "=== Running CE19 smoke tests ==="
  ./docker/test-ce19.sh
else
  echo "⚠️ ./docker/test-ce19.sh not found or not executable (SKIPPING TEST)"
fi

echo
echo "=== Starting local dev sandbox (sandbox/dev/docker-compose.yml) ==="
cd "$ROOT_DIR/sandbox/dev"
docker compose up -d

echo
echo "Active Odoo containers:"
docker ps --format "table {{.Names}}\t{{.Image}}\t{{.Status}}" | grep -i odoo || echo "No Odoo containers found"

echo
echo "Try: curl -I http://localhost:8069/web/login"
