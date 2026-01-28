#!/usr/bin/env bash
set -euo pipefail

# Parse OCA must-have modules from config/addons_manifest.oca_ipai.json
# Returns comma-separated list of module names for Odoo installer

MANIFEST_FILE="${MANIFEST_FILE:-config/addons_manifest.oca_ipai.json}"

if [ ! -f "${MANIFEST_FILE}" ]; then
  echo "ERROR: Manifest file not found: ${MANIFEST_FILE}" >&2
  exit 1
fi

# Check for jq
if ! command -v jq &> /dev/null; then
  echo "ERROR: jq is required but not installed. Install with: brew install jq" >&2
  exit 1
fi

# Extract all must-have modules from all OCA repos
# Returns flat list, comma-separated
jq -r '.oca_must_have_modules | to_entries[] | .value[]' "${MANIFEST_FILE}" \
  | sort -u \
  | paste -sd ',' -
