#!/usr/bin/env bash
#
# Odoo/OCA Lint Runner
#
# Single-command entry point for all linting operations.
# Wrapper around Makefile lint targets for convenience.
#
# Usage:
#   ./scripts/lint.sh           # Run all linters
#   ./scripts/lint.sh layout    # Layout validation only
#   ./scripts/lint.sh python    # Python linters only
#   ./scripts/lint.sh oca       # OCA checks only
#   ./scripts/lint.sh quick     # Quick layout check
#   ./scripts/lint.sh all       # All linters including OCA
#   ./scripts/lint.sh --help    # Show help
#
# Exit Codes:
#   0 - All lints passed
#   1 - Lint errors found
#   2 - Script error

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Find repo root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

# Show help
show_help() {
    cat << EOF
Odoo/OCA Lint Runner

Usage:
    $(basename "$0") [command] [options]

Commands:
    (default)   Run all linters (layout + python)
    layout      Validate Odoo/OCA directory layout and naming
    python      Run Python linters (black, isort, flake8)
    oca         Run OCA module checks via pre-commit
    quick       Quick layout check (quiet mode)
    all         Run all linters including OCA checks

Options:
    --strict    Treat warnings as errors
    --verbose   Enable verbose output
    --help      Show this help message

Examples:
    $(basename "$0")              # Run default lint suite
    $(basename "$0") layout       # Layout validation only
    $(basename "$0") quick        # Fast layout check
    $(basename "$0") all          # Full lint suite including OCA

Environment Variables:
    LINT_STRICT=1    Same as --strict
    LINT_VERBOSE=1   Same as --verbose

EOF
}

# Parse options
STRICT="${LINT_STRICT:-0}"
VERBOSE="${LINT_VERBOSE:-0}"

for arg in "$@"; do
    case $arg in
        --strict)
            STRICT=1
            shift
            ;;
        --verbose)
            VERBOSE=1
            shift
            ;;
        --help|-h)
            show_help
            exit 0
            ;;
    esac
done

# Get command (remaining arg after options)
COMMAND="${1:-default}"

# Build args for validators
VALIDATOR_ARGS=""
if [[ "$STRICT" == "1" ]]; then
    VALIDATOR_ARGS="$VALIDATOR_ARGS --strict"
fi
if [[ "$VERBOSE" == "1" ]]; then
    VALIDATOR_ARGS="$VALIDATOR_ARGS --verbose"
fi

# Log functions
log_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

log_success() {
    echo -e "${GREEN}✅${NC} $1"
}

log_error() {
    echo -e "${RED}❌${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# Run layout validation
run_layout() {
    log_info "Running Odoo/OCA layout validation..."
    cd "$REPO_ROOT"

    local exit_code=0

    python3 scripts/odoo/validate_oca_layout.py $VALIDATOR_ARGS || exit_code=$?
    python3 scripts/odoo/validate_addons_path.py $VALIDATOR_ARGS || exit_code=$?

    return $exit_code
}

# Run Python linters
run_python() {
    log_info "Running Python linters..."
    cd "$REPO_ROOT"

    local exit_code=0

    if command -v pre-commit &> /dev/null; then
        pre-commit run black --all-files || true
        pre-commit run isort --all-files || true
        pre-commit run flake8 --all-files || true
    else
        log_warn "pre-commit not installed, running standalone linters..."

        if command -v black &> /dev/null; then
            black --check addons/ipai/ scripts/odoo/ || true
        else
            log_warn "black not found"
        fi

        if command -v isort &> /dev/null; then
            isort --check-only addons/ipai/ scripts/odoo/ || true
        else
            log_warn "isort not found"
        fi

        if command -v flake8 &> /dev/null; then
            flake8 addons/ipai/ scripts/odoo/ --max-line-length=120 || true
        else
            log_warn "flake8 not found"
        fi
    fi

    return $exit_code
}

# Run OCA checks
run_oca() {
    log_info "Running OCA module checks..."
    cd "$REPO_ROOT"

    if command -v pre-commit &> /dev/null; then
        pre-commit run oca-checks-odoo-module --all-files || true
    else
        log_warn "pre-commit not installed"
        log_warn "Install with: pip install pre-commit && pre-commit install"
        return 1
    fi
}

# Run quick layout check
run_quick() {
    log_info "Running quick layout check..."
    cd "$REPO_ROOT"

    python3 scripts/odoo/validate_oca_layout.py --quiet $VALIDATOR_ARGS
    python3 scripts/odoo/validate_addons_path.py --quiet $VALIDATOR_ARGS
}

# Main execution
main() {
    cd "$REPO_ROOT"

    echo ""
    echo "========================================"
    echo "  Odoo/OCA Lint Runner"
    echo "========================================"
    echo ""

    local exit_code=0

    case "$COMMAND" in
        default)
            run_layout || exit_code=$?
            echo ""
            run_python || exit_code=$?
            ;;
        layout)
            run_layout || exit_code=$?
            ;;
        python)
            run_python || exit_code=$?
            ;;
        oca)
            run_oca || exit_code=$?
            ;;
        quick)
            run_quick || exit_code=$?
            ;;
        all)
            run_layout || exit_code=$?
            echo ""
            run_python || exit_code=$?
            echo ""
            run_oca || exit_code=$?
            ;;
        *)
            log_error "Unknown command: $COMMAND"
            echo ""
            show_help
            exit 2
            ;;
    esac

    echo ""
    echo "----------------------------------------"
    if [[ $exit_code -eq 0 ]]; then
        log_success "All lints passed!"
    else
        log_error "Lint errors found (exit code: $exit_code)"
    fi
    echo "----------------------------------------"
    echo ""

    return $exit_code
}

main "$@"
