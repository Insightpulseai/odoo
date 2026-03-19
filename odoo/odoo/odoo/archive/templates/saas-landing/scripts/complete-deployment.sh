#!/usr/bin/env bash
#
# complete-deployment.sh - Complete SaaS Landing Template Deployment
#
# Prerequisites:
# 1. Database migration applied via Supabase SQL Editor
# 2. Environment variables set in ~/.zshrc:
#    - SUPABASE_ANON_KEY
#    - SUPABASE_SERVICE_ROLE_KEY
#    - ZOHO_PASS
#

set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_DIR"

echo "🚀 SaaS Landing Template - Complete Deployment"
echo "=============================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check prerequisites
echo "📋 Checking prerequisites..."

if [ -z "${SUPABASE_ANON_KEY:-}" ]; then
  echo -e "${RED}❌ SUPABASE_ANON_KEY not set${NC}"
  echo "   Get from: https://supabase.com/dashboard/project/spdtwktxdalcfigzeqrz/settings/api"
  exit 1
fi

if [ -z "${SUPABASE_SERVICE_ROLE_KEY:-}" ]; then
  echo -e "${RED}❌ SUPABASE_SERVICE_ROLE_KEY not set${NC}"
  echo "   Get from: https://supabase.com/dashboard/project/spdtwktxdalcfigzeqrz/settings/api"
  exit 1
fi

if [ -z "${ZOHO_PASS:-}" ]; then
  echo -e "${RED}❌ ZOHO_PASS not set${NC}"
  echo "   Get from: ~/.zshrc"
  exit 1
fi

echo -e "${GREEN}✅ All environment variables present${NC}"
echo ""

# Step 1: Verify migration applied
echo "1️⃣  Verifying database migration..."
echo "   ⚠️  Manual step required:"
echo "   Go to: https://supabase.com/dashboard/project/spdtwktxdalcfigzeqrz/sql/new"
echo "   Copy/paste: supabase/migrations/20260212_org_invites.sql"
echo "   Execute, then press ENTER to continue..."
read -r

# Step 2: Create/Link Vercel project
echo ""
echo "2️⃣  Creating/Linking Vercel project..."
if [ ! -f ".vercel/project.json" ]; then
  echo "   Running: vercel --prod"
  vercel --prod
else
  echo -e "${GREEN}✅ Project already linked${NC}"
fi

# Get project name
PROJECT_NAME=$(jq -r '.name' .vercel/project.json 2>/dev/null || echo "unknown")
echo "   Project: $PROJECT_NAME"
echo ""

# Step 3: Set environment variables
echo "3️⃣  Setting environment variables..."

ENV_VARS=(
  "NEXT_PUBLIC_SUPABASE_URL=https://spdtwktxdalcfigzeqrz.supabase.co"
  "NEXT_PUBLIC_SUPABASE_ANON_KEY=$SUPABASE_ANON_KEY"
  "SUPABASE_SERVICE_ROLE_KEY=$SUPABASE_SERVICE_ROLE_KEY"
  "ZOHO_USER=business@insightpulseai.com"
  "ZOHO_PASS=$ZOHO_PASS"
  "ZOHO_FROM_NAME=InsightPulse.ai"
  "NEXT_PUBLIC_APP_URL=https://ops.insightpulseai.com"
)

for ENV_VAR in "${ENV_VARS[@]}"; do
  KEY="${ENV_VAR%%=*}"
  VALUE="${ENV_VAR#*=}"

  # Check if already exists
  if vercel env ls production 2>&1 | grep -q "^$KEY"; then
    echo "   ⏭️  $KEY (already set)"
  else
    echo "   ➕ Setting $KEY..."
    echo "$VALUE" | vercel env add "$KEY" production --yes 2>&1 | tail -1
  fi
done

echo -e "${GREEN}✅ Environment variables configured${NC}"
echo ""

# Step 4: Deploy to production
echo "4️⃣  Deploying to production..."
echo "   Running: vercel --prod"
DEPLOY_URL=$(vercel --prod 2>&1 | grep -E "https://.*\.vercel\.app" | head -1 | awk '{print $NF}')

if [ -n "$DEPLOY_URL" ]; then
  echo -e "${GREEN}✅ Deployed to: $DEPLOY_URL${NC}"
else
  echo -e "${YELLOW}⚠️  Deployment initiated - check Vercel dashboard${NC}"
fi
echo ""

# Step 5: Verify deployment
echo "5️⃣  Verifying deployment..."
echo "   Waiting 10 seconds for build to complete..."
sleep 10

BASE_URL="${DEPLOY_URL:-https://ops.insightpulseai.com}"

echo "   Testing API endpoints..."
for ENDPOINT in "/api/org/create" "/api/invite/send" "/api/invite/accept"; do
  HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL$ENDPOINT" || echo "000")
  if [ "$HTTP_STATUS" -ge 200 ] && [ "$HTTP_STATUS" -lt 500 ]; then
    echo -e "   ${GREEN}✅ $ENDPOINT ($HTTP_STATUS)${NC}"
  else
    echo -e "   ${RED}❌ $ENDPOINT ($HTTP_STATUS)${NC}"
  fi
done

echo ""
echo "6️⃣  Running automated verification..."
if [ -x "./scripts/verify-org-invites.sh" ]; then
  ./scripts/verify-org-invites.sh
else
  echo -e "${YELLOW}⚠️  Verification script not executable${NC}"
  echo "   Run: chmod +x ./scripts/verify-org-invites.sh && ./scripts/verify-org-invites.sh"
fi

echo ""
echo "=============================================="
echo -e "${GREEN}🎉 Deployment Complete!${NC}"
echo ""
echo "📝 Next Steps:"
echo "   1. Configure custom domain: ops.insightpulseai.com"
echo "   2. Add CNAME: ops.insightpulseai.com → cname.vercel-dns.com"
echo "   3. Test E2E flow: /org/new → create → invite → accept"
echo ""
echo "📊 Deployment URLs:"
echo "   Preview: $DEPLOY_URL"
echo "   Production: https://ops.insightpulseai.com (after DNS)"
echo ""
echo "📁 Evidence:"
echo "   Deployment status: docs/evidence/20260212-1530/deployment-status.md"
echo "   Implementation: docs/IMPLEMENTATION_SUMMARY.md"
echo ""
