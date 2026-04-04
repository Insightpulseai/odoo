#!/usr/bin/env bash
# =============================================================================
# Evidence Pack Assembly — automations/scripts/evidence_pack.sh
# =============================================================================
# Collects all verification artifacts from a pipeline run into a single
# evidence bundle with a machine-readable manifest.
#
# Required env vars:
#   BUILD_ID — pipeline build identifier (e.g. Azure DevOps $(Build.BuildId))
#
# Optional env vars:
#   EVIDENCE_ROOT — source root for evidence artifacts (default: docs/evidence)
#   OUTPUT_DIR    — bundle output directory (default: .artifacts/evidence-pack)
#   BASE_URL      — target URL that was verified (for manifest metadata)
# =============================================================================

set -euo pipefail

: "${BUILD_ID:?BUILD_ID is required}"

EVIDENCE_ROOT="${EVIDENCE_ROOT:-docs/evidence}"
OUTPUT_DIR="${OUTPUT_DIR:-.artifacts/evidence-pack}"
BASE_URL="${BASE_URL:-unknown}"
TIMESTAMP=$(date +%Y%m%d-%H%M)

mkdir -p "${OUTPUT_DIR}"

echo "=============================================="
echo "Evidence Pack Assembly"
echo "Time:          $(date)"
echo "Build ID:      ${BUILD_ID}"
echo "Evidence root: ${EVIDENCE_ROOT}"
echo "Output dir:    ${OUTPUT_DIR}"
echo "=============================================="

# --- Step 1: Discover evidence directories ---
# Evidence dirs follow the pattern: docs/evidence/<YYYYMMDD-HHMM>/<scope>/
EVIDENCE_DIRS=()
if [ -d "${EVIDENCE_ROOT}" ]; then
  while IFS= read -r dir; do
    EVIDENCE_DIRS+=("${dir}")
  done < <(find "${EVIDENCE_ROOT}" -mindepth 2 -maxdepth 2 -type d 2>/dev/null | sort)
fi

echo "Found ${#EVIDENCE_DIRS[@]} evidence directories"

if [ "${#EVIDENCE_DIRS[@]}" -eq 0 ]; then
  echo "WARN: No evidence directories found under ${EVIDENCE_ROOT}"
  echo "  Expected structure: ${EVIDENCE_ROOT}/<YYYYMMDD-HHMM>/<scope>/"
  echo "  The evidence pack will contain only pipeline metadata."
fi

# --- Step 2: Collect verification manifests ---
MANIFESTS=()
OVERALL_VERDICT="PASS"

for dir in "${EVIDENCE_DIRS[@]}"; do
  manifest="${dir}/verification.json"
  if [ -f "${manifest}" ]; then
    MANIFESTS+=("${manifest}")
    # Check for any FAIL verdict
    if grep -q '"verdict":\s*"FAIL"' "${manifest}" 2>/dev/null; then
      OVERALL_VERDICT="FAIL"
    fi
  fi
done

echo "Found ${#MANIFESTS[@]} verification manifests"

# --- Step 3: Collect screenshots ---
SCREENSHOT_COUNT=0
SCREENSHOT_DIR="${OUTPUT_DIR}/screenshots"
mkdir -p "${SCREENSHOT_DIR}"

for dir in "${EVIDENCE_DIRS[@]}"; do
  if [ -d "${dir}/screenshots" ]; then
    scope=$(basename "${dir}")
    while IFS= read -r img; do
      base=$(basename "${img}")
      cp "${img}" "${SCREENSHOT_DIR}/${scope}-${base}"
      SCREENSHOT_COUNT=$((SCREENSHOT_COUNT + 1))
    done < <(find "${dir}/screenshots" -name "*.png" -type f 2>/dev/null)
  fi
done

echo "Collected ${SCREENSHOT_COUNT} screenshots"

# --- Step 4: Collect logs ---
LOG_COUNT=0
LOG_DIR="${OUTPUT_DIR}/logs"
mkdir -p "${LOG_DIR}"

# Playwright logs
for dir in "${EVIDENCE_DIRS[@]}"; do
  if [ -f "${dir}/playwright.log" ]; then
    scope=$(basename "${dir}")
    cp "${dir}/playwright.log" "${LOG_DIR}/${scope}-playwright.log"
    LOG_COUNT=$((LOG_COUNT + 1))
  fi
done

# Odoo test logs
if [ -d ".artifacts/test-logs" ]; then
  for log in .artifacts/test-logs/*.log; do
    [ -f "${log}" ] || continue
    cp "${log}" "${LOG_DIR}/$(basename "${log}")"
    LOG_COUNT=$((LOG_COUNT + 1))
  done
fi

echo "Collected ${LOG_COUNT} log files"

# --- Step 5: Build pack manifest ---
PACK_MANIFEST="${OUTPUT_DIR}/evidence-pack.json"

cat > "${PACK_MANIFEST}" <<MANIFEST
{
  "pack_version": "1.0",
  "build_id": "${BUILD_ID}",
  "timestamp": "${TIMESTAMP}",
  "target": "${BASE_URL}",
  "overall_verdict": "${OVERALL_VERDICT}",
  "counts": {
    "evidence_dirs": ${#EVIDENCE_DIRS[@]},
    "verification_manifests": ${#MANIFESTS[@]},
    "screenshots": ${SCREENSHOT_COUNT},
    "logs": ${LOG_COUNT}
  },
  "sources": [
$(for i in "${!EVIDENCE_DIRS[@]}"; do
    dir="${EVIDENCE_DIRS[$i]}"
    scope=$(basename "${dir}")
    timestamp_dir=$(basename "$(dirname "${dir}")")
    has_manifest="false"
    [ -f "${dir}/verification.json" ] && has_manifest="true"
    comma=","
    [ "$i" -eq $((${#EVIDENCE_DIRS[@]} - 1)) ] && comma=""
    echo "    {\"scope\": \"${scope}\", \"timestamp\": \"${timestamp_dir}\", \"has_manifest\": ${has_manifest}}${comma}"
done)
  ],
  "artifacts": {
    "screenshots": "${OUTPUT_DIR}/screenshots/",
    "logs": "${OUTPUT_DIR}/logs/",
    "manifest": "${PACK_MANIFEST}"
  }
}
MANIFEST

# --- Step 6: Create tarball ---
TARBALL="${OUTPUT_DIR}/evidence-pack-${BUILD_ID}.tar.gz"
tar -czf "${TARBALL}" -C "${OUTPUT_DIR}" \
  evidence-pack.json \
  screenshots/ \
  logs/ \
  2>/dev/null || true

echo ""
echo "=============================================="
echo "Evidence Pack: ${OVERALL_VERDICT}"
echo "  Evidence dirs:  ${#EVIDENCE_DIRS[@]}"
echo "  Manifests:      ${#MANIFESTS[@]}"
echo "  Screenshots:    ${SCREENSHOT_COUNT}"
echo "  Logs:           ${LOG_COUNT}"
echo "  Pack manifest:  ${PACK_MANIFEST}"
echo "  Tarball:        ${TARBALL}"
echo "=============================================="

# Exit code reflects overall verdict
if [ "${OVERALL_VERDICT}" = "FAIL" ]; then
  exit 1
fi
exit 0
