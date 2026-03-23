# Unified Target Architecture — InsightPulse AI Platform

> Consolidated view of all system domains, data flows, integration surfaces,
> and the target end state for the InsightPulse AI platform.
>
> **Architecture model:** Azure SaaS Workload Framework (9 design areas). Within this model, Odoo CE 19
> serves as the transactional system of record, Azure Databricks + ADLS/Delta +
> Unity Catalog serves as the governed data intelligence core, and Microsoft
> Foundry serves as the agent factory and hosted agent runtime plane.
>
> Cross-references:
> - `docs/architecture/PLATFORM_TARGET_STATE.md` (canonical target doctrine)
> - `docs/architecture/WHOLESALE_SAAS_ERP_ON_AZURE.md` (long-form rationale)
> - `ssot/architecture/platform-boundaries.yaml` (machine-readable boundaries)
> - `ssot/architecture/data-flows.yaml` (machine-readable data flows)
> - `docs/architecture/SSOT_BOUNDARIES.md` (domain ownership)
> - `docs/architecture/IPAI_TARGET_ARCHITECTURE.md` (module consolidation)
> - `docs/contracts/DATA_AUTHORITY_CONTRACT.md` (data authority)
> - `docs/contracts/SAP_JOULE_CONCUR_ODOO_AZURE_CONTRACT.md` (SAP integration)
> - `docs/contracts/REVERSE_ETL_GUARDRAILS.md` (reverse ETL)
> - `ssot/integrations/adls-etl-reverse-etl.yaml` (ADLS flows)
> - `ssot/integrations/sap-joule-concur-odoo-azure.yaml` (SAP flows)
> - `ssot/finance/unified-system.yaml` (finance system)

---

## 1. Platform Identity

| Attribute | Value |
|-----------|-------|
| Platform | InsightPulse AI |
| Domain | `insightpulseai.com` |
| Runtime | Azure Container Apps (`southeastasia`) |
| Edge | Azure Front Door (`ipai-fd-dev`) |
| ERP | Odoo CE 19.0 + OCA + `ipai_*` |
| Database | PostgreSQL 16 (Odoo-local) |
| Control Plane | Supabase (`spdtwktxdalcfigzeqrz`) |
| Analytical Lake | Azure Data Lake Storage Gen2 |
| AI Compute | Azure AI Foundry |
| BI | Power BI (mandatory; live connection to Unity Catalog) |
| Automation | n8n (self-hosted on Azure) |
| Identity | Microsoft Entra ID (SSO plane) |
| Chat | Slack |
| DNS | Cloudflare (delegated from Spacesquare) |
| Mail | Zoho SMTP (`smtp.zoho.com:587`) |
| Secrets | Azure Key Vault (`kv-ipai-dev`) |
| Productivity Surface | Microsoft 365 Copilot / Copilot Agents |

---

## 2. Target End State — System Topology

```
                          ┌─────────────────────────────┐
                          │     Microsoft Entra ID       │
                          │   (Identity / SSO Plane)     │
                          └──────┬──────────┬────────────┘
                                 │          │
                    SAML/OIDC    │          │   SAML/OIDC
                                 │          │
              ┌──────────────────▼──┐  ┌────▼──────────────────┐
              │   SAP Concur        │  │   SAP Joule            │
              │   (Expense/Travel)  │  │   (Conversational AI)  │
              │   SoR: T&E docs     │  │   Read + bounded write │
              └──────────┬──────────┘  └────┬──────────────────┘
                         │                  │
                    Concur API         Joule → Azure relay
                    (expense sync)     (no direct Odoo writes)
                         │                  │
    ┌────────────────────▼──────────────────▼──────────────────────────┐
    │                                                                  │
    │                    Azure Container Apps                           │
    │                    (`cae-ipai-dev`, southeastasia)                │
    │                                                                  │
    │  ┌──────────────┐  ┌──────────────┐  ┌────────────────────────┐ │
    │  │  Odoo CE 19   │  │  n8n         │  │  Relay Functions       │ │
    │  │  (ERP / SoR)  │  │  (Automation)│  │  (Joule mediation)     │ │
    │  │  Port 8069    │  │              │  │                        │ │
    │  └──────┬────────┘  └──────┬───────┘  └────────────────────────┘ │
    │         │                  │                                      │
    │         │ PostgreSQL 16    │ Webhooks                             │
    │         ▼                  ▼                                      │
    │  ┌──────────────┐  ┌──────────────┐                              │
    │  │  Odoo DB      │  │  Slack       │                              │
    │  │  (local PG)   │  │  (ChatOps)   │                              │
    │  └──────────────┘  └──────────────┘                              │
    │                                                                  │
    └──────────────────────────┬───────────────────────────────────────┘
                               │
                    Azure Front Door (TLS, WAF, routing)
                               │
    ┌──────────────────────────▼───────────────────────────────────────┐
    │                                                                  │
    │                    Supabase (SSOT / Control Plane)                │
    │                    `spdtwktxdalcfigzeqrz`                        │
    │                                                                  │
    │  Auth │ Edge Functions │ Realtime │ pgvector │ Vault │ Storage   │
    │                                                                  │
    └──────────────────────────┬───────────────────────────────────────┘
                               │
                          ETL (batch)
                               │
    ┌──────────────────────────▼───────────────────────────────────────┐
    │                                                                  │
    │              Azure Data Lake Storage Gen2                        │
    │              (`adlsipaidev`, southeastasia)                      │
    │                                                                  │
    │  raw/bronze/ │ standardized/silver/ │ curated/gold/              │
    │  reverse_etl_exports/ │ rejected/quarantine/ │ audit/            │
    │                                                                  │
    └──────────────────────────┬───────────────────────────────────────┘
                               │
                    ┌──────────┼──────────┐
                    │          │          │
              ┌─────▼────┐ ┌──▼───────┐ ┌▼──────────────┐
              │ Power BI  │ │ Azure AI │ │ Reverse ETL   │
              │ (BI/viz)  │ │ Foundry  │ │ (bounded)     │
              │ (ML/AI)   │ │ (ML/AI)  │ │               │
              └───────────┘ └──────────┘ └───────────────┘
```

---

## 3. System Authority Model

Every system has exactly one role. No system may claim authority beyond its designation.

| System | Role | Owns | Does NOT Own |
|--------|------|------|-------------|
| **Odoo CE 19** | System of Record (SoR) | Accounting, invoicing, projects, tasks, BIR filings, employees, vendors, analytic accounts, expense documents | Identity, platform events, vector embeddings |
| **Supabase** | Single Source of Truth (SSOT) | Platform control plane, app metadata, workflow state, vector embeddings, agent memory, Auth identity, Edge Function state | ERP data, accounting, HR |
| **ADLS Gen2** | Analytical Lake | Replicated bronze/silver/gold datasets, ML features, BI marts, reverse ETL staging | Nothing operational |
| **Azure AI Foundry** | Compute Only | Model training, scoring, hosting, agent runtime, tracing, evaluations | No data ownership |
| **Document Intelligence** | Extraction Authority | Specialized OCR, invoice/receipt parsing, document classification | No operational state |
| **SAP Concur** | SoR (T&E) | Expense reports, travel bookings, invoice captures | ERP posting, tax compliance |
| **SAP Joule** | Copilot Surface | Conversational interface, Microsoft 365 interop | No data ownership, no direct writes |
| **Power BI** | Presentation Only | BI dashboards and reports | No data ownership |
| **n8n** | Automation | Workflow orchestration, event routing | No data ownership |
| **Slack** | Communication | ChatOps, notifications, alerts | No data ownership |
| **Cloudflare** | Edge DNS | DNS resolution, CDN | No data ownership |
| **Azure Key Vault** | Secrets Store | All credentials, tokens, API keys | No application data |
| **Microsoft Entra ID** | Identity Plane | SSO federation, SAML/OIDC tokens | No application data |
| **Databricks Apps** | Data Agent Runtime | RAG, lakehouse retrieval, data-intelligence agents (ResponsesAgent) | Transactional SoR |
| **M365 Copilot** | Productivity Surface | User-facing assistant, delivery channel | Not a core runtime, no data ownership |

---

## 4. Data Flow Architecture

### 4.1 ETL Flows (Inbound to ADLS)

```
Supabase ──► Databricks Bronze    (incremental batch, daily/hourly)
  auth.users, platform_events, ops.task_queue

Odoo ──► Fabric Mirroring ──► OneLake/Bronze (CDC)
  account.move, project.project, hr.employee, bir.tax.return

SAP Concur ──► Odoo         (API sync, on-submit/daily)
  Expense reports → account.move (draft)
```

### 4.2 Transform Flows (ADLS Internal)

```
Bronze (raw Delta/UniForm, append-only, schema-on-read)
  ↓ dedup, type casting, null handling (Databricks)
Silver (normalized, typed, deduplicated Delta)
  ↓ business logic, aggregation, cross-source resolution (dbt)
Gold (curated Delta, business-ready)
  ├── finance/       (budget, actuals, variance)
  ├── projects/      (portfolio, resource, timeline)
  ├── compliance/    (BIR filing status, deadlines)
  ├── platform/      (user activity, events)
  └── ml_features/   (feature tables for Azure AI)
```

### 4.3 Reverse ETL Flows (Outbound from ADLS)

All reverse ETL is **bounded, typed, and contract-governed**.

| Flow | Source | Target | Type | Guard |
|------|--------|--------|------|-------|
| ML risk scores | ADLS gold | Supabase `_risk_score` | `scoring_writeback` | Enrichment column only |
| Dashboard refresh | ADLS gold | Supabase mat tables | `read_model_refresh` | Full table replace |
| Budget forecast | ADLS gold | Odoo `x_forecast_*` | `enrichment_writeback` | Enrichment fields only |
| Anomaly alerts | ADLS gold | Slack via n8n | `notification_trigger` | Alert payload only |

### 4.4 SAP Integration Flows

| Flow | Source | Target | Mediation |
|------|--------|--------|-----------|
| Expense sync | SAP Concur | Odoo `account.move` (draft) | Azure relay function |
| Joule read | SAP Joule | Odoo (read-only) | Azure relay function |
| Joule bounded write | SAP Joule | Odoo `x_forecast_*` | Azure relay + field guard |
| Entra SSO | Entra ID | SAP Concur + Odoo + M365 Copilot | SAML/OIDC federation |
| M365 Copilot Channel | M365 Agents SDK | `agent-platform` APIs | Integration surface |

---

## 5. Odoo Module Target State

From 109 modules → 60 consolidated modules across 8 layers:

| Layer | Module Count | Key Modules |
|-------|-------------|-------------|
| **Core** | 5 | `ipai_dev_studio_base`, `ipai_workspace_core`, `ipai_ce_branding`, `ipai_tenant_core`, `ipai_module_gating` |
| **Platform** | 7 | `ipai_platform_theme`, `ipai_platform_audit`, `ipai_platform_approvals`, `ipai_platform_workflow`, `ipai_platform_permissions`, `ipai_ui_brand_tokens`, `ipai_web_icons_fluent` |
| **AI/Agents** | 7 | `ipai_ai_core`, `ipai_ai_agents`, `ipai_ai_prompts`, `ipai_ai_connectors`, `ipai_ai_provider_kapa`, `ipai_ai_copilot`, `ipai_ai_search` |
| **Finance** | 5 | `ipai_finance_ppm` (unified), `ipai_finance_close_seed`, `ipai_bir_tax_compliance`, `ipai_bir_notifications`, `ipai_bir_plane_sync` |
| **HR** | 4 | `ipai_hr_payroll_ph`, `ipai_hr_expense_liquidation`, `ipai_hr_attendance`, `ipai_hr_leave` |
| **Services** | 5 | `ipai_helpdesk`, `ipai_approvals`, `ipai_planning`, `ipai_timesheet`, `ipai_documents_ai` |
| **Connectors** | 5 | `ipai_slack_connector`, `ipai_superset_connector`, `ipai_ops_connector`, `ipai_pulser_connector`, `ipai_llm_supabase_bridge` |
| **WorkOS** | 5 | `ipai_workos_core`, `ipai_workos_blocks`, `ipai_workos_canvas`, `ipai_workos_docs`, `ipai_workos_search` |

**EE Parity Target**: >= 80% weighted parity score via `CE + OCA + ipai_*`.

---

## 6. Finance Unified System

Single governance model across all finance-related modules:

```
ipai_finance_ppm (core)
├── Budget management (PPM)
├── Month-end close orchestration
├── BIR tax compliance (1601-C, 2316, Alphalist)
├── Expense automation + liquidation
└── Financial reporting (via OCA + Superset)

Seed format: Odoo XML/CSV (canonical), JSON (derived export)
Tax tables: TRAIN Law, SSS, PhilHealth, Pag-IBIG (2025 rates)
```

**Contract**: `spec/finance-unified/constitution.md` — 8 immutable rules.

---

## 7. Security Architecture

```
┌──────────────────────────────────────────────────────┐
│                  Azure Key Vault                      │
│                  (`kv-ipai-dev`)                      │
│                                                      │
│  Supabase credentials ──► managed identity           │
│  Odoo API tokens ──► managed identity                │
│  Zoho SMTP creds ──► managed identity                │
│  SAP Concur API key ──► managed identity             │
│  ADLS access ──► Storage RBAC + managed identity     │
│                                                      │
│  Secrets in repo: PROHIBITED                         │
└──────────────────────────────────────────────────────┘

Identity flow:
  Entra ID ──SAML/OIDC──► SAP Concur
  Entra ID ──SAML/OIDC──► Odoo (via ipai_auth_oidc)
  Supabase Auth ──JWT──► Edge Functions, Realtime, pgvector
  Managed Identity ──► ADLS, Key Vault, AI Foundry
```

---

## 8. Observability Stack

| Layer | Tool | Data Source |
|-------|------|-------------|
| Infrastructure | Azure Monitor | Container Apps, Front Door, ADLS |
| Application | Odoo logs + n8n execution logs | Container stdout/stderr |
| Data Pipeline | ADLS `audit/` zone | Run logs, watermarks, lineage, quarantine |
| BI | Power BI | Databricks SQL / Unity Catalog |
| Alerting | Slack via n8n | Pipeline failures, anomaly detection |
| Schema | ADLS `audit/evidence/` | Schema drift detection per flow |

---

## 9. Target End State Milestones

### Phase 1 — Foundation (Current)
- [x] Odoo CE 19 on Azure Container Apps
- [x] Supabase as control plane (Auth, Edge Functions, pgvector)
- [x] Cloudflare DNS + Azure Front Door
- [x] Zoho SMTP for outbound mail
- [x] Slack for ChatOps
- [x] n8n for automation
- [x] Spec bundle governance (`spec/`, `ssot/`, `docs/contracts/`)

### Phase 2 — Data Lake
- [ ] Provision ADLS Gen2 (`adlsipaidev`)
- [ ] Supabase → ADLS bronze ETL pipelines
- [ ] Odoo → ADLS bronze ETL pipelines (Extract API)
- [ ] Silver normalization (cross-source entity resolution)
- [ ] Gold curation (finance, projects, compliance, platform marts)

### Phase 3 — Reverse ETL + BI
- [ ] Bounded reverse ETL: scoring writeback, enrichment writeback, read model refresh
- [ ] Power BI connected to Unity Catalog
- [ ] Field-level write guards enforced per contract
- [ ] Idempotency enforcement on all writeback flows

### Phase 4 — SAP Integration
- [ ] Microsoft Entra ID as SSO plane (Concur + Odoo)
- [ ] SAP Concur → Odoo expense ingestion (draft-first)
- [ ] SAP Joule read-only access to Odoo operational data
- [ ] Joule bounded writes to enrichment fields via Azure relay
- [ ] BIR reconciliation across Odoo + Concur expense data

### Phase 5 — AI + ML
- [ ] Azure AI Foundry scoring pipelines (risk, forecast, anomaly)
- [ ] ML feature tables in ADLS gold
- [ ] Scoring writeback to Supabase/Odoo enrichment columns
- [ ] Supabase pgvector for operational RAG (semantic search, agent memory)

### Phase 6 — M365 Copilot Readiness
- [ ] Microsoft 365 Copilot readiness assessment complete
- [ ] M365 Agents SDK established as channel adapter layer
- [ ] Identity/authz posture for Copilot validated in Entra
- [ ] Pre-built vs build-your-own agent policy defined

### Phase 6 — EE Parity
- [ ] >= 80% weighted EE parity score
- [ ] All P0 modules live: bank reconciliation, financial reports, payroll, approvals
- [ ] All P1 modules live: helpdesk, planning, timesheet, asset management
- [ ] Parity CI gate enforced (`ee_parity_gate.sh`)

---

## 10. Prohibited Patterns

| Pattern | Why | Alternative |
|---------|-----|-------------|
| ADLS as operational data source | ADLS is analytical only | Read from Odoo/Supabase directly |
| Generic "sync" between systems | Unbounded, untyped | Use classified reverse ETL types |
| Direct Joule → Odoo writes | Bypasses mediation + audit | Route through Azure relay function |
| M365 Copilot as Runtime | Architectural blur | Use `agent-platform` as core runtime |
| Databricks as Universal Agent Runtime | Scope creep | Reserve for data-intelligence/RAG agents; use Foundry for operational agents |
| Foundry Local in Production | Reliability risk | Local prototyping/dev only; use Microsoft Foundry for production |
| Posted accounting entry mutation | Regulatory immutability | Create reversal/correction entries |
| Secrets in repo | Security | Azure Key Vault + managed identity |
| Vercel deployments | Deprecated | Azure Container Apps |
| DigitalOcean hosting | Decommissioned | Azure Container Apps |
| Mailgun SMTP | Deprecated | Zoho SMTP |
| Mattermost | Deprecated | Slack |
| `insightpulseai.net` | Deprecated | `insightpulseai.com` |

---

## 11. Settled Decisions (Mandatory Controls)

| Decision | Selection | Status |
|----------|-----------|--------|
| Databricks required? | Yes — mandatory engineering and governance core | Settled |
| Unity Catalog required? | Yes — mandatory governance plane | Settled |
| Delta Lake format? | Mandatory (UniForm on ADLS Gen2) | Settled |
| Primary BI Surface | Power BI (connected to Unity Catalog) | Settled |
| SaaS Design Authority | Azure SaaS Workload Documentation | Settled |
| Fabric Role | Complementary mirroring and semantic integration | Settled |
| Reverse ETL orchestrator | Azure Functions / Databricks Jobs | Settled |
| ADLS region | `southeastasia` (co-locate with ACA) | Settled |

---

## 12. Contract Index

All cross-boundary integrations are governed by contracts:

| Contract | File | Governs |
|----------|------|---------|
| Data Authority | `docs/contracts/DATA_AUTHORITY_CONTRACT.md` | Entity-level ownership across all systems |
| Reverse ETL Guardrails | `docs/contracts/REVERSE_ETL_GUARDRAILS.md` | Approved/prohibited ADLS writebacks |
| SAP Joule/Concur/Odoo/Azure | `docs/contracts/SAP_JOULE_CONCUR_ODOO_AZURE_CONTRACT.md` | SAP integration boundaries |
| SSOT Boundaries | `docs/architecture/SSOT_BOUNDARIES.md` | 16-domain ownership map |
| Finance Unified | `spec/finance-unified/constitution.md` | Finance module governance |
| DNS/Email | `docs/contracts/DNS_EMAIL_CONTRACT.md` | DNS + mail configuration |
| Monorepo | `docs/architecture/MONOREPO_CONTRACT.md` | Repository structure |
| Platform Contracts Index | `docs/contracts/PLATFORM_CONTRACTS_INDEX.md` | Master contract registry |

---

*Last updated: 2026-03-13*
