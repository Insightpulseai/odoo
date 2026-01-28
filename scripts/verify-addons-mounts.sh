#!/usr/bin/env bash
# ============================================================================
# Addons Mount Validation Script
# ============================================================================
# Purpose: Validate that CE, OCA, and IPAI addons are properly mounted
# Usage: ./scripts/verify-addons-mounts.sh [--ci] [--fix]
# ============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
MANIFEST="$REPO_ROOT/addons.manifest.json"

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Flags
CI_MODE=false
FIX_MODE=false
VERBOSE=false

# Counters
TOTAL_CHECKS=0
PASSED_CHECKS=0
FAILED_CHECKS=0
WARNINGS=0

# ============================================================================
# Parse Arguments
# ============================================================================

while [[ $# -gt 0 ]]; do
    case $1 in
        --ci)
            CI_MODE=true
            shift
            ;;
        --fix)
            FIX_MODE=true
            shift
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# ============================================================================
# Helper Functions
# ============================================================================

log_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

log_success() {
    echo -e "${GREEN}✅${NC} $1"
    PASSED_CHECKS=$((PASSED_CHECKS + 1))
}

log_error() {
    echo -e "${RED}❌${NC} $1"
    FAILED_CHECKS=$((FAILED_CHECKS + 1))
}

log_warning() {
    echo -e "${YELLOW}⚠️${NC} $1"
    WARNINGS=$((WARNINGS + 1))
}

log_header() {
    echo ""
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

# ============================================================================
# Validation Functions
# ============================================================================

check_manifest_exists() {
    log_header "1. Checking Manifest File"
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))

    if [ ! -f "$MANIFEST" ]; then
        log_error "addons.manifest.json not found at: $MANIFEST"
        return 1
    fi

    # Validate JSON syntax
    if ! jq empty "$MANIFEST" 2>/dev/null; then
        log_error "Invalid JSON in addons.manifest.json"
        return 1
    fi

    log_success "Manifest file exists and is valid JSON"
}

check_source_directories() {
    log_header "2. Checking Source Directories"

    local sources=$(jq -r '.source | to_entries[] | "\(.key):\(.value)"' "$MANIFEST")

    while IFS=: read -r name path; do
        TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
        local full_path="$REPO_ROOT/$path"

        if [ -d "$full_path" ]; then
            log_success "Source directory exists: $name ($path)"
        else
            log_error "Source directory missing: $name ($path)"

            if [ "$FIX_MODE" = true ]; then
                log_info "Creating directory: $full_path"
                mkdir -p "$full_path"
            fi
        fi
    done <<< "$sources"
}

check_mount_paths() {
    log_header "3. Checking Mount Paths"

    local mounts=$(jq -c '.mounts[]' "$MANIFEST")

    while IFS= read -r mount; do
        TOTAL_CHECKS=$((TOTAL_CHECKS + 1))

        local name=$(echo "$mount" | jq -r '.name')
        local source=$(echo "$mount" | jq -r '.source')
        local required=$(echo "$mount" | jq -r '.required')
        local full_path="$REPO_ROOT/$source"

        if [ -d "$full_path" ]; then
            local module_count=$(find "$full_path" -maxdepth 2 -name "__manifest__.py" -o -name "__openerp__.py" | wc -l)
            log_success "$name: $module_count modules found"

            if [ "$VERBOSE" = true ]; then
                find "$full_path" -maxdepth 2 -type d -name "[!.]*" | sed 's/^/    /'
            fi
        else
            if [ "$required" = "true" ]; then
                log_error "$name: REQUIRED path missing ($source)"
            else
                log_warning "$name: Optional path missing ($source)"
            fi

            if [ "$FIX_MODE" = true ] && [ "$required" = "true" ]; then
                log_info "Creating required directory: $full_path"
                mkdir -p "$full_path"
            fi
        fi
    done <<< "$mounts"
}

check_odoo_config() {
    log_header "4. Checking Odoo Configuration"

    local odoo_conf="$REPO_ROOT/odoo.conf"

    if [ -f "$odoo_conf" ]; then
        TOTAL_CHECKS=$((TOTAL_CHECKS + 1))

        if grep -q "^addons_path" "$odoo_conf"; then
            local addons_path=$(grep "^addons_path" "$odoo_conf" | cut -d= -f2 | tr ',' '\n')
            log_success "Found addons_path in odoo.conf"

            if [ "$VERBOSE" = true ]; then
                echo "$addons_path" | sed 's/^/    /'
            fi
        else
            log_warning "addons_path not configured in odoo.conf"
        fi
    else
        log_warning "odoo.conf not found (expected for development)"
    fi
}

check_oca_lock_file() {
    log_header "5. Checking OCA Lock File"

    local oca_lock="$REPO_ROOT/oca.lock.json"

    if [ -f "$oca_lock" ]; then
        TOTAL_CHECKS=$((TOTAL_CHECKS + 1))

        if jq empty "$oca_lock" 2>/dev/null; then
            local repo_count=$(jq -r '.repos | length' "$oca_lock")
            log_success "oca.lock.json valid: $repo_count repositories"
        else
            log_error "oca.lock.json is invalid JSON"
        fi
    else
        log_warning "oca.lock.json not found (run: make oca-pull)"
    fi
}

check_devcontainer_mounts() {
    log_header "6. Checking DevContainer Mounts"

    local devcontainer="$REPO_ROOT/.devcontainer/devcontainer.json"

    if [ -f "$devcontainer" ]; then
        TOTAL_CHECKS=$((TOTAL_CHECKS + 1))

        if jq empty "$devcontainer" 2>/dev/null; then
            local has_mounts=$(jq -r '.mounts // [] | length' "$devcontainer")
            log_success "devcontainer.json valid: $has_mounts mount(s) configured"
        else
            log_error "devcontainer.json is invalid JSON"
        fi
    else
        log_warning "devcontainer.json not found"
    fi
}

check_docker_compose_volumes() {
    log_header "7. Checking Docker Compose Volumes"

    local compose_file="$REPO_ROOT/docker-compose.yml"

    if [ -f "$compose_file" ]; then
        TOTAL_CHECKS=$((TOTAL_CHECKS + 1))

        if yq eval '.services.odoo.volumes' "$compose_file" &>/dev/null; then
            local volume_count=$(yq eval '.services.odoo.volumes | length' "$compose_file")
            log_success "docker-compose.yml valid: $volume_count volume(s)"

            if [ "$VERBOSE" = true ]; then
                yq eval '.services.odoo.volumes[]' "$compose_file" | sed 's/^/    /'
            fi
        else
            log_error "docker-compose.yml missing odoo service volumes"
        fi
    else
        log_warning "docker-compose.yml not found"
    fi
}

update_manifest_timestamp() {
    if [ "$CI_MODE" = false ] && [ -f "$MANIFEST" ]; then
        local timestamp=$(date -Iseconds)
        jq --arg ts "$timestamp" '.metadata.last_validated = $ts' "$MANIFEST" > "$MANIFEST.tmp"
        mv "$MANIFEST.tmp" "$MANIFEST"
        log_info "Updated manifest timestamp: $timestamp"
    fi
}

# ============================================================================
# Main Execution
# ============================================================================

main() {
    log_header "Odoo Addons Mount Validation"
    echo "Repository: $REPO_ROOT"
    echo "CI Mode: $CI_MODE"
    echo "Fix Mode: $FIX_MODE"
    echo ""

    # Run all checks
    check_manifest_exists
    check_source_directories
    check_mount_paths
    check_odoo_config
    check_oca_lock_file
    check_devcontainer_mounts
    check_docker_compose_volumes

    # Update manifest if successful
    if [ $FAILED_CHECKS -eq 0 ]; then
        update_manifest_timestamp
    fi

    # Summary
    log_header "Validation Summary"
    echo "Total Checks: $TOTAL_CHECKS"
    echo -e "${GREEN}Passed: $PASSED_CHECKS${NC}"
    echo -e "${RED}Failed: $FAILED_CHECKS${NC}"
    echo -e "${YELLOW}Warnings: $WARNINGS${NC}"
    echo ""

    if [ $FAILED_CHECKS -eq 0 ]; then
        log_success "All critical validations passed!"
        exit 0
    else
        log_error "Validation failed with $FAILED_CHECKS error(s)"

        if [ "$FIX_MODE" = false ]; then
            echo ""
            log_info "Run with --fix to auto-create missing directories"
        fi

        exit 1
    fi
}

# Run main function
main
