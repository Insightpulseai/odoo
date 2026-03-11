#!/bin/bash
# Interactive GitHub PAT setup for Codespaces
# Validates token and sets as Codespaces secret

set -e

REPO="jgtolentino/odoo-ce"
SECRET_NAME="CODESPACES_PAT"

echo "🔐 GitHub PAT Setup for Codespaces"
echo "=================================="
echo ""
echo "This script will:"
echo "  1. Validate your GitHub PAT has required scopes"
echo "  2. Test authentication"
echo "  3. Set as Codespaces secret: $SECRET_NAME"
echo ""

# Check if gh is authenticated
if ! gh auth status &>/dev/null; then
    echo "❌ GitHub CLI not authenticated"
    echo ""
    echo "Run: gh auth login"
    echo "Or set GITHUB_TOKEN environment variable"
    exit 1
fi

# Prompt for PAT
echo "📝 Enter your GitHub Personal Access Token:"
echo "   (Generate at: https://github.com/settings/tokens?type=beta)"
echo ""
read -sp "Token: " PAT_VALUE
echo ""
echo ""

if [ -z "$PAT_VALUE" ]; then
    echo "❌ Token cannot be empty"
    exit 1
fi

# Validate token format
if [[ ! $PAT_VALUE =~ ^(ghp_|github_pat_) ]]; then
    echo "⚠️  Warning: Token doesn't match expected format"
    echo "   Expected: ghp_... (classic) or github_pat_... (fine-grained)"
    echo ""
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Test authentication with token
echo "🔍 Validating token..."
if ! curl -sf -H "Authorization: Bearer $PAT_VALUE" \
     https://api.github.com/user > /dev/null; then
    echo "❌ Token validation failed"
    echo "   Token may be invalid or expired"
    exit 1
fi

# Get token scopes
SCOPES=$(curl -sf -H "Authorization: Bearer $PAT_VALUE" \
         -I https://api.github.com/user \
         | grep -i "x-oauth-scopes:" \
         | cut -d: -f2 \
         | tr -d ' \r\n')

echo "✅ Token valid"
echo "   Scopes: $SCOPES"
echo ""

# Check for required scopes
REQUIRED_SCOPES=("repo" "codespace")
MISSING_SCOPES=()

for scope in "${REQUIRED_SCOPES[@]}"; do
    if [[ ! $SCOPES =~ $scope ]]; then
        MISSING_SCOPES+=("$scope")
    fi
done

if [ ${#MISSING_SCOPES[@]} -gt 0 ]; then
    echo "⚠️  Warning: Missing recommended scopes:"
    for scope in "${MISSING_SCOPES[@]}"; do
        echo "   - $scope"
    done
    echo ""
    echo "Token will work but some features may be limited"
    echo ""
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "ℹ️  Update token scopes at: https://github.com/settings/tokens"
        exit 1
    fi
fi

# Set as Codespaces secret
echo "📦 Setting Codespaces secret: $SECRET_NAME"
if echo "$PAT_VALUE" | gh secret set "$SECRET_NAME" \
   --repo "$REPO" \
   --app codespaces; then
    echo "✅ Secret set successfully"
else
    echo "❌ Failed to set secret"
    echo ""
    echo "Common issues:"
    echo "  1. Current GitHub CLI token missing 'codespace:secrets' permission"
    echo "  2. No access to repository: $REPO"
    echo ""
    echo "To fix:"
    echo "  1. Go to: https://github.com/settings/tokens"
    echo "  2. Find your token (used by gh CLI)"
    echo "  3. Add 'codespace' scope with 'codespace:secrets' sub-scope"
    echo "  4. Regenerate and update GITHUB_TOKEN in ~/.zshrc"
    exit 1
fi

# Verify secret was set
echo ""
echo "🔍 Verifying secret..."
if gh secret list --repo "$REPO" --app codespaces | grep -q "$SECRET_NAME"; then
    echo "✅ Secret verified in repository"
else
    echo "⚠️  Secret not found in list (may take a moment to propagate)"
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "  1. Open a new Codespace for: $REPO"
echo "  2. Verify with: printenv CODESPACES_PAT"
echo "  3. Test gh CLI: gh auth status"
echo ""
echo "Documentation: docs/GITHUB_PAT_CODESPACES.md"
