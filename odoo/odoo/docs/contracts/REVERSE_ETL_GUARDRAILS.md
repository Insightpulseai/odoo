# Contract — Reverse ETL Guardrails

> Defines what ADLS-derived data is allowed to write back into operational
> systems, under what constraints, and what is prohibited.

---

## Reverse ETL Classification

Every reverse ETL flow must be classified as exactly one type:

| Type | Description | Mutates Authoritative Data? |
|------|-------------|---------------------------|
| `read_model_refresh` | Overwrite a pre-computed read model (materialized view/table) | No — read models are derived |
| `enrichment_writeback` | Add derived fields to existing operational records | No — writes to designated enrichment columns only |
| `scoring_writeback` | Write ML/AI scoring outputs to operational records | No — writes to designated score columns only |
| `notification_trigger` | Fire an alert/notification based on analytical results | No — no data mutation |
| `draft_record_creation` | Create draft (non-posted) records in operational systems | Partially — creates new records in draft state |

Untyped, generic "sync" is **prohibited**.

---

## Approved Writeback Flows

### To Supabase

| Flow | Type | Target Table | Writable Columns | Guard |
|------|------|-------------|-----------------|-------|
| Customer segmentation | `scoring_writeback` | User profiles | `_segment` | Append/overwrite enrichment column only |
| ML risk scores | `scoring_writeback` | Operational records | `_risk_score` | Append/overwrite enrichment column only |
| Dashboard summaries | `read_model_refresh` | Materialized tables | All columns in designated mat tables | Full table replace on refresh |

### To Odoo

| Flow | Type | Target Model | Writable Fields | Guard |
|------|------|-------------|----------------|-------|
| Budget forecast | `enrichment_writeback` | `account.analytic.account` | `x_forecast_amount`, `x_forecast_date`, `x_forecast_confidence` | Write to `x_forecast_*` fields only |
| Draft expense import | `draft_record_creation` | `account.move` | All fields (draft state) | Created in `draft` state only; posting requires Odoo approval |

### To External Systems

| Flow | Type | Target | Guard |
|------|------|--------|-------|
| Anomaly alerts | `notification_trigger` | Slack via n8n | Alert payload only; no data mutation |

---

## Prohibited Writebacks

| Target | Prohibition | Reason |
|--------|-------------|--------|
| Odoo `account.move` (posted state) | No mutation of any field | Posted accounting entries are immutable — audit and regulatory requirement |
| Odoo `account.move.line` (posted) | No mutation | Same as above |
| Supabase `auth.users` (core fields) | No overwrite of `email`, `encrypted_password`, `role` | Identity authority belongs to Supabase Auth |
| Supabase SSOT control tables | No overwrite of core operational columns | SSOT integrity |
| Odoo `res.partner` (core fields) | No overwrite of `name`, `vat`, `company_type` | Master data authority belongs to Odoo |
| Odoo `hr.employee` (core fields) | No overwrite of `name`, `job_id`, `department_id` | Master data authority belongs to Odoo |
| Any system without a contract entry | All writes prohibited | Every writeback must be registered in this document |

---

## Idempotency Requirements

Every reverse ETL flow must define an idempotency key:

| Flow | Idempotency Key | Behavior |
|------|----------------|----------|
| Customer segmentation | `user_id` + `scoring_run_id` | Overwrite previous score for same user; skip if run_id already applied |
| ML risk scores | `record_id` + `model_version` | Overwrite previous score; skip if model_version already applied |
| Budget forecast | `analytic_account_id` + `forecast_period` | Overwrite forecast for same account+period |
| Draft expense import | `source_document_id` | Skip if `account.move.ref` already exists with same source_document_id |
| Dashboard summaries | `materialized_table_name` + `refresh_timestamp` | Full replace; skip if timestamp already processed |

---

## Failure Handling

| Failure Mode | Response |
|--------------|----------|
| Target system unavailable | Queue to dead-letter; retry with exponential backoff (max 5 attempts) |
| Idempotency key already exists (posted record) | Skip; log as "already processed" |
| Field-level guard violation (attempt to write to prohibited field) | Reject entire record; log to quarantine with violation details |
| Schema mismatch (target field does not exist) | Reject entire batch; alert; log to quarantine |
| Partial batch failure | Commit successful records; quarantine failed records; log counts |

---

## Adding a New Writeback Flow

To register a new reverse ETL flow:

1. Add entry to the "Approved Writeback Flows" section above
2. Add entry to `ssot/integrations/adls-etl-reverse-etl.yaml`
3. Define idempotency key in the "Idempotency Requirements" section
4. Commit all changes together
5. Implement field-level guards in the writeback pipeline code
