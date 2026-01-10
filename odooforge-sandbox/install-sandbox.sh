#!/bin/bash
# OdooForge Sandbox - One-Click Installation Script
# Handles Docker environment setup, container builds, and health verification

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo_step() {
    echo -e "${BLUE}==>${NC} $1"
}

echo_success() {
    echo -e "${GREEN}✓${NC} $1"
}

echo_error() {
    echo -e "${RED}✗${NC} $1"
}

echo_warning() {
    echo -e "${YELLOW}!${NC} $1"
}

# Header
echo ""
echo "=============================================="
echo "   OdooForge Sandbox Installation"
echo "=============================================="
echo ""

# Check prerequisites
echo_step "Checking prerequisites..."

if ! command -v docker &> /dev/null; then
    echo_error "Docker is not installed. Please install Docker first."
    exit 1
fi
echo_success "Docker is installed"

if ! command -v docker compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo_error "Docker Compose is not available. Please install Docker Compose."
    exit 1
fi
echo_success "Docker Compose is available"

if ! docker info &> /dev/null; then
    echo_error "Docker daemon is not running. Please start Docker."
    exit 1
fi
echo_success "Docker daemon is running"

# Check for port conflicts
echo_step "Checking for port conflicts..."

check_port() {
    local port=$1
    local service=$2
    if lsof -i :"$port" &> /dev/null 2>&1 || ss -tuln | grep -q ":$port " 2>/dev/null; then
        echo_warning "Port $port ($service) may be in use"
        return 1
    fi
    return 0
}

PORT_CONFLICT=0
check_port 8069 "Odoo" || PORT_CONFLICT=1
check_port 5432 "PostgreSQL" || PORT_CONFLICT=1

if [ $PORT_CONFLICT -eq 1 ]; then
    echo_warning "Some ports may be in use. Containers may fail to start."
    echo_warning "Stop conflicting services or modify docker-compose.yml ports."
    read -p "Continue anyway? [y/N] " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    echo_success "All required ports are available"
fi

# Create necessary directories
echo_step "Creating directory structure..."
mkdir -p addons templates specs reports
echo_success "Directories created"

# Pull images first
echo_step "Pulling Docker images..."
docker compose pull db odoo 2>/dev/null || true
echo_success "Images pulled"

# Build kit container
echo_step "Building kit CLI container..."
docker compose build kit
echo_success "Kit container built"

# Start services
echo_step "Starting services..."
docker compose up -d
echo_success "Services started"

# Wait for database
echo_step "Waiting for PostgreSQL to be ready..."
RETRIES=30
until docker compose exec -T db pg_isready -U odoo -d odoo &> /dev/null || [ $RETRIES -eq 0 ]; do
    echo -n "."
    sleep 1
    ((RETRIES--))
done
echo ""

if [ $RETRIES -eq 0 ]; then
    echo_error "PostgreSQL failed to start"
    docker compose logs db
    exit 1
fi
echo_success "PostgreSQL is ready"

# Wait for Odoo
echo_step "Waiting for Odoo to be ready (this may take 1-2 minutes)..."
RETRIES=120
until curl -sf http://localhost:8069/web/health &> /dev/null || [ $RETRIES -eq 0 ]; do
    echo -n "."
    sleep 2
    ((RETRIES--))
done
echo ""

if [ $RETRIES -eq 0 ]; then
    echo_warning "Odoo health check timed out, but service may still be starting..."
    # Check if container is running and healthy
    if docker compose ps odoo | grep -q "running"; then
        echo_success "Odoo container is running"
    else
        echo_error "Odoo container is not running"
        docker compose logs odoo | tail -20
        exit 1
    fi
else
    echo_success "Odoo is ready and healthy"
fi

# Verify kit CLI
echo_step "Verifying kit CLI..."
if docker compose exec -T kit kit version &> /dev/null; then
    KIT_VERSION=$(docker compose exec -T kit kit version 2>/dev/null | head -1)
    echo_success "Kit CLI is working: $KIT_VERSION"
else
    echo_warning "Kit CLI version check failed, but container is running"
fi

# Final status
echo ""
echo "=============================================="
echo "   Installation Complete!"
echo "=============================================="
echo ""
echo "Services:"
docker compose ps --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}" 2>/dev/null || docker compose ps
echo ""
echo "Quick Start:"
echo "  - Odoo:        http://localhost:8069"
echo "  - Enter CLI:   docker compose exec kit bash"
echo "  - Create module: docker compose exec kit kit init ipai_hello"
echo "  - Run tests:   docker compose exec kit pytest tests/test_uat.py -v"
echo ""
echo "Credentials:"
echo "  - Odoo Admin:  admin / admin"
echo "  - Database:    odoo / odoo"
echo ""
