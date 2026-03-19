#!/usr/bin/env bash
set -euo pipefail

# Directory where Odoo source will live on CI
ODOO_SRC_DIR="${ODOO_SRC_DIR:-$HOME/odoo-source-18}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEFAULT_CONSTRAINTS="$SCRIPT_DIR/constraints-gevent.txt"

# Honor an explicit PIP_CONSTRAINT if provided; otherwise, use the CI constraints file when available
PIP_CONSTRAINT_FILE="${PIP_CONSTRAINT:-}"
if [[ -z "$PIP_CONSTRAINT_FILE" && -f "$DEFAULT_CONSTRAINTS" ]]; then
  PIP_CONSTRAINT_FILE="$DEFAULT_CONSTRAINTS"
fi

if [[ -n "$PIP_CONSTRAINT_FILE" ]]; then
  echo "Using pip constraints from: $PIP_CONSTRAINT_FILE"
  PIP_CONSTRAINT_ARG=( -c "$PIP_CONSTRAINT_FILE" )
else
  PIP_CONSTRAINT_ARG=()
fi

echo "🔧 Installing Odoo 18 CE into: $ODOO_SRC_DIR"

if [ ! -d "$ODOO_SRC_DIR" ]; then
  git clone --depth=1 --branch 18.0 https://github.com/odoo/odoo.git "$ODOO_SRC_DIR"
fi

pip install --upgrade pip
pip install "${PIP_CONSTRAINT_ARG[@]}" -r "$ODOO_SRC_DIR/requirements.txt"
# For safety – often needed by tests
pip install "${PIP_CONSTRAINT_ARG[@]}" psycopg2-binary

# Export ODOO_BIN path for downstream steps
ODOO_BIN="$ODOO_SRC_DIR/odoo-bin"

if [ ! -f "$ODOO_BIN" ]; then
  echo "❌ odoo-bin not found at $ODOO_BIN"
  exit 1
fi

echo "✅ Odoo installed. Binary: $ODOO_BIN"

# Write an env file for GitHub Actions to consume
{
  echo "ODOO_SRC_DIR=$ODOO_SRC_DIR"
  echo "ODOO_BIN=$ODOO_BIN"
  echo "PATH=$ODOO_SRC_DIR:\$PATH"
  if [[ -n "$PIP_CONSTRAINT_FILE" ]]; then
    echo "PIP_CONSTRAINT=$PIP_CONSTRAINT_FILE"
  fi
} >> "$GITHUB_ENV"
