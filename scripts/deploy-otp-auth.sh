#!/bin/bash
# Deploy Email OTP Authentication System to Supabase
# Purpose: One-command deployment of database schema + Edge Functions

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"

echo "============================================================"
echo "Email OTP Authentication - Deployment"
echo "============================================================"
echo ""

# Check prerequisites
echo "Checking prerequisites..."

if ! command -v psql &> /dev/null; then
    echo "❌ ERROR: psql not found. Install PostgreSQL client."
    exit 1
fi

if ! command -v supabase &> /dev/null; then
    echo "❌ ERROR: supabase CLI not found. Install: npm install -g supabase"
    exit 1
fi

# Check environment variables
if [ -z "$POSTGRES_URL" ]; then
    echo "❌ ERROR: POSTGRES_URL not set"
    echo "Required format: postgresql://user:pass@host:6543/db"
    exit 1
fi

if [ -z "$MAILGUN_API_KEY" ]; then
    echo "⚠️  WARNING: MAILGUN_API_KEY not set (will fail when sending emails)"
fi

echo "✅ Prerequisites check passed"
echo ""

# Step 1: Deploy database schema
echo "Step 1: Deploying database schema..."
echo "---"

SCHEMA_FILE="$REPO_ROOT/supabase/migrations/20260120_email_otp_auth.sql"

if [ ! -f "$SCHEMA_FILE" ]; then
    echo "❌ ERROR: Schema file not found: $SCHEMA_FILE"
    exit 1
fi

echo "Applying schema to database..."
psql "$POSTGRES_URL" -f "$SCHEMA_FILE" --set ON_ERROR_STOP=1

if [ $? -eq 0 ]; then
    echo "✅ Database schema deployed successfully"
else
    echo "❌ Database schema deployment failed"
    exit 1
fi

echo ""

# Verify tables created
echo "Verifying tables..."
TABLES=$(psql "$POSTGRES_URL" -t -c "SELECT table_name FROM information_schema.tables WHERE table_schema = 'auth_otp' ORDER BY table_name;")

echo "Tables created:"
echo "$TABLES" | sed 's/^/ - /'

echo ""

# Step 2: Deploy Edge Functions
echo "Step 2: Deploying Edge Functions..."
echo "---"

SUPABASE_PROJECT_REF="${SUPABASE_PROJECT_REF:-spdtwktxdalcfigzeqrz}"

echo "Deploying to project: $SUPABASE_PROJECT_REF"
echo ""

# Deploy auth-otp-request
echo "Deploying auth-otp-request..."
cd "$REPO_ROOT/supabase/functions/auth-otp-request"
supabase functions deploy auth-otp-request --project-ref "$SUPABASE_PROJECT_REF"

if [ $? -eq 0 ]; then
    echo "✅ auth-otp-request deployed"
else
    echo "❌ auth-otp-request deployment failed"
    exit 1
fi

echo ""

# Deploy auth-otp-verify
echo "Deploying auth-otp-verify..."
cd "$REPO_ROOT/supabase/functions/auth-otp-verify"
supabase functions deploy auth-otp-verify --project-ref "$SUPABASE_PROJECT_REF"

if [ $? -eq 0 ]; then
    echo "✅ auth-otp-verify deployed"
else
    echo "❌ auth-otp-verify deployment failed"
    exit 1
fi

cd "$REPO_ROOT"

echo ""

# Step 3: Set secrets
echo "Step 3: Setting Edge Function secrets..."
echo "---"

if [ -n "$MAILGUN_API_KEY" ]; then
    echo "Setting MAILGUN_API_KEY..."
    echo "$MAILGUN_API_KEY" | supabase secrets set MAILGUN_API_KEY --project-ref "$SUPABASE_PROJECT_REF" --from-stdin
    echo "✅ MAILGUN_API_KEY set"
else
    echo "⚠️  MAILGUN_API_KEY not set - skipping"
fi

if [ -n "$MAILGUN_DOMAIN" ]; then
    echo "Setting MAILGUN_DOMAIN..."
    echo "$MAILGUN_DOMAIN" | supabase secrets set MAILGUN_DOMAIN --project-ref "$SUPABASE_PROJECT_REF" --from-stdin
    echo "✅ MAILGUN_DOMAIN set"
else
    echo "Using default MAILGUN_DOMAIN: mg.insightpulseai.net"
    echo "mg.insightpulseai.net" | supabase secrets set MAILGUN_DOMAIN --project-ref "$SUPABASE_PROJECT_REF" --from-stdin
fi

echo ""

# Step 4: Test endpoints
echo "Step 4: Testing endpoints..."
echo "---"

SUPABASE_URL="${SUPABASE_URL:-https://spdtwktxdalcfigzeqrz.supabase.co}"
SUPABASE_ANON_KEY="${SUPABASE_ANON_KEY}"

if [ -z "$SUPABASE_ANON_KEY" ]; then
    echo "⚠️  SUPABASE_ANON_KEY not set - skipping endpoint tests"
    echo "Set SUPABASE_ANON_KEY to test endpoints"
else
    echo "Testing auth-otp-request endpoint..."
    TEST_EMAIL="test-deploy-$(date +%s)@example.com"

    RESPONSE=$(curl -s -X POST "$SUPABASE_URL/functions/v1/auth-otp-request" \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer $SUPABASE_ANON_KEY" \
        -d "{\"email\":\"$TEST_EMAIL\"}" \
        -w "\n%{http_code}")

    HTTP_CODE=$(echo "$RESPONSE" | tail -1)
    BODY=$(echo "$RESPONSE" | head -n -1)

    if [ "$HTTP_CODE" -eq 200 ]; then
        echo "✅ auth-otp-request endpoint working (HTTP $HTTP_CODE)"
        echo "Response: $BODY" | jq '.' 2>/dev/null || echo "$BODY"
    else
        echo "❌ auth-otp-request endpoint failed (HTTP $HTTP_CODE)"
        echo "Response: $BODY"
    fi
fi

echo ""

# Step 5: Setup cron job (optional)
echo "Step 5: Setting up cron job for cleanup..."
echo "---"

echo "Creating cron job to cleanup expired OTPs daily at 2 AM..."

CRON_SQL=$(cat <<'SQL'
SELECT cron.schedule(
  'cleanup-expired-otps',
  '0 2 * * *', -- 2 AM daily
  $$SELECT auth_otp.cleanup_expired_otps();$$
);
SQL
)

psql "$POSTGRES_URL" -c "$CRON_SQL" 2>/dev/null || echo "⚠️  Cron extension not available - cleanup must be scheduled manually"

echo ""

# Summary
echo "============================================================"
echo "✅ Deployment Complete"
echo "============================================================"
echo ""
echo "Database Schema:"
echo "  - auth_otp.email_otps"
echo "  - auth_otp.rate_limits"
echo "  - auth_otp.audit_log"
echo ""
echo "Edge Functions:"
echo "  - POST $SUPABASE_URL/functions/v1/auth-otp-request"
echo "  - POST $SUPABASE_URL/functions/v1/auth-otp-verify"
echo ""
echo "Secrets:"
echo "  - MAILGUN_API_KEY (set: $([ -n "$MAILGUN_API_KEY" ] && echo "✅" || echo "❌"))"
echo "  - MAILGUN_DOMAIN (set: ✅)"
echo ""
echo "Next Steps:"
echo "  1. Test OTP flow with a real email:"
echo "     curl -X POST $SUPABASE_URL/functions/v1/auth-otp-request \\"
echo "       -H \"Content-Type: application/json\" \\"
echo "       -H \"Authorization: Bearer \$SUPABASE_ANON_KEY\" \\"
echo "       -d '{\"email\":\"your-email@example.com\"}'"
echo ""
echo "  2. Check email and verify OTP:"
echo "     curl -X POST $SUPABASE_URL/functions/v1/auth-otp-verify \\"
echo "       -H \"Content-Type: application/json\" \\"
echo "       -H \"Authorization: Bearer \$SUPABASE_ANON_KEY\" \\"
echo "       -d '{\"email\":\"your-email@example.com\",\"otp_code\":\"123456\"}'"
echo ""
echo "Documentation: docs/auth/EMAIL_OTP_IMPLEMENTATION.md"
echo ""
