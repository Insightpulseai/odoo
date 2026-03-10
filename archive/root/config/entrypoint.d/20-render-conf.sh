#!/bin/bash
# =============================================================================
# 20-render-conf.sh - Render odoo.conf from template with environment variables
# =============================================================================
# Supports both direct environment variables and *_FILE variants for secrets.
#
# Supported variables:
#   HOST, PORT, USER, PASSWORD (or PASSWORD_FILE)
#   DB_NAME, ADMIN_PASSWD (or ADMIN_PASSWD_FILE)
#   PROXY_MODE, LOG_LEVEL, LIST_DB
#   ODOO_WORKERS, ODOO_MAX_CRON_THREADS
#   ODOO_LIMIT_MEMORY_SOFT, ODOO_LIMIT_MEMORY_HARD
#   ODOO_LIMIT_TIME_CPU, ODOO_LIMIT_TIME_REAL
#
# =============================================================================

set -euo pipefail

TEMPLATE="${ODOO_CONF_TEMPLATE:-/etc/odoo/odoo.conf.template}"
CONFIG="${ODOO_RC:-/etc/odoo/odoo.conf}"

# Helper to read secret from file or use direct value
read_secret() {
    local var_name="$1"
    local file_var_name="${var_name}_FILE"
    local value="${!var_name:-}"
    local file_path="${!file_var_name:-}"

    if [[ -n "$file_path" && -f "$file_path" ]]; then
        cat "$file_path"
    elif [[ -n "$value" ]]; then
        echo "$value"
    else
        echo ""
    fi
}

# Skip if template doesn't exist
if [[ ! -f "$TEMPLATE" ]]; then
    echo "[20-render-conf] No template found at $TEMPLATE, skipping..."
    exit 0
fi

echo "[20-render-conf] Rendering configuration from template..."

# Read secrets from files if provided
export DB_PASSWORD="$(read_secret PASSWORD)"
export ADMIN_PASSWORD="$(read_secret ADMIN_PASSWD)"

# Set defaults for optional variables
export DB_HOST="${HOST:-db}"
export DB_PORT="${PORT:-5432}"
export DB_USER="${USER:-odoo}"
export DB_NAME="${DB_NAME:-False}"
export PROXY_MODE="${PROXY_MODE:-True}"
export LOG_LEVEL="${LOG_LEVEL:-info}"
export LIST_DB="${LIST_DB:-False}"
export WORKERS="${ODOO_WORKERS:-4}"
export MAX_CRON_THREADS="${ODOO_MAX_CRON_THREADS:-2}"
export LIMIT_MEMORY_SOFT="${ODOO_LIMIT_MEMORY_SOFT:-2147483648}"
export LIMIT_MEMORY_HARD="${ODOO_LIMIT_MEMORY_HARD:-2684354560}"
export LIMIT_TIME_CPU="${ODOO_LIMIT_TIME_CPU:-600}"
export LIMIT_TIME_REAL="${ODOO_LIMIT_TIME_REAL:-1200}"

# Render template using envsubst
envsubst < "$TEMPLATE" > "$CONFIG"

echo "[20-render-conf] Configuration written to $CONFIG"

# Verify critical values are not placeholder
if grep -q "CHANGE_ME" "$CONFIG" 2>/dev/null; then
    echo "[20-render-conf] WARNING: Configuration contains CHANGE_ME placeholders!"
fi
