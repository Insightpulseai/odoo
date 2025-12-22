#!/usr/bin/env bash
# CI check script to require audit artifacts before production claims
set -euo pipefail

AUDIT_DIR="${1:-audit}"

echo "Checking for required audit artifacts in $AUDIT_DIR..."

MISSING=0

if [ ! -f "$AUDIT_DIR/snapshot.txt" ]; then
    echo "ERROR: Missing $AUDIT_DIR/snapshot.txt"
    echo "  Run: ./tools/audit/snapshot.sh"
    MISSING=1
fi

if [ ! -f "$AUDIT_DIR/db_truth.txt" ]; then
    echo "WARNING: Missing $AUDIT_DIR/db_truth.txt"
    echo "  Run: psql -f tools/audit/db_truth.sql > audit/db_truth.txt"
    # Not blocking, as DB access may not be available in CI
fi

if [ $MISSING -eq 1 ]; then
    echo ""
    echo "FAILED: Required audit artifacts are missing."
    echo "Please generate artifacts before claiming production readiness."
    exit 2
fi

echo "SUCCESS: All required audit artifacts present."
exit 0
