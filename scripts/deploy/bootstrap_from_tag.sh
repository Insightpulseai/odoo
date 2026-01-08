#!/usr/bin/env bash
set -euo pipefail

# IPAI AIUX Ship v1.1.0 Bootstrap Script
# Canonical fresh deployment from git tag to new DigitalOcean droplet
# Run this script on a fresh Ubuntu 22.04+ droplet

# ============================================================================
# Configuration
# ============================================================================

REPO="${REPO:-https://github.com/jgtolentino/odoo-ce.git}"
APP_DIR="${APP_DIR:-/opt/odoo-ce}"
TAG="${TAG:-ship-aiux-v1.1.0}"
COMPOSE="${COMPOSE:-deploy/docker-compose.prod.yml}"
DB="${DB:-odoo}"
MODULES="${MODULES:-ipai_theme_aiux,ipai_aiux_chat,ipai_ask_ai,ipai_document_ai,ipai_expense_ocr}"

echo "============================================================================"
echo "IPAI AIUX Ship v1.1.0 Bootstrap"
echo "============================================================================"
echo "Repository: $REPO"
echo "Tag: $TAG"
echo "Install Dir: $APP_DIR"
echo "Compose File: $COMPOSE"
echo "Database: $DB"
echo "Modules: $MODULES"
echo "============================================================================"
echo

# ============================================================================
# Step 1: System Dependencies
# ============================================================================

echo "==> Step 1: Installing system dependencies..."
sudo apt-get update -y
sudo apt-get install -y git curl ca-certificates gnupg lsb-release

# Install Docker
echo "==> Installing Docker..."
if ! command -v docker &> /dev/null; then
  curl -fsSL https://get.docker.com | sudo sh
  sudo usermod -aG docker "$USER"
  echo "Docker installed. You may need to log out and back in for group changes."
else
  echo "Docker already installed."
fi

# Verify Docker Compose V2
if ! docker compose version &> /dev/null; then
  echo "ERROR: Docker Compose V2 not found. Please install Docker Compose V2."
  exit 1
fi

echo "✅ System dependencies installed"
echo

# ============================================================================
# Step 2: Clone Repository at Tag
# ============================================================================

echo "==> Step 2: Cloning repository at tag $TAG..."
sudo mkdir -p "$APP_DIR"
sudo chown -R "$USER":"$USER" "$APP_DIR"
cd "$APP_DIR"

if [ -d ".git" ]; then
  echo "Repository already cloned. Fetching tag $TAG..."
  git fetch origin
  git checkout "$TAG"
else
  git clone "$REPO" .
  git checkout "$TAG"
fi

echo "✅ Repository cloned at tag $TAG"
echo

# ============================================================================
# Step 3: Environment Configuration
# ============================================================================

echo "==> Step 3: Configuring environment..."

if [ ! -f "deploy/.env" ]; then
  echo "Creating deploy/.env from example..."
  if [ -f "deploy/.env.example" ]; then
    cp deploy/.env.example deploy/.env
    echo "⚠️  WARNING: Please configure deploy/.env with production values!"
  else
    echo "ERROR: deploy/.env.example not found. Cannot create environment file."
    exit 1
  fi
else
  echo "deploy/.env already exists."
fi

echo "✅ Environment configured (review deploy/.env for production values)"
echo

# ============================================================================
# Step 4: Pull Docker Images
# ============================================================================

echo "==> Step 4: Pulling Docker images..."
docker compose -f "$COMPOSE" pull

echo "✅ Docker images pulled"
echo

# ============================================================================
# Step 5: Start Services
# ============================================================================

echo "==> Step 5: Starting services..."
docker compose -f "$COMPOSE" up -d

echo "Waiting 30 seconds for services to initialize..."
sleep 30

docker compose -f "$COMPOSE" ps

echo "✅ Services started"
echo

# ============================================================================
# Step 6: Initial Verification
# ============================================================================

echo "==> Step 6: Running initial verification..."
if [ -f "./scripts/deploy/verify_prod.sh" ]; then
  ./scripts/deploy/verify_prod.sh || echo "⚠️  Verification warnings detected"
else
  echo "⚠️  Verification script not found, skipping..."
fi

echo

# ============================================================================
# Step 7: Install AIUX Modules
# ============================================================================

echo "==> Step 7: Installing AIUX modules..."
echo "Modules: $MODULES"

docker compose -f "$COMPOSE" exec -T odoo \
  odoo -d "$DB" -i "$MODULES" --stop-after-init

echo "✅ Modules installed"
echo

# ============================================================================
# Step 8: Rebuild Web Assets (Prevent 500 errors)
# ============================================================================

echo "==> Step 8: Rebuilding web assets..."
docker compose -f "$COMPOSE" exec -T odoo \
  odoo -d "$DB" -u web,ipai_theme_aiux,ipai_aiux_chat --stop-after-init

echo "✅ Web assets rebuilt"
echo

# ============================================================================
# Step 9: Restart Odoo
# ============================================================================

echo "==> Step 9: Restarting Odoo..."
docker compose -f "$COMPOSE" restart odoo-ce

echo "Waiting 20 seconds for Odoo to restart..."
sleep 20

echo "✅ Odoo restarted"
echo

# ============================================================================
# Step 10: Final Verification
# ============================================================================

echo "==> Step 10: Running final verification..."
if [ -f "./scripts/deploy/verify_prod.sh" ]; then
  ./scripts/deploy/verify_prod.sh
else
  echo "⚠️  Verification script not found"
fi

echo
echo "==> Checking recent logs..."
docker compose -f "$COMPOSE" logs --tail=200 odoo-ce

echo
echo "============================================================================"
echo "AIUX Ship v1.1.0 Bootstrap Complete!"
echo "============================================================================"
echo "Access Odoo at: http://$(hostname -I | awk '{print $1}'):8069"
echo "Default database: $DB"
echo "Installed modules: $MODULES"
echo
echo "Next steps:"
echo "1. Configure domain/DNS for production access"
echo "2. Review deploy/.env for production secrets"
echo "3. Configure nginx reverse proxy (see deploy/nginx/)"
echo "4. Run AIUX verification: ./scripts/aiux/verify_install.sh"
echo "5. Run asset verification: ./scripts/aiux/verify_assets.sh"
echo "============================================================================"
