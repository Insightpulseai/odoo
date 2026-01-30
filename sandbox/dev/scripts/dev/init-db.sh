#!/usr/bin/env bash
set -euo pipefail

# ═══════════════════════════════════════════════════════════════════════════════
# Odoo Dev Sandbox - Database Initialization Script
# ═══════════════════════════════════════════════════════════════════════════════
#
# Purpose: Non-interactive database initialization for Odoo 18 CE
# Usage: ./scripts/dev/init-db.sh [--with-demo]
#
# Environment Variables Required:
#   - ODOO_DB_NAME
#   - ODOO_ADMIN_PASSWORD
#   - POSTGRES_USER
#   - POSTGRES_PASSWORD
#
# ═══════════════════════════════════════════════════════════════════════════════

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Load environment variables
if [ -f "$PROJECT_ROOT/.env" ]; then
    set -a
    source "$PROJECT_ROOT/.env"
    set +a
else
    echo "❌ Error: .env file not found at $PROJECT_ROOT/.env"
    exit 1
fi

# Parse arguments
WITH_DEMO="all"
if [ "${1:-}" = "--with-demo" ]; then
    WITH_DEMO="all"
else
    WITH_DEMO="False"
fi

# Configuration
CONTAINER_NAME="odoo-dev"
DB_HOST="db"
DB_NAME="${ODOO_DB_NAME:-odoo_dev}"
ADMIN_PASSWORD="${ODOO_ADMIN_PASSWORD:-admin}"
ADMIN_EMAIL="${ODOO_ADMIN_EMAIL:-admin@insightpulseai.net}"

echo "════════════════════════════════════════════════════════════════"
echo "Odoo Dev Sandbox - Database Initialization"
echo "════════════════════════════════════════════════════════════════"
echo
echo "Configuration:"
echo "  Database Name: $DB_NAME"
echo "  Admin Email: $ADMIN_EMAIL"
echo "  Demo Data: $WITH_DEMO"
echo "  Container: $CONTAINER_NAME"
echo

# Check if container is running
if ! docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    echo "❌ Error: Container $CONTAINER_NAME is not running"
    echo "   Run: ./scripts/dev/up.sh"
    exit 1
fi

# Check if database already exists
DB_EXISTS=$(docker exec odoo-dev-db psql -U "$POSTGRES_USER" -d postgres -tAc "SELECT 1 FROM pg_database WHERE datname='$DB_NAME'")

if [ "$DB_EXISTS" = "1" ]; then
    echo "⚠️  Warning: Database '$DB_NAME' already exists"
    echo
    read -p "Do you want to DROP and recreate it? (yes/no): " confirm
    if [ "$confirm" != "yes" ]; then
        echo "❌ Aborted. Database not modified."
        exit 1
    fi

    echo "🗑️  Dropping existing database '$DB_NAME'..."
    docker exec odoo-dev-db psql -U "$POSTGRES_USER" -d postgres -c "DROP DATABASE $DB_NAME" || true
fi

# Create database
echo "📦 Creating database '$DB_NAME'..."
docker exec odoo-dev-db psql -U "$POSTGRES_USER" -d postgres -c "CREATE DATABASE $DB_NAME OWNER $POSTGRES_USER"

echo
echo "🚀 Initializing Odoo with base modules..."
echo "   This may take 3-5 minutes..."
echo

# Initialize Odoo database
if [ "$WITH_DEMO" = "all" ]; then
    DEMO_FLAG="--load-demo=all"
else
    DEMO_FLAG="--without-demo=all"
fi

# Odoo 18 CE doesn't support --admin-password flag
# Admin password is set to 'admin' by default on fresh database
docker exec "$CONTAINER_NAME" odoo \
    --db_host="$DB_HOST" \
    --db_user="$POSTGRES_USER" \
    --db_password="$POSTGRES_PASSWORD" \
    --database="$DB_NAME" \
    --init=base,web,mail,contacts \
    $DEMO_FLAG \
    --stop-after-init

if [ $? -eq 0 ]; then
    echo
    echo "════════════════════════════════════════════════════════════════"
    echo "✅ Database initialization complete!"
    echo "════════════════════════════════════════════════════════════════"
    echo
    echo "Access your Odoo instance:"
    echo "  URL: http://localhost:${ODOO_PORT:-8069}"
    echo "  Database: $DB_NAME"
    echo "  Username: admin"
    echo "  Password: $ADMIN_PASSWORD"
    echo
    echo "Next steps:"
    echo "  1. Login at http://localhost:${ODOO_PORT:-8069}/web/login"
    echo "  2. Install custom modules from Apps menu"
    echo "  3. Configure settings as needed"
    echo
else
    echo
    echo "════════════════════════════════════════════════════════════════"
    echo "❌ Database initialization failed!"
    echo "════════════════════════════════════════════════════════════════"
    echo
    echo "Troubleshooting:"
    echo "  1. Check container logs: ./scripts/dev/logs.sh odoo"
    echo "  2. Verify PostgreSQL: ./scripts/dev/health.sh"
    echo "  3. Check .env configuration"
    echo
    exit 1
fi
