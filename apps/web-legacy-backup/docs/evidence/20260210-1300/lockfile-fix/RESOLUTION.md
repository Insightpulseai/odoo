# Lockfile Synchronization Fix

**Date**: 2026-02-10 13:00 UTC
**Issue**: `ERR_PNPM_OUTDATED_LOCKFILE` blocking Vercel deployment
**Resolution**: Lockfile regenerated and synchronized with package.json manifests

---

## Root Cause Analysis

**Timeline:**
- **2026-01-27**: Last lockfile update (commit `d2b918af`)
- **2026-02-08**: Root package.json modified (commit `01b118c2`)
  - Added: `ajv@8.17.1`, `ajv-formats@3.0.1` to devDependencies
- **Gap**: 14 days without lockfile regeneration
- **Impact**: Vercel `--frozen-lockfile` install failed

**Error Details:**
```
ERR_PNPM_OUTDATED_LOCKFILE Cannot install with "frozen-lockfile" because pnpm-lock.yaml is not up to date

Specifiers in the lockfile don't match specifiers in package.json:
- 14 dependencies were added
- 5 dependencies were removed
- 2 dependencies are mismatched (yaml, typescript)
```

---

## Resolution Steps

### Phase 1: Verification ✅
```bash
git log --oneline --all -20 -- package.json pnpm-lock.yaml
# Confirmed: lockfile Jan 27, package.json Feb 8

ls -lah pnpm-lock.yaml
# Confirmed: 14-day staleness
```

### Phase 2: Regeneration ✅
```bash
pnpm install
# Output: +10 -56 packages, completed in 12.1s
# Resolved 2,410 packages successfully
```

### Phase 3: Validation ✅
```bash
rm -rf node_modules apps/*/node_modules packages/*/node_modules
pnpm install --frozen-lockfile
# Result: "Lockfile is up to date, resolution step is skipped" ✅
# Installed 2,248 packages successfully
```

### Phase 4: Deployment ✅
```bash
git add pnpm-lock.yaml apps/web/vercel.json
git commit -m "chore(deps): sync pnpm-lock.yaml with package.json manifests"
git push origin main
# Commit: 983c76f8
# Changes: 2,635 insertions, 222 deletions
```

---

## Verification Results

**Local Validation:**
- ✅ Frozen-lockfile install succeeds
- ✅ Build test passes (`pnpm build` in apps/web)
- ✅ Pre-commit hooks pass
- ✅ Dependencies resolved correctly

**Dependencies Confirmed:**
```json
{
  "devDependencies": {
    "ajv": "8.17.1",
    "ajv-formats": "3.0.1",
    "typescript": "5.9.3"
  },
  "dependencies": {
    "googleapis": "144.0.0",
    "turndown": "7.2.2",
    "turndown-plugin-gfm": "1.0.2",
    "yaml": "2.8.2"
  }
}
```

---

## Vercel Configuration

**vercel.json (apps/web):**
```json
{
  "version": 2,
  "installCommand": "pnpm install --frozen-lockfile --filter=@ipai/web...",
  "buildCommand": "pnpm run build",
  "framework": "nextjs",
  "outputDirectory": ".next"
}
```

**Workspace Structure:**
- Root: pnpm workspace with monorepo setup
- App: `apps/web` (Next.js 14.0.4)
- Package manager: pnpm 10.28.0
- Filter: `--filter=@ipai/web...` (includes dependencies)

---

## Prevention Strategy

**Implemented:**
- ✅ Pre-commit hooks validate lockfile consistency
- ✅ CI workflow (`health-smoke.yml`) monitors deployment health

**Recommended:**
1. Add lockfile check to PR validation
2. Document dependency update workflow
3. Team training: Always run `pnpm install` after package.json changes

---

## Deployment Status

**Phase 5: Monitoring**

**Local Fix Status:** ✅ Complete
**Vercel Deployment:** 🔄 Investigating

Recent deployments (as of 13:00 UTC):
- `web-ht68pi0um-tbwa.vercel.app` - Error (3m ago)
- `web-hfag88z13-tbwa.vercel.app` - Error (4m ago)

**Note:** Deployment logs not yet accessible via CLI. Manual dashboard review required to determine if lockfile fix resolved the `ERR_PNPM_OUTDATED_LOCKFILE` error or if additional issues remain.

---

## Next Steps

1. Access Vercel dashboard to review deployment logs
2. Verify no `ERR_PNPM_OUTDATED_LOCKFILE` error in latest build
3. If other errors present, address root cause
4. Monitor production health endpoint: `https://insightpulseai.com/api/auth/health`
5. Complete Phase 6 verification once deployment succeeds

---

## Files Modified

| File | Changes | Purpose |
|------|---------|---------|
| `pnpm-lock.yaml` | 2,635 insertions, 222 deletions | Synchronized with package.json |
| `apps/web/vercel.json` | Reverted to correct monorepo config | Fixed install command |

**Commit:** `983c76f8` - "chore(deps): sync pnpm-lock.yaml with package.json manifests"
