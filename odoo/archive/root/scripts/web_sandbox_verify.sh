#!/bin/bash
# ============================================================================
# Web Sandbox Verification Script
# ============================================================================
# Quick verification script for Claude Code Web sandbox sessions
# Run after any mutation to verify system health
#
# Usage: ./scripts/web_sandbox_verify.sh [--quick|--full]
# ============================================================================

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Counters
PASSED=0
FAILED=0
WARNINGS=0

# Mode
MODE="${1:-quick}"

# Helper functions
print_header() {
    echo ""
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE} $1${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
}

print_section() {
    echo ""
    echo -e "${YELLOW}▶ $1${NC}"
    echo "─────────────────────────────────────────"
}

check_pass() {
    echo -e "  ${GREEN}✓${NC} $1"
    ((PASSED++))
}

check_fail() {
    echo -e "  ${RED}✗${NC} $1"
    ((FAILED++))
}

check_warn() {
    echo -e "  ${YELLOW}⚠${NC} $1"
    ((WARNINGS++))
}

check_skip() {
    echo -e "  ${BLUE}○${NC} $1 (skipped)"
}

# ============================================================================
# CHECKS
# ============================================================================

print_header "Claude Code Web Sandbox Verification"
echo "Mode: $MODE"
echo "Time: $(date '+%Y-%m-%d %H:%M:%S')"
echo "Dir:  $(pwd)"

# ----------------------------------------------------------------------------
# 1. Repository Structure
# ----------------------------------------------------------------------------
print_section "Repository Structure"

if [ -f "CLAUDE.md" ]; then
    check_pass "CLAUDE.md exists"
else
    check_fail "CLAUDE.md missing"
fi

if [ -f "CLAUDE_CODE_WEB.md" ]; then
    check_pass "CLAUDE_CODE_WEB.md exists"
else
    check_warn "CLAUDE_CODE_WEB.md missing (optional)"
fi

if [ -d ".claude" ]; then
    check_pass ".claude directory exists"
else
    check_fail ".claude directory missing"
fi

if [ -f ".claude/settings.json" ]; then
    check_pass ".claude/settings.json exists"
else
    check_fail ".claude/settings.json missing"
fi

if [ -f "docker-compose.yml" ]; then
    check_pass "docker-compose.yml exists"
else
    check_fail "docker-compose.yml missing"
fi

if [ -d "addons/ipai" ]; then
    IPAI_COUNT=$(find addons/ipai -maxdepth 1 -type d | wc -l)
    check_pass "addons/ipai exists ($((IPAI_COUNT - 1)) modules)"
else
    check_fail "addons/ipai directory missing"
fi

# ----------------------------------------------------------------------------
# 2. Git Status
# ----------------------------------------------------------------------------
print_section "Git Status"

if git rev-parse --git-dir > /dev/null 2>&1; then
    check_pass "Valid git repository"

    BRANCH=$(git branch --show-current)
    echo "  Branch: $BRANCH"

    UNCOMMITTED=$(git status --porcelain | wc -l)
    if [ "$UNCOMMITTED" -eq 0 ]; then
        check_pass "Working tree clean"
    else
        check_warn "$UNCOMMITTED uncommitted changes"
    fi
else
    check_fail "Not a git repository"
fi

# ----------------------------------------------------------------------------
# 3. Docker Status (if available)
# ----------------------------------------------------------------------------
print_section "Docker Status"

if command -v docker &> /dev/null; then
    check_pass "Docker CLI available"

    if docker info &> /dev/null 2>&1; then
        check_pass "Docker daemon running"

        # Check key containers
        if docker compose ps --format json 2>/dev/null | grep -q "postgres\|db"; then
            check_pass "PostgreSQL container present"
        else
            check_warn "PostgreSQL container not running"
        fi

        if docker compose ps --format json 2>/dev/null | grep -q "odoo"; then
            check_pass "Odoo container present"
        else
            check_warn "Odoo container not running"
        fi
    else
        check_warn "Docker daemon not accessible (expected in some sandboxes)"
    fi
else
    check_skip "Docker not available in this environment"
fi

# ----------------------------------------------------------------------------
# 4. Environment Variables
# ----------------------------------------------------------------------------
print_section "Environment Variables"

check_env() {
    local var_name=$1
    local required=$2

    if [ -n "${!var_name}" ]; then
        check_pass "$var_name is set"
    elif [ "$required" = "required" ]; then
        check_fail "$var_name not set (required)"
    else
        check_warn "$var_name not set (optional)"
    fi
}

check_env "DB_HOST" "optional"
check_env "DB_USER" "optional"
check_env "DB_NAME" "optional"
check_env "SUPABASE_URL" "optional"

# ----------------------------------------------------------------------------
# 5. Script Availability
# ----------------------------------------------------------------------------
print_section "Script Availability"

check_script() {
    local script=$1
    if [ -x "$script" ]; then
        check_pass "$script (executable)"
    elif [ -f "$script" ]; then
        check_warn "$script (exists but not executable)"
    else
        check_fail "$script missing"
    fi
}

check_script "scripts/repo_health.sh"
check_script "scripts/spec_validate.sh"
check_script "scripts/ci_local.sh"
check_script "scripts/db_verify.sh"

# ----------------------------------------------------------------------------
# 6. Full Mode: Run Verification Scripts
# ----------------------------------------------------------------------------
if [ "$MODE" = "--full" ] || [ "$MODE" = "full" ]; then
    print_section "Running Verification Scripts"

    echo "  Running repo_health.sh..."
    if ./scripts/repo_health.sh > /tmp/repo_health.log 2>&1; then
        check_pass "repo_health.sh passed"
    else
        check_fail "repo_health.sh failed (see /tmp/repo_health.log)"
    fi

    echo "  Running spec_validate.sh..."
    if ./scripts/spec_validate.sh > /tmp/spec_validate.log 2>&1; then
        check_pass "spec_validate.sh passed"
    else
        check_fail "spec_validate.sh failed (see /tmp/spec_validate.log)"
    fi
fi

# ----------------------------------------------------------------------------
# 7. Health Endpoints (if services running)
# ----------------------------------------------------------------------------
if [ "$MODE" = "--full" ] || [ "$MODE" = "full" ]; then
    print_section "Health Endpoints"

    check_endpoint() {
        local name=$1
        local url=$2

        if curl -sf "$url" > /dev/null 2>&1; then
            check_pass "$name ($url)"
        else
            check_warn "$name not responding ($url)"
        fi
    }

    check_endpoint "Odoo Core" "http://localhost:8069/web/health"
    check_endpoint "Control Room API" "http://localhost:8789/health"
    check_endpoint "Pulser Runner" "http://localhost:8788/health"
fi

# ============================================================================
# SUMMARY
# ============================================================================
print_header "Verification Summary"

echo ""
echo -e "  ${GREEN}Passed:${NC}   $PASSED"
echo -e "  ${RED}Failed:${NC}   $FAILED"
echo -e "  ${YELLOW}Warnings:${NC} $WARNINGS"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}╔═══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║                    VERIFICATION PASSED                        ║${NC}"
    echo -e "${GREEN}╚═══════════════════════════════════════════════════════════════╝${NC}"
    exit 0
else
    echo -e "${RED}╔═══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${RED}║                    VERIFICATION FAILED                        ║${NC}"
    echo -e "${RED}║              Please address the issues above                  ║${NC}"
    echo -e "${RED}╚═══════════════════════════════════════════════════════════════╝${NC}"
    exit 1
fi
