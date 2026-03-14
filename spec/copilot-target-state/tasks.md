# Copilot Target-State — Tasks

## Phase 2A: Odoo-Native Workflow Enhancement

### Approved Stage
- [ ] Add `approved` to state selection on `bir.tax.return`
- [ ] Add `action_approve()` method with `ensure_one()` + security check
- [ ] Create `group_ipai_bir_approver` security group
- [ ] Update statusbar widget to include `approved` step
- [ ] Update button visibility conditions for approve step
- [ ] Add approval activity creation on `action_validate()` completion
- [ ] Update `action_file()` to require `state == 'approved'` (not `validated`)
- [ ] Update views: form, list, search filters
- [ ] Update tests for new state transition

### Filing Task Templates
- [ ] Create `bir.filing.task.template` model
- [ ] Fields: form_type, cadence (monthly/quarterly/annual), lead_days, owner_role, prerequisite_state, approval_required, output_artifact
- [ ] Seed XML data for all 24 form types
- [ ] Cron job: auto-generate tasks N days before deadline
- [ ] Link to `project.task` if project module installed (optional dep)
- [ ] Milestone checkpoints per generated task

### Compliance Worklist
- [ ] Kanban view grouped by stage for `bir.tax.return`
- [ ] "Blocked filings" computed field + filter
- [ ] Month-end close checklist view
- [ ] Overdue filings dashboard widget

## Phase 2B: Copilot Tools as Action Triggers

- [ ] `compute_bir_vat_return` tool definition in copilot_tools.xml
- [ ] `compute_bir_withholding_return` tool definition
- [ ] `validate_bir_return` tool definition
- [ ] `check_overdue_filings` tool definition
- [ ] `generate_alphalist` tool definition
- [ ] `generate_efps_xml` tool stub
- [ ] `generate_bir_pdf` tool definition
- [ ] Update `bir_compliance_search` with improved grounding
- [ ] Add BIR Compliance Pack to agent capability matrix

## Phase 3: Document Intake & Extraction Pack
- [ ] Azure Document Intelligence integration scaffold
- [ ] Invoice/receipt extraction model
- [ ] BIR attachment classifier
- [ ] Document-to-record linking on `bir.tax.return`

## Phase 4: Router + Ops + Actions
- [ ] Agent Framework router workflow
- [ ] Ops runtime (read-only)
- [ ] Actions runtime (approval-gated)
- [ ] Integration with Advisory front door

## Phase 5: Production Hardening
- [ ] APIM AI Gateway configuration
- [ ] Eval datasets per role
- [ ] Simulation mode for Actions
- [ ] Foundry tracing + App Insights connection
