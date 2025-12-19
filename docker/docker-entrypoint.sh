#!/bin/bash
# =============================================================================
# Odoo Docker Entrypoint with envsubst Configuration Templating
# =============================================================================
# This script:
#   1. Expands environment variables in odoo.conf.template → odoo.conf
#   2. Sets up proper permissions
#   3. Launches Odoo with the provided arguments
# =============================================================================

set -e

# -----------------------------------------------------------------------------
# Configuration Templating
# -----------------------------------------------------------------------------
# Odoo does NOT natively expand ${ENV_VAR} in config files
# We use envsubst to expand variables at container startup

CONF_TEMPLATE="/etc/odoo/odoo.conf.template"
CONF_OUTPUT="/etc/odoo/odoo.conf"

if [ -f "$CONF_TEMPLATE" ]; then
    echo "[entrypoint] Expanding configuration template..."

    # Export all environment variables for envsubst
    # Filter to only include expected Odoo-related vars
    envsubst '${DB_HOST} ${DB_PORT} ${DB_USER} ${DB_PASSWORD} ${DB_NAME} ${DB_SSLMODE} ${DB_MAXCONN}
              ${DB_FILTER} ${LIST_DB}
              ${ODOO_ADDONS_PATH}
              ${HTTP_PORT} ${LONGPOLLING_PORT} ${HTTP_INTERFACE} ${PROXY_MODE}
              ${WORKERS} ${MAX_CRON_THREADS}
              ${LIMIT_TIME_CPU} ${LIMIT_TIME_REAL} ${LIMIT_TIME_REAL_CRON}
              ${LIMIT_MEMORY_HARD} ${LIMIT_MEMORY_SOFT} ${LIMIT_REQUEST}
              ${LOGFILE} ${LOG_LEVEL} ${LOG_HANDLER} ${LOG_DB}
              ${ADMIN_PASSWORD} ${SERVER_WIDE_MODULES} ${DATA_DIR}
              ${EMAIL_FROM} ${SMTP_SERVER} ${SMTP_PORT} ${SMTP_SSL} ${SMTP_USER} ${SMTP_PASSWORD}
              ${TEST_ENABLE} ${WITHOUT_DEMO} ${UNACCENT}' \
        < "$CONF_TEMPLATE" > "$CONF_OUTPUT"

    echo "[entrypoint] Configuration written to $CONF_OUTPUT"
else
    echo "[entrypoint] No template found at $CONF_TEMPLATE, using existing config"
fi

# -----------------------------------------------------------------------------
# Database Initialization Check
# -----------------------------------------------------------------------------
# Wait for database if DB_HOST is set
if [ -n "$DB_HOST" ]; then
    echo "[entrypoint] Waiting for database at $DB_HOST:${DB_PORT:-5432}..."
    timeout=60
    while ! pg_isready -h "$DB_HOST" -p "${DB_PORT:-5432}" -U "${DB_USER:-odoo}" -q; do
        timeout=$((timeout - 1))
        if [ $timeout -le 0 ]; then
            echo "[entrypoint] ERROR: Database not ready after 60 seconds"
            exit 1
        fi
        sleep 1
    done
    echo "[entrypoint] Database is ready!"
fi

# -----------------------------------------------------------------------------
# Execute Odoo
# -----------------------------------------------------------------------------
echo "[entrypoint] Starting Odoo..."

# If no arguments provided, use default config
if [ $# -eq 0 ]; then
    exec odoo --config="$CONF_OUTPUT"
else
    exec odoo "$@"
fi
