#!/usr/bin/env bash
# Format Python code with black and ruff
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$ROOT_DIR"

echo "Formatting Python code..."

# Format with black
echo "Running black..."
black src/ tests/ notebooks/

# Sort imports with ruff
echo "Running ruff format..."
ruff check --fix src/ tests/

echo "Formatting complete."
