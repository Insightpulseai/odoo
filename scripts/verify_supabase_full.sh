#!/bin/bash
# =============================================================================
# Full Supabase Verification: Migrations + Edge Functions + Vault Secrets
# =============================================================================
# Credentials are auto-loaded from .env.local (run setup_credentials.sh first)
#
# Usage:
#   ./scripts/verify_supabase_full.sh
# =============================================================================

set -euo pipefail

# Auto-load credentials from .env.local
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ -f "$SCRIPT_DIR/lib/load_env.sh" ]; then
    source "$SCRIPT_DIR/lib/load_env.sh"
fi

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_pass() { echo -e "${GREEN}[PASS]${NC} $1"; }
log_fail() { echo -e "${RED}[FAIL]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }

echo ""
echo "============================================="
echo "  Supabase Full Verification"
echo "  Project: spdtwktxdalcfigzeqrz"
echo "  $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
echo "============================================="
echo ""

# Check required env vars
if [ -z "${POSTGRES_URL:-}" ]; then
    log_fail "POSTGRES_URL not set"
    echo "Export: POSTGRES_URL='postgresql://postgres.[ref]:[password]@aws-0-[region].pooler.supabase.com:5432/postgres'"
    exit 1
fi

# =============================================================================
# A) MIGRATIONS
# =============================================================================
echo ""
log_info "=== A) MIGRATIONS ==="

# Count applied migrations
APPLIED=$(psql "$POSTGRES_URL" -t -A -c "SELECT COUNT(*) FROM supabase_migrations.schema_migrations" 2>/dev/null || echo "ERROR")

if [ "$APPLIED" == "ERROR" ]; then
    log_fail "Could not query migrations table"
else
    log_pass "Applied migrations: $APPLIED"
fi

# List recent migrations
log_info "Recent 10 migrations:"
psql "$POSTGRES_URL" -t -A -c "SELECT version FROM supabase_migrations.schema_migrations ORDER BY version DESC LIMIT 10" 2>/dev/null || echo "ERROR"

# Check key migrations
KEY_MIGRATIONS=("5001_auth_foundation" "5002_auth_jwt_claims" "5003_rls_policies" "mcp_jobs" "odoo_shadow")

echo ""
log_info "Key migrations check:"
for m in "${KEY_MIGRATIONS[@]}"; do
    COUNT=$(psql "$POSTGRES_URL" -t -A -c "SELECT COUNT(*) FROM supabase_migrations.schema_migrations WHERE version LIKE '%$m%'" 2>/dev/null || echo "0")
    if [ "$COUNT" -gt 0 ]; then
        log_pass "$m: Applied"
    else
        log_warn "$m: NOT FOUND"
    fi
done

# =============================================================================
# B) SCHEMAS
# =============================================================================
echo ""
log_info "=== B) SCHEMAS ==="

SCHEMAS=$(psql "$POSTGRES_URL" -t -A -c "SELECT schema_name FROM information_schema.schemata WHERE schema_name NOT LIKE 'pg_%' AND schema_name NOT IN ('information_schema') ORDER BY schema_name" 2>/dev/null)

echo "$SCHEMAS" | while read schema; do
    [ -z "$schema" ] && continue
    TABLE_COUNT=$(psql "$POSTGRES_URL" -t -A -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = '$schema'" 2>/dev/null || echo "0")
    echo "  $schema: $TABLE_COUNT tables"
done

# =============================================================================
# C) VAULT SECRETS
# =============================================================================
echo ""
log_info "=== C) VAULT SECRETS ==="

# Check if vault extension exists
VAULT_EXISTS=$(psql "$POSTGRES_URL" -t -A -c "SELECT COUNT(*) FROM pg_extension WHERE extname = 'supabase_vault'" 2>/dev/null || echo "0")

if [ "$VAULT_EXISTS" == "0" ]; then
    log_warn "Vault extension not installed"
else
    log_pass "Vault extension installed"

    # List secret names (not values!)
    log_info "Stored secrets (names only):"
    psql "$POSTGRES_URL" -t -A -c "SELECT name FROM vault.secrets ORDER BY name" 2>/dev/null || echo "  (could not query)"
fi

# Check for store_secret function
FUNC_EXISTS=$(psql "$POSTGRES_URL" -t -A -c "SELECT COUNT(*) FROM pg_proc WHERE proname = 'store_secret'" 2>/dev/null || echo "0")

if [ "$FUNC_EXISTS" -gt 0 ]; then
    log_pass "store_secret() function exists"
else
    log_warn "store_secret() function missing"
fi

# =============================================================================
# D) EDGE FUNCTIONS (via API)
# =============================================================================
echo ""
log_info "=== D) EDGE FUNCTIONS ==="

if [ -z "${SUPABASE_URL:-}" ] || [ -z "${SUPABASE_SERVICE_ROLE_KEY:-}" ]; then
    log_warn "SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY not set - skipping function checks"
else
    FUNCTIONS=(
        "auth-bootstrap"
        "tenant-invite"
        "copilot-chat"
        "sync-odoo-modules"
        "seed-odoo-finance"
        "mcp-gateway"
        "ops-job-worker"
    )

    for func in "${FUNCTIONS[@]}"; do
        HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" \
            -X OPTIONS \
            "${SUPABASE_URL}/functions/v1/${func}" 2>/dev/null || echo "000")

        if [ "$HTTP_CODE" == "200" ] || [ "$HTTP_CODE" == "204" ]; then
            log_pass "$func: Deployed (CORS OK)"
        elif [ "$HTTP_CODE" == "404" ]; then
            log_fail "$func: NOT DEPLOYED"
        else
            log_warn "$func: HTTP $HTTP_CODE"
        fi
    done
fi

# =============================================================================
# E) RLS STATUS
# =============================================================================
echo ""
log_info "=== E) RLS STATUS ==="

RLS_TABLES=$(psql "$POSTGRES_URL" -t -A -c "
SELECT schemaname || '.' || tablename || ' -> ' ||
    CASE WHEN rowsecurity THEN 'ENABLED' ELSE 'DISABLED' END
FROM pg_tables
WHERE schemaname IN ('app', 'ops', 'public')
AND tablename IN ('tenants', 'profiles', 'service_tokens', 'audit_log', 'jobs')
ORDER BY schemaname, tablename
" 2>/dev/null || echo "ERROR")

echo "$RLS_TABLES"

# =============================================================================
# F) KEY FUNCTIONS
# =============================================================================
echo ""
log_info "=== F) KEY DATABASE FUNCTIONS ==="

KEY_FUNCS=("custom_access_token_hook" "current_user_id" "current_tenant_id" "enqueue_job" "claim_next_job")

for func in "${KEY_FUNCS[@]}"; do
    COUNT=$(psql "$POSTGRES_URL" -t -A -c "SELECT COUNT(*) FROM pg_proc WHERE proname = '$func'" 2>/dev/null || echo "0")
    if [ "$COUNT" -gt 0 ]; then
        log_pass "$func() exists"
    else
        log_warn "$func() missing"
    fi
done

# =============================================================================
# SUMMARY
# =============================================================================
echo ""
echo "============================================="
echo "  Verification Complete"
echo "============================================="
echo ""
echo "To apply missing migrations:"
echo "  supabase db push"
echo ""
echo "To deploy missing functions:"
echo "  supabase functions deploy"
echo ""
echo "To store secrets in vault:"
echo "  psql \$POSTGRES_URL -c \"SELECT store_secret('key_name', 'secret_value', 'description')\""
echo ""
