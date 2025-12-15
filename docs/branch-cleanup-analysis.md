# Branch Cleanup Analysis

**Date:** 2025-12-04
**Repository:** jgtolentino/odoo-ce

## Summary

Analysis of 25 remote branches following the decision rules for branch management.

## Decision Rules Applied

1. **Default/long-lived branches** - Never delete (`main`)
2. **Fully merged branches** - Safe to delete
3. **Open PR or active work** - Keep
4. **Tool run/experiment branches** - Delete after PR merged/abandoned

## Branch Categories

### SAFE TO DELETE (1 branch)

| Branch | Commits Ahead | Last Activity | Reason |
|--------|--------------|---------------|--------|
| `feat/odoo-18-oca-automation` | 0 | 4 days | **Fully merged into main** |

### KEEP - Active Work (4 branches)

| Branch | Commits Ahead | Last Activity | Reason |
|--------|--------------|---------------|--------|
| `main` | - | - | Default branch |
| `codex/fix-oca-architecture-compliance` | 1 | 2 days | Active, minimal divergence |
| `feature/add-expense-equipment-prd` | 216 | 2 days | Recent activity |
| `claude/fix-website-template-error-01KHFsoDtCE6MsDsjrXj8YuF` | 124 | 17 hours | Very recent |

### KEEP - Review Needed (4 branches)

These are feature/chore branches that may contain important unmerged work:

| Branch | Commits Ahead | Last Activity | Notes |
|--------|--------------|---------------|-------|
| `chore/finalize-prod-readiness-v1` | 75 | 11 days | Production readiness work |
| `chore/hardening-v1.1` | 78 | 11 days | Security hardening |
| `feat-add-Odoo-18-CE/OCA-target-image-with-workspace-modules` | 128 | 7 days | Docker/image work |
| `feature/finance-workflow-raci-stages` | 135 | 7 days | Finance workflow |

### CANDIDATES FOR DELETION (17 branches)

Old AI/tool branches (claude/*, codex/*) with session IDs - likely abandoned single-task branches:

| Branch | Commits Ahead | Last Activity |
|--------|--------------|---------------|
| `claude/add-semantic-query-layer-01TFMbP98TsY3aCJrw5rsvB2` | 147 | 6 days |
| `claude/create-bir-deadline-model-01EBd9CozQSQqZdz8xeATaxk` | 174 | 6 days |
| `claude/fix-odoo-oca-ci-01AswGq9t1gQtMbzjJ996Ghr` | 69 | 11 days |
| `claude/fix-rpc-module-error-01WCacwV8wHVbBTYECYpdH2P` | 66 | 11 days |
| `claude/fix-todo-miexvtcs0fh5do8s-01MrGQtkFRRGd5qkho4PwGGV` | 123 | 9 days |
| `claude/fix-website-template-error-01L8EJKkeQQgmNp1CAuiK4s7` | 125 | 8 days |
| `claude/fix-website-template-error-01RdtPGjnHdApCZFsE2ab7A8` | 130 | 7 days |
| `claude/odoo-docker-ppm-01UpNvSzuqpacs56TK3JiEWV` | 115 | 9 days |
| `claude/odoo-docker-setup-01M8UjzLJWtyZeS9AFUnrQjQ` | 143 | 6 days |
| `claude/plan-odoo-feature-01QiTF2ikgkYUUbCYajaDgMD` | 114 | 9 days |
| `claude/refactor-claude-sqlite-view-01TyJSiSvAmFgjJjM83zVDpS` | 65 | 11 days |
| `claude/vibe-coding-guide-01XykKpzur1NeeRREYww5Eee` | 48 | 11 days |
| `codex/define-success-criteria-for-doks-deployment` | 128 | 10 days |
| `codex/fix-codex-task-branch-configuration` | 96 | 11 days |
| `codex/implement-ipai_ppm_advanced-module-in-odoo` | 133 | 10 days |
| `codex/remove-deprecated-numbercall-field-from-xml` | 115 | 10 days |
| `pr-35` | 174 | 8 days |

## Recommended Actions

### Immediate (Safe)
```bash
# Delete fully merged branch
git push origin --delete feat/odoo-18-oca-automation
```

### After PR Verification
Before deleting the 17 candidate branches, verify no open PRs exist:
1. Check https://github.com/jgtolentino/odoo-ce/pulls
2. If no open PR for a branch, it's safe to delete

### For Archive (Optional)
If you want to preserve a reference to deleted branches:
```bash
# Create archive tag before deletion
git tag -a archive/<branch-name> origin/<branch-name> -m "Archived before cleanup"
git push origin archive/<branch-name>
```

## Notes

- High "commits ahead" counts indicate branches diverged from older main states
- Session ID suffixes (e.g., `01TFMbP98TsY3aCJrw5rsvB2`) identify AI tool runs
- Multiple branches with similar names (e.g., `fix-website-template-error-*`) are separate task attempts
