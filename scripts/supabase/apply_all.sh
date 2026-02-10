#!/usr/bin/env bash
set -euo pipefail

# ========================================
# Master Orchestrator for Supabase Secrets
# ========================================
# Applies all configuration: Edge Secrets + Auth SMTP + Email Templates
# Usage: ./apply_all.sh [path_to_env_file]

echo "🚀 Supabase Secrets Migration - Master Orchestrator"
echo "===================================================="
echo ""

# Load env file if provided
if [ $# -gt 0 ]; then
  env_file="$1"
  if [ ! -f "$env_file" ]; then
    echo "❌ Error: File not found: $env_file"
    exit 1
  fi
  echo "→ Loading secrets from: $env_file"
  set -a
  source "$env_file"
  set +a
fi

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Step 1: Deploy Edge Secrets
echo "Step 1/4: Deploying Edge Secrets..."
"${SCRIPT_DIR}/set_edge_secrets.sh"
echo ""

# Step 2: Configure Auth SMTP and URLs
echo "Step 2/4: Configuring Auth SMTP and URLs..."
"${SCRIPT_DIR}/configure_auth_smtp_and_urls.sh"
echo ""

# Step 3: Configure Email Templates
echo "Step 3/4: Configuring Email Templates..."
"${SCRIPT_DIR}/configure_auth_email_templates.sh"
echo ""

# Step 4: Verify Configuration
echo "Step 4/4: Verifying Configuration..."
"${SCRIPT_DIR}/verify_auth_config.sh"
echo ""

echo "===================================================="
echo "✅ All configuration applied successfully!"
echo ""
echo "Next steps:"
echo "  1. Deploy secret-smoke function: supabase functions deploy secret-smoke"
echo "  2. Test Magic Link: node scripts/supabase/test_magic_link.js"
echo "  3. Test Email OTP: node scripts/supabase/test_email_otp.js"
echo "  4. Rotate compromised secrets (if needed)"
