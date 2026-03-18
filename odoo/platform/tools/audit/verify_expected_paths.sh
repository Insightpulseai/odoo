#!/usr/bin/env bash
# Verify expected repo paths exist
set -euo pipefail

# Define expected paths for jgtolentino/odoo-ce
EXPECTED=(
  "addons"
  "deploy"
  ".github/workflows"
  "tools"
  "spec"
  "catalog"
  "kb"
)

MISSING=0
for p in "${EXPECTED[@]}"; do
  if [ ! -e "$p" ]; then
    echo "Missing expected path: $p"
    MISSING=1
  fi
done

if [ $MISSING -eq 1 ]; then
  echo ""
  echo "FAILED: Some expected paths are missing."
  exit 2
fi

echo "All expected paths present."
