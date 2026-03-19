#!/usr/bin/env bash
set -euo pipefail

# ============================================================================
# Vercel Token Provisioning Script
# ============================================================================
# Purpose: Persist VERCEL_TOKEN to local env file and GitHub Actions secrets
# Prerequisites: Token manually created at https://vercel.com/account/tokens
# ============================================================================

: "${VERCEL_TOKEN:?Set VERCEL_TOKEN environment variable first}"

ENV_FILE="${ENV_FILE:-.env.platform.local}"
KEY="VERCEL_TOKEN"
VAL="${VERCEL_TOKEN}"

echo "[1/3] Persist to local env file: ${ENV_FILE}"

# Create file if doesn't exist
touch "$ENV_FILE"

# Replace if exists, append if doesn't
if grep -q "^${KEY}=" "$ENV_FILE"; then
  echo "  → Updating existing ${KEY} entry"
  perl -0777 -i -pe "s/^${KEY}=.*$/${KEY}=${VAL}/m" "$ENV_FILE"
else
  echo "  → Appending new ${KEY} entry"
  printf "\n%s=%s\n" "$KEY" "$VAL" >> "$ENV_FILE"
fi

echo "[2/3] Verify local persistence"
if grep -q "^${KEY}=" "$ENV_FILE"; then
  echo "  ✅ ${KEY} present in ${ENV_FILE}"
  # Show prefix only (security)
  grep "^${KEY}=" "$ENV_FILE" | sed "s/=${VAL}/=REDACTED/"
else
  echo "  ❌ Failed to persist ${KEY}"
  exit 1
fi

echo "[3/3] Push to GitHub Actions secrets"
# Requires gh CLI authenticated
if command -v gh &>/dev/null; then
  gh secret set VERCEL_TOKEN -R Insightpulseai/odoo --body "$VERCEL_TOKEN"
  echo "  ✅ VERCEL_TOKEN set in GitHub Actions"
else
  echo "  ⚠️  gh CLI not found, skipping GitHub Actions secret"
  echo "  → Install: https://cli.github.com"
  echo "  → Manual: Settings → Secrets → Actions → New secret"
fi

echo ""
echo "✅ Token provisioning complete"
echo ""
echo "Next steps:"
echo "  1. Run: ./scripts/vercel/fix_root_directory.sh"
echo "  2. Trigger deploy: git commit --allow-empty -m 'chore: trigger deploy'"
echo "  3. Check logs: ./scripts/vercel/latest_deploy_logs.sh"
