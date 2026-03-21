---
title: Data flows
description: ETL pipelines, medallion transforms, reverse ETL, and SAP integration flows.
---

# Data flows

Data flows between systems in well-defined patterns. This page documents the ETL, transform, reverse ETL, and integration flows.

## Ingestion: source systems to ADLS bronze

Source systems (Odoo, Supabase) push data into the ADLS bronze layer as raw, append-only records.

```mermaid
flowchart LR
    Odoo[Odoo CE 19<br/>SoR] -->|CDC events| n8n[n8n<br/>automation]
    Supabase[Supabase<br/>SSOT] -->|platform events| n8n
    n8n -->|JSON append| Bronze[ADLS Bronze<br/>raw events]
```

### Ingestion rules

- All records land as immutable JSON with a `_ingested_at` timestamp.
- Source system identifiers (`external_id`, UUID) are preserved as-is.
- No transformations occur at the bronze layer. Data arrives exactly as the source emitted it.
- n8n handles event routing, retry logic, and dead-letter queuing.

## Transform: bronze to silver to gold

The medallion architecture transforms data through three layers:

```mermaid
flowchart LR
    Bronze[Bronze<br/>raw, append-only] -->|clean + validate| Silver[Silver<br/>typed, deduplicated]
    Silver -->|aggregate + join| Gold[Gold<br/>business metrics]
    Gold -->|materialize| Platinum[Platinum<br/>ML features]
```

| Layer | Purpose | Example |
|-------|---------|---------|
| **Bronze** | Raw ingestion, no transforms | `invoice_events_raw.parquet` |
| **Silver** | Cleaned, typed, deduplicated | `invoices_cleaned.parquet` (validated amounts, normalized currencies) |
| **Gold** | Aggregated business metrics | `monthly_revenue_by_cluster.parquet` (joins invoices + finance clusters) |
| **Platinum** | ML-ready feature tables | `expense_anomaly_features.parquet` (engineered features for fraud detection) |

### Transform rules

- Silver deduplicates by source system primary key + event timestamp.
- Gold aggregations use idempotent SQL/Spark jobs that can re-run safely.
- Platinum features are versioned and tagged with the model version that consumes them.

## Reverse ETL: bounded write-back

Reverse ETL writes data from the analytical layer back into operational systems. This is tightly bounded to prevent authority violations.

!!! warning "Reverse ETL constraints"
    Reverse ETL must never overwrite authoritative data. It creates draft records or enriches existing records with non-authoritative metadata only.

### Allowed reverse ETL patterns

| # | Pattern | Source | Target | Constraint |
|---|---------|--------|--------|------------|
| 1 | **Draft expense creation** | SAP Concur (via ADLS) | Odoo `hr.expense` | Creates in `draft` state only. Human approves. |
| 2 | **AI enrichment tags** | Azure AI Foundry | Odoo custom fields | Writes to `x_ai_*` fields only. Never touches core fields. |
| 3 | **Anomaly flags** | ADLS gold | Supabase `ops.alerts` | Append-only alert records. Does not modify source data. |
| 4 | **Forecast values** | ADLS platinum | Supabase analytics views | Overwrites forecast-specific materialized views only. |
| 5 | **Sync status markers** | n8n | Supabase `ops.sync_cursors` | Updates cursor positions for idempotent replay. |

### Forbidden patterns

- Writing to `account.move` (posted entries) from any external system
- Updating Odoo `res.partner` contact data from analytics
- Overwriting Supabase `ops.platform_events` rows
- Any flow without an entry in `ssot/azure/service-matrix.yaml`

## SAP integration flows

### SAP Concur: expense sync

```mermaid
sequenceDiagram
    participant Concur as SAP Concur
    participant n8n as n8n
    participant Odoo as Odoo CE 19
    participant ADLS as ADLS Gen2

    Concur->>n8n: Approved expense report (webhook)
    n8n->>n8n: Validate payload, extract line items
    n8n->>Odoo: Create hr.expense (draft state)
    n8n->>ADLS: Append raw event to bronze
    Note over Odoo: Finance team reviews + posts
    Odoo->>ADLS: CDC event on post (via n8n)
```

**Rules:**

- Expenses arrive as `draft` -- never auto-posted.
- Receipt attachments store in Supabase Storage with a link in the Odoo record.
- Currency conversion uses Odoo's rate tables, not Concur's.

### SAP Joule: AI agent queries

```mermaid
sequenceDiagram
    participant Joule as SAP Joule
    participant Relay as Relay (webhook)
    participant Supabase as Supabase
    participant Odoo as Odoo CE 19

    Joule->>Relay: Query (natural language)
    Relay->>Supabase: Retrieve context (pgvector similarity search)
    Supabase-->>Relay: Relevant records + embeddings
    Relay->>Odoo: Fetch live data (XML-RPC read-only)
    Odoo-->>Relay: Current record state
    Relay-->>Joule: Structured response
```

**Rules:**

- Joule queries are read-only against Odoo. No mutations.
- Vector similarity search runs against Supabase pgvector, not Odoo.
- Query audit records append to `ops.platform_events`.

## Event flow summary

```mermaid
flowchart TB
    subgraph Sources
        Odoo[Odoo CE 19]
        Concur[SAP Concur]
        Supabase[Supabase]
    end

    subgraph Processing
        n8n[n8n automation]
    end

    subgraph Lake["ADLS Gen2"]
        Bronze[Bronze]
        Silver[Silver]
        Gold[Gold]
    end

    subgraph Consumers
        Tableau[Tableau]
        AI[Azure AI Foundry]
    end

    Odoo -->|CDC| n8n
    Concur -->|webhook| n8n
    Supabase -->|events| n8n
    n8n --> Bronze
    Bronze --> Silver
    Silver --> Gold
    Gold --> Tableau
    Gold --> AI
    AI -.->|enrichment tags| Odoo
    Concur -.->|draft expenses| Odoo
```
