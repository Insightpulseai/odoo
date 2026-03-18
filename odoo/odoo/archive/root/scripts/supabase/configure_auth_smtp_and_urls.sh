#!/usr/bin/env bash
set -euo pipefail

# ========================================
# Configure Supabase Auth SMTP and URLs
# ========================================
# Sets up custom SMTP (Zoho Mail) and redirect URLs
# Uses Management API for programmatic configuration

echo "📧 Configuring Supabase Auth SMTP and URLs..."

# Verify prerequisites
: "${SUPABASE_PROJECT_REF:?Error: SUPABASE_PROJECT_REF not set}"
: "${SUPABASE_ACCESS_TOKEN:?Error: SUPABASE_ACCESS_TOKEN not set}"

# Use existing Zoho variables from .env.platform.local
export SMTP_HOST="${SMTP_HOST:-${ZOHO_SMTP_HOST:-}}"
export SMTP_PORT="${SMTP_PORT:-${ZOHO_SMTP_PORT:-587}}"
export SMTP_USER="${SMTP_USER:-${ZOHO_SMTP_USER:-}}"
export SMTP_PASS="${SMTP_PASS:-${ZOHO_SMTP_PASS:-}}"
export SMTP_FROM="${SMTP_FROM:-${MAIL_DEFAULT_FROM:-no-reply@insightpulseai.com}}"
export SMTP_SENDER_NAME="${SMTP_SENDER_NAME:-InsightPulseAI}"

# Derive AUTH_SITE_URL from AUTH_JWT_ISSUER if not set
export AUTH_SITE_URL="${AUTH_SITE_URL:-${AUTH_JWT_ISSUER:-https://auth.insightpulseai.com}}"

# Default redirect URLs for common services
export AUTH_ADDITIONAL_REDIRECT_URLS="${AUTH_ADDITIONAL_REDIRECT_URLS:-https://erp.insightpulseai.com,https://n8n.insightpulseai.com,https://superset.insightpulseai.com,http://localhost:3000,http://localhost:8069}"

# Verify required variables
: "${SMTP_HOST:?Error: SMTP_HOST or ZOHO_SMTP_HOST not set}"
: "${SMTP_USER:?Error: SMTP_USER or ZOHO_SMTP_USER not set}"
: "${SMTP_PASS:?Error: SMTP_PASS or ZOHO_SMTP_PASS not set}"

# Construct payload with SMTP + URLs (single Python block)
payload="$(python3 - <<'PY'
import os, json

# Parse redirect URLs
redirect_urls_str = os.environ.get("AUTH_ADDITIONAL_REDIRECT_URLS", "")
redirect_urls = [u.strip() for u in redirect_urls_str.split(",") if u.strip()]

# Build configuration payload
config = {
  "site_url": os.environ["AUTH_SITE_URL"],
  "additional_redirect_urls": redirect_urls,
  "external_email_enabled": True,
  "mailer_autoconfirm": False,
  "mailer_secure_email_change_enabled": True,
  "smtp_admin_email": os.environ["SMTP_FROM"],
  "smtp_sender_name": os.environ["SMTP_SENDER_NAME"],
  "smtp_host": os.environ["SMTP_HOST"],
  "smtp_port": str(os.environ["SMTP_PORT"]),  # API expects string
  "smtp_user": os.environ["SMTP_USER"],
  "smtp_pass": os.environ["SMTP_PASS"],
}

print(json.dumps(config))
PY
)"

# PATCH via Management API
echo "→ Applying configuration via Management API..."
echo "→ Payload preview (first 200 chars): $(echo "$payload" | cut -c1-200)..."

response=$(curl -w "\nHTTP_CODE:%{http_code}" -X PATCH "https://api.supabase.com/v1/projects/${SUPABASE_PROJECT_REF}/config/auth" \
  -H "Authorization: Bearer ${SUPABASE_ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d "$payload" 2>&1)

http_code=$(echo "$response" | grep "HTTP_CODE:" | cut -d: -f2)
body=$(echo "$response" | grep -v "HTTP_CODE:")

if [ "$http_code" != "200" ]; then
  echo "❌ API request failed with HTTP $http_code"
  echo "Response: $body"
  exit 1
fi

echo "✅ Auth SMTP and URLs configured successfully"
echo ""
echo "Configuration applied:"
echo "  Site URL: $AUTH_SITE_URL"
echo "  Redirect URLs: $(echo "$AUTH_ADDITIONAL_REDIRECT_URLS" | tr ',' '\n' | sed 's/^/    /')"
echo "  SMTP Host: $SMTP_HOST"
echo "  SMTP User: $SMTP_USER"
