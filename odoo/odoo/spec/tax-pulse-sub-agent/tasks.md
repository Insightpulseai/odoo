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
- [ ] **3.7** Create `ssot/agents/tax_pulse_tool_contracts.yaml`
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

## AFC Parity — Bridge & Contract Tasks

### Wave 3A: Bridge OpenAPI Contract
- [x] **3A.1** Create `agents/contracts/openapi/ipai_odoo_bridge.openapi.yaml` with narrow endpoint spec
- [ ] **3A.2** Implement Azure Function / FastAPI bridge for read endpoints
- [ ] **3A.3** Configure APIM policy for `apim-ipai-dev.azure-api.net/odoo/*`
- [ ] **3A.4** Implement `getComplianceFindings` bridge endpoint
- [ ] **3A.5** Implement `getComplianceTasks` bridge endpoint
- [ ] **3A.6** Implement `getCompliancePeriods` bridge endpoint
- [ ] **3A.7** Test: bridge returns correct data, APIM auth enforced

### Wave 3B: Compliance Check Registry
- [x] **3B.1** Create `ssot/tax/compliance_check_catalog.yaml` with 12 checks (CI-001 to CI-012)
- [ ] **3B.2** Implement check execution method on `tax.compliance.period`
- [ ] **3B.3** Wire each check to its `query_source` Odoo model
- [ ] **3B.4** Persist findings as `tax.compliance.finding` records
- [ ] **3B.5** Test: all 12 checks execute and produce correct findings

### Wave 3C: Narrow Write Operations
- [x] **3C.1** Create `agents/contracts/ui/confirm_action_card.json` (Adaptive Card v1.4)
- [ ] **3C.2** Implement `updateComplianceTask` write endpoint in bridge
- [ ] **3C.3** Implement `createComplianceFinding` write endpoint in bridge
- [ ] **3C.4** Implement `postChatterNote` write endpoint in bridge
- [ ] **3C.5** Wire confirmation card presentation before all writes
- [ ] **3C.6** Test: write blocked without confirmation, chatter note posted on every write

### Wave 5A: Teams Card Surfaces
- [x] **5A.1** Create `agents/contracts/ui/adaptive_cards_index.yaml` with 6 card definitions
- [ ] **5A.2** Implement ComplianceBriefingCard rendering in agent
- [ ] **5A.3** Implement FindingCard with Create Finding + View buttons
- [ ] **5A.4** Implement TaskCard with Mark Complete + Reassign buttons
- [ ] **5A.5** Implement DeadlineAlertCard proactive DM
- [ ] **5A.6** Configure Teams channel integration for #tax-compliance
- [ ] **5A.7** Test: cards render correctly, button actions route through bridge

### Wave 5B: Odoo Widget Integration
- [ ] **5B.1** Add BIR compliance panel to `ipai_ai_copilot` OWL widget
- [ ] **5B.2** Render Adaptive Cards in Odoo web client context
- [ ] **5B.3** Test: same card JSON works in both Teams and Odoo

### Prompt & Knowledge Refactor
- [ ] **P.1** Refactor Tax Pulse agent instructions to reference externalized knowledge sources
- [ ] **P.2** Remove any hardcoded tax rules from prompt templates
- [ ] **P.3** Add `compliance_check_catalog.yaml` as SSOT reference in agent instructions
- [ ] **P.4** Validate grounding: agent cites AI Search sources, not embedded knowledge

### Existing Module Mapping
- [x] **M.1** Update `ssot/agents/tax_pulse_tool_contracts.yaml` with agent metadata and module mapping
- [ ] **M.2** Verify `ipai_bir_tax_compliance` owns compliance checks and findings
- [ ] **M.3** Verify `ipai_bir_notifications` owns deadline alerts and proactive notifications
- [ ] **M.4** Verify `ipai_finance_ppm` owns close orchestration tasks
- [ ] **M.5** Verify `ipai_odoo_copilot` owns copilot runtime and card dispatch

## Workstream — n8n alignment

- [ ] N.1 Document which current Odoo interactions can use the native n8n Odoo node
- [ ] N.2 Identify gaps that require HTTP Request/custom bridge instead of native Odoo node
- [ ] N.3 Define approved async automations for Tax Pulse (alerts, reminders, package delivery, escalation)
- [ ] N.4 Define which write actions remain approval-gated via Foundry/Odoo instead of direct n8n mutation
- [ ] N.5 Add n8n webhook/event patterns for task-state-driven notifications
