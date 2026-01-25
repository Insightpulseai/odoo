#!/usr/bin/env bash
# Run unit and integration tests
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$ROOT_DIR"

echo "Running tests..."

# Install package in development mode if needed
if ! pip show workbench &> /dev/null; then
    echo "Installing workbench package..."
    pip install -e ".[dev]"
fi

# Run pytest with coverage
pytest tests/ \
    -v \
    --tb=short \
    --cov=src/workbench \
    --cov-report=term-missing \
    --cov-report=html:coverage_html \
    "$@"

echo "Tests complete. Coverage report in coverage_html/"
