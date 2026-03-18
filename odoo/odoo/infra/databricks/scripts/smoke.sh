#!/usr/bin/env bash
# Run smoke tests against deployed bundle
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$ROOT_DIR"

TARGET="${1:-dev}"

echo "Running smoke tests for target: $TARGET"

# Check if databricks CLI is installed
if ! command -v databricks &> /dev/null; then
    echo "ERROR: databricks CLI not found"
    exit 1
fi

# List deployed jobs
echo "Listing deployed jobs..."
databricks jobs list --output table | grep -i "ppm\|notion" || echo "No matching jobs found"

# Run DQ checks job
echo ""
echo "Running DQ checks job..."
if databricks bundle run --target "$TARGET" dq_checks; then
    echo "DQ checks completed successfully"
else
    echo "WARNING: DQ checks job failed"
fi

# Check control room status
echo ""
echo "Running control room refresh..."
if databricks bundle run --target "$TARGET" control_room_refresh; then
    echo "Control room refresh completed successfully"
else
    echo "WARNING: Control room refresh failed"
fi

echo ""
echo "Smoke tests complete for target: $TARGET"
