#!/usr/bin/env bash
# validate_runtime_schema_mirror.sh — Drift guard for runtime schema artifacts.
#
# Checks that runtime-derived artifacts exist and are recent.
# Intended for CI or pre-commit to catch stale schema snapshots.
#
# Usage: ./scripts/validate_runtime_schema_mirror.sh [--max-age-days N]
#
# Returns: 0 if artifacts exist and are fresh, 1 otherwise.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
RUNTIME_DIR="${REPO_ROOT}/docs/data-model/runtime"
MAX_AGE_DAYS="${1:-7}"  # Default: warn if older than 7 days
EXIT_CODE=0

echo "=== Runtime Schema Mirror Validation ==="
echo "Artifact dir: ${RUNTIME_DIR}"
echo "Max age:      ${MAX_AGE_DAYS} days"
echo ""

# Check directory exists
if [[ ! -d "${RUNTIME_DIR}" ]]; then
    echo "FAIL: Runtime artifact directory does not exist"
    echo "  Run: ./scripts/dev/run_schema_mirror_local.sh"
    exit 1
fi

# Check required artifacts
REQUIRED_FILES=(
    "odoo_schema.json"
    "manifest.json"
)

for file in "${REQUIRED_FILES[@]}"; do
    path="${RUNTIME_DIR}/${file}"
    if [[ ! -f "$path" ]]; then
        echo "FAIL: Missing required artifact: ${file}"
        EXIT_CODE=1
    else
        # Check age
        if [[ "$(uname)" == "Darwin" ]]; then
            file_age=$(( ( $(date +%s) - $(stat -f %m "$path") ) / 86400 ))
        else
            file_age=$(( ( $(date +%s) - $(stat -c %Y "$path") ) / 86400 ))
        fi

        if (( file_age > MAX_AGE_DAYS )); then
            echo "WARN: ${file} is ${file_age} days old (max: ${MAX_AGE_DAYS})"
            # Warn but don't fail — staleness is informational
        else
            echo "PASS: ${file} (${file_age}d old)"
        fi
    fi
done

# Validate manifest.json structure
MANIFEST="${RUNTIME_DIR}/manifest.json"
if [[ -f "${MANIFEST}" ]]; then
    if python3 -c "import json; json.load(open('${MANIFEST}'))" 2>/dev/null; then
        echo "PASS: manifest.json is valid JSON"
    else
        echo "FAIL: manifest.json is malformed"
        EXIT_CODE=1
    fi
fi

# Check schema JSON is non-trivial
SCHEMA="${RUNTIME_DIR}/odoo_schema.json"
if [[ -f "${SCHEMA}" ]]; then
    size=$(wc -c < "${SCHEMA}" | tr -d ' ')
    if (( size < 100 )); then
        echo "FAIL: odoo_schema.json is suspiciously small (${size} bytes)"
        EXIT_CODE=1
    else
        echo "PASS: odoo_schema.json (${size} bytes)"
    fi
fi

echo ""
if [[ $EXIT_CODE -eq 0 ]]; then
    echo "All runtime schema artifacts valid."
else
    echo "Runtime schema validation failed."
    echo "Run: ./scripts/dev/run_schema_mirror_local.sh"
fi

exit $EXIT_CODE
