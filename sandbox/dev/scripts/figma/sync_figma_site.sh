#!/usr/bin/env bash
# Figma Design Token Sync Orchestrator
# Exports all Figma artifacts (styles, components, variables, file, manifest, contract)
# Integrates poll-based version detection with parallel API calls
#
# Usage:
#   source scripts/figma/load_figma_env.sh
#   ./scripts/figma/sync_figma_site.sh
#
# Environment:
#   FIGMA_ACCESS_TOKEN - Figma personal access token (required)
#   FIGMA_FILE_KEY - Figma file key (required)
#   DESIGN_TOKENS_DIR - Output directory (default: design-tokens/)

set -euo pipefail

# ============================================================================
# CONFIGURATION
# ============================================================================

: "${FIGMA_ACCESS_TOKEN:?Missing FIGMA_ACCESS_TOKEN}"
: "${FIGMA_FILE_KEY:?Missing FIGMA_FILE_KEY}"

DESIGN_TOKENS_DIR="${DESIGN_TOKENS_DIR:-design-tokens}"
CACHE_DIR="${CACHE_DIR:-.cache}"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

mkdir -p "$DESIGN_TOKENS_DIR" "$CACHE_DIR"

echo "=== Figma Sync Orchestrator ==="
echo "File Key: ${FIGMA_FILE_KEY}"
echo "Output Dir: ${DESIGN_TOKENS_DIR}"
echo ""

# ============================================================================
# STEP 1: Poll for Changes (Deterministic Version Detection)
# ============================================================================

echo "[1/6] Polling Figma file version..."

export OUT_DIR="artifacts/figma"
"${REPO_ROOT}/scripts/figma/poll_file_version.sh"

# Read poll result
POLL_RESULT="${OUT_DIR}/poll_result.json"
if [[ ! -f "$POLL_RESULT" ]]; then
  echo "ERROR: Poll result not found at $POLL_RESULT"
  exit 1
fi

FIGMA_CHANGED="$(python3 -c "import json; print(json.load(open('$POLL_RESULT'))['changed'])")"
FIGMA_VERSION="$(python3 -c "import json; print(json.load(open('$POLL_RESULT'))['current_version'])")"
FIGMA_NAME="$(python3 -c "import json; print(json.load(open('$POLL_RESULT'))['name'])")"

echo "Version: ${FIGMA_VERSION}"
echo "Changed: ${FIGMA_CHANGED}"

# Early exit if no changes (unless FORCE_SYNC=true)
if [[ "${FIGMA_CHANGED}" == "False" ]] && [[ "${FORCE_SYNC:-false}" != "true" ]]; then
  echo ""
  echo "✅ No changes detected. Skipping sync."
  echo "   Set FORCE_SYNC=true to force sync."
  exit 0
fi

echo ""

# ============================================================================
# STEP 2: Export Figma Artifacts in Parallel (Performance Optimization)
# ============================================================================

echo "[2/6] Exporting Figma API artifacts (parallel)..."

# Background job tracking
pids=()

# Export Styles
(
  echo "  - Fetching styles..."
  curl -sS "https://api.figma.com/v1/files/${FIGMA_FILE_KEY}/styles" \
    -H "X-Figma-Token: ${FIGMA_ACCESS_TOKEN}" \
    -o "${DESIGN_TOKENS_DIR}/figma-styles.json"
  echo "  ✅ Styles exported"
) &
pids+=($!)

# Export Components
(
  echo "  - Fetching components..."
  curl -sS "https://api.figma.com/v1/files/${FIGMA_FILE_KEY}/components" \
    -H "X-Figma-Token: ${FIGMA_ACCESS_TOKEN}" \
    -o "${DESIGN_TOKENS_DIR}/figma-components.json"
  echo "  ✅ Components exported"
) &
pids+=($!)

# Export Variables (Enterprise only - graceful fail)
(
  echo "  - Fetching variables (may fail for non-Enterprise)..."
  if curl -sS "https://api.figma.com/v1/files/${FIGMA_FILE_KEY}/variables/local" \
    -H "X-Figma-Token: ${FIGMA_ACCESS_TOKEN}" \
    -o "${DESIGN_TOKENS_DIR}/figma-variables.json" 2>/dev/null; then
    echo "  ✅ Variables exported (Enterprise)"
  else
    echo "{}" > "${DESIGN_TOKENS_DIR}/figma-variables.json"
    echo "  ⚠️  Variables unavailable (requires Enterprise plan)"
  fi
) &
pids+=($!)

# Export Full File
(
  echo "  - Fetching full file..."
  curl -sS "https://api.figma.com/v1/files/${FIGMA_FILE_KEY}" \
    -H "X-Figma-Token: ${FIGMA_ACCESS_TOKEN}" \
    -o "${DESIGN_TOKENS_DIR}/figma-file.json"
  echo "  ✅ Full file exported"
) &
pids+=($!)

# Wait for all parallel API calls
for pid in "${pids[@]}"; do
  wait "$pid"
done

echo ""

# ============================================================================
# STEP 3: Export Manifest (Node.js Script)
# ============================================================================

echo "[3/6] Exporting Figma manifest..."

# Check if manifest script exists
MANIFEST_SCRIPT="${REPO_ROOT}/../scripts/figma/pull_figma_sites_manifest.mjs"
if [[ -f "$MANIFEST_SCRIPT" ]]; then
  cd "${REPO_ROOT}/.."
  FIGMA_TOKEN="${FIGMA_ACCESS_TOKEN}" node "$MANIFEST_SCRIPT" > "${REPO_ROOT}/${DESIGN_TOKENS_DIR}/manifest.json"
  cd "${REPO_ROOT}"
  echo "  ✅ Manifest exported"
else
  echo "  ⚠️  Manifest script not found at $MANIFEST_SCRIPT"
  echo "     Skipping manifest export"
fi

echo ""

# ============================================================================
# STEP 4: Export Contract (TypeScript Script)
# ============================================================================

echo "[4/6] Exporting Figma contract..."

# Check if contract script exists
CONTRACT_SCRIPT="${REPO_ROOT}/../odoo/scripts/design/export_figma_contract.ts"
if [[ -f "$CONTRACT_SCRIPT" ]]; then
  cd "${REPO_ROOT}/.."
  FIGMA_TOKEN="${FIGMA_ACCESS_TOKEN}" npx tsx "$CONTRACT_SCRIPT" \
    --file-key "${FIGMA_FILE_KEY}" \
    --out "${REPO_ROOT}/${DESIGN_TOKENS_DIR}/figma-contract.json"
  cd "${REPO_ROOT}"
  echo "  ✅ Contract exported"
else
  echo "  ⚠️  Contract script not found at $CONTRACT_SCRIPT"
  echo "     Skipping contract export"
fi

echo ""

# ============================================================================
# STEP 5: Save Version Metadata
# ============================================================================

echo "[5/6] Saving version metadata..."

echo "${FIGMA_VERSION}" > "${DESIGN_TOKENS_DIR}/.figma-version"
python3 -c "import json; print(json.load(open('$POLL_RESULT'))['last_modified'])" > "${DESIGN_TOKENS_DIR}/.figma-last-modified"

echo "  ✅ Version metadata saved"
echo ""

# ============================================================================
# STEP 6: Summary
# ============================================================================

echo "[6/6] Sync Summary"
echo "================="

artifact_count=0
for file in figma-styles.json figma-components.json figma-variables.json figma-file.json manifest.json figma-contract.json; do
  if [[ -f "${DESIGN_TOKENS_DIR}/$file" ]]; then
    size=$(wc -c < "${DESIGN_TOKENS_DIR}/$file" | tr -d ' ')
    echo "  ✅ $file (${size} bytes)"
    ((artifact_count++))
  fi
done

echo ""
echo "Total artifacts: ${artifact_count}/6"
echo "Version: ${FIGMA_VERSION}"
echo "File: ${FIGMA_NAME}"
echo ""
echo "✅ Figma sync complete!"
