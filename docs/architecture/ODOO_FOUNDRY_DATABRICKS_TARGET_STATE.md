# InsightPulseAI Platform Target State

> Canonical reference for the InsightPulseAI production architecture.
> Every repo in the org should align to this document.

## One-Line Summary

Odoo runs operations. Databricks computes and governs intelligence. Foundry runs copilots and agents. Azure secures, deploys, and monitors everything.

---

## Platform Components and Roles

| Component | Role | What It Runs |
|---|---|---|
| **Odoo 19 CE + OCA + IPAI** | System of action | Accounting, tax/compliance, approvals, workflows, operational records |
| **Azure AI Foundry** | Production copilot / agent runtime | Copilot runtime, tool routing, agent instructions, evaluations, published agent endpoints |
| **Databricks** | Lakehouse / data engineering / ML / governed analytics | Pipelines, medallion (bronze-silver-gold), Spark jobs, ML/feature engineering, Unity Catalog governance, SQL analytics, semantic marts |
| **Azure / Entra / Azure DevOps** | Identity, RBAC, monitoring, release control | Identity, RBAC, monitoring, DevOps, Key Vault, deployment targets |
| **Cloudflare** | Edge only | CDN, WAF, DNS, edge caching |
| **Tableau Cloud** | BI consumption only | Dashboards, reports, governed visual analytics |

---

## Architecture Diagram

```
users
  -> InsightPulseAI control tower / copilot UI
    -> Foundry agents
      -> Odoo APIs and workflows
      -> Databricks analytics / jobs / models / catalog
      -> governed business and compliance intelligence
```

---

## Component Detail

### Odoo (System of Action)

Runs the business:

- Accounting and financial close
- Tax and compliance automation
- Approval chains and workflow engine
- Operational records and master data
- ERP state (customers, vendors, products, invoices)

Odoo is the **system of record** for operational data. All business transactions originate or settle here.

### Databricks (Intelligence Layer)

Runs the intelligence layer:

- Ingestion pipelines (batch and streaming)
- Medallion architecture (bronze → silver → gold)
- Spark jobs and Delta Lake / Iceberg tables
- ML training, feature engineering, MLflow
- Unity Catalog for data governance
- SQL analytics and semantic marts
- Terraform-managed workspace patterns

Databricks is the **governed lakehouse**. It computes, transforms, and governs all analytical data. It does **not** replace Odoo, Foundry, or the Azure control plane.

### Azure AI Foundry (Agent Runtime)

Runs the assistants and agents:

- Copilot runtime (model hosting, prompt management)
- Tool routing and function calling
- Agent instruction sets and policies
- Evaluation pipelines and guardrails
- Published agent endpoints for production consumption

Foundry is the **production agent runtime**. All copilot and agent workloads run here, not in Databricks or Odoo.

### Azure (Control Plane)

Runs the platform control plane:

- Entra ID for identity and SSO
- RBAC and Conditional Access
- Azure Monitor, App Insights, Log Analytics
- Azure DevOps for CI/CD and release gates
- Key Vault for secrets and certificates
- Deployment targets (Container Apps, App Service, Functions)

Azure is the **security and deployment backbone**. Everything authenticates, deploys, and observes through Azure.

---

## Repo Mapping

| Repo | Owns | Contains |
|---|---|---|
| `odoo` | Business workflows, compliance, finance, ERP state | Odoo modules, OCA addons, IPAI customizations, Odoo config |
| `lakehouse` | Databricks jobs, governed analytics | SQL, notebooks, medallion pipelines, governed subject areas, Unity Catalog config |
| `agents` | Foundry agent contracts, orchestration | Agent specs, tool policies, evals, orchestration definitions |
| `infra` | Azure + Databricks + IAM + monitoring + deployment | Bicep/Terraform, IAM policies, monitoring config, deployment pipelines |
| `web` | Marketing, control tower UI, copilot exposure layer | Frontend code, CMS, copilot UI components |
| `ops-platform` | DevOps automation, operational tooling | Automation scripts, operational runbooks, platform tooling |
| `automations` | Workflow automations, integrations | Integration connectors, scheduled automations, event handlers |

---

## What SAP Architecture Patterns Teach Us

The SAP Architecture Center is a reference for **enterprise patterns**, not a product to adopt. Useful patterns extracted:

- **Agent interoperability** — assistants that call business system APIs through governed tool routing
- **Event-driven architecture** — business events trigger analytics and agent pipelines
- **Strong IAM** — Entra-backed identity with RBAC at every layer
- **Secure service consumption** — API Management + Key Vault for all cross-system calls
- **Enterprise assistant layer** — copilots sit above business systems, not inside them
- **Governed analytics foundation** — lakehouse feeds BI, not the other way around

---

## What Databricks Material Supports

Databricks belongs in:

```
lakehouse/
  ingestion/
  bronze/
  silver/
  gold/
  semantic/
  jobs/
  notebooks/
```

Databricks supports:

- Open lakehouse architecture
- Spark and distributed compute
- Delta Lake / Iceberg table formats
- Unity Catalog data governance
- MLflow experiment tracking and model registry
- Terraform-managed workspace provisioning

Databricks does **not** replace:

- Odoo (operational system of action)
- Foundry (agent runtime)
- Azure identity / control plane

---

## Anti-Patterns

| Anti-Pattern | Correct Approach |
|---|---|
| Databricks as the main platform | Databricks is the intelligence layer only |
| Agents running inside Databricks notebooks | Agents run in Foundry; Databricks provides data |
| Odoo bypassed for analytics | Odoo is the source of record; lakehouse syncs from Odoo |
| Identity managed per-service | Entra ID is the single identity provider |
| BI tools writing back to operational systems | Tableau is read-only consumption |
| Copilot logic embedded in Odoo modules | Copilot logic lives in Foundry; Odoo exposes APIs |

---

## Doctrine

1. **Odoo runs operations** — all business transactions, approvals, and compliance workflows
2. **Databricks computes and governs intelligence** — all data engineering, ML, and governed analytics
3. **Foundry runs copilots and agents** — all assistant and agent workloads in production
4. **Azure secures, deploys, and monitors everything** — identity, RBAC, observability, release control
5. **Cloudflare handles the edge** — CDN, WAF, DNS only
6. **Tableau consumes** — read-only BI dashboards over governed semantic marts

---

*Last updated: 2026-03-14*
