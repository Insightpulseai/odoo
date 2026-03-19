#!/usr/bin/env bash
# Validate Databricks Asset Bundle configuration
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$ROOT_DIR"

TARGET="${1:-dev}"

echo "Validating bundle for target: $TARGET"

# Check if databricks CLI is installed
if ! command -v databricks &> /dev/null; then
    echo "ERROR: databricks CLI not found. Install with:"
    echo "  pip install databricks-cli"
    echo "  or"
    echo "  brew tap databricks/tap && brew install databricks"
    exit 1
fi

# Validate bundle
databricks bundle validate --target "$TARGET"

echo "Bundle validation successful for target: $TARGET"
