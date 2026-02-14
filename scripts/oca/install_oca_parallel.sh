#!/usr/bin/env bash
# =============================================================================
# OCA Module Parallel Installer
# =============================================================================
# Installs 65+ OCA modules in dependency-ordered phases with parallel execution.
# Expected time: 30-45 minutes (vs 120+ sequential)
#
# Usage:
#   ./scripts/oca/install_oca_parallel.sh              # Full install
#   ./scripts/oca/install_oca_parallel.sh --phase 3    # Resume from phase 3
#   ./scripts/oca/install_oca_parallel.sh --dry-run    # Show plan only
#
# Prerequisites:
#   - OCA modules fetched to third_party/oca/
#   - config/odoo.conf updated with addons_path
#   - Database initialized and running
# =============================================================================

set -euo pipefail

# Configuration
ODOO_DB="${ODOO_DB:-odoo_dev}"
ODOO_BIN="${ODOO_BIN:-odoo-bin}"
ODOO_ADDONS_PATH="${ODOO_ADDONS_PATH:-/usr/lib/python3/dist-packages/odoo/addons,/mnt/extra-addons/ipai,/mnt/extra-addons/third_party/oca/*}"
CONFIG_FILE="${CONFIG_FILE:-config/oca/module_allowlist.yml}"
LOG_DIR="${LOG_DIR:-logs/oca_install}"
START_PHASE="${START_PHASE:-1}"
DRY_RUN="${DRY_RUN:-false}"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Phase definitions - maps pack names to phase numbers
declare -A PACK_PHASES=(
  # Phase 1: Foundation (no dependencies)
  [foundation]=1

  # Phase 2: Tier 1 Parallel (5 packs can run simultaneously)
  [web_ux]=2
  [reporting]=2
  [purchase_workflow]=2
  [project_timesheet]=2
  [crm_extensions]=2

  # Phase 3: Accounting Core
  [accounting_core]=3

  # Phase 4: Accounting Reconcile (depends on accounting_core)
  [accounting_reconcile]=4

  # Phase 5: Accounting Statements (depends on reconcile)
  [accounting_statements]=5

  # Phase 6: HR Modules
  [hr_modules]=6
)

# Setup
mkdir -p "$LOG_DIR"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
MAIN_LOG="$LOG_DIR/install_${TIMESTAMP}.log"

# Logging
log() {
  echo -e "${BLUE}[$(date +%H:%M:%S)]${NC} $*" | tee -a "$MAIN_LOG"
}

log_success() {
  echo -e "${GREEN}[$(date +%H:%M:%S)] ✓${NC} $*" | tee -a "$MAIN_LOG"
}

log_error() {
  echo -e "${RED}[$(date +%H:%M:%S)] ✗${NC} $*" | tee -a "$MAIN_LOG"
}

log_warning() {
  echo -e "${YELLOW}[$(date +%H:%M:%S)] ⚠${NC} $*" | tee -a "$MAIN_LOG"
}

# Check prerequisites
check_prerequisites() {
  log "Checking prerequisites..."

  # Check yq installed
  if ! command -v yq &> /dev/null; then
    log_error "yq not found. Install with: brew install yq"
    exit 1
  fi

  # Check config file
  if [[ ! -f "$CONFIG_FILE" ]]; then
    log_error "Config file not found: $CONFIG_FILE"
    exit 1
  fi

  # Check OCA modules
  if [[ ! -d "third_party/oca" ]]; then
    log_error "OCA modules not found. Run: ./scripts/oca/fetch_and_pin.sh --force"
    exit 1
  fi

  local module_count=$(find third_party/oca -name "__manifest__.py" 2>/dev/null | wc -l | tr -d ' ')
  if [[ "$module_count" -lt 50 ]]; then
    log_error "Only $module_count OCA modules found (expected 65+)"
    exit 1
  fi

  log_success "Prerequisites OK (OCA modules: $module_count)"
}

# Install a single pack of modules
install_pack() {
  local pack_name=$1
  local modules_csv=$2
  local pack_log="$LOG_DIR/${pack_name}_${TIMESTAMP}.log"

  if [[ "$DRY_RUN" == "true" ]]; then
    log "  [DRY RUN] Would install: $pack_name ($modules_csv)"
    return 0
  fi

  log "  📦 Installing $pack_name..." | tee -a "$pack_log"

  # Use Docker exec if running in container context
  if [[ -n "${DOCKER_EXEC_CMD:-}" ]]; then
    $DOCKER_EXEC_CMD $ODOO_BIN \
      -d "$ODOO_DB" \
      --addons-path "$ODOO_ADDONS_PATH" \
      -i "$modules_csv" \
      --stop-after-init \
      --log-level=info \
      --without-demo=all \
      >> "$pack_log" 2>&1
  else
    $ODOO_BIN \
      -d "$ODOO_DB" \
      --addons-path "$ODOO_ADDONS_PATH" \
      -i "$modules_csv" \
      --stop-after-init \
      --log-level=info \
      --without-demo=all \
      >> "$pack_log" 2>&1
  fi

  if [[ $? -eq 0 ]]; then
    log_success "  ✓ Completed: $pack_name" | tee -a "$pack_log"
  else
    log_error "  ✗ Failed: $pack_name (see $pack_log)" | tee -a "$pack_log"
    return 1
  fi
}

# Main orchestrator
main() {
  log "═══════════════════════════════════════════════════════════"
  log "  OCA Module Parallel Installer"
  log "═══════════════════════════════════════════════════════════"
  log "Database: $ODOO_DB"
  log "Addons Path: $ODOO_ADDONS_PATH"
  log "Start Phase: $START_PHASE"
  log "Dry Run: $DRY_RUN"
  log "Log Directory: $LOG_DIR"
  log ""

  check_prerequisites

  # Process each phase
  for phase in {1..6}; do
    if [[ $phase -lt $START_PHASE ]]; then
      log "Skipping phase $phase (starting from phase $START_PHASE)"
      continue
    fi

    log ""
    log "═══════════════════════════════════════════════════════════"
    log "  Phase $phase: Starting..."
    log "═══════════════════════════════════════════════════════════"

    declare -a PIDS=()
    declare -a PACK_NAMES=()

    # Find all packs for this phase
    for pack in "${!PACK_PHASES[@]}"; do
      if [[ ${PACK_PHASES[$pack]} -eq $phase ]]; then
        # Get modules for this pack from YAML
        MODULES=$(yq -r ".packs.$pack | join(\",\")" "$CONFIG_FILE")

        if [[ -z "$MODULES" || "$MODULES" == "null" ]]; then
          log_warning "  No modules found for pack: $pack"
          continue
        fi

        # Install pack in background
        install_pack "$pack" "$MODULES" &
        PIDS+=($!)
        PACK_NAMES+=("$pack")
      fi
    done

    # Wait for all packs in this phase
    if [[ ${#PIDS[@]} -gt 0 ]]; then
      log "  ⏳ Waiting for phase $phase (${#PIDS[@]} packs: ${PACK_NAMES[*]})..."

      local failed=0
      for i in "${!PIDS[@]}"; do
        local pid=${PIDS[$i]}
        local pack_name=${PACK_NAMES[$i]}

        if wait "$pid"; then
          log_success "  ✓ Pack completed: $pack_name"
        else
          log_error "  ✗ Pack failed: $pack_name (PID $pid)"
          failed=$((failed + 1))
        fi
      done

      if [[ $failed -gt 0 ]]; then
        log_error "Phase $phase failed ($failed/${#PIDS[@]} packs failed)"
        log_error "Check individual pack logs in: $LOG_DIR"
        exit 1
      fi

      log_success "Phase $phase complete (${#PIDS[@]} packs installed)"
    else
      log_warning "Phase $phase: No packs to install"
    fi
  done

  log ""
  log "═══════════════════════════════════════════════════════════"
  log_success "  All phases complete!"
  log "═══════════════════════════════════════════════════════════"
  log "Next steps:"
  log "  1. Validate: python3 scripts/oca/validate_installation.py"
  log "  2. Generate parity report: python scripts/test_ee_parity.py"
  log "  3. Check logs: $MAIN_LOG"
}

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --phase)
      START_PHASE="$2"
      shift 2
      ;;
    --dry-run)
      DRY_RUN=true
      shift
      ;;
    --docker-exec)
      DOCKER_EXEC_CMD="$2"
      shift 2
      ;;
    *)
      echo "Unknown option: $1"
      echo "Usage: $0 [--phase N] [--dry-run] [--docker-exec 'docker exec odoo']"
      exit 1
      ;;
  esac
done

# Run
main
