#!/usr/bin/env bash
# apply_vendor_patches.sh — Apply repo-owned patches to vendor Python packages.
#
# Idempotent: already-applied patches are detected and skipped.
# Uses Python to locate site-packages paths reliably across venv/system layouts.
# Does NOT rely on sed, git apply, or hardcoded paths.
#
# Usage:
#   /usr/local/bin/apply_vendor_patches.sh
#
# Environment:
#   VENDOR_PATCHES_DIR   Directory containing patch scripts (default: /opt/vendor-patches)
#   DRY_RUN              Set to "1" to print actions without applying (default: 0)

set -euo pipefail

PATCHES_DIR="${VENDOR_PATCHES_DIR:-/opt/vendor-patches}"
DRY_RUN="${DRY_RUN:-0}"

log()  { echo "[vendor-patch] $*"; }
warn() { echo "[vendor-patch] WARN: $*" >&2; }
die()  { echo "[vendor-patch] ERROR: $*" >&2; exit 1; }

# ---------------------------------------------------------------------------
# Patch: odoo-test-helper / fake_model_loader.py
#
# Problem: MetaModel.module_to_models renamed to _module_to_models__ in Odoo 19.
# The published odoo-test-helper still accesses the old attribute; crashes at
# import time and blocks the whole test runner.
#
# Fix: replace the direct attribute access with a getattr fallback.
#
# Idempotency marker: presence of "_module_to_models__" in the file body.
# ---------------------------------------------------------------------------
patch_odoo_test_helper() {
    local target
    target="$(python3 - <<'PY'
import site, os, glob, sys

candidates = []
for base in (site.getsitepackages() or []) + [site.getusersitepackages() or ""]:
    if base and os.path.isdir(base):
        p = os.path.join(base, "odoo_test_helper", "fake_model_loader.py")
        if os.path.exists(p):
            candidates.append(p)

# Fallback: filesystem search (slower, comprehensive)
if not candidates:
    for p in glob.glob("/**/odoo_test_helper/fake_model_loader.py", recursive=True):
        if os.path.exists(p):
            candidates.append(p)

print(candidates[0] if candidates else "")
PY
)"

    if [[ -z "${target}" ]]; then
        warn "odoo_test_helper/fake_model_loader.py not found; skipping patch."
        warn "Install odoo-test-helper first: pip install odoo-test-helper"
        return 0
    fi

    log "target: ${target}"

    # Idempotency check: patch already applied?
    if grep -q "_module_to_models__" "${target}" 2>/dev/null; then
        log "already patched: $(basename "${target}") — skipping"
        return 0
    fi

    # Verify the old attribute access is still present (sanity check)
    if ! grep -q "module_to_models = models.MetaModel.module_to_models" "${target}" 2>/dev/null; then
        warn "Expected pattern not found in ${target}."
        warn "odoo-test-helper may have been updated upstream. Review the patch."
        warn "Continuing without patching — tests may fail."
        return 0
    fi

    if [[ "${DRY_RUN}" == "1" ]]; then
        log "DRY_RUN: would patch ${target}"
        return 0
    fi

    # Apply the patch via Python (no sed, no git, no external tools needed)
    python3 - "${target}" <<'PY'
import sys, re, pathlib

path = pathlib.Path(sys.argv[1])
content = path.read_text(encoding="utf-8")

OLD = "module_to_models = models.MetaModel.module_to_models"
NEW = (
    "# Odoo 19: MetaModel.module_to_models was renamed to _module_to_models__.\n"
    "# Patched by: runtime/scripts/apply_vendor_patches.sh\n"
    "_module_to_models = (\n"
    "    getattr(models.MetaModel, \"module_to_models\", None)\n"
    "    or getattr(models.MetaModel, \"_module_to_models__\", {})\n"
    ")\n"
    "module_to_models = _module_to_models"
)

if OLD not in content:
    print(f"[vendor-patch] ERROR: OLD pattern not found in {path}", file=sys.stderr)
    sys.exit(1)

patched = content.replace(OLD, NEW, 1)
path.write_text(patched, encoding="utf-8")
print(f"[vendor-patch] OK patched: {path}")
PY
}

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
log "Applying vendor patches from: ${PATCHES_DIR}"
log "DRY_RUN=${DRY_RUN}"
echo ""

patch_odoo_test_helper

echo ""
log "Vendor patch application complete."
