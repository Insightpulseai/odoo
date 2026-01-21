# Plan: Odoo Copilot – Process Mining

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                     Process Mining Architecture                      │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│   Odoo PostgreSQL                                                    │
│   ├── purchase_order                                                 │
│   ├── stock_picking         ──► Extractor (SQL Views/ETL Job)       │
│   ├── account_move                      │                           │
│   └── account_payment                   ▼                           │
│                              ┌──────────────────────┐               │
│                              │    pm.* Schema       │               │
│                              │ ├── pm.case          │               │
│                              │ ├── pm.event         │               │
│                              │ ├── pm.variant       │               │
│                              │ ├── pm.edge          │               │
│                              │ └── pm.deviation     │               │
│                              └──────────────────────┘               │
│                                        │                            │
│                                        ▼                            │
│                              ┌──────────────────────┐               │
│                              │   Miner Worker       │               │
│                              │ (Odoo cron / Python) │               │
│                              │ • Variant compute    │               │
│                              │ • DFG edges          │               │
│                              │ • Conformance rules  │               │
│                              └──────────────────────┘               │
│                                        │                            │
│                                        ▼                            │
│                              ┌──────────────────────┐               │
│                              │   Copilot API        │               │
│                              │   (FastAPI local)    │               │
│                              │ • Summary            │               │
│                              │ • Bottlenecks        │               │
│                              │ • Variants           │               │
│                              │ • Case timeline      │               │
│                              └──────────────────────┘               │
│                                        │                            │
│                                        ▼                            │
│                              ┌──────────────────────┐               │
│                              │   Odoo Copilot UI    │               │
│                              │   (ipai_ai_copilot)  │               │
│                              │ • NLQ interface      │               │
│                              │ • Evidence cards     │               │
│                              │ • Action suggestions │               │
│                              └──────────────────────┘               │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

## Components

### 1. Extractor (SQL Views / ETL Job)

- Runs as PostgreSQL function `pm.run_p2p_etl()`
- Idempotent: safe to re-run
- Incremental: processes only changed records since last run
- Tracks state in `pm.job_state` table

### 2. Miner (Python Worker or Scheduled Action)

- Computes variants from event sequences
- Calculates DFG edges with latency percentiles
- Applies conformance rules to detect deviations

### 3. Copilot API

- FastAPI service running locally
- Queries pm.* schema for insights
- Returns JSON for Copilot UI consumption

### 4. Optional: Supabase Sync

- Push only aggregated metrics (no raw events)
- Anonymize case IDs and sensitive attributes
- Enable cross-app dashboards in Superset

## Deliverables

| Deliverable | Location |
|-------------|----------|
| Schema migrations | `db/process_mining/001_pm_schema.sql` |
| P2P ETL function | `db/process_mining/010_p2p_etl.sql` |
| Query API service | `services/pm_api/` |
| Copilot prompts | `addons/ipai/ipai_ai_copilot/data/pm_prompts.xml` |
| Evidence renderer | `addons/ipai/ipai_ai_copilot/static/src/pm_cards/` |

## Milestones

| Milestone | Deliverables |
|-----------|--------------|
| M1 | Schema + P2P extraction |
| M2 | Discovery + bottleneck metrics |
| M3 | Conformance rules + insights |
| M4 | Copilot NLQ + action suggestions |

## Conformance Rules (P2P)

| Rule ID | Description | Severity |
|---------|-------------|----------|
| `BILL_BEFORE_RECEIPT` | Vendor bill posted before goods received | High |
| `MISSING_RECEIPT` | Bill exists but no receipt recorded | Medium |
| `MISSING_VENDOR_BILL` | Receipt exists but no bill posted | Medium |
| `APPROVAL_BYPASSED` | PO moved to purchase state without approval | High |
| `LATE_PAYMENT` | Payment posted >30 days after bill | Low |

## Performance Considerations

- Index on `pm.event(case_id, ts)` for timeline queries
- Index on `pm.edge(process, p95_s)` for bottleneck sorting
- Partition large tables by date if volume exceeds 10M events
- Use SKIP LOCKED for concurrent ETL runs
