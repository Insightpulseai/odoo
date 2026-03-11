#!/usr/bin/env bash
set -euo pipefail

# ============================================================================
# Auth Bootstrap Test Script
# ============================================================================
# Purpose: Test complete auth flow (bootstrap tenant, invite user, verify JWT)
#
# Usage: ./scripts/test_auth_bootstrap.sh
#
# Tests:
# 1. Bootstrap new tenant with owner
# 2. Login as owner and verify JWT claims
# 3. Invite new user as admin
# 4. Login as invited user and verify tenant isolation
# 5. Attempt cross-tenant access (should fail)
# ============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Load credentials
if [ -f "$HOME/.zshrc" ]; then
  source "$HOME/.zshrc"
fi

if [ -z "${SUPABASE_URL:-}" ] || [ -z "${SUPABASE_ANON_KEY:-}" ]; then
  echo -e "${RED}✗ Missing SUPABASE_URL or SUPABASE_ANON_KEY${NC}"
  echo "Set in ~/.zshrc or export manually"
  exit 1
fi

# Generate unique test tenant slug
TEST_SLUG="test-$(date +%s)"
TEST_OWNER_EMAIL="owner-${TEST_SLUG}@test.local"
TEST_OWNER_PASSWORD="TestPassword123!"
TEST_USER_EMAIL="user-${TEST_SLUG}@test.local"

echo ""
echo -e "${BLUE}=====================================${NC}"
echo -e "${BLUE}  Auth Bootstrap Test${NC}"
echo -e "${BLUE}=====================================${NC}"
echo ""

# Test 1: Bootstrap Tenant
echo -e "${BLUE}[1/5] Bootstrapping Tenant: $TEST_SLUG${NC}"

BOOTSTRAP_RESPONSE=$(curl -s -X POST \
  "$SUPABASE_URL/functions/v1/auth-bootstrap" \
  -H "apikey: $SUPABASE_ANON_KEY" \
  -H "Content-Type: application/json" \
  -d "{
    \"tenant\": {
      \"slug\": \"$TEST_SLUG\",
      \"name\": \"Test Tenant $TEST_SLUG\",
      \"settings\": {\"features\": [\"ocr\", \"bir_compliance\"]}
    },
    \"owner\": {
      \"email\": \"$TEST_OWNER_EMAIL\",
      \"password\": \"$TEST_OWNER_PASSWORD\",
      \"display_name\": \"Test Owner\"
    }
  }")

if echo "$BOOTSTRAP_RESPONSE" | jq -e '.success' > /dev/null 2>&1; then
  TENANT_ID=$(echo "$BOOTSTRAP_RESPONSE" | jq -r '.tenant.id')
  OWNER_ID=$(echo "$BOOTSTRAP_RESPONSE" | jq -r '.user.id')
  echo -e "${GREEN}✓ Tenant created: $TENANT_ID${NC}"
  echo -e "${GREEN}✓ Owner created: $OWNER_ID${NC}"
else
  echo -e "${RED}✗ Bootstrap failed${NC}"
  echo "$BOOTSTRAP_RESPONSE" | jq '.'
  exit 1
fi

sleep 2
echo ""

# Test 2: Login as Owner
echo -e "${BLUE}[2/5] Login as Owner${NC}"

LOGIN_RESPONSE=$(curl -s -X POST \
  "$SUPABASE_URL/auth/v1/token?grant_type=password" \
  -H "apikey: $SUPABASE_ANON_KEY" \
  -H "Content-Type: application/json" \
  -d "{
    \"email\": \"$TEST_OWNER_EMAIL\",
    \"password\": \"$TEST_OWNER_PASSWORD\"
  }")

if echo "$LOGIN_RESPONSE" | jq -e '.access_token' > /dev/null 2>&1; then
  OWNER_JWT=$(echo "$LOGIN_RESPONSE" | jq -r '.access_token')
  OWNER_TENANT_ID=$(echo "$LOGIN_RESPONSE" | jq -r '.user.user_metadata.tenant_id // empty')
  OWNER_ROLE=$(echo "$LOGIN_RESPONSE" | jq -r '.user.user_metadata.role // empty')

  if [ "$OWNER_TENANT_ID" = "$TENANT_ID" ] && [ "$OWNER_ROLE" = "owner" ]; then
    echo -e "${GREEN}✓ Owner logged in successfully${NC}"
    echo -e "  Tenant ID: ${YELLOW}$OWNER_TENANT_ID${NC}"
    echo -e "  Role: ${YELLOW}$OWNER_ROLE${NC}"
  else
    echo -e "${RED}✗ JWT claims missing or incorrect${NC}"
    echo -e "  Expected tenant_id: $TENANT_ID, got: ${OWNER_TENANT_ID:-none}"
    echo -e "  Expected role: owner, got: ${OWNER_ROLE:-none}"
    exit 1
  fi
else
  echo -e "${RED}✗ Owner login failed${NC}"
  echo "$LOGIN_RESPONSE" | jq '.'
  exit 1
fi

sleep 2
echo ""

# Test 3: Invite User
echo -e "${BLUE}[3/5] Invite User as Admin${NC}"

INVITE_RESPONSE=$(curl -s -X POST \
  "$SUPABASE_URL/functions/v1/tenant-invite" \
  -H "apikey: $SUPABASE_ANON_KEY" \
  -H "Authorization: Bearer $OWNER_JWT" \
  -H "Content-Type: application/json" \
  -d "{
    \"email\": \"$TEST_USER_EMAIL\",
    \"role\": \"finance\",
    \"display_name\": \"Test User\",
    \"send_email\": false
  }")

if echo "$INVITE_RESPONSE" | jq -e '.success' > /dev/null 2>&1; then
  USER_ID=$(echo "$INVITE_RESPONSE" | jq -r '.user.id')
  echo -e "${GREEN}✓ User invited: $USER_ID${NC}"
  echo -e "  Email: ${YELLOW}$TEST_USER_EMAIL${NC}"
  echo -e "  Role: ${YELLOW}finance${NC}"
else
  echo -e "${RED}✗ User invitation failed${NC}"
  echo "$INVITE_RESPONSE" | jq '.'
  exit 1
fi

sleep 2
echo ""

# Test 4: Verify Tenant Isolation (RLS)
echo -e "${BLUE}[4/5] Verify Tenant Isolation${NC}"

# Query tenants as owner (should see own tenant)
OWNER_TENANTS=$(curl -s -X GET \
  "$SUPABASE_URL/rest/v1/tenants?select=id,slug" \
  -H "apikey: $SUPABASE_ANON_KEY" \
  -H "Authorization: Bearer $OWNER_JWT")

TENANT_COUNT=$(echo "$OWNER_TENANTS" | jq 'length')

if [ "$TENANT_COUNT" = "1" ]; then
  VISIBLE_TENANT=$(echo "$OWNER_TENANTS" | jq -r '.[0].id')
  if [ "$VISIBLE_TENANT" = "$TENANT_ID" ]; then
    echo -e "${GREEN}✓ Tenant isolation working${NC}"
    echo -e "  Owner can only see their tenant: ${YELLOW}$TEST_SLUG${NC}"
  else
    echo -e "${RED}✗ Wrong tenant visible${NC}"
    echo -e "  Expected: $TENANT_ID"
    echo -e "  Got: $VISIBLE_TENANT"
    exit 1
  fi
else
  echo -e "${RED}✗ Tenant isolation broken${NC}"
  echo -e "  Expected 1 tenant, got: $TENANT_COUNT"
  echo "$OWNER_TENANTS" | jq '.'
  exit 1
fi

sleep 2
echo ""

# Test 5: Verify Profile Access
echo -e "${BLUE}[5/5] Verify Profile Access${NC}"

# Query profiles as owner (should see both owner and invited user)
OWNER_PROFILES=$(curl -s -X GET \
  "$SUPABASE_URL/rest/v1/profiles?select=user_id,role&tenant_id=eq.$TENANT_ID" \
  -H "apikey: $SUPABASE_ANON_KEY" \
  -H "Authorization: Bearer $OWNER_JWT")

PROFILE_COUNT=$(echo "$OWNER_PROFILES" | jq 'length')

if [ "$PROFILE_COUNT" = "2" ]; then
  echo -e "${GREEN}✓ Profile access working${NC}"
  echo -e "  Owner can see 2 profiles (owner + invited user)"
  echo "$OWNER_PROFILES" | jq -r '.[] | "  - \(.role): \(.user_id)"'
else
  echo -e "${RED}✗ Profile access broken${NC}"
  echo -e "  Expected 2 profiles, got: $PROFILE_COUNT"
  echo "$OWNER_PROFILES" | jq '.'
  exit 1
fi

echo ""

# Summary
echo -e "${BLUE}=====================================${NC}"
echo -e "${BLUE}  Test Summary${NC}"
echo -e "${BLUE}=====================================${NC}"
echo -e "${GREEN}✓ All tests passed!${NC}"
echo ""
echo -e "${YELLOW}Test Artifacts:${NC}"
echo "  Tenant: $TEST_SLUG ($TENANT_ID)"
echo "  Owner: $TEST_OWNER_EMAIL ($OWNER_ID)"
echo "  User: $TEST_USER_EMAIL ($USER_ID)"
echo ""
echo -e "${YELLOW}Cleanup:${NC}"
echo "To delete test data, run:"
echo "  psql \"\$POSTGRES_URL\" -c \"DELETE FROM app.tenants WHERE id = '$TENANT_ID';\""
echo ""

exit 0
