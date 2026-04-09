#!/bin/bash
set -eo pipefail

# =============================================================================
# Odoo 18 CE — Unified Entrypoint for ACA web / worker / cron roles
# =============================================================================
#
# Role selection:  ODOO_ROLE=web|worker|cron  (default: web)
# Config file:     ODOO_RC or /etc/odoo/odoo.conf
# DB wait:         waits for $DB_HOST:$DB_PORT before starting (max 30s)
#
# Role contract:
#
#   web    — Serves HTTP (8069) + longpolling (8072). Uses workers= from
#            odoo.conf. Cron disabled (max_cron_threads=0) because the cron
#            role handles scheduled actions. This is the only role that
#            should have public ingress (Front Door / ACA ingress).
#
#   cron   — No HTTP. Runs Odoo in single-thread mode with cron enabled
#            (max_cron_threads from odoo.conf or default 2). Executes
#            ir.cron scheduled actions + mail queue processing. Must NOT
#            have public ingress. Connects to the same DB as web.
#
#   worker — No HTTP, no cron. Runs Odoo in single-thread mode as an OCA
#            queue_job runner. queue_job's jobrunner polls the DB for
#            enqueued jobs and processes them in-process. Channels are
#            configured in odoo.conf [queue_job] section. If queue_job is
#            not installed, this role idles (safe but pointless).
#            Must NOT have public ingress.
#
# =============================================================================

ODOO_ROLE="${ODOO_ROLE:-web}"
ODOO_RC="${ODOO_RC:-/etc/odoo/odoo.conf}"
DB_HOST="${DB_HOST:-${HOST:-localhost}}"
DB_PORT="${DB_PORT:-${PORT:-5432}}"

# --- Wait for database availability ---
wait_for_db() {
    local retries=30
    local wait_s=1
    echo "[entrypoint] Waiting for database at ${DB_HOST}:${DB_PORT}..."
    while ! pg_isready -h "$DB_HOST" -p "$DB_PORT" -q 2>/dev/null; do
        retries=$((retries - 1))
        if [ "$retries" -le 0 ]; then
            echo "[entrypoint] ERROR: Database not available after 30s" >&2
            exit 1
        fi
        sleep "$wait_s"
    done
    echo "[entrypoint] Database is ready."
}

# --- Validate required config ---
if [ ! -f "$ODOO_RC" ]; then
    echo "[entrypoint] ERROR: Config file not found: $ODOO_RC" >&2
    exit 1
fi

wait_for_db

# --- Start Odoo in the requested role ---
echo "[entrypoint] Role: $ODOO_ROLE | Config: $ODOO_RC | DB: $DB_HOST:$DB_PORT"

case "$ODOO_ROLE" in
    web)
        # HTTP-serving Odoo. Workers from odoo.conf. Cron disabled here
        # because the dedicated cron container handles scheduled actions.
        echo "[entrypoint] Starting Odoo web (HTTP + longpolling, cron disabled)"
        exec odoo -c "$ODOO_RC" \
            --max-cron-threads=0 \
            "$@"
        ;;

    cron)
        # No HTTP. Cron threads process ir.cron records + mail queue.
        # max_cron_threads defaults to 2; override via $@ if needed.
        echo "[entrypoint] Starting Odoo cron (no HTTP, cron threads=2)"
        exec odoo -c "$ODOO_RC" \
            --no-http \
            --workers=0 \
            --max-cron-threads=2 \
            "$@"
        ;;

    worker)
        # No HTTP, no cron. OCA queue_job jobrunner processes enqueued jobs.
        # queue_job channels configured in odoo.conf [queue_job] section.
        # With --workers=0 --max-cron-threads=0 --no-http, Odoo starts its
        # single-thread server; queue_job hooks into the server lifecycle
        # and polls for jobs via its internal runner thread.
        echo "[entrypoint] Starting Odoo worker (no HTTP, no cron, queue_job runner)"
        exec odoo -c "$ODOO_RC" \
            --no-http \
            --workers=0 \
            --max-cron-threads=0 \
            "$@"
        ;;

    *)
        echo "[entrypoint] ERROR: Unknown ODOO_ROLE: $ODOO_ROLE" >&2
        echo "[entrypoint] Valid roles: web, worker, cron" >&2
        exit 1
        ;;
esac
