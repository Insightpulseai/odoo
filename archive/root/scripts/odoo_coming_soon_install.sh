#!/usr/bin/env bash
# =============================================================================
# Install / upgrade ipai_website_coming_soon and set as homepage.
# Idempotent: safe to run multiple times.
#
# Usage (Docker):
#   ./scripts/odoo_coming_soon_install.sh
#
# Usage (bare metal / custom):
#   ODOO_BIN=./odoo-bin ODOO_DB=odoo ./scripts/odoo_coming_soon_install.sh
# =============================================================================
set -euo pipefail

MODULE="ipai_website_coming_soon"

# ---------------------------------------------------------------------------
# Docker mode (default): uses docker compose exec
# ---------------------------------------------------------------------------
if command -v docker &>/dev/null && docker compose ps --services 2>/dev/null | grep -q "web\|odoo"; then
    SERVICE=$(docker compose ps --services 2>/dev/null | grep -E "^(web|odoo-core|odoo)$" | head -1)
    DB=$(docker compose exec -T "$SERVICE" grep -oP '(?<=db_name\s=\s)\S+' /etc/odoo/odoo.conf 2>/dev/null || echo "odoo")

    echo "Installing $MODULE on service=$SERVICE db=$DB ..."
    docker compose exec -T "$SERVICE" odoo -d "$DB" -i "$MODULE" --stop-after-init
    echo "OK: $MODULE installed. Restarting service ..."
    docker compose restart "$SERVICE"
    echo "Done."
    exit 0
fi

# ---------------------------------------------------------------------------
# Bare-metal / CI mode
# ---------------------------------------------------------------------------
: "${ODOO_BIN:=odoo}"
: "${ODOO_DB:=odoo}"
: "${ODOO_CONF:=}"

ARGS=(-d "$ODOO_DB" -i "$MODULE" --stop-after-init)
[[ -n "$ODOO_CONF" ]] && ARGS=(-c "$ODOO_CONF" "${ARGS[@]}")

echo "Installing $MODULE on db=$ODOO_DB ..."
"$ODOO_BIN" "${ARGS[@]}"
echo "OK: $MODULE installed. Restart Odoo service if required."
