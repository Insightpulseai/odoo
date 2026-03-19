#!/usr/bin/env bash
# check_odoo_addons_path.sh — fail if any odoo.conf addons_path references addons/oca/repos
# Policy: Only addons/oca/selected (symlink allowlist) is permitted in addons_path.
#         addons/oca/repos contains submodules and must NEVER be in addons_path.
# Complements: check_addons_path_invariants.sh (which handles devcontainer/mount hygiene)
set -euo pipefail

ROOT="${ROOT:-.}"
FAIL=0

echo "[policy] Checking Odoo config files for forbidden addons_path entries (addons/oca/repos)..."

# Find all tracked .conf files that contain addons_path
mapfile -t conf_files < <(
  git -C "$ROOT" ls-files '*.conf' 2>/dev/null \
    | while IFS= read -r f; do
        grep -l 'addons_path' "$ROOT/$f" 2>/dev/null && true
      done || true
)

# Also check .cfg files
mapfile -t cfg_files < <(
  git -C "$ROOT" ls-files '*.cfg' 2>/dev/null \
    | while IFS= read -r f; do
        grep -l 'addons_path' "$ROOT/$f" 2>/dev/null && true
      done || true
)

all_files=("${conf_files[@]:-}" "${cfg_files[@]:-}")

if [[ ${#all_files[@]} -eq 0 ]]; then
  echo "[policy] No .conf/.cfg files with addons_path found via git ls-files. Skipping."
  exit 0
fi

for f in "${all_files[@]}"; do
  [[ -z "$f" ]] && continue

  rel_path="${f#$ROOT/}"
  rel_path="${rel_path#./}"

  # Hard fail: addons/oca/repos (repo-relative path) in an addons_path line
  if grep -n 'addons_path' "$f" | grep -qE 'addons/oca/repos|addons\\oca\\repos'; then
    lineno=$(grep -n 'addons_path' "$f" | grep -E 'addons/oca/repos|addons\\oca\\repos' | head -1 | cut -d: -f1)
    echo "::error file=${rel_path},line=${lineno}::Forbidden: addons_path references addons/oca/repos. Use addons/oca/selected (symlink allowlist) only."
    FAIL=1
  fi

  # Soft warning: addons/oca present but not via /mnt mount AND not via selected
  # Docker mount paths like /mnt/oca are fine — only repo-relative paths need selected
  if grep -n 'addons_path' "$f" | grep -qE '[^/]addons/oca[^/]|[^/]addons/oca$'; then
    if ! grep -n 'addons_path' "$f" | grep -qE 'addons/oca/selected'; then
      echo "::warning file=${rel_path}::addons_path references addons/oca without addons/oca/selected. Verify only selected/ is used (Docker mounts at /mnt/oca are OK)."
    fi
  fi
done

if [[ "$FAIL" -ne 0 ]]; then
  echo "[policy] FAILED: addons_path policy violated. See errors above."
  exit 1
fi

echo "[policy] OK: All addons_path entries satisfy the selected-only policy."
