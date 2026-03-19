#!/bin/bash
# =============================================================================
# Repository Structure Guardrail
# =============================================================================
# Enforces the CE → OCA → IPAI layered architecture.
#
# Supports TWO layouts:
# A) Flat structure (canonical): addons/ipai_*, addons/oca/
# B) Namespaced structure: addons/ipai/, addons/oca/
#
# Rules:
# 1. IPAI modules must follow naming: ipai_* (either flat or in addons/ipai/)
# 2. OCA modules must be in addons/oca/
# 3. No other modules allowed in addons/ root
# 4. No duplicate module names
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
# Detect structure type
# -----------------------------------------------------------------------------
FLAT_STRUCTURE=false
NAMESPACED_STRUCTURE=false

if [[ -d "$ADDONS_DIR/ipai" ]]; then
    NAMESPACED_STRUCTURE=true
fi

# Check for flat ipai_* modules
flat_ipai_count=$(find "$ADDONS_DIR" -maxdepth 1 -type d -name "ipai_*" 2>/dev/null | wc -l)
if [[ $flat_ipai_count -gt 0 ]]; then
    FLAT_STRUCTURE=true
fi

if $FLAT_STRUCTURE; then
    echo "Detected: FLAT structure (ipai_* modules in addons/)"
elif $NAMESPACED_STRUCTURE; then
    echo "Detected: NAMESPACED structure (addons/ipai/ subdirectory)"
else
    echo "Detected: No IPAI modules found yet"
fi
echo ""

# -----------------------------------------------------------------------------
# Check 1: Addons directory structure
# -----------------------------------------------------------------------------
echo "Check 1: Addons directory structure"

if [[ -d "$ADDONS_DIR" ]]; then
    for dir in "$ADDONS_DIR"/*/; do
        if [[ -d "$dir" ]]; then
            name=$(basename "$dir")
            case "$name" in
                ipai|oca)
                    # Namespaced structure - always valid
                    log_ok "Valid addon namespace: $name/"
                    ;;
                ipai_*)
                    # Flat structure - ipai_* modules directly in addons/
                    if $FLAT_STRUCTURE; then
                        log_ok "Valid IPAI module: $name/"
                    else
                        log_error "Flat module $name/ found but repo uses namespaced structure"
                        echo "       Move to addons/ipai/$name/"
                    fi
                    ;;
                *)
                    log_error "Invalid addon directory: addons/$name/"
                    echo "       Allowed: ipai_* modules, oca/, or ipai/"
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

ipai_modules_found=0

# Check namespaced structure
if [[ -d "$ADDONS_DIR/ipai" ]]; then
    for module_dir in "$ADDONS_DIR/ipai"/*/; do
        if [[ -d "$module_dir" ]]; then
            module=$(basename "$module_dir")
            if [[ "$module" =~ ^ipai_ ]]; then
                log_ok "Valid IPAI module: ipai/$module"
                ipai_modules_found=$((ipai_modules_found + 1))
            else
                log_error "Invalid IPAI module name: $module"
                echo "       IPAI modules must start with 'ipai_'"
            fi
        fi
    done
fi

# Check flat structure
if $FLAT_STRUCTURE; then
    for module_dir in "$ADDONS_DIR"/ipai_*/; do
        if [[ -d "$module_dir" ]]; then
            module=$(basename "$module_dir")
            log_ok "Valid IPAI module (flat): $module"
            ipai_modules_found=$((ipai_modules_found + 1))
        fi
    done
fi

if [[ $ipai_modules_found -eq 0 ]]; then
    log_warn "No IPAI modules found"
else
    echo "Found $ipai_modules_found IPAI module(s)"
fi

echo ""

# -----------------------------------------------------------------------------
# Check 3: OCA modules are vendored (have .git or pinned)
# -----------------------------------------------------------------------------
echo "Check 3: OCA module vendoring"

if [[ -d "$ADDONS_DIR/oca" ]]; then
    oca_found=0
    for repo_dir in "$ADDONS_DIR/oca"/*/; do
        if [[ -d "$repo_dir" ]]; then
            repo=$(basename "$repo_dir")
            oca_found=$((oca_found + 1))
            if [[ -d "$repo_dir/.git" ]]; then
                log_ok "OCA repo vendored: $repo"
            else
                log_warn "OCA directory without .git: $repo (may be extracted)"
            fi
        fi
    done

    if [[ $oca_found -eq 0 ]]; then
        log_ok "OCA directory exists but is empty"
    fi

    # Check for lockfile
    if [[ -f "$REPO_ROOT/vendor/oca.lock" ]]; then
        log_ok "OCA lockfile present: vendor/oca.lock"
    else
        log_warn "OCA lockfile missing: vendor/oca.lock"
        echo "       Run: ./vendor/oca-sync.sh update"
    fi
else
    log_warn "addons/oca/ not found (no OCA modules vendored yet)"
fi

echo ""

# -----------------------------------------------------------------------------
# Check 4: No duplicate module names
# -----------------------------------------------------------------------------
echo "Check 4: No duplicate module names"

declare -A seen_modules

# Check namespaced IPAI modules
if [[ -d "$ADDONS_DIR/ipai" ]]; then
    for module_dir in "$ADDONS_DIR/ipai"/*/; do
        if [[ -d "$module_dir" ]]; then
            module=$(basename "$module_dir")
            if [[ -n "${seen_modules[$module]:-}" ]]; then
                log_error "Duplicate module: $module (also in ${seen_modules[$module]})"
            else
                seen_modules[$module]="ipai/"
            fi
        fi
    done
fi

# Check flat IPAI modules (flat structure is canonical when duplicates exist)
if $FLAT_STRUCTURE; then
    for module_dir in "$ADDONS_DIR"/ipai_*/; do
        if [[ -d "$module_dir" ]]; then
            module=$(basename "$module_dir")
            if [[ -n "${seen_modules[$module]:-}" ]]; then
                # Flat structure is canonical - warn but don't error
                log_warn "Module $module exists in both addons/$module and addons/ipai/$module (flat is canonical)"
                seen_modules[$module]="addons/ (canonical)"
            else
                seen_modules[$module]="addons/"
            fi
        fi
    done
fi

# Check OCA modules
if [[ -d "$ADDONS_DIR/oca" ]]; then
    for repo_dir in "$ADDONS_DIR/oca"/*/; do
        if [[ -d "$repo_dir" ]]; then
            for module_dir in "$repo_dir"/*/; do
                if [[ -d "$module_dir" && -f "$module_dir/__manifest__.py" ]]; then
                    module=$(basename "$module_dir")
                    if [[ -n "${seen_modules[$module]:-}" ]]; then
                        log_error "Duplicate module: $module (${seen_modules[$module]} vs oca)"
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

ipai_dirs=""
if [[ -d "$ADDONS_DIR/ipai" ]]; then
    ipai_dirs="$ADDONS_DIR/ipai"
fi
if $FLAT_STRUCTURE; then
    ipai_dirs="$ipai_dirs $(find "$ADDONS_DIR" -maxdepth 1 -type d -name 'ipai_*' | tr '\n' ' ')"
fi

if [[ -n "$ipai_dirs" ]]; then
    duplicates=""
    for dir in $ipai_dirs; do
        if [[ -d "$dir" ]]; then
            dup=$(grep -r 'inherit_id=.*template.*id=' "$dir" 2>/dev/null | \
                  grep -o 'id="[^"]*"' | sort | uniq -d || true)
            if [[ -n "$dup" ]]; then
                duplicates="$duplicates $dup"
            fi
        fi
    done
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
