# Plan — Unified Finance System

> Implementation plan for unifying BIR tax compliance, month-end close,
> and finance PPM as one coordinated system.

---

## 1. Active Module Graph

```
┌─────────────────────────────────────────────────────────────┐
│                    Active Modules (5)                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Foundation Layer (standalone, no IPAI deps):               │
│  ┌──────────────────────┐  ┌──────────────────────────────┐│
│  │ ipai_finance_ppm     │  │ ipai_bir_tax_compliance      ││
│  │ v18.0.1.0.0          │  │ v18.0.1.0.0 → 18.0.1.0.0    ││
│  │ project, account,    │  │ base, mail, account, project ││
│  │ analytic, mail, web  │  │ 36 eBIRForms, dashboard      ││
│  └──────────────────────┘  └──────────┬───────────────────┘│
│                                       │                     │
│  Satellite Layer (depends on BIR):    │                     │
│  ┌────────────────────────────────────┤                     │
│  │                                    │                     │
│  │  ┌─────────────────────┐  ┌───────┴──────────────┐      │
│  │  │ ipai_bir_notifications│ │ ipai_bir_plane_sync  │      │
│  │  │ v18.0.1.0.0          │ │ v18.0.1.0.0          │      │
│  │  │ mail alerts, cron    │ │ Plane.so bidirectional│      │
│  │  │ installable: False   │ │ installable: False    │      │
│  │  └─────────────────────┘  └──────────────────────┘      │
│                                                             │
│  Data Layer (no code, only seed data):                      │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ ipai_finance_close_seed                             │    │
│  │ v18.0.1.0.0 | 7 XML + 2 CSV                        │    │
│  │ 39 close tasks + 50 BIR tasks + team + milestones   │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│                  Deprecated Modules (2)                      │
├─────────────────────────────────────────────────────────────┤
│  ipai_finance_workflow     → superseded by close_seed       │
│  ipai_finance_tax_return   → migrated to enterprise_bridge  │
└─────────────────────────────────────────────────────────────┘
```

## 2. Deprecated Module Disposition

| Module | Current State | Action | Timeline |
|--------|---------------|--------|----------|
| `ipai_finance_workflow` | `installable: False`, has data files overlapping with `close_seed` | Keep in tree as-is. Already non-installable. Add `DEPRECATED` banner to `__manifest__.py` description if not present. | Phase 1 |
| `ipai_finance_tax_return` | `installable: False`, manifest says "migrated to enterprise_bridge" | Keep in tree as-is. Already marked. No action needed. | Done |

No deletion — deprecated modules stay in the tree with `installable: False`
to preserve git history and avoid breaking references. They are simply
excluded from the active module graph.

## 3. Seed Normalization Plan

### 3.1 Canonical: Odoo XML/CSV

Location: `addons/ipai/ipai_finance_close_seed/data/`

```
01_stages.xml              6 Kanban stages
02_tags.xml                33 project tags (phases + categories + BIR forms)
03_partners_employees.xml  9 team members
04_projects.xml            2 projects (Month-End Close + BIR Tax Filing)
05_milestones.xml          11 milestones
06_tasks_month_end.xml     39 month-end closing tasks
07_tasks_bir_tax.xml       50 BIR tax filing tasks
tasks_month_end.csv        CSV mirror of 06
tasks_bir.csv              CSV mirror of 07
```

These are the authoritative operational seeds. Changes start here.

### 3.2 Derived: JSON Reference

Location: `ipai_finance_closing_seed.json` (repo root)

This file contains BIR form schedules (`ipai.bir.form.schedule` model
instances) with prep/review/approval dates. It is a **reference export**
for external tooling and agent consumption.

**Action**: Add a header comment or companion `README` noting it is derived
from the XML seeds. Do not modify independently.

### 3.3 Deprecated: Supabase SQL

Location: `supabase/seeds/002_finance_seed.sql`

Already marked deprecated (2026-03-09) with note: "Canonical seed data
moved to `data/finance_seed/` subdirectory." Contains expense categories
and approval rules — downstream Supabase projection, not Odoo operational data.

**Action**: No change. Already deprecated in-file.

## 4. Canonical Documentation Ownership

### Create: `docs/modules/FINANCE_UNIFIED_SYSTEM.md`

One document that covers:

- Process model (monthly cycle: close + BIR + PPM)
- Module graph (5 active, 2 deprecated, dependency arrows)
- Seed ownership table (XML = canonical, JSON = derived, SQL = deprecated)
- BIR calendar coverage (36 forms, monthly/quarterly/annual cadences)
- Month-end close flow (5 phases, 39 tasks)
- Clarity/PPM mapping (WBS hierarchy, OKR dashboard, analytic controls)
- Team roles and responsibilities (9 members, 4 roles)
- Test gaps and planned validators

### Existing docs (no deletion, reclassified):

The 24+ existing module doc stubs remain as per-module status reports.
They are subordinate to `FINANCE_UNIFIED_SYSTEM.md` for system-level truth.

## 5. Version Alignment

| Module | Current Version | Target | Action |
|--------|----------------|--------|--------|
| `ipai_bir_tax_compliance` | 18.0.1.0.0 | — | Already aligned |
| `ipai_bir_notifications` | 18.0.1.0.0 | — | Already aligned |
| `ipai_bir_plane_sync` | 18.0.1.0.0 | — | Already aligned |
| `ipai_finance_ppm` | 18.0.1.0.0 | — | Already aligned |
| `ipai_finance_close_seed` | 18.0.1.0.0 | — | Already aligned |

## 6. Installability Assessment

Two satellite modules are currently `installable: False`:

| Module | Why | Recommendation |
|--------|-----|----------------|
| `ipai_bir_notifications` | Placeholder — has manifest + data files but incomplete | Keep `False` until mail templates and cron are validated. Activate when notification logic is tested. |
| `ipai_bir_plane_sync` | Placeholder — requires Plane API configuration | Keep `False` until Plane.so API connectivity is verified. Activate when sync is end-to-end tested. |

These are not deprecated — they are **planned but unfinished**. They remain
in the active module graph but gated behind installability.

## 7. Cross-Repo Capability Sourcing

Do not constrain solution discovery to OCA/project.

The implementation plan must perform a cross-repo addon scan and prefer
composition over custom development. Thin custom models are allowed only
for capabilities that remain unresolved after adjacent-repo evaluation.

**Anti-pattern**: declaring a custom `ipai_finance_ppm` feature because the
feature is absent from `project` repo alone.

### Adjacent repos to scan

| OCA Repo | PPM-relevant capabilities |
|---|---|
| [helpdesk](https://github.com/OCA/helpdesk) | Issue register substrate (project-linked tickets, SLA, stages) |
| [knowledge](https://github.com/OCA/knowledge) | Governance approvals, decision records (`document_page_approval`, `document_page_project`) |
| [mis-builder](https://github.com/OCA/mis-builder) | KPI rollups, financial reporting, budget vs. actual |
| [project-agile](https://github.com/OCA/project-agile) | Demand/backlog/intake approximation |
| [reporting-engine](https://github.com/OCA/reporting-engine) | Spreadsheet/dashboard composition |
| [account-analytic](https://github.com/OCA/account-analytic) | Analytic budget surfaces, financial rollups |
| [project-reporting](https://github.com/OCA/project-reporting) | Project-level reporting and metrics |

### Capabilities downgraded from "custom" to "candidate composable"

- **Issue register** → OCA Helpdesk has 18.0 modules for project-linked tickets, SLA, related tickets, stage validation, and timesheets
- **Governance approvals / decision records** → OCA Knowledge has 18.0 addons (`document_page_approval`, `document_page_project`)
- **Executive / operational dashboards** → MIS Builder + OCA Spreadsheet + Odoo global-filter dashboard pattern
- **Demand / intake** → not proven solved, but must be tested against project-agile and helpdesk/form intake before declaring custom-only

### Capabilities that remain likely real gaps

- Enterprise capacity planning / optimization
- Advanced drag-and-drop resource scheduling
- Scenario scoring / investment prioritization
- Portfolio-level optimization logic

OCA project discussions still point to forecasts/planning as an open area
rather than a mature, established 18.0 solution.

## 8. Test and Validator Plan

### 7.1 Seed Integrity Tests

File: `addons/ipai/ipai_finance_close_seed/tests/test_seed_integrity.py`

| Test | What it validates |
|------|-------------------|
| `test_stages_complete` | All 6 Kanban stages present and ordered |
| `test_tags_complete` | All 33 tags present (5 phase + 19 category + 9 BIR form) |
| `test_team_members_complete` | All 9 team members have both partner and employee records |
| `test_projects_exist` | Month-End Close and BIR Tax Filing projects created |
| `test_milestones_complete` | All 11 milestones present with correct project assignment |
| `test_close_tasks_count` | Exactly 39 month-end closing tasks across 5 phases |
| `test_bir_tasks_count` | Exactly 50 BIR filing tasks (12 monthly + quarterly + annual) |
| `test_task_stage_refs_valid` | All task stage references resolve to existing stage records |
| `test_task_milestone_refs_valid` | All task milestone references resolve to existing milestones |

### 7.2 BIR Schedule Validation

File: `addons/ipai/ipai_bir_tax_compliance/tests/test_bir_schedules.py`

| Test | What it validates |
|------|-------------------|
| `test_all_monthly_forms_present` | 1601-C, 0619-E, SSS, PhilHealth, Pag-IBIG for each month |
| `test_quarterly_forms_present` | 2550Q, 1601-EQ for Q1–Q4 |
| `test_annual_forms_present` | 1604-CF, 2316, Alphalist |
| `test_filing_deadlines_not_past` | No deadline in seed data is before module install date |
| `test_tax_rates_loaded` | BIR tax rate data records exist |

### 7.3 PPM Smoke Tests

File: `addons/ipai/ipai_finance_ppm/tests/test_ppm_smoke.py`

| Test | What it validates |
|------|-------------------|
| `test_module_installs_clean` | Module installs on empty DB without errors |
| `test_project_extensions_exist` | `ipai_finance_ppm` fields on `project.project` are accessible |
| `test_analytic_extensions_exist` | `ipai_finance_ppm` fields on `account.analytic.account` are accessible |
| `test_ppm_import_wizard_loads` | Import wizard form view renders without errors |
| `test_okr_dashboard_action` | Dashboard action record exists and points to valid JS |

### 7.4 Contract Tests

File: `tests/contracts/test_finance_system.py` (repo-level)

| Test | What it validates |
|------|-------------------|
| `test_no_deprecated_modules_installable` | `ipai_finance_workflow` and `ipai_finance_tax_return` remain `installable: False` |
| `test_active_modules_version_aligned` | All 5 active modules have `18.0.x.x.x` version |
| `test_seed_canonical_doc_exists` | `docs/modules/FINANCE_UNIFIED_SYSTEM.md` exists |
| `test_spec_bundle_complete` | All 4 spec files exist in `spec/finance-unified/` |
