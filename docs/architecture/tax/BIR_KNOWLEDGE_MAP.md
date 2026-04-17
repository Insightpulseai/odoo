# Tax/BIR Knowledge Map

> Domain map of all discovered tax/BIR knowledge areas, forms, workflows,
> rules packs, review engines, reporting/eval assets, and tool/API surfaces.
> Generated: 2026-03-18 · **Updated: 2026-04-18** (deep research from bir.gov.ph)

---

## Domain Map

```
Philippine Tax / BIR Compliance
|
+-- Tax Computation
|   +-- VAT (Output/Input/Payable)
|   +-- Expanded Withholding Tax (EWT) -- 10 ATC codes
|   +-- Final Withholding Tax (FWT) -- 5 codes
|   +-- Compensation Tax (TRAIN Law brackets)
|   +-- Corporate Income Tax (25% regular, 2% MCIT)
|   +-- Documentary Stamp Tax (DST)
|
+-- BIR Forms
|   +-- Monthly: 1601-C, 1601-E, 1601-F, 2550M, 2551M, 0619-E, 0619-F
|   +-- Quarterly: 2550Q, 1601-EQ, 1601-FQ, 1702Q
|   +-- Annual: 1702-RT, 1702-MX, 1700, 1604-CF, 1604-E
|   +-- Certificates: 2307, 2306, 2316
|
+-- Compliance Workflows
|   +-- Filing lifecycle: Draft > Computed > Validated > Approved > Filed > Confirmed
|   +-- Month-end close checklists (via project.task templates)
|   +-- Filing deadline tracking with activity generation
|   +-- Overdue/compliance worklist views
|   +-- Approval gates (PLM-style required/optional)
|
+-- Compliance Intelligence (12 checks)
|   +-- CI-001: Missing EWT on vendor bills
|   +-- CI-002: Output VAT vs SLSP gap
|   +-- CI-003: Input VAT vs SLSP gap
|   +-- CI-004: Compensation WHT remittance
|   +-- CI-005: Ungenerated BIR 2307
|   +-- CI-006: ATC code completeness
|   +-- CI-007: Filing deadline countdown
|   +-- CI-008: Overdue compliance tasks
|   +-- CI-009: DST on applicable documents
|   +-- CI-010: QAP completeness
|   +-- CI-011: SAWT completeness
|   +-- CI-012: Period completion status
|
+-- Supporting Structures
|   +-- SAWT (Summary Alphalist of Withholding Taxes)
|   +-- SLSP (Summary List of Sales/Purchases)
|   +-- QAP (Quarterly Alphalist of Payees)
|   +-- Alphalist (1604-CF, 1604-E)
|   +-- ATC code master data
|   +-- BIR filing calendar / deadline registry
|
+-- eServices Integration (confirmed live 2026-04-17)
|   +-- ORUS (Online Registration and Update System) -- replaces eREG
|   +-- NewBizReg (New Business Registration Portal)
|   +-- TRRA (Taxpayer Registration-Related Application)
|   +-- eFPS v5.74 (Electronic Filing & Payment System)
|   +-- eBIRForms v7.9.5.0 (36 forms, RMC 49-2025)
|   +-- ePAY (ePayment via AABs, GCash, PayMaya, bank online)
|   +-- eTSPCert (Tax Software Provider Certification)
|   +-- eONETT (One-Time Transactions: CGT, donor's, DST)
|   +-- eTCBP-TCVC (Tax Clearance for Bidding)
|   +-- eTCS (Tax Clearance System, pilot Makati RR 8A)
|   +-- eAFS (Audited Financial Statements, PDF upload)
|   +-- eAPPOINTMENT (scheduling)
|   +-- Withholding Tax Calculator
|
+-- AI / Agent Capabilities
|   +-- Advisory: Explain BIR rules, rates, deadlines
|   +-- Navigational: Locate returns, tasks, blockers, overdue items
|   +-- Transactional: Compute, validate, export, generate alphalist
|   +-- Review: 5-dimension AI compliance scoring
```

---

## Forms / Workflows Covered

### BIR Form Coverage Matrix

| Form | In Odoo Module | In Agent Skill | In Supabase Schema | In Seeds/Demo | eBIRForms Support |
|------|---------------|---------------|-------------------|--------------|------------------|
| 1601-C | Yes (demo XML) | Yes (skill) | Yes (`ops.bir_forms`) | Yes | Documented |
| 1601-E | Referenced | Yes (skill) | Yes | No | Documented |
| 1601-F | No | Referenced | Yes | No | Documented |
| 2550M | No | Yes (skill) | Yes | No | Documented |
| 2550Q | Referenced (spec) | Yes (skill) | Yes | No | Documented |
| 1601-EQ | Referenced | Referenced | Yes | No | Documented |
| 1702-RT | Referenced (spec) | Yes (skill) | No | No | Documented |
| 1604-CF | Referenced | Yes (skill) | No | No | Documented |
| 1604-E | Referenced | Yes (skill) | No | No | Documented |
| 2307 | Referenced | Yes (skill) | Yes (`ops.bir_forms`) | No | Documented |
| 2316 | Referenced | Referenced | Yes | No | Documented |
| SAWT | Referenced (checks) | Referenced | Yes | No | Not documented |
| SLSP | Referenced (checks) | Referenced | Yes | No | Not documented |
| QAP | Referenced (checks) | Referenced | Yes | No | Not documented |

### Form Generation Pipeline Status

| Stage | Status | Location |
|-------|--------|----------|
| Tax computation from `account.move` | Working | `ipai_bir_tax_compliance/engine/` |
| ATC code resolution | Working (Supabase) | `odoo/supabase/functions/tax-compute/` |
| Risk scoring / flagging | Working (Supabase) | `odoo/supabase/functions/tax-compute/` |
| eBIRForms XML export | Not implemented | Spec only |
| PDF report templates | Not implemented | Spec only |
| eFPS browser automation | Not implemented | PoC only in roadmap |
| BIR form .dat generation | Documented (n8n bridge) | `odoo/platform/bridges/bir-form-generation/` |

---

## Rules Packs

### JSONLogic Rules Engine

| Pack | File | Rules Count | Coverage |
|------|------|-------------|----------|
| EWT rules | `data/rules/ewt.rules.yaml` | 11 (10 ATC + 1 aggregation) | W010, W020, W030, W040, W050 (missing), W157, W158, W161, W169, W170 |
| VAT rules | `data/rules/vat.rules.yaml` | 8 | Output VAT, Input VAT, VAT payable, adjustments |

### Rate Tables

| Table | File | Coverage |
|-------|------|----------|
| PH rates 2025 | `data/rates/ph_rates_2025.json` | VAT (12%), EWT (10 codes), FWT (5 codes), TRAIN brackets (6), Corporate IT |

### Supabase ATC Matrix

| Source | File | Codes | Notes |
|--------|------|-------|-------|
| SQL seed | `20260317_bir_tax_engine.sql` | 18 ATC codes (WI/WC namespace) | Different namespace than JSON rates |
| SQL rates | Same migration | 18 rates effective 2018-01-01 | |
| SQL matrix | Same migration | 18 decision rules | Includes income band, VAT status, TOP WHA |

---

## Review Engines

| Engine | Location | Status |
|--------|----------|--------|
| Supabase `tax-compute` Edge Function | `odoo/supabase/functions/tax-compute/index.ts` | Active -- computes EWT, scores risk |
| AI compliance review (`finance-tax-pulse`) | TaxPulse-PH-Pack (external) | Not absorbed -- 5-dimension scoring |
| Compliance check catalog | `odoo/ssot/tax/compliance_check_catalog.yaml` | Active -- 12 checks, machine-readable |

---

## Reporting / Eval Assets

### Copilot Eval Datasets (in `agents/`)

| Dataset | Path | Content |
|---------|------|---------|
| eval-dataset-v2.json | `agents/evals/odoo-copilot/datasets/` | Contains BIR-related test cases |
| eval-run-20260314 | `agents/evals/odoo-copilot/results/` | Run results |
| eval-run-20260315-final | `agents/evals/odoo-copilot/results/` | Final eval results |
| copilot_marketplace_benchmark | `ssot/evals/copilot_marketplace_benchmark.yaml` | Benchmark definition (references BIR) |

### Planned (Not Yet Created)

| Dataset | Purpose | Spec Reference |
|---------|---------|---------------|
| `bir_advisory.yaml` | 50 informational accuracy cases | `spec/tax-pulse-sub-agent/prd.md` |
| `bir_ops.yaml` | 30 navigational accuracy cases | Same |
| `bir_actions.yaml` | 40 transactional correctness cases | Same |
| `bir_sft_catalog.yaml` | SFT training sample catalog | Same |
| `bir_sft_train.jsonl` | Fine-tuning training set | Same |
| `bir_sft_valid.jsonl` | Fine-tuning validation set | Same |

---

## Tool / API Surfaces

### Agent Tool Contracts (SSOT)

Defined in `odoo/ssot/agents/tax_pulse_tool_contracts.yaml`:

| Tool | Agent | Approval | Odoo Model |
|------|-------|----------|-----------|
| `bir_compliance_search` | Advisory, Ops | No | N/A (Azure AI Search) |
| `check_overdue_filings` | Ops | No | `bir.filing.deadline` |
| `compute_bir_vat_return` | Actions | Yes | `bir.vat.return` |
| `compute_bir_withholding_return` | Actions | Yes | `bir.withholding.return` |
| `validate_bir_return` | Actions | Yes | `bir.tax.return` |
| `generate_alphalist` | Actions | Yes | `bir.alphalist` |
| `generate_efps_xml` | Actions | Yes | `bir.tax.return` |
| `generate_bir_pdf` | Actions | Yes | `bir.tax.return` |

### Bridge API (Read)

| Endpoint | Purpose |
|----------|---------|
| `getComplianceFindings` | Query compliance findings |
| `getComplianceTasks` | Get compliance task status |
| `getCompliancePeriods` | Get period completion status |
| `getInvoices` | Get invoice data |
| `getTaxSummary` | Get tax summary |
| `getWithholdingLines` | Get WHT detail lines |
| `getReport2550Q` | Get 2550Q report data |
| `getReportSAWT` | Get SAWT data |
| `getReportSLSP` | Get SLSP data |
| `getReportBIR2307` | Get 2307 certificate data |

### Bridge API (Write -- Phase 1)

| Endpoint | Purpose |
|----------|---------|
| `updateComplianceTask` | Update state, assignee, completion_note |
| `createComplianceFinding` | Create new finding from check |
| `postChatterNote` | Audit trail on any Odoo record |

### Supabase RPCs

| RPC | Purpose |
|-----|---------|
| `ops.resolve_atc()` | ATC code lookup by payee type, income type, income band |
| `ops.get_current_rate()` | Get current rate for ATC code as of date |

---

## Benchmark Surfaces

### TaxPulse vs AvaTax (Avalara) -- Documented

| Dimension | TaxPulse | AvaTax |
|-----------|----------|--------|
| Focus | Philippines BIR (PH-specific) | Global (190+ countries) |
| Forms | 36 eBIRForms | N/A (rate engine) |
| Tax types | EWT, FWT, VAT, income, DST | Sales, use, VAT, GST |
| Computation | Batch (form-level) from Odoo | Real-time per transaction (20ms) |
| AI review | 5-dimension compliance scoring | Agentic tax compliance (new 2026) |
| Pricing | Open source (AGPL-3) | $1+/year (Azure Marketplace) |

**Verdict**: Complementary, not competing. TaxPulse for PH filing; AvaTax only if expanding to US/global sales tax.

### SAP Tax Compliance Parity

The STC (SAP Tax Compliance) workstream seeds define a SAP-compatible taxonomy with:
- 4 compliance domains: VAT, WHT, INC, ALP
- 4 worklist types: S4_VAT, S4_VND, S4_INV, S4_WHT
- 3 filing frequencies: MONTHLY, QUARTERLY, ANNUAL
- RACI roles: R, A, C, I

---

---

## TaxPulse-PH-Pack Legacy Coverage

> Source: `jgtolentino/TaxPulse-PH-Pack` (commit `72ce864958099748c60cf11ed3b3536ddf82064c`)
> Scanned: 2026-03-18

### BIR Forms Covered (Odoo ORM Models)

| Form | Model Name | Fields | Status |
|------|-----------|--------|--------|
| 1601-C | `bir.1601c` | compensation_tax, final_tax, total_tax_withheld, agency_id, period, state, supabase_sync | Full Odoo model with line items (`bir.1601c.line`) |
| 2550Q | `bir.2550q` | output_vat, input_vat, vat_payable, quarter, year, agency_id, state, supabase_sync | Full Odoo model |
| 1702-RT | `bir.1702rt` | gross_income, deductions, taxable_income, income_tax_due, tax_credits, net_tax_payable, fiscal_year, state | Full Odoo model |

### Multi-Agency Framework

The `taxpulse.agency` model supports 8 entities: RIM, CKVC, BOM, JPAL, JLI, JAP, LAS, RMQB. Each agency has:

- TIN and RDO code
- Analytic account linkage (for expense tracking)
- Smart buttons to view associated BIR forms
- SQL constraint on unique code

### Tax Computation Methods

| Method | Location | Description |
|--------|----------|-------------|
| `compute_withholding_tax_from_moves()` | `models/bir_1601c.py` | Scans posted `account.move` lines within period, classifies by tax group name and WC/WF code prefix, accumulates compensation vs final tax |
| `_compute_vat_payable()` | `models/bir_2550q.py` | Simple output_vat - input_vat |
| `_compute_taxable_income()` | `models/bir_1702rt.py` | gross_income - deductions |
| `_compute_net_tax()` | `models/bir_1702rt.py` | income_tax_due - tax_credits |

### Rules Engine (Standalone, Not Odoo ORM)

| Component | File | Description |
|-----------|------|-------------|
| JSONLogic Evaluator | `engine/rules_engine/evaluator.py` | 14 operators, condition evaluation, rule application with bucket accumulation |
| Formula Engine | `engine/rules_engine/formula.py` | SUM/MAX/MIN/ABS/ROUND, form line evaluation from bucket mappings, aggregation rules |
| Rules Loader | `engine/rules_engine/loader.py` | YAML loader with caching for rules, rates, mappings, validations, forms |
| EWT Rules | `packs/ph/rules/ewt.rules.yaml` | 10 EWT rules (W010-W170) + aggregation |
| VAT Rules | `packs/ph/rules/vat.rules.yaml` | 8 VAT rules (output/input/payable/adjustments) |
| PH Rates 2025 | `packs/ph/rates/ph_rates_2025.json` | VAT 12%, EWT (10 codes), FWT (5 codes), TRAIN brackets (6 tiers), Corporate IT |
| Core Validations | `packs/ph/validations/core_validations.yaml` | 9 transaction + 9 aggregate validations |
| 2550Q Form Def | `packs/ph/forms/bir_2550Q_2025.form.yaml` | Complete BIR 2550Q form with all line items |
| 2550Q Mapping | `packs/ph/mappings/vat_2550Q.mapping.yaml` | Bucket-to-form-line mapping with formulas |

### AI Review Engine (Finance Tax Pulse)

| Component | File | Description |
|-----------|------|-------------|
| Edge Function | `supabase/functions/finance-tax-pulse/index.ts` | 450-line Deno orchestrator: load protocol, fetch data, build prompt, call LLM, score, save |
| Protocol v1 | `supabase/004_tax_pulse_protocol_seed.sql` | High Compliance Mode: 5 dimensions, variance thresholds, reconciliation requirements |
| Authority Sources | `config/tax_pulse_sources.yaml` | 13 sources across 4 tiers with RAG routing rules |
| LLM Config | `engine/config/finance_tax_pulse_model.yaml` | Claude Sonnet 4 primary, Haiku fallback, cost controls |

### 5-Dimension Scoring Model

| Dimension | Weight | What It Measures |
|-----------|--------|-----------------|
| D1: Compliance Accuracy | 30% | BIR form completeness, ATC code usage, TIN format, RDO alignment |
| D2: Numerical Accuracy | 25% | Computation correctness, cross-footing, GL variance < 0.01% |
| D3: Coverage & Risk | 20% | Transaction completeness, classification accuracy, audit triggers |
| D4: Timeliness | 15% | Filing deadline buffer, amendment frequency, cycle time |
| D5: Clarity & Auditability | 10% | Working paper quality, audit trail completeness |

Status thresholds: Pass (composite >= 80, all dimensions >= 70), Conditional (composite 60-80), Fail (composite < 60 or any dimension < 50).

### Supabase Schema (BIR Data Warehouse)

| Table | Schema | Purpose |
|-------|--------|---------|
| `bir.agencies` | `bir` | 8 agency entities with RLS |
| `bir.form_1601c` | `bir` | Monthly withholding forms with odoo_id FK |
| `bir.form_2550q` | `bir` | Quarterly VAT forms |
| `bir.form_1702rt` | `bir` | Annual income tax forms |
| `bir.user_agency_access` | `bir` | Agency-scoped RLS access control |
| `tax_pulse_sources` | `public` | Authority source registry (4 tiers) |
| `tax_pulse_source_aliases` | `public` | Multi-domain aliases |
| `tax_pulse_protocols` | `public` | Versioned review protocols |
| `tax_pulse_run_log` | `public` | AI review run audit trail (5-dimension scores) |
| `tax_pulse_protocol_audit` | `public` | Protocol change audit |

### Spec Coverage (SpectraTax Engine PRD)

The PRD (`specs/001-taxpulse-engine.prd.md`) defines 18 functional requirements:

- FR-1 to FR-3: Data ingestion and canonical transaction schema
- FR-4 to FR-6: Rules and rates model with JSONLogic evaluation
- FR-7 to FR-8: BIR form mapping (bucket to form line)
- FR-9 to FR-10: Tax return lifecycle (Draft/ForReview/Approved/Filed)
- FR-11 to FR-13: Validation engine with error/warning severity
- FR-14 to FR-16: Reconciliation engine (GL vs Return, Subledger vs Return, Period vs Period)
- FR-17 to FR-18: AI agent integration (read-only on math)

5-phase rollout: Prototype VAT -> Extend EWT/FWT -> Historical Parallel Run -> Shadow Mode -> Primary Computation Source.

---

---

## Philippine Tax Types — Complete Reference (10 types, from bir.gov.ph)

### 1. Capital Gains Tax (CGT)

Tax on gains from sale/exchange/disposition of capital assets in PH, including pacto de retro sales.

| Item | Detail |
|---|---|
| Rate (real property) | 6% of selling price or FMV, whichever is higher |
| Rate (shares, unlisted) | 15% of net capital gains |
| Forms | 1706 (real property), 1707 (shares) |
| Filing | Within 30 days of sale |
| eService | eONETT |

### 2. Documentary Stamp Tax (DST)

Tax on documents, instruments, loan agreements evidencing acceptance/assignment/sale/transfer of obligations/rights/property.

| Item | Detail |
|---|---|
| Rate | Varies by document type (see NIRC Sec 174-199) |
| Forms | 2000, 2000-OT |
| Filing | Within 5 days of execution for one-time; monthly for recurring |
| eService | eBIRForms, eONETT (for one-time) |

### 3. Donor's Tax

Tax on gratuitous transfer of property between living persons.

| Item | Detail |
|---|---|
| Rate | 6% of total gifts exceeding PHP 250,000 |
| Exempt | First PHP 250,000 per donor per year |
| Form | 1800 |
| Filing | Within 30 days of donation |
| eService | eONETT |

### 4. Estate Tax

Tax on transmission of estate from deceased to heirs at time of death.

| Item | Detail |
|---|---|
| Rate | 6% of net estate |
| Standard deduction | PHP 5,000,000 |
| Family home deduction | Up to PHP 10,000,000 |
| Form | 1801 |
| Filing | Within 1 year of death (extendable by 30 days) |
| eService | eBIRForms |

### 5. Income Tax

Tax on yearly profits from property, profession, trades, offices.

| Bracket (TRAIN Law, individual, per annum) | Rate |
|---|---|
| Up to PHP 250,000 | 0% |
| Over 250,000 to 400,000 | 15% of excess over 250,000 |
| Over 400,000 to 800,000 | 22,500 + 20% of excess over 400,000 |
| Over 800,000 to 2,000,000 | 102,500 + 25% of excess over 800,000 |
| Over 2,000,000 to 8,000,000 | 402,500 + 30% of excess over 2,000,000 |
| Over 8,000,000 | 2,202,500 + 35% of excess over 8,000,000 |

| Corporate | Rate |
|---|---|
| Regular corporate income tax (RCIT) | 25% (20% for MSMEs with net taxable income ≤ PHP 5M and total assets ≤ PHP 100M) |
| Minimum corporate income tax (MCIT) | 1% of gross income (CREATE MORE: reduced from 2%) |
| Proprietary educational institutions / hospitals | 10% if 50%+ of revenue from education/hospital ops |

| Forms | Frequency |
|---|---|
| 1700 | Annual (individual, compensation only) |
| 1701 / 1701Q | Annual / Quarterly (self-employed, mixed) |
| 1702-RT / 1702-MX / 1702-EX | Annual (corporate: regular / mixed / exempt) |
| 1702Q | Quarterly (corporate) |
| 1704 | Improperly Accumulated Earnings Tax |

### 6. Percentage Tax

Business tax on persons/entities with gross annual sales/receipts not exceeding PHP 3,000,000 and not VAT-registered.

| Item | Detail |
|---|---|
| Rate | 3% of gross sales/receipts (CREATE Law: reverted from temporary 1% as of Jul 2023) |
| Threshold | Gross annual sales/receipts ≤ PHP 3,000,000 |
| Forms | 2551M (monthly), 2551Q (quarterly), 2552 (shares via LSE), 2553 (special laws) |
| Filing | 2551M: 20th of following month; 2551Q: 25th of month after quarter |

### 7. Value-Added Tax (VAT)

Business tax on sale of properties, lease of goods/properties, or services. Indirect tax — passed to buyer.

| Item | Detail |
|---|---|
| Rate | 12% |
| VAT threshold | Gross annual sales > PHP 3,000,000 (mandatory registration) |
| Zero-rated | Exports, services to non-residents |
| VAT-exempt | Agricultural food products, educational services, health services, etc. |
| Digital services VAT | 12% on non-resident digital service providers (RA 12023, RR 3-2025) |
| Forms | 2550M (monthly declaration), 2550Q (quarterly return) |
| Filing | 2550M: 25th of following month; 2550Q: 25th of month after quarter |

### 8. Withholding Tax (4 subtypes)

**8a. Withholding Tax on Compensation (WTC)**
Tax withheld from employees receiving compensation income.

| Item | Detail |
|---|---|
| Rate | Per TRAIN Law graduated brackets (same as income tax) |
| Forms | 1601-C (monthly remittance), 1604-CF (annual info return) |
| Certificate | 2316 (Certificate of Compensation Payment/Tax Withheld) |

**8b. Expanded Withholding Tax (EWT)**
Creditable withholding tax on certain income payments.

| Item | Detail |
|---|---|
| Rate | 1% to 15% depending on income type (per RR 11-2018) |
| ATC namespace | WI (individual), WC (corporate), WB (both) per RR 11-2018 Annex |
| Forms | 0619-E (monthly remittance, M1/M2 only), 1601-EQ (quarterly) |
| Certificate | 2307 (Certificate of Creditable Tax Withheld at Source) |
| Annual | 1604-E (Annual Information Return of EWT) |
| Alphalist | QAP (Quarterly Alphalist of Payees), SAWT (Summary Alphalist of WT) |

**8c. Final Withholding Tax (FWT)**
Non-creditable withholding tax — constitutes full and final payment.

| Item | Detail |
|---|---|
| Covers | Interest on deposits, royalties, prizes, dividends to non-residents, fringe benefits |
| Forms | 0619-F (monthly, M1/M2), 1601-FQ (quarterly), 1603 (fringe benefits quarterly) |
| Annual | 1604-CF (Annual Information Return — Compensation + Final WT) |

**8d. Withholding Tax on Government Money Payments (WTGMP)**
Tax withheld by government offices before paying private entities.

| Item | Detail |
|---|---|
| Rate | 1% to 15% per applicable EWT/FWT schedule |
| Applies to | Government procurement payments to private contractors/suppliers |

### 9. Excise Tax

Tax on production, sale, or consumption of commodities (domestic or imported).

| Product | Form |
|---|---|
| Alcohol products | 2200A |
| Automobiles and non-essential goods | 2200AN |
| Mineral products | 2200M |
| Petroleum products | 2200P |
| Tobacco products | 2200T |

### 10. Other Taxes / Fees

| Item | Detail |
|---|---|
| Annual registration fee | PHP 500 (Form 0605, due January 31) |
| Books of accounts | Stamping fee per book |
| Compromise penalties | Per RMO, varies by violation |

---

## Complete eBIRForms Package — 36 Forms (v7.9.5.0, RMC 49-2025)

| # | Form | Name | Domain | Frequency |
|---|---|---|---|---|
| 1 | 0605 | Payment Form | Payment | Annual (Jan 31) |
| 2 | 1600 | Monthly Remittance — VAT/PT Withheld | VAT/PT | Monthly |
| 3 | 1600WP | Race Track VAT Remittance | VAT | Monthly |
| 4 | 1601-C | Monthly Remittance — WT Compensation | Comp WT | Monthly |
| 5 | 1601-E | Monthly Remittance — Creditable (Expanded) WT | EWT | Monthly |
| 6 | 1601-F | Monthly Remittance — Final WT | FWT | Monthly |
| 7 | 1602 | Monthly Remittance — Final Tax on Interest/Deposits | FWT | Monthly |
| 8 | 1603 | Quarterly Final Tax on Fringe Benefits | FWT | Quarterly |
| 9 | 1604-CF | Annual Info Return — Compensation + Final WT | Annual | Annual |
| 10 | 1604-E | Annual Info Return — Expanded WT | Annual | Annual |
| 11 | 1606 | WT Remittance — Real Property Transfer | ONETT | Per transaction |
| 12 | 1700 | Annual ITR — Individual (Compensation Only) | Income | Annual |
| 13 | 1701 | Annual ITR — Self-Employed / Estates / Trusts | Income | Annual |
| 14 | 1701Q | Quarterly ITR — Self-Employed | Income | Quarterly |
| 15 | 1702-EX | Annual ITR — Exempt Corporations | Corporate | Annual |
| 16 | 1702-MX | Annual ITR — Mixed Rate Corporations | Corporate | Annual |
| 17 | 1702-RT | Annual ITR — Regular Rate Corporations | Corporate | Annual |
| 18 | 1702Q | Quarterly ITR — Corporations | Corporate | Quarterly |
| 19 | 1704 | Improperly Accumulated Earnings Tax | Corporate | Annual |
| 20 | 1706 | CGT — Real Property | CGT | Per transaction |
| 21 | 1707 | CGT — Shares (unlisted) | CGT | Per transaction |
| 22 | 1800 | Donor's Tax Return | Donor | Per transaction |
| 23 | 1801 | Estate Tax Return | Estate | Per event |
| 24 | 2000 | DST Declaration/Return | DST | Monthly |
| 25 | 2000-OT | DST for One-Time Transactions | DST | Per transaction |
| 26 | 2200A | Excise Tax — Alcohol Products | Excise | Monthly |
| 27 | 2200AN | Excise Tax — Automobiles/Non-Essential | Excise | Monthly |
| 28 | 2200M | Excise Tax — Mineral Products | Excise | Monthly |
| 29 | 2200P | Excise Tax — Petroleum Products | Excise | Monthly |
| 30 | 2200T | Excise Tax — Tobacco Products | Excise | Monthly |
| 31 | 2550M | Monthly VAT Declaration | VAT | Monthly |
| 32 | 2550Q | Quarterly VAT Return | VAT | Quarterly |
| 33 | 2551M | Monthly Percentage Tax Return | PT | Monthly |
| 34 | 2551Q | Quarterly Percentage Tax Return | PT | Quarterly |
| 35 | 2552 | Percentage Tax — Shares Traded via LSE | PT | Monthly |
| 36 | 2553 | Percentage Tax under Special Laws | PT | As applicable |

**Not in eBIRForms** (certificates, not returns): 2307, 2306, 2316, 0619-E, 0619-F, 1601-EQ, 1601-FQ.

---

## Filing Calendar Matrix

| Form | Frequency | Deadline rule | eFPS extension | Penalty |
|---|---|---|---|---|
| 0605 | Annual | January 31 | N/A | 25% surcharge + 12% interest/yr |
| 0619-E | Monthly (M1, M2 only) | 10th of following month | +5 days (group-staggered) | 25% surcharge + 12% interest |
| 0619-F | Monthly (M1, M2 only) | 10th of following month | +5 days | 25% surcharge |
| 1601-C | Monthly | 10th of following month; Dec → Jan 25 | +5 days | 25% surcharge |
| 1601-EQ | Quarterly | Last day of month after quarter end | +5 days | 25% surcharge |
| 1601-FQ | Quarterly | Last day of month after quarter end | +5 days | 25% surcharge |
| 1604-CF | Annual | January 31 | N/A | 25% surcharge |
| 1604-E | Annual | March 1 | N/A | 25% surcharge |
| 1700 | Annual | April 15 | N/A | 25% surcharge + 12% interest |
| 1701 / 1701Q | Annual / Quarterly | April 15 / 60 days after quarter | +5 days (quarterly) | 25% surcharge |
| 1702Q | Quarterly | 60 days after quarter end | +5 days | 25% surcharge |
| 1702-RT/MX/EX | Annual | April 15 | N/A | 25% surcharge + 12% interest |
| 2550M | Monthly | 25th of following month | +5 days | 25% surcharge |
| 2550Q | Quarterly | 25th of month after quarter end | +5 days | 25% surcharge |
| 2551M | Monthly | 20th of following month | N/A | 25% surcharge |
| 2551Q | Quarterly | 25th of month after quarter end | N/A | 25% surcharge |

**eFPS group stagger**: filing groups A–E by industry; each group gets +5 calendar days past the base deadline.

**Official deadline surface**: RMC 110-2025 — Interactive Tax Calendar (digital replaces printed).

---

## eServices Complete Inventory (confirmed live 2026-04-17)

| # | Service | URL | Purpose | API? |
|---|---|---|---|---|
| 1 | ORUS | `orus.bir.gov.ph` | TIN registration, COR, business registration (replaces eREG) | No |
| 2 | NewBizReg | `newbizreg.bir.gov.ph` | New Business Registration | No |
| 3 | TRRA | `trra.bir.gov.ph` | Taxpayer Registration-Related Application | No |
| 4 | eFPS v5.74 | `efps.bir.gov.ph` | Electronic filing + payment (mandated for large taxpayers) | No (XML upload only) |
| 5 | eBIRForms v7.9.5.0 | `bir.gov.ph/ebirforms` | Offline prep + online submit (36 forms) | No (XML import) |
| 6 | ePAY | `bir.gov.ph/ePay` | Tax payment via AABs, GCash, PayMaya, bank online | No (redirect) |
| 7 | eTSPCert | `etspcert.bir.gov.ph` | Tax Software Provider certification (enables server-to-server XML submission) | Certification program |
| 8 | eONETT | `eonett.bir.gov.ph` | One-time transactions: CGT, donor's, DST | No |
| 9 | eTCBP-TCVC | `web-services.bir.gov.ph` | Tax clearance for government bidding | Email submission |
| 10 | eTCS | `tcsfo.bir.gov.ph` | Tax clearance system (pilot: RR 7A/7B/8A/8B, NCR) | No |
| 11 | eAFS | `eafs.bir.gov.ph` | Audited Financial Statements PDF upload | No |
| 12 | eAPPOINTMENT | `eappointment.bir.gov.ph` | Scheduling | No |
| 13 | WT Calculator | `bir.gov.ph` (embedded) | Withholding tax computation | No |

**No public REST APIs exist.** eTSPCert is the only legitimate path for automated submission.

---

## Current Legislative Programs (active from BIR homepage, 2026-04-17)

| # | Law | Short name | Impact on IPAI |
|---|---|---|---|
| 1 | RA 12253 | Enhanced Fiscal Regime for Large-Scale Metallic Mining | Not in scope |
| 2 | RA 12214 | Capital Markets Efficiency Promotion Act | Affects DST on shares |
| 3 | RA 12066 | CREATE MORE | Corporate IT rate 25%/20%, MCIT 1%, incentives modernization |
| 4 | RA 12023 | VAT on Digital Services | 12% VAT on non-resident digital services — **rate seeded, not wired in Odoo** |
| 5 | RA 11976 | Ease of Paying Taxes | Simplified filing, classification system reform |
| 6 | RA 11213 | Tax Amnesty | Estate, delinquencies amnesty |
| 7 | RA 11534 | CREATE (Corporate Recovery) | Base law for corporate tax incentives |

---

## IPAI Coverage Gap Matrix (updated 2026-04-18)

### Automation readiness by form

| Form | Seeded in `bir_forms.xml` | XML generator | DAT alphalist | PDF report | eFPS submit | Priority |
|---|---|---|---|---|---|---|
| 0619-E | ✅ | ❌ | N/A | ❌ | ❌ | P0 |
| 0619-F | ❌ | ❌ | N/A | ❌ | ❌ | P1 |
| 1601-C | ✅ | ❌ | N/A | ❌ | ❌ | P1 |
| 1601-EQ | ✅ | ❌ | ❌ (QAP) | ❌ | ❌ | P0 |
| 1601-FQ | ❌ | ❌ | ❌ | ❌ | ❌ | P1 |
| 1604-CF | ✅ | ❌ | ❌ (alphalist) | ❌ | N/A | P0 |
| 1604-E | ✅ | ❌ | ❌ (alphalist) | ❌ | N/A | P0 |
| 1701Q | ✅ | ❌ | N/A | ❌ | ❌ | P1 |
| 1702Q | ❌ | ❌ | N/A | ❌ | ❌ | P0 |
| 1702-RT | ❌ | ❌ | N/A | ❌ | ❌ | P0 |
| 2307 (cert) | ✅ (skill) | ❌ | N/A | ❌ | N/A | P0 |
| 2550Q | ✅ | ❌ | N/A | ❌ | ❌ | P0 |

### P0 blockers for R3 (Oct 14, 2026)

1. **eBIRForms XML generator** — referenced but not implemented (`bir_extractor.py` stub)
2. **DAT file generator** (SAWT/QAP/alphalist) — `alphalist_attachment_id` field exists, no logic
3. **4 forms not seeded** — 0619-F, 1601-FQ, 1702Q, 1702-RT
4. **n8n references in `bir-eservices` skill** — deprecated, replace with Azure Functions
5. **eTSPCert application** — not started; certification takes weeks

### Deprecated references to clean up

| Item | Status | Replacement |
|---|---|---|
| Supabase Edge Functions for tax compute | Deprecated 2026-03-26 | Azure Functions |
| Supabase `ops.bir_forms` schema | Deprecated | PG Flex `platform` schema |
| n8n BIR workflow bridge | Deprecated 2026-04-07 | Azure Logic Apps / Azure Functions |
| `eREG` references | Replaced by ORUS | Update docs |

---

*Generated by tax-bir-scan, 2026-03-18 · Updated 2026-04-18 with deep research from bir.gov.ph + Foundry inference validation*
