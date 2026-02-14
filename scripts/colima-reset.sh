#!/usr/bin/env bash
set -euo pipefail

# Colima reset script - nuclear option for broken states
# Part of enterprise Docker/DevContainer standards
# WARNING: Destroys all Docker data (images, volumes, containers)

PROFILE="odoo"

echo "⚠️  WARNING: This will DELETE all Docker data for profile '${PROFILE}'"
echo "   - All containers, images, volumes, and networks will be removed"
echo "   - This cannot be undone"
echo ""
read -p "Continue? (yes/NO): " confirm

if [[ "${confirm}" != "yes" ]]; then
  echo "❌ Reset cancelled"
  exit 0
fi

echo ""
echo "🗑️  Resetting Colima profile: ${PROFILE}"

# Stop Colima if running
if colima status -p "${PROFILE}" &>/dev/null; then
  echo "📦 Stopping Colima..."
  ./scripts/colima-down.sh || colima stop -p "${PROFILE}" || true
fi

# Delete Colima profile (removes VM and all Docker data)
echo "🔥 Deleting Colima profile and all data..."
colima delete -p "${PROFILE}" -f || true

# Wait for cleanup
sleep 2

# Restart with clean state
echo ""
echo "🔄 Starting fresh Colima instance..."
./scripts/colima-up.sh

echo ""
echo "✅ Reset complete!"
echo "   - Fresh Colima VM created"
echo "   - All Docker data cleared"
echo "   - Ready for development"
echo ""
echo "ℹ️  Next steps:"
echo "   - Run 'make up' to start services"
echo "   - Or 'docker compose up' directly"
