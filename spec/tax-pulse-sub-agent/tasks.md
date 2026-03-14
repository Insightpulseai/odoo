# Tasks — Tax Pulse Sub-Agent (BIR Compliance Pack)

## Wave 1: Knowledge Ingestion

- [ ] **1.1** Create `data/knowledge/` directory with BIR regulation summaries
- [ ] **1.2** Prepare form-type guides (2550M, 2550Q, 1601-C, 1601-E, etc.)
- [ ] **1.3** Register BIR knowledge store in Foundry project
- [ ] **1.4** Add grounding check to `bir_compliance_search` tool
- [ ] **1.5** Test: Advisory refuses ungrounded tax advice

## Wave 2: Rates/Rules Port — COMPLETE

- [x] **2.1** Port `ph_rates_2025.json` (TRAIN brackets, EWT W010-W170, FWT, corporate, VAT)
- [x] **2.2** Port `vat.rules.yaml` (8 JSONLogic rules)
- [x] **2.3** Port `ewt.rules.yaml` (11 JSONLogic rules)
- [x] **2.4** Port rules engine: `evaluator.py`, `formula.py`, `loader.py`
- [x] **2.5** Create test fixtures: `vat_basic_transactions.csv`, `vat_basic_expected_lines.csv`, `ewt_expected_withholding.csv`
- [x] **2.6** Create `test_rules_engine.py` (37 tests)
- [x] **2.7** Create `test_bir_vat_compute.py` (12 tests)
- [x] **2.8** Create `test_bir_ewt_compute.py` (18 tests)
- [x] **2.9** Verify: 67/67 tests pass, all py_compile clean, JSON/YAML parse clean

## Wave 3: Compute/Validate Tools

- [ ] **3.1** Add `approved` state to `bir.tax.return` state selection
- [ ] **3.2** Add `action_approve()` method with `group_ipai_bir_approver` check
- [ ] **3.3** Create `group_ipai_bir_approver` security group
- [ ] **3.4** Update `action_file()` to require `state == 'approved'`
- [ ] **3.5** Update statusbar and button visibility for approved stage
- [ ] **3.6** Create `copilot_tools_bir.xml` with 8 BIR tool definitions
- [ ] **3.7** Create `infra/ssot/agents/tax_pulse_tool_contracts.yaml`
- [ ] **3.8** Wire `compute_bir_vat_return` → `action_compute()` on `bir.vat.return`
- [ ] **3.9** Wire `compute_bir_withholding_return` → `action_compute()` on `bir.withholding.return`
- [ ] **3.10** Wire `validate_bir_return` → `action_validate()` on `bir.tax.return`
- [ ] **3.11** Wire `check_overdue_filings` → query `bir.filing.deadline` state=overdue
- [ ] **3.12** Wire `generate_alphalist` → `action_generate_alphalist()` stub
- [ ] **3.13** Wire `generate_efps_xml` → eFPS export stub
- [ ] **3.14** Wire `generate_bir_pdf` → report action
- [ ] **3.15** Add BIR Compliance Pack to `agent_capability_matrix.yaml`

## Wave 4: Filing/Export Artifacts

- [ ] **4.1** Create eFPS XML export wizard (`bir_efps_export.py`)
- [ ] **4.2** Create PDF report templates (QWeb) for 2550M, 1601-C, 1601-E
- [ ] **4.3** Create alphalist generation wizard
- [ ] **4.4** Create 2316 certificate generation
- [ ] **4.5** Validate eFPS XML against BIR schema samples
- [ ] **4.6** Test: PDF renders with correct amounts and TIN
- [ ] **4.7** Test: Alphalist aggregates from WHT returns correctly

## Wave 5: Project/Task/Approval Orchestration

- [ ] **5.1** Create `bir.filing.task.template` model
- [ ] **5.2** Define fields: form_type, cadence, lead_days, owner_role, prerequisite_state, approval_required
- [ ] **5.3** Create seed XML: task templates for all 24 form types
- [ ] **5.4** Normalize month-end closing workbook into canonical seed data
- [ ] **5.5** Create cron: auto-generate tasks N days before deadline
- [ ] **5.6** Link generated tasks to `bir.tax.return` records
- [ ] **5.7** Create Kanban view grouped by filing stage
- [ ] **5.8** Create calendar view with filing deadlines
- [ ] **5.9** Add "Blocked filings" computed field + filter
- [ ] **5.10** Wire approval activities to `action_approve()` completion

## Wave 6: Evals + SFT

- [ ] **6.1** Create `eval/datasets/bir_advisory.yaml` (50 informational cases)
- [ ] **6.2** Create `eval/datasets/bir_ops.yaml` (30 navigational cases)
- [ ] **6.3** Create `eval/datasets/bir_actions.yaml` (40 transactional cases)
- [ ] **6.4** Create `eval/training/bir_sft_catalog.yaml` (sample catalog)
- [ ] **6.5** Create `eval/training/bir_sft_train.jsonl` (training set)
- [ ] **6.6** Create `eval/training/bir_sft_valid.jsonl` (validation set)
- [ ] **6.7** Run baseline Advisory evaluation: groundedness ≥ 0.8
- [ ] **6.8** Run baseline Actions evaluation: safety = 1.0
- [ ] **6.9** Capture eval evidence in `docs/evidence/`

## Wave 7: Production Wiring

- [ ] **7.1** Update router rules for BIR intent classification
- [ ] **7.2** Register BIR pack in Foundry Tool Catalog
- [ ] **7.3** Configure APIM route for BIR-specific endpoints
- [ ] **7.4** Enable App Insights tracing for BIR domain
- [ ] **7.5** Test graceful degradation when BIR knowledge store unavailable
- [ ] **7.6** End-to-end: BIR request → APIM → Router → Advisory/Actions → Odoo
