#!/bin/bash
# Start local Odoo development environment

set -e

echo "==========================================="
echo "Starting Local Odoo Development"
echo "==========================================="
echo ""

# Set Docker environment for Colima
COLIMA_PROFILE="odoo"
if [ -S "$HOME/.colima/${COLIMA_PROFILE}/docker.sock" ]; then
    export DOCKER_HOST="unix://$HOME/.colima/${COLIMA_PROFILE}/docker.sock"
    echo "🔧 Using Colima Docker socket: $DOCKER_HOST"
    echo ""
fi

# Check if Docker daemon is running
echo "1. Checking Docker daemon..."
if ! docker ps &> /dev/null; then
    echo "⚠️  Docker daemon is not running"
    echo "💡 Start with: make colima-up"
    echo ""
    echo "Attempting to start Colima automatically..."

    # Try to start Colima
    if command -v colima &> /dev/null; then
        ./scripts/colima-up.sh || {
            echo "❌ Failed to start Colima. Please run: make colima-up"
            exit 1
        }
    else
        echo "❌ Colima not installed. Install with: brew install colima docker docker-compose"
        exit 1
    fi
fi
echo "✅ Docker daemon is running"
echo ""

# Start Odoo services
echo "2. Starting Odoo services..."

# Use canonical docker-compose.yml from repo root
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

echo "Using docker-compose.yml (ipai workspace)"
docker compose up -d
echo ""

# Wait for services to be ready
echo "3. Waiting for services to start..."
sleep 10

# Check service status
echo "📊 Service status:"
docker compose ps
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
