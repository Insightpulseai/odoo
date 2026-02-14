#!/usr/bin/env bash
# Figma Integration Verification Script
# Tests all components of the Figma sync system

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO_ROOT"

echo "=== Figma Integration Verification ==="
echo ""

# ============================================================================
# 1. Check Required Files
# ============================================================================

echo "[1/6] Checking required files..."

required_files=(
  "scripts/figma/poll_file_version.sh"
  "scripts/figma/sync_figma_site.sh"
  "scripts/figma/load_figma_env.sh"
  "scripts/figma/setup_figma_token.sh"
  ".github/workflows/figma-sync-scheduled.yml"
)

missing=0
for file in "${required_files[@]}"; do
  if [[ -f "$file" ]]; then
    echo "  ✅ $file"
  else
    echo "  ❌ $file (missing)"
    ((missing++))
  fi
done

if [[ $missing -gt 0 ]]; then
  echo ""
  echo "ERROR: $missing required files missing"
  exit 1
fi

echo ""

# ============================================================================
# 2. Check Environment
# ============================================================================

echo "[2/6] Checking environment setup..."

if source scripts/figma/load_figma_env.sh 2>/dev/null; then
  echo "  ✅ Environment loaded successfully"
  echo "     FIGMA_FILE_KEY: ${FIGMA_FILE_KEY}"

  if [[ -n "${FIGMA_ACCESS_TOKEN}" ]]; then
    token_prefix="${FIGMA_ACCESS_TOKEN:0:10}"
    echo "     FIGMA_ACCESS_TOKEN: ${token_prefix}... (${#FIGMA_ACCESS_TOKEN} chars)"
  fi
else
  echo "  ❌ Environment setup failed"
  echo "     Run: ./scripts/figma/setup_figma_token.sh"
  exit 1
fi

echo ""

# ============================================================================
# 3. Test Figma API Access
# ============================================================================

echo "[3/6] Testing Figma API access..."

if ! command -v curl &> /dev/null; then
  echo "  ❌ curl not found"
  exit 1
fi

api_response=$(curl -sS -o /dev/null -w "%{http_code}" \
  -H "X-Figma-Token: ${FIGMA_ACCESS_TOKEN}" \
  "https://api.figma.com/v1/files/${FIGMA_FILE_KEY}")

if [[ "$api_response" == "200" ]]; then
  echo "  ✅ Figma API access successful (HTTP 200)"
else
  echo "  ❌ Figma API access failed (HTTP ${api_response})"
  echo "     Check your token and file key"
  exit 1
fi

echo ""

# ============================================================================
# 4. Test Poll Script
# ============================================================================

echo "[4/6] Testing poll_file_version.sh..."

if OUT_DIR=".test-artifacts/figma" ./scripts/figma/poll_file_version.sh; then
  echo "  ✅ Poll script executed successfully"

  if [[ -f ".test-artifacts/figma/poll_result.json" ]]; then
    version=$(python3 -c "import json; print(json.load(open('.test-artifacts/figma/poll_result.json'))['current_version'])")
    echo "     Current version: ${version}"
  fi
else
  echo "  ❌ Poll script failed"
  exit 1
fi

echo ""

# ============================================================================
# 5. Test Orchestrator (Dry Run)
# ============================================================================

echo "[5/6] Testing sync_figma_site.sh orchestrator..."

# Create test output directory
mkdir -p .test-artifacts/design-tokens

if DESIGN_TOKENS_DIR=".test-artifacts/design-tokens" \
   FORCE_SYNC=true \
   ./scripts/figma/sync_figma_site.sh; then
  echo "  ✅ Orchestrator executed successfully"

  # Count artifacts
  artifact_count=0
  for file in figma-styles.json figma-components.json figma-variables.json figma-file.json; do
    if [[ -f ".test-artifacts/design-tokens/$file" ]]; then
      size=$(wc -c < ".test-artifacts/design-tokens/$file" | tr -d ' ')
      echo "     ✅ $file (${size} bytes)"
      ((artifact_count++))
    fi
  done

  echo "     Total artifacts: ${artifact_count}/6 (4 core + 2 optional)"
else
  echo "  ❌ Orchestrator failed"
  exit 1
fi

echo ""

# ============================================================================
# 6. Cleanup Test Artifacts
# ============================================================================

echo "[6/6] Cleaning up test artifacts..."

rm -rf .test-artifacts/
echo "  ✅ Test artifacts cleaned"

echo ""
echo "==================================="
echo "✅ All verification checks passed!"
echo "==================================="
echo ""
echo "Next steps:"
echo "  1. Review integration: cat scripts/figma/README.md"
echo "  2. Run manual sync: ./scripts/figma/sync_figma_site.sh"
echo "  3. Trigger CI workflow: gh workflow run figma-sync-scheduled.yml -f force_sync=true"
echo ""
