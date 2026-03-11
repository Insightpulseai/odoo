#!/bin/bash
# Branch Cleanup Script for odoo-ce repository
# Generated: 2025-12-04
# Based on decision rules for branch management

set -e

echo "=== Git Branch Cleanup Script ==="
echo ""

# Sync and prune remotes first
echo "Fetching and pruning remote branches..."
git fetch --all --prune 2>/dev/null

echo ""
echo "=== BRANCHES TO DELETE (fully merged or abandoned) ==="
echo ""

# Fully merged branches (safe to delete)
MERGED_BRANCHES=(
    "feat/odoo-18-oca-automation"  # 0 commits ahead of main - FULLY MERGED
)

# Old AI/tool branches (claude/*, codex/*) - single-task branches older than 7 days
# These have session IDs and are typically abandoned after the task is complete
OLD_AI_BRANCHES=(
    "claude/add-semantic-query-layer-01TFMbP98TsY3aCJrw5rsvB2"
    "claude/create-bir-deadline-model-01EBd9CozQSQqZdz8xeATaxk"
    "claude/fix-odoo-oca-ci-01AswGq9t1gQtMbzjJ996Ghr"
    "claude/fix-rpc-module-error-01WCacwV8wHVbBTYECYpdH2P"
    "claude/fix-todo-miexvtcs0fh5do8s-01MrGQtkFRRGd5qkho4PwGGV"
    "claude/fix-website-template-error-01L8EJKkeQQgmNp1CAuiK4s7"
    "claude/fix-website-template-error-01RdtPGjnHdApCZFsE2ab7A8"
    "claude/odoo-docker-ppm-01UpNvSzuqpacs56TK3JiEWV"
    "claude/odoo-docker-setup-01M8UjzLJWtyZeS9AFUnrQjQ"
    "claude/plan-odoo-feature-01QiTF2ikgkYUUbCYajaDgMD"
    "claude/refactor-claude-sqlite-view-01TyJSiSvAmFgjJjM83zVDpS"
    "claude/vibe-coding-guide-01XykKpzur1NeeRREYww5Eee"
    "codex/define-success-criteria-for-doks-deployment"
    "codex/fix-codex-task-branch-configuration"
    "codex/implement-ipai_ppm_advanced-module-in-odoo"
    "codex/remove-deprecated-numbercall-field-from-xml"
    "pr-35"
)

echo "Merged branches:"
for branch in "${MERGED_BRANCHES[@]}"; do
    echo "  - $branch (fully merged)"
done

echo ""
echo "Old AI/tool branches (abandoned):"
for branch in "${OLD_AI_BRANCHES[@]}"; do
    echo "  - $branch"
done

echo ""
echo "=== BRANCHES TO KEEP ==="
echo ""

# Branches to keep (recent activity, important work, or uncertain)
KEEP_BRANCHES=(
    "main"                                                    # Default branch - NEVER DELETE
    "codex/fix-oca-architecture-compliance"                   # 2 days ago, 1 commit ahead (active)
    "feature/add-expense-equipment-prd"                       # 2 days ago (recent activity)
    "claude/fix-website-template-error-01KHFsoDtCE6MsDsjrXj8YuF"  # 17 hours ago (very recent)
    "chore/finalize-prod-readiness-v1"                        # Production readiness - may be important
    "chore/hardening-v1.1"                                    # Security hardening - may be important
    "feat-add-Odoo-18-CE/OCA-target-image-with-workspace-modules"  # Feature work
    "feature/finance-workflow-raci-stages"                    # Feature work
)

for branch in "${KEEP_BRANCHES[@]}"; do
    echo "  - $branch"
done

echo ""
echo "=== CLEANUP COMMANDS ==="
echo ""
echo "To delete merged branches, run:"
echo ""
for branch in "${MERGED_BRANCHES[@]}"; do
    echo "git push origin --delete $branch"
done

echo ""
echo "To delete old AI branches (after verifying no open PRs), run:"
echo ""
for branch in "${OLD_AI_BRANCHES[@]}"; do
    echo "git push origin --delete $branch"
done

echo ""
echo "=== DRY RUN MODE ==="
echo "This script only prints commands. To execute, copy and run the commands above."
echo ""
echo "Before deleting, verify no open PRs exist for these branches at:"
echo "https://github.com/jgtolentino/odoo-ce/pulls"
