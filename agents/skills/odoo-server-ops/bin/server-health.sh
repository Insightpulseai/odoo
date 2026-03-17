#!/usr/bin/env bash
# odoo-server-ops: Check Odoo server health
# Usage: server-health.sh [--port <port>]
set -euo pipefail

PORT="${2:-8069}"

HTTP_CODE=$(curl -sf -o /dev/null -w "%{http_code}" "http://localhost:${PORT}/web/health" 2>/dev/null || echo "000")

if [ "${HTTP_CODE}" = "200" ]; then
  echo "HEALTHY: Odoo responding on port ${PORT} (HTTP ${HTTP_CODE})"
  exit 0
else
  echo "UNHEALTHY: Odoo not responding on port ${PORT} (HTTP ${HTTP_CODE})"
  exit 1
fi
