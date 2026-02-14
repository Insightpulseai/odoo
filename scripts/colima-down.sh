#!/usr/bin/env bash
set -euo pipefail

# Colima shutdown script - graceful Docker daemon stop
# Part of enterprise Docker/DevContainer standards

PROFILE="odoo"

echo "🛑 Stopping Colima profile: ${PROFILE}"

# Check if Colima is running
if ! colima status -p "${PROFILE}" &>/dev/null; then
  echo "ℹ️  Colima '${PROFILE}' not running"
  exit 0
fi

# Stop Docker Compose services first (graceful shutdown)
if docker compose ps --format table 2>/dev/null | grep -q "ipai"; then
  echo "📦 Stopping Docker Compose services..."
  docker compose down || echo "⚠️  Docker Compose down failed (continuing)"
fi

# Stop Colima
echo "🔄 Stopping Colima VM..."
colima stop -p "${PROFILE}"

# Verify shutdown
if ! colima status -p "${PROFILE}" &>/dev/null; then
  echo "✅ Colima '${PROFILE}' stopped successfully"
else
  echo "⚠️  Colima may still be running"
  colima status -p "${PROFILE}"
fi

echo ""
echo "✨ Colima stopped. Resources freed."
echo "   - To restart: ./scripts/colima-up.sh or make colima-up"
