# Resource Map — InsightPulseAI Strategy Alignment

This document serves as the authoritative mapping between InsightPulseAI's product pillars and the technical resource stack (Microsoft, Databricks, and Odoo).

---

## Pillar 1: Odoo on Cloud
**Capability**: Transactional System of Record (SSoT)

| Component | Responsibility | Technical Stack |
| :--- | :--- | :--- |
| **ERP Core** | Financials, CRM, Operations | Odoo 18 CE |
| **Localizations** | BIR Compliance, PH Payroll | `l10n_ph` + `ipai_bir_automation` |
| **Infrastructure** | Resilient Hosting | Azure Container Apps + Managed Postgres |
| **Data Authority** | Ground Truth for Agents | Odoo Transactional DB |

---

## Pillar 2: Pulser (Agentic ERP)
**Capability**: AI-native Workflow Orchestration & Copilot

| Component | Responsibility | Technical Stack |
| :--- | :--- | :--- |
| **Agent Runtime** | Execution & Tool Handling | **Microsoft AI Foundry** |
| **Orchestration** | Multi-agent collaboration | **Microsoft Agent Framework** |
| **Interface** | User engagement surfaces | Teams / M365 (SDK) + Pulser Widget |
| **Governance** | Agent Identity & Security | Microsoft Entra Agent ID |

---

## Pillar 3: Cloud Operations
**Capability**: GenAIOps, Observability & Security

| Component | Responsibility | Technical Stack |
| :--- | :--- | :--- |
| **Lifecycle** | Prompt eng, Evals, CI/CD | Microsoft GenAIOps Pipeline |
| **Observability** | Tracing, Logs, Token Tracking | Foundry Agent Service + Databricks Monitoring |
| **Guardrails** | Safety & Content Filtering | Microsoft Azure AI Content Safety |
| **Connectivity** | Integration Bus | n8n (Orchestration) + MCP (Tools) |

---

## Pillar 4: Analytics & Dashboards
**Capability**: Governed Business Intelligence & Decisioning

| Component | Responsibility | Technical Stack |
| :--- | :--- | :--- |
| **Lakehouse** | Unified Data Storage | Databricks OneLake integration |
| **Semantic Layer** | Governed Business Metrics | **Databricks AI/BI** |
| **Self-Service** | Natural Language Query (NLQ) | **Databricks Genie** |
| **Model Serving** | Specialized Analytics Models | Mosaic AI Model Serving |

---

## Official Learning & Implementation Paths

### 1. Microsoft (Agent Lane)
- **Primary SDK**: Microsoft Agent Framework SDK
- **Learn Path**: [Develop generative AI apps on Microsoft Foundry](https://learn.microsoft.com/en-us/training/paths/develop-generative-ai-apps/)
- **Key Whitepaper**: [Build, Deploy, and Govern AI Agents at Enterprise Scale](https://azure.microsoft.com/en-us/products/ai-agent-service/)

### 2. Databricks (Analytics Lane)
- **Primary SDK**: Databricks SQL SDK / MLflow
- **Learn Path**: [AI/BI Genie Spaces](https://docs.databricks.com/en/genie/index.html)
- **Key Reference**: [Monitor model quality and endpoint health](https://docs.databricks.com/gcp/machine-learning/model-serving/monitor-diagnose-endpoints)

---

*Last Updated: 2026-04-13 by Pulser Architecture Agent*
