#!/usr/bin/env bash
set -euo pipefail

# ========================================
# Apply GitHub Actions Secrets
# ========================================
# Pushes secrets from .env.platform.local to GitHub Actions
# Usage: ./gh_actions_secrets_apply.sh [REPO] [ENV_FILE]

REPO="${1:-Insightpulseai/odoo}"
ENV_FILE="${2:-.env.platform.local}"

echo "📦 Applying GitHub Actions Secrets to $REPO"
echo "===================================================="
echo ""

if [[ -f "$ENV_FILE" ]]; then
  echo "→ Loading secrets from: $ENV_FILE"
  set -a
  source "$ENV_FILE"
  set +a
fi

# Required secrets for CI/CD workflow
required=(
  SUPABASE_PROJECT_REF
  SUPABASE_ACCESS_TOKEN

  OPENAI_API_KEY
  ANTHROPIC_API_KEY

  AUTH_JWT_ISSUER
)

# Optional secrets (derive from env or use defaults)
optional_mapping=(
  "SMTP_FROM:MAIL_DEFAULT_FROM:no-reply@insightpulseai.com"
  "SMTP_HOST:ZOHO_SMTP_HOST:smtppro.zoho.com"
  "SMTP_PORT:ZOHO_SMTP_PORT:587"
  "SMTP_USER:ZOHO_SMTP_USER:business@insightpulseai.com"
  "SMTP_PASS:ZOHO_SMTP_PASS:"
  "AUTH_SITE_URL:AUTH_JWT_ISSUER:https://auth.insightpulseai.com"
)

# Default redirect URLs
AUTH_ADDITIONAL_REDIRECT_URLS="${AUTH_ADDITIONAL_REDIRECT_URLS:-https://erp.insightpulseai.com,https://n8n.insightpulseai.com,https://superset.insightpulseai.com,http://localhost:3000,http://localhost:8069}"

echo "→ Validating required secrets..."
missing=0
for k in "${required[@]}"; do
  if [[ -z "${!k:-}" ]]; then
    echo "  ❌ Missing: $k"
    missing=1
  else
    echo "  ✓ Found: $k"
  fi
done

if [[ "$missing" -eq 1 ]]; then
  echo ""
  echo "❌ Missing required secrets. Cannot proceed."
  exit 1
fi

echo ""
echo "→ Deriving optional secrets..."
for mapping in "${optional_mapping[@]}"; do
  IFS=':' read -r target source default <<< "$mapping"

  # Use target if set, else source, else default
  value="${!target:-${!source:-$default}}"

  if [[ -n "$value" ]]; then
    export "$target=$value"
    echo "  ✓ $target (from ${!target:+target}${!source:+source}${default:+default})"
  else
    echo "  ⚠ $target not set (no source or default available)"
  fi
done

echo ""
echo "→ Pushing secrets to GitHub Actions..."

# Push required secrets
for k in "${required[@]}"; do
  gh secret set "$k" -R "$REPO" --body "${!k}" >/dev/null 2>&1
  echo "  ✓ $k"
done

# Push derived optional secrets
for mapping in "${optional_mapping[@]}"; do
  IFS=':' read -r target _ _ <<< "$mapping"
  if [[ -n "${!target:-}" ]]; then
    gh secret set "$target" -R "$REPO" --body "${!target}" >/dev/null 2>&1
    echo "  ✓ $target"
  fi
done

# Push redirect URLs
gh secret set AUTH_ADDITIONAL_REDIRECT_URLS -R "$REPO" --body "$AUTH_ADDITIONAL_REDIRECT_URLS" >/dev/null 2>&1
echo "  ✓ AUTH_ADDITIONAL_REDIRECT_URLS"

echo ""
echo "✅ GitHub Actions secrets applied successfully!"
echo ""
echo "Total secrets: $((${#required[@]} + $(echo "${optional_mapping[@]}" | wc -w) + 1))"
echo "Repository: $REPO"
