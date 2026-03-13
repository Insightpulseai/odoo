#!/usr/bin/env bash
# =============================================================================
# scripts/supabase/local_up.sh
# =============================================================================
# Start Supabase local stack pinned to Colima profile "odoo".
# Prevents socket mismatch with the default Docker context.
#
# Usage: ./scripts/supabase/local_up.sh
# =============================================================================
set -euo pipefail

COLIMA_PROFILE="odoo"
DOCKER_SOCK="${HOME}/.colima/${COLIMA_PROFILE}/docker.sock"
export DOCKER_HOST="unix://${DOCKER_SOCK}"

echo "🐳 Ensuring Colima profile '${COLIMA_PROFILE}' is running..."
if ! colima status --profile "${COLIMA_PROFILE}" >/dev/null 2>&1; then
  colima start --profile "${COLIMA_PROFILE}"
else
  echo "   Already running."
fi

[[ -S "${DOCKER_SOCK}" ]] || { echo "❌ Socket missing: ${DOCKER_SOCK}" >&2; exit 1; }

echo ""
echo "🚀 Starting Supabase local stack..."
supabase start
echo ""
supabase status
