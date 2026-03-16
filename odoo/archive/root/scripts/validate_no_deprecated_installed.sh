#!/usr/bin/env bash
# =============================================================================
# Validate No Deprecated Addons Referenced
# =============================================================================
# Ensures modules in addons/_deprecated/ are not referenced in:
#   - Install scripts
#   - CI workflows
#   - Docker compose env vars
#   - Active module manifests (depends)
#
# Usage:
#   ./scripts/validate_no_deprecated_installed.sh
#
# Exit Codes:
#   0 - No deprecated references found
#   1 - Deprecated module referenced somewhere
# =============================================================================
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DEPRECATED_DIR="${ROOT_DIR}/addons/_deprecated"
ERRORS=0

echo "== Deprecated Addons Validation =="
echo ""

# Collect deprecated module names
deprecated_modules=()
if [[ -d "${DEPRECATED_DIR}" ]]; then
  for d in "${DEPRECATED_DIR}"/*/; do
    if [[ -d "$d" ]]; then
      mod_name=$(basename "$d")
      if [[ "$mod_name" != ".gitkeep" && "$mod_name" != "." ]]; then
        deprecated_modules+=("$mod_name")
      fi
    fi
  done
fi

if [[ ${#deprecated_modules[@]} -eq 0 ]]; then
  echo "No deprecated modules found in addons/_deprecated/. Nothing to check."
  echo ""
  echo "== Validation Passed =="
  exit 0
fi

echo "Deprecated modules: ${deprecated_modules[*]}"
echo ""

# Search patterns: install scripts, CI workflows, compose files, active manifests
SEARCH_PATHS=(
  "${ROOT_DIR}/scripts"
  "${ROOT_DIR}/.github/workflows"
  "${ROOT_DIR}/docker-compose*.yml"
  "${ROOT_DIR}/infra"
)

for mod in "${deprecated_modules[@]}"; do
  echo "Checking references to: ${mod}"

  # Check install scripts and CI workflows
  for search_path in "${SEARCH_PATHS[@]}"; do
    if [[ -e "$search_path" ]]; then
      matches=$(grep -rl "${mod}" "$search_path" 2>/dev/null || true)
      if [[ -n "$matches" ]]; then
        echo "  ERROR: ${mod} referenced in:"
        echo "$matches" | sed 's/^/    /'
        ERRORS=$((ERRORS + 1))
      fi
    fi
  done

  # Check active module manifests for depends on deprecated module
  while IFS= read -r manifest; do
    # Skip manifests inside _deprecated itself
    if [[ "$manifest" == *"_deprecated"* ]]; then
      continue
    fi
    if grep -q "'${mod}'" "$manifest" 2>/dev/null || grep -q "\"${mod}\"" "$manifest" 2>/dev/null; then
      echo "  ERROR: ${mod} listed as dependency in ${manifest}"
      ERRORS=$((ERRORS + 1))
    fi
  done < <(find "${ROOT_DIR}/addons" -name "__manifest__.py" -not -path "*/_deprecated/*" 2>/dev/null)

done

echo ""
echo "----------------------------------------"
if [[ $ERRORS -gt 0 ]]; then
  echo "FAILED: ${ERRORS} deprecated module reference(s) found."
  echo "Remove references or move modules out of addons/_deprecated/."
  exit 1
else
  echo "PASSED: No deprecated module references found."
fi
echo "----------------------------------------"
