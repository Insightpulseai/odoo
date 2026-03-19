#!/usr/bin/env bash
set -euo pipefail

# ============================================
# Vercel First-Time Deployment
# ============================================
# Creates Vercel project and gets deployment URL for DNS setup

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$PROJECT_ROOT"

echo "============================================"
echo "Vercel First-Time Deployment"
echo "============================================"
echo ""
echo "This will:"
echo "1. Create a new Vercel project"
echo "2. Deploy to a preview URL"
echo "3. Give you the deployment URL for Cloudflare DNS"
echo ""

# Unset placeholder Vercel env vars that interfere with CLI
unset VERCEL_PROJECT_ID
unset VERCEL_ORG_ID
unset VERCEL_TOKEN

# Clear any existing .vercel directory
rm -rf .vercel

echo "▶ Deploying to Vercel..."
echo ""

# Deploy without --yes to allow interactive project creation
vercel

echo ""
echo "============================================"
echo "Next Steps: Cloudflare DNS Configuration"
echo "============================================"
echo ""
echo "1. Copy the deployment URL above (looks like: saas-landing-xxx.vercel.app)"
echo ""
echo "2. Add Cloudflare DNS record:"
echo "   - Go to: https://dash.cloudflare.com/"
echo "   - Select: insightpulseai.com"
echo "   - DNS → Add record"
echo "   - Type: CNAME"
echo "   - Name: ops"
echo "   - Target: [paste-vercel-url-here]"
echo "   - Proxy: ON (orange cloud)"
echo "   - Save"
echo ""
echo "3. Add custom domain in Vercel:"
echo "   - Go to: Vercel dashboard → Your project → Settings → Domains"
echo "   - Add: ops.insightpulseai.com"
echo ""
echo "4. Wait for DNS propagation (1-5 minutes)"
echo ""
echo "5. Deploy to production:"
echo "   source ~/.zshrc && ./scripts/deploy-production.sh"
