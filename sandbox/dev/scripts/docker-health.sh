#!/usr/bin/env bash
set -euo pipefail

# Docker Health Check Script
# Comprehensive status verification for Docker Desktop and Odoo services

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Flags
WAIT_MODE=false
AUTO_FIX=false

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --wait)
      WAIT_MODE=true
      shift
      ;;
    --fix)
      AUTO_FIX=true
      shift
      ;;
    *)
      echo "Usage: $0 [--wait] [--fix]"
      echo "  --wait  Wait for Docker Desktop to start"
      echo "  --fix   Auto-run fixes (docker compose up -d)"
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

print_section() {
  echo ""
  echo -e "${BLUE}=== $1 ===${NC}"
  echo ""
}

# Check 1: Docker Desktop daemon
check_docker_daemon() {
  if docker info &>/dev/null; then
    print_status "ok" "Docker Desktop: Running"
    return 0
  else
    print_status "fail" "Docker Desktop: Not running"
    echo ""
    echo "To start Docker Desktop:"
    echo "  1. Open Spotlight (⌘ + Space)"
    echo "  2. Type 'Docker' and press Enter"
    echo "  3. Wait for 'Docker Desktop is running' in menu bar"
    echo "  4. Then run: docker compose up -d"
    echo ""
    echo "Or run: ./scripts/start-odoo.sh"

    if [[ "$WAIT_MODE" == true ]]; then
      echo ""
      print_status "info" "Waiting for Docker Desktop to start..."
      local timeout=120
      while ! docker info &>/dev/null && [[ $timeout -gt 0 ]]; do
        sleep 2
        timeout=$((timeout - 2))
        echo -n "."
      done
      echo ""

      if docker info &>/dev/null; then
        print_status "ok" "Docker Desktop started successfully"
        return 0
      else
        print_status "fail" "Docker Desktop failed to start within 2 minutes"
        return 1
      fi
    fi

    return 1
  fi
}

# Check 2: Docker Compose services
check_compose_services() {
  local services_json
  if ! services_json=$(docker compose ps --format json 2>/dev/null); then
    print_status "fail" "Compose Services: Unable to query"
    echo ""
    echo "Run: docker compose up -d"

    if [[ "$AUTO_FIX" == true ]]; then
      echo ""
      print_status "info" "Auto-fix enabled: Starting services..."
      docker compose up -d
      sleep 5
      return 0
    fi

    return 1
  fi

  local total_services
  local running_services
  total_services=$(echo "$services_json" | jq -s 'length')
  running_services=$(echo "$services_json" | jq -s '[.[] | select(.State == "running")] | length')

  if [[ "$running_services" -eq "$total_services" ]] && [[ "$total_services" -gt 0 ]]; then
    print_status "ok" "Compose Services: $running_services/$total_services running"
    return 0
  else
    print_status "warn" "Compose Services: $running_services/$total_services running"
    echo ""
    echo "Services status:"
    echo "$services_json" | jq -r '.[] | "  - \(.Name): \(.State)"'

    if [[ "$AUTO_FIX" == true ]]; then
      echo ""
      print_status "info" "Auto-fix enabled: Starting missing services..."
      docker compose up -d
      sleep 5
    fi

    return 1
  fi
}

# Check 3: PostgreSQL health
check_postgres() {
  if docker compose exec -T db pg_isready -U odoo -d odoo_dev &>/dev/null; then
    print_status "ok" "PostgreSQL (odoo_dev): Ready"
    return 0
  else
    print_status "fail" "PostgreSQL (odoo_dev): Not ready"
    echo ""
    echo "Check logs: docker compose logs db"
    return 1
  fi
}

# Check 4: Redis health
check_redis() {
  local redis_response
  if redis_response=$(docker compose exec -T redis redis-cli ping 2>/dev/null); then
    if [[ "$redis_response" == "PONG" ]]; then
      print_status "ok" "Redis Cache: PONG"
      return 0
    fi
  fi

  print_status "fail" "Redis Cache: Not responding"
  echo ""
  echo "Check logs: docker compose logs redis"
  return 1
}

# Check 5: Odoo web health
check_odoo_web() {
  local max_retries=3
  local retry_delay=2
  local attempt=1

  while [[ $attempt -le $max_retries ]]; do
    if curl -sf http://localhost:8069/web/health &>/dev/null; then
      print_status "ok" "Odoo Web (8069): Healthy"
      return 0
    fi

    if [[ $attempt -lt $max_retries ]]; then
      sleep $retry_delay
      ((attempt++))
    else
      break
    fi
  done

  print_status "fail" "Odoo Web (8069): Not responding"
  echo ""
  echo "Possible causes:"
  echo "  - Odoo still starting (wait up to 90s)"
  echo "  - Check logs: docker compose logs odoo"
  echo "  - Verify health check: docker compose ps odoo"
  return 1
}

# Main execution
main() {
  print_section "Docker Health Check"

  local all_checks_passed=true

  # Check Docker daemon
  if ! check_docker_daemon; then
    all_checks_passed=false
    # If Docker isn't running, no point checking services
    exit 1
  fi

  # Check Compose services
  if ! check_compose_services; then
    all_checks_passed=false
    # If services aren't running, wait for auto-fix before continuing
    if [[ "$AUTO_FIX" == true ]]; then
      print_status "info" "Waiting 10s for services to initialize..."
      sleep 10
    fi
  fi

  # Check PostgreSQL
  if ! check_postgres; then
    all_checks_passed=false
  fi

  # Check Redis
  if ! check_redis; then
    all_checks_passed=false
  fi

  # Check Odoo web
  if ! check_odoo_web; then
    all_checks_passed=false
  fi

  # Summary
  echo ""
  if [[ "$all_checks_passed" == true ]]; then
    print_section "Summary"
    print_status "ok" "All systems operational!"
    echo ""
    echo -e "${BLUE}🌐 Access Odoo:${NC} http://localhost:8069"
    echo ""
    exit 0
  else
    print_section "Summary"
    print_status "fail" "Some checks failed"
    echo ""
    echo "Next steps:"
    echo "  1. Fix issues shown above"
    echo "  2. Re-run: $0"
    echo "  3. Or run smart startup: ./scripts/start-odoo.sh"
    echo ""
    exit 1
  fi
}

main
