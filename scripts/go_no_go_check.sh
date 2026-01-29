#!/usr/bin/env bash
# =============================================================================
# GO / NO-GO Checklist Script
# =============================================================================
# Validates all prerequisites before proceeding to next phase
#
# Usage:
#   ./scripts/go_no_go_check.sh [phase]
#
# Phases:
#   0  - Platform Readiness (default)
#   1  - Infrastructure Baseline
#   2  - Database Initialization
#   3  - CE + OCA Parity
#   4  - Odoo.sh Operational Parity
#   5  - Enterprise Extras
# =============================================================================

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Counters
PASSED=0
FAILED=0
WARNINGS=0

# Phase to check (default: 0)
PHASE="${1:-0}"

# =============================================================================
# Helper Functions
# =============================================================================

check_pass() {
    echo -e "  ${GREEN}✅${NC} $1"
    PASSED=$((PASSED + 1))
}

check_fail() {
    echo -e "  ${RED}❌${NC} $1"
    FAILED=$((FAILED + 1))
}

check_warn() {
    echo -e "  ${YELLOW}⚠️${NC} $1"
    WARNINGS=$((WARNINGS + 1))
}

check_info() {
    echo -e "  ${BLUE}ℹ️${NC} $1"
}

check_file() {
    if [ -f "$1" ]; then
        check_pass "File exists: $1"
        return 0
    else
        check_fail "Missing file: $1"
        return 1
    fi
}

check_dir() {
    if [ -d "$1" ]; then
        check_pass "Directory exists: $1"
        return 0
    else
        check_fail "Missing directory: $1"
        return 1
    fi
}

check_executable() {
    if [ -x "$1" ]; then
        check_pass "Executable: $1"
        return 0
    else
        check_fail "Not executable: $1"
        return 1
    fi
}

# =============================================================================
# Phase 0: Platform Readiness
# =============================================================================

check_phase_0() {
    echo ""
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}PHASE 0: PLATFORM READINESS${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
    echo ""

    echo "1. Spec Kit Structure"
    echo "─────────────────────"
    check_dir "spec/"

    echo ""
    echo "2. LLM Context Files"
    echo "────────────────────"
    check_file "llms.txt"
    check_file "llms-full.txt"

    # Validate llms.txt content
    if [ -f "llms.txt" ]; then
        LINES=$(wc -l < llms.txt | tr -d ' ')
        if [ "$LINES" -ge 100 ]; then
            check_pass "llms.txt has $LINES lines (≥100)"
        else
            check_fail "llms.txt has only $LINES lines (<100)"
        fi
    fi

    echo ""
    echo "3. CI Gates"
    echo "───────────"
    check_file ".github/workflows/llms-txt-check.yml"
    check_file ".github/workflows/ci-runbot.yml"
    check_file ".github/workflows/docs-drift-gate.yml"

    echo ""
    echo "4. Parity Check"
    echo "───────────────"
    if check_file "scripts/check_odoosh_parity.py"; then
        if python3 scripts/check_odoosh_parity.py --threshold 95 > /dev/null 2>&1; then
            SCORE=$(python3 scripts/check_odoosh_parity.py --output json 2>/dev/null | python3 -c "import sys,json; print(json.load(sys.stdin)['total_score'])" 2>/dev/null || echo "0")
            check_pass "Parity score: ${SCORE}% (≥95%)"
        else
            check_fail "Parity score below 95%"
        fi
    fi

    echo ""
    echo "5. Documentation"
    echo "────────────────"
    check_file "CLAUDE.md"
    check_dir "docs/"
}

# =============================================================================
# Phase 1: Infrastructure Baseline
# =============================================================================

check_phase_1() {
    echo ""
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}PHASE 1: INFRASTRUCTURE BASELINE${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
    echo ""

    echo "1. Docker Compose Files"
    echo "───────────────────────"
    check_file "docker-compose.yml" || check_file "docker-compose.dev.yml"
    check_file "deploy/docker-compose.prod.yml" || check_file "deploy/docker-compose.ce19.yml"

    echo ""
    echo "2. Docker Images"
    echo "────────────────"
    check_file "docker/Dockerfile.ce19" || check_file "docker/Dockerfile.odoo"

    echo ""
    echo "3. Backup Scripts"
    echo "─────────────────"
    check_executable "scripts/backup/full_backup.sh"
    check_executable "scripts/backup/restore_test.sh"

    echo ""
    echo "4. Security Configuration"
    echo "─────────────────────────"
    check_dir "security/"
    check_file "security/Caddyfile.shell" || check_file "deploy/nginx/"

    echo ""
    echo "5. Runtime Documentation"
    echo "────────────────────────"
    check_file "docs/DR_RUNBOOK.md"
    check_file "docs/DB_INIT_RUNBOOK.md" || check_warn "DB init runbook not found"
}

# =============================================================================
# Phase 2: Database Initialization
# =============================================================================

check_phase_2() {
    echo ""
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}PHASE 2: DATABASE INITIALIZATION${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
    echo ""

    echo "1. Prerequisites (Phase 0 + 1)"
    echo "──────────────────────────────"
    if python3 scripts/check_odoosh_parity.py --threshold 95 > /dev/null 2>&1; then
        check_pass "Phase 0: Parity check passes"
    else
        check_fail "Phase 0: Parity check fails"
    fi

    check_file "scripts/backup/full_backup.sh" && check_pass "Phase 1: Backup scripts exist" || check_fail "Phase 1: Backup scripts missing"

    echo ""
    echo "2. Database Runbook"
    echo "───────────────────"
    check_file "docs/DB_INIT_RUNBOOK.md"

    echo ""
    echo "3. Environment Configuration"
    echo "────────────────────────────"
    if [ -f ".env" ] || [ -f ".env.local" ] || [ -f ".env.example" ]; then
        check_pass "Environment file template exists"
    else
        check_warn "No .env template found"
    fi

    echo ""
    echo "4. Docker Status"
    echo "────────────────"
    if command -v docker &> /dev/null; then
        check_pass "Docker CLI available"
        if docker compose version &> /dev/null; then
            check_pass "Docker Compose available"
        else
            check_fail "Docker Compose not available"
        fi
    else
        check_fail "Docker CLI not available"
    fi
}

# =============================================================================
# Phase 3: CE + OCA Parity
# =============================================================================

check_phase_3() {
    echo ""
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}PHASE 3: CE + OCA FUNCTIONAL PARITY${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
    echo ""

    echo "1. OCA Module Management"
    echo "────────────────────────"
    check_file "oca.lock.json" || check_dir "addons/oca/"

    echo ""
    echo "2. IPAI Custom Modules"
    echo "──────────────────────"
    check_dir "addons/ipai/" || check_dir "addons/"

    echo ""
    echo "3. Module Testing"
    echo "─────────────────"
    check_file ".github/workflows/ci-runbot.yml"
    check_file ".github/workflows/ci-odoo-ce.yml" || check_warn "Optional: ci-odoo-ce.yml"

    echo ""
    echo "4. Parity Mapping"
    echo "─────────────────"
    check_file "docs/ee_parity_mapping.yml" || check_warn "EE parity mapping not found"
}

# =============================================================================
# Phase 4: Odoo.sh Operational Parity
# =============================================================================

check_phase_4() {
    echo ""
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}PHASE 4: ODOO.SH OPERATIONAL PARITY${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
    echo ""

    echo "1. GAP 1: Branch Promotion"
    echo "──────────────────────────"
    check_file ".github/workflows/branch-promotion.yml"

    echo ""
    echo "2. GAP 2: Runbot Dashboard"
    echo "──────────────────────────"
    check_file ".github/workflows/ci-runbot.yml"
    check_file "infra/superset/datasets/ci_runbot_results.sql" || check_warn "Superset dataset optional"

    echo ""
    echo "3. GAP 3: Multi-DC Backups"
    echo "──────────────────────────"
    check_executable "scripts/backup/full_backup.sh"
    check_executable "scripts/backup/restore_test.sh"
    check_file "docs/DR_RUNBOOK.md"

    echo ""
    echo "4. GAP 4: Browser Web Shell"
    echo "───────────────────────────"
    check_file "docker-compose.shell.yml"
    check_file "security/Caddyfile.shell"
    check_file "security/WEB_SHELL_THREAT_MODEL.md"
}

# =============================================================================
# Phase 5: Enterprise Extras
# =============================================================================

check_phase_5() {
    echo ""
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}PHASE 5: ENTERPRISE EXTRAS (ROADMAP)${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
    echo ""

    echo "1. BI Integration"
    echo "─────────────────"
    check_dir "infra/superset/" || check_warn "Superset not configured"

    echo ""
    echo "2. AI Agents"
    echo "────────────"
    check_dir "mcp/" || check_warn "MCP servers not configured"

    echo ""
    echo "3. Advanced Monitoring"
    echo "──────────────────────"
    check_file "deploy/monitoring_schema.sql" || check_warn "Monitoring schema not found"

    echo ""
    echo "4. DR Drills"
    echo "────────────"
    check_file "docs/DR_RUNBOOK.md"
}

# =============================================================================
# Main Execution
# =============================================================================

main() {
    echo ""
    echo -e "${BLUE}╔═══════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║          GO / NO-GO CHECKLIST - PHASE ${PHASE}                   ║${NC}"
    echo -e "${BLUE}╚═══════════════════════════════════════════════════════════╝${NC}"

    case "$PHASE" in
        0) check_phase_0 ;;
        1) check_phase_0; check_phase_1 ;;
        2) check_phase_0; check_phase_1; check_phase_2 ;;
        3) check_phase_0; check_phase_1; check_phase_2; check_phase_3 ;;
        4) check_phase_0; check_phase_1; check_phase_2; check_phase_3; check_phase_4 ;;
        5) check_phase_0; check_phase_1; check_phase_2; check_phase_3; check_phase_4; check_phase_5 ;;
        *)
            echo "Unknown phase: $PHASE"
            echo "Usage: $0 [0|1|2|3|4|5]"
            exit 2
            ;;
    esac

    # Summary
    echo ""
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}SUMMARY${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
    echo ""
    echo -e "  ${GREEN}Passed:${NC}   $PASSED"
    echo -e "  ${RED}Failed:${NC}   $FAILED"
    echo -e "  ${YELLOW}Warnings:${NC} $WARNINGS"
    echo ""

    if [ "$FAILED" -eq 0 ]; then
        echo -e "${GREEN}╔═══════════════════════════════════════════════════════════╗${NC}"
        echo -e "${GREEN}║                    ✅ GO - PHASE $PHASE READY                   ║${NC}"
        echo -e "${GREEN}╚═══════════════════════════════════════════════════════════╝${NC}"
        exit 0
    else
        echo -e "${RED}╔═══════════════════════════════════════════════════════════╗${NC}"
        echo -e "${RED}║                 ❌ NO-GO - FIX $FAILED ISSUE(S)                  ║${NC}"
        echo -e "${RED}╚═══════════════════════════════════════════════════════════╝${NC}"
        exit 1
    fi
}

main
