# Odoo Dev Sandbox - Repository Audit Report

**Date**: 2026-01-18
**Auditor**: Claude Code (automated)
**Purpose**: Assess current state vs canonical SSOT and identify normalization needs

---

## Executive Summary

**Current State**: This repository (`odoo-dev-sandbox`) is a **fragmented extraction** with:
- ✅ Custom addons (`ipai`, `ipai_enterprise_bridge`) present
- ❌ **NO docker-compose.yml** in repo root
- ❌ **NO working dev stack** locally
- ⚠️ Empty config directory (`config/odoo.conf/` is an empty dir, not a file)
- ⚠️ Git in uncommitted state (staged files from design extraction)

**Canonical SSOT Location**: `~/Documents/GitHub/odoo-ce/sandbox/dev/`
- ✅ Has working `docker-compose.yml` (Odoo 18 CE + PostgreSQL 16)
- ✅ Properly configured volumes and hot-reload
- ✅ Clear separation: `./addons` (custom), `../../addons/external/oca` (OCA modules)

**Assessment**: This repo appears to be an **incomplete copy or experimental workspace**. It does NOT match the canonical dev sandbox structure documented in `infra/docker/DOCKER_DESKTOP_SSOT.yaml`.

---

## Current Repository Structure

```
odoo-dev-sandbox/
├── .git/                          # Git initialized but no commits
├── .github/workflows/             # Has pbi-migration.yml only
├── addons/
│   ├── ipai/                      # Main custom module (18.0.1.0.0)
│   └── ipai_enterprise_bridge/    # Enterprise parity module
├── config/
│   └── odoo.conf/                 # ❌ EMPTY DIRECTORY (should be a file)
├── docs/
│   ├── runbooks/
│   └── tasks/
├── infra/docker/
│   └── DOCKER_DESKTOP_SSOT.yaml   # ✅ SSOT reference document
├── ipai_dashboard_tools/          # Dashboard generation utilities
├── oca-addons/                    # ❌ EMPTY (no OCA modules present)
├── out/insightpulseai/            # Design system extraction artifacts
└── scripts/
    ├── docker-desktop-audit.sh
    ├── extract-design-and-html.js
    └── extract-design-tokens.js
```

---

## What's Running (Expected vs Actual)

### Expected (per DOCKER_DESKTOP_SSOT.yaml)
**Location**: `~/Documents/GitHub/odoo-ce/sandbox/dev/`

| Component | Container Name | Port | Status |
|-----------|----------------|------|--------|
| Odoo 18 CE | `odoo-dev` | 8069 | ✅ Running (canonical location) |
| PostgreSQL 16 | `odoo-dev-db` | 5433 | ✅ Running (canonical location) |
| pgAdmin (optional) | `odoo-dev-pgadmin` | 5050 | Profile: tools |
| Mailpit (optional) | `odoo-dev-mailpit` | 8025/1025 | Profile: tools |

### Actual (this repo)
**Location**: `/Users/tbwa/Downloads/extracted_files/odoo-dev-sandbox/`

| Component | Status | Issue |
|-----------|--------|-------|
| docker-compose.yml | ❌ Missing | No stack definition |
| Odoo config | ❌ Invalid | `config/odoo.conf/` is empty directory |
| Custom addons | ✅ Present | `ipai` + `ipai_enterprise_bridge` |
| OCA addons | ❌ Missing | `oca-addons/` empty |
| Scripts | ⚠️ Partial | Audit + extraction scripts only |

---

## What's Missing

### Critical
1. **docker-compose.yml** - No orchestration file in repo root
2. **config/odoo.conf** - Should be a file, not an empty directory
3. **OCA dependencies** - `oca-addons/` is empty (24 modules referenced in manifest)
4. **Dev scripts** - No `scripts/dev/` directory with standard operations
5. **.env** - No environment template or example

### Recommended
6. **Makefile** - Quick shortcuts for common operations
7. **README.md** - Setup and usage instructions
8. **CI workflow** - Only has `pbi-migration.yml`, needs dev-sandbox validation
9. **.gitignore** - Should ignore `.env`, `*.pyc`, `__pycache__`, logs, etc.

---

## What's Redundant

### Design Extraction Artifacts (questionable relevance)
```
out/insightpulseai/visual/        # 30+ files from design system extraction
scripts/extract-design-*.js       # Node.js extraction tools
```
**Issue**: These appear to be frontend design artifacts, not Odoo development assets. Consider moving to a separate repo or archiving.

### Staged But Uncommitted Files
Git shows 32 staged files (all in `out/` and `scripts/`) but no commits. This creates ambiguity about repo purpose.

---

## Odoo Module Analysis

### Custom Modules Present

#### 1. `addons/ipai/` (v18.0.1.0.0)
**Status**: ✅ Well-structured OCA-compliant module
**Purpose**: Enterprise Bridge (18 CE → 19/EE parity)

**Dependencies** (59 total):
- Core: project, hr_timesheet, sale_project, account, contacts, sale_management
- External Gantt: devjs_web_gantt
- OCA modules: 24 project/timesheet/helpdesk/fieldservice modules
- OCA QMS: maintenance, quality_control, mgmtsystem
- OCA Docs: dms, knowledge
- OCA Reporting: mis_builder

**Views**: 8 XML files in `views/`
- ✅ No deprecated `<tree>` tags found (already using Odoo 18 conventions)
- ⚠️ Action view_mode validation needed (not found in grep)

**Data**: Seed data for Finance Logframe + BIR Schedule

#### 2. `addons/ipai_enterprise_bridge/`
**Status**: ⚠️ Exists but minimal content (only 2 view files)

**Missing from This Repo**:
All 24 OCA dependencies referenced in `ipai/__manifest__.py` are declared but not present in `oca-addons/`.

---

## View Convention Compliance (Odoo 18)

### ✅ Already Compliant
Grep search for deprecated `<tree>` tags: **0 results**

All view files in `addons/ipai/views/` appear to follow Odoo 18 conventions:
- Using `<gantt>`, `<form>`, `<page>` tags appropriately
- No legacy `<tree>` usage detected

### ⚠️ Action view_mode Validation
No `<field name="view_mode">` declarations found in XML files. This suggests:
- Actions may be inherited from base modules (acceptable)
- Or actions defined in Python models (needs verification)

**Action to verify**:
```python
# Check for view_mode in Python models
grep -r "view_mode.*=.*tree" addons/ipai/models/
```

---

## Recommended Changes

### Priority 1: Establish Working Dev Stack

1. **Copy canonical docker-compose.yml** from `~/Documents/GitHub/odoo-ce/sandbox/dev/`
   - Adjust paths for this repo structure
   - Update volume mounts to reference local `./addons`, `./oca-addons`

2. **Create config/odoo.conf** (file, not directory)
   ```ini
   [options]
   addons_path = /mnt/extra-addons,/mnt/oca
   admin_passwd = admin_dev_password
   db_host = db
   db_port = 5432
   db_user = odoo
   db_password = odoo_dev_password
   dev_mode = reload,qweb,werkzeug,xml
   ```

3. **Populate oca-addons/** with dependencies
   - Option A: Git submodules for each OCA repo
   - Option B: Symlink to canonical `~/Documents/GitHub/odoo-ce/addons/external/oca`
   - Option C: Document that users must clone separately

### Priority 2: Add Dev Scripts

Create `scripts/dev/` with:
```bash
scripts/dev/
├── up.sh           # docker compose up -d
├── down.sh         # docker compose down
├── reset-db.sh     # Drop/recreate odoo_dev database
├── health.sh       # curl http://localhost:8069/web/health
└── logs.sh         # docker compose logs -f odoo
```

### Priority 3: CI Validation

Add `.github/workflows/dev-sandbox-verify.yml`:
- Validate `docker-compose.yml` syntax
- Check `config/odoo.conf` exists and is valid
- Shellcheck for all scripts
- List expected addons

### Priority 4: Clean Up Git State

**Decision needed**: What is this repo's purpose?

**Option A**: Pure Odoo dev sandbox
- Remove `out/insightpulseai/` (design artifacts)
- Remove Node.js extraction scripts
- Focus on Odoo modules only

**Option B**: Multi-purpose workspace
- Create separate directories: `odoo/`, `design-system/`, `tools/`
- Clear README explaining dual purpose

**Current uncommitted state**:
- 32 staged files (design extraction)
- 7 untracked directories (actual Odoo workspace)

Suggest: **Unstage design artifacts**, commit Odoo structure first.

### Priority 5: Documentation

Create `docs/runbooks/DEV_SANDBOX.md` with:
- Prerequisites (Docker Desktop, Git)
- First-time setup steps
- Daily development workflow
- Troubleshooting common issues
- How to add OCA modules

---

## Comparison to Canonical SSOT

| Aspect | Canonical (`odoo-ce/sandbox/dev`) | This Repo (`odoo-dev-sandbox`) |
|--------|-----------------------------------|--------------------------------|
| docker-compose.yml | ✅ Present, working | ❌ Missing |
| Odoo config | ✅ Valid file | ❌ Empty directory |
| Custom addons | ✅ Mounted from `./addons` | ✅ Present in `./addons` |
| OCA addons | ✅ Mounted from `../../addons/external/oca` | ❌ Empty `./oca-addons` |
| Scripts | ✅ Full `scripts/` directory | ⚠️ Partial (audit only) |
| Documentation | ✅ README, QUICK_START, VERIFICATION_CHECKLIST | ⚠️ Minimal |
| Git state | ✅ Clean commits | ❌ Uncommitted, no history |

**Verdict**: This repo is **NOT** a canonical dev sandbox. It's either:
- An incomplete copy
- An experimental workspace
- A merge/extraction artifact

---

## Action Plan

### Phase 1: Establish Baseline (Day 1)
1. ✅ Create this REPORT.md
2. Create working docker-compose.yml (adapted from canonical)
3. Fix config/odoo.conf (delete directory, create file)
4. Add .env.example
5. Add .gitignore
6. Commit: "feat: establish dev sandbox baseline"

### Phase 2: Operational Scripts (Day 1)
1. Create scripts/dev/ with 5 essential scripts
2. Make all scripts executable
3. Test: `scripts/dev/up.sh && scripts/dev/health.sh`
4. Commit: "feat: add dev operation scripts"

### Phase 3: CI + Validation (Day 2)
1. Add .github/workflows/dev-sandbox-verify.yml
2. Add scripts/verify.sh (runs locally or in CI)
3. Test CI passes
4. Commit: "feat: add CI validation"

### Phase 4: Documentation (Day 2)
1. Create docs/runbooks/DEV_SANDBOX.md
2. Update CLAUDE.md to reference skills (avoid bloat)
3. Add README.md (if missing)
4. Commit: "docs: complete dev sandbox documentation"

### Phase 5: Clean Up (Optional)
1. Decide: Keep or remove `out/insightpulseai/`?
2. Unstage design artifacts if removing
3. Update .gitignore accordingly
4. Commit: "chore: clean up non-Odoo artifacts"

---

## Verification Commands (Post-Implementation)

Run these to confirm working state:

```bash
# 1. Docker config valid
docker compose config

# 2. Services start cleanly
docker compose up -d

# 3. All containers healthy
docker compose ps

# 4. Odoo responds
curl -I http://localhost:8069

# 5. Logs show successful startup
docker compose logs --tail=200 odoo | grep -i "odoo.*running"

# 6. Database accessible
docker compose exec db psql -U odoo -d postgres -c "\l"

# 7. Modules loaded
docker compose exec odoo odoo shell -d odoo_dev --no-http <<< "env['ir.module.module'].search([('state', '=', 'installed')])"
```

---

## Conclusion

**Current State**: Incomplete, non-functional dev workspace
**Canonical Reference**: `~/Documents/GitHub/odoo-ce/sandbox/dev/` (working)
**Gap**: Missing docker-compose, invalid config, empty OCA addons, no scripts

**Recommended Path**:
1. Copy canonical structure
2. Adapt paths for this repo
3. Add missing operational scripts
4. Document everything
5. Decide on design artifacts (keep/remove)

**Estimated Effort**: 4-6 hours to fully normalize and document
**Risk**: Low (can validate against working canonical sandbox)

---

**Next Step**: Proceed with Phase 1 implementation?
