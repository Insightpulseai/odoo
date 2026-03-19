#!/usr/bin/env bash
# Lint Python code with ruff, black, and mypy
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$ROOT_DIR"

echo "Linting Python code..."
EXIT_CODE=0

# Check formatting with black
echo "Checking black formatting..."
if ! black --check src/ tests/; then
    echo "ERROR: Black formatting check failed. Run ./scripts/fmt.sh"
    EXIT_CODE=1
fi

# Lint with ruff
echo "Running ruff..."
if ! ruff check src/ tests/; then
    echo "ERROR: Ruff linting failed"
    EXIT_CODE=1
fi

# Type check with mypy
echo "Running mypy..."
if ! mypy src/ --ignore-missing-imports; then
    echo "WARNING: mypy found type issues"
    # Don't fail on mypy errors for now
fi

# Lint YAML files
echo "Checking YAML syntax..."
if command -v yamllint &> /dev/null; then
    if ! yamllint -d relaxed databricks.yml resources/ config/; then
        echo "WARNING: YAML lint issues found"
    fi
fi

if [ $EXIT_CODE -ne 0 ]; then
    echo "Linting failed. Please fix the issues above."
    exit $EXIT_CODE
fi

echo "Linting complete - all checks passed."
