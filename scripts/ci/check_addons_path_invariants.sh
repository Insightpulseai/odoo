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
            line=$(grep -n "/mnt/extra-addons" "$file" | head -1)
            echo "FAIL[AP-03]: /mnt/extra-addons reference in devcontainer config: $file"
            echo "  Line: $line"
            FAIL=1
        fi
    done < <(git ls-files "$pattern" 2>/dev/null || true)
done

DC=".devcontainer/docker-compose.devcontainer.yml"
if [[ -f "$DC" ]]; then
    if ! grep -q "working_dir: /workspaces/odoo" "$DC"; then
        echo "FAIL[AP-01]: working_dir must be /workspaces/odoo in $DC"
        FAIL=1
    fi
    if grep -q "/mnt/extra-addons" "$DC"; then
        line=$(grep -n "/mnt/extra-addons" "$DC" | head -1)
        echo "FAIL[AP-02]: devcontainer must not mount /mnt/extra-addons: $DC"
        echo "  Line: $line"
        FAIL=1
    fi
fi

[[ "$FAIL" -eq 0 ]] && echo "✅ OK: All addons path invariants satisfied"
exit "$FAIL"
