#!/bin/bash
# SaaS Landing Page - Vercel Deployment Script

set -e

echo "🚀 Deploying SaaS Landing Page to Vercel..."
echo ""

# Check if vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    echo "❌ Vercel CLI not found. Installing..."
    npm install -g vercel
fi

# Check if we're in the right directory
if [ ! -f "package.json" ]; then
    echo "❌ Error: Must run from templates/saas-landing directory"
    exit 1
fi

# Environment variables reminder
echo "📋 Required Environment Variables:"
echo "   NEXT_PUBLIC_ODOO_URL=https://erp.insightpulseai.com"
echo "   NEXT_PUBLIC_ODOO_DB=odoo"
echo "   NEXT_PUBLIC_PLATFORM_NAME=InsightPulse.ai"
echo ""

# Prompt for deployment type
echo "Select deployment option:"
echo "1) New project (first time deployment)"
echo "2) Update existing project"
echo ""
read -p "Enter choice [1-2]: " choice

case $choice in
    1)
        echo ""
        echo "🆕 Creating new Vercel project..."
        echo ""
        echo "You'll be prompted to:"
        echo "  1. Select your team/account"
        echo "  2. Link to a Git repository (optional)"
        echo "  3. Configure project settings"
        echo ""
        read -p "Press Enter to continue..."

        # Deploy with prompts
        vercel --prod

        echo ""
        echo "✅ Deployment complete!"
        echo ""
        echo "⚠️  Don't forget to add environment variables in Vercel Dashboard:"
        echo "   https://vercel.com/dashboard"
        ;;

    2)
        echo ""
        echo "🔄 Updating existing project..."

        # Check if project is linked
        if [ ! -d ".vercel" ]; then
            echo "⚠️  Project not linked. Linking now..."
            vercel link
        fi

        # Deploy
        vercel --prod

        echo ""
        echo "✅ Deployment complete!"
        ;;

    *)
        echo "❌ Invalid choice"
        exit 1
        ;;
esac

echo ""
echo "📚 Next steps:"
echo "   1. Configure environment variables (if not done)"
echo "   2. Visit your deployment URL"
echo "   3. Test dashboard at /dashboard"
echo "   4. Verify Odoo API connection"
