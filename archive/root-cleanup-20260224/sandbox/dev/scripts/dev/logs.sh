#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════════════════════
# View Odoo Dev Sandbox Logs
# ═══════════════════════════════════════════════════════════════════════════════
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO_ROOT"

SERVICE="${1:-odoo}"

echo "📋 Showing logs for: $SERVICE"
echo "   (Ctrl+C to exit)"
echo ""

docker compose logs -f --tail=100 "$SERVICE"
