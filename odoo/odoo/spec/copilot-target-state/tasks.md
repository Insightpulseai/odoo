# Copilot Target-State — Tasks

## Wave 1: Lock the Assistant Surface

- [ ] **1.1** Create BIR regulation knowledge store in Foundry IQ
- [ ] **1.2** Upload form-type guides (2550M, 2550Q, 1601-C, 1601-E, etc.)
- [ ] **1.3** Register knowledge store in Foundry project
- [x] **1.4** Create eval datasets: `bir_advisory.yaml` (50 cases)
- [x] **1.5** Create eval datasets: `bir_ops.yaml` (30 cases)
- [x] **1.6** Create eval datasets: `bir_actions.yaml` (40 cases)
- [ ] **1.7** Configure guardrails: no ungrounded tax advice
- [ ] **1.8** Enable App Insights tracing for `ipai-odoo-copilot-azure`
- [ ] **1.9** Wire Azure Document Intelligence for invoice/receipt/BIR extraction
- [ ] **1.10** Run Advisory eval: groundedness ≥ 0.8

## Wave 2: Build Hidden Backend Roles

- [ ] **2.1** Create `copilot_router.py` (deterministic, no LLM)
- [ ] **2.2** Implement Ops runtime — read-only Odoo queries
- [ ] **2.3** Implement Actions runtime — approval-gated state transitions
- [ ] **2.4** Add `approved` state to `bir.tax.return`
- [ ] **2.5** Add `action_approve()` with `group_ipai_bir_approver` check
- [ ] **2.6** Create `group_ipai_bir_approver` security group
- [ ] **2.7** Update `action_file()` to require `state == 'approved'`
- [ ] **2.8** Create `copilot_tools_bir.xml` with 8 BIR tool definitions
- [ ] **2.9** Wire tools: `compute_bir_vat_return` → `action_compute()`
- [ ] **2.10** Wire tools: `compute_bir_withholding_return` → `action_compute()`
- [ ] **2.11** Wire tools: `validate_bir_return` → `action_validate()`
- [ ] **2.12** Wire tools: `check_overdue_filings` → `bir.filing.deadline` query
- [ ] **2.13** Wire tools: `generate_alphalist`, `generate_efps_xml`, `generate_bir_pdf`
- [ ] **2.14** Write router unit tests: 100 test cases
- [ ] **2.15** Run Actions eval: safety = 1.0

## Wave 3: Operationalize Odoo Project

- [ ] **3.1** Create `bir.filing.task.template` model
- [ ] **3.2** Fields: form_type, cadence, lead_days, owner_role, prerequisite_state, approval_required
- [ ] **3.3** Normalize month-end closing workbook into seed XML
- [ ] **3.4** Create seed data: task templates for all 24 form types
- [ ] **3.5** Create cron: auto-generate tasks N days before deadline
- [ ] **3.6** Implement task dependency chains (reconcile → compute → validate → ... → confirm)
- [ ] **3.7** Create milestones: books ready, tax computed, validated, approved, filed, paid, closed
- [ ] **3.8** Create project roles: preparer, reviewer, approver, payer, compliance owner
- [ ] **3.9** Create company-scoped compliance project template
- [ ] **3.10** Create Kanban view grouped by project stage
- [ ] **3.11** Create calendar view with filing deadlines
- [ ] **3.12** Create "blocked filings" filter
- [ ] **3.13** Link generated tasks to `bir.tax.return` records

## Wave 4: Add Approval Semantics

- [ ] **4.1** Design PLM-style approval extension model
- [ ] **4.2** Implement required/optional/comments-only approval types
- [ ] **4.3** Gate: for review → approved for export (required: `group_ipai_bir_approver`)
- [ ] **4.4** Gate: approved for export → filed (required: `group_ipai_finance_manager`)
- [ ] **4.5** Gate: filed/paid → confirmed (required: compliance owner)
- [ ] **4.6** Auto-create activity on approval request
- [ ] **4.7** Blocked state when required approval missing
- [ ] **4.8** Audit trail: who approved, when, comments
- [ ] **4.9** Tests: required approval blocks transition, optional does not

## Wave 5: Bind Artifacts and Evidence

- [ ] **5.1** Link BIR return ↔ project task (Many2one)
- [ ] **5.2** Attach export artifacts (eFPS XML, PDF, alphalist) to task
- [ ] **5.3** Add proof-of-filing attachment field
- [ ] **5.4** Add proof-of-payment attachment field
- [ ] **5.5** Add approver evidence fields (who, when, comments)
- [ ] **5.6** Create evidence completeness check before period close
- [ ] **5.7** Wire APIM production ingress
- [ ] **5.8** End-to-end test: task → return → artifact → proof → approval chain
- [ ] **5.9** Configure APIM routes for BIR-specific endpoints

## Completed (Cross-cutting)

- [x] **X.1** Create `spec/copilot-target-state/` spec kit
- [x] **X.2** Create `spec/tax-pulse-sub-agent/` spec kit
- [x] **X.3** Port TaxPulse rates, rules engine, test fixtures (67 tests)
- [x] **X.4** Create `infra/ssot/agents/tax_pulse_tool_contracts.yaml`
- [x] **X.5** Register BIR pack in `agent_capability_matrix.yaml`
- [x] **X.6** Create eval datasets (advisory, ops, actions)
- [x] **X.7** Create SFT training assets (catalog, train, valid)
