#!/bin/bash
# =============================================================================
# IPAI Odoo Docker Entrypoint
# =============================================================================
# This script:
#   1. Runs startup hooks from /entrypoint.d/*.sh
#   2. Expands environment variables in odoo.conf.template → odoo.conf
#   3. Waits for database connectivity
#   4. Launches Odoo with the provided arguments
#
# Hook ordering:
#   10-log-env.sh      - Log environment information
#   20-render-conf.sh  - Render configuration from template
#   90-preflight.sh    - Pre-flight checks before starting Odoo
#
# =============================================================================

set -e

# -----------------------------------------------------------------------------
# Run Entrypoint Hooks
# -----------------------------------------------------------------------------
# Execute all scripts in /entrypoint.d/ in sorted order
# Each script should be idempotent and handle its own error conditions

HOOKS_DIR="/entrypoint.d"

if [ -d "$HOOKS_DIR" ]; then
    echo "[entrypoint] Running startup hooks from $HOOKS_DIR..."

    for hook in $(ls -1 "$HOOKS_DIR"/*.sh 2>/dev/null | sort); do
        if [ -x "$hook" ]; then
            echo "[entrypoint] Executing: $(basename "$hook")"
            . "$hook"
            HOOK_EXIT=$?
            if [ $HOOK_EXIT -ne 0 ]; then
                echo "[entrypoint] ERROR: Hook $(basename "$hook") failed with exit code $HOOK_EXIT"
                exit $HOOK_EXIT
            fi
        else
            echo "[entrypoint] Skipping non-executable: $(basename "$hook")"
        fi
    done

    echo "[entrypoint] All hooks completed successfully"
else
    echo "[entrypoint] No hooks directory found at $HOOKS_DIR"
fi

# -----------------------------------------------------------------------------
# Configuration Templating (fallback if not handled by hooks)
# -----------------------------------------------------------------------------
CONF_TEMPLATE="/etc/odoo/odoo.conf.template"
CONF_OUTPUT="${ODOO_RC:-/etc/odoo/odoo.conf}"

# Only render if template exists and hasn't been rendered by hooks
if [ -f "$CONF_TEMPLATE" ] && [ ! -f "$CONF_OUTPUT" -o "$CONF_TEMPLATE" -nt "$CONF_OUTPUT" ]; then
    echo "[entrypoint] Rendering configuration from template..."

    # Set defaults for envsubst
    export DB_HOST="${HOST:-db}"
    export DB_PORT="${PORT:-5432}"
    export DB_USER="${USER:-odoo}"
    export DB_PASSWORD="${PASSWORD:-odoo}"
    export DB_NAME="${DB_NAME:-False}"
    export DB_SSLMODE="${DB_SSLMODE:-prefer}"
    export DB_MAXCONN="${DB_MAXCONN:-64}"
    export DB_FILTER="${DBFILTER:-.*}"
    export LIST_DB="${LIST_DB:-False}"
    export HTTP_PORT="${HTTP_PORT:-8069}"
    export LONGPOLLING_PORT="${LONGPOLLING_PORT:-8072}"
    export HTTP_INTERFACE="${HTTP_INTERFACE:-0.0.0.0}"
    export PROXY_MODE="${PROXY_MODE:-True}"
    export WORKERS="${ODOO_WORKERS:-4}"
    export MAX_CRON_THREADS="${ODOO_MAX_CRON_THREADS:-2}"
    export LIMIT_TIME_CPU="${ODOO_LIMIT_TIME_CPU:-600}"
    export LIMIT_TIME_REAL="${ODOO_LIMIT_TIME_REAL:-1200}"
    export LIMIT_TIME_REAL_CRON="${ODOO_LIMIT_TIME_REAL_CRON:-120}"
    export LIMIT_MEMORY_HARD="${ODOO_LIMIT_MEMORY_HARD:-2684354560}"
    export LIMIT_MEMORY_SOFT="${ODOO_LIMIT_MEMORY_SOFT:-2147483648}"
    export LIMIT_REQUEST="${ODOO_LIMIT_REQUEST:-8192}"
    export LOG_LEVEL="${LOG_LEVEL:-info}"
    export LOG_HANDLER="${LOG_HANDLER:-:INFO}"
    export ADMIN_PASSWORD="${ADMIN_PASSWD:-admin}"
    export DATA_DIR="${ODOO_DATA_DIR:-/var/lib/odoo}"
    export WITHOUT_DEMO="${WITHOUT_DEMO:-True}"

    envsubst < "$CONF_TEMPLATE" > "$CONF_OUTPUT"
    echo "[entrypoint] Configuration written to $CONF_OUTPUT"
fi

# -----------------------------------------------------------------------------
# Database Connectivity Check
# -----------------------------------------------------------------------------
DB_HOST="${HOST:-db}"
DB_PORT="${PORT:-5432}"
DB_USER="${USER:-odoo}"

if [ -n "$DB_HOST" ] && [ "$DB_HOST" != "False" ]; then
    echo "[entrypoint] Waiting for database at $DB_HOST:$DB_PORT..."

    # Use pg_isready if available
    if command -v pg_isready &>/dev/null; then
        timeout=60
        while ! pg_isready -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -q 2>/dev/null; do
            timeout=$((timeout - 1))
            if [ $timeout -le 0 ]; then
                echo "[entrypoint] WARNING: Database not ready after 60 seconds"
                echo "[entrypoint] Proceeding anyway - Odoo will retry connection"
                break
            fi
            sleep 1
        done

        if [ $timeout -gt 0 ]; then
            echo "[entrypoint] Database is ready!"
        fi
    else
        echo "[entrypoint] pg_isready not available, skipping database check"
    fi
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
