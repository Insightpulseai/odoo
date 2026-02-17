#!/usr/bin/env bash
# check_parity_boundaries.sh — CI gate enforcing EE-OCA parity directory boundaries.
#
# Rules enforced (from spec/ee-oca-parity/constitution.md):
#   PB-001: addons/oca/* must have __manifest__.py
#   PB-002: addons/ipai/* must have __manifest__.py
#   PB-003: addons/ipai/* must match ipai_* naming
#   PB-004: bridges/* must NOT have __manifest__.py
#   PB-005: addons/ipai/* >1000 LOC Python = warning
#   PB-006: addons/_deprecated/* excluded from checks
#   PB-007: addons/* subdirs (except oca/, ipai/, _deprecated/) must have __manifest__.py
#
# Exit codes: 0 = pass, 1 = fail (blocking), 2 = warnings only

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
ADDONS_DIR="$REPO_ROOT/addons"
BRIDGES_DIR="$REPO_ROOT/bridges"
SERVICES_DIR="$REPO_ROOT/services"

ERRORS=0
WARNINGS=0

error() { echo "  ERROR: $1"; ERRORS=$((ERRORS + 1)); }
warn()  { echo "  WARN:  $1"; WARNINGS=$((WARNINGS + 1)); }
pass()  { echo "  PASS:  $1"; }

echo "=== Parity Boundary Check ==="
echo ""

# ---------------------------------------------------------------------------
# PB-001: addons/oca/* must have __manifest__.py
# ---------------------------------------------------------------------------
echo "[PB-001] OCA addons must have __manifest__.py"
if [ -d "$ADDONS_DIR/oca" ]; then
    for dir in "$ADDONS_DIR/oca"/*/; do
        [ -d "$dir" ] || continue
        name=$(basename "$dir")
        # OCA repos contain multiple modules — check that at least ONE subdir
        # has __manifest__.py, or the dir itself does
        if [ -f "$dir/__manifest__.py" ]; then
            pass "addons/oca/$name has __manifest__.py"
        else
            has_submodule=false
            for subdir in "$dir"/*/; do
                [ -d "$subdir" ] || continue
                if [ -f "$subdir/__manifest__.py" ]; then
                    has_submodule=true
                    break
                fi
            done
            if $has_submodule; then
                pass "addons/oca/$name has submodules with __manifest__.py"
            else
                error "addons/oca/$name has no __manifest__.py (PB-001)"
            fi
        fi
    done
else
    echo "  (addons/oca/ does not exist yet — skipping)"
fi
echo ""

# ---------------------------------------------------------------------------
# PB-002 + PB-003: addons/ipai/* must have __manifest__.py and match ipai_*
# ---------------------------------------------------------------------------
echo "[PB-002] IPAI addons must have __manifest__.py"
echo "[PB-003] IPAI addons must match ipai_* naming"
if [ -d "$ADDONS_DIR/ipai" ]; then
    for dir in "$ADDONS_DIR/ipai"/*/; do
        [ -d "$dir" ] || continue
        name=$(basename "$dir")
        if [ ! -f "$dir/__manifest__.py" ]; then
            error "addons/ipai/$name has no __manifest__.py (PB-002)"
        fi
        if [[ ! "$name" =~ ^ipai_ ]]; then
            error "addons/ipai/$name does not match ipai_* naming (PB-003)"
        fi
    done
else
    echo "  (addons/ipai/ does not exist yet — skipping)"
fi

# Also check ipai_* modules at addons root level (current layout)
for dir in "$ADDONS_DIR"/ipai_*/; do
    [ -d "$dir" ] || continue
    name=$(basename "$dir")
    if [ ! -f "$dir/__manifest__.py" ]; then
        error "addons/$name has no __manifest__.py (PB-002)"
    else
        pass "addons/$name has __manifest__.py"
    fi
done
echo ""

# ---------------------------------------------------------------------------
# PB-004: bridges/* must NOT have __manifest__.py
# ---------------------------------------------------------------------------
echo "[PB-004] Bridges must NOT have __manifest__.py"
for bdir in "$BRIDGES_DIR" "$SERVICES_DIR"; do
    [ -d "$bdir" ] || continue
    bname=$(basename "$bdir")
    while IFS= read -r manifest; do
        rel="${manifest#$REPO_ROOT/}"
        error "$rel found in $bname/ — bridges must not be Odoo modules (PB-004)"
    done < <(find "$bdir" -name "__manifest__.py" -type f 2>/dev/null || true)
    if [ "$(find "$bdir" -name "__manifest__.py" -type f 2>/dev/null | wc -l)" -eq 0 ]; then
        pass "$bname/ has no __manifest__.py files"
    fi
done
echo ""

# ---------------------------------------------------------------------------
# PB-005: addons/ipai/* >1000 LOC Python = warning
# ---------------------------------------------------------------------------
echo "[PB-005] IPAI addons LOC check (<1000 Python LOC)"
for dir in "$ADDONS_DIR"/ipai_*/ "$ADDONS_DIR"/ipai/ipai_*/; do
    [ -d "$dir" ] || continue
    name=$(basename "$dir")
    loc=$(find "$dir" -name "*.py" -type f -exec cat {} + 2>/dev/null | wc -l || echo 0)
    if [ "$loc" -gt 1000 ]; then
        warn "addons/$name has ${loc} Python LOC (>1000, review needed) (PB-005)"
        if [ ! -f "$dir/PARITY_CONNECTOR_JUSTIFICATION.md" ]; then
            warn "addons/$name exceeds 1000 LOC and is missing PARITY_CONNECTOR_JUSTIFICATION.md (PB-005)"
        else
            pass "addons/$name has PARITY_CONNECTOR_JUSTIFICATION.md"
        fi
    else
        pass "addons/$name: ${loc} Python LOC"
    fi
done
echo ""

# ---------------------------------------------------------------------------
# PB-007: addons/* subdirs (except oca, ipai, _deprecated) must have __manifest__.py
# ---------------------------------------------------------------------------
echo "[PB-007] Other addons subdirs must have __manifest__.py"
EXEMPT_DIRS="oca|ipai|_deprecated|__pycache__"
for dir in "$ADDONS_DIR"/*/; do
    [ -d "$dir" ] || continue
    name=$(basename "$dir")
    # Skip exempt dirs and ipai_* (checked above)
    [[ "$name" =~ ^($EXEMPT_DIRS)$ ]] && continue
    [[ "$name" =~ ^ipai_ ]] && continue
    [[ "$name" =~ ^\.  ]] && continue
    if [ ! -f "$dir/__manifest__.py" ]; then
        warn "addons/$name has no __manifest__.py — not a valid Odoo module (PB-007)"
    fi
done
echo ""

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
echo "=== Summary ==="
echo "  Errors:   $ERRORS"
echo "  Warnings: $WARNINGS"
echo ""

if [ "$ERRORS" -gt 0 ]; then
    echo "FAIL — $ERRORS boundary violations found."
    exit 1
elif [ "$WARNINGS" -gt 0 ]; then
    echo "PASS (with $WARNINGS warnings)"
    exit 0
else
    echo "PASS — all parity boundaries respected."
    exit 0
fi
