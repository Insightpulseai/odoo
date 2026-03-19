# Repository SSOT Map

**Single Source of Truth for Odoo Development**

This document defines the canonical locations for all Odoo-related development work and enforces the **single repository root** principle.

---

## Canonical Roots

| Location | Purpose | Status |
|----------|---------|--------|
| `/odoo/` (this repo) | Canonical Odoo runtime, addons, specs, CI | ✅ **SSOT** |
| `/spec/` (this repo) | Spec bundles for features and architecture | ✅ Canonical |
| `/docs/` (this repo) | Project documentation and architecture | ✅ Canonical |
| `/scripts/` (this repo) | Automation scripts and utilities | ✅ Canonical |
| `/.github/workflows/` (this repo) | CI/CD workflows and quality gates | ✅ Canonical |

---

## Non-Canonical (Scratch) Locations

| Location | Purpose | Rules |
|----------|---------|-------|
| `../work/` | Agent scratch space, temporary files | ⚠️ **Must NOT** contain odoo roots |
| `../work/apps/` | Temporary app prototypes | ⚠️ Migrate to `/apps/` or `/addons/` when stable |
| `./_work/` (this repo) | Per-repo scratch directory | ⚠️ Local only, git-ignored |

---

## Repository Structure

```
Insightpulseai/                      # Parent workspace (separate git repo)
├── odoo/                            # This repository (CANONICAL SSOT) ✅
│   ├── addons/                     # Odoo modules
│   │   ├── ipai/                   # IPAI custom modules
│   │   └── oca/                    # OCA modules (submodules)
│   ├── apps/                       # Platform apps
│   ├── spec/                       # Spec bundles (spec-kit)
│   ├── docs/                       # Documentation
│   ├── scripts/                    # Automation scripts
│   ├── .github/workflows/          # CI/CD pipelines
│   ├── sandbox/                    # Development sandboxes
│   ├── architecture-review/        # Architecture templates and baselines
│   └── CLAUDE.md                   # AI agent contract (SSOT declaration)
│
└── work/                            # Scratch repository ⚠️
    ├── apps/                       # Temporary app experiments
    ├── spec/                       # Spec experiments (migrate to odoo/spec/)
    ├── .github/workflows/          # CI guards (no shadow odoo roots)
    └── .gitignore                  # Blocks: odoo/, odoo-ce/, odoo-ce-*, odoo19/
```

---

## SSOT Enforcement

### 1. Git Structure Guards

**File:** `.github/workflows/repo-structure-guard.yml` (both repositories)

**Purpose:** Prevent shadow Odoo roots from being created

**Blocked Patterns:**
- `work/odoo/`
- `work/odoo-ce/`
- `work/odoo-ce-*/`
- `work/odoo19/`
- Nested `odoo/` within this canonical repo

### 2. Gitignore Enforcement

**File:** `../work/.gitignore`

**Blocked:**
```gitignore
odoo/
odoo-ce/
odoo-ce-*/
odoo19/
```

### 3. Documentation Requirements

All repositories must declare SSOT compliance:
- ✅ `CLAUDE.md` contains SSOT declaration
- ✅ `README.md` contains SSOT section
- ✅ `docs/architecture/REPO_SSOT_MAP.md` (this file)

---

## Decision Rules

### When to Use Canonical `odoo/`

✅ **Always use for:**
- Production code (modules, scripts, apps)
- Spec bundles (PRD, plans, tasks)
- CI/CD workflows
- Documentation
- Architecture decisions
- Anything that ships to production or defines product behavior

### When to Use Scratch `work/`

✅ **Only use for:**
- Temporary experiments
- Quick prototypes (migrate to `odoo/` when validated)
- Agent workspace scratch files
- Local caches and logs

❌ **Never use for:**
- Odoo module development
- Feature implementation
- Spec bundles
- Production-bound code

---

## Migration Path

If code exists in wrong location:

1. **Verify Value:** Confirm the code has production value
2. **Choose Destination:**
   - Odoo modules → `odoo/addons/ipai/<module>/`
   - Apps → `odoo/apps/<app>/`
   - Specs → `odoo/spec/<feature-slug>/`
   - Scripts → `odoo/scripts/`
3. **Move with History:**
   ```bash
   cd /path/to/canonical/repo
   git mv ../work/path/to/code ./destination/path
   git commit -m "chore(repo): relocate [name] to canonical location"
   ```
4. **Update References:** Fix import paths, docs, CI
5. **Verify:** Run tests, checks, CI gates
6. **Remove Shadow:** Delete original from `work/`

---

## Compliance Verification

```bash
# From odoo/ repository root
./scripts/repo_health.sh              # Verify repo structure
./scripts/spec_validate.sh            # Verify spec bundles

# Manual check
find ../work -maxdepth 2 -name "odoo*" -type d  # Should return nothing
```

---

## History

| Date | Change | Reason |
|------|--------|--------|
| 2026-02-15 | Created SSOT map | Eliminate shadow odoo-ce roots in work/ |
| 2026-02-15 | Added CI guards | Prevent regression of shadow roots |

---

**Maintained by:** Architecture team
**Last updated:** 2026-02-15
**CI enforcement:** ✅ Active via `repo-structure-guard.yml`
