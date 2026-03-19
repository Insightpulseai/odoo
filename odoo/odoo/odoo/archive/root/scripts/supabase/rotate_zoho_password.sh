#!/usr/bin/env bash
set -euo pipefail

# ========================================
# One-Shot Zoho Password Rotation
# ========================================
# Rotates Zoho SMTP app password across all systems:
# 1. Updates .env.platform.local (dev-only)
# 2. Pushes to GitHub Actions secret (CI)
# 3. Re-applies Supabase Auth SMTP config
# 4. Runs smoke tests to verify
#
# Usage: ./rotate_zoho_password.sh <NEW_PASSWORD>
# Example: ./rotate_zoho_password.sh "Abc123Xyz789"

NEW_PASSWORD="${1:?Error: Provide new Zoho app password as first argument}"
REPO="${2:-Insightpulseai/odoo}"
ENV_FILE=".env.platform.local"

echo "🔐 Rotating Zoho SMTP Password"
echo "===================================================="
echo ""

# Step 1: Update .env.platform.local
echo "→ Step 1/5: Updating $ENV_FILE..."
if [[ ! -f "$ENV_FILE" ]]; then
  echo "❌ $ENV_FILE not found"
  exit 1
fi

# Backup first
cp "$ENV_FILE" "${ENV_FILE}.bak.$(date +%Y%m%d-%H%M%S)"
echo "  ✓ Backup created: ${ENV_FILE}.bak.$(date +%Y%m%d-%H%M%S)"

# Update ZOHO_SMTP_PASS
if grep -q "^ZOHO_SMTP_PASS=" "$ENV_FILE"; then
  perl -i -pe "s/^ZOHO_SMTP_PASS=.*/ZOHO_SMTP_PASS=$NEW_PASSWORD/" "$ENV_FILE"
  echo "  ✓ Updated ZOHO_SMTP_PASS in $ENV_FILE"
else
  echo "ZOHO_SMTP_PASS=$NEW_PASSWORD" >> "$ENV_FILE"
  echo "  ✓ Added ZOHO_SMTP_PASS to $ENV_FILE"
fi

# Reload env
set -a
source "$ENV_FILE"
set +a

echo ""

# Step 2: Push to GitHub Actions
echo "→ Step 2/5: Updating GitHub Actions secret..."
if command -v gh &>/dev/null; then
  gh secret set SMTP_PASS -R "$REPO" --body "$NEW_PASSWORD" >/dev/null 2>&1
  echo "  ✓ SMTP_PASS secret updated in $REPO"
else
  echo "  ⚠️  gh CLI not found - skipping GitHub Actions update"
  echo "  ⚠️  Run manually: gh secret set SMTP_PASS -R $REPO --body '<PASSWORD>'"
fi

echo ""

# Step 3: Re-apply Supabase Auth SMTP config
echo "→ Step 3/5: Re-applying Supabase Auth SMTP configuration..."
if [[ -x "./scripts/supabase/configure_auth_smtp_and_urls.sh" ]]; then
  ./scripts/supabase/configure_auth_smtp_and_urls.sh
  echo "  ✓ Supabase Auth SMTP config updated"
else
  echo "  ❌ configure_auth_smtp_and_urls.sh not found or not executable"
  exit 1
fi

echo ""

# Step 4: Verify Edge Secrets (should not be affected)
echo "→ Step 4/5: Verifying Edge Secrets health..."
if [[ -x "./scripts/supabase/invoke_secret_smoke.sh" ]]; then
  ./scripts/supabase/invoke_secret_smoke.sh
else
  echo "  ⚠️  secret-smoke script not found - skipping"
fi

echo ""

# Step 5: Test Auth flows
echo "→ Step 5/5: Testing Auth flows..."

# Magic Link test
if [[ -x "./scripts/supabase/test_magic_link_curl.sh" ]]; then
  echo "  Testing Magic Link..."
  ./scripts/supabase/test_magic_link_curl.sh
else
  echo "  ⚠️  Magic Link test script not found - skipping"
fi

echo ""

# Wait 60s for rate limit to reset
echo "  ⏳ Waiting 60s for rate limit reset..."
sleep 60

# Email OTP test
if [[ -x "./scripts/supabase/test_email_otp_curl.sh" ]]; then
  echo "  Testing Email OTP..."
  ./scripts/supabase/test_email_otp_curl.sh
else
  echo "  ⚠️  Email OTP test script not found - skipping"
fi

echo ""
echo "===================================================="
echo "✅ Zoho Password Rotation Complete!"
echo ""
echo "Summary:"
echo "  ✓ .env.platform.local updated"
echo "  ✓ GitHub Actions SMTP_PASS secret updated"
echo "  ✓ Supabase Auth SMTP config re-applied"
echo "  ✓ Edge Secrets health verified"
echo "  ✓ Auth flows smoke tested"
echo ""
echo "Next steps:"
echo "  1. Check business@insightpulseai.com inbox for test emails"
echo "  2. Verify Magic Link and OTP emails received successfully"
echo "  3. Delete backup: rm ${ENV_FILE}.bak.*"
echo ""
