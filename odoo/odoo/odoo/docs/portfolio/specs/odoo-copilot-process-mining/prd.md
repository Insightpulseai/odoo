# PRD: Odoo Copilot – Process Mining & Process Intelligence (Mindzie-style, Local-First)

## 1. Problem

Finance/Ops teams need Joule-like guidance: find bottlenecks, non-compliance, cycle time variance, and automation opportunities across Odoo processes (P2P, O2C, R2R, Inventory, HR), without sending sensitive operational data to third parties.

Current pain points:
- No visibility into actual process execution paths vs intended workflows
- Manual analysis of cycle times and bottlenecks
- Compliance deviations discovered only during audits
- Lack of evidence-backed recommendations for process improvement

## 2. Goals

- Generate event logs (XES-like) from Odoo transactional data
- Compute core process mining metrics: cycle time, rework, variant frequency, conformance
- Provide Copilot answers and recommendations with evidence
- Support "Done locally" mode; optionally sync derived aggregates to Supabase

## 3. Users

| User | Primary Use Cases |
|------|-------------------|
| Finance Director / Controllers | Cycle time KPIs, compliance dashboards |
| Operations Manager | Bottleneck identification, process optimization |
| Process Owner (AP, AR, Procurement, Warehouse) | Variant analysis, deviation alerts |
| Admin/IT | ETL configuration, redaction policies |

## 4. Key Features

### A. Event Log Builder (ETL)

- **Extract**: Odoo Postgres tables (account.move, stock.picking, purchase.order, sale.order, hr.expense, etc.)
- **Transform**: map to (case_id, activity, ts, resource, attributes)
- **Load**: local store (Postgres schema `pm_*` or parquet) + optional XES export

### B. Process Discovery

- Variant graph + top variants
- DFG (directly-follows graph) metrics
- Bottleneck hotspots (median/95p lead time by edge/activity)

### C. Conformance & Compliance

- Reference model per process (configurable)
- Deviations: missing approvals, out-of-order steps, bypassed controls
- Compliance score & explanation

### D. Copilot Integration (SAP Joule-like)

- **NLQ**: "Why is AP cycle time worse this month?"
- **Drill-through**: "Show the top 5 variants causing delays"
- **Action suggestions**: "Add approval rule", "Fix vendor master", "Automate 3-way match check"
- **Evidence cards**: clickable case samples with timestamps

### E. Local-first + Optional Cloud

- Default: everything runs on Odoo host / internal network
- Optional: push only aggregates + anonymized embeddings to Supabase for cross-app analytics

## 5. KPIs

| Metric | Target |
|--------|--------|
| Cycle time reduction | Measure baseline vs after optimization |
| Rework rate reduction | Track % of cases with duplicate activities |
| Compliance rate | % cases conforming to reference model |
| Mean time-to-detect anomalies | < 24 hours for high-severity deviations |

## 6. Data Model (minimal)

```
pm.case        (case_id, process, start_ts, end_ts, duration_s, variant_id, attrs_json)
pm.event       (event_id, case_id, activity, ts, resource, attrs_json)
pm.variant     (variant_id, process, sequence_hash, sequence, count)
pm.edge        (process, activity_from, activity_to, count, p50_s, p95_s)
pm.deviation   (case_id, rule_id, severity, details_json)
pm.insight     (insight_id, process, created_ts, type, summary, evidence_json)
```

## 7. Security

- Redact PII fields configurable per model/field
- Retention policy per table (default: 2 years for events, 5 years for aggregates)
- Row-level filtering by company + user roles
- Audit log for all ETL runs and data access

## 8. Rollout

| Phase | Scope | Processes |
|-------|-------|-----------|
| 1 | AP + Procurement | P2P (Purchase → Receipt → Bill → Payment) |
| 2 | AR + Sales | O2C (Quote → Order → Delivery → Invoice → Payment) |
| 3 | Inventory | Stock moves, transfers, adjustments |
| 4 | Record-to-Report | Month-end close, reconciliations |

## 9. API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/pm/{process}/summary` | GET | Process-level KPIs |
| `/pm/{process}/bottlenecks` | GET | Top edges by latency |
| `/pm/{process}/variants` | GET | Top variants by frequency |
| `/pm/{process}/cases/{id}` | GET | Case timeline + deviations |
| `/pm/{process}/deviations` | GET | List deviations with filters |
| `/pm/{process}/etl/run` | POST | Trigger incremental ETL |
