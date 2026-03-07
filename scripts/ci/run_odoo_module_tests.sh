#!/bin/bash
# =============================================================================
# Odoo Module Test Runner — CI Entrypoint
# =============================================================================
# Initializes a test database, installs specified modules, and runs unit tests.
# Designed for use as the ENTRYPOINT in docker/Dockerfile.test.
#
# Environment variables:
#   DB_HOST         PostgreSQL host (default: db)
#   DB_PORT         PostgreSQL port (default: 5432)
#   DB_USER         PostgreSQL user (default: odoo)
#   DB_PASSWORD     PostgreSQL password (default: odoo)
#   DB_NAME         Test database name (default: odoo_test)
#   TEST_MODULES    Comma-separated modules to install and test (default: base)
#   TEST_TAGS       Odoo test tags filter (optional)
#   EXTRA_ARGS      Additional odoo-bin arguments (optional)
# =============================================================================

set -euo pipefail

DB_HOST="${DB_HOST:-db}"
DB_PORT="${DB_PORT:-5432}"
DB_USER="${DB_USER:-odoo}"
DB_PASSWORD="${DB_PASSWORD:-odoo}"
DB_NAME="${DB_NAME:-odoo_test}"
TEST_MODULES="${TEST_MODULES:-base}"
TEST_TAGS="${TEST_TAGS:-}"
EXTRA_ARGS="${EXTRA_ARGS:-}"

ADDONS_PATH="${ODOO_ADDONS_PATH:-/opt/odoo/odoo-src/addons,/opt/odoo/addons/oca,/opt/odoo/addons/ipai}"

echo "=== Odoo CI Test Runner ==="
echo "  DB:      ${DB_HOST}:${DB_PORT}/${DB_NAME}"
echo "  Modules: ${TEST_MODULES}"
echo "  Tags:    ${TEST_TAGS:-<all>}"
echo "=========================="

# Wait for PostgreSQL
echo "Waiting for PostgreSQL..."
for i in $(seq 1 30); do
    if PGPASSWORD="${DB_PASSWORD}" pg_isready -h "${DB_HOST}" -p "${DB_PORT}" -U "${DB_USER}" -q 2>/dev/null; then
        echo "PostgreSQL ready."
        break
    fi
    if [ "$i" -eq 30 ]; then
        echo "ERROR: PostgreSQL not ready after 30 seconds"
        exit 1
    fi
    sleep 1
done

# Drop existing test database (if any) for clean state
echo "Ensuring clean test database..."
PGPASSWORD="${DB_PASSWORD}" dropdb \
    -h "${DB_HOST}" -p "${DB_PORT}" -U "${DB_USER}" \
    --if-exists "${DB_NAME}" 2>/dev/null || true

PGPASSWORD="${DB_PASSWORD}" createdb \
    -h "${DB_HOST}" -p "${DB_PORT}" -U "${DB_USER}" \
    "${DB_NAME}" 2>/dev/null || true

# Build odoo-bin command
CMD=(
    python -m odoo
    --database="${DB_NAME}"
    --db_host="${DB_HOST}"
    --db_port="${DB_PORT}"
    --db_user="${DB_USER}"
    --db_password="${DB_PASSWORD}"
    --addons-path="${ADDONS_PATH}"
    --init="${TEST_MODULES}"
    --test-enable
    --stop-after-init
    --log-level=test
    --no-http
)

# Add test tags if specified
if [ -n "${TEST_TAGS}" ]; then
    CMD+=(--test-tags="${TEST_TAGS}")
fi

# Add any extra arguments
if [ -n "${EXTRA_ARGS}" ]; then
    # shellcheck disable=SC2206
    CMD+=(${EXTRA_ARGS})
fi

echo "Running: ${CMD[*]}"
echo ""

# Execute tests and capture exit code
set +e
"${CMD[@]}" 2>&1
TEST_EXIT=$?
set -e

echo ""
echo "=== Test Result ==="
if [ "$TEST_EXIT" -eq 0 ]; then
    echo "PASS: All tests passed for modules: ${TEST_MODULES}"
else
    echo "FAIL: Tests failed (exit code: ${TEST_EXIT}) for modules: ${TEST_MODULES}"
fi

exit $TEST_EXIT
