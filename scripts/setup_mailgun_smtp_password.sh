#!/usr/bin/env bash
# scripts/setup_mailgun_smtp_password.sh
#
# Wire Mailgun SMTP password into Odoo ir.mail_server record (idempotent).
# Reads password from environment variable — NEVER commit the value to git.
#
# Usage (on the DO droplet, or with Docker access):
#
#   export MAILGUN_SMTP_PASSWORD=...
#   bash scripts/setup_mailgun_smtp_password.sh
#
# After running, install/update the module if not already installed:
#   docker exec -u odoo odoo-prod odoo --stop-after-init -d odoo -i ipai_mailgun_smtp
#   # or if already installed:
#   docker exec -u odoo odoo-prod odoo --stop-after-init -d odoo -u ipai_mailgun_smtp

set -euo pipefail

# ── Validate required vars ────────────────────────────────────────────────────
: "${MAILGUN_SMTP_PASSWORD:?MAILGUN_SMTP_PASSWORD must be set}"

ODOO_DB="${ODOO_DB:-odoo}"

echo "▶ Wiring Mailgun SMTP password into Odoo (db=${ODOO_DB})"

# ── Python snippet to set smtp_pass via Odoo shell ───────────────────────────
PYTHON_CMD=$(cat <<PYEOF
import os
IMS = env['ir.mail_server'].sudo()
server = IMS.search([('smtp_host', '=', 'smtp.mailgun.org')], limit=1)
if not server:
    raise ValueError(
        "No ir.mail_server with smtp_host=smtp.mailgun.org found. "
        "Install ipai_mailgun_smtp first."
    )
server.write({'smtp_pass': os.environ['MAILGUN_SMTP_PASSWORD']})
env.cr.commit()
print(f"  set smtp_pass for server: {server.name}")
print("Done")
PYEOF
)

# ── Detect execution context and run ─────────────────────────────────────────
# Look for any running Odoo container (odoo-prod or legacy odoo-ce)
ODOO_CONTAINER=""
if command -v docker &>/dev/null; then
    ODOO_CONTAINER=$(docker ps --format '{{.Names}}' 2>/dev/null | grep -E '^odoo-' | head -1 || true)
fi

if [[ -n "$ODOO_CONTAINER" ]]; then
    echo "  using container: $ODOO_CONTAINER"
    echo "$PYTHON_CMD" | docker exec -i \
        -e MAILGUN_SMTP_PASSWORD="$MAILGUN_SMTP_PASSWORD" \
        -u odoo "$ODOO_CONTAINER" \
        odoo shell --no-http -d "$ODOO_DB"

elif command -v odoo &>/dev/null; then
    echo "  using odoo in PATH"
    echo "$PYTHON_CMD" | MAILGUN_SMTP_PASSWORD="$MAILGUN_SMTP_PASSWORD" \
        odoo shell --no-http -d "$ODOO_DB"

else
    echo "❌ Cannot find an Odoo Docker container (odoo-*) or 'odoo' in PATH."
    echo "   Set the SMTP password manually via Odoo Settings:"
    echo "     Settings → Technical → Outgoing Mail Servers → Mailgun SMTP"
    echo "   Or set MAILGUN_SMTP_PASSWORD and re-run after starting the container."
    exit 1
fi

echo ""
echo "▶ Next steps:"
echo "   1. Verify DNS records are published (check Mailgun dashboard → Domain Verified)"
echo "   2. Test outgoing email from Odoo:"
echo "      Settings → Outgoing Mail Servers → Mailgun SMTP → Test Connection"
echo "   3. Check Mailgun Logs for delivery confirmation"
