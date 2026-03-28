# Pulser: AI Assistant for Odoo CE 19 on Azure

> Top-level offering page for the InsightPulse AI copilot product. Public name:
> **Pulser**. Internal/technical name: Copilot. Powered by Microsoft Foundry
> (formerly Azure AI Foundry), hosted on Azure Container Apps, backed by Odoo
> CE 19 + OCA as the system of record.

---

## Purpose and Scope

Pulser is an AI assistant embedded in Odoo Community Edition 19 running on
Microsoft Azure. It enables finance teams, HR operators, supply chain managers,
and executives to interact with ERP data through natural language -- asking
questions, navigating to records, and executing transactional workflows without
leaving the conversational interface.

Pulser is grounded in live Odoo data (the system of record), curated analytics
from Databricks SQL warehouses (the system of insight), and document knowledge
via Azure AI Search. It enforces the same security model as Odoo itself: every
action respects the authenticated user's groups, record rules, and field-level
access controls.

### In scope

| Area | Description |
|------|-------------|
| Odoo CE 19 ERP actions | Read, write, and workflow transitions across all installed modules |
| Microsoft Foundry agent runtime | Model hosting, evaluation, tracing, and governance |
| Azure AI Search document grounding | Policy documents, SOPs, contracts indexed for retrieval |
| Entra ID identity | Workforce (OIDC), workload (managed identity), agent (Foundry-managed) |
| Finance, HR, inventory, CRM tools | Domain-specific copilot tools with appropriate authorization |
| Audit trail and traceability | Every agent action logged with actor, delegated user, and timestamp |
| Power BI analytics surfacing | Summary metrics and trend data from the governed lakehouse |

### Out of scope

| Area | Reason |
|------|--------|
| Direct database SQL access | All data access goes through Odoo ORM or Databricks SQL endpoints |
| Self-hosted LLM inference | Model hosting is exclusively via Microsoft Foundry |
| Third-party vector databases | Azure AI Search is the canonical retrieval surface |
| Basic auth or API key in production | Entra ID is required for all production identity flows |
| Odoo Enterprise-only modules | CE + OCA + IPAI modules only (no Enterprise dependencies) |
| Unlogged autonomous actions | Every mutation must be traceable to a user delegation chain |

---

## Target Users

| Role | What Pulser does for them |
|------|--------------------------|
| Finance Controller | Assists with period close, reconciliation exceptions, AP/AR aging analysis, and journal entry review |
| HR Manager | Surfaces leave balances, contract renewal dates, headcount summaries, and onboarding checklists |
| Operations Manager | Navigates purchase orders, inventory levels, delivery exceptions, and vendor performance |
| Sales Manager | Summarizes pipeline status, overdue quotes, win/loss ratios, and customer account health |
| Executive | Provides KPI dashboards, cross-functional summaries, and drill-down into operational exceptions |
| ERP Administrator | Configures tool permissions, agent profiles, prompt templates, and monitors copilot health |
| Platform Engineer | Manages runtime deployment, identity configuration, observability, and scaling |

---

## Decision Outcome

By adopting Pulser on this stack, the organization gets:

1. **An AI assistant that respects ERP security** -- no shadow IT, no bypassed access controls. Pulser operates within Odoo's permission model.
2. **Enterprise-grade identity** -- Microsoft Entra ID for all human and machine authentication, with managed identity eliminating credential rotation.
3. **Governed analytics layer** -- Databricks Unity Catalog enforces data governance; Pulser reads curated gold-tier datasets, not raw operational tables.
4. **CE-based cost structure** -- no Odoo Enterprise license fees. Equivalent capability achieved through OCA modules and thin IPAI bridge modules.
5. **Azure-native operations** -- container scaling, Key Vault secrets, Front Door edge protection, and Application Insights observability without third-party infrastructure.
6. **Auditable AI actions** -- every Pulser action is logged with the agent identity, the delegated human user, the tool invoked, and the outcome.

---

## Capability Categories

Pulser capabilities are organized into three classes, following the
informational/navigational/transactional taxonomy:

### Informational (Answer and Summarize)

The assistant retrieves data, computes aggregates, and presents answers without
modifying any records. Examples: "What is the total AR aging over 90 days?" or
"Summarize this month's journal entries by account."

### Navigational (Find, Open, Filter)

The assistant locates records and constructs filtered views, directing the user
to the right place in the ERP. Examples: "Show me all draft purchase orders
from last week" or "Open the most recent bank reconciliation."

### Transactional (Create, Update, Approve)

The assistant performs write operations on behalf of the user, subject to their
permissions and any approval workflows. Examples: "Create a vendor bill from
this PDF" or "Approve all expense reports under 5,000 PHP."

See [Capability Model](capability-model.md) for the full taxonomy, example
prompts, Odoo model scope, and authorization requirements per class.

---

## Deployment Architecture at a Glance

```
+------------------------------------------------------------------+
|                    Three-Plane Architecture                       |
+------------------------------------------------------------------+

  System of Record (SoR)          System of Insight (SoI)
  +------------------------+      +---------------------------+
  | Odoo CE 19 + OCA       |      | Databricks + Unity Catalog|
  | Azure Container Apps   | ---> | SQL Warehouses            |
  | PostgreSQL (pg-ipai-   |      | DLT Pipelines             |
  | odoo)                  |      | Power BI Semantic Models  |
  +------------------------+      +---------------------------+
           |                                |
           v                                v
  +--------------------------------------------------+
  | Agent Factory (Microsoft Foundry)                 |
  | - Agent Service (hosted runtime)                  |
  | - Evaluations (quality gates)                     |
  | - Tracing (end-to-end observability)              |
  | - Azure AI Search (document grounding)            |
  +--------------------------------------------------+
           |
           v
  +--------------------------------------------------+
  | Delivery Surfaces                                 |
  | - Odoo embedded panel (primary)                   |
  | - M365 Copilot plugin (secondary)                 |
  | - Slack (notifications and lightweight queries)   |
  +--------------------------------------------------+
```

| Component | Azure Resource | Purpose |
|-----------|---------------|---------|
| Odoo Web | `ipai-odoo-dev-web` (ACA) | ERP application server, copilot UI host |
| Copilot Gateway | `ipai-copilot-gateway` (ACA) | Request routing, auth mediation, tool dispatch |
| Odoo Worker | `ipai-odoo-dev-worker` (ACA) | Background task execution for async copilot actions |
| PostgreSQL | `pg-ipai-odoo` (Flexible Server) | Odoo database, copilot action audit log |
| Foundry Project | `data-intel-ph` | Agent hosting, model deployment, evaluation runs |
| AI Search | `srch-ipai-dev` | Document index for retrieval-augmented generation |
| Databricks | `dbw-ipai-dev` | Governed analytics, SQL warehouse endpoints |
| Key Vault | `kv-ipai-dev` | Runtime secrets (DB credentials, SMTP, API keys) |
| Front Door | `ipai-fd-dev` | Edge TLS, WAF, geographic routing |
| Entra ID | Tenant `402de71a` | Workforce SSO, workload MI, conditional access |

---

## Documentation Tree

### Product Documentation

| Document | Purpose |
|----------|---------|
| [Capability Model](capability-model.md) | Three-class taxonomy, example prompts, model scope, maturity stages |
| [M365 Copilot Interoperability](m365-copilot-interoperability.md) | Cross-copilot invocation, render classes, fallback behavior |
| [Runtime Overview](runtime-overview.md) | Prompt-only vs hosted agent, Foundry dependencies |
| [Grounding and Search](grounding-search.md) | Azure AI Search role, safety boundaries, index design |
| [Action Layer](action-layer.md) | Odoo actions, guardrails, approval-aware mutations |
| [Operations](operations.md) | Health checks, evals, tracing, rollout/rollback |
| [Security and Governance](security-governance.md) | Identity boundaries, secrets, tenant isolation |
| [Identity and Access](identity-access.md) | Workforce/workload/agent identity model |
| [Authentication Flow](authentication-flow.md) | OIDC exchange, Odoo session mapping, backend workload auth |
| [FAQ](faq.md) | Common questions and answers |
| [Changelog](changelog.md) | Dated change entries |

### Architecture Documentation

| Document | Purpose |
|----------|---------|
| [Runtime Container Contract](../../architecture/runtime-container-contract.md) | Source roots, addon paths, config, logs, data dirs, image layers, ACA specifics |
| [Identity Architecture](../../architecture/identity-architecture.md) | Identity subjects, trust boundaries, token flows, RBAC mapping, Key Vault |
| [Addon Taxonomy](../../architecture/addon-taxonomy.md) | Core/OCA/bridge/local/l10n module classification |

### SSOT Files

| File | Purpose |
|------|---------|
| `ssot/odoo/runtime_contract.yaml` | Machine-readable runtime contract |
| `ssot/odoo/copilot-provider.yaml` | Provider configuration |
| `ssot/odoo/odoo_copilot_benchmark_v2.yaml` | Benchmark scorecard |
| `ssot/odoo/odoo_copilot_finance_tools.yaml` | Finance tool contract |

---

## Key Infrastructure Reference

| Item | Value |
|------|-------|
| Odoo base URL | `https://erp.insightpulseai.com` |
| ACA environment | `ipai-odoo-dev-env` (`salmontree-b7d27e19.southeastasia.azurecontainerapps.io`) |
| ACA static IP | `57.155.216.101` |
| Foundry project | `data-intel-ph` |
| Foundry resource | `data-intel-ph-resource` |
| Model deployment | `gpt-4.1` |
| Entra tenant | `402de71a-87ec-4302-a609-fb76098d1da7` |
| Copilot module | `ipai_odoo_copilot` (installed) |
| Copilot actions module | `ipai_copilot_actions` (installed) |
| Domain | `insightpulseai.com` |
| DNS authority | Azure DNS |
| Mail transport | Zoho SMTP (`smtp.zoho.com:587`) |
