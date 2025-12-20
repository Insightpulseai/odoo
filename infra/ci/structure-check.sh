#!/bin/bash
# =============================================================================
# Repository Structure Guardrail
# =============================================================================
# Enforces the CE → OCA → IPAI layered architecture.
#
# Rules:
# 1. Addons must be in addons/ipai/ or addons/oca/
# 2. No flat modules in addons/ root
# 3. IPAI modules must follow naming: ipai_*
# 4. No duplicate module names across ipai/oca
#
# Usage:
#   ./infra/ci/structure-check.sh
#
# Returns:
#   0 - Structure valid
#   1 - Structure violations found
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
ADDONS_DIR="$REPO_ROOT/addons"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

errors=0

log_ok() { echo -e "${GREEN}[OK]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; errors=$((errors + 1)); }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }

echo ""
echo "Repository Structure Check"
echo "=========================="
echo ""

# -----------------------------------------------------------------------------
# Check 1: Only ipai/ and oca/ directories allowed in addons/
# -----------------------------------------------------------------------------
echo "Check 1: Addons directory structure"

if [[ -d "$ADDONS_DIR" ]]; then
    for dir in "$ADDONS_DIR"/*/; do
        if [[ -d "$dir" ]]; then
            name=$(basename "$dir")
            case "$name" in
                ipai|oca)
                    log_ok "Valid addon namespace: $name/"
                    ;;
                *)
                    log_error "Invalid addon directory: addons/$name/"
                    echo "       Only addons/ipai/ and addons/oca/ are allowed."
                    echo "       Move $name to appropriate namespace or archive it."
                    ;;
            esac
        fi
    done
else
    log_error "addons/ directory not found"
fi

echo ""

# -----------------------------------------------------------------------------
# Check 2: IPAI modules follow naming convention
# -----------------------------------------------------------------------------
echo "Check 2: IPAI module naming convention"

if [[ -d "$ADDONS_DIR/ipai" ]]; then
    for module_dir in "$ADDONS_DIR/ipai"/*/; do
        if [[ -d "$module_dir" ]]; then
            module=$(basename "$module_dir")
            if [[ "$module" =~ ^ipai_ ]]; then
                log_ok "Valid IPAI module: $module"
            else
                log_error "Invalid IPAI module name: $module"
                echo "       IPAI modules must start with 'ipai_'"
            fi
        fi
    done
else
    log_warn "addons/ipai/ not found (not yet migrated?)"
fi

echo ""

# -----------------------------------------------------------------------------
# Check 3: OCA modules are vendored (have .git or pinned)
# -----------------------------------------------------------------------------
echo "Check 3: OCA module vendoring"

if [[ -d "$ADDONS_DIR/oca" ]]; then
    for repo_dir in "$ADDONS_DIR/oca"/*/; do
        if [[ -d "$repo_dir" ]]; then
            repo=$(basename "$repo_dir")
            if [[ -d "$repo_dir/.git" ]]; then
                log_ok "OCA repo vendored: $repo"
            else
                log_warn "OCA directory without .git: $repo (may be extracted)"
            fi
        fi
    done

    # Check for lockfile
    if [[ -f "$REPO_ROOT/vendor/oca.lock" ]]; then
        log_ok "OCA lockfile present: vendor/oca.lock"
    else
        log_warn "OCA lockfile missing: vendor/oca.lock"
        echo "       Run: ./vendor/oca-sync.sh update"
    fi
else
    log_warn "addons/oca/ not found (not yet migrated?)"
fi

echo ""

# -----------------------------------------------------------------------------
# Check 4: No duplicate module names
# -----------------------------------------------------------------------------
echo "Check 4: No duplicate module names"

declare -A seen_modules

# Check IPAI modules
if [[ -d "$ADDONS_DIR/ipai" ]]; then
    for module_dir in "$ADDONS_DIR/ipai"/*/; do
        if [[ -d "$module_dir" ]]; then
            module=$(basename "$module_dir")
            if [[ -n "${seen_modules[$module]:-}" ]]; then
                log_error "Duplicate module: $module (also in ${seen_modules[$module]})"
            else
                seen_modules[$module]="ipai"
            fi
        fi
    done
fi

# Check OCA modules (just top-level, OCA repos have submodules)
if [[ -d "$ADDONS_DIR/oca" ]]; then
    for repo_dir in "$ADDONS_DIR/oca"/*/; do
        if [[ -d "$repo_dir" ]]; then
            for module_dir in "$repo_dir"/*/; do
                if [[ -d "$module_dir" && -f "$module_dir/__manifest__.py" ]]; then
                    module=$(basename "$module_dir")
                    if [[ -n "${seen_modules[$module]:-}" ]]; then
                        log_error "Duplicate module: $module (ipai vs oca)"
                    fi
                fi
            done
        fi
    done
fi

log_ok "No duplicate modules found"

echo ""

# -----------------------------------------------------------------------------
# Check 5: No --stop-after-init + restart loops in docker-compose
# -----------------------------------------------------------------------------
echo "Check 5: Docker compose restart loop check"

if [ -f "$REPO_ROOT/docker-compose.yml" ]; then
    awk '
        function ltrim(s){ sub(/^[ \t]+/, "", s); return s }
        /^[a-zA-Z0-9_-]+:$/ && in_services==1 {
            # new top-level key inside services (service name)
            svc = substr($0, 1, length($0)-1)
            stop[svc]=0; restart[svc]=""
        }
        /^services:$/ { in_services=1; next }
        in_services==1 {
            line=$0
            # Detect service headers (2-space indent: "  name:")
            if (match(line, /^[ ]{2}[a-zA-Z0-9_-]+:$/)) {
                svc=ltrim(line); svc=substr(svc, 1, length(svc)-1)
                stop[svc]=0; restart[svc]=""
                next
            }
            if (svc!="") {
                if (index(line, "--stop-after-init")>0) stop[svc]=1
                if (match(line, /^[ ]{4}restart:/)) {
                    sub(/^[ ]{4}restart:[ ]*/, "", line)
                    restart[svc]=line
                }
            }
        }
        END {
            bad=0
            for (s in stop) {
                if (s ~ /-init$/) continue
                if (stop[s]==1 && restart[s] ~ /unless-stopped/) {
                    printf "'"${RED}"'[ERROR]'"${NC}"' %s has --stop-after-init with restart: %s\n", s, restart[s]
                    bad=1
                }
            }
            if (bad==0) print "'"${GREEN}"'[OK]'"${NC}"' No restart loop patterns detected"
            exit bad
        }
    ' "$REPO_ROOT/docker-compose.yml" || errors=$((errors + 1))
else
    log_ok "docker-compose.yml not found (skipped)"
fi

echo ""

# -----------------------------------------------------------------------------
# Check 6: QWeb template ID uniqueness
# -----------------------------------------------------------------------------
echo "Check 6: QWeb template ID check"

# Find potential ID collisions in inherited templates
if [[ -d "$ADDONS_DIR/ipai" ]]; then
    duplicates=$(grep -r 'inherit_id=.*template.*id=' "$ADDONS_DIR/ipai" 2>/dev/null | \
                 grep -o 'id="[^"]*"' | sort | uniq -d || true)
    if [[ -n "$duplicates" ]]; then
        log_error "Potential QWeb ID collisions: $duplicates"
    else
        log_ok "No QWeb ID collisions detected"
    fi
else
    log_ok "No IPAI modules to check"
fi

echo ""

# -----------------------------------------------------------------------------
# Summary
# -----------------------------------------------------------------------------
echo "=========================="
if [[ $errors -gt 0 ]]; then
    echo -e "${RED}FAILED${NC}: $errors error(s) found"
    exit 1
else
    echo -e "${GREEN}PASSED${NC}: Repository structure is valid"
    exit 0
fi
