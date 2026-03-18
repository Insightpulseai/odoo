# PRD — IPAI Tax Engine (ipai_tax_engine)

## Objective

Build a PH-native tax compliance engine that fills the gap between Odoo CE 19 PH localization and enterprise tax platforms (SAP Tax Compliance, AvaTax). Core deliverable: automated BIR 2307 generation from posted Odoo journal entries.

## Architecture

```
Odoo SoR (posted moves)
  → Supabase Edge Function (tax-compute)
    → ATC resolution (mdm.atc_matrix)
    → Rate lookup (mdm.tax_rates)
    → EWT computation
    → Risk scoring (delta vs posted)
    → Form generation (2307, 1601-EQ)
  → Supabase Storage (filled .xlsx / .dat)
  → ops.artifacts + audit.tax_events
  → Databricks Gold (ML risk model)
```

## Feature matrix (reverse-engineered from SAP + AvaTax)

| Capability | Implementation |
|---|---|
| Rule engine | `mdm.tax_rules` + Odoo rule wizard |
| Transaction screening | Odoo webhook → Edge Function |
| Jurisdiction mapping | `mdm.tax_codes` + BIR RDO mapping |
| Risk scoring | `ai.tax_risk_scores` (Databricks Gold) |
| Rate updates | `mdm.tax_rates` + pg_cron refresh |
| Withholding (EWT) | Full BIR ATC matrix (WC100, WC160, WI010...) |
| Form generation | 2307, 2316, 2550Q, SLSP, SAWT, QAP |
| Audit trail | `audit.tax_events` (append-only) |
| Validation checks | Pre-post Odoo constraint + Edge Function |
| Multi-entity | `tenant_id` RLS from day one |
| API | Supabase Edge Function + ACA worker |

## Core schemas

```sql
-- Rule engine
mdm.tax_codes        -- BIR ATC master (WC100, WI010, etc.)
mdm.tax_rates        -- Rate history with effective dates
mdm.tax_rules        -- ATC code → rate × transaction type × entity type
mdm.atc_matrix       -- Payee type × income type × threshold → ATC + rate

-- Compute state
ops.tax_runs         -- Each screening job
ops.tax_findings     -- Per-document risk findings
ops.tax_exceptions   -- Conflicts / manual review queue

-- Output
ops.bir_forms        -- Generated form metadata + Storage URL
audit.tax_events     -- Immutable computation log
```

## Core Edge Function: tax-compute

```
INPUT:  Odoo posted account.move.line batch
PROCESS:
  1. Resolve ATC code from mdm.atc_matrix (payee_type × income_type × threshold)
  2. Look up rate from mdm.tax_rates (effective_date <= posting_date)
  3. Compute EWT = base_amount × rate
  4. Risk score: compare computed vs posted EWT → flag if delta > tolerance
  5. Aggregate to quarter → generate 2307 payload
  6. Write ops.artifacts + Supabase Storage
IDEMPOTENCY: keyed on (odoo_db, move_id, atc_code, period)
```

## BIR form generation

| Form | Source | Output | Status |
|---|---|---|---|
| 2307 (EWT Certificate) | account.move.line by vendor/quarter | Filled .xlsx | Primary deliverable |
| 2316 (Compensation EWT) | hr.payslip by employee/year | Filled .xlsx | Phase 2 |
| 2550Q (Quarterly VAT) | Odoo 19 native | Extend with ops.artifacts | Phase 2 |
| 1601-EQ (Quarterly EWT Return) | ops.tax_runs aggregation | Filled .xlsx | Phase 2 |
| SLSP .dat | Odoo 19 native export | Wire to Supabase Storage | Phase 2 |
| QAP .dat | Odoo 19 native export | Wire to Supabase Storage | Phase 2 |
| SAWT .dat | Odoo 19 native export | Wire to Supabase Storage | Phase 2 |

## Phased delivery

### Phase 1 — Core (target: Q2 2026)

- mdm.tax_codes + mdm.atc_matrix seed data
- tax-compute Edge Function (ATC resolver + EWT calc)
- 2307 generator (openpyxl template filler)
- ops.tax_findings risk flagging
- Excel templates: 1601-C, 2550-M, 2307 (done this session)

### Phase 2 — Forms (target: Q3 2026)

- 1601-EQ automated generation
- 2550Q: wire Odoo v19 native → ops.artifacts
- SLSP/QAP/SAWT: wire v19 native .dat export → Supabase Storage
- 2316 generation for year-end

### Phase 3 — Intelligence (target: Q4 2026)

- Databricks DLT: Bronze tax_events → Gold tax_risk_scores
- ML model: predict under-withholding risk per vendor
- Azure Marketplace: package as SaaS offer for PH SMEs

## Odoo 19 action items

| Area | Change in v19 | Action |
|---|---|---|
| PH localization | .dat export native for SLSP/QAP/SAWT | Retire custom generators; keep 2307 pipeline |
| Fiscal positions | Tax mappings removed, reworked | Audit l10n_ph fiscal position config |
| Withholding on payment | New native feature | Test against 2307/2306 generation workflow |
| UoM / Packaging | UoM categories removed | Check ipai_* modules for UoM category refs |
| AI Agents | Native Odoo agents with DB query | Evaluate vs MS Agent Framework for tax ops |
