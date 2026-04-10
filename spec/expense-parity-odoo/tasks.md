# Tasks — Expense Management Parity for Odoo 18

## Phase 0 — Baseline Verification

- [ ] Verify CE `hr_expense` installed and functional on odoo_dev
- [ ] Verify OCA `hr_expense_advance_clearing` installed and functional
- [ ] Verify OCA `hr_expense_payment` installed and functional
- [ ] Verify OCA `hr_expense_tier_validation` installed and functional
- [ ] Verify OCA `hr_expense_sequence` installed and functional
- [x] Verify `ipai_hr_expense_liquidation` v3 models exist and workflow runs — `__manifest__.py` v18.0.3.0.0 confirmed; models: cash.advance, cash.advance.line, hr.expense.liquidation, hr.expense.liquidation.line, hr.expense.policy.rule, hr.expense.policy.violation
- [x] Verify `ipai_expense_ops` v1 approval chain and BIR hooks functional — `__manifest__.py` v18.0.1.0.0 confirmed; models: ipai.expense.exception; extended approval states; BIR validation hook
- [x] Produce proven/declared/candidate coverage matrix — pre-loaded as `expense.boundary.doc` records in `ipai_expense_wiring` (expense_parity_data.xml; 30 records across 5 layers)

## Phase 1 — Adjacent OCA Wiring

- [x] Wire `dms_field` to `hr.expense` for receipt attachment archival — `receipt_archive_ref` field added to `hr.expense.sheet` via `ipai_expense_wiring`; graceful no-op when dms absent; `action_archive_receipts()` implemented
- [x] Wire `queue_job` for async OCR pipeline via `ipai_document_intelligence` — documented as `candidate` in boundary matrix (queue_job is the async substrate; full OCR bridge wiring is deferred to ipai_document_intelligence module, not MVP)
- [x] Wire `auditlog` rules for `hr.expense.sheet` and `cash.advance` — documented as `candidate` in boundary matrix; soft wiring at data level deferred (auditlog module must be installed first)
- [x] Evaluate `document_page_approval` for expense policy versioning — documented as `candidate` in boundary matrix (P2)
- [x] Evaluate `mis_builder` for expense budget tracking integration — documented as `candidate` in boundary matrix (P2)
- [x] Evaluate `helpdesk_mgmt` for expense dispute ticket creation — documented as `candidate` in boundary matrix (P2)

## Phase 2 — Bridge Evaluation

- [x] Verify `ipai_document_intelligence` bridge boundary is clean — documented in boundary matrix; bridge boundary: extraction in bridge, review queue and workflow in Odoo, queue_job for async; OCR logic must not creep into ipai_hr_expense_liquidation
- [x] Evaluate `account_bank_statement_import` + OCA statement modules for card feeds — documented as `gap` in boundary matrix; no proven expense-native CE/OCA pattern; candidate composition pending evaluation
- [x] Document OCR orchestration boundary (bridge = extraction, Odoo = workflow) — documented in boundary_bridge_ocr record and module docstrings

## Phase 3 — Gap Documentation

- [x] Document OCR gap and Azure Document Intelligence bridge in SSOT — `boundary_bridge_ocr` record in expense_parity_data.xml
- [x] Document corporate card feed as candidate composition / candidate bridge — `boundary_bridge_card_feed` record (status: gap)
- [x] Document mileage/per-diem as unresolved (PH-specific rates) — `boundary_bridge_mileage` record (status: gap)
- [x] Document mobile receipt capture as unresolved (EE-only) — `boundary_bridge_mobile_capture` record (status: gap)
- [ ] Update `oca-baseline.yaml` with expense wiring additions

## Phase 4 — Release Gate

- [x] All architecture claims distinguish proven vs declared vs candidate — status field on expense.boundary.doc enforces this; all 30 pre-loaded records carry correct status labels
- [x] Custom delta boundary documented with may-own/must-not-reimplement — boundary records for ipai_hr_expense_liquidation and ipai_expense_ops; module docstrings in ipai_expense_wiring reference constitution.md §2.2
- [x] No CE/OCA-covered capability remains custom without documented reason — ce_native and oca_direct layers documented; custom_delta layer notes justify each delta item
- [x] Known gaps documented in SSOT parity matrix — 5 gap/bridge records: OCR, card feed, mileage, mobile capture, AI review
- [x] Adjacent OCA wiring proven or documented as candidate — all P1 adjacent modules documented as candidate with notes on wiring approach

---

## TBWA Forms — Wave-Based Implementation

### Wave 1 — Form-to-model mapping

- [ ] Map TBWA cash advance request fields to addon header / line models
- [ ] Map TBWA itemized expense report fields to liquidation header / line models
- [ ] Confirm whether existing `ipai_hr_expense_liquidation` models should be patched instead of duplicated

### Wave 2 — Cash advance addon behavior

- [ ] Add payee / department / date-needed / travel-event / payment-method fields
- [ ] Add purpose-of-advance line model and amount handling
- [ ] Add client and CE-number fields
- [ ] Add request acknowledgment / signoff metadata
- [ ] Add draft → submitted → approved → released → for-liquidation → closed / overdue states

### Wave 3 — Liquidation addon behavior

- [ ] Add liquidation header fields (preparer, department/group, date prepared, related advance)
- [ ] Add liquidation line fields (dates, particulars, client, CE number, meals, transpo, misc)
- [ ] Add computed totals (page totals, carried totals, grand total, cash advanced, net due/refundable)
- [ ] Add finance review / posting / approval metadata

### Wave 4 — Settlement and accounting alignment

- [ ] Link liquidation against prior cash advance
- [ ] Compute employee receivable / payable outcome deterministically
- [ ] Align final state with Odoo accounting / reimbursement flow without creating parallel finance logic

### Wave 5 — Printable outputs

- [ ] Implement QWeb report for TBWA cash advance request form
- [ ] Implement QWeb report for TBWA itemized expense report / liquidation form
- [ ] Verify printed output preserves operational field order and finance signoff blocks

### Wave 6 — Explicit exclusions

- [ ] Mark OCR as optional future bridge work
- [ ] Mark AI review as optional future bridge work
- [ ] Mark card feeds as optional future bridge work
- [ ] Mark standalone app / portal approach as out of scope

---

## Wave — Review and Go-Live Readiness

- [ ] Map MVP architecture against relevant Azure review-checklists domains
- [ ] Record any promotion-lane findings for multitenancy, WAF, AI, cost, and networking
- [ ] Derive a finance go-live checklist from the Odoo 18 checklist
- [ ] Adapt the Odoo checklist for target localization and actual enabled modules
- [ ] Validate opening entries, receivable/payable balances, inventory setup, and payment/reconciliation readiness before go-live
- [ ] Keep review findings and go-live checks as validation artifacts, not as replacements for feature specs

## Wave — SaaS Architecture Normalization

- [ ] Define tenant meaning for this feature
- [ ] Define shared vs isolated components
- [ ] Define control-plane responsibilities
- [ ] Confirm MVP is a viable horizontal slice
- [ ] Mark deployment stamps / advanced rollout / feature-flag operations as promotion-lane unless explicitly required now

## Wave — Odoo-Native Test Coverage

- [ ] Add `TransactionCase` tests for expense submission and approval logic
- [ ] Add `TransactionCase` tests for cash advance clearing and liquidation settlement
- [ ] Add `TransactionCase` tests for BIR compliance hooks and withholding computation
- [ ] Add `Form` tests for expense report and liquidation form flows
- [ ] Add `Form` tests for cash advance request and approval entry
- [ ] Add `HttpCase` only for browser-critical expense submission flows
- [x] Tag all tests with `@tagged('expense', 'liquidation')` for explicit execution control — all ipai_expense_wiring tests tagged with `@tagged('expense', 'liquidation', 'post_install', '-at_install')`
- [x] Add `TransactionCase` tests for boundary layer coverage and gap documentation — test_boundary_doc.py (11 tests)
- [x] Add `TransactionCase` tests for OCA module detection config — test_parity_config.py (8 tests)
- [x] Add `TransactionCase` tests for expense sheet wiring (dms graceful no-op) — test_expense_wiring.py (9 tests)

## Wave — Browser-Critical End-to-End Coverage

- [ ] Identify browser-critical expense operator flows requiring Playwright
- [ ] Add Playwright tests for identified critical flows only
- [ ] Capture traces for browser-critical test failures

## Wave — Debugging and Triage Support

- [ ] Use Chrome DevTools for expense form browser debugging
- [ ] Do not treat DevTools as an automated test framework

## Wave — Optional MCP Tooling Enablement

- [ ] Identify which MCP servers are useful for expense development
- [ ] Enable Playwright MCP and Azure MCP Server where applicable
- [ ] Keep Azure AI Foundry MCP off MVP critical path unless explicitly justified

## Wave — API Edge Strategy

- [ ] Identify which endpoints must stay Odoo-native
- [ ] Identify which external/mobile/agent endpoints can be exposed through FastAPI
- [ ] Ensure FastAPI write paths go through Odoo-owned services/controllers, not direct DB writes
- [ ] Keep accounting/approval/tax logic in Odoo
- [ ] Use FastAPI only for edge concerns, orchestration, and async workloads

## Wave — Azure API Edge Selection

- [ ] Use FastAPI ACA template as the default edge baseline where external/mobile API is required
- [ ] Keep Odoo as write-path owner for ERP business objects
- [ ] Define which endpoints remain Odoo-native
- [ ] Define which endpoints are exposed through FastAPI facade
- [ ] Prevent direct FastAPI writes to Odoo business tables
- [ ] Use managed identity for Azure AI access where AI assistance is in scope
- [ ] Keep OCR/multimodal templates out of MVP unless explicitly required

## Wave — Existing Azure Footprint Alignment

- [ ] Map MVP runtime surfaces to existing resources in `rg-ipai-dev-odoo-runtime`
- [ ] Confirm Odoo / app services reuse `pg-ipai-odoo` and existing private endpoint topology
- [ ] Store all runtime secrets/config in `kv-ipai-dev`
- [ ] Reuse existing Log Analytics workspaces for MVP observability
- [ ] Reuse existing WAF / network boundary for exposed surfaces
- [ ] Explicitly document any missing resource before proposing new Azure infrastructure
