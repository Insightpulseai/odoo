#!/bin/bash
# =============================================================================
# Fix Odoo Email Configuration
# =============================================================================
# Problem: Emails failing to admin@yourcompany.example.com (placeholder domain)
# Solution: Update system parameters to use insightpulseai.net
# =============================================================================

set -euo pipefail

# Configuration
ODOO_CONTAINER="${ODOO_CONTAINER:-odoo}"
DB_CONTAINER="${DB_CONTAINER:-odoo-db}"
DB_NAME="${DB_NAME:-odoo}"
DB_USER="${DB_USER:-odoo}"
DOMAIN="${DOMAIN:-insightpulseai.net}"
ERP_URL="${ERP_URL:-https://erp.insightpulseai.net}"

echo "=========================================="
echo "Odoo Email Configuration Fix"
echo "=========================================="
echo "Domain: ${DOMAIN}"
echo "ERP URL: ${ERP_URL}"
echo "Database: ${DB_NAME}"
echo ""

# Check if running in Docker environment
if command -v docker &> /dev/null; then
    echo "[1/4] Checking Docker containers..."

    if ! docker ps | grep -q "${DB_CONTAINER}"; then
        echo "ERROR: Database container '${DB_CONTAINER}' not running"
        echo "Available containers:"
        docker ps --format "table {{.Names}}\t{{.Status}}"
        exit 1
    fi

    echo "[2/4] Updating mail.catchall.domain..."
    docker exec -i "${DB_CONTAINER}" psql -U "${DB_USER}" -d "${DB_NAME}" -c "
        UPDATE ir_config_parameter
        SET value = '${DOMAIN}'
        WHERE key = 'mail.catchall.domain';
    "

    echo "[3/4] Updating mail.default.from..."
    docker exec -i "${DB_CONTAINER}" psql -U "${DB_USER}" -d "${DB_NAME}" -c "
        UPDATE ir_config_parameter
        SET value = 'no-reply@${DOMAIN}'
        WHERE key = 'mail.default.from';
    "

    echo "[4/4] Updating web.base.url..."
    docker exec -i "${DB_CONTAINER}" psql -U "${DB_USER}" -d "${DB_NAME}" -c "
        UPDATE ir_config_parameter
        SET value = '${ERP_URL}'
        WHERE key = 'web.base.url';
    "

    echo ""
    echo "Verifying updates..."
    docker exec -i "${DB_CONTAINER}" psql -U "${DB_USER}" -d "${DB_NAME}" -c "
        SELECT key, value
        FROM ir_config_parameter
        WHERE key IN ('mail.catchall.domain', 'mail.default.from', 'web.base.url');
    "

    echo ""
    echo "Restarting Odoo container..."
    if docker ps | grep -q "${ODOO_CONTAINER}"; then
        docker restart "${ODOO_CONTAINER}"
        echo "Odoo container restarted successfully"
    else
        echo "WARNING: Odoo container '${ODOO_CONTAINER}' not found"
    fi

else
    echo "Docker not found. Generating SQL script instead..."
    cat << EOF

-- Run this SQL in your Odoo database:
UPDATE ir_config_parameter SET value = '${DOMAIN}' WHERE key = 'mail.catchall.domain';
UPDATE ir_config_parameter SET value = 'no-reply@${DOMAIN}' WHERE key = 'mail.default.from';
UPDATE ir_config_parameter SET value = '${ERP_URL}' WHERE key = 'web.base.url';

-- Verify:
SELECT key, value FROM ir_config_parameter WHERE key IN ('mail.catchall.domain', 'mail.default.from', 'web.base.url');

EOF
fi

echo ""
echo "=========================================="
echo "Email configuration fix complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Test email sending from Odoo"
echo "2. Check Mailgun logs for delivery status"
echo "3. Verify DNS records are configured"
