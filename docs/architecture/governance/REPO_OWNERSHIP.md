# Repo Ownership Doctrine

> Canonical mapping of repo directories to platform planes and ownership boundaries.
> Cross-referenced by: `ACTIVE_PLATFORM_BOUNDARIES.md`, `AZURE_NATIVE_TARGET_STATE.md`
> Updated: 2026-03-25

---

## Operating Split

| Repo / Directory | Plane | Canonical Role |
|------------------|-------|----------------|
| `.github/` | SDLC | Reusable workflows, policy enforcement, CI agent orchestration, GitHub Actions |
| `spec/` | SDLC | Spec-driven entry point: requirements, plans, tasks (Spec Kit) |
| `templates/` | SDLC | Project/module/spec templates |
| `agents/` | AI | Personas, skills, judges, evals, prompt contracts for Pulser + SDLC gates |
| `infra/azure/` | Infrastructure | Azure substrate: ACA, Front Door, Foundry, Doc Intelligence, Key Vault, networking |
| `infra/ai/` | AI | Provider router, creative generation, eval runner |
| `infra/azure/dns/` | Infrastructure | Azure-managed DNS and certificate configuration |
| `data-intelligence/` | Data | Databricks-owned: notebooks, DLT pipelines, Unity Catalog schemas, ML |
| `web/` | Frontend | Browser-facing Pulser widget, landing pages, SaaS, marketing, ops UI |
| `odoo/` / `addons/ipai/` | ERP | Transactional SoR: modules, config, migrations, Odoo-side embeddings |
| `addons/oca/` | ERP | OCA community modules (read-only, submodule-pinned) |
| `platform/` | Control Plane | Thin SSOT: contracts, schemas, registry, governance config |
| `ssot/` | Governance | Intended-state truth: agent surfaces, creative policy, architecture policy |
| `design/` | Brand | Design tokens, brand assets, Figma exports |
| `docs/` | Documentation | Architecture authority: ADRs, doctrine, contracts, evidence |
| `automations/` | Archive | n8n workflows (retiring — see `RETIRED_SERVICES.md`) |
| `prompts/` | AI | Versioned prompt library (Gemini image, etc.) |

## Odoo Application Layers (4-Layer Benchmark)

`odoo/` owns four application-local layers, benchmarked against Odoo 18 documentation:

### Layer 1: General / Foundational

Users, companies, multi-company, calendars, email, VoIP, IoT, import/admin, developer mode, Odoo basics.

- Benchmark: <https://www.odoo.com/documentation/19.0/applications/general/>
- Modules: `base`, `mail`, `calendar`, `contacts`, `web`, `auth_*`, core config

### Layer 2: Integration Workflows

Payments, tax connectors, bank sync, document digitization, marketplace connectivity.

- Benchmark: <https://www.odoo.com/documentation/19.0/applications/general/integrations.html>
- Modules: `payment_*`, `account_bank_*`, `ipai_document_intelligence`, marketplace bridges

### Layer 3: Services Workflows

Project, timesheets, planning, field service, helpdesk, service-linked appointments/calendar/chat.

- Benchmark: <https://www.odoo.com/documentation/19.0/applications/services.html>
- Modules: `project`, `hr_timesheet`, `planning`, `helpdesk` (ipai bridge), `appointment`, `im_livechat`

### Layer 4: Finance Workflows

Chart of accounts, journals, multi-currency, tax units, invoices, vendor bills, payments, bank sync/reconciliation, analytic accounting, budgets, year-end closing, tax computation, fiscal positions, expenses, approvals, reimbursements, reinvoicing, finance localization (Philippines).

- Benchmark: <https://www.odoo.com/documentation/19.0/applications/finance/accounting.html>
- Modules: `account`, `account_payment`, `analytic`, `hr_expense`, `ipai_finance_ppm`, `ipai_bir_*`, `ipai_finance_close_seed`

### Azure Platform Substrate (Owned by `infra/`)

Front Door / edge / DNS / certificates, Entra ID / identity, Key Vault / secrets, Foundry / AI hub, Document Intelligence infrastructure, Databricks infrastructure, Azure OpenAI, AI Search, runtime substrate (ACA, PG, networking), observability (App Insights, Log Analytics, Monitor).

- Benchmark: SAP on Azure reference patterns
- Owner: `infra/azure/`

### Authority Statement

> Odoo owns application-local workflow truth. Azure owns mission-critical platform substrate.
> Pulser assists both but owns neither. `agents/` owns Pulser behavior only -- personas, skills, evals, prompts, contracts -- NOT finance/service workflow truth (that is in `odoo/`).

---

## Boundary Rules

### What lives where

| Asset Type | Canonical Location | Never In |
|-----------|-------------------|----------|
| Pulser widget UI (React) | `web/packages/pulser-widget/` | `agents/`, `platform/`, `odoo/` |
| Pulser agent behavior | `agents/` | `web/`, `odoo/`, `infra/` |
| Pulser in Odoo (module) | `addons/ipai/ipai_ai_copilot/` | `agents/`, `web/` |
| Eval rubrics & judges | `agents/evals/` | `infra/`, `platform/`, `web/` |
| Creative generation code | `infra/ai/provider_router/` | `agents/`, `web/` |
| Databricks notebooks | `data-intelligence/` | `platform/`, `infra/`, `agents/` |
| Azure IaC (Bicep/Terraform) | `infra/azure/` | `platform/`, `docs/` |
| Brand assets & tokens | `design/` | `web/public/` (derived copies only) |
| Foundry agent deployment | `infra/azure/foundry/` | `agents/` (agents/ owns behavior, not deployment) |
| GitHub Actions workflows | `.github/workflows/` | `infra/`, `platform/` |
| Spec bundles | `spec/<bundle-name>/` | `docs/`, `platform/` |

### Cross-boundary rules

1. **`agents/` owns behavior, `infra/` owns deployment.** A Pulser agent's prompts/skills/judges live in `agents/`. Its Foundry deployment config lives in `infra/azure/foundry/`.

2. **`data-intelligence/` owns transformation, `platform/` owns contracts.** DLT pipeline code lives in `data-intelligence/`. The schema contract that other services depend on lives in `platform/contracts/`.

3. **`web/` owns UI, `agents/` owns logic.** The Pulser chat widget's React code lives in `web/`. The routing/orchestration logic that decides what happens when a user asks a question lives in `agents/`.

4. **`odoo/` is self-contained for Odoo concerns.** Odoo modules, config, migrations, and Odoo-native integrations (mail, OIDC) live in `addons/ipai/`. Cross-system integrations (Odoo↔Foundry, Odoo↔Databricks) are bridge modules in `addons/ipai/` or thin adapters in `platform/bridges/`.

5. **`ssot/` is intended state, `docs/` is architecture authority.** SSOT YAML files describe what the system *should* be. Architecture docs describe *why* and provide decision records.

## Platform Planes (Summary)

```
┌──────────────────────────────────────────────────────────┐
│  SDLC Plane: .github/ + spec/ + templates/               │
│  (Spec Kit → Coding Agent → Quality Gate → Deploy)        │
├──────────────────────────────────────────────────────────┤
│  AI Plane: agents/ + infra/ai/ + Foundry                  │
│  (Pulser behavior, eval, creative gen, orchestration)     │
├──────────────────────────────────────────────────────────┤
│  Data Plane: data-intelligence/ + Databricks + Power BI   │
│  (Lakehouse, DLT, Unity Catalog, semantic consumption)    │
├──────────────────────────────────────────────────────────┤
│  ERP Plane: odoo/ + addons/ipai/ + addons/oca/            │
│  (Operational SoR, CRM, HR, Finance)                      │
├──────────────────────────────────────────────────────────┤
│  Frontend Plane: web/                                     │
│  (Pulser widget, landing, SaaS, marketing, ops UI)        │
├──────────────────────────────────────────────────────────┤
│  Infrastructure Plane: infra/azure/                        │
│  (ACA, Front Door, Key Vault, Foundry deploy, DNS, certs) │
├──────────────────────────────────────────────────────────┤
│  Identity Plane: Entra ID (tenant-level, no repo)         │
│  (SSO, agent identity, RBAC, conditional access)          │
└──────────────────────────────────────────────────────────┘
```

---

*This document defines repo boundaries. `ACTIVE_PLATFORM_BOUNDARIES.md` defines what services are active.*
