#!/usr/bin/env bash
# Stage Lock Script - Enforce CI-Only Deployment
# Usage: ./scripts/lock_stage.sh
#
# Purpose: Remove system user privileges from staging environment
# to prevent manual modifications. Stage becomes CI-only deployment target.

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

info() {
    echo -e "${GREEN}INFO: $1${NC}"
}

die() {
    echo -e "${RED}ERROR: $1${NC}" >&2
    exit 1
}

# Discover service names from docker-compose.yml
source "$(dirname "$0")/compose_vars.sh" --quiet || die "Failed to detect service names"

info "Locking staging environment to CI-only deployment..."
info "Detected Odoo service: $APP_SVC"

# Verify staging is running
if ! docker compose ps "$APP_SVC" | grep -q "Up"; then
    die "Odoo container is not running. Start with: ENV=stage ./scripts/up.sh"
fi

# Check if we're actually on staging database
CURRENT_DB=$(docker compose exec -T "$APP_SVC" odoo shell -d odoo_stage --no-http <<'PY' 2>/dev/null || echo "FAILED"
import os
print(os.getenv('PGDATABASE', 'unknown'))
PY
)

if [[ ! "$CURRENT_DB" =~ "stage" ]]; then
    die "Not running on staging database. Current: $CURRENT_DB"
fi

info "Removing system privileges from all users..."

# Remove system group from all users
docker compose exec -T "$APP_SVC" odoo shell -d odoo_stage --no-http <<'PY'
# Remove system user privileges
group = env.ref('base.group_system')
users = env['res.users'].sudo().search([])

# Count before
count_before = len([u for u in users if group in u.groups_id])

# Remove group from all users
users.write({'groups_id': [(3, group.id)]})

# Commit changes
env.cr.commit()

# Count after
count_after = len([u for u in users if group in u.groups_id])

print(f"Stage locked: Removed system group from {count_before} users")
print(f"Remaining system users: {count_after}")
PY

if [ $? -eq 0 ]; then
    info "✅ Stage locked successfully"
    info "Staging environment is now CI-only"
    info "Manual system changes are blocked"
    info ""
    info "To unlock (if needed):"
    info "  docker compose exec -T $APP_SVC odoo shell -d odoo_stage"
    info "  >>> admin = env.ref('base.user_admin')"
    info "  >>> group = env.ref('base.group_system')"
    info "  >>> admin.write({'groups_id': [(4, group.id)]})"
    info "  >>> env.cr.commit()"
else
    die "Failed to lock staging environment"
fi
