#!/usr/bin/env bash
# =============================================================================
# Production Verification Runner — automations/scripts/prod_verify_playwright.sh
# =============================================================================
# Runs Playwright smoke tests against a target URL and produces deterministic
# evidence output (screenshots, verification JSON, pass/fail summary).
#
# Required env vars:
#   BASE_URL — target to verify (e.g. https://erp.insightpulseai.com)
#
# Optional env vars:
#   EVIDENCE_ROOT — override evidence root (default: docs/evidence)
#   SKIP_INSTALL  — set to "1" to skip npx playwright install
# =============================================================================

set -euo pipefail

: "${BASE_URL:?BASE_URL is required (e.g. https://erp.insightpulseai.com)}"

TIMESTAMP=$(date +%Y%m%d-%H%M)
EVIDENCE_ROOT="${EVIDENCE_ROOT:-docs/evidence}"
EVIDENCE_DIR="${EVIDENCE_ROOT}/${TIMESTAMP}/prod-verify"
SCREENSHOTS_DIR="${EVIDENCE_DIR}/screenshots"
RESULT_FILE="${EVIDENCE_DIR}/verification.json"

mkdir -p "${SCREENSHOTS_DIR}"

echo "=============================================="
echo "Production Verification Runner"
echo "Time:         $(date)"
echo "Target:       ${BASE_URL}"
echo "Evidence dir: ${EVIDENCE_DIR}"
echo "=============================================="

# --- Step 1: Ensure Playwright is available ---
E2E_DIR="infra/tests/e2e"

if [ ! -d "${E2E_DIR}/node_modules" ]; then
  echo "Installing test dependencies..."
  (cd "${E2E_DIR}" && npm install --no-audit --no-fund 2>&1)
fi

if [ "${SKIP_INSTALL:-0}" != "1" ]; then
  echo "Installing Playwright browsers..."
  (cd "${E2E_DIR}" && npx playwright install chromium --with-deps 2>&1 | tail -5)
fi

# --- Step 2: Run prod-verify specs ---
echo ""
echo "Running production verification specs..."

PLAYWRIGHT_EXIT=0
(cd "${E2E_DIR}" && \
  BASE_URL="${BASE_URL}" \
  EVIDENCE_DIR="../../../${EVIDENCE_DIR}" \
  npx playwright test specs/prod-verify.spec.ts \
    --reporter=list,json \
    --output="../../../${EVIDENCE_DIR}/test-results" \
    2>&1) | tee "${EVIDENCE_DIR}/playwright.log" || PLAYWRIGHT_EXIT=$?

# --- Step 3: Build verification manifest ---
PASS_COUNT=$(grep -c "✓\|passed" "${EVIDENCE_DIR}/playwright.log" 2>/dev/null || echo "0")
FAIL_COUNT=$(grep -c "✘\|failed" "${EVIDENCE_DIR}/playwright.log" 2>/dev/null || echo "0")
SCREENSHOT_COUNT=$(find "${SCREENSHOTS_DIR}" -name "*.png" 2>/dev/null | wc -l | tr -d ' ')

# Determine overall verdict
if [ "${PLAYWRIGHT_EXIT}" -eq 0 ]; then
  VERDICT="PASS"
else
  VERDICT="FAIL"
fi

cat > "${RESULT_FILE}" <<MANIFEST
{
  "timestamp": "${TIMESTAMP}",
  "target": "${BASE_URL}",
  "verdict": "${VERDICT}",
  "exit_code": ${PLAYWRIGHT_EXIT},
  "counts": {
    "passed": ${PASS_COUNT},
    "failed": ${FAIL_COUNT},
    "screenshots": ${SCREENSHOT_COUNT}
  },
  "artifacts": {
    "log": "${EVIDENCE_DIR}/playwright.log",
    "screenshots": "${SCREENSHOTS_DIR}/",
    "test_results": "${EVIDENCE_DIR}/test-results/"
  }
}
MANIFEST

echo ""
echo "=============================================="
echo "Verification: ${VERDICT}"
echo "  Passed: ${PASS_COUNT}"
echo "  Failed: ${FAIL_COUNT}"
echo "  Screenshots: ${SCREENSHOT_COUNT}"
echo "  Manifest: ${RESULT_FILE}"
echo "=============================================="

exit "${PLAYWRIGHT_EXIT}"
