#!/usr/bin/env bash
# Example: Run tests for a single IPAI module
set -euo pipefail

MODULE="ipai_ai_core"
TEST_DB="test_${MODULE}"

echo "=== Drop existing test DB ==="
dropdb -h localhost -U tbwa --if-exists "${TEST_DB}" 2>/dev/null || true

echo "=== Run tests ==="
~/.pyenv/versions/odoo-18-dev/bin/python vendor/odoo/odoo-bin \
  --database="${TEST_DB}" \
  --db_host=localhost --db_port=5432 --db_user=tbwa --db_password=False \
  --addons-path=vendor/odoo/addons,addons/ipai \
  --init="${MODULE}" \
  --test-enable \
  --stop-after-init \
  --log-level=test

echo "=== Run specific test class ==="
# Uncomment to run specific tests:
# --test-tags /${MODULE}:TestAiCore

echo "=== Cleanup ==="
dropdb -h localhost -U tbwa --if-exists "${TEST_DB}" 2>/dev/null || true
