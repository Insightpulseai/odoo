#!/usr/bin/env bash
# =============================================================================
# Odoo CE Go-Live Orchestrator
# =============================================================================
# Main orchestration script for production go-live sequence.
# Executes pre-flight checks, deployment, and validation in order.
#
# Usage:
#   ./scripts/go_live.sh [--dry-run] [--validate-only] [--skip-backup]
#
# Options:
#   --dry-run        Show what would be done without executing
#   --validate-only  Only run validation checks, skip deployment
#   --skip-backup    Skip pre-deployment backup (use with caution)
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Defaults
DRY_RUN=false
VALIDATE_ONLY=false
SKIP_BACKUP=false
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
LOG_FILE="$ROOT_DIR/logs/go_live_$TIMESTAMP.log"

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --validate-only)
            VALIDATE_ONLY=true
            shift
            ;;
        --skip-backup)
            SKIP_BACKUP=true
            shift
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            exit 1
            ;;
    esac
done

# Ensure log directory exists
mkdir -p "$ROOT_DIR/logs"

# Logging function
log() {
    local level=$1
    local message=$2
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo -e "${timestamp} [${level}] ${message}" | tee -a "$LOG_FILE"
}

# Banner
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}   Odoo CE Go-Live Orchestrator${NC}"
echo -e "${BLUE}   Timestamp: $TIMESTAMP${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo ""

if [[ "$DRY_RUN" == "true" ]]; then
    echo -e "${YELLOW}DRY RUN MODE - No changes will be made${NC}"
    echo ""
fi

if [[ "$VALIDATE_ONLY" == "true" ]]; then
    echo -e "${CYAN}VALIDATE ONLY MODE - Only running checks${NC}"
    echo ""
fi

# =============================================================================
# Phase 1: Pre-Flight Checks
# =============================================================================
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}Phase 1: Pre-Flight Checks${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

log "INFO" "Starting pre-flight checks..."

# Check Docker
echo -n "  Docker installed... "
if command -v docker &>/dev/null; then
    echo -e "${GREEN}✓${NC}"
    log "INFO" "Docker check passed"
else
    echo -e "${RED}✗${NC}"
    log "ERROR" "Docker not installed"
    exit 1
fi

# Check Docker Compose
echo -n "  Docker Compose installed... "
if command -v docker compose &>/dev/null || command -v docker-compose &>/dev/null; then
    echo -e "${GREEN}✓${NC}"
    log "INFO" "Docker Compose check passed"
else
    echo -e "${RED}✗${NC}"
    log "ERROR" "Docker Compose not installed"
    exit 1
fi

# Check docker-compose.yml exists
echo -n "  docker-compose.yml exists... "
if [[ -f "$ROOT_DIR/docker-compose.yml" ]]; then
    echo -e "${GREEN}✓${NC}"
    log "INFO" "docker-compose.yml found"
else
    echo -e "${RED}✗${NC}"
    log "ERROR" "docker-compose.yml not found"
    exit 1
fi

# Check environment file
echo -n "  Environment file exists... "
if [[ -f "$ROOT_DIR/.env" ]] || [[ -f "$ROOT_DIR/.env.prod" ]]; then
    echo -e "${GREEN}✓${NC}"
    log "INFO" "Environment file found"
else
    echo -e "${YELLOW}⚠ (using defaults)${NC}"
    log "WARN" "No environment file found, using defaults"
fi

# Check OCA allowlist
echo -n "  OCA allowlist configured... "
if [[ -f "$ROOT_DIR/config/oca/module_allowlist.yml" ]]; then
    MODULE_COUNT=$(grep -c "^    - " "$ROOT_DIR/config/oca/module_allowlist.yml" 2>/dev/null || echo "0")
    echo -e "${GREEN}✓ ($MODULE_COUNT modules)${NC}"
    log "INFO" "OCA allowlist found with $MODULE_COUNT modules"
else
    echo -e "${YELLOW}⚠ (no allowlist)${NC}"
    log "WARN" "No OCA allowlist configured"
fi

# Check Phase 0 gate
echo -n "  Phase 0 gate status... "
if [[ -f "$ROOT_DIR/scripts/phase0_gate.sh" ]]; then
    if [[ "$DRY_RUN" == "true" ]]; then
        echo -e "${CYAN}(dry-run skip)${NC}"
    else
        if bash "$ROOT_DIR/scripts/phase0_gate.sh" &>/dev/null; then
            echo -e "${GREEN}✓ PASSED${NC}"
            log "INFO" "Phase 0 gate passed"
        else
            echo -e "${RED}✗ FAILED${NC}"
            log "ERROR" "Phase 0 gate failed"
            exit 1
        fi
    fi
else
    echo -e "${YELLOW}⚠ (script not found)${NC}"
    log "WARN" "Phase 0 gate script not found"
fi

echo ""

# =============================================================================
# Phase 2: Pre-Deployment Backup
# =============================================================================
if [[ "$VALIDATE_ONLY" != "true" ]]; then
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}Phase 2: Pre-Deployment Backup${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

    if [[ "$SKIP_BACKUP" == "true" ]]; then
        echo -e "${YELLOW}  Backup skipped (--skip-backup flag)${NC}"
        log "WARN" "Pre-deployment backup skipped"
    elif [[ "$DRY_RUN" == "true" ]]; then
        echo -e "${CYAN}  Would create backup: backup_pre_golive_$TIMESTAMP${NC}"
        log "INFO" "Dry-run: Would create backup"
    else
        log "INFO" "Creating pre-deployment backup..."

        if [[ -f "$ROOT_DIR/scripts/backup/create_backup.sh" ]]; then
            if bash "$ROOT_DIR/scripts/backup/create_backup.sh" --full --tag "pre_golive_$TIMESTAMP"; then
                echo -e "  ${GREEN}✓ Backup created: pre_golive_$TIMESTAMP${NC}"
                log "INFO" "Backup created successfully"
            else
                echo -e "  ${RED}✗ Backup failed${NC}"
                log "ERROR" "Backup creation failed"
                exit 1
            fi
        else
            echo -e "  ${YELLOW}⚠ Backup script not found, skipping${NC}"
            log "WARN" "Backup script not found"
        fi
    fi
    echo ""
fi

# =============================================================================
# Phase 3: Service Deployment
# =============================================================================
if [[ "$VALIDATE_ONLY" != "true" ]]; then
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}Phase 3: Service Deployment${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

    if [[ "$DRY_RUN" == "true" ]]; then
        echo -e "${CYAN}  Would execute:${NC}"
        echo "    docker compose pull"
        echo "    docker compose up -d"
        log "INFO" "Dry-run: Would deploy services"
    else
        log "INFO" "Deploying services..."

        echo -n "  Pulling latest images... "
        if docker compose -f "$ROOT_DIR/docker-compose.yml" pull &>/dev/null; then
            echo -e "${GREEN}✓${NC}"
            log "INFO" "Images pulled successfully"
        else
            echo -e "${YELLOW}⚠ (some pulls failed)${NC}"
            log "WARN" "Some image pulls failed"
        fi

        echo -n "  Starting services... "
        if docker compose -f "$ROOT_DIR/docker-compose.yml" up -d; then
            echo -e "${GREEN}✓${NC}"
            log "INFO" "Services started"
        else
            echo -e "${RED}✗${NC}"
            log "ERROR" "Service startup failed"
            exit 1
        fi

        echo -n "  Waiting for healthy state... "
        RETRIES=30
        while [[ $RETRIES -gt 0 ]]; do
            if docker compose -f "$ROOT_DIR/docker-compose.yml" ps | grep -q "healthy\|running"; then
                echo -e "${GREEN}✓${NC}"
                log "INFO" "Services healthy"
                break
            fi
            sleep 5
            RETRIES=$((RETRIES - 1))
        done

        if [[ $RETRIES -eq 0 ]]; then
            echo -e "${RED}✗ (timeout)${NC}"
            log "ERROR" "Services did not become healthy within timeout"
            exit 1
        fi
    fi
    echo ""
fi

# =============================================================================
# Phase 4: Smoke Tests
# =============================================================================
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}Phase 4: Smoke Tests${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

if [[ -f "$ROOT_DIR/scripts/smoke_test_odoo.sh" ]]; then
    if [[ "$DRY_RUN" == "true" ]]; then
        echo -e "${CYAN}  Would run: smoke_test_odoo.sh${NC}"
        log "INFO" "Dry-run: Would run smoke tests"
    else
        log "INFO" "Running smoke tests..."
        if bash "$ROOT_DIR/scripts/smoke_test_odoo.sh"; then
            echo -e "  ${GREEN}✓ All smoke tests passed${NC}"
            log "INFO" "Smoke tests passed"
        else
            echo -e "  ${RED}✗ Smoke tests failed${NC}"
            log "ERROR" "Smoke tests failed"
            exit 1
        fi
    fi
else
    echo -e "  ${YELLOW}⚠ Smoke test script not found${NC}"
    log "WARN" "Smoke test script not found"

    # Basic health check fallback
    echo -n "  Basic health check... "
    if [[ "$DRY_RUN" != "true" ]]; then
        ODOO_URL="${ODOO_URL:-http://localhost:8069}"
        if curl -sf "$ODOO_URL/web/health" &>/dev/null || curl -sf "$ODOO_URL/" &>/dev/null; then
            echo -e "${GREEN}✓${NC}"
            log "INFO" "Basic health check passed"
        else
            echo -e "${RED}✗${NC}"
            log "ERROR" "Basic health check failed"
            exit 1
        fi
    else
        echo -e "${CYAN}(dry-run skip)${NC}"
    fi
fi

echo ""

# =============================================================================
# Phase 5: Post-Deployment Validation
# =============================================================================
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}Phase 5: Post-Deployment Validation${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

log "INFO" "Running post-deployment validation..."

# Check container status
echo -n "  Container status... "
if [[ "$DRY_RUN" != "true" ]]; then
    RUNNING=$(docker compose -f "$ROOT_DIR/docker-compose.yml" ps --status running -q 2>/dev/null | wc -l | tr -d ' ')
    if [[ "$RUNNING" -gt 0 ]]; then
        echo -e "${GREEN}✓ ($RUNNING containers running)${NC}"
        log "INFO" "$RUNNING containers running"
    else
        echo -e "${YELLOW}⚠ (no containers)${NC}"
        log "WARN" "No containers detected"
    fi
else
    echo -e "${CYAN}(dry-run skip)${NC}"
fi

# Check for errors in logs
echo -n "  Error log check... "
if [[ "$DRY_RUN" != "true" ]]; then
    ERROR_COUNT=$(docker compose -f "$ROOT_DIR/docker-compose.yml" logs --tail=100 2>/dev/null | grep -ci "error\|critical\|fatal" || echo "0")
    if [[ "$ERROR_COUNT" -eq 0 ]]; then
        echo -e "${GREEN}✓ (no errors)${NC}"
        log "INFO" "No errors in recent logs"
    else
        echo -e "${YELLOW}⚠ ($ERROR_COUNT errors found)${NC}"
        log "WARN" "$ERROR_COUNT errors found in logs"
    fi
else
    echo -e "${CYAN}(dry-run skip)${NC}"
fi

echo ""

# =============================================================================
# Summary
# =============================================================================
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}   Go-Live Summary${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"

if [[ "$DRY_RUN" == "true" ]]; then
    echo -e "${CYAN}Dry run completed - no changes made${NC}"
elif [[ "$VALIDATE_ONLY" == "true" ]]; then
    echo -e "${GREEN}Validation completed successfully${NC}"
else
    echo -e "${GREEN}Go-live sequence completed successfully${NC}"
fi

echo ""
echo -e "Log file: ${BLUE}$LOG_FILE${NC}"
echo ""

log "INFO" "Go-live sequence completed"
