# Odoo CE Repository Restructure Plan

## Philosophy: CE → OCA → IPAI Layering

```
Native Odoo CE (foundation)
    ↓
OCA Gap-Fill (commodity extensions)
    ↓
IPAI Custom (unique governance + integrations)
```

---

## Current State Analysis

### Addons (28 modules - flat structure)
```
addons/
├── ipai_accounting_firm_pack    # Industry pack
├── ipai_advisor                 # ✅ KEEP (Control Center core)
├── ipai_bir_compliance          # Finance/BIR
├── ipai_ce_cleaner              # Utility
├── ipai_clarity_ppm_parity      # PPM - duplicate?
├── ipai_docs                    # Docs
├── ipai_docs_project            # Docs
├── ipai_equipment               # Equipment tracking
├── ipai_expense                 # Expense
├── ipai_finance_ap_aging        # Finance
├── ipai_finance_bir_compliance  # Finance/BIR - duplicate?
├── ipai_finance_controller_dashboard  # Finance
├── ipai_finance_month_end       # Finance - duplicate?
├── ipai_finance_monthly_closing # Finance - duplicate?
├── ipai_finance_ppm             # Finance/PPM
├── ipai_finance_ppm_closing     # Finance/PPM
├── ipai_finance_ppm_dashboard   # Finance/PPM
├── ipai_finance_ppm_tdi         # Finance/PPM
├── ipai_finance_project_hybrid  # Finance/Project
├── ipai_idp                     # IDP
├── ipai_marketing_agency_pack   # Industry pack
├── ipai_ocr_expense             # OCR/Expense
├── ipai_partner_pack            # Industry pack
├── ipai_portal_fix              # Portal fix
├── ipai_ppm                     # ✅ KEEP (Control Center core)
├── ipai_ppm_monthly_close       # PPM close
├── ipai_project_program         # Project/Program
└── tbwa_spectra_integration     # External integration
```

### OCA Sources (scattered)
- `oca-addons/` - 5 repos (mis-builder, project, purchase-workflow, reporting-engine, server-ux)
- `external-src/` - 14 repos (account-*, calendar, contract, dms, hr-expense, etc.)
- `oca/` - empty placeholder

### Infra (scattered)
- `docker/` - docker-compose, Dockerfile
- `deploy/` - production compose files
- `dev-docker/` - development compose

---

## Target Structure

```
odoo-ce/
├── addons/
│   ├── ipai/                        # Custom modules (namespaced)
│   │   ├── ipai_workspace_core/     # NEW: shared base (mixins, groups, utils)
│   │   ├── ipai_ppm/                # Portfolio/Program/Risk/Allocation
│   │   ├── ipai_advisor/            # Recommendations/Scores/Playbooks
│   │   ├── ipai_workbooks/          # NEW: Workbook registry (Superset/Scout links)
│   │   ├── ipai_connectors/         # NEW: Webhook/sync glue (optional)
│   │   ├── ipai_finance/            # CONSOLIDATED: Finance modules
│   │   ├── ipai_expense/            # Expense + OCR
│   │   └── ipai_equipment/          # Equipment tracking
│   │
│   └── oca/                         # Vendored OCA (read-only, pinned)
│       ├── project/
│       ├── mis-builder/
│       ├── reporting-engine/
│       ├── server-tools/
│       ├── hr-expense/
│       └── ...
│
├── vendor/
│   ├── oca.lock                     # OCA repo pins (commit SHAs)
│   └── oca-sync.sh                  # Deterministic vendor sync
│
├── infra/
│   ├── docker/
│   │   ├── docker-compose.yml       # Primary compose
│   │   ├── docker-compose.prod.yml  # Production overrides
│   │   ├── docker-compose.dev.yml   # Development overrides
│   │   ├── Dockerfile               # Main Odoo image
│   │   ├── Dockerfile.seeded        # Pre-seeded image
│   │   └── odoo.conf                # Odoo configuration
│   ├── ci/
│   │   ├── install-test.sh          # Module install test
│   │   ├── lint.sh                  # Linting
│   │   └── structure-check.sh       # Repo structure guard
│   └── entrypoint.d/                # Init scripts
│
├── supabase/                        # Already exists
│   └── migrations/
│
├── n8n/                             # Move from workflows/
│   └── workflows/
│
├── mattermost/                      # NEW
│   ├── webhook-templates/
│   └── runbooks/
│
├── spec/                            # Already exists
│   └── ipai-control-center/
│
└── .github/workflows/               # CI gates
```

---

## Module Consolidation Plan

### Phase 1: Core Control Center (Keep As-Is)
| Module | Action | Notes |
|--------|--------|-------|
| `ipai_ppm` | ✅ Keep | Portfolio/Program/Risk core |
| `ipai_advisor` | ✅ Keep | Recommendations/Scores/Playbooks |

### Phase 2: Create New Base Modules
| Module | Action | Notes |
|--------|--------|-------|
| `ipai_workspace_core` | 🆕 Create | Shared mixins, groups, utils |
| `ipai_workbooks` | 🆕 Create | Workbook registry for Superset/Scout |
| `ipai_connectors` | 🆕 Create | Webhook endpoints, sync jobs |

### Phase 3: Consolidate Finance Modules
| Current Modules | Target | Notes |
|-----------------|--------|-------|
| `ipai_finance_ppm` | `ipai_finance` | Merge core finance |
| `ipai_finance_ppm_closing` | `ipai_finance` | Merge |
| `ipai_finance_ppm_dashboard` | `ipai_finance` | Merge |
| `ipai_finance_ppm_tdi` | `ipai_finance` | Merge |
| `ipai_finance_ap_aging` | `ipai_finance` | Merge |
| `ipai_finance_controller_dashboard` | `ipai_finance` | Merge |
| `ipai_finance_month_end` | `ipai_finance` | Merge (duplicate) |
| `ipai_finance_monthly_closing` | `ipai_finance` | Merge (duplicate) |
| `ipai_finance_project_hybrid` | `ipai_finance` | Merge |
| `ipai_finance_bir_compliance` | `ipai_finance` | Merge (keep BIR logic) |

### Phase 4: Consolidate Expense Modules
| Current Modules | Target | Notes |
|-----------------|--------|-------|
| `ipai_expense` | `ipai_expense` | Keep |
| `ipai_ocr_expense` | `ipai_expense` | Merge OCR into expense |

### Phase 5: Consolidate/Archive Duplicates
| Module | Action | Notes |
|--------|--------|-------|
| `ipai_clarity_ppm_parity` | Archive | Replaced by `ipai_ppm` |
| `ipai_bir_compliance` | Archive | Merged into `ipai_finance` |
| `ipai_ppm_monthly_close` | Archive | Merged into `ipai_finance` |
| `ipai_project_program` | Archive | Replaced by `ipai_ppm` |

### Phase 6: Keep Separate (Industry Packs)
| Module | Action | Notes |
|--------|--------|-------|
| `ipai_accounting_firm_pack` | Keep separate | Industry-specific |
| `ipai_marketing_agency_pack` | Keep separate | Industry-specific |
| `ipai_partner_pack` | Keep separate | Industry-specific |

### Phase 7: Utilities & Integrations
| Module | Action | Notes |
|--------|--------|-------|
| `ipai_ce_cleaner` | Keep | Utility |
| `ipai_portal_fix` | Keep | Portal fix |
| `ipai_docs` | Keep | Documentation |
| `ipai_docs_project` | Keep | Documentation |
| `ipai_equipment` | Keep | Equipment tracking |
| `ipai_idp` | Keep | IDP |
| `tbwa_spectra_integration` | Move to `ipai_connectors` | External integration |

---

## Dependency Graph (Target)

```
ipai_workspace_core (base, mail)
    ↓
ipai_ppm (project, hr, resource, account)
    ↓
ipai_advisor (mail)
    ↓
ipai_workbooks (ipai_advisor - optional)
    ↓
ipai_connectors (ipai_ppm, ipai_advisor)
```

**Rule**: Core modules NEVER depend on connectors.

---

## OCA Lockfile Format

`vendor/oca.lock`:
```yaml
# OCA Module Pinning
# Generated: 2025-12-19
# Odoo Version: 18.0

repos:
  project:
    url: https://github.com/OCA/project.git
    ref: 18.0
    commit: abc123def456
    modules:
      - project_task_default_stage
      - project_template

  mis-builder:
    url: https://github.com/OCA/mis-builder.git
    ref: 18.0
    commit: def456abc789
    modules:
      - mis_builder
      - mis_builder_budget

  reporting-engine:
    url: https://github.com/OCA/reporting-engine.git
    ref: 18.0
    commit: 789abc123def
    modules:
      - report_xlsx
      - report_xlsx_helper

  server-tools:
    url: https://github.com/OCA/server-tools.git
    ref: 18.0
    commit: 123def456abc
    modules:
      - base_technical_user
```

---

## CI Guardrails

### 1. Repo Structure Check
```bash
#!/bin/bash
# infra/ci/structure-check.sh

# Only allow addons/ipai/* and addons/oca/*
for dir in addons/*/; do
  name=$(basename "$dir")
  if [[ "$name" != "ipai" && "$name" != "oca" ]]; then
    echo "ERROR: Invalid addon directory: $dir"
    echo "Only addons/ipai/* and addons/oca/* allowed"
    exit 1
  fi
done

echo "✅ Repo structure valid"
```

### 2. Module Install Test
```bash
#!/bin/bash
# infra/ci/install-test.sh

MODULES="ipai_workspace_core,ipai_ppm,ipai_advisor,ipai_workbooks"
./odoo-bin -d test_db -i "$MODULES" --stop-after-init --log-level=warn
```

### 3. No Restart Loop Check
```bash
#!/bin/bash
# Ensure no --stop-after-init + restart: unless-stopped combo
grep -r "stop-after-init" infra/docker/*.yml && \
grep -r "restart: unless-stopped" infra/docker/*.yml && \
echo "ERROR: Potential restart loop" && exit 1
```

---

## Migration Steps

### Step 1: Create Directory Structure
```bash
mkdir -p addons/ipai addons/oca
mkdir -p vendor
mkdir -p infra/{docker,ci,entrypoint.d}
mkdir -p n8n/workflows
mkdir -p mattermost/{webhook-templates,runbooks}
```

### Step 2: Move IPAI Modules
```bash
# Move all ipai_* to addons/ipai/
mv addons/ipai_* addons/ipai/

# Move tbwa to ipai_connectors later
```

### Step 3: Consolidate OCA
```bash
# Merge oca-addons/ and external-src/ into addons/oca/
mv oca-addons/* addons/oca/
mv external-src/* addons/oca/
```

### Step 4: Move Infra
```bash
mv docker/* infra/docker/
mv deploy/*.yml infra/docker/
```

### Step 5: Create Lockfile
```bash
# Generate oca.lock from current pinned commits
./vendor/oca-sync.sh generate > vendor/oca.lock
```

### Step 6: Update odoo.conf
```ini
[options]
addons_path = /mnt/odoo/addons/ipai,/mnt/odoo/addons/oca,/mnt/odoo/odoo/addons
```

### Step 7: Add CI Gates
- Add `.github/workflows/repo-structure.yml`
- Update existing CI to use new paths

---

## Rollback Plan

If migration fails:
1. Git revert to pre-migration commit
2. Restore original `addons/` structure
3. Restore original `docker/`, `deploy/` locations

---

## Success Criteria

- [ ] All modules in `addons/ipai/` or `addons/oca/`
- [ ] OCA pinned via `vendor/oca.lock`
- [ ] Infra consolidated in `infra/`
- [ ] CI passes with new structure
- [ ] `odoo.conf` addons_path updated
- [ ] No restart loops in docker-compose
- [ ] No QWeb xmlid collisions

---

*Plan created: 2025-12-19*
*Target completion: Incremental over multiple PRs*
