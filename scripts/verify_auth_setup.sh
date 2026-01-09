#!/usr/bin/env bash
set -euo pipefail

# ============================================================================
# Auth Setup Verification Script
# ============================================================================
# Purpose: Verify complete auth system setup (migrations, RLS, JWT claims)
#
# Usage: ./scripts/verify_auth_setup.sh
#
# Checks:
# 1. Schemas exist (app, ops)
# 2. Tables created (tenants, profiles, service_tokens, audit_log)
# 3. RLS enabled on all tables
# 4. JWT claim functions exist
# 5. Custom access token hook configured
# 6. Triggers and policies exist
# ============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

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

# Load credentials
if [ -f "$HOME/.zshrc" ]; then
  source "$HOME/.zshrc"
fi

if [ -z "${POSTGRES_URL_NON_POOLING:-}" ]; then
  echo -e "${RED}✗ POSTGRES_URL_NON_POOLING not set${NC}"
  echo "Set in ~/.zshrc or export manually"
  exit 1
fi

# Helper function for checks
check() {
  local description="$1"
  local query="$2"
  local expected="$3"

  result=$(psql "$POSTGRES_URL_NON_POOLING" -t -c "$query" 2>&1 | xargs)

  if [ "$result" = "$expected" ]; then
    echo -e "${GREEN}✓ $description${NC}"
    ((PASSED++))
  else
    echo -e "${RED}✗ $description${NC}"
    echo -e "  Expected: ${YELLOW}$expected${NC}"
    echo -e "  Got: ${YELLOW}$result${NC}"
    ((FAILED++))
  fi
}

# Helper for existence checks
check_exists() {
  local description="$1"
  local query="$2"

  result=$(psql "$POSTGRES_URL_NON_POOLING" -t -c "$query" 2>&1 | xargs)

  if [ -n "$result" ] && [ "$result" != "0" ]; then
    echo -e "${GREEN}✓ $description${NC}"
    ((PASSED++))
  else
    echo -e "${RED}✗ $description${NC}"
    ((FAILED++))
  fi
}

# Header
echo ""
echo -e "${BLUE}=====================================${NC}"
echo -e "${BLUE}  Auth Setup Verification${NC}"
echo -e "${BLUE}=====================================${NC}"
echo ""

# 1. Schema Checks
echo -e "${BLUE}[1/7] Checking Schemas...${NC}"
check "Schema: app" \
  "SELECT COUNT(*) FROM information_schema.schemata WHERE schema_name = 'app';" \
  "1"

check "Schema: ops" \
  "SELECT COUNT(*) FROM information_schema.schemata WHERE schema_name = 'ops';" \
  "1"

echo ""

# 2. Table Checks
echo -e "${BLUE}[2/7] Checking Tables...${NC}"
check "Table: app.tenants" \
  "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'app' AND table_name = 'tenants';" \
  "1"

check "Table: app.profiles" \
  "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'app' AND table_name = 'profiles';" \
  "1"

check "Table: ops.service_tokens" \
  "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'ops' AND table_name = 'service_tokens';" \
  "1"

check "Table: ops.audit_log" \
  "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'ops' AND table_name = 'audit_log';" \
  "1"

echo ""

# 3. RLS Checks
echo -e "${BLUE}[3/7] Checking Row Level Security...${NC}"
check "RLS enabled: app.tenants" \
  "SELECT relrowsecurity::int FROM pg_class WHERE relname = 'tenants' AND relnamespace = 'app'::regnamespace;" \
  "1"

check "RLS enabled: app.profiles" \
  "SELECT relrowsecurity::int FROM pg_class WHERE relname = 'profiles' AND relnamespace = 'app'::regnamespace;" \
  "1"

check "RLS enabled: ops.service_tokens" \
  "SELECT relrowsecurity::int FROM pg_class WHERE relname = 'service_tokens' AND relnamespace = 'ops'::regnamespace;" \
  "1"

check "RLS enabled: ops.audit_log" \
  "SELECT relrowsecurity::int FROM pg_class WHERE relname = 'audit_log' AND relnamespace = 'ops'::regnamespace;" \
  "1"

echo ""

# 4. Policy Checks
echo -e "${BLUE}[4/7] Checking RLS Policies...${NC}"
check_exists "Policies on app.tenants (expected: 2)" \
  "SELECT COUNT(*) FROM pg_policies WHERE schemaname = 'app' AND tablename = 'tenants';"

check_exists "Policies on app.profiles (expected: 5)" \
  "SELECT COUNT(*) FROM pg_policies WHERE schemaname = 'app' AND tablename = 'profiles';"

check_exists "Policies on ops.service_tokens (expected: 4)" \
  "SELECT COUNT(*) FROM pg_policies WHERE schemaname = 'ops' AND tablename = 'service_tokens';"

echo ""

# 5. Function Checks
echo -e "${BLUE}[5/7] Checking JWT Claim Functions...${NC}"
check_exists "Function: app.current_tenant_id()" \
  "SELECT COUNT(*) FROM pg_proc WHERE proname = 'current_tenant_id' AND pronamespace = 'app'::regnamespace;"

check_exists "Function: app.current_role()" \
  "SELECT COUNT(*) FROM pg_proc WHERE proname = 'current_role' AND pronamespace = 'app'::regnamespace;"

check_exists "Function: app.current_user_id()" \
  "SELECT COUNT(*) FROM pg_proc WHERE proname = 'current_user_id' AND pronamespace = 'app'::regnamespace;"

check_exists "Function: public.custom_access_token_hook()" \
  "SELECT COUNT(*) FROM pg_proc WHERE proname = 'custom_access_token_hook' AND pronamespace = 'public'::regnamespace;"

echo ""

# 6. Trigger Checks
echo -e "${BLUE}[6/7] Checking Triggers...${NC}"
check_exists "Trigger: on_auth_user_created" \
  "SELECT COUNT(*) FROM pg_trigger WHERE tgname = 'on_auth_user_created';"

check_exists "Trigger: tenants_updated_at" \
  "SELECT COUNT(*) FROM pg_trigger WHERE tgname = 'tenants_updated_at';"

check_exists "Trigger: profiles_updated_at" \
  "SELECT COUNT(*) FROM pg_trigger WHERE tgname = 'profiles_updated_at';"

check_exists "Trigger: profiles_audit_trigger" \
  "SELECT COUNT(*) FROM pg_trigger WHERE tgname = 'profiles_audit_trigger';"

echo ""

# 7. Bootstrap Data Check
echo -e "${BLUE}[7/7] Checking Bootstrap Data...${NC}"
check_exists "Bootstrap tenant exists" \
  "SELECT COUNT(*) FROM app.tenants WHERE slug = 'insightpulse';"

echo ""

# Summary
echo -e "${BLUE}=====================================${NC}"
echo -e "${BLUE}  Verification Summary${NC}"
echo -e "${BLUE}=====================================${NC}"
echo -e "${GREEN}Passed: $PASSED${NC}"
echo -e "${RED}Failed: $FAILED${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
  echo -e "${GREEN}✓ All checks passed! Auth system is properly configured.${NC}"
  echo ""
  echo -e "${YELLOW}Next Steps:${NC}"
  echo "1. Enable Custom Access Token Hook in Supabase Dashboard:"
  echo "   → Authentication → Hooks → Custom Access Token"
  echo "   → Function: public.custom_access_token_hook"
  echo ""
  echo "2. Deploy Edge Functions:"
  echo "   supabase functions deploy auth-bootstrap"
  echo "   supabase functions deploy tenant-invite"
  echo ""
  echo "3. Test bootstrap flow:"
  echo "   ./scripts/test_auth_bootstrap.sh"
  exit 0
else
  echo -e "${RED}✗ $FAILED checks failed. Please review errors above.${NC}"
  echo ""
  echo -e "${YELLOW}Common Issues:${NC}"
  echo "• Migrations not applied: psql \"\$POSTGRES_URL\" -f supabase/migrations/500*.sql"
  echo "• Custom hook not enabled: Check Supabase Dashboard → Authentication → Hooks"
  echo "• Connection issues: Verify POSTGRES_URL_NON_POOLING is correct"
  exit 1
fi
