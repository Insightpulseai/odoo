#!/usr/bin/env bash
# Example: Create a disposable test database for module testing
set -euo pipefail

MODULE="ipai_ai_core"
TEST_DB="test_${MODULE}"

echo "=== Drop existing test DB (if any) ==="
dropdb -h localhost -U tbwa --if-exists "${TEST_DB}" 2>/dev/null || true

echo "=== Create and initialize test DB ==="
~/.pyenv/versions/odoo-18-dev/bin/python vendor/odoo/odoo-bin \
  --database="${TEST_DB}" \
  --db_host=localhost --db_port=5432 --db_user=tbwa --db_password=False \
  --addons-path=vendor/odoo/addons,addons/ipai \
  --init="${MODULE}" \
  --without-demo all \
  --stop-after-init

echo "=== Verify module installed ==="
psql -h localhost -U tbwa -d "${TEST_DB}" -c \
  "SELECT name, state FROM ir_module_module WHERE name='${MODULE}'"

echo "=== Cleanup (drop test DB) ==="
# dropdb -h localhost -U tbwa "${TEST_DB}"
# Uncomment to auto-cleanup
