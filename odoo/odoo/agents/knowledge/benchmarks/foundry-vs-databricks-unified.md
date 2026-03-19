# Azure AI Foundry vs Azure Databricks — Unified Approach

## Source

https://techcommunity.microsoft.com/blog/microsoftmissioncriticalblog/azure-ai-foundry-vs-azure-databricks-a-unified-approach-to-enterprise-intellig/4467576

## Weight

1.0

## Why it matters

This is Microsoft's own canonical guidance on how Foundry and Databricks complement each other. It directly validates the platform plane separation in our architecture.

## The split

| Concern | Owner | Our repo |
|---|---|---|
| Data ingestion, processing, governance, traditional ML | **Databricks** | `data-intelligence` |
| Generative AI apps, agents, prompt engineering, RAG | **Foundry** | `agent-platform` |
| Foundation model access, benchmarking, model catalog | **Foundry** | `agent-platform` |
| Large-scale data warehousing, lakehouse, Unity Catalog | **Databricks** | `data-intelligence` |
| Feature engineering, ETL, BI | **Databricks** | `data-intelligence` |
| Multi-agent orchestration, conversational AI | **Foundry** | `agent-platform` |

## The integration pattern

Databricks prepares governed data → Foundry agents consume it via native connector.

Foundry agents can query real-time governed data from Databricks AI/BI Genie, maintaining auditable interactions.

## Decision rule for our platform

- Need data products, pipelines, governance, traditional ML? → `data-intelligence` (Databricks)
- Need agents, generative AI, RAG, model orchestration? → `agent-platform` (Foundry)
- Need both? → Databricks prepares data, Foundry consumes it. Sequential, not competing.

## Validation of our architecture

| Our plane | Microsoft's recommended owner |
|---|---|
| `data-intelligence` = Databricks | Data engineering, analytics, ML, governance |
| `agent-platform` = Foundry | Agent dev, generative AI, RAG, model catalog |
| `odoo` = neither | Transactional SoR (consumes both) |

This is exactly our target. The article confirms we are not inventing a split — Microsoft recommends it.

## Must not influence

- Repo topology (already decided)
- Odoo module boundaries
- SSOT structure
