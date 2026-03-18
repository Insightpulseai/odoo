#!/usr/bin/env bash
set -euo pipefail

# Safe user deletion script for Supabase auth
# Handles foreign key constraints by deleting child records first

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Load credentials from environment
if [ -f "$HOME/.zshrc" ]; then
  source "$HOME/.zshrc"
fi

# Validate required environment variables
if [ -z "${POSTGRES_URL_NON_POOLING:-}" ]; then
  echo "Error: POSTGRES_URL_NON_POOLING not set in environment"
  echo "Expected format: postgresql://postgres.<project_ref>:<password>@aws-1-us-east-1.pooler.supabase.com:5432/postgres?sslmode=require"
  exit 1
fi

# Check for user ID or email argument
if [ $# -eq 0 ]; then
  echo "Usage: $0 <user_id_or_email>"
  echo ""
  echo "Examples:"
  echo "  $0 f0304ff6-60bd-439e-be9c-ea36c29a3464"
  echo "  $0 jgtolentino.rn@gmail.com"
  exit 1
fi

USER_IDENTIFIER="$1"

# Determine if argument is UUID or email
if [[ "$USER_IDENTIFIER" =~ ^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$ ]]; then
  WHERE_CLAUSE="id = '$USER_IDENTIFIER'"
else
  WHERE_CLAUSE="email = '$USER_IDENTIFIER'"
fi

echo "🔍 Looking up user..."

# Get user ID
USER_ID=$(psql "$POSTGRES_URL_NON_POOLING" -t -c "SELECT id FROM auth.users WHERE $WHERE_CLAUSE;" | xargs)

if [ -z "$USER_ID" ]; then
  echo "❌ User not found: $USER_IDENTIFIER"
  exit 1
fi

USER_EMAIL=$(psql "$POSTGRES_URL_NON_POOLING" -t -c "SELECT email FROM auth.users WHERE id = '$USER_ID';" | xargs)

echo "✅ Found user: $USER_EMAIL (ID: $USER_ID)"
echo ""
echo "⚠️  WARNING: This will permanently delete the user and all associated data:"
echo "   - Identity providers"
echo "   - Active sessions"
echo "   - Refresh tokens"
echo "   - MFA factors"
echo "   - One-time tokens"
echo "   - OAuth authorizations"
echo ""
read -p "Continue? (yes/no): " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
  echo "Cancelled."
  exit 0
fi

echo ""
echo "🗑️  Deleting user data..."

# Delete child records in correct order (least to most dependent)
psql "$POSTGRES_URL_NON_POOLING" <<SQL
BEGIN;

-- Delete OAuth authorizations
DELETE FROM auth.oauth_authorizations WHERE user_id = '$USER_ID';

-- Delete one-time tokens
DELETE FROM auth.one_time_tokens WHERE user_id = '$USER_ID';

-- Delete MFA factors
DELETE FROM auth.mfa_factors WHERE user_id = '$USER_ID';

-- Delete refresh tokens
DELETE FROM auth.refresh_tokens WHERE user_id = '$USER_ID';

-- Delete sessions
DELETE FROM auth.sessions WHERE user_id = '$USER_ID';

-- Delete identities
DELETE FROM auth.identities WHERE user_id = '$USER_ID';

-- Finally delete the user
DELETE FROM auth.users WHERE id = '$USER_ID';

COMMIT;

SELECT '✅ User deleted successfully' AS result;
SQL

echo ""
echo "✅ User $USER_EMAIL has been deleted."
