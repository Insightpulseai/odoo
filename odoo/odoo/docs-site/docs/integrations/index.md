# Integrations

InsightPulse AI integrates with external systems through **contract-governed boundaries**. Every integration has an SSOT YAML entry in `ssot/integrations/` and a corresponding contract document in `docs/contracts/`.

No integration bypasses the contract layer. Data flows are classified, ownership is explicit, and reverse ETL is guardrailed.

## Pages in this section

| Page | Description |
|------|-------------|
| [Supabase](supabase.md) | Auth identity, Edge Functions, pgvector, Realtime |
| [ADLS ETL](adls-etl.md) | Data lake zones, ETL flows, reverse ETL classification |
| [SAP integration](sap-integration.md) | SAP Concur T&E sync, Joule copilot, Entra ID SSO |
| [Slack and n8n](slack-n8n.md) | ChatOps, automation workflows, scheduled jobs |
| [Azure AI Foundry](azure-ai.md) | ML training, scoring, operational RAG |

## Integration boundary model

```mermaid
graph TB
    subgraph "Data authority"
        SUP[Supabase<br>Auth, Realtime, pgvector]
        ODOO[Odoo CE 19<br>ERP SSOT]
        ADLS[ADLS Gen2<br>Analytical lake]
    end
    subgraph "Compute"
        ACA[Azure Container Apps]
        AAI[Azure AI Foundry]
    end
    subgraph "External"
        SAP[SAP Concur / Joule]
        SLACK[Slack]
        N8N[n8n]
    end
    SAP -->|relay functions| ODOO
    N8N -->|webhooks| ODOO
    N8N -->|webhooks| SUP
    SLACK -->|ChatOps| N8N
    ODOO -->|ETL| ADLS
    SUP -->|ETL| ADLS
    ADLS -->|reverse ETL| SUP
    ADLS -->|reverse ETL| ODOO
    AAI -->|scoring| SUP
```
