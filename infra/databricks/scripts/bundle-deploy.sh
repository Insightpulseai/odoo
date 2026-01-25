#!/usr/bin/env bash
# Deploy Databricks Asset Bundle to target environment
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$ROOT_DIR"

TARGET="${1:-dev}"

echo "Deploying bundle to target: $TARGET"

# Check if databricks CLI is installed
if ! command -v databricks &> /dev/null; then
    echo "ERROR: databricks CLI not found"
    exit 1
fi

# Check for required environment variables
if [ -z "${DATABRICKS_HOST:-}" ] || [ -z "${DATABRICKS_TOKEN:-}" ]; then
    echo "WARNING: DATABRICKS_HOST or DATABRICKS_TOKEN not set"
    echo "Attempting to use existing CLI configuration..."
fi

# Validate first
echo "Validating bundle..."
databricks bundle validate --target "$TARGET"

# Deploy
echo "Deploying..."
databricks bundle deploy --target "$TARGET"

echo "Deployment complete for target: $TARGET"
echo ""
echo "To run a job:"
echo "  databricks bundle run --target $TARGET <job_name>"
