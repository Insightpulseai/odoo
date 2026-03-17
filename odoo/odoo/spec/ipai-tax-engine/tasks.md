# Tasks — IPAI Tax Engine

## Phase 1: Core

- [ ] Seed mdm.tax_codes with BIR ATC master data
- [ ] Seed mdm.atc_matrix (payee type × income type × threshold → ATC + rate)
- [ ] Seed mdm.tax_rates with current BIR withholding rates
- [ ] Create tax-compute Edge Function scaffold
- [ ] Implement ATC resolver in tax-compute
- [ ] Implement EWT computation in tax-compute
- [ ] Implement risk scoring (computed vs posted delta)
- [ ] Create generate_2307.py script (openpyxl template filler)
- [ ] Test 2307 generation with sample TBWA/SMP vendor data
- [x] Create BIR 1601-C Excel template (official layout)
- [x] Create BIR 2550-M Excel template (official layout)
- [x] Create BIR 2307 Excel template (official layout)
- [ ] Commit all BIR Excel forms

## Phase 2: Forms

- [ ] Wire Odoo 19 native 2550Q → ops.artifacts
- [ ] Wire Odoo 19 native SLSP .dat → Supabase Storage
- [ ] Wire Odoo 19 native QAP .dat → Supabase Storage
- [ ] Wire Odoo 19 native SAWT .dat → Supabase Storage
- [ ] Generate 1601-EQ from ops.tax_runs aggregation
- [ ] Generate 2316 for year-end compensation EWT

## Phase 3: Intelligence

- [ ] Databricks DLT pipeline: Bronze tax_events → Silver → Gold
- [ ] ML model: under-withholding risk prediction per vendor
- [ ] Azure Marketplace packaging for PH SME SaaS offer
