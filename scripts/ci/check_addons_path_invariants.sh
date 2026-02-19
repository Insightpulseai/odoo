#!/usr/bin/env bash
# check_addons_path_invariants.sh — fail if /mnt/extra-addons bleeds into devcontainer config
set -euo pipefail
FAIL=0

# Only check runtime configuration files (not docs, archives, etc.)
CHECK_PATTERNS=(
    ".devcontainer/*.yml"
    ".devcontainer/*.yaml"
    ".devcontainer/docker-compose*.yml"
)

# Exceptions (production configs that legitimately use /mnt/extra-addons)
EXCEPTIONS=("docker-compose.yml" "config/dev/odoo.conf" "config/prod/odoo.conf" "config/stage/odoo.conf")

for pattern in "${CHECK_PATTERNS[@]}"; do
    while IFS= read -r file; do
        [[ -z "$file" ]] && continue
        skip=0
        for exc in "${EXCEPTIONS[@]}"; do
            [[ "$file" == *"$exc" ]] && skip=1 && break
        done
        [[ "$skip" == "1" ]] && continue
        if grep -q "/mnt/extra-addons" "$file" 2>/dev/null; then
            echo "FAIL: /mnt/extra-addons found in $file"
            FAIL=1
        fi
    done < <(git ls-files "$pattern" 2>/dev/null || true)
done

DC=".devcontainer/docker-compose.devcontainer.yml"
if [[ -f "$DC" ]]; then
    grep -q "working_dir: /workspaces/odoo" "$DC" || {
        echo "FAIL: working_dir missing from $DC"; FAIL=1; }
    grep -q "/mnt/extra-addons" "$DC" && {
        echo "FAIL: /mnt/extra-addons still in devcontainer overlay"; FAIL=1; }
fi

[[ "$FAIL" -eq 0 ]] && echo "OK: All addons path invariants satisfied"
exit "$FAIL"
