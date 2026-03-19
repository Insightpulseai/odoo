#!/bin/bash
# Start local Odoo development environment

set -e

echo "==========================================="
echo "Starting Local Odoo Development"
echo "==========================================="
echo ""

# Check if Docker is running
echo "1. Checking Docker..."
if ! docker ps &> /dev/null; then
    echo "⚠️  Docker is not running. Starting Docker Desktop..."
    open -a Docker
    echo "⏳ Waiting for Docker to start (30 seconds)..."
    sleep 30

    # Check again
    if ! docker ps &> /dev/null; then
        echo "❌ Docker failed to start. Please start Docker Desktop manually."
        exit 1
    fi
fi
echo "✅ Docker is running"
echo ""

# Start Odoo services
echo "2. Starting Odoo services..."
cd /Users/tbwa/odoo-ce

if [ -f "docker-compose.dev.yml" ]; then
    echo "Using docker-compose.dev.yml"
    docker compose -f docker-compose.dev.yml up -d postgres odoo-core
else
    echo "❌ docker-compose.dev.yml not found"
    exit 1
fi
echo ""

# Wait for services to be ready
echo "3. Waiting for Odoo to start..."
sleep 10

# Check if services are running
POSTGRES_STATUS=$(docker compose -f docker-compose.dev.yml ps postgres | grep -c "Up" || echo "0")
ODOO_STATUS=$(docker compose -f docker-compose.dev.yml ps odoo-core | grep -c "Up" || echo "0")

if [ "$POSTGRES_STATUS" -gt "0" ]; then
    echo "✅ PostgreSQL is running"
else
    echo "❌ PostgreSQL failed to start"
fi

if [ "$ODOO_STATUS" -gt "0" ]; then
    echo "✅ Odoo is running"
else
    echo "❌ Odoo failed to start"
    echo ""
    echo "Checking logs..."
    docker compose -f docker-compose.dev.yml logs --tail 50 odoo-core
    exit 1
fi
echo ""

# Show access information
echo "==========================================="
echo "Local Odoo is Ready!"
echo "==========================================="
echo ""
echo "🌐 URL: http://localhost:8069"
echo "📧 Default Username: admin"
echo "🔑 Default Password: admin"
echo ""
echo "To view logs:"
echo "  docker compose -f docker-compose.dev.yml logs -f odoo-core"
echo ""
echo "To stop:"
echo "  docker compose -f docker-compose.dev.yml down"
echo ""
echo "Opening browser..."
sleep 3
open http://localhost:8069/web/login
