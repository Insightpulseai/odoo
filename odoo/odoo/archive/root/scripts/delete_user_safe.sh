#!/usr/bin/env bash
set -euo pipefail

# ============================================================================
# Safe User Deletion Script
# ============================================================================
# Purpose: Delete user from Supabase with proper foreign key handling
#
# Usage: ./scripts/delete_user_safe.sh <user_id_or_email>
#
# This script handles all foreign key dependencies in correct order:
# 1. OAuth authorizations/consents
# 2. MFA factors
# 3. One-time tokens
# 4. Sessions
# 5. Identities
# 6. App profiles (our custom table)
# 7. Audit logs (set user_id to NULL, not deleted)
# 8. Finally, the user record
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
  source "$HOME/.zshrc" 2>/dev/null || true
fi

if [ -z "${POSTGRES_URL_NON_POOLING:-}" ]; then
  echo -e "${RED}✗ Missing POSTGRES_URL_NON_POOLING${NC}"
  echo "Set in ~/.zshrc or export manually"
  exit 1
fi

# Get user identifier (ID or email)
USER_IDENTIFIER="${1:-}"

if [ -z "$USER_IDENTIFIER" ]; then
  echo -e "${RED}Usage: $0 <user_id_or_email>${NC}"
  echo ""
  echo "Examples:"
  echo "  $0 f0304ff6-60bd-439e-be9c-ea36c29a3464"
  echo "  $0 test@example.com"
  exit 1
fi

echo ""
echo -e "${BLUE}=====================================${NC}"
echo -e "${BLUE}  Safe User Deletion${NC}"
echo -e "${BLUE}=====================================${NC}"
echo ""

# Resolve user ID from email if needed
if [[ "$USER_IDENTIFIER" =~ ^[a-f0-9\-]{36}$ ]]; then
  USER_ID="$USER_IDENTIFIER"
  USER_EMAIL=$(psql "$POSTGRES_URL_NON_POOLING" -t -c "SELECT email FROM auth.users WHERE id = '$USER_ID';" | xargs)
else
  USER_EMAIL="$USER_IDENTIFIER"
  USER_ID=$(psql "$POSTGRES_URL_NON_POOLING" -t -c "SELECT id FROM auth.users WHERE email = '$USER_EMAIL';" | xargs)
fi

if [ -z "$USER_ID" ]; then
  echo -e "${RED}✗ User not found: $USER_IDENTIFIER${NC}"
  exit 1
fi

echo -e "${YELLOW}User to delete:${NC}"
echo "  ID: $USER_ID"
echo "  Email: $USER_EMAIL"
echo ""

# Check if this is the last owner
IS_LAST_OWNER=$(psql "$POSTGRES_URL_NON_POOLING" -t -c "
  SELECT EXISTS(
    SELECT 1 FROM app.profiles
    WHERE user_id = '$USER_ID'
      AND role = 'owner'
      AND is_active = true
      AND (
        SELECT COUNT(*)
        FROM app.profiles p2
        WHERE p2.tenant_id = (SELECT tenant_id FROM app.profiles WHERE user_id = '$USER_ID')
          AND p2.role = 'owner'
          AND p2.is_active = true
      ) = 1
  );
" | xargs)

if [ "$IS_LAST_OWNER" = "t" ]; then
  echo -e "${RED}⚠️  WARNING: This is the last owner of their tenant!${NC}"
  echo -e "${RED}   Deleting will leave the tenant without an owner.${NC}"
  echo ""
  read -p "Are you sure you want to continue? (yes/no): " CONFIRM
  if [ "$CONFIRM" != "yes" ]; then
    echo -e "${YELLOW}Deletion cancelled${NC}"
    exit 0
  fi
fi

# Confirm deletion
echo -e "${YELLOW}This will permanently delete the user and all associated data.${NC}"
read -p "Continue? (yes/no): " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
  echo -e "${YELLOW}Deletion cancelled${NC}"
  exit 0
fi

echo ""
echo -e "${BLUE}[1/9] Deleting OAuth authorizations...${NC}"
DELETED=$(psql "$POSTGRES_URL_NON_POOLING" -t -c "
  DELETE FROM auth.oauth_authorizations WHERE user_id = '$USER_ID';
  SELECT COUNT(*);
" | xargs)
echo -e "${GREEN}✓ Deleted $DELETED OAuth authorizations${NC}"

echo -e "${BLUE}[2/9] Deleting OAuth consents...${NC}"
DELETED=$(psql "$POSTGRES_URL_NON_POOLING" -t -c "
  DELETE FROM auth.oauth_consents WHERE user_id = '$USER_ID';
  SELECT COUNT(*);
" | xargs)
echo -e "${GREEN}✓ Deleted $DELETED OAuth consents${NC}"

echo -e "${BLUE}[3/9] Deleting MFA factors...${NC}"
DELETED=$(psql "$POSTGRES_URL_NON_POOLING" -t -c "
  DELETE FROM auth.mfa_factors WHERE user_id = '$USER_ID';
  SELECT COUNT(*);
" | xargs)
echo -e "${GREEN}✓ Deleted $DELETED MFA factors${NC}"

echo -e "${BLUE}[4/9] Deleting one-time tokens...${NC}"
DELETED=$(psql "$POSTGRES_URL_NON_POOLING" -t -c "
  DELETE FROM auth.one_time_tokens WHERE user_id = '$USER_ID';
  SELECT COUNT(*);
" | xargs)
echo -e "${GREEN}✓ Deleted $DELETED one-time tokens${NC}"

echo -e "${BLUE}[5/9] Deleting refresh tokens...${NC}"
DELETED=$(psql "$POSTGRES_URL_NON_POOLING" -t -c "
  DELETE FROM auth.refresh_tokens WHERE user_id = '$USER_ID';
  SELECT COUNT(*);
" | xargs)
echo -e "${GREEN}✓ Deleted $DELETED refresh tokens${NC}"

echo -e "${BLUE}[6/9] Deleting sessions...${NC}"
DELETED=$(psql "$POSTGRES_URL_NON_POOLING" -t -c "
  DELETE FROM auth.sessions WHERE user_id = '$USER_ID';
  SELECT COUNT(*);
" | xargs)
echo -e "${GREEN}✓ Deleted $DELETED sessions${NC}"

echo -e "${BLUE}[7/9] Deleting identities...${NC}"
DELETED=$(psql "$POSTGRES_URL_NON_POOLING" -t -c "
  DELETE FROM auth.identities WHERE user_id = '$USER_ID';
  SELECT COUNT(*);
" | xargs)
echo -e "${GREEN}✓ Deleted $DELETED identities${NC}"

echo -e "${BLUE}[8/9] Deleting app profile...${NC}"
DELETED=$(psql "$POSTGRES_URL_NON_POOLING" -t -c "
  DELETE FROM app.profiles WHERE user_id = '$USER_ID';
  SELECT COUNT(*);
" | xargs)
echo -e "${GREEN}✓ Deleted app profile${NC}"

echo -e "${BLUE}[9/9] Anonymizing audit logs...${NC}"
UPDATED=$(psql "$POSTGRES_URL_NON_POOLING" -t -c "
  UPDATE ops.audit_log SET user_id = NULL WHERE user_id = '$USER_ID';
  SELECT COUNT(*);
" | xargs)
echo -e "${GREEN}✓ Anonymized $UPDATED audit log entries${NC}"

echo -e "${BLUE}[10/10] Deleting user record...${NC}"
psql "$POSTGRES_URL_NON_POOLING" -c "DELETE FROM auth.users WHERE id = '$USER_ID';"
echo -e "${GREEN}✓ User deleted${NC}"

echo ""
echo -e "${GREEN}=====================================${NC}"
echo -e "${GREEN}  ✅ User successfully deleted${NC}"
echo -e "${GREEN}=====================================${NC}"
echo ""
echo "Deleted user: $USER_EMAIL ($USER_ID)"
echo ""
