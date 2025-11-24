#!/usr/bin/env bash
# Odoo CE/OCA Test Runner
# Runs Odoo tests with configurable modules and logging

set -euo pipefail

# Ensure python exists
if ! command -v python >/dev/null 2>&1; then
  echo "❌ python not found"
  exit 1
fi

DB_NAME="${DB_NAME:-odoo}"
ODOO_MODULES="${ODOO_MODULES:-all}"
LOG_LEVEL="${LOG_LEVEL:-info}"
ADDONS_PATH="${ADDONS_PATH:-addons,oca}"
ODOO_BIN="${ODOO_BIN:-odoo-bin}"  # Can be overridden for CI
TEST_TAGS="${TEST_TAGS:-}"        # Optional test tags (e.g., "/unit", "/integration")
WITH_COVERAGE="${WITH_COVERAGE:-false}"  # Enable coverage reporting

echo "========================================="
echo "Odoo Test Runner"
echo "========================================="
echo "Modules: ${ODOO_MODULES}"
echo "Database: ${DB_NAME}"
echo "Log level: ${LOG_LEVEL}"
echo "Addons path: ${ADDONS_PATH}"
echo "Odoo binary (raw): ${ODOO_BIN:-<auto>}"
echo "Test tags: ${TEST_TAGS:-all}"
echo "Coverage: ${WITH_COVERAGE}"
echo "========================================="

# Detect odoo-bin location if not specified or left as default
if [ -z "${ODOO_BIN:-}" ] || [ "${ODOO_BIN}" = "odoo-bin" ]; then
  # Try common locations
  if [ -f "$HOME/odoo-source-18/odoo-bin" ]; then
    ODOO_BIN="$HOME/odoo-source-18/odoo-bin"
  elif [ -f "/tmp/odoo/odoo-bin" ]; then
    ODOO_BIN="python /tmp/odoo/odoo-bin"
  elif command -v odoo-bin &> /dev/null; then
    ODOO_BIN="odoo-bin"
  elif command -v odoo &> /dev/null; then
    ODOO_BIN="odoo"
  else
    echo "❌ ODOO_BIN not set and could not find odoo/odoo-bin in PATH"
    echo "   Make sure scripts/ci/install_odoo_18.sh ran earlier in this job or set ODOO_BIN explicitly."
    exit 1
  fi
fi

echo "Resolved Odoo binary: ${ODOO_BIN}"

# Build test command
EXTRA_ARGS="$*"
TEST_CMD="${ODOO_BIN} -d ${DB_NAME} -i ${ODOO_MODULES} --stop-after-init --log-level=${LOG_LEVEL} --test-enable --addons-path=${ADDONS_PATH}"

# Add test tags if specified
if [ -n "${TEST_TAGS}" ]; then
  TEST_CMD="${TEST_CMD} --test-tags=${TEST_TAGS}"
  echo "Running tests with tags: ${TEST_TAGS}"
fi

# Append any extra CLI args passed to this script
if [ -n "${EXTRA_ARGS}" ]; then
  TEST_CMD="${TEST_CMD} ${EXTRA_ARGS}"
fi

# Run with or without coverage
if [ "${WITH_COVERAGE}" = "true" ]; then
  echo "Running with coverage analysis..."

  # Ensure coverage is installed
  if ! command -v coverage &> /dev/null; then
    echo "Warning: coverage not installed. Installing..."
    pip install coverage
  fi

  # Run with coverage
  eval "coverage run --source=addons --omit='*/tests/*' ${TEST_CMD}"

  # Generate reports
  echo ""
  echo "========================================="
  echo "Coverage Report"
  echo "========================================="
  coverage report -m

  # Generate HTML report if requested
  if [ "${COVERAGE_HTML:-false}" = "true" ]; then
    coverage html -d coverage_html
    echo "HTML coverage report generated in: coverage_html/"
  fi
else
  # Run without coverage
  eval "${TEST_CMD}"
fi

echo ""
echo "========================================="
echo "Tests completed successfully!"
echo "========================================="
