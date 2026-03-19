#!/usr/bin/env bash
# apply_runtime_patches.sh — Idempotent application of runtime/patches/*.patch
#
# Usage:
#   bash scripts/apply_runtime_patches.sh          # apply all patches
#   bash scripts/apply_runtime_patches.sh --check   # dry-run (check only)
#
# Each patch is re-applied after OCA submodule updates. Script is idempotent:
# if a patch is already applied it is skipped (git apply --check detects this).
#
# Patch targets must exist as git working-tree files. Patches in
# runtime/patches/ follow the naming convention:
#   <vendor>_<module>_<odoo-version>_<description>.patch
#
# Exit codes:
#   0 — all patches applied (or already applied)
#   1 — one or more patches failed to apply
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
PATCH_DIR="${REPO_ROOT}/runtime/patches"
DRY_RUN=false
FAILED=0

if [[ "${1:-}" == "--check" ]]; then
    DRY_RUN=true
    echo "[apply_runtime_patches] dry-run mode — no files modified"
fi

echo "[apply_runtime_patches] patch dir: ${PATCH_DIR}"
echo ""

apply_patch() {
    local patch_file="$1"
    local name
    name="$(basename "${patch_file}")"

    # Skip non-.patch files and subdirectory patches (handled separately)
    if [[ ! "${patch_file}" == *.patch ]]; then
        return 0
    fi

    echo "--- ${name}"

    # Extract target path(s) from patch header to detect missing targets
    local target
    target="$(grep -m1 "^+++ b/" "${patch_file}" | sed 's|^+++ b/||')"
    if [[ -n "${target}" ]] && [[ ! -f "${REPO_ROOT}/${target}" ]]; then
        echo "    [SKIP] target not present locally: ${target} (apply in container)"
        return 0
    fi

    # Check if already applied
    if git -C "${REPO_ROOT}" apply --check --reverse "${patch_file}" 2>/dev/null; then
        echo "    [SKIP] already applied"
        return 0
    fi

    # Check if it can be applied cleanly
    if ! git -C "${REPO_ROOT}" apply --check "${patch_file}" 2>/dev/null; then
        echo "    [FAIL] cannot apply (conflict or unexpected state)"
        FAILED=$((FAILED + 1))
        return 1
    fi

    if [[ "${DRY_RUN}" == "true" ]]; then
        echo "    [DRY-RUN] would apply"
        return 0
    fi

    git -C "${REPO_ROOT}" apply "${patch_file}"
    echo "    [APPLIED] ✅"
}

# Apply all top-level patches in deterministic order
while IFS= read -r -d '' patch_file; do
    apply_patch "${patch_file}" || true
done < <(find "${PATCH_DIR}" -maxdepth 1 -name "*.patch" -print0 | sort -z)

echo ""
if [[ "${FAILED}" -gt 0 ]]; then
    echo "[apply_runtime_patches] ❌ ${FAILED} patch(es) failed"
    exit 1
else
    echo "[apply_runtime_patches] ✅ all patches applied"
    exit 0
fi
