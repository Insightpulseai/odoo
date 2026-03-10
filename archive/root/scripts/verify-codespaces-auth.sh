#!/bin/bash
# Comprehensive authentication verification for Codespaces
# Run this inside a Codespace to verify all authentication is working

set -e

echo "🔍 Codespaces Authentication Verification"
echo "========================================="
echo ""

# Color codes for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

ERRORS=0

# Test 1: Check CODESPACES_PAT environment variable
echo "Test 1: CODESPACES_PAT environment variable"
if [ -n "$CODESPACES_PAT" ]; then
    echo -e "${GREEN}✅ CODESPACES_PAT is set${NC}"
    echo "   Value: ${CODESPACES_PAT:0:15}... (${#CODESPACES_PAT} chars)"
else
    echo -e "${RED}❌ CODESPACES_PAT not found${NC}"
    echo "   Set at: https://github.com/jgtolentino/odoo-ce/settings/secrets/codespaces"
    ERRORS=$((ERRORS + 1))
fi
echo ""

# Test 2: GitHub CLI authentication
echo "Test 2: GitHub CLI authentication"
if gh auth status &>/dev/null; then
    echo -e "${GREEN}✅ gh CLI authenticated${NC}"
    gh auth status 2>&1 | grep -E "Logged in|Token|protocol" | sed 's/^/   /'
else
    echo -e "${YELLOW}⚠️  gh CLI not authenticated${NC}"
    if [ -n "$CODESPACES_PAT" ]; then
        echo "   Attempting authentication with CODESPACES_PAT..."
        if echo "$CODESPACES_PAT" | gh auth login --with-token; then
            echo -e "${GREEN}✅ Authentication successful${NC}"
        else
            echo -e "${RED}❌ Authentication failed${NC}"
            ERRORS=$((ERRORS + 1))
        fi
    else
        echo "   Run: echo \$CODESPACES_PAT | gh auth login --with-token"
        ERRORS=$((ERRORS + 1))
    fi
fi
echo ""

# Test 3: Git configuration
echo "Test 3: Git configuration"
if git config --global user.name &>/dev/null && git config --global user.email &>/dev/null; then
    echo -e "${GREEN}✅ Git configured${NC}"
    echo "   Name: $(git config --global user.name)"
    echo "   Email: $(git config --global user.email)"
else
    echo -e "${YELLOW}⚠️  Git not fully configured${NC}"
    echo "   Run:"
    echo "   git config --global user.name \"Your Name\""
    echo "   git config --global user.email \"your.email@example.com\""
fi
echo ""

# Test 4: Codespaces secrets access
echo "Test 4: Codespaces secrets management"
if gh secret list --repo jgtolentino/odoo-ce --app codespaces &>/dev/null; then
    echo -e "${GREEN}✅ Can access Codespaces secrets${NC}"
    SECRET_COUNT=$(gh secret list --repo jgtolentino/odoo-ce --app codespaces 2>/dev/null | wc -l)
    echo "   Secrets found: $SECRET_COUNT"
else
    echo -e "${RED}❌ Cannot access Codespaces secrets${NC}"
    echo "   Token may be missing 'codespace' scope"
    ERRORS=$((ERRORS + 1))
fi
echo ""

# Test 5: Repository access
echo "Test 5: Repository access"
if gh repo view jgtolentino/odoo-ce --json name &>/dev/null; then
    echo -e "${GREEN}✅ Can access repository${NC}"
    REPO_INFO=$(gh repo view jgtolentino/odoo-ce --json name,owner,isPrivate 2>/dev/null)
    echo "   $REPO_INFO" | jq -r '. | "   Name: \(.name)\n   Owner: \(.owner.login)\n   Private: \(.isPrivate)"'
else
    echo -e "${RED}❌ Cannot access repository${NC}"
    echo "   Check token has 'repo' scope"
    ERRORS=$((ERRORS + 1))
fi
echo ""

# Test 6: Supabase environment variables
echo "Test 6: Supabase environment variables"
SUPABASE_VARS=("POSTGRES_URL" "NEXT_PUBLIC_SUPABASE_ANON_KEY" "SUPABASE_SERVICE_ROLE_KEY")
MISSING_VARS=()

for var in "${SUPABASE_VARS[@]}"; do
    if [ -n "${!var}" ]; then
        echo -e "${GREEN}✅ $var is set${NC}"
    else
        echo -e "${RED}❌ $var not found${NC}"
        MISSING_VARS+=("$var")
    fi
done

if [ ${#MISSING_VARS[@]} -gt 0 ]; then
    echo ""
    echo "Missing Supabase variables:"
    for var in "${MISSING_VARS[@]}"; do
        echo "   - $var"
    done
    echo "   Set at: https://github.com/jgtolentino/odoo-ce/settings/secrets/codespaces"
    ERRORS=$((ERRORS + 1))
fi
echo ""

# Test 7: Supabase connection
echo "Test 7: Supabase database connection"
if [ -n "$POSTGRES_URL" ]; then
    if psql "$POSTGRES_URL" -c "SELECT version();" &>/dev/null; then
        echo -e "${GREEN}✅ Supabase connection successful${NC}"
        VERSION=$(psql "$POSTGRES_URL" -t -c "SELECT version();" 2>/dev/null | head -1 | xargs)
        echo "   $VERSION"
    else
        echo -e "${RED}❌ Supabase connection failed${NC}"
        echo "   Check POSTGRES_URL is correct"
        ERRORS=$((ERRORS + 1))
    fi
else
    echo -e "${YELLOW}⚠️  POSTGRES_URL not set - skipping test${NC}"
fi
echo ""

# Test 8: Supabase API
echo "Test 8: Supabase API access"
if [ -n "$NEXT_PUBLIC_SUPABASE_ANON_KEY" ]; then
    if curl -sf -H "apikey: $NEXT_PUBLIC_SUPABASE_ANON_KEY" \
         "https://spdtwktxdalcfigzeqrz.supabase.co/rest/v1/" &>/dev/null; then
        echo -e "${GREEN}✅ Supabase API accessible${NC}"
    else
        echo -e "${RED}❌ Supabase API connection failed${NC}"
        echo "   Check NEXT_PUBLIC_SUPABASE_ANON_KEY is correct"
        ERRORS=$((ERRORS + 1))
    fi
else
    echo -e "${YELLOW}⚠️  NEXT_PUBLIC_SUPABASE_ANON_KEY not set - skipping test${NC}"
fi
echo ""

# Summary
echo "========================================="
if [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}✅ All tests passed!${NC}"
    echo ""
    echo "Your Codespace is fully configured and ready to use."
else
    echo -e "${RED}❌ $ERRORS test(s) failed${NC}"
    echo ""
    echo "Review the errors above and:"
    echo "  1. Check Codespaces secrets: https://github.com/jgtolentino/odoo-ce/settings/secrets/codespaces"
    echo "  2. Verify GitHub PAT scopes: https://github.com/settings/tokens"
    echo "  3. Rebuild Codespace if secrets were just added"
    echo ""
    echo "Documentation: docs/GITHUB_PAT_CODESPACES.md"
    exit 1
fi
