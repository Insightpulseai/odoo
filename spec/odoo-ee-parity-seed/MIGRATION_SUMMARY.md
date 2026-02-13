# Migration Summary: Sandbox → Repo Root

**Date:** 2026-02-13
**Status:** ✅ Complete

---

## Migration Overview

Migrated Odoo Editions Parity Seed Generator from `sandbox/dev/` to repo root for:
1. **CI Compatibility**: GitHub Actions only executes workflows from `.github/workflows/` at repo root
2. **Project Visibility**: Spec Kit bundles should be accessible project-wide
3. **Path Consistency**: Eliminate ambiguity between sandbox and repo-root contracts

## Structural Fixes

### 1. Deterministic Timestamp Mode

**Problem:** Every script run generated a new `fetched_at` timestamp, causing false-positive drift detection.

**Solution:**
```python
# Added in scripts/gen_odoo_editions_parity_seed.py
det = os.getenv("PARITY_SEED_DETERMINISTIC", "").lower() in ("1", "true", "yes")
fetched_ts = "1970-01-01T00:00:00Z" if det else datetime.now(timezone.utc).isoformat()
```

**Usage:**
```bash
PARITY_SEED_DETERMINISTIC=1 python scripts/gen_odoo_editions_parity_seed.py
```

**Result:** Drift detection now only triggers on actual content changes, not timestamp updates.

### 2. Git Command Syntax

**Problem:** `git diff sandbox/dev/Makefile` treated path as revision, causing errors.

**Solution:** Always use `--` separator:
```bash
git diff -- sandbox/dev/Makefile        # ✅ Correct
git diff --exit-code -- spec/parity/odoo_editions_parity_seed.yaml  # ✅ Correct
```

### 3. Workflow Location

**Before:** `sandbox/dev/.github/workflows/editions-parity-seed.yml` (won't execute)
**After:** `.github/workflows/editions-parity-seed.yml` (executes on schedule)

GitHub Actions requires workflows at repo-root `.github/workflows/`.

---

## File Relocation Map

| Before (Sandbox) | After (Repo Root) | Status |
|------------------|-------------------|--------|
| `sandbox/dev/spec/odoo-ee-parity-seed/` | `spec/odoo-ee-parity-seed/` | ✅ Migrated |
| `sandbox/dev/scripts/gen_odoo_editions_parity_seed.py` | `scripts/gen_odoo_editions_parity_seed.py` | ✅ Migrated |
| `sandbox/dev/.github/workflows/editions-parity-seed.yml` | `.github/workflows/editions-parity-seed.yml` | ✅ Migrated |
| `sandbox/dev/spec/parity/` | `spec/parity/` | ✅ Migrated |

**Sandbox Copies:** Preserved for reference, updated with deterministic mode support.

---

## Commits

1. **36abd75b** - feat(parity): migrate parity seed generator to repo root + add deterministic mode
   - Moved all files to repo root
   - Added deterministic timestamp mode
   - Fixed workflow paths and git diff syntax

2. **21462a10** - feat(parity): update sandbox with deterministic timestamp mode
   - Updated sandbox copies to match repo-root implementation
   - Added deterministic mode to sandbox Makefile

---

## Verification Evidence

### 1. Deterministic Timestamp Works

```bash
$ PARITY_SEED_DETERMINISTIC=1 python scripts/gen_odoo_editions_parity_seed.py
✅ Wrote 64 rows to spec/parity/odoo_editions_parity_seed.yaml

$ grep 'fetched_at:' spec/parity/odoo_editions_parity_seed.yaml
    fetched_at: '1970-01-01T00:00:00Z'
```

### 2. Drift Detection Is Accurate

```bash
$ PARITY_SEED_DETERMINISTIC=1 python scripts/gen_odoo_editions_parity_seed.py
$ git diff --exit-code -- spec/parity/odoo_editions_parity_seed.yaml
✅ No drift detected
```

Re-running with deterministic mode produces identical output (no false positives).

### 3. Workflow Location Verified

```bash
$ ls -la .github/workflows/editions-parity-seed.yml
.rw-r--r--@ 1.6k tbwa 13 Feb 08:52  .github/workflows/editions-parity-seed.yml
```

Workflow is now at repo root and will execute on schedule.

### 4. Script Writes to Correct Location

```bash
$ PARITY_SEED_DETERMINISTIC=1 python scripts/gen_odoo_editions_parity_seed.py
Writing to /Users/tbwa/.../odoo/spec/parity/odoo_editions_parity_seed.yaml...
```

Script correctly writes to `spec/parity/` at repo root (not sandbox).

---

## Updated Workflow Configuration

**CI Workflow** (`.github/workflows/editions-parity-seed.yml`):
- ✅ Uses `PARITY_SEED_DETERMINISTIC=1`
- ✅ Uses `git diff --exit-code --` (proper syntax)
- ✅ Weekly cron: Sundays at midnight UTC
- ✅ Manual trigger: `workflow_dispatch`

**Changes:**
```diff
- python scripts/gen_odoo_editions_parity_seed.py
+ PARITY_SEED_DETERMINISTIC=1 python scripts/gen_odoo_editions_parity_seed.py

- if ! git diff --exit-code spec/parity/odoo_editions_parity_seed.yaml; then
+ if ! git diff --exit-code -- spec/parity/odoo_editions_parity_seed.yaml; then
```

---

## Testing Commands

### Local Execution
```bash
# Generate with deterministic timestamp
PARITY_SEED_DETERMINISTIC=1 python scripts/gen_odoo_editions_parity_seed.py

# Verify no drift
git diff --exit-code -- spec/parity/odoo_editions_parity_seed.yaml
```

### CI Workflow Trigger
```bash
# Manual trigger (requires repo push first)
gh workflow run editions-parity-seed.yml

# Check run status
gh run list --workflow=editions-parity-seed.yml
```

---

## Next Steps

### Immediate (Required)
1. ✅ Push commits to origin
2. ⏳ Verify workflow appears in GitHub Actions UI
3. ⏳ Trigger workflow manually to test CI execution
4. ⏳ Verify artifact upload works

### Short-term (Optional)
5. 🔄 Remove sandbox copies after confirming CI works
6. 🔄 Add Makefile targets to repo-root Makefile (if needed)
7. 🔄 Update documentation references to point to repo-root paths

### Long-term (Enhancement)
8. 🔄 Implement Phase 2 enrichment scripts (CE candidates, OCA matching)
9. 🔄 Implement Phase 3 cross-reference tool (deduplication with ee_parity_mapping.yml)
10. 🔄 Manual enrichment of high-priority features

---

## Rollback Instructions

**If migration causes issues:**

```bash
# Revert migration commits
git revert --no-edit 21462a10 36abd75b

# Or restore workflow to sandbox (not recommended - won't execute)
git mv .github/workflows/editions-parity-seed.yml sandbox/dev/.github/workflows/

# Commit and push
git commit -m "revert: rollback parity seed migration to sandbox"
git push
```

**Note:** Rolling back is not recommended - the migration fixes critical path issues (CI execution, deterministic drift detection). If issues arise, fix forward instead.

---

## Success Criteria

| Criterion | Status | Evidence |
|-----------|--------|----------|
| ✅ Files at repo root | ✅ Complete | All files in `spec/`, `scripts/`, `.github/workflows/` |
| ✅ Deterministic mode works | ✅ Complete | Timestamp is `1970-01-01T00:00:00Z` |
| ✅ Drift detection accurate | ✅ Complete | No false positives from timestamps |
| ✅ Workflow at correct location | ✅ Complete | `.github/workflows/editions-parity-seed.yml` |
| ✅ Script writes to repo root | ✅ Complete | Output at `spec/parity/odoo_editions_parity_seed.yaml` |
| ⏳ CI workflow executes | Pending | Requires push + manual trigger |

---

## References

- **Original Implementation:** Commits f70b34f7, 7a4b8dd1, 4cc03e59
- **Migration Commits:** 36abd75b, 21462a10
- **Workflow Path:** `.github/workflows/editions-parity-seed.yml`
- **Script Path:** `scripts/gen_odoo_editions_parity_seed.py`
- **Output Path:** `spec/parity/odoo_editions_parity_seed.yaml`
- **Spec Kit:** `spec/odoo-ee-parity-seed/`

---

**Migration completed successfully. All structural issues resolved.**
