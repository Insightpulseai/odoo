# Skill: Databricks — Financial Services Use Cases

source: databricks.com/solutions/industries/financial-services
extracted: 2026-03-15
applies-to: lakehouse, agents

## Use case mapping to IPAI

| Databricks FS Use Case | IPAI equivalent |
|---|---|
| Real-time fraud detection | AP/AR anomaly detection |
| AI model risk management | Budget variance alerts |
| Card transaction analytics | Expense categorization |
| Regulatory compliance reporting | BIR tax compliance automation |
| Risk-weighted asset computation | Financial period close analytics |
| Customer 360 for banking | Client/project profitability dashboards |

## BIR compliance pattern on Databricks

```
Bronze: raw Odoo journal entries (replicated via Supabase)
Silver: validated + enriched (BIR field mapping, tax code normalization)
Gold: BIR-ready summaries (2307, SLSP, SAWT reports)
  → export via DBSQL → PDF via Edge Function → store in Supabase Storage
```

## Key principle
Financial data from Odoo flows ONE WAY into Databricks.
Databricks produces analytics artifacts only.
Odoo retains all posted records as SOR — never overwrite from lakehouse.
