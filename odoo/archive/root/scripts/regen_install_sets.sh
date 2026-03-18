#!/usr/bin/env bash
# =============================================================================
# Regenerate all curated install sets from addons roots + allow-lists.
#
# Runs gen_install_set.py for each feature set (PPM, DMS, Helpdesk, OCR),
# then union_prune_install_sets.py for the mega set.
#
# Environment overrides (for CI or local):
#   OCA_ROOTS   - space-separated list of OCA addon roots
#   CUSTOM_ROOT - IPAI custom addons root
# =============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_ROOT"

# Default roots: host-side repo paths
# In CI or local, these point to repo directories.
# In container, override to /mnt/extra-addons/oca etc.
OCA_ROOTS="${OCA_ROOTS:-vendor/oca vendor/oca/OCA external-src}"
CUSTOM_ROOT="${CUSTOM_ROOT:-addons/ipai addons}"
DENY_FILE="config/install_sets/deny_modules.txt"

GEN="python3 scripts/gen_install_set.py"
UNION="python3 scripts/union_prune_install_sets.py"

# Build --addons-root flags
ROOTS_FLAGS=""
for r in $OCA_ROOTS; do
    ROOTS_FLAGS="$ROOTS_FLAGS --addons-root $r"
done
for r in $CUSTOM_ROOT; do
    ROOTS_FLAGS="$ROOTS_FLAGS --addons-root $r"
done

gen_one() {
    local allow_file="$1"
    local out_file="$2"
    local header="$3"

    $GEN \
        $ROOTS_FLAGS \
        --allow-file "$allow_file" \
        --deny-file "$DENY_FILE" \
        --expand-deps \
        --include-core \
        --comment-header "$header" \
        --out "$out_file"
}

mkdir -p config/install_sets

echo "=== Regenerating individual install sets ==="

gen_one "config/install_sets/allow_modules_ppm.txt" \
        "config/install_sets/ppm_parity_autogen.txt" \
        "AUTO-GENERATED INSTALL SET: PPM"

gen_one "config/install_sets/allow_modules_dms.txt" \
        "config/install_sets/dms_parity_autogen.txt" \
        "AUTO-GENERATED INSTALL SET: DMS"

gen_one "config/install_sets/allow_modules_helpdesk.txt" \
        "config/install_sets/helpdesk_parity_autogen.txt" \
        "AUTO-GENERATED INSTALL SET: HELPDESK"

gen_one "config/install_sets/allow_modules_ocr.txt" \
        "config/install_sets/ocr_parity_autogen.txt" \
        "AUTO-GENERATED INSTALL SET: OCR"

echo "=== Generating mega union set ==="

$UNION \
    --set config/install_sets/ppm_parity_autogen.txt \
    --set config/install_sets/dms_parity_autogen.txt \
    --set config/install_sets/helpdesk_parity_autogen.txt \
    --set config/install_sets/ocr_parity_autogen.txt \
    $ROOTS_FLAGS \
    --expand-deps \
    --stable-order \
    --out config/install_sets/mega_parity_autogen.txt \
    --comment-header "AUTO-GENERATED INSTALL SET: MEGA (PPM+DMS+HELPDESK+OCR)"

echo "=== All install sets regenerated ==="
