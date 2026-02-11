#!/usr/bin/env bash
set -euo pipefail

# ============================================
# Production Deployment Script
# ============================================
# This script handles the complete deployment workflow:
# 1. Vercel environment variables
# 2. Production deployment
# 3. End-to-end verification

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$PROJECT_ROOT"

# ============================================
# Configuration
# ============================================

SUPABASE_URL="https://spdtwktxdalcfigzeqrz.supabase.co"
SUPABASE_ANON_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNwZHR3a3R4ZGFsY2ZpZ3plcXJ6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjA2NDQwMzUsImV4cCI6MjA3NjIyMDAzNX0.IHBJ0cNTMKJvRozljqaEqWph_gC0zlW2Td5Xl_GENs4"
ZOHO_USER="business@insightpulseai.com"
ZOHO_FROM_NAME="InsightPulse.ai"
APP_URL="https://ops.insightpulseai.com"

# These must be set as environment variables (never commit!)
: "${SUPABASE_SERVICE_ROLE_KEY:?Error: SUPABASE_SERVICE_ROLE_KEY not set}"
: "${ZOHO_PASS:?Error: ZOHO_PASS not set}"

echo "============================================"
echo "Vercel Production Deployment"
echo "============================================"
echo ""

# ============================================
# Step 1: Set Vercel Environment Variables
# ============================================

echo "Step 1: Setting Vercel environment variables..."

vercel env add NEXT_PUBLIC_SUPABASE_URL production <<<"$SUPABASE_URL" || echo "Already exists"
vercel env add NEXT_PUBLIC_SUPABASE_ANON_KEY production <<<"$SUPABASE_ANON_KEY" || echo "Already exists"
vercel env add SUPABASE_SERVICE_ROLE_KEY production <<<"$SUPABASE_SERVICE_ROLE_KEY" || echo "Already exists"
vercel env add ZOHO_USER production <<<"$ZOHO_USER" || echo "Already exists"
vercel env add ZOHO_PASS production <<<"$ZOHO_PASS" || echo "Already exists"
vercel env add ZOHO_FROM_NAME production <<<"$ZOHO_FROM_NAME" || echo "Already exists"
vercel env add NEXT_PUBLIC_APP_URL production <<<"$APP_URL" || echo "Already exists"

echo "✓ Environment variables configured"
echo ""

# ============================================
# Step 2: List Current Environment Variables
# ============================================

echo "Step 2: Verifying environment variables..."
vercel env ls production
echo ""

# ============================================
# Step 3: Deploy to Production
# ============================================

echo "Step 3: Deploying to production..."
vercel --prod
echo ""

# ============================================
# Step 4: Run Verification
# ============================================

echo "Step 4: Running end-to-end verification..."
if [[ -x "$SCRIPT_DIR/verify-org-invites.sh" ]]; then
  "$SCRIPT_DIR/verify-org-invites.sh"
else
  echo "⚠ Verification script not found or not executable"
fi

echo ""
echo "============================================"
echo "Deployment Complete!"
echo "============================================"
echo ""
echo "Next steps:"
echo "1. Visit $APP_URL to verify deployment"
echo "2. Test invite flow end-to-end"
echo "3. Monitor logs: vercel logs --follow"
