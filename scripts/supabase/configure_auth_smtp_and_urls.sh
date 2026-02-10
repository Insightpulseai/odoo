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
: "${AUTH_SITE_URL:?Error: AUTH_SITE_URL not set}"
: "${AUTH_ADDITIONAL_REDIRECT_URLS:?Error: AUTH_ADDITIONAL_REDIRECT_URLS not set}"
: "${SMTP_FROM:?Error: SMTP_FROM not set}"
: "${SMTP_SENDER_NAME:?Error: SMTP_SENDER_NAME not set}"
: "${SMTP_HOST:?Error: SMTP_HOST not set}"
: "${SMTP_PORT:?Error: SMTP_PORT not set}"
: "${SMTP_USER:?Error: SMTP_USER not set}"
: "${SMTP_PASS:?Error: SMTP_PASS not set}"

# Transform comma-separated redirect URLs to JSON array
redirects_json="$(python3 - <<'PY'
import os, json
urls = [u.strip() for u in os.environ["AUTH_ADDITIONAL_REDIRECT_URLS"].split(",") if u.strip()]
print(json.dumps(urls))
PY
)"

# Construct payload with SMTP + URLs
payload="$(python3 - <<PY
import os, json
print(json.dumps({
  "site_url": os.environ["AUTH_SITE_URL"],
  "additional_redirect_urls": json.loads(os.environ["redirects_json"]),
  "external_email_enabled": True,
  "mailer_autoconfirm": False,
  "mailer_secure_email_change_enabled": True,
  "smtp_admin_email": os.environ["SMTP_FROM"],
  "smtp_sender_name": os.environ["SMTP_SENDER_NAME"],
  "smtp_host": os.environ["SMTP_HOST"],
  "smtp_port": int(os.environ["SMTP_PORT"]),
  "smtp_user": os.environ["SMTP_USER"],
  "smtp_pass": os.environ["SMTP_PASS"],
}))
PY
)"

# PATCH via Management API
echo "→ Applying configuration via Management API..."
response=$(curl -fsS -X PATCH "https://api.supabase.com/v1/projects/${SUPABASE_PROJECT_REF}/config/auth" \
  -H "Authorization: Bearer ${SUPABASE_ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d "$payload")

echo "✅ Auth SMTP and URLs configured successfully"
echo ""
echo "Configuration applied:"
echo "  Site URL: $AUTH_SITE_URL"
echo "  Redirect URLs: $(echo $redirects_json | jq -r 'join(", ")')"
echo "  SMTP Host: $SMTP_HOST"
echo "  SMTP User: $SMTP_USER"
