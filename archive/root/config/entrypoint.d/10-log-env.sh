#!/bin/bash
# =============================================================================
# 10-log-env.sh - Log environment information at startup
# =============================================================================
# This script runs early in the entrypoint to log useful debug information
# without exposing secrets.
#
# =============================================================================

set -euo pipefail

echo "============================================="
echo "  IPAI Odoo CE Container Starting"
echo "============================================="
echo "  Hostname:  $(hostname)"
echo "  Date:      $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "  User:      $(whoami)"
echo "  Profile:   ${PROFILE:-standard}"
echo "============================================="
echo ""

# Log non-sensitive environment variables
echo "Environment Configuration:"
echo "  HOST:             ${HOST:-db}"
echo "  PORT:             ${PORT:-5432}"
echo "  USER:             ${USER:-odoo}"
echo "  DB_NAME:          ${DB_NAME:-auto}"
echo "  PROXY_MODE:       ${PROXY_MODE:-false}"
echo "  LOG_LEVEL:        ${LOG_LEVEL:-info}"
echo "  WORKERS:          ${ODOO_WORKERS:-auto}"
echo "  ODOO_RC:          ${ODOO_RC:-/etc/odoo/odoo.conf}"
echo ""

# Log addons paths
if [[ -n "${ODOO_ADDONS_PATH:-}" ]]; then
    echo "Addons Paths (from env):"
    echo "$ODOO_ADDONS_PATH" | tr ',' '\n' | sed 's/^/  - /'
    echo ""
fi

# Log Python version
echo "Python Version: $(python3 --version 2>&1 || echo 'unknown')"
echo ""
