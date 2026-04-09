# Blast Radius Analysis: docs-sync-odoo-official.yml

**Analysis Date**: 2026-03-05T00:00+0800
**Workflow**: `.github/workflows/docs-sync-odoo-official.yml`
**Analyst**: Claude Code

---

## Current Sync Scope

### Target Directory
```
docs/odoo-official/
├── administration/
├── applications/
├── contributing/
└── developer/
```

### Sync Mechanism
- **Tool**: `rsync -av --delete --checksum`
- **Source**: `odoo/documentation:19.0` (GitHub)
- **Deletion**: `--delete` flag removes files not in source
- **Scope**: 4 directories, ~400-600 RST files (estimated)

---

## Identified Blast Radius Issues

### 1. **Wide-Scope Deletion Risk** ⚠️ CRITICAL

**Problem**: `rsync --delete` with no safeguards can remove large numbers of files if:
- Upstream repo changes structure
- Network interruption causes partial clone
- Git clone fails silently but rsync proceeds

**Example Failure Scenario**:
```bash
# If official-docs clone is empty or incomplete
rsync -av --delete --checksum \
  official-docs/content/administration/ \
  repo/docs/odoo-official/administration/
# → Deletes ALL administration docs
```

**Impact**: Loss of 100+ documentation files in a single job run.

---

### 2. **No Pre-Sync Validation** ⚠️ HIGH

**Problem**: Workflow does not validate upstream source before syncing:
- No file count check (e.g., "must have >100 files")
- No commit age check (e.g., "upstream updated within 7 days")
- No structural integrity check

**Failure Mode**: Syncs from corrupted/incomplete upstream state.

---

### 3. **Direct Main Branch Push** ⚠️ HIGH

**Problem**: Line 155 commits directly to `main` without PR review:
```yaml
git push origin main
```

**Impact**: Accidental wide-scope changes bypass review process.

---

### 4. **No Diff Size Gate** ⚠️ MEDIUM

**Problem**: No validation of change magnitude before commit:
- No check for "changes >50 files = suspicious"
- No alert if >1000 lines deleted
- No threshold for "unexpected large sync"

**Failure Mode**: Silent acceptance of catastrophic changes.

---

### 5. **Shared Namespace Pollution** ⚠️ MEDIUM

**Problem**: Synced docs live in main `docs/` tree, not isolated subtree:
```
docs/
├── odoo-official/     ← Synced (external)
├── architecture/      ← Local (internal)
├── ai/                ← Local (internal)
└── runbooks/          ← Local (internal)
```

**Risk**: Accidental cross-contamination if rsync path misconfigured.

---

### 6. **No Rollback Strategy** ⚠️ MEDIUM

**Problem**: If bad sync detected post-merge, no automated rollback:
- No tagged "last known good" state
- No revert automation
- Manual git revert required

**Impact**: Extended downtime if bad sync reaches production.

---

## Blast Radius Quantification

| Scenario | Files Affected | Severity |
|----------|----------------|----------|
| Empty upstream clone | ~400-600 (all docs) | CRITICAL |
| Partial upstream corruption | 50-200 | HIGH |
| Upstream restructure | 100-300 | HIGH |
| Network timeout mid-sync | 20-100 | MEDIUM |
| Single section failure | 50-150 | MEDIUM |

---

## Recommended Safeguards

### 1. **Vendor Subtree Isolation**
Move sync target to isolated vendor directory:
```
vendor/odoo-official-docs/
└── 19.0/
    ├── administration/
    ├── applications/
    ├── contributing/
    └── developer/
```

**Benefits**:
- Clear boundary: `vendor/` = external, `docs/` = internal
- No namespace collision risk
- Easy to `.gitignore` entire vendor tree if needed

### 2. **Pre-Sync Validation Gate**
Add checks before rsync:
```bash
# Validate upstream clone
FILE_COUNT=$(find official-docs -name '*.rst' | wc -l)
if [ "$FILE_COUNT" -lt 100 ]; then
  echo "❌ Upstream clone incomplete ($FILE_COUNT files)"
  exit 1
fi

# Validate commit recency
COMMIT_AGE=$(git -C official-docs log -1 --format=%ct)
NOW=$(date +%s)
AGE_DAYS=$(( (NOW - COMMIT_AGE) / 86400 ))
if [ "$AGE_DAYS" -gt 90 ]; then
  echo "⚠️ Upstream commit is $AGE_DAYS days old"
fi
```

### 3. **Diff Size Gate**
Calculate change magnitude before commit:
```bash
# Check diff size
ADDED=$(git diff --numstat | awk '{sum+=$1} END {print sum}')
DELETED=$(git diff --numstat | awk '{sum+=$2} END {print sum}')
FILES_CHANGED=$(git diff --name-only | wc -l)

if [ "$FILES_CHANGED" -gt 50 ]; then
  echo "⚠️ Large sync: $FILES_CHANGED files changed"
  echo "   +$ADDED lines, -$DELETED lines"
  # Require manual approval
fi
```

### 4. **Staged Rollout via PR**
Replace direct push with PR creation:
```yaml
- name: Create Pull Request
  uses: peter-evans/create-pull-request@v5
  with:
    branch: docs-sync-${{ github.run_id }}
    title: "docs(sync): Odoo 18.0 official docs - ${{ steps.metadata.outputs.date }}"
    body: |
      **Files Changed**: ${{ steps.diff.outputs.files }}
      **Lines Added**: +${{ steps.diff.outputs.added }}
      **Lines Deleted**: -${{ steps.diff.outputs.deleted }}
```

### 5. **Last Known Good Tag**
Tag successful syncs for rollback:
```bash
git tag -a "docs-sync-$(date +%Y%m%d-%H%M)" -m "Sync checkpoint"
git push --tags
```

---

## Priority Actions

| Priority | Action | Effort | Impact |
|----------|--------|--------|--------|
| P0 | Vendor subtree migration | 1h | Prevents namespace pollution |
| P0 | Pre-sync validation | 30min | Prevents empty/corrupted syncs |
| P1 | Diff size gate | 30min | Prevents catastrophic changes |
| P1 | PR-based rollout | 30min | Adds review layer |
| P2 | Rollback tags | 15min | Enables quick recovery |

---

## Next Steps

1. **Implement vendor subtree** (Task 3 deliverable)
2. **Add validation gates** (prevent bad syncs)
3. **Add diff gates** (prevent large unexpected changes)
4. **Switch to PR workflow** (add review layer)
5. **Test with dry-run** (validate all gates work)

---

**Evidence Location**: `web/docs/evidence/20260305-0000+0800/docs-sync-sandbox/logs/`
**Status**: Analysis complete, ready for implementation
