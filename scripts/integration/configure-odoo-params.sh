#!/usr/bin/env bash
# Configure Odoo system parameters for Supabase integration
# Usage: ./scripts/integration/configure-odoo-params.sh [--docker] [--database DB_NAME]
set -euo pipefail

# Configuration
ODOO_CONTAINER="${ODOO_CONTAINER:-odoo-core}"
ODOO_DB="${ODOO_DB:-odoo_core}"
USE_DOCKER=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --docker)
            USE_DOCKER=true
            shift
            ;;
        --database)
            ODOO_DB="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Load environment variables
if [[ -f .env ]]; then
    # shellcheck disable=SC1091
    source .env
fi

# Supabase configuration
SUPABASE_PROJECT_ID="${SUPABASE_PROJECT_ID:-spdtwktxdalcfigzeqrz}"
WEBHOOK_URL="${IPAI_WEBHOOK_URL:-https://${SUPABASE_PROJECT_ID}.supabase.co/functions/v1/odoo-webhook}"
WEBHOOK_SECRET="${IPAI_WEBHOOK_SECRET:-}"

if [[ -z "$WEBHOOK_SECRET" ]]; then
    echo "Warning: IPAI_WEBHOOK_SECRET not set. Generating a random secret..."
    WEBHOOK_SECRET=$(openssl rand -hex 32)
    echo "Generated secret: $WEBHOOK_SECRET"
    echo "Save this to your .env file as IPAI_WEBHOOK_SECRET"
fi

# SQL to configure parameters
SQL_COMMANDS=$(cat <<EOF
-- Configure Supabase integration webhook
INSERT INTO ir_config_parameter (key, value, create_uid, create_date, write_uid, write_date)
VALUES
    ('ipai.webhook.url', '${WEBHOOK_URL}', 1, NOW(), 1, NOW()),
    ('ipai.webhook.secret', '${WEBHOOK_SECRET}', 1, NOW(), 1, NOW())
ON CONFLICT (key) DO UPDATE SET
    value = EXCLUDED.value,
    write_date = NOW();

-- Verify configuration
SELECT key, value FROM ir_config_parameter
WHERE key LIKE 'ipai.webhook.%';
EOF
)

echo "Configuring Odoo integration parameters..."
echo "  Webhook URL: $WEBHOOK_URL"
echo "  Database: $ODOO_DB"

if $USE_DOCKER; then
    echo "Using Docker container: $ODOO_CONTAINER"
    docker exec -i "$ODOO_CONTAINER" psql -U odoo -d "$ODOO_DB" <<< "$SQL_COMMANDS"
else
    echo "Using local psql..."
    psql -U odoo -d "$ODOO_DB" <<< "$SQL_COMMANDS"
fi

echo ""
echo "Configuration complete!"
echo ""
echo "Next steps:"
echo "1. Ensure the IPAI_WEBHOOK_SECRET is saved in your .env file"
echo "2. Set the same secret in Supabase Edge Function environment"
echo "3. Update and restart the Odoo module:"
echo "   docker exec $ODOO_CONTAINER odoo -d $ODOO_DB -u ipai_enterprise_bridge --stop-after-init"
