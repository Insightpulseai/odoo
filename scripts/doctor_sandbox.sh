#!/bin/bash
# doctor_sandbox.sh - Verify canonical sandbox environment health
# Checks cwd, docker compose files, ports, and provides next steps

set -euo pipefail

REPO_ROOT="$HOME/Documents/GitHub/odoo-ce"
CANONICAL_SANDBOX="$REPO_ROOT/sandbox/dev"
REQUIRED_PORTS=(8069 5432)

echo "=== Odoo CE Sandbox Health Check ==="
echo ""

# Check 1: Current working directory
echo "1. Checking current directory..."
if [ "$PWD" = "$CANONICAL_SANDBOX" ]; then
    echo "   ✅ Working directory is canonical sandbox: $PWD"
else
    echo "   ⚠️  Working directory: $PWD"
    echo "   Expected: $CANONICAL_SANDBOX"
    echo "   Fix: cd $CANONICAL_SANDBOX"
fi
echo ""

# Check 2: Docker Compose files exist
echo "2. Checking Docker Compose configuration..."
COMPOSE_FILES=(
    "$CANONICAL_SANDBOX/docker-compose.yml"
    "$CANONICAL_SANDBOX/config/odoo.conf"
)

all_files_exist=true
for file in "${COMPOSE_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "   ✅ Found: $(basename "$file")"
    else
        echo "   ❌ Missing: $file"
        all_files_exist=false
    fi
done
echo ""

# Check 3: Docker daemon status
echo "3. Checking Docker daemon..."
if docker info &>/dev/null; then
    echo "   ✅ Docker daemon is running"
else
    echo "   ❌ Docker daemon not running"
    echo "   Fix: colima start  # or open Docker Desktop"
    echo ""
    echo "=== Doctor Summary: BLOCKED (Docker not running) ==="
    exit 1
fi
echo ""

# Check 4: Port availability
echo "4. Checking required ports..."
for port in "${REQUIRED_PORTS[@]}"; do
    if lsof -Pi :$port -sTCP:LISTEN -t &>/dev/null; then
        echo "   ⚠️  Port $port is in use (stack may already be running)"
    else
        echo "   ✅ Port $port is available"
    fi
done
echo ""

# Check 5: Container status
echo "5. Checking container status..."
cd "$CANONICAL_SANDBOX"
if docker compose ps --services &>/dev/null; then
    RUNNING_COUNT=$(docker compose ps --services --filter "status=running" 2>/dev/null | wc -l | tr -d ' ')
    TOTAL_COUNT=$(docker compose ps --services 2>/dev/null | wc -l | tr -d ' ')

    if [ "$RUNNING_COUNT" -gt 0 ]; then
        echo "   ✅ Stack is running ($RUNNING_COUNT/$TOTAL_COUNT services)"
        echo ""
        echo "=== Current Stack Status ==="
        docker compose ps
        echo ""
        echo "=== Next Steps ==="
        echo "   View logs:    docker compose logs -f odoo"
        echo "   Restart:      docker compose restart odoo"
        echo "   Stop:         docker compose down"
        echo "   Odoo URL:     http://localhost:8069"
    else
        echo "   ⚠️  Stack is not running ($RUNNING_COUNT/$TOTAL_COUNT services)"
        echo ""
        echo "=== Next Steps: Start Stack ==="
        echo "   cd $CANONICAL_SANDBOX"
        echo "   docker compose up -d"
        echo "   docker compose logs -f odoo"
        echo ""
        echo "After startup, access Odoo at: http://localhost:8069"
    fi
else
    echo "   ℹ️  No running containers found"
    echo ""
    echo "=== Next Steps: First-Time Setup ==="
    echo "   cd $CANONICAL_SANDBOX"
    echo "   docker compose up -d"
    echo "   docker compose logs -f odoo"
    echo ""
    echo "After startup, access Odoo at: http://localhost:8069"
fi

echo ""
echo "=== Doctor Summary: $([ "$all_files_exist" = true ] && echo "HEALTHY" || echo "NEEDS ATTENTION") ==="
