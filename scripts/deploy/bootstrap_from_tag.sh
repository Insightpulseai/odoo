#!/usr/bin/env bash
set -euo pipefail

# IPAI AIUX Ship v1.1.0 Bootstrap Script
# Canonical fresh deployment from git tag to new DigitalOcean droplet
# Run this script on a fresh Ubuntu 22.04+ droplet
#
# PARAMETERIZED: No hardcoded service names, DB names, or paths
# All values can be overridden via environment variables

# ============================================================================
# Configuration (All parameterized - no hardcoded assumptions)
# ============================================================================

REPO="${REPO:-https://github.com/jgtolentino/odoo-ce.git}"
APP_DIR="${APP_DIR:-/opt/odoo-ce}"
GIT_REF="${GIT_REF:-ship-aiux-v1.1.0}"
COMPOSE_FILE="${COMPOSE_FILE:-deploy/docker-compose.prod.yml}"
ODOO_SERVICE="${ODOO_SERVICE:-odoo}"
DB_SERVICE="${DB_SERVICE:-db}"
ODOO_DB="${ODOO_DB:-odoo}"
SHIP_MODULES="${SHIP_MODULES:-ipai_theme_aiux,ipai_aiux_chat,ipai_ask_ai,ipai_document_ai,ipai_expense_ocr}"

echo "============================================================================"
echo "IPAI AIUX Ship v1.1.0 Bootstrap"
echo "============================================================================"
echo "Repository: $REPO"
echo "Git Ref: $GIT_REF"
echo "Install Dir: $APP_DIR"
echo "Compose File: $COMPOSE_FILE"
echo "Odoo Service: $ODOO_SERVICE"
echo "DB Service: $DB_SERVICE"
echo "Database: $ODOO_DB"
echo "Modules: $SHIP_MODULES"
echo "============================================================================"
echo "NOTE: All values above are parameterized - no hardcoded assumptions"
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

echo "==> Step 2: Cloning repository at $GIT_REF..."
sudo mkdir -p "$APP_DIR"
sudo chown -R "$USER":"$USER" "$APP_DIR"
cd "$APP_DIR"

if [ -d ".git" ]; then
  echo "Repository already cloned. Fetching $GIT_REF..."
  git fetch origin
  git checkout "$GIT_REF"
else
  git clone "$REPO" .
  git checkout "$GIT_REF"
fi

echo "✅ Repository cloned at $GIT_REF"
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
docker compose -f "$COMPOSE_FILE" pull

echo "✅ Docker images pulled"
echo

# ============================================================================
# Step 5: Start Services
# ============================================================================

echo "==> Step 5: Starting services..."
docker compose -f "$COMPOSE_FILE" up -d

echo "Waiting for health checks (Odoo needs 120s start_period)..."
echo "Waiting 30 seconds for DB..."
sleep 30

echo "Checking DB health..."
docker compose -f "$COMPOSE_FILE" exec -T "$DB_SERVICE" \
  psql -U postgres -d postgres -c 'SELECT 1' || echo "⚠️  DB not ready yet"

echo "Waiting 90 more seconds for Odoo initialization..."
sleep 90

docker compose -f "$COMPOSE_FILE" ps

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
echo "Database: $ODOO_DB"
echo "Modules: $SHIP_MODULES"

docker compose -f "$COMPOSE_FILE" exec -T "$ODOO_SERVICE" \
  odoo -d "$ODOO_DB" -i "$SHIP_MODULES" --stop-after-init

echo "✅ Modules installed"
echo

# ============================================================================
# Step 8: Rebuild Web Assets (Prevent 500 errors)
# ============================================================================

echo "==> Step 8: Rebuilding web assets..."
echo "Running: odoo -d $ODOO_DB -u web,$SHIP_MODULES --stop-after-init"

docker compose -f "$COMPOSE_FILE" exec -T "$ODOO_SERVICE" \
  odoo -d "$ODOO_DB" -u "web,$SHIP_MODULES" --stop-after-init

echo "✅ Web assets rebuilt"
echo

# ============================================================================
# Step 9: Restart Odoo
# ============================================================================

echo "==> Step 9: Restarting Odoo service..."
docker compose -f "$COMPOSE_FILE" restart "$ODOO_SERVICE"

echo "Waiting 120 seconds for Odoo health check start_period..."
sleep 120

echo "✅ Odoo restarted"
echo

# ============================================================================
# Step 10: Final Verification
# ============================================================================

echo "==> Step 10: Running final verification..."
if [ -f "./scripts/deploy/verify_prod.sh" ]; then
  COMPOSE_FILE="$COMPOSE_FILE" ODOO_SERVICE="$ODOO_SERVICE" DB_SERVICE="$DB_SERVICE" \
    ./scripts/deploy/verify_prod.sh
else
  echo "⚠️  Verification script not found"
fi

echo
echo "==> Checking recent logs..."
docker compose -f "$COMPOSE_FILE" logs --tail=200 "$ODOO_SERVICE"

echo
echo "==> Health check verification..."
echo "DB Health:"
docker compose -f "$COMPOSE_FILE" exec -T "$DB_SERVICE" \
  psql -U postgres -d postgres -c 'SELECT 1' || echo "❌ DB health check failed"

echo
echo "Odoo Health:"
docker compose -f "$COMPOSE_FILE" exec -T "$ODOO_SERVICE" \
  curl -fsS http://localhost:8069/web/health || echo "❌ Odoo health check failed"

echo
echo "============================================================================"
echo "AIUX Ship v1.1.0 Bootstrap Complete!"
echo "============================================================================"
echo "Git Ref: $GIT_REF"
echo "Compose File: $COMPOSE_FILE"
echo "Odoo Service: $ODOO_SERVICE"
echo "Database: $ODOO_DB"
echo "Installed modules: $SHIP_MODULES"
echo
echo "Access Odoo at: http://$(hostname -I | awk '{print $1}'):8069"
echo
echo "Next steps:"
echo "1. Configure domain/DNS for production access"
echo "2. Review deploy/.env for production secrets"
echo "3. Configure nginx reverse proxy (see deploy/nginx/)"
echo "4. Run AIUX verification:"
echo "   ODOO_DB=$ODOO_DB ./scripts/aiux/verify_install.sh"
echo "5. Run asset verification:"
echo "   ODOO_DB=$ODOO_DB ./scripts/aiux/verify_assets.sh"
echo
echo "============================================================================"
echo "PARAMETERIZED DEPLOYMENT - All service/DB names resolved from environment"
echo "To customize: Set COMPOSE_FILE, ODOO_SERVICE, DB_SERVICE, ODOO_DB before running"
echo "============================================================================"
