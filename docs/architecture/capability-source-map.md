# Capability-to-Source Map — Odoo 18 + OCA + Adapters + OData

> **Locked:** 2026-04-15
> **Authority:** this file (what we consume, from where, for which Microsoft-parity capability)
> **Companions:**
> - [`ssot/governance/upstream-adoption-register.yaml`](../../ssot/governance/upstream-adoption-register.yaml) — adoption posture per repo
> - [`config/addons.manifest.yaml`](../../config/addons.manifest.yaml) — module install manifest
> - [`docs/architecture/data-model-erd.md`](./data-model-erd.md) — schema + ORM layer (BOM v2 aligned)
> - [`docs/architecture/odata-to-odoo-mapping.md`](./odata-to-odoo-mapping.md) — OData Bridge v1
> - [`docs/architecture/booking-surface-microsoft-parity.md`](./booking-surface-microsoft-parity.md) — Bookings parity
> - [`docs/architecture/planner-surface-microsoft-parity.md`](./planner-surface-microsoft-parity.md) — Planner parity
> - [`docs/architecture/revised-bom-target-state.md`](./revised-bom-target-state.md) — BOM v2

---

## Doctrine stack (what consumes what)

```
Layer 0: Odoo CE 18 core       ← vendor/odoo/ (CE upstream, never forked)
Layer 1: OCA repos             ← addons/oca/<repo>/ (vendored submodules, 27 repos today)
Layer 2: ipai_* modules        ← addons/ipai/<module>/ (50 modules today)
Layer 3: Thin adapters         ← platform/contracts/odata/v1/* + ipai_*_bridge modules
Layer 4: External surfaces     ← OData bridge, FastAPI, Foundry, Databricks, Teams
```

Build order per CLAUDE.md: CE → property fields → OCA → adjacent OCA → compose → `ipai_*` last resort.

---

## Layer 1 — OCA repos consumed (27 total, 2026-04-15)

Paths under `addons/oca/`. Each repo contains many modules; we install a subset per [`config/addons.manifest.yaml`](../../config/addons.manifest.yaml).

| # | Repo | Primary role | Covers Microsoft capability |
|---|---|---|---|
| 1 | `account-financial-tools` | AR/AP enhancements, asset mgmt, FX, fiscal-year close | D365 Finance core (accounting) |
| 2 | `account-financial-reporting` | Custom P&L, BS, CF reports | D365 Finance financial reports |
| 3 | `account-invoicing` | Invoice workflow extensions | D365 Finance AR |
| 4 | `account-reconcile` | Bank reconciliation + Pulser recon agent data source | D365 Account Reconciliation Agent |
| 5 | `credit-control` | AR collections, dunning letters | D365 Finance collections |
| 6 | `dms` | Document management (folders, tagging) | SharePoint / Documents pillar |
| 7 | `helpdesk` | Ticket mgmt | D365 Customer Service (EE parity) |
| 8 | `hr-expense` | Expense workflows | D365 Project Operations expense / MS Expense agent |
| 9 | `knowledge` | Wiki-like pages (adjacent to Odoo Files surface) | Microsoft OneNote / Planner kb |
| 10 | `mis-builder` | Financial statement / MIS report builder | Power BI financial reports |
| 11 | `partner-contact` | Contact / address enhancements | Customer Insights basics |
| 12 | `project` | PPM depth (timeline, template, milestone, role, status) | D365 Project Operations + MS Planner Premium |
| 13 | `purchase-workflow` | P2P enhancements | D365 Supply Chain / Procurement |
| 14 | `queue` | `queue_job` background processing | — (infra; supports heavy OCA/ipai_ workloads) |
| 15 | `reporting-engine` | XLSX / BI report generation | Excel export / SSRS parity |
| 16 | `sale-reporting` | Sales KPIs | D365 Sales reporting |
| 17 | `sale-workflow` | Sales order enhancements | D365 Sales |
| 18 | `server-auth` | `auth_oauth`, `auth_oidc`, OIDC providers | Entra ID OAuth/OIDC |
| 19 | `server-backend` | Backend UI enhancements | — (productivity) |
| 20 | `server-brand` | Branding / debranding, portal branding | — (productivity) |
| 21 | `server-env` | Environment-based config | Bicep / Key Vault adjacency |
| 22 | `server-tools` | Auditlog, password security, cron exclusion | D365 auditing baseline |
| 23 | `server-ux` | UX tuning (base_user_role, responsive) | — (productivity) |
| 24 | `social` | `mail.activity.team`, `mail.activity.board` | MS Teams / Outlook mail activities |
| 25 | `timesheet` | Timesheet enhancements | D365 Project Operations timesheet |
| 26 | `web` | Responsive, dialog size, refresher | — (UX) |
| 27 | `ai` | OCA AI experiments (non-baseline on 19.0; per-module verification) | — (optional; verify before adopt) |

**Adoption posture** per [`ssot/governance/upstream-adoption-register.yaml`](../../ssot/governance/upstream-adoption-register.yaml): all 27 are `consume_directly` via git submodule pins.

---

## Layer 2 — `ipai_*` modules (50 total)

```bash
ls addons/ipai/ | wc -l    # → 50
```

Grouped by domain (names as they appear in `addons/ipai/`):

| Domain | Modules | Purpose |
|---|---|---|
| **Foundation** | `ipai_foundation`, `ipai_web_branding` | Platform base, brand + login surface |
| **AI / Agents** | `ipai_ai_core`, `ipai_ai_copilot`, `ipai_ai_widget`, `ipai_ai_platform`, `ipai_ask_ai_azure`, `ipai_ai_channel_actions`, `ipai_agent`, `ipai_copilot_actions`, `ipai_odoo_copilot` | Pulser copilot substrate, agent channels, AI widget |
| **Auth** | `ipai_auth_oidc` *(deprecated 2026-04-14)* | Prior custom OIDC — replaced by OCA `server-auth` per `feedback_no_custom_default` |
| **Finance — AP/AR + Close** | `ipai_finance_ap_ar`, `ipai_finance_close`, `ipai_finance_close_seed`, `ipai_finance_gl` | AP/AR parity + close seed + GL extensions |
| **Finance — PPM / FP&A** | `ipai_finance_ppm`, `ipai_finance_ppm_seed` | Estimate line, forecast version (D365 PO parity) |
| **BIR Compliance** | `ipai_bir_2307`, `ipai_bir_2307_automation`, `ipai_bir_compliance`, `ipai_bir_returns`, `ipai_bir_slsp`, `ipai_bir_tax_compliance`, `ipai_ph_tax_config` | PH regulatory — Monthly + Quarterly + Annual filings |
| **Copilot / MCP / Bridges** | `ipai_aca_proxy`, `ipai_mail_plugin_bridge`, `ipai_enterprise_bridge`, `ipai_knowledge_bridge`, `ipai_google_workspace` | Odoo ↔ external integrations |
| **Compliance & Governance** | `ipai_compliance_approval`, `ipai_compliance_evidence`, `ipai_compliance_graph`, `ipai_branch_profile` | Approval chains, evidence capture |
| **Ops / Expense** | `ipai_expense_ops`, `ipai_expense_wiring`, `ipai_hr_expense_liquidation` | Expense workflow deltas |
| **Document Intelligence** | `ipai_document_extraction`, `ipai_document_intelligence` | Foundry DI integration |
| **Data Intelligence** | `ipai_data_intelligence`, `ipai_ops_api`, `ipai_chat_file_upload` (symlink) | Data lane glue |

**Module philosophy** (per CLAUDE.md): each `ipai_*` must justify its existence via `docs/MODULE_INTROSPECTION.md` (not yet present for all 50 — candidate cleanup work).

---

## Layer 3 — OData Bridge v1 (3 entity sets)

Read-only, tenant-scoped. Lives at [`platform/contracts/odata/v1/`](../../platform/contracts/odata/v1/).

| OData EntitySet | Odoo source model | CDM target | Contract file |
|---|---|---|---|
| `Projects` | `project.project` | `msdyn_project` | [`projects.yaml`](../../platform/contracts/odata/v1/entitysets/projects.yaml) |
| `ProjectTasks` | `project.task` | `msdyn_projecttask` | [`project_tasks.yaml`](../../platform/contracts/odata/v1/entitysets/project_tasks.yaml) |
| `TimeEntries` | `account.analytic.line` | `msdyn_timeentry` / `bookableresourcebooking` | [`time_entries.yaml`](../../platform/contracts/odata/v1/entitysets/time_entries.yaml) |

v1 locked scope: `$metadata + $select + $filter + $top + $skip + $orderby + $count`. Excluded: `$batch`, `$delta`, `$expand`, writes. Contract tests at [`tests/contracts/odata/`](../../tests/contracts/odata/).

Build trigger: 4-box gate per [`odata-to-odoo-mapping.md`](./odata-to-odoo-mapping.md).

---

## Layer 4 — Microsoft capability → IPAI coverage matrix

| Microsoft product / capability | IPAI coverage (layer) | Parity doc |
|---|---|---|
| **D365 Finance** — Accounting + Close + Cash + FP&A | Odoo CE `account` + OCA `account-*` (5 repos) + `ipai_finance_*` (6 modules) | [`odata-to-odoo-mapping.md`](./odata-to-odoo-mapping.md) §7.1 + [`revised-bom-target-state.md`](./revised-bom-target-state.md) §3 |
| **D365 Finance** — Account Reconciliation Agent | OCA `account-reconcile` + Pulser Recon Agent (v0 R2 target) | R2 ship gate |
| **D365 Project Operations** — Core | Odoo CE `project` + `hr_timesheet` + `hr.expense` | [`odata-to-odoo-mapping.md`](./odata-to-odoo-mapping.md) §7.2 |
| **D365 Project Operations** — Integrated with ERP | Above + OCA `project`, `project-reporting`, `account-analytic`, `timesheet`, `hr-expense` + `ipai_finance_ppm` | Same |
| **D365 Project Operations** — Manufacturing | **Deferred** (not in scope) | — |
| **D365 Project Operations** — Time & Expense Agent | OCA `hr-expense` + `ipai_hr_expense_liquidation` + Pulser Tax Guru preflight | R2 target |
| **D365 Customer Insights** — audience + journeys | `data-intelligence/` + Databricks workspace + AI Search + Pulser customer intel | [`data-intelligence-vertical-target-state.md`](../strategy/data-intelligence-vertical-target-state.md) |
| **D365 Business Central** — SMB ERP | Odoo CE core + OCA adjacent repos | [`revised-bom-target-state.md`](./revised-bom-target-state.md) §3 Core Ops plane |
| **Microsoft Planner** — team todo | Odoo `project.task` kanban + OCA `project` | [`planner-surface-microsoft-parity.md`](./planner-surface-microsoft-parity.md) |
| **Microsoft Planner Premium** — timelines / deps / baseline | OCA `project_timeline` + `project_task_predecessor` + `project_template` | Same |
| **Microsoft Bookings** | Odoo CE `appointment` + `ipai_web_branding` data (4 types seeded) + `google_calendar` + `microsoft_calendar` | [`booking-surface-microsoft-parity.md`](./booking-surface-microsoft-parity.md) |
| **Microsoft Teams meeting auto-create** | ⚠️ Needs `ipai_bookings_teams_bridge` thin adapter (build-triggered) | Same |
| **Microsoft SharePoint / Documents** | OCA `dms` + `ipai_document_extraction` + Foundry DI | `ipai_document_*` |
| **Microsoft OneNote / Knowledge** | OCA `knowledge` + Odoo Files (`/odoo/action-399`) | [`work-artifact-placement.md`](../programs/work-artifact-placement.md) Tier 3 |
| **Microsoft Outlook** — calendar sync | Odoo CE `microsoft_calendar` | — |
| **Microsoft Outlook** — mail activities | OCA `social` (`mail_activity_team`, `mail_activity_board`) | — |
| **Microsoft Entra ID** — OAuth / OIDC | OCA `server-auth` (`auth_oauth`, `auth_oidc`) + `ipai_web_branding` data | [`ssot/tenants/tbwa-smp/identity.yaml`](../../ssot/tenants/tbwa-smp/identity.yaml) |
| **Azure Boards** — portfolio + sprints | Direct use; Odoo not a substitute | [`azure-boards-portfolio-target-state.md`](../backlog/azure-boards-portfolio-target-state.md) |
| **Azure Pipelines** — CI/CD | Direct use per CLAUDE.md doctrine #24 (no GHA) | [`ssot/governance/ci-cd-authority-matrix.yaml`](../../ssot/governance/ci-cd-authority-matrix.yaml) |
| **Microsoft Fabric** — OneLake + semantic model | Fabric `fcipaidev` mirror of `pg-ipai-odoo` (live per memory) | [`data-model-erd.md`](./data-model-erd.md) §0 |
| **Microsoft Power BI** | Fabric mirror + OData consumer pattern | [`azure-boards-reporting.md`](../ops/azure-boards-reporting.md) Tier 2 |
| **Microsoft Foundry** (AI) | `ipai-copilot-resource` (Foundry resource + project) + Pulser | [`multitenant-saas-target-state.md`](./multitenant-saas-target-state.md) §4 |
| **Microsoft Dataverse** — entity model | Not adopted. CDM projection via OData bridge + Fabric (read-only) | [`cdm-and-analytics-bridge.md`](./cdm-and-analytics-bridge.md) |
| **Common Data Model** — schemas | Not adopted. Projection-only posture | Same |
| **Health Data Services / FHIR** | Not in default BOM. `regulated_scope` escalation gate | [`revised-bom-target-state.md`](./revised-bom-target-state.md) §Research plane |
| **Microsoft Advertising** | Pulser customer-intel wedge (data-intelligence plane) | [`data-intelligence-vertical-target-state.md`](../strategy/data-intelligence-vertical-target-state.md) |
| **Microsoft Agent Framework** | Foundry Agents SDK (azure-ai-projects) | Per memory `project_foundry_agent_requirements.md` |
| **Microsoft DevOps Boards Analytics** | OData endpoint consumed by Power BI | [`cdm-and-analytics-bridge.md`](./cdm-and-analytics-bridge.md) §4 |

---

## Layer 5 — Consumption provenance (where upstream lives)

| Upstream | Where consumed from | Adoption posture | Update mechanism |
|---|---|---|---|
| Odoo CE 18 | `vendor/odoo/` (upstream mirror) | `consume_directly`, never forked | `git pull origin 18.0` |
| OCA repos (27) | `addons/oca/<repo>/` (git submodules) | `consume_directly` per `upstream-adoption-register.yaml` | `git submodule update --remote` |
| Azure AI Projects SDK (Python) | `pip install azure-ai-projects>=2.0.0` | `consume_directly` | `pyproject.toml` / `requirements.txt` |
| Microsoft Foundry | Service endpoint `services.ai.azure.com` | N/A — service | — |
| Microsoft Fabric | Service (mirror configured) | N/A — service | — |
| Microsoft Graph API | REST endpoint (for future Teams/Planner bridges) | N/A — service | — |
| CDM schemas | Reference (no import) | `clone_as_reference` | Manual when needed |
| Microsoft DevOps SDKs | `azure-devops` CLI + MCP | `consume_directly` | `az extension add` |
| `microsoftgbb/agentic-platform-engineering` | Reference read | `clone_as_reference` | Per [`upstream-adoption-register.yaml`](../../ssot/governance/upstream-adoption-register.yaml) |

---

## Cross-links (everything else consuming this)

- **CDM projection** → [`cdm-and-analytics-bridge.md`](./cdm-and-analytics-bridge.md) — defers CDM mapping until consumer triggers
- **OData external consumers** → [`odata-to-odoo-mapping.md`](./odata-to-odoo-mapping.md) — v1 scope locked
- **Multitenant pattern** → [`multitenant-saas-target-state.md`](./multitenant-saas-target-state.md) — shapes tag model + data isolation
- **Revised BOM** → [`revised-bom-target-state.md`](./revised-bom-target-state.md) — 4 product planes consume these layers
- **Domain BOM** → [`domain-and-web-bom-target-state.md`](./domain-and-web-bom-target-state.md) — 4 web surfaces consume subsets
- **Program template** → [`_PROGRAM_OKR_TEMPLATE.md`](../programs/_PROGRAM_OKR_TEMPLATE.md) — programs consume delivery via Odoo Projects
- **Data-intelligence vertical** → [`data-intelligence-vertical-target-state.md`](../strategy/data-intelligence-vertical-target-state.md) — Smartly/Quilt/Cannes/dataintelligence.ro consumption targets

---

## Coverage honesty table

| Layer | What's real | What's gap |
|---|---|---|
| Odoo CE 18 core | ✅ Vendored at `vendor/odoo/` | None |
| OCA submodules | ✅ 27 repos cloned | Verification of per-module 18.0 install status pending per [`oca-governance.md`](../../.claude/rules/oca-governance.md) |
| `ipai_*` modules | ✅ 50 modules exist | ~42 missing `MODULE_INTROSPECTION.md` per CLAUDE.md rule |
| OData Bridge | ✅ Contracts + tests written | Implementation not built — blocked until a named consumer triggers |
| Microsoft parity docs | ✅ Bookings + Planner covered | D365 Customer Insights parity doc not yet written |
| Consumption provenance | ✅ Upstream register exists | Two references still point at Azure Sub 1 (migration pending) |
| Foundry model deployments | ✅ gpt-4.1 + embedding + gpt-4o-mini | Claude-sonnet-4-6 pending quota grant |
| Foundry project | ❌ Not yet created | Blocked by missing project on `ipai-copilot-resource` |

---

## Update triggers (when this map changes)

- New OCA repo cloned → add row to Layer 1
- New `ipai_*` module created → add row to Layer 2 domain table
- New OData entity set added (post-v1) → add row to Layer 3
- New Microsoft product evaluated → add row to Layer 4
- BOM v2 evolves → update cross-links (currently: §0, §3, §5)
- `upstream-adoption-register.yaml` changes → Layer 5 provenance updates

PR gate: any module install / submodule add must update this file **and** [`config/addons.manifest.yaml`](../../config/addons.manifest.yaml) in the same PR.

---

## Bottom line

```
Consumption:  Odoo CE 18  +  27 OCA repos  +  50 ipai_* modules  +  3 OData entity sets

Microsoft parity target:
  D365 Finance              ← Odoo + 5 OCA account-* repos + 6 ipai_finance_* modules
  D365 Project Operations   ← Odoo project + OCA project/timesheet + ipai_finance_ppm + OData
  D365 Customer Insights    ← Databricks + AI Search + Pulser wedge
  D365 Business Central     ← Odoo CE core + OCA adjacent
  MS Bookings                ← Odoo appointment + ipai_web_branding data
  MS Planner                 ← Odoo project + OCA project
  MS Teams / Outlook         ← OCA social + Odoo calendar sync; thin bridges on trigger
  MS Foundry                 ← Direct consumption (ipai-copilot-resource)
  MS Fabric / Power BI       ← PG mirror + OData

Anti-pattern: fork Odoo or OCA. Never.
Build gate:   thin ipai_* adapter only when triggered by named customer.
```

---

*Last updated: 2026-04-15*
