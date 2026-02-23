#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════════════════════
# Supabase Email Events - Integration Verification Script
# ═══════════════════════════════════════════════════════════════════════════════
# Purpose: Verify Supabase integration is correctly configured and operational
# Version: 1.0.0
# Date: 2026-01-28
# ═══════════════════════════════════════════════════════════════════════════════

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Counters
PASSED=0
FAILED=0
WARNINGS=0

# ───────────────────────────────────────────────────────────────────────────────
# Helper Functions
# ───────────────────────────────────────────────────────────────────────────────

print_header() {
    echo -e "\n${BLUE}═══════════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════════${NC}\n"
}

print_section() {
    echo -e "\n${YELLOW}───────────────────────────────────────────────────────────────────${NC}"
    echo -e "${YELLOW}$1${NC}"
    echo -e "${YELLOW}───────────────────────────────────────────────────────────────────${NC}\n"
}

pass() {
    echo -e "${GREEN}✓${NC} $1"
    ((PASSED++))
}

fail() {
    echo -e "${RED}✗${NC} $1"
    ((FAILED++))
}

warn() {
    echo -e "${YELLOW}⚠${NC} $1"
    ((WARNINGS++))
}

# ───────────────────────────────────────────────────────────────────────────────
# Environment Variable Checks
# ───────────────────────────────────────────────────────────────────────────────

check_env_vars() {
    print_section "Environment Variables"

    if [[ -n "${SUPABASE_URL:-}" ]]; then
        pass "SUPABASE_URL is set"
    else
        fail "SUPABASE_URL is not set"
    fi

    if [[ -n "${SUPABASE_ANON_KEY:-}" ]]; then
        pass "SUPABASE_ANON_KEY is set"
    else
        fail "SUPABASE_ANON_KEY is not set"
    fi

    if [[ -n "${SUPABASE_SERVICE_ROLE_KEY:-}" ]]; then
        pass "SUPABASE_SERVICE_ROLE_KEY is set"
    else
        fail "SUPABASE_SERVICE_ROLE_KEY is not set"
    fi

    if [[ -n "${MAILGUN_WEBHOOK_SIGNING_KEY:-}" ]]; then
        pass "MAILGUN_WEBHOOK_SIGNING_KEY is set"
    else
        warn "MAILGUN_WEBHOOK_SIGNING_KEY is not set (optional for testing)"
    fi

    if [[ -n "${SUPABASE_PROJECT_REF:-}" ]]; then
        pass "SUPABASE_PROJECT_REF is set: ${SUPABASE_PROJECT_REF}"
    else
        warn "SUPABASE_PROJECT_REF is not set (used for CLI operations)"
    fi
}

# ───────────────────────────────────────────────────────────────────────────────
# Supabase CLI Checks
# ───────────────────────────────────────────────────────────────────────────────

check_supabase_cli() {
    print_section "Supabase CLI"

    if command -v supabase &> /dev/null; then
        local version
        version=$(supabase --version 2>&1 | head -n1)
        pass "Supabase CLI installed: $version"
    else
        fail "Supabase CLI not installed (run: brew install supabase/tap/supabase)"
        return 1
    fi

    # Check if logged in
    if supabase projects list &> /dev/null; then
        pass "Supabase CLI authenticated"
    else
        warn "Supabase CLI not authenticated (run: supabase login)"
    fi
}

# ───────────────────────────────────────────────────────────────────────────────
# Database Schema Checks
# ───────────────────────────────────────────────────────────────────────────────

check_database_schema() {
    print_section "Database Schema"

    if [[ -z "${SUPABASE_URL:-}" ]] || [[ -z "${SUPABASE_SERVICE_ROLE_KEY:-}" ]]; then
        fail "Cannot check database schema: missing credentials"
        return 1
    fi

    # Check if email schema exists
    local schema_check
    schema_check=$(curl -s "${SUPABASE_URL}/rest/v1/rpc/check_schema_exists" \
        -H "apikey: ${SUPABASE_SERVICE_ROLE_KEY}" \
        -H "Authorization: Bearer ${SUPABASE_SERVICE_ROLE_KEY}" \
        -H "Content-Type: application/json" \
        -d '{"schema_name": "email"}' 2>&1 || echo "error")

    if [[ "$schema_check" == *"true"* ]]; then
        pass "email schema exists"
    else
        fail "email schema not found (run: psql \"\$POSTGRES_URL\" -f db/migrations/20260128_email_events_schema.sql)"
    fi

    # Check if email.events table exists
    local events_check
    events_check=$(curl -s "${SUPABASE_URL}/rest/v1/email.events?select=id&limit=0" \
        -H "apikey: ${SUPABASE_SERVICE_ROLE_KEY}" \
        -H "Authorization: Bearer ${SUPABASE_SERVICE_ROLE_KEY}" 2>&1)

    if [[ "$events_check" != *"error"* ]] && [[ "$events_check" != *"does not exist"* ]]; then
        pass "email.events table exists"
    else
        fail "email.events table not found"
    fi

    # Check if email.daily_stats table exists
    local stats_check
    stats_check=$(curl -s "${SUPABASE_URL}/rest/v1/email.daily_stats?select=id&limit=0" \
        -H "apikey: ${SUPABASE_SERVICE_ROLE_KEY}" \
        -H "Authorization: Bearer ${SUPABASE_SERVICE_ROLE_KEY}" 2>&1)

    if [[ "$stats_check" != *"error"* ]] && [[ "$stats_check" != *"does not exist"* ]]; then
        pass "email.daily_stats table exists"
    else
        fail "email.daily_stats table not found"
    fi

    # Check if email.recipient_engagement table exists
    local engagement_check
    engagement_check=$(curl -s "${SUPABASE_URL}/rest/v1/email.recipient_engagement?select=id&limit=0" \
        -H "apikey: ${SUPABASE_SERVICE_ROLE_KEY}" \
        -H "Authorization: Bearer ${SUPABASE_SERVICE_ROLE_KEY}" 2>&1)

    if [[ "$engagement_check" != *"error"* ]] && [[ "$engagement_check" != *"does not exist"* ]]; then
        pass "email.recipient_engagement table exists"
    else
        fail "email.recipient_engagement table not found"
    fi
}

# ───────────────────────────────────────────────────────────────────────────────
# Edge Function Checks
# ───────────────────────────────────────────────────────────────────────────────

check_edge_function() {
    print_section "Edge Function"

    # Check if function file exists
    if [[ -f "db/functions/mailgun-events-proxy/index.ts" ]]; then
        pass "mailgun-events-proxy function file exists"
    else
        fail "mailgun-events-proxy function file not found"
    fi

    # Check if function is deployed (requires project ref)
    if [[ -n "${SUPABASE_PROJECT_REF:-}" ]]; then
        local function_url="${SUPABASE_URL}/functions/v1/mailgun-events-proxy"
        local health_check
        health_check=$(curl -s -o /dev/null -w "%{http_code}" "${function_url}" \
            -H "apikey: ${SUPABASE_ANON_KEY}" 2>&1 || echo "000")

        if [[ "$health_check" == "200" ]] || [[ "$health_check" == "405" ]]; then
            pass "mailgun-events-proxy function is deployed and accessible"
        else
            warn "mailgun-events-proxy function not deployed (HTTP $health_check)"
            echo "   Deploy with: supabase functions deploy mailgun-events-proxy"
        fi
    else
        warn "Cannot check Edge Function deployment: SUPABASE_PROJECT_REF not set"
    fi
}

# ───────────────────────────────────────────────────────────────────────────────
# RLS Policy Checks
# ───────────────────────────────────────────────────────────────────────────────

check_rls_policies() {
    print_section "Row Level Security (RLS)"

    if [[ -z "${SUPABASE_URL:-}" ]] || [[ -z "${SUPABASE_SERVICE_ROLE_KEY:-}" ]]; then
        warn "Cannot check RLS policies: missing credentials"
        return 0
    fi

    # Note: This requires a custom RPC function to check RLS status
    # For now, we'll just warn that manual verification is needed
    warn "RLS policies should be verified manually:"
    echo "   1. Open Supabase Dashboard → Database → Tables"
    echo "   2. Check email.events, email.daily_stats, email.recipient_engagement"
    echo "   3. Verify RLS is enabled and policies are present"
}

# ───────────────────────────────────────────────────────────────────────────────
# File Checks
# ───────────────────────────────────────────────────────────────────────────────

check_required_files() {
    print_section "Required Files"

    local files=(
        "db/migrations/20260128_email_events_schema.sql"
        "db/functions/mailgun-events-proxy/index.ts"
        "db/types/email_events.ts"
        "db/sql/bi_queries.sql"
        "db/examples/realtime_subscription.ts"
    )

    for file in "${files[@]}"; do
        if [[ -f "$file" ]]; then
            pass "$file exists"
        else
            fail "$file not found"
        fi
    done
}

# ───────────────────────────────────────────────────────────────────────────────
# Test Data Insert
# ───────────────────────────────────────────────────────────────────────────────

test_data_insert() {
    print_section "Test Data Insert"

    if [[ -z "${SUPABASE_URL:-}" ]] || [[ -z "${SUPABASE_SERVICE_ROLE_KEY:-}" ]]; then
        warn "Cannot test data insert: missing credentials"
        return 0
    fi

    local test_event
    test_event=$(cat <<EOF
{
    "event_type": "delivered",
    "event_timestamp": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
    "message_id": "<test-$(date +%s)@verify.test>",
    "recipient": "verify-test@example.com",
    "sender": "noreply@test.com",
    "subject": "Verification Test",
    "raw_payload": {"test": true, "timestamp": $(date +%s)}
}
EOF
)

    local insert_result
    insert_result=$(curl -s "${SUPABASE_URL}/rest/v1/email.events" \
        -H "apikey: ${SUPABASE_SERVICE_ROLE_KEY}" \
        -H "Authorization: Bearer ${SUPABASE_SERVICE_ROLE_KEY}" \
        -H "Content-Type: application/json" \
        -H "Prefer: return=representation" \
        -d "$test_event" 2>&1)

    if [[ "$insert_result" == *'"id"'* ]]; then
        pass "Test event inserted successfully"

        # Clean up test event
        local event_id
        event_id=$(echo "$insert_result" | grep -o '"id":"[^"]*"' | head -1 | cut -d'"' -f4)
        if [[ -n "$event_id" ]]; then
            curl -s "${SUPABASE_URL}/rest/v1/email.events?id=eq.${event_id}" \
                -H "apikey: ${SUPABASE_SERVICE_ROLE_KEY}" \
                -H "Authorization: Bearer ${SUPABASE_SERVICE_ROLE_KEY}" \
                -X DELETE &> /dev/null
            pass "Test event cleaned up"
        fi
    else
        fail "Test event insert failed: $insert_result"
    fi
}

# ───────────────────────────────────────────────────────────────────────────────
# Main Verification
# ───────────────────────────────────────────────────────────────────────────────

main() {
    print_header "Supabase Email Events Integration Verification"

    check_env_vars
    check_supabase_cli
    check_required_files
    check_database_schema
    check_edge_function
    check_rls_policies
    test_data_insert

    # Summary
    print_header "Verification Summary"
    echo -e "${GREEN}✓ Passed:${NC}   $PASSED"
    echo -e "${RED}✗ Failed:${NC}   $FAILED"
    echo -e "${YELLOW}⚠ Warnings:${NC} $WARNINGS"
    echo ""

    if [[ $FAILED -eq 0 ]]; then
        echo -e "${GREEN}✓ All critical checks passed!${NC}"
        echo ""
        echo "Next steps:"
        echo "  1. Deploy Edge Function: supabase functions deploy mailgun-events-proxy"
        echo "  2. Configure Mailgun webhook: https://api.mailgun.net/v3/domains/\$DOMAIN/webhooks"
        echo "  3. Test webhook delivery: scripts/supabase/test-webhook.sh"
        echo "  4. Set up BI dashboards using: db/sql/bi_queries.sql"
        echo "  5. Implement realtime subscriptions from: db/examples/realtime_subscription.ts"
        exit 0
    else
        echo -e "${RED}✗ Some checks failed. Please fix the issues above.${NC}"
        exit 1
    fi
}

main "$@"
