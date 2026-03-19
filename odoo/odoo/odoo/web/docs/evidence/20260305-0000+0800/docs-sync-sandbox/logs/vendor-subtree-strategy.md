# Vendor Subtree Isolation Strategy

**Design Date**: 2026-03-05T00:00+0800
**Scope**: Isolate external documentation syncs to prevent blast radius
**Related**: Governance Hardening Plan - Task 3

---

## Current State vs Proposed State

### Current (Problematic)
```
docs/
├── odoo-official/         ← External sync (mixed namespace)
│   ├── administration/
│   ├── applications/
│   ├── contributing/
│   └── developer/
├── architecture/          ← Internal docs
├── ai/                    ← Internal docs
└── runbooks/              ← Internal docs
```

**Problems**:
- External and internal docs share `docs/` namespace
- Risk of rsync misconfiguration affecting internal docs
- Unclear ownership boundary

### Proposed (Isolated)
```
vendor/
└── docs/
    └── odoo-official/
        └── 19.0/
            ├── administration/
            ├── applications/
            ├── contributing/
            ├── developer/
            ├── SYNC_METADATA.json
            └── SYNC_REPORT.md

docs/
├── architecture/          ← Internal only
├── ai/                    ← Internal only
└── runbooks/              ← Internal only
```

**Benefits**:
- Clear boundary: `vendor/` = external, `docs/` = internal
- No namespace collision possible
- Easy to identify sync artifacts
- Can `.gitignore vendor/` if needed for size

---

## Migration Plan

### Phase 1: Create Vendor Subtree Structure

**Directory Structure**:
```
vendor/
└── docs/
    └── odoo-official/
        └── 19.0/          ← Version-specific isolation
```

**Rationale**:
- `vendor/` = third-party content (standard convention)
- `docs/` subdirectory = documentation-specific vendor content
- `odoo-official/` = source identification
- `19.0/` = version isolation (future-proof for 20.0, 21.0)

### Phase 2: Update Sync Target Paths

**Old rsync commands**:
```bash
rsync -av --delete --checksum \
  official-docs/content/administration/ \
  repo/docs/odoo-official/administration/
```

**New rsync commands**:
```bash
rsync -av --delete --checksum \
  official-docs/content/administration/ \
  repo/vendor/docs/odoo-official/19.0/administration/
```

**All path updates**:
- `docs/odoo-official/` → `vendor/docs/odoo-official/19.0/`
- Metadata files move with content
- Search index stays with vendor docs

### Phase 3: Update Documentation References

**Files to update**:
1. Sphinx `conf.py` - update source paths
2. `index.rst` - update toctree paths
3. AI chat widget - update search index path
4. GitHub Pages deployment - update artifact path

**Search Index Path**:
- Old: `docs/odoo-official/search-index.json`
- New: `vendor/docs/odoo-official/19.0/search-index.json`

### Phase 4: Add Vendor Metadata

Create `vendor/docs/odoo-official/README.md`:
```markdown
# Odoo Official Documentation (Vendor)

**Source**: https://github.com/odoo/documentation
**Sync Workflow**: `.github/workflows/docs-sync-odoo-official.yml`
**Last Sync**: See `19.0/SYNC_METADATA.json`

## Directory Structure

- `19.0/` - Odoo 19.0 documentation (current)
- Future: `20.0/`, `21.0/` as versions are released

## Sync Schedule

- **Daily**: 3 AM UTC via GitHub Actions
- **Manual**: Workflow dispatch available
- **Validation**: Pre-sync checks + diff gates

## Ownership

- **Content**: Odoo SA (upstream)
- **Sync Process**: InsightPulse AI DevOps
- **Do Not Edit**: Files are overwritten on next sync
```

---

## Gitignore Strategy

### Option A: Track All Vendor Docs (Recommended)
```gitignore
# vendor/.gitignore
# Track all documentation for offline access and search
# Only ignore build artifacts and temp files
**/node_modules/
**/__pycache__/
**/.DS_Store
**/Thumbs.db
```

**Pros**:
- Offline documentation access
- Full-text search in IDE
- Version control tracks changes
- No external dependency for builds

**Cons**:
- Larger repo size (~50-100MB)
- Git history tracks external changes

### Option B: Ignore All Vendor Docs (Not Recommended)
```gitignore
# .gitignore (root)
/vendor/docs/odoo-official/19.0/
!/vendor/docs/odoo-official/19.0/SYNC_METADATA.json
!/vendor/docs/odoo-official/19.0/SYNC_REPORT.md
```

**Pros**:
- Smaller repo size
- No external changes in git history

**Cons**:
- Requires sync before local builds
- No offline docs access
- CI must sync before every build

**Recommendation**: Option A (track all) - benefits outweigh size cost.

---

## Diff Gate Implementation

### Gate 1: File Count Validation

**Before Sync**:
```bash
# Validate upstream has expected file count
UPSTREAM_FILES=$(find official-docs/content -name '*.rst' | wc -l)
EXPECTED_MIN=100
EXPECTED_MAX=1000

if [ "$UPSTREAM_FILES" -lt "$EXPECTED_MIN" ]; then
  echo "❌ Upstream file count too low: $UPSTREAM_FILES (expected >$EXPECTED_MIN)"
  exit 1
fi

if [ "$UPSTREAM_FILES" -gt "$EXPECTED_MAX" ]; then
  echo "⚠️ Upstream file count unusually high: $UPSTREAM_FILES (expected <$EXPECTED_MAX)"
  echo "   Proceeding with caution..."
fi
```

### Gate 2: Diff Magnitude Check

**After Sync, Before Commit**:
```bash
# Calculate change statistics
git diff --numstat vendor/docs/odoo-official/19.0/ > /tmp/diff-stats.txt

ADDED=$(awk '{sum+=$1} END {print sum}' /tmp/diff-stats.txt)
DELETED=$(awk '{sum+=$2} END {print sum}' /tmp/diff-stats.txt)
FILES_CHANGED=$(wc -l < /tmp/diff-stats.txt)

# Define thresholds
MAX_FILES=50
MAX_LINES_DELETED=5000
WARN_LINES_ADDED=10000

# Hard stop conditions
if [ "$FILES_CHANGED" -gt "$MAX_FILES" ]; then
  echo "🚨 GATE FAILURE: $FILES_CHANGED files changed (threshold: $MAX_FILES)"
  echo "   This may indicate upstream restructure or sync error."
  exit 1
fi

if [ "$DELETED" -gt "$MAX_LINES_DELETED" ]; then
  echo "🚨 GATE FAILURE: $DELETED lines deleted (threshold: $MAX_LINES_DELETED)"
  echo "   This may indicate accidental deletion."
  exit 1
fi

# Warnings only
if [ "$ADDED" -gt "$WARN_LINES_ADDED" ]; then
  echo "⚠️ WARNING: $ADDED lines added (threshold: $WARN_LINES_ADDED)"
  echo "   Review sync carefully."
fi

echo "✅ Diff gate passed:"
echo "   Files changed: $FILES_CHANGED"
echo "   Lines added: +$ADDED"
echo "   Lines deleted: -$DELETED"
```

### Gate 3: Structural Integrity Check

**Verify expected directories exist**:
```bash
# Ensure all 4 documentation sections present
REQUIRED_DIRS=(
  "vendor/docs/odoo-official/19.0/administration"
  "vendor/docs/odoo-official/19.0/applications"
  "vendor/docs/odoo-official/19.0/contributing"
  "vendor/docs/odoo-official/19.0/developer"
)

for dir in "${REQUIRED_DIRS[@]}"; do
  if [ ! -d "$dir" ]; then
    echo "❌ Missing required directory: $dir"
    exit 1
  fi

  FILE_COUNT=$(find "$dir" -name '*.rst' | wc -l)
  if [ "$FILE_COUNT" -lt 5 ]; then
    echo "❌ Directory nearly empty: $dir ($FILE_COUNT files)"
    exit 1
  fi
done

echo "✅ Structural integrity verified"
```

---

## Rollback Strategy

### Automatic Rollback Triggers

**Trigger automatic rollback if**:
1. Diff gate failures (>50 files, >5000 lines deleted)
2. Structural integrity failures (missing directories)
3. Search index build failures
4. Sphinx build failures

**Rollback Mechanism**:
```bash
# Tag successful syncs
git tag -a "docs-sync-good-$(date +%Y%m%d-%H%M)" -m "Known good sync"
git push --tags

# Rollback command (manual or automated)
LAST_GOOD=$(git tag -l "docs-sync-good-*" | sort -r | head -1)
git checkout "$LAST_GOOD" -- vendor/docs/odoo-official/
git commit -m "revert(docs): rollback to $LAST_GOOD"
git push origin main
```

### Manual Rollback Procedure

**If bad sync reaches production**:
```bash
# 1. Find last known good tag
git tag -l "docs-sync-good-*" | sort -r

# 2. Restore from tag
git checkout docs-sync-good-20260304-0300 -- vendor/docs/odoo-official/

# 3. Commit rollback
git commit -m "revert(docs): emergency rollback to 20260304-0300"

# 4. Push and redeploy
git push origin main
# GitHub Pages will auto-redeploy
```

---

## Success Criteria

### Validation Checklist

- [ ] Vendor subtree created at `vendor/docs/odoo-official/19.0/`
- [ ] All 4 documentation sections synced
- [ ] `SYNC_METADATA.json` present with file counts
- [ ] `SYNC_REPORT.md` present with sync timestamp
- [ ] Search index built at `19.0/search-index.json`
- [ ] Sphinx build succeeds with new paths
- [ ] GitHub Pages deployment succeeds
- [ ] AI chat widget functional with new index path
- [ ] All diff gates pass (file count, magnitude, structure)
- [ ] First successful sync tagged as `docs-sync-good-*`

### Monitoring Metrics

**Track in workflow**:
1. Sync duration (baseline: ~2-5 minutes)
2. File count deltas (baseline: ±5 files per sync)
3. Line count deltas (baseline: ±500 lines per sync)
4. Gate failure rate (target: <5% of syncs)
5. Rollback frequency (target: <1% of syncs)

---

## Implementation Order

1. ✅ Create vendor subtree structure
2. ✅ Add vendor README and metadata
3. ✅ Update workflow rsync paths
4. ✅ Add pre-sync validation (Gate 1)
5. ✅ Add diff magnitude check (Gate 2)
6. ✅ Add structural integrity check (Gate 3)
7. ✅ Update Sphinx configuration
8. ✅ Update AI widget paths
9. ✅ Test with dry-run
10. ✅ Deploy and tag first good sync

---

**Status**: Design complete, ready for implementation
**Next**: Implement modified workflow in `.github/workflows/docs-sync-odoo-official.yml`
