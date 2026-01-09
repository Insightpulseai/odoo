#!/usr/bin/env bash
# =============================================================================
# DevContainer Post-Create Script
# =============================================================================
# Runs after the container is created to set up the development environment
# =============================================================================
set -e

echo "=== Setting up Odoo CE + IPAI development environment ==="

# Install system dependencies
echo "Installing system dependencies..."
sudo apt-get update
sudo apt-get install -y --no-install-recommends \
  jq \
  postgresql-client \
  libpq-dev \
  libxml2-dev \
  libxslt1-dev \
  libldap2-dev \
  libsasl2-dev \
  libssl-dev \
  libjpeg-dev \
  zlib1g-dev

# Install Python dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Install Node.js dependencies
echo "Installing Node.js dependencies..."
corepack enable
pnpm install

# Hydrate OCA repos
echo "Hydrating OCA repositories..."
if [[ -f "scripts/oca_hydrate.sh" ]]; then
  bash scripts/oca_hydrate.sh --tier 4
fi

# Create local config if not exists
if [[ ! -f "config/odoo.conf.local" ]]; then
  echo "Creating local Odoo config..."
  cat > config/odoo.conf.local << 'EOF'
[options]
db_host = localhost
db_port = 5432
db_user = odoo
db_password = odoo
addons_path = /workspaces/odoo-ce/addons/ipai,/workspaces/odoo-ce/addons/oca/server-tools,/workspaces/odoo-ce/addons/oca/server-ux,/workspaces/odoo-ce/addons/oca/web,/workspaces/odoo-ce/addons/oca/queue,/workspaces/odoo-ce/addons/oca/reporting-engine,/workspaces/odoo-ce/addons/oca/mis-builder
http_port = 8069
EOF
fi

echo ""
echo "=== Setup complete! ==="
echo ""
echo "Quick start:"
echo "  1. Start PostgreSQL: docker compose up -d postgres"
echo "  2. Run Odoo: odoo -c config/odoo.conf.local"
echo "  3. Or use Docker: docker compose up -d odoo-core"
echo ""
