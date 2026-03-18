#!/usr/bin/env bash
# ============================================================================
# Rollback to Previous Vercel Deployment
# ============================================================================
# Description: Promotes the previous production deployment as the current one
# Usage: VERCEL_TOKEN=xxx VERCEL_ORG_ID=xxx ./scripts/vercel_promote_previous.sh
# ============================================================================

set -euo pipefail

# Required environment variables
: "${VERCEL_TOKEN:?missing VERCEL_TOKEN}"
: "${VERCEL_ORG_ID:?missing VERCEL_ORG_ID}"

echo "[rollback] Fetching deployment list..."

# Get the last two production deployments
DEPLOYMENTS=$(vercel ls --token "$VERCEL_TOKEN" --scope "$VERCEL_ORG_ID" --prod 2>/dev/null | tail -n +2 | head -3)

if [ -z "$DEPLOYMENTS" ]; then
  echo "[rollback] ERROR: No deployments found"
  exit 1
fi

echo "[rollback] Recent deployments:"
echo "$DEPLOYMENTS"

# Get the second deployment (previous production)
PREVIOUS_URL=$(echo "$DEPLOYMENTS" | sed -n '2p' | awk '{print $2}')

if [ -z "$PREVIOUS_URL" ]; then
  echo "[rollback] ERROR: No previous deployment found"
  exit 1
fi

echo "[rollback] Promoting previous deployment: $PREVIOUS_URL"

# Promote to production
vercel promote "$PREVIOUS_URL" \
  --token "$VERCEL_TOKEN" \
  --scope "$VERCEL_ORG_ID" \
  --yes

echo "[rollback] Rollback complete. Current production: $PREVIOUS_URL"
