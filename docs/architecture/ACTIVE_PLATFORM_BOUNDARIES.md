# Active Platform Boundaries

> Canonical map of active vs retired services for InsightPulseAI.
> Cross-referenced by: `RETIRED_SERVICES.md`, `AZURE_NATIVE_TARGET_STATE.md`, `PULSER_MINIMAL_RUNTIME.md`
> Updated: 2026-03-25

---

## Active Plane (Azure-Native Minimal Set)

| Service | Role | Runtime | Owner |
|---------|------|---------|-------|
| **Microsoft Entra ID** | Identity, SSO, agent identity (Agent ID preview) | Azure-native | Platform |
| **Azure Front Door** | Edge routing, TLS termination, WAF | Azure-native | Infra |
| **Odoo CE 19** | Operational system of record (ERP, CRM, HR, Finance) | ACA (`ipai-odoo-dev-web`) | ERP |
| **Pulser** | AI assistant family (Diva, Studio, Genie, Docs, Ask Pulser) | ACA + Foundry agents | Agents |
| **Azure AI Foundry** | Agent runtime, orchestration, MCP hosting | Azure-native | Agents |
| **Azure AI Document Intelligence** | OCR, document extraction, BIR form processing | Azure-native | Data |
| **Azure Databricks** | Lakehouse, DLT pipelines, Unity Catalog, ML serving | Azure-native | Data |
| **Power BI** | Business-facing reporting, dashboards | Azure-native (SaaS) | Data |
| **Azure Key Vault** | Secrets, certificates, managed identity binding | Azure-native | Platform |
| **Azure Container Apps** | Application hosting (all services) | Azure-native | Infra |
| **Azure DevOps** | CI/CD pipelines, promotion gates | Azure-native | Platform |
| **Azure Monitor** | Observability, Application Insights | Azure-native | Platform |
| **Cloudflare** | Authoritative DNS (proxy mode off) | External | Infra |
| **Zoho** | SMTP outbound mail (`insightpulseai.com`) | External | Comms |

## Retired Plane (Decommission Targets)

| Service | Reason | Replacement | Retire Date | Status |
|---------|--------|-------------|-------------|--------|
| **Supabase** (self-hosted VM) | Non-Azure-native, operational burden | Entra (auth), Databricks (data), ACA (functions) | 2026-03-25 | **Decommissioned** — VM deleted, DNS removed |
| **n8n** | Workflow automation replaced by Foundry agents + DevOps pipelines | Azure AI Foundry + DevOps | 2026-03-25 | **Decommissioned** — VM deleted, DNS removed |
| **Plane** | Project management — consolidate to Azure DevOps | Azure DevOps Boards | 2026-03-25 | **Decommissioned** — ACA deleted |
| **Shelf** | Knowledge base — consolidate to Odoo Knowledge + Databricks | Odoo Knowledge module | 2026-03-25 | **Decommissioned** — ACA deleted |
| **Standalone CRM** (`ipai-crm-dev`) | Redundant — Odoo CRM is canonical | Odoo CRM module | 2026-03-25 | **Decommissioned** — ACA deleted |
| **Keycloak** (`ipai-auth-dev`) | Never operationalized — Entra is target IdP | Entra ID | 2026-03-25 | **Decommissioned** — ACA deleted |
| **Cloudflare** (as long-term DNS) | Target: migrate DNS authority to Azure DNS | Azure DNS (when deployed) | TBD | Active (migration planned) |
| **Superset** (as primary BI) | Supplemental only — Power BI is primary | Power BI | 2026-03-21 | Demoted |
| **GitHub Actions** (as CI/CD) | Migrating to Azure DevOps Pipelines | Azure DevOps | 2026-03-21 | Transitional |

## Decision Checklist

Before adding any new service to the active plane:

- [ ] Is it Azure-native or does it require a separate VM/container?
- [ ] Does it duplicate a capability already in the active set?
- [ ] Can the same job be done by Odoo (operational), Foundry (AI), or Databricks (data)?
- [ ] Does it require its own identity system (disqualifying)?
- [ ] What is the operational cost of running it vs the alternative?

**Default answer**: If it is not Azure-native and not Odoo, it does not belong in the active plane.

---

## Per-Repo Purpose Definitions

| Repo / Directory | Purpose | Active Services |
|------------------|---------|-----------------|
| `odoo/` (`addons/ipai/`, `vendor/odoo/`) | ERP system of record — modules, config, migrations | Odoo CE 19, PostgreSQL |
| `web/` | All browser-facing surfaces — landing, SaaS, public pages | ACA, Front Door |
| `agents/` | Pulser behavior definitions — personas, skills, evals, judges | Foundry agents |
| `platform/` | Thin SSOT — control plane config, governance YAML | DevOps, Key Vault |
| `infra/` | Azure-native IaC — ACA, Front Door, DNS, Key Vault, networking | All Azure infra |
| `data-intelligence/` | Databricks notebooks, DLT pipelines, Unity Catalog schemas | Databricks |
| `design/` | Design tokens, brand assets, Figma exports | Static (no runtime) |
| `docs/` | Architecture authority — ADRs, doctrine, contracts | Static (no runtime) |
| `automations/` | Thin/archive — n8n workflows being retired | n8n (retiring) |

## Structural Rules

| Asset | Lives In | Never In |
|-------|----------|----------|
| Pulser widget UI | `web/packages/pulser-widget/` | `agents/`, `platform/` |
| Pulser agent logic | `agents/` | `web/`, `odoo/` |
| Pulser in Odoo | `odoo/addons/ipai/ipai_ai_copilot/` | `agents/`, `web/` |
| Eval rubrics & judges | `agents/evals/` | `infra/`, `platform/` |
| Creative generation code | `infra/ai/provider_router/` | `agents/`, `web/` |
| Databricks notebooks | `data-intelligence/` | `platform/`, `infra/` |
| Azure IaC (Bicep/Terraform) | `infra/azure/` | `platform/`, `docs/` |
| Brand assets & tokens | `design/` | `web/public/` (derived only) |

---

*This document is the authority for what is active. `RETIRED_SERVICES.md` has decommission details.*
