#!/usr/bin/env bash
# =============================================================================
# scripts/supabase/local_down.sh
# =============================================================================
# Stop Supabase local stack (optionally the Colima VM too).
#
# Usage:
#   ./scripts/supabase/local_down.sh           # stop Supabase only
#   ./scripts/supabase/local_down.sh --full    # stop Supabase + Colima VM
# =============================================================================
set -euo pipefail

COLIMA_PROFILE="odoo"
export DOCKER_HOST="unix://${HOME}/.colima/${COLIMA_PROFILE}/docker.sock"

echo "🛑 Stopping Supabase local stack..."
supabase stop || true

if [[ "${1:-}" == "--full" ]]; then
  echo "🛑 Stopping Colima profile '${COLIMA_PROFILE}'..."
  colima stop --profile "${COLIMA_PROFILE}" || true
else
  echo "ℹ️  Colima still running (pass --full to stop VM too)."
fi
echo "✅ Done."
