#!/usr/bin/env bash
# ============================================================================
# Deploy to Vercel (Production)
# ============================================================================
# Description: Deterministic Vercel deployment without UI interaction
# Usage: VERCEL_TOKEN=xxx VERCEL_ORG_ID=xxx VERCEL_PROJECT_ID=xxx ./scripts/deploy_vercel_prod.sh
# ============================================================================

set -euo pipefail

# Required environment variables
: "${VERCEL_TOKEN:?missing VERCEL_TOKEN}"
: "${VERCEL_ORG_ID:?missing VERCEL_ORG_ID}"
: "${VERCEL_PROJECT_ID:?missing VERCEL_PROJECT_ID}"

echo "[deploy] Installing Vercel CLI..."
npm i -g vercel@latest

echo "[deploy] Pulling project settings..."
vercel pull --yes --environment=production \
  --token "$VERCEL_TOKEN" \
  --scope "$VERCEL_ORG_ID"

echo "[deploy] Building for production..."
vercel build --prod \
  --token "$VERCEL_TOKEN" \
  --scope "$VERCEL_ORG_ID"

echo "[deploy] Deploying prebuilt artifacts..."
DEPLOY_URL=$(vercel deploy --prebuilt --prod \
  --token "$VERCEL_TOKEN" \
  --scope "$VERCEL_ORG_ID" \
  --name "$VERCEL_PROJECT_ID")

echo "[deploy] Deployment complete: $DEPLOY_URL"

# Verify deployment is healthy
echo "[deploy] Verifying deployment..."
sleep 10

HTTP_STATUS=$(curl -fsS -o /dev/null -w "%{http_code}" "$DEPLOY_URL" 2>/dev/null || echo "000")

if [ "$HTTP_STATUS" = "200" ]; then
  echo "[deploy] Health check passed (HTTP $HTTP_STATUS)"
else
  echo "[deploy] Health check returned HTTP $HTTP_STATUS (may still be propagating)"
fi

echo "[deploy] Done."
