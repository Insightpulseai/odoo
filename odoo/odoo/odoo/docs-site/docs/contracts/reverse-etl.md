# Reverse ETL guardrails

Reverse ETL flows write data **from the analytical layer (ADLS) back to operational systems** (Supabase, Odoo). Every reverse ETL flow must be classified, approved, and audited.

## Classification types

Every reverse ETL flow is assigned one of five types:

| Type | Description | Risk level |
|------|-------------|------------|
| `read_model_refresh` | Refresh a read-optimized view or cache in an operational system | Low |
| `enrichment_writeback` | Add computed fields to existing records without modifying source fields | Medium |
| `scoring_writeback` | Write model predictions to dedicated scoring tables | Medium |
| `notification_trigger` | Trigger an alert or notification based on analytical output | Low |
| `draft_record_creation` | Create draft records in an operational system for human review | High |

## Approved writeback flows

### To Supabase

| Flow | Type | Source | Target table | Frequency |
|------|------|--------|-------------|-----------|
| ML prediction scores | `scoring_writeback` | `curated/ml_scores/` | `public.ml_scores` | On model run |
| Dashboard refresh | `read_model_refresh` | `curated/dashboards/` | `public.dashboard_cache` | Hourly |
| Anomaly alerts | `notification_trigger` | `curated/anomalies/` | `public.notifications` | On detection |

### To Odoo

| Flow | Type | Source | Target model | Frequency |
|------|------|--------|-------------|-----------|
| Forecast drafts | `draft_record_creation` | `curated/forecasts/` | `project.forecast` (draft) | Daily |
| Project risk enrichment | `enrichment_writeback` | `curated/ml/project_features/` | `project.project` (risk score field) | Daily |

### To external systems

| Flow | Type | Source | Target | Frequency |
|------|------|--------|--------|-----------|
| Slack anomaly alert | `notification_trigger` | `curated/anomalies/` | Slack via n8n | On detection |

## Prohibited writebacks

!!! danger "These writebacks are never allowed"

    | Target | Entity | Reason |
    |--------|--------|--------|
    | Odoo | `account.move` (posted) | Financial records are immutable after posting |
    | Odoo | `account.move.line` (posted) | Journal items are immutable after posting |
    | Supabase | `auth.users` | Identity is owned by Supabase Auth exclusively |
    | SAP Concur | Any entity | Concur is the T&E system of record |
    | Any system | Any entity without a contract | Uncontracted writebacks are prohibited |

## Idempotency requirements

Every reverse ETL flow must be idempotent:

- Use a **natural key** or **source hash** to detect duplicates.
- On duplicate detection: **skip** (do not upsert unless the flow type explicitly allows it).
- Record the deduplication decision in the audit log.

```sql
-- Example: idempotent scoring writeback
INSERT INTO public.ml_scores (entity_id, model_id, score, scored_at, source_hash)
VALUES ($1, $2, $3, now(), $4)
ON CONFLICT (entity_id, model_id)
DO UPDATE SET score = EXCLUDED.score, scored_at = EXCLUDED.scored_at
WHERE ml_scores.source_hash != EXCLUDED.source_hash;
```

## Failure handling

| Failure mode | Response | Escalation |
|--------------|----------|------------|
| Target system unavailable | Retry with exponential backoff (max 3 attempts) | Alert to `#alerts` after 3 failures |
| Schema mismatch | Halt flow, log error | Alert to `#dev`; requires manual fix |
| Duplicate rejection | Log and skip | No escalation (expected behavior) |
| Partial batch failure | Commit successful records, quarantine failures | Alert with failure count |
| Quota / rate limit | Back off and retry on next schedule | Alert if persists beyond 2 cycles |

## Add a new writeback flow

Follow this checklist:

- [ ] Classify the flow into one of the five types
- [ ] Add the flow to the approved writeback table in this document
- [ ] Add an SSOT YAML entry in `ssot/integrations/`
- [ ] Implement idempotency with natural key or source hash
- [ ] Define failure handling for all five failure modes
- [ ] Add monitoring and alerting
- [ ] Get architecture review approval
- [ ] Update `docs/contracts/PLATFORM_CONTRACTS_INDEX.md`
