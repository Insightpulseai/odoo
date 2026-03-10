#!/usr/bin/env bash
set -euo pipefail

# ========================================
# Verify Supabase Auth Configuration
# ========================================
# Checks that SMTP, URLs, and templates are configured

echo "🔍 Verifying Auth Configuration..."

# Verify prerequisites
: "${SUPABASE_PROJECT_REF:?Error: SUPABASE_PROJECT_REF not set}"
: "${SUPABASE_ACCESS_TOKEN:?Error: SUPABASE_ACCESS_TOKEN not set}"

# Fetch current config
config=$(curl -fsS "https://api.supabase.com/v1/projects/${SUPABASE_PROJECT_REF}/config/auth" \
  -H "Authorization: Bearer ${SUPABASE_ACCESS_TOKEN}")

# Check critical fields
echo "→ Checking configuration..."

site_url=$(echo "$config" | jq -r '.site_url // empty')
smtp_host=$(echo "$config" | jq -r '.smtp_host // empty')
redirect_urls=$(echo "$config" | jq -r '.additional_redirect_urls | length')
magic_link_subject=$(echo "$config" | jq -r '.mailer_subjects_magic_link // empty')
otp_subject=$(echo "$config" | jq -r '.mailer_subjects_reauthentication // empty')

errors=0

if [ -z "$site_url" ]; then
  echo "  ❌ site_url not set"
  ((errors++))
else
  echo "  ✅ site_url: $site_url"
fi

if [ -z "$smtp_host" ]; then
  echo "  ❌ smtp_host not set"
  ((errors++))
else
  echo "  ✅ smtp_host: $smtp_host"
fi

if [ "$redirect_urls" -eq 0 ]; then
  echo "  ❌ additional_redirect_urls empty"
  ((errors++))
else
  echo "  ✅ additional_redirect_urls: $redirect_urls URLs"
fi

if [ -z "$magic_link_subject" ]; then
  echo "  ❌ Magic Link template not set"
  ((errors++))
else
  echo "  ✅ Magic Link template: $magic_link_subject"
fi

if [ -z "$otp_subject" ]; then
  echo "  ❌ Email OTP template not set"
  ((errors++))
else
  echo "  ✅ Email OTP template: $otp_subject"
fi

if [ $errors -eq 0 ]; then
  echo ""
  echo "✅ All auth configuration verified successfully"
  exit 0
else
  echo ""
  echo "❌ $errors configuration error(s) found"
  exit 1
fi
