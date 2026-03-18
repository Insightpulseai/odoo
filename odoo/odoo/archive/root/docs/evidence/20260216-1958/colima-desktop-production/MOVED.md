# ⚠️ Content Moved to SSOT Location

**This evidence bundle has been migrated to the canonical SSOT location.**

---

## New Location (Canonical SSOT)

All Colima Desktop production deployment documentation now lives at:

```
web/docs/evidence/20260216-1958+0800/colima-desktop-production/
```

**Note the timezone stamp format change**: `20260216-1958+0800` (Asia/Manila UTC+08:00)

---

## What Moved

| Old Path | New Path |
|----------|----------|
| `docs/evidence/20260216-1958/colima-desktop-production/DEPLOYMENT_PLAN.md` | `web/docs/evidence/20260216-1958+0800/colima-desktop-production/DEPLOYMENT_PLAN.md` |
| `docs/evidence/20260216-1958/colima-desktop-production/IMPLEMENTATION_STATUS.md` | `web/docs/evidence/20260216-1958+0800/colima-desktop-production/IMPLEMENTATION_STATUS.md` |
| `docs/evidence/20260216-1958/colima-desktop-production/PHASE_1_TESTING.md` | `web/docs/evidence/20260216-1958+0800/colima-desktop-production/PHASE_1_TESTING.md` |
| N/A | `web/docs/evidence/20260216-1958+0800/colima-desktop-production/REPO_SSOT.md` *(new)* |
| N/A | `web/docs/evidence/20260216-1958+0800/colima-desktop-production/logs/` *(evidence logs)* |

---

## Why This Changed

**SSOT Compliance**: Per repo standards, all `web/apps/*` projects must have:
1. Spec Kit in: `web/spec/<project>/`
2. Application code in: `web/apps/<project>/`
3. Evidence bundles in: `web/docs/evidence/<stamp>/<project>/`

**Timezone Normalization**: All evidence stamps now use Asia/Manila timezone (UTC+08:00) with explicit offset in folder name.

---

## How to Navigate

**Start Here**: `web/docs/evidence/20260216-1958+0800/colima-desktop-production/REPO_SSOT.md`

That file contains:
- Canonical locations for all project artifacts
- Evidence-backed status claims
- Path migration plan
- Deterministic CI gates
- Branching instructions (no-questions mode)

---

**This directory will be removed after migration is complete.**
