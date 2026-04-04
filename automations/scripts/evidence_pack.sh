#!/usr/bin/env bash
set -euo pipefail

: "${EVIDENCE_DIR:?missing EVIDENCE_DIR}"
: "${OUTPUT_DIR:?missing OUTPUT_DIR}"

mkdir -p "${OUTPUT_DIR}"

echo "=== Evidence Pack Assembly ==="
echo "Source: ${EVIDENCE_DIR}"
echo "Output: ${OUTPUT_DIR}"
echo ""

echo "Steps:"
echo "  1. Collect raw evidence files"
echo "  2. Normalize via Markitdown"
echo "  3. Generate artifact manifest"
echo "  4. Bundle into ${OUTPUT_DIR}/evidence-pack.tar.gz"
echo ""

# TODO: Wire Markitdown normalization + tar bundle
echo "[STUB] Evidence pack assembly not yet wired. Replace with actual runner."
exit 1
