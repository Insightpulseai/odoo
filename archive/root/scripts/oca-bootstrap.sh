#!/usr/bin/env bash
# ============================================================================
# oca-bootstrap.sh - Clone essential OCA repositories for Odoo CE
# ============================================================================
# Clones OCA repos needed for "Enterprise replacement" features:
# - queue (queue_job for async processing)
# - rest-framework (base_rest for API endpoints)
# - server-ux (base_tier_validation for approvals)
# - server-tools (iap_alternative_provider)
# - web (web_responsive for better UX)
#
# Usage:
#   ./scripts/oca-bootstrap.sh
#
# ============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
OCA_DIR="${REPO_ROOT}/addons/oca"

# OCA repos to clone (essential for "Enterprise replacement")
REPOS=(
    "queue"
    "rest-framework"
    "server-ux"
    "server-tools"
    "web"
)

# Try branches in order of preference
BRANCHES=("18.0" "17.0" "16.0" "main")

echo "=== OCA Repository Bootstrap ==="
echo "Target directory: ${OCA_DIR}"
echo ""

mkdir -p "${OCA_DIR}"
cd "${OCA_DIR}"

clone_repo() {
    local repo="$1"
    local repo_dir="${OCA_DIR}/${repo}"

    if [ -d "${repo_dir}" ] && [ -d "${repo_dir}/.git" ]; then
        echo "[SKIP] ${repo} already exists"
        return 0
    fi

    echo "[CLONE] OCA/${repo}..."

    for branch in "${BRANCHES[@]}"; do
        if git clone --depth 1 -b "${branch}" "https://github.com/OCA/${repo}.git" "${repo_dir}" 2>/dev/null; then
            echo "  -> cloned branch ${branch}"
            return 0
        fi
    done

    echo "  [WARN] Failed to clone ${repo} - check if repo exists"
    return 1
}

# Clone each repo
for repo in "${REPOS[@]}"; do
    clone_repo "${repo}" || true
done

echo ""
echo "=== Bootstrap Complete ==="
echo ""
echo "Essential modules to install (in order):"
echo "  1. queue_job (from oca/queue)"
echo "  2. base_rest (from oca/rest-framework)"
echo "  3. base_tier_validation (from oca/server-ux)"
echo "  4. web_responsive (from oca/web) [optional but recommended]"
echo ""
echo "Optional: iap_alternative_provider (from oca/server-tools)"
echo ""
echo "Next steps:"
echo "  1. Restart Odoo to detect new addons"
echo "  2. Go to Apps -> Update Apps List"
echo "  3. Install modules in order listed above"
echo ""
