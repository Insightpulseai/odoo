#!/bin/bash
# Setup GitHub Codespaces secrets for odoo-ce repository
# Run this locally with proper GitHub PAT permissions

set -e

REPO="jgtolentino/odoo-ce"

echo "🔐 Setting up GitHub Codespaces secrets for $REPO"
echo ""
echo "⚠️  Note: Your GitHub PAT must have 'codespace' scope"
echo "    Go to: https://github.com/settings/tokens"
echo ""

# Check if gh is authenticated
if ! gh auth status &>/dev/null; then
    echo "❌ GitHub CLI not authenticated"
    echo "   Run: gh auth login"
    exit 1
fi

# Source secrets from .env.local if it exists
if [ -f .env.local ]; then
    echo "📄 Loading secrets from .env.local"
    set -a
    source .env.local
    set +a
else
    echo "❌ .env.local not found"
    echo "   Create .env.local with your actual values (copy from .env.example)"
    exit 1
fi

# Function to set secret
set_secret() {
    local name=$1
    local value=$2

    if [ -z "$value" ]; then
        echo "⏭️  Skipping $name (empty value)"
        return
    fi

    echo "✅ Setting $name"
    echo "$value" | gh secret set "$name" --repo "$REPO" --app codespaces || {
        echo "⚠️  Failed to set $name (check PAT permissions)"
    }
}

# Set all secrets
set_secret "NEXT_PUBLIC_SUPABASE_ANON_KEY" "$NEXT_PUBLIC_SUPABASE_ANON_KEY"
set_secret "POSTGRES_PASSWORD" "$POSTGRES_PASSWORD"
set_secret "POSTGRES_PRISMA_URL" "$POSTGRES_PRISMA_URL"
set_secret "POSTGRES_URL" "$POSTGRES_URL"
set_secret "POSTGRES_URL_NON_POOLING" "$POSTGRES_URL_NON_POOLING"
set_secret "SUPABASE_JWT_SECRET" "$SUPABASE_JWT_SECRET"
set_secret "SUPABASE_PUBLISHABLE_KEY" "$SUPABASE_PUBLISHABLE_KEY"
set_secret "SUPABASE_SECRET_KEY" "$SUPABASE_SECRET_KEY"
set_secret "SUPABASE_SERVICE_ROLE_KEY" "$SUPABASE_SERVICE_ROLE_KEY"
set_secret "VITE_SUPABASE_ANON_KEY" "$VITE_SUPABASE_ANON_KEY"
set_secret "VITE_SUPABASE_PUBLISHABLE_KEY" "$VITE_SUPABASE_PUBLISHABLE_KEY"

echo ""
echo "✅ Done! All secrets have been set for Codespaces"
echo "   Verify at: https://github.com/$REPO/settings/secrets/codespaces"
