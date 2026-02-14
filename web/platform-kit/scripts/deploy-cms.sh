#!/bin/bash
set -euo pipefail

# Deploy Supabase CMS
# Project: spdtwktxdalcfigzeqrz

echo "=== Deploying Supabase CMS ==="

# Check Supabase CLI
if ! command -v supabase &> /dev/null; then
    echo "❌ Supabase CLI not found. Install: npm i -g supabase"
    exit 1
fi

# Link to project
echo "1. Linking to Supabase project..."
supabase link --project-ref spdtwktxdalcfigzeqrz

# Run migrations
echo "2. Running database migrations..."
supabase db push

# Deploy Edge Function
echo "3. Deploying posts-api Edge Function..."
supabase functions deploy posts-api --no-verify-jwt

# Set environment variables for the function
echo "4. Setting function environment variables..."
supabase secrets set \
  SUPABASE_URL="https://spdtwktxdalcfigzeqrz.supabase.co" \
  SUPABASE_ANON_KEY="${SUPABASE_ANON_KEY}"

echo ""
echo "✅ CMS deployed successfully!"
echo ""
echo "API Endpoint: https://spdtwktxdalcfigzeqrz.supabase.co/functions/v1/posts-api"
echo ""
echo "Next steps:"
echo "1. Update .env with your service role key"
echo "2. Test the API: curl https://spdtwktxdalcfigzeqrz.supabase.co/functions/v1/posts-api"
echo "3. Create your first post via the API or Supabase dashboard"
