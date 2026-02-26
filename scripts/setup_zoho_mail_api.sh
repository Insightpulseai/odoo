#!/usr/bin/env bash
# scripts/setup_zoho_mail_api.sh
#
# Wire Zoho Mail API credentials into Odoo ir.config_parameter.
# Reads credentials from environment variables — NEVER commit values to git.
#
# Usage (on the DO droplet, inside the odoo container or virtualenv):
#
#   export ZOHO_CLIENT_ID=...
#   export ZOHO_CLIENT_SECRET=...
#   export ZOHO_REFRESH_TOKEN=...
#   export ZOHO_ACCOUNT_ID=...
#   export ZOHO_FROM_EMAIL=no-reply@insightpulseai.com   # optional
#   bash scripts/setup_zoho_mail_api.sh
#
# After running, install/update the module:
#   docker exec -u odoo odoo-ce odoo --stop-after-init -d odoo -i ipai_zoho_mail_api
#   # or if already installed:
#   docker exec -u odoo odoo-ce odoo --stop-after-init -d odoo -u ipai_zoho_mail_api

set -euo pipefail

# ── Validate required vars ────────────────────────────────────────────────────
: "${ZOHO_CLIENT_ID:?ZOHO_CLIENT_ID must be set}"
: "${ZOHO_CLIENT_SECRET:?ZOHO_CLIENT_SECRET must be set}"
: "${ZOHO_REFRESH_TOKEN:?ZOHO_REFRESH_TOKEN must be set}"
: "${ZOHO_ACCOUNT_ID:?ZOHO_ACCOUNT_ID must be set}"

ZOHO_FROM_EMAIL="${ZOHO_FROM_EMAIL:-no-reply@insightpulseai.com}"
ODOO_DB="${ODOO_DB:-odoo}"

echo "▶ Wiring Zoho Mail API credentials into Odoo (db=${ODOO_DB})"

# ── Python snippet to set ir.config_parameter via Odoo shell ─────────────────
read -r -d '' PYTHON_SNIPPET << 'PYEOF' || true
import sys
params = {
    "ipai.zoho.client_id":     ZOHO_CLIENT_ID,
    "ipai.zoho.client_secret": ZOHO_CLIENT_SECRET,
    "ipai.zoho.refresh_token": ZOHO_REFRESH_TOKEN,
    "ipai.zoho.account_id":    ZOHO_ACCOUNT_ID,
    "ipai.zoho.accounts_base": "https://accounts.zoho.com",
    "ipai.zoho.mail_base":     "https://mail.zoho.com",
}
ICP = env["ir.config_parameter"].sudo()
for k, v in params.items():
    ICP.set_param(k, v)
    print(f"  set {k}")
env.cr.commit()
print("✅ Done — ir.config_parameter updated")
PYEOF

# Substitute actual values (shell-safe via export + Python os.environ)
PYTHON_CMD=$(cat <<PYEOF
import os
params = {
    "ipai.zoho.client_id":     os.environ["ZOHO_CLIENT_ID"],
    "ipai.zoho.client_secret": os.environ["ZOHO_CLIENT_SECRET"],
    "ipai.zoho.refresh_token": os.environ["ZOHO_REFRESH_TOKEN"],
    "ipai.zoho.account_id":    os.environ["ZOHO_ACCOUNT_ID"],
    "ipai.zoho.accounts_base": "https://accounts.zoho.com",
    "ipai.zoho.mail_base":     "https://mail.zoho.com",
}
ICP = env["ir.config_parameter"].sudo()
for k, v in params.items():
    ICP.set_param(k, v)
    print(f"  set {k}")
env.cr.commit()
print("Done")
PYEOF
)

# ── Detect execution context and run ─────────────────────────────────────────
# Context A: inside the Odoo Docker container (odoo-ce)
if command -v docker &>/dev/null && docker ps --format '{{.Names}}' 2>/dev/null | grep -q 'odoo-ce'; then
    echo "$PYTHON_CMD" | docker exec -i \
        -e ZOHO_CLIENT_ID="$ZOHO_CLIENT_ID" \
        -e ZOHO_CLIENT_SECRET="$ZOHO_CLIENT_SECRET" \
        -e ZOHO_REFRESH_TOKEN="$ZOHO_REFRESH_TOKEN" \
        -e ZOHO_ACCOUNT_ID="$ZOHO_ACCOUNT_ID" \
        -u odoo odoo-ce \
        odoo shell --no-http -d "$ODOO_DB"

# Context B: virtualenv / bare-metal with odoo in PATH
elif command -v odoo &>/dev/null; then
    echo "$PYTHON_CMD" | ZOHO_CLIENT_ID="$ZOHO_CLIENT_ID" \
        ZOHO_CLIENT_SECRET="$ZOHO_CLIENT_SECRET" \
        ZOHO_REFRESH_TOKEN="$ZOHO_REFRESH_TOKEN" \
        ZOHO_ACCOUNT_ID="$ZOHO_ACCOUNT_ID" \
        odoo shell --no-http -d "$ODOO_DB"

else
    echo "❌ Cannot find Docker container 'odoo-ce' or 'odoo' in PATH."
    echo "   Set credentials manually via Odoo Settings → Technical → Parameters → System Parameters."
    echo "   Keys:"
    echo "     ipai.zoho.client_id"
    echo "     ipai.zoho.client_secret"
    echo "     ipai.zoho.refresh_token"
    echo "     ipai.zoho.account_id"
    echo "     ipai.zoho.accounts_base = https://accounts.zoho.com"
    echo "     ipai.zoho.mail_base     = https://mail.zoho.com"
    exit 1
fi

echo ""
echo "▶ Next: install the module"
echo "   docker exec -u odoo odoo-ce odoo --stop-after-init -d $ODOO_DB -i ipai_zoho_mail_api"
echo ""
echo "▶ Verify: send a test email"
echo "   See scripts/verify_zoho_mail_api.py"
