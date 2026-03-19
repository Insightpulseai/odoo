#!/usr/bin/env bash
# odoo-test-runner-ops: Classify test failure from log output
# Usage: classify-failure.sh <test.log>
set -euo pipefail

LOG_FILE="${1:?Usage: classify-failure.sh <test.log>}"

if [ ! -f "${LOG_FILE}" ]; then
  echo "ERROR: Log file not found: ${LOG_FILE}"
  exit 1
fi

echo "=== Failure Classification ==="
echo "Log: ${LOG_FILE}"

# Check for no tests
if ! grep -q "test_" "${LOG_FILE}"; then
  echo "Classification: init only — no tests found in module"
  exit 0
fi

# Check for environment issues
if grep -qE "(no-http|demo data|ordering|ImportError)" "${LOG_FILE}"; then
  echo "Classification: env issue — test environment problem"
  grep -E "(no-http|demo data|ordering|ImportError)" "${LOG_FILE}" | head -5
  exit 0
fi

# Check for migration gaps
if grep -qE "(AttributeError.*field|OperationalError.*column|migration)" "${LOG_FILE}"; then
  echo "Classification: migration gap — incomplete 19.0 migration"
  grep -E "(AttributeError|OperationalError|migration)" "${LOG_FILE}" | head -5
  exit 0
fi

# Check for real defects
if grep -qE "(AssertionError|FAIL|ERROR)" "${LOG_FILE}"; then
  echo "Classification: real defect — functional failure"
  grep -E "(AssertionError|FAIL|ERROR)" "${LOG_FILE}" | head -10
  exit 1
fi

echo "Classification: passes locally"
exit 0
