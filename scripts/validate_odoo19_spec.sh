#!/bin/bash
# =============================================================================
# Odoo 19 Migration Spec Bundle Validator
# =============================================================================
# Validates the completeness and quality of the Odoo 19 migration spec bundle.
# Run before migration kickoff to ensure all documentation is in place.
#
# Usage:
#   ./scripts/validate_odoo19_spec.sh
#   ./scripts/validate_odoo19_spec.sh --strict  # Fail on warnings
# =============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
SPEC_DIR="$REPO_ROOT/spec/odoo-19-migration"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Counters
ERRORS=0
WARNINGS=0
CHECKS=0

# Options
STRICT_MODE=false
if [[ "$1" == "--strict" ]]; then
    STRICT_MODE=true
fi

# =============================================================================
# Helper Functions
# =============================================================================

log_header() {
    echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

log_check() {
    ((CHECKS++))
    echo -e "  ${BLUE}[CHECK]${NC} $1"
}

log_pass() {
    echo -e "    ${GREEN}✓ PASS${NC}: $1"
}

log_fail() {
    ((ERRORS++))
    echo -e "    ${RED}✗ FAIL${NC}: $1"
}

log_warn() {
    ((WARNINGS++))
    echo -e "    ${YELLOW}⚠ WARN${NC}: $1"
}

file_exists() {
    [[ -f "$1" ]]
}

file_has_content() {
    [[ -s "$1" ]]
}

file_contains() {
    grep -q "$2" "$1" 2>/dev/null
}

count_lines() {
    wc -l < "$1" | tr -d ' '
}

# =============================================================================
# Validation Checks
# =============================================================================

log_header "Odoo 19 Migration Spec Bundle Validator"

echo -e "\nSpec Directory: ${SPEC_DIR}"
echo -e "Strict Mode: ${STRICT_MODE}"

# -----------------------------------------------------------------------------
# 1. Required Files Check
# -----------------------------------------------------------------------------
log_header "1. Required Files"

REQUIRED_FILES=(
    "constitution.md"
    "prd.md"
    "plan.md"
    "tasks.md"
)

for file in "${REQUIRED_FILES[@]}"; do
    log_check "Checking $file exists"
    if file_exists "$SPEC_DIR/$file"; then
        log_pass "$file exists"
    else
        log_fail "$file is missing"
    fi
done

# -----------------------------------------------------------------------------
# 2. Constitution Validation
# -----------------------------------------------------------------------------
log_header "2. Constitution Validation"

CONSTITUTION="$SPEC_DIR/constitution.md"

log_check "Constitution has core principles"
if file_contains "$CONSTITUTION" "Core Principles"; then
    log_pass "Core principles section found"
else
    log_fail "Core principles section missing"
fi

log_check "Constitution has technical constraints"
if file_contains "$CONSTITUTION" "Technical Constraints"; then
    log_pass "Technical constraints section found"
else
    log_fail "Technical constraints section missing"
fi

log_check "Constitution has migration rules"
if file_contains "$CONSTITUTION" "Migration Rules"; then
    log_pass "Migration rules section found"
else
    log_fail "Migration rules section missing"
fi

log_check "Constitution has testing requirements"
if file_contains "$CONSTITUTION" "Testing Requirements"; then
    log_pass "Testing requirements section found"
else
    log_fail "Testing requirements section missing"
fi

log_check "Constitution defines rollback triggers"
if file_contains "$CONSTITUTION" "Rollback"; then
    log_pass "Rollback triggers defined"
else
    log_warn "Rollback triggers not explicitly defined"
fi

log_check "Constitution minimum length (>200 lines)"
CONST_LINES=$(count_lines "$CONSTITUTION")
if [[ $CONST_LINES -gt 200 ]]; then
    log_pass "Constitution has $CONST_LINES lines"
else
    log_warn "Constitution only has $CONST_LINES lines (expected >200)"
fi

# -----------------------------------------------------------------------------
# 3. PRD Validation
# -----------------------------------------------------------------------------
log_header "3. PRD Validation"

PRD="$SPEC_DIR/prd.md"

log_check "PRD has executive summary"
if file_contains "$PRD" "Executive Summary"; then
    log_pass "Executive summary found"
else
    log_fail "Executive summary missing"
fi

log_check "PRD has success criteria"
if file_contains "$PRD" "Success Criteria"; then
    log_pass "Success criteria found"
else
    log_fail "Success criteria missing"
fi

log_check "PRD defines P0 requirements"
if file_contains "$PRD" "P0"; then
    log_pass "P0 requirements defined"
else
    log_fail "P0 requirements not defined"
fi

log_check "PRD has user stories"
if file_contains "$PRD" "User Stories\|As a"; then
    log_pass "User stories found"
else
    log_warn "User stories not found"
fi

log_check "PRD has risks and mitigations"
if file_contains "$PRD" "Risk"; then
    log_pass "Risks section found"
else
    log_fail "Risks section missing"
fi

log_check "PRD has rollback plan"
if file_contains "$PRD" "Rollback"; then
    log_pass "Rollback plan found"
else
    log_fail "Rollback plan missing"
fi

log_check "PRD has cost estimate"
if file_contains "$PRD" "Cost\|Budget"; then
    log_pass "Cost estimate found"
else
    log_warn "Cost estimate not found"
fi

log_check "PRD minimum length (>150 lines)"
PRD_LINES=$(count_lines "$PRD")
if [[ $PRD_LINES -gt 150 ]]; then
    log_pass "PRD has $PRD_LINES lines"
else
    log_warn "PRD only has $PRD_LINES lines (expected >150)"
fi

# -----------------------------------------------------------------------------
# 4. Plan Validation
# -----------------------------------------------------------------------------
log_header "4. Plan Validation"

PLAN="$SPEC_DIR/plan.md"

log_check "Plan has timeline overview"
if file_contains "$PLAN" "Timeline"; then
    log_pass "Timeline overview found"
else
    log_fail "Timeline overview missing"
fi

log_check "Plan has preparation phase"
if file_contains "$PLAN" "Phase 1\|Preparation"; then
    log_pass "Preparation phase found"
else
    log_fail "Preparation phase missing"
fi

log_check "Plan has migration phase"
if file_contains "$PLAN" "Phase 2\|Migration"; then
    log_pass "Migration phase found"
else
    log_fail "Migration phase missing"
fi

log_check "Plan has testing phase"
if file_contains "$PLAN" "Phase 3\|Testing"; then
    log_pass "Testing phase found"
else
    log_fail "Testing phase missing"
fi

log_check "Plan has deployment phase"
if file_contains "$PLAN" "Phase 4\|Deployment"; then
    log_pass "Deployment phase found"
else
    log_fail "Deployment phase missing"
fi

log_check "Plan has stabilization phase"
if file_contains "$PLAN" "Phase 5\|Stabilization"; then
    log_pass "Stabilization phase found"
else
    log_warn "Stabilization phase not found"
fi

log_check "Plan has milestones"
if file_contains "$PLAN" "Milestone\|M1\|M2"; then
    log_pass "Milestones defined"
else
    log_fail "Milestones not defined"
fi

log_check "Plan has resource allocation"
if file_contains "$PLAN" "Resource\|Team"; then
    log_pass "Resource allocation found"
else
    log_warn "Resource allocation not found"
fi

log_check "Plan has risk register"
if file_contains "$PLAN" "Risk Register\|Risk.*Mitigation"; then
    log_pass "Risk register found"
else
    log_warn "Risk register not found"
fi

log_check "Plan minimum length (>200 lines)"
PLAN_LINES=$(count_lines "$PLAN")
if [[ $PLAN_LINES -gt 200 ]]; then
    log_pass "Plan has $PLAN_LINES lines"
else
    log_warn "Plan only has $PLAN_LINES lines (expected >200)"
fi

# -----------------------------------------------------------------------------
# 5. Tasks Validation
# -----------------------------------------------------------------------------
log_header "5. Tasks Validation"

TASKS="$SPEC_DIR/tasks.md"

log_check "Tasks has summary table"
if file_contains "$TASKS" "Task Summary\|Phase.*Stories"; then
    log_pass "Task summary found"
else
    log_fail "Task summary missing"
fi

log_check "Tasks defines story points"
if file_contains "$TASKS" "Story Points\|SP"; then
    log_pass "Story points defined"
else
    log_warn "Story points not defined"
fi

log_check "Tasks has acceptance criteria"
if file_contains "$TASKS" "Acceptance Criteria"; then
    log_pass "Acceptance criteria found"
else
    log_warn "Acceptance criteria not found"
fi

log_check "Tasks has Phase 1 tasks"
if file_contains "$TASKS" "Phase 1"; then
    log_pass "Phase 1 tasks found"
else
    log_fail "Phase 1 tasks missing"
fi

log_check "Tasks has Phase 2 tasks"
if file_contains "$TASKS" "Phase 2"; then
    log_pass "Phase 2 tasks found"
else
    log_fail "Phase 2 tasks missing"
fi

log_check "Tasks has Phase 3 tasks"
if file_contains "$TASKS" "Phase 3"; then
    log_pass "Phase 3 tasks found"
else
    log_fail "Phase 3 tasks missing"
fi

log_check "Tasks has BIR compliance tasks"
if file_contains "$TASKS" "BIR\|bir"; then
    log_pass "BIR compliance tasks found"
else
    log_fail "BIR compliance tasks missing (critical for PH)"
fi

log_check "Tasks has payroll migration tasks"
if file_contains "$TASKS" "payroll\|Payroll"; then
    log_pass "Payroll migration tasks found"
else
    log_fail "Payroll migration tasks missing"
fi

log_check "Tasks minimum length (>500 lines)"
TASKS_LINES=$(count_lines "$TASKS")
if [[ $TASKS_LINES -gt 500 ]]; then
    log_pass "Tasks has $TASKS_LINES lines"
else
    log_warn "Tasks only has $TASKS_LINES lines (expected >500)"
fi

# -----------------------------------------------------------------------------
# 6. Cross-Reference Validation
# -----------------------------------------------------------------------------
log_header "6. Cross-Reference Validation"

log_check "PRD references constitution"
if file_contains "$PRD" "constitution\|Constitution"; then
    log_pass "PRD references constitution"
else
    log_warn "PRD does not reference constitution"
fi

log_check "Plan references PRD requirements"
if file_contains "$PLAN" "PRD\|requirement"; then
    log_pass "Plan references PRD"
else
    log_warn "Plan does not reference PRD"
fi

log_check "Tasks reference plan phases"
if file_contains "$TASKS" "Week\|Phase\|Sprint"; then
    log_pass "Tasks reference plan phases"
else
    log_warn "Tasks do not reference plan phases"
fi

# -----------------------------------------------------------------------------
# 7. EE Parity Test Script
# -----------------------------------------------------------------------------
log_header "7. Supporting Scripts"

EE_PARITY_SCRIPT="$REPO_ROOT/scripts/test_ee_parity.py"

log_check "EE parity test script exists"
if file_exists "$EE_PARITY_SCRIPT"; then
    log_pass "test_ee_parity.py exists"
else
    log_fail "test_ee_parity.py missing"
fi

log_check "EE parity script is executable or Python"
if file_contains "$EE_PARITY_SCRIPT" "#!/usr/bin/env python"; then
    log_pass "EE parity script has Python shebang"
else
    log_warn "EE parity script missing shebang"
fi

log_check "EE parity script defines 80% threshold"
if file_contains "$EE_PARITY_SCRIPT" "80"; then
    log_pass "80% parity threshold defined"
else
    log_warn "80% parity threshold not found"
fi

# -----------------------------------------------------------------------------
# Summary
# -----------------------------------------------------------------------------
log_header "Validation Summary"

TOTAL_ISSUES=$((ERRORS + WARNINGS))

echo -e "\n  Checks Run:  $CHECKS"
echo -e "  ${RED}Errors:${NC}      $ERRORS"
echo -e "  ${YELLOW}Warnings:${NC}    $WARNINGS"

if [[ $ERRORS -gt 0 ]]; then
    echo -e "\n${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${RED}  VALIDATION FAILED: $ERRORS error(s) found${NC}"
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    exit 1
elif [[ $WARNINGS -gt 0 && "$STRICT_MODE" == "true" ]]; then
    echo -e "\n${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${YELLOW}  VALIDATION FAILED (STRICT): $WARNINGS warning(s) found${NC}"
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    exit 1
else
    echo -e "\n${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}  VALIDATION PASSED${NC}"
    if [[ $WARNINGS -gt 0 ]]; then
        echo -e "${GREEN}  ($WARNINGS warning(s) - review recommended)${NC}"
    fi
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    exit 0
fi
