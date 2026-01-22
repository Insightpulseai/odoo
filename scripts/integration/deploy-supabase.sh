#!/usr/bin/env bash
# Deploy Supabase integration bus (migrations + Edge Functions)

set -euo pipefail

echo "=== Deploying Supabase Integration Bus ==="
echo ""

# Check Supabase CLI installed
if ! command -v supabase &> /dev/null; then
    echo "❌ Supabase CLI not found. Install with: brew install supabase/tap/supabase"
    exit 1
fi

# Check Supabase project linked
if [ ! -f .supabase/config.toml ]; then
    echo "❌ Supabase project not linked. Run: supabase link --project-ref spdtwktxdalcfigzeqrz"
    exit 1
fi

echo "✅ Supabase CLI ready"
echo ""

# Deploy migrations
echo "[1/4] Deploying database migrations..."
supabase db push

echo "✅ Migrations deployed"
echo ""

# Deploy Edge Function
echo "[2/4] Deploying odoo-webhook Edge Function..."
supabase functions deploy odoo-webhook --no-verify-jwt

echo "✅ Edge Function deployed"
echo ""

# Set secrets
echo "[3/4] Setting Edge Function secrets..."
if [ -z "${ODOO_WEBHOOK_SECRET:-}" ]; then
    echo "⚠️  ODOO_WEBHOOK_SECRET not set in environment. Generating random secret..."
    ODOO_WEBHOOK_SECRET=$(openssl rand -hex 32)
    echo ""
    echo "Generated secret (save this to your .env file):"
    echo "ODOO_WEBHOOK_SECRET=${ODOO_WEBHOOK_SECRET}"
    echo ""
fi

supabase secrets set ODOO_WEBHOOK_SECRET="${ODOO_WEBHOOK_SECRET}"

echo "✅ Secrets configured"
echo ""

# Verify deployment
echo "[4/4] Verifying deployment..."

# Check schema exists
if supabase db query "SELECT schema_name FROM information_schema.schemata WHERE schema_name='integration';" | grep -q integration; then
    echo "✅ integration schema exists"
else
    echo "❌ integration schema not found"
    exit 1
fi

# Check tables exist
TABLES=("outbox" "event_log" "id_map")
for table in "${TABLES[@]}"; do
    if supabase db query "SELECT tablename FROM pg_tables WHERE schemaname='integration' AND tablename='${table}';" | grep -q "${table}"; then
        echo "✅ integration.${table} table exists"
    else
        echo "❌ integration.${table} table not found"
        exit 1
    fi
done

# Check functions exist
FUNCTIONS=("claim_outbox" "ack_outbox" "fail_outbox")
for func in "${FUNCTIONS[@]}"; do
    if supabase db query "SELECT proname FROM pg_proc JOIN pg_namespace ON pg_proc.pronamespace = pg_namespace.oid WHERE pg_namespace.nspname='integration' AND proname='${func}';" | grep -q "${func}"; then
        echo "✅ integration.${func}() function exists"
    else
        echo "❌ integration.${func}() function not found"
        exit 1
    fi
done

echo ""
echo "=== Deployment Complete ==="
echo ""
echo "Next Steps:"
echo "1. Add Odoo system parameters:"
echo "   - ipai.webhook.url = https://spdtwktxdalcfigzeqrz.supabase.co/functions/v1/odoo-webhook"
echo "   - ipai.webhook.secret = ${ODOO_WEBHOOK_SECRET}"
echo ""
echo "2. Update Odoo models to emit events (see docs/integration/EVENT_TAXONOMY.md)"
echo ""
echo "3. Import n8n workflows:"
echo "   - n8n/workflows/integration/event-router.json"
echo "   - n8n/workflows/integration/expense-handler.json"
echo "   - n8n/workflows/integration/asset-handler.json"
echo "   - n8n/workflows/integration/finance-handler.json"
echo ""
echo "4. Test end-to-end:"
echo "   - Submit test expense in Odoo"
echo "   - Verify event in Supabase: supabase db query \"SELECT * FROM integration.outbox ORDER BY created_at DESC LIMIT 10;\""
echo "   - Check Mattermost for notification"
echo ""
