#!/usr/bin/env bash
set -euo pipefail

: "${INPUT_FILE:?missing INPUT_FILE}"
: "${OUTPUT_FILE:?missing OUTPUT_FILE}"

echo "=== Markitdown Normalize ==="
echo "Input:  ${INPUT_FILE}"
echo "Output: ${OUTPUT_FILE}"
echo ""

# TODO: Wire Markitdown MCP/tool runner
# markitdown "${INPUT_FILE}" > "${OUTPUT_FILE}"

echo "[STUB] Markitdown normalization not yet wired. Replace with actual runner."
exit 1
