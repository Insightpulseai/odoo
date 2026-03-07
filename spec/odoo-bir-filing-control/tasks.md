# BIR Filing Control - Task Checklist

## Phase 1: Filing Calendar + Obligation Tracker

- [ ] Create `ipai_finance_bir_filing` module scaffold (`__init__.py`, `__manifest__.py`)
- [ ] Implement `bir.filing.schedule` model (BIR statutory schedule data)
- [ ] Load BIR schedule data (all 9 form types with frequencies and deadlines)
- [ ] Implement `bir.filing.obligation` model with status workflow
- [ ] Add status workflow: draft -> in_preparation -> ready_for_review -> approved -> filed -> confirmed
- [ ] Integrate Philippine holiday calendar for deadline adjustment
- [ ] Create calendar auto-population wizard (generate obligations per fiscal year)
- [ ] Build obligation list view with filters (status, form type, due date)
- [ ] Build obligation calendar view (color-coded by status)
- [ ] Create security groups: bir_filing_preparer, bir_filing_reviewer, bir_filing_admin
- [ ] Write security access rules (`ir.model.access.csv`)
- [ ] Create record rules (company-based, role-based)
- [ ] Add menu structure under Accounting > BIR Filing
- [ ] Write unit tests for obligation model and deadline adjustment

## Phase 2: eBIRForms Export + Evidence Vault

- [ ] Implement eBIRForms export wizard
- [ ] Create export templates for 1601-C, 0619-E, 1601-EQ, 2550Q
- [ ] Create export templates for 1702-RT/EX, 1702Q
- [ ] Add pre-export validation (required fields check)
- [ ] Track export history (version, user, timestamp)
- [ ] Implement `bir.filing.evidence` model (immutable, create-only)
- [ ] Build evidence upload form (attachments, confirmation number, notes)
- [ ] Add evidence type selection (filing_receipt, efps_confirmation, payment_receipt, etc.)
- [ ] Enforce evidence requirement before status = filed
- [ ] Build evidence search view (filter by form type, period, confirmation number)
- [ ] Write unit tests for export wizard and evidence immutability

## Phase 3: eFPS Integration + Payment Tracking

- [ ] Add eFPS fields to obligation model (transaction_ref, filing_timestamp)
- [ ] Add payment tracking fields (payment_ref, amount, date, bank, status)
- [ ] Implement payment status workflow: pending -> paid -> confirmed
- [ ] Support amended returns (link original filing to amendment)
- [ ] Build payment reconciliation view
- [ ] Create eFPS filing record form
- [ ] Write unit tests for eFPS tracking and amended returns

## Phase 4: Dashboard + Alerts + Audit Trail

- [ ] Build filing status dashboard (kanban view)
- [ ] Add summary cards: upcoming, in-progress, filed, overdue
- [ ] Create penalty exposure widget (25% surcharge + 20% interest estimate)
- [ ] Implement overdue detection cron job (ir.cron)
- [ ] Configure n8n webhook for deadline alerts (5-day, 1-day)
- [ ] Configure Slack notifications for overdue filings
- [ ] Build compliance rate report
- [ ] Build audit trail report (all state changes for a period)
- [ ] Integrate with close orchestration (filing status as gate input)
- [ ] Write unit tests for overdue detection and dashboard accuracy

## Validation Criteria

- [ ] All 9 BIR form types have schedule entries and can generate obligations
- [ ] Deadline adjustment correctly accounts for Philippine holidays
- [ ] Evidence is immutable (no edit/delete after creation)
- [ ] Filing cannot be marked as "filed" without at least one evidence record
- [ ] Separation of duties: preparer cannot approve own filing
- [ ] Overdue detection triggers within 1 hour of deadline
- [ ] Dashboard shows accurate filing status counts
- [ ] Export files are eBIRForms-compatible (validated against schema)
- [ ] 10-year retention policy enforced (no deletion within window)
- [ ] Audit trail captures all state transitions with user and timestamp
