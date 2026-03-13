#!/bin/bash
set -e

echo "🔍 Verifying Organization Invite Implementation..."
echo ""

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check files exist
echo "📁 Checking file structure..."

FILES=(
  "supabase/migrations/20260212_org_invites.sql"
  "lib/supabase/client.ts"
  "lib/supabase/server.ts"
  "lib/email/zoho.ts"
  "lib/auth/invite-token.ts"
  "app/api/org/create/route.ts"
  "app/api/invite/send/route.ts"
  "app/api/invite/accept/route.ts"
  "app/api/invite/list/route.ts"
  "app/api/invite/cancel/route.ts"
  "app/org/new/page.tsx"
  "app/org/[orgId]/page.tsx"
  "app/invite/accept/page.tsx"
  "docs/ORG_INVITES.md"
)

MISSING=0
for file in "${FILES[@]}"; do
  if [ -f "$file" ]; then
    echo -e "  ${GREEN}✓${NC} $file"
  else
    echo -e "  ${RED}✗${NC} $file (missing)"
    MISSING=$((MISSING + 1))
  fi
done

if [ $MISSING -gt 0 ]; then
  echo -e "${RED}✗ $MISSING files missing${NC}"
  exit 1
fi

echo ""

# Check dependencies
echo "📦 Checking dependencies..."

DEPS=(
  "@supabase/supabase-js"
  "nodemailer"
  "@radix-ui/react-label"
  "@radix-ui/react-select"
)

for dep in "${DEPS[@]}"; do
  if grep -q "\"$dep\"" package.json; then
    echo -e "  ${GREEN}✓${NC} $dep"
  else
    echo -e "  ${RED}✗${NC} $dep (not in package.json)"
  fi
done

echo ""

# Check environment variables
echo "🔐 Checking environment configuration..."

ENV_VARS=(
  "ZOHO_USER"
  "ZOHO_PASS"
  "ZOHO_FROM_NAME"
  "NEXT_PUBLIC_APP_URL"
)

if [ -f ".env.example" ]; then
  for var in "${ENV_VARS[@]}"; do
    if grep -q "^$var=" .env.example; then
      echo -e "  ${GREEN}✓${NC} $var in .env.example"
    else
      echo -e "  ${YELLOW}⚠${NC} $var not in .env.example"
    fi
  done
else
  echo -e "  ${RED}✗${NC} .env.example not found"
fi

echo ""

# Check build
echo "🏗️  Running build test..."
if pnpm build >/dev/null 2>&1; then
  echo -e "  ${GREEN}✓${NC} Build successful"
else
  echo -e "  ${RED}✗${NC} Build failed"
  exit 1
fi

echo ""

# Summary
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}✅ Verification Complete${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Next Steps:"
echo "1. Deploy database migration:"
echo "   supabase db push"
echo ""
echo "2. Configure environment variables (.env.local):"
echo "   cp .env.example .env.local"
echo "   # Edit with actual credentials"
echo ""
echo "3. Start dev server:"
echo "   pnpm dev"
echo ""
echo "4. Test invite flow:"
echo "   - Create org: http://localhost:3000/org/new"
echo "   - Send invite: http://localhost:3000/org/{orgId}"
echo "   - Accept invite: Check email for link"
echo ""
echo "Documentation: docs/ORG_INVITES.md"
