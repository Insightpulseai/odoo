# Copilot Target-State — Plan

## Current State

- 1 Foundry prompt agent: `ipai-odoo-copilot-azure`
- BIR module has: `draft → computed → validated → filed → confirmed` state machine
- `mail.activity.mixin` inherited (activities work)
- No explicit Approved stage between validated and filed
- No recurring task templates
- No document ingestion pipeline
- Copilot has 18 tools, 1 BIR tool (read-only `bir_compliance_search`)

## Implementation Order

### Phase 2A — Odoo-native workflow enhancement (immediate)

**Add Approved stage** to `bir.tax.return` state machine:
- `draft → computed → validated → approved → filed → confirmed`
- `action_approve()` requires `group_ipai_bir_approver` security group
- Approval creates `mail.activity` for export/file step
- Blocked state if validation fails

**Add BIR filing task template model** (`bir.filing.task.template`):
- Template-based recurring task generation
- Maps to `project.task` if project module installed, else standalone
- Cadence: monthly/quarterly/annual per form type
- Auto-generate tasks N days before deadline
- Milestone checkpoints: compute → validate → approve → export → file → confirm

**Add compliance worklist reporting**:
- Kanban view grouped by stage
- Calendar view with filing deadlines
- "Blocked filings" filter (missing data, failed validation)

### Phase 2B — Copilot tools as Odoo action triggers

8 copilot tools that call Odoo's own state machine:
1. `compute_bir_vat_return` → `action_compute()` on `bir.vat.return`
2. `compute_bir_withholding_return` → `action_compute()` on `bir.withholding.return`
3. `validate_bir_return` → `action_validate()` on `bir.tax.return`
4. `check_overdue_filings` → query `bir.filing.deadline` state=overdue
5. `generate_alphalist` → `action_generate_alphalist()` on `bir.alphalist`
6. `generate_efps_xml` → export stub (Phase 3)
7. `generate_bir_pdf` → report action
8. `bir_compliance_search` → exists (read-only)

### Phase 3 — Document Intake & Extraction Pack

- Azure AI Document Intelligence for invoice/receipt/BIR attachment ingestion
- OCR → structured extraction → normalized evidence
- Document-to-record linking on `bir.tax.return`

### Phase 4 — Router + Ops + Actions backend

- Agent Framework runtimes behind Advisory
- Router: deterministic request classification
- Ops: read-only diagnostics
- Actions: approval-gated execution

### Phase 5 — APIM + production hardening

- APIM AI Gateway as ingress
- Eval datasets and gates
- Simulation mode for Actions

## Exit Gates

| Phase | Gate |
|---|---|
| 2A | Approved stage works, task templates generate, worklist renders |
| 2B | All 8 copilot tools trigger correct Odoo actions |
| 3 | Document extraction returns structured data, links to records |
| 4 | Router correctly classifies and routes 95%+ of requests |
| 5 | APIM fronts all traffic, traces visible, evals passing |
