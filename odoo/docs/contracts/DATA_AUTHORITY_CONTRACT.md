# Contract — Data Authority

> Defines which system owns which data domain. No system may claim
> authority over another system's designated domain without an explicit
> ownership transfer registered in this contract.

---

## Authority Matrix

| System | Authority Level | Owns |
|--------|----------------|------|
| **Supabase** | SSOT | Platform/control-plane entities, app metadata, workflow state, vector embeddings, agent memory, Edge Function state, Auth identity |
| **Odoo** | SoR | ERP-operational entities: accounting, invoicing, projects, tasks, BIR tax filings, employees, vendors, analytic accounts, expense documents |
| **ADLS** | Analytical lake | Replicated bronze/silver/gold datasets, ML features, BI marts, reverse ETL staging. **Authoritative for nothing operational.** |
| **Azure AI Foundry** | Compute only | Model training, scoring, embedding generation. No data ownership. |
| **Tableau Cloud** | Presentation only | BI dashboards consuming ADLS gold. No data ownership. |

## Entity-Level Authority

| Entity | Authoritative System | Replication Target | Reverse ETL Allowed |
|--------|---------------------|-------------------|---------------------|
| `auth.users` | Supabase | ADLS bronze → silver → gold | Yes — `scoring_writeback` to `_segment`, `_risk_score` columns only |
| `platform_events` | Supabase | ADLS bronze → silver | No |
| `ops.task_queue` | Supabase | ADLS bronze → silver | No |
| Workflow state | Supabase | ADLS bronze → silver | No |
| Vector embeddings | Supabase | ADLS bronze | No |
| `account.move` (journal entries) | Odoo | ADLS bronze → silver → gold | **Never** — posted entries are immutable |
| `account.move` (invoices) | Odoo | ADLS bronze → silver → gold | No |
| `project.project` | Odoo | ADLS bronze → silver → gold | Yes — `enrichment_writeback` to forecast fields |
| `project.task` | Odoo | ADLS bronze → silver → gold | No |
| `hr.employee` | Odoo | ADLS bronze → silver → gold | No |
| `res.partner` | Odoo | ADLS bronze → silver → gold | No |
| `account.analytic.account` | Odoo | ADLS bronze → silver → gold | Yes — `enrichment_writeback` to `x_forecast_*` fields |
| `bir.tax.return` | Odoo | ADLS bronze → silver | No |
| `hr.expense` | Odoo | ADLS bronze → silver → gold | Yes — `draft_record_creation` only |
| ML feature tables | ADLS (computed) | — | Yes — `scoring_writeback` to Supabase/Odoo enrichment columns |
| Dashboard summaries | ADLS (aggregated) | — | Yes — `read_model_refresh` to Supabase materialized tables |

## Hard Rules

1. ADLS is a **consumer**, not a source of truth. No operational system reads from ADLS as its primary data source.
2. Supabase SSOT tables cannot be overwritten by ADLS reverse ETL. Only designated enrichment columns (`_enriched`, `_score`, `_segment`) are writable.
3. Odoo posted accounting entries (`account.move` in `posted` state) are immutable from all external systems. No reverse ETL path may modify them.
4. Odoo draft records created by reverse ETL require Odoo-side approval before posting.
5. Every data flow between systems must have an entry in `ssot/integrations/adls-etl-reverse-etl.yaml`.

## Ownership Transfer Protocol

If a data domain needs to move between systems (e.g., a Supabase table becomes Odoo-owned), the following steps are required:

1. Update this contract with the new authority assignment
2. Update `ssot/integrations/adls-etl-reverse-etl.yaml`
3. Update all downstream ETL/reverse ETL flows
4. Commit all changes together with evidence of review
