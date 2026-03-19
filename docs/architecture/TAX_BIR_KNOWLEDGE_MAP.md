# Tax/BIR Knowledge Map

> Domain map of all discovered tax/BIR knowledge areas, forms, workflows,
> rules packs, review engines, reporting/eval assets, and tool/API surfaces.
> Generated: 2026-03-18

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
+-- eServices Integration
|   +-- eFPS (Electronic Filing & Payment System)
|   +-- eBIRForms (Offline preparation + online submission)
|   +-- eAFS (Audited Financial Statements)
|   +-- eREG/ORUS (Registration)
|   +-- TIN Verification
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

*Generated by tax-bir-scan, 2026-03-18 (updated with TaxPulse-PH-Pack salvage)*
