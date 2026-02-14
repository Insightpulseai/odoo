#!/usr/bin/env bash
set -euo pipefail

# Smart Odoo Startup Script
# One-command startup with Docker detection, health checks, and browser launch

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Flags
NO_BROWSER=false

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --no-browser)
      NO_BROWSER=true
      shift
      ;;
    *)
      echo "Usage: $0 [--no-browser]"
      echo "  --no-browser  Don't auto-open browser when ready"
      exit 1
      ;;
  esac
done

# Helper functions
print_status() {
  local status=$1
  local message=$2
  if [[ "$status" == "ok" ]]; then
    echo -e "${GREEN}✅${NC} $message"
  elif [[ "$status" == "fail" ]]; then
    echo -e "${RED}❌${NC} $message"
  elif [[ "$status" == "warn" ]]; then
    echo -e "${YELLOW}⚠️${NC} $message"
  else
    echo -e "${BLUE}ℹ️${NC} $message"
  fi
}

# Step 1: Check Docker daemon
echo ""
echo -e "${BLUE}=== Odoo Smart Startup ===${NC}"
echo ""

if ! docker info &>/dev/null; then
  print_status "fail" "Docker Desktop is not running"
  echo ""
  echo "Please start Docker Desktop:"
  echo "  1. Open Docker Desktop app (⌘ + Space → 'Docker')"
  echo "  2. Wait for 'Docker Desktop is running' in menu bar"
  echo "  3. Re-run: $0"
  echo ""
  echo "Or enable auto-start: ./scripts/setup-docker-autostart.sh --enable"
  exit 1
fi

print_status "ok" "Docker Desktop is running"

# Step 2: Start services if not running
if ! docker compose ps odoo 2>/dev/null | grep -q "running"; then
  echo ""
  print_status "info" "Starting Odoo services..."
  docker compose up -d

  # Wait a moment for containers to initialize
  sleep 3
else
  print_status "ok" "Odoo services already running"
fi

# Step 3: Wait for PostgreSQL to be ready
echo ""
print_status "info" "Waiting for PostgreSQL..."
timeout=30
while ! docker compose exec -T db pg_isready -U odoo -d odoo_dev &>/dev/null; do
  sleep 2
  timeout=$((timeout - 2))
  if [[ $timeout -le 0 ]]; then
    print_status "fail" "PostgreSQL failed to start within 30 seconds"
    echo ""
    echo "Check logs: docker compose logs db"
    exit 1
  fi
  echo -n "."
done
echo ""
print_status "ok" "PostgreSQL ready"

# Step 4: Wait for Odoo health check (max 90s)
echo ""
print_status "info" "Waiting for Odoo web server..."
timeout=90
while ! curl -sf http://localhost:8069/web/health &>/dev/null; do
  sleep 2
  timeout=$((timeout - 2))
  if [[ $timeout -le 0 ]]; then
    print_status "fail" "Odoo failed to start within 90 seconds"
    echo ""
    echo "Check health status:"
    echo "  docker compose ps odoo"
    echo ""
    echo "Check logs:"
    echo "  docker compose logs odoo"
    echo ""
    echo "Common issues:"
    echo "  - Database migration in progress (wait longer)"
    echo "  - Module installation errors (check logs)"
    echo "  - Port 8069 already in use (check: lsof -i :8069)"
    exit 1
  fi
  echo -n "."
done
echo ""
print_status "ok" "Odoo web server healthy"

# Step 5: Success message
echo ""
echo -e "${GREEN}✅ Odoo is ready!${NC}"
echo ""
echo -e "${BLUE}🌐 Access URL:${NC} http://localhost:8069"
echo ""

# Step 6: Open browser (unless --no-browser)
if [[ "$NO_BROWSER" == false ]]; then
  print_status "info" "Opening browser..."
  open http://localhost:8069 2>/dev/null || true
fi

# Step 7: Show helpful commands
echo ""
echo "Useful commands:"
echo "  docker compose logs -f odoo    # Follow Odoo logs"
echo "  docker compose ps              # Check service status"
echo "  ./scripts/docker-health.sh     # Full health check"
echo "  docker compose down            # Stop all services"
echo ""
