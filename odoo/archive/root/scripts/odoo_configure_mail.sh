#!/bin/bash
set -euo pipefail

# =============================================================================
# Odoo Mail Configuration Script (SSOT)
# =============================================================================
# Applies Zoho Mail PRO SMTP configuration to Odoo database headlessly
# Idempotent: safe to run multiple times
#
# Usage:
#   ./scripts/odoo_configure_mail.sh
#   ./scripts/odoo_configure_mail.sh --verify-only
#
# Requirements:
#   - .env.platform.local with ZOHO_SMTP_* variables
#   - Docker compose odoo container running
#   - PostgreSQL database accessible
# =============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
ENV_FILE="${ENV_FILE:-$REPO_ROOT/.env.platform.local}"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}✅${NC} $*"
}

log_warn() {
    echo -e "${YELLOW}⚠️${NC}  $*"
}

log_error() {
    echo -e "${RED}❌${NC} $*" >&2
}

# Check if .env.platform.local exists
if [ ! -f "$ENV_FILE" ]; then
    log_error "Environment file not found: $ENV_FILE"
    log_error "Create .env.platform.local with ZOHO_SMTP_* variables"
    exit 1
fi

# Verify only mode
VERIFY_ONLY=false
if [ "${1:-}" = "--verify-only" ]; then
    VERIFY_ONLY=true
fi

cd "$REPO_ROOT"

if [ "$VERIFY_ONLY" = true ]; then
    log_info "Verification mode: checking configuration..."

    docker compose -f .devcontainer/docker-compose.yml exec -T postgres bash -lc '
    set -euo pipefail
    DB_NAME="${DB_NAME:-postgres}"

    echo "=== SMTP Server Configuration ==="
    psql -U odoo -d "$DB_NAME" -c "
    select id, name, smtp_host, smtp_port, smtp_encryption, smtp_user, active, sequence
    from ir_mail_server
    where smtp_host = '\''smtppro.zoho.com'\''
    order by sequence asc, id asc;
    "

    echo ""
    echo "=== Mail System Parameters ==="
    psql -U odoo -d "$DB_NAME" -c "
    select key, value
    from ir_config_parameter
    where key in (
      '\''mail.default.from'\'',
      '\''mail.default.reply_to'\'',
      '\''mail.catchall.domain'\''
    )
    order by key;
    "
    '

    exit 0
fi

log_info "Applying Zoho Mail PRO configuration to Odoo..."

docker compose -f .devcontainer/docker-compose.yml exec -T odoo bash -lc '
set -euo pipefail
cd /workspace
set -a; . /workspace/.env.platform.local; set +a

DB_NAME="${DB_NAME:-postgres}"
ODOO_BIN="/workspace/odoo-bin"
[ -f "$ODOO_BIN" ] || ODOO_BIN="/workspace/vendor/odoo/odoo-bin"

# Verify required variables
: "${ZOHO_SMTP_HOST:?ZOHO_SMTP_HOST not set}"
: "${ZOHO_SMTP_PORT:?ZOHO_SMTP_PORT not set}"
: "${ZOHO_SMTP_USER:?ZOHO_SMTP_USER not set}"
: "${ZOHO_SMTP_PASS:?ZOHO_SMTP_PASS not set}"
: "${MAIL_DEFAULT_FROM:?MAIL_DEFAULT_FROM not set}"
: "${MAIL_REPLY_TO:?MAIL_REPLY_TO not set}"
: "${MAIL_CATCHALL_DOMAIN:?MAIL_CATCHALL_DOMAIN not set}"

python3 "$ODOO_BIN" shell -d "$DB_NAME" --no-http <<PY
import os

smtp_host=os.environ["ZOHO_SMTP_HOST"]
smtp_port=int(os.environ["ZOHO_SMTP_PORT"])
smtp_user=os.environ["ZOHO_SMTP_USER"]
smtp_pass=os.environ["ZOHO_SMTP_PASS"]
smtp_tls=os.environ.get("ZOHO_SMTP_TLS","false").lower()=="true"
smtp_ssl=os.environ.get("ZOHO_SMTP_SSL","false").lower()=="true"

# Upsert SMTP server
MailServer = env["ir.mail_server"]
existing = MailServer.search([("smtp_host","=",smtp_host)])
vals = {
    "name": "Zoho Mail PRO",
    "smtp_host": smtp_host,
    "smtp_port": smtp_port,
    "smtp_user": smtp_user,
    "smtp_pass": smtp_pass,
    "smtp_encryption": "starttls" if smtp_tls else ("ssl" if smtp_ssl else "none"),
    "sequence": 10,
    "active": True,
}
if existing:
    existing.write(vals)
    print(f"✅ Updated existing Zoho SMTP server (id={existing.id})")
else:
    rec = MailServer.create(vals)
    print(f"✅ Created Zoho SMTP server (id={rec.id})")

# System parameters
ICP = env["ir.config_parameter"].sudo()
ICP.set_param("mail.default.from", os.environ["MAIL_DEFAULT_FROM"])
ICP.set_param("mail.default.reply_to", os.environ["MAIL_REPLY_TO"])
ICP.set_param("mail.catchall.domain", os.environ["MAIL_CATCHALL_DOMAIN"])
print("✅ Set mail.default.from, mail.default.reply_to, mail.catchall.domain")

env.cr.commit()
PY
'

log_info "Configuration applied successfully"
log_info "Run with --verify-only to check current settings"
