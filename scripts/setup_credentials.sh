#!/bin/bash
# =============================================================================
# One-Time Credentials Setup
# =============================================================================
# Run this ONCE to set up your credentials. They'll be stored in .env.local
# (gitignored) and auto-loaded by all scripts.
#
# Usage:
#   ./scripts/setup_credentials.sh
#
# After setup, you'll NEVER be asked for credentials again.
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
ENV_FILE="$REPO_ROOT/.env.local"

echo ""
echo "============================================="
echo "  IPAI Credentials Setup (One-Time)"
echo "============================================="
echo ""
echo "This will create .env.local with your credentials."
echo "You only need to do this ONCE."
echo ""

# Check if .env.local already exists
if [ -f "$ENV_FILE" ]; then
    echo "Found existing .env.local"
    read -p "Overwrite? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Keeping existing credentials."
        exit 0
    fi
fi

# Supabase Project Info
echo ""
echo "=== Supabase Credentials ==="
echo "Get these from: https://supabase.com/dashboard/project/spdtwktxdalcfigzeqrz/settings/api"
echo ""

read -p "SUPABASE_ANON_KEY: " SUPABASE_ANON_KEY
read -p "SUPABASE_SERVICE_ROLE_KEY: " SUPABASE_SERVICE_ROLE_KEY

echo ""
echo "Get database URL from: https://supabase.com/dashboard/project/spdtwktxdalcfigzeqrz/settings/database"
echo "(Use 'Connection string' → 'URI' with your password)"
echo ""

read -p "POSTGRES_URL (pooled, port 6543): " POSTGRES_URL
read -p "POSTGRES_URL_NON_POOLING (direct, port 5432): " POSTGRES_URL_NON_POOLING

# SSH for deployment
echo ""
echo "=== Deployment Credentials (Optional) ==="
echo "Press Enter to skip if not deploying."
echo ""

read -p "SSH_HOST (e.g., 178.128.112.214): " SSH_HOST
read -p "SSH_USER (e.g., root): " SSH_USER

# Write .env.local
cat > "$ENV_FILE" << EOF
# =============================================================================
# IPAI Local Credentials (GITIGNORED - DO NOT COMMIT)
# =============================================================================
# Generated: $(date -u '+%Y-%m-%d %H:%M:%S UTC')
# =============================================================================

# ----- Supabase -----
SUPABASE_PROJECT_REF=spdtwktxdalcfigzeqrz
SUPABASE_URL=https://spdtwktxdalcfigzeqrz.supabase.co
SUPABASE_ANON_KEY=${SUPABASE_ANON_KEY}
SUPABASE_SERVICE_ROLE_KEY=${SUPABASE_SERVICE_ROLE_KEY}

# ----- PostgreSQL -----
POSTGRES_URL=${POSTGRES_URL}
POSTGRES_URL_NON_POOLING=${POSTGRES_URL_NON_POOLING}

# ----- Deployment -----
SSH_HOST=${SSH_HOST:-}
SSH_USER=${SSH_USER:-root}

# ----- Odoo -----
ODOO_URL=https://erp.insightpulseai.net
ODOO_DB=production

# =============================================================================
# Add any additional secrets below
# =============================================================================
EOF

chmod 600 "$ENV_FILE"

echo ""
echo "============================================="
echo "  Setup Complete!"
echo "============================================="
echo ""
echo "Credentials saved to: $ENV_FILE"
echo ""
echo "All scripts will now auto-load these credentials."
echo "You won't be asked again."
echo ""
echo "Test with:"
echo "  ./scripts/verify_supabase_full.sh"
echo ""

# Verify .gitignore includes .env.local
if ! grep -q "^\.env\.local$" "$REPO_ROOT/.gitignore" 2>/dev/null; then
    echo ".env.local" >> "$REPO_ROOT/.gitignore"
    echo "Added .env.local to .gitignore"
fi
