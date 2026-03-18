#!/usr/bin/env bash
set -euo pipefail

# ============================================
# Secure Production Deployment Script
# ============================================
# Loads secrets from ~/.zshrc and deploys to Vercel
# NEVER prints secret values

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$PROJECT_ROOT"

# Load master secrets from .zshrc (SSOT)
if [[ -f "$HOME/.zshrc" ]]; then
  # shellcheck disable=SC1090
  source "$HOME/.zshrc"
fi

# Validate required secrets are set
: "${SUPABASE_URL:?missing SUPABASE_URL in ~/.zshrc}"
: "${SUPABASE_ANON_KEY:?missing SUPABASE_ANON_KEY in ~/.zshrc}"
: "${SUPABASE_SERVICE_ROLE_KEY:?missing SUPABASE_SERVICE_ROLE_KEY in ~/.zshrc}"
: "${ZOHO_SMTP_PASSWORD:?missing ZOHO_SMTP_PASSWORD in ~/.zshrc}"

APP_URL="${NEXT_PUBLIC_APP_URL:-https://ops.insightpulseai.com}"

echo "============================================"
echo "Vercel Production Deployment"
echo "============================================"
echo ""
echo "▶ Validating secrets loaded from ~/.zshrc..."
echo "  ✅ SUPABASE_URL (${#SUPABASE_URL} chars)"
echo "  ✅ SUPABASE_ANON_KEY (${#SUPABASE_ANON_KEY} chars)"
echo "  ✅ SUPABASE_SERVICE_ROLE_KEY (${#SUPABASE_SERVICE_ROLE_KEY} chars)"
echo "  ✅ ZOHO_SMTP_PASSWORD (${#ZOHO_SMTP_PASSWORD} chars)"
echo ""

# Helper: set env var non-interactively (replace if exists)
set_env () {
  local key="$1"
  local value="$2"

  # Remove existing key if present (vercel env add doesn't overwrite cleanly)
  vercel env rm "$key" production >/dev/null 2>&1 || true
  printf '%s' "$value" | vercel env add "$key" production >/dev/null 2>&1
  echo "  ✅ $key"
}

echo "▶ Setting Vercel environment variables (production)..."
set_env NEXT_PUBLIC_SUPABASE_URL "$SUPABASE_URL"
set_env NEXT_PUBLIC_SUPABASE_ANON_KEY "$SUPABASE_ANON_KEY"
set_env SUPABASE_SERVICE_ROLE_KEY "$SUPABASE_SERVICE_ROLE_KEY"
set_env ZOHO_USER "business@insightpulseai.com"
set_env ZOHO_PASS "$ZOHO_SMTP_PASSWORD"
set_env ZOHO_FROM_NAME "InsightPulse.ai"
set_env NEXT_PUBLIC_APP_URL "$APP_URL"
echo ""

echo "▶ Deploying to Vercel (production)..."
vercel --prod
echo ""

echo "============================================"
echo "Deployment Complete!"
echo "============================================"
echo ""
echo "▶ Smoke tests:"
echo ""
echo "export BASE_URL=\"$APP_URL\""
echo "curl -sS -I \"\$BASE_URL/\" | head -20"
echo "curl -sS -I \"\$BASE_URL/api/invite/list\" | head -20"
echo "curl -sS -I \"\$BASE_URL/api/invite/send\" | head -20"
echo "curl -sS -I \"\$BASE_URL/api/invite/accept\" | head -20"
echo ""
echo "▶ Full verification:"
echo "./scripts/verify-org-invites.sh"
