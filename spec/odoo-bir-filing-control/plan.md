# BIR Filing Control - Implementation Plan

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                      Odoo CE 19 + OCA                               │
│                                                                     │
│  ┌──────────────────────┐    ┌──────────────────────┐               │
│  │ ipai_finance_tax_    │    │ ph.holiday           │               │
│  │ return               │    │ (Philippine Calendar)│               │
│  │ (Computed Returns)   │    └──────────┬───────────┘               │
│  └──────────┬───────────┘               │                           │
│             │                           │                           │
│             ▼                           ▼                           │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │              ipai_finance_bir_filing                         │   │
│  │                                                             │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │   │
│  │  │   Filing     │  │  Obligation  │  │   Evidence   │      │   │
│  │  │   Calendar   │  │  Tracker     │  │   Vault      │      │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘      │   │
│  │                                                             │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │   │
│  │  │  eBIRForms   │  │    eFPS      │  │  Dashboard   │      │   │
│  │  │  Export      │  │  Tracking    │  │  & Reports   │      │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘      │   │
│  └──────────────────────────────────────────────────────────────┘   │
│             │                                                       │
│             ▼                                                       │
│  ┌──────────────────────┐                                           │
│  │ ipai_close_           │                                          │
│  │ orchestration         │                                          │
│  │ (Close Cycle Gates)   │                                          │
│  └──────────────────────┘                                           │
└─────────────────────────────────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    n8n Orchestration                                 │
│  - Deadline alerts (5-day, 1-day before)                            │
│  - Overdue notifications → Slack                                    │
│  - Filing status sync to close orchestration                        │
└─────────────────────────────────────────────────────────────────────┘
```

## Module Structure

```
addons/ipai/ipai_finance_bir_filing/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   ├── bir_filing_obligation.py       # Core obligation model
│   ├── bir_filing_calendar.py         # Calendar auto-population
│   ├── bir_filing_evidence.py         # Immutable evidence vault
│   ├── bir_filing_schedule.py         # BIR statutory schedule data
│   └── bir_tax_return_ext.py          # Extend ipai_finance_tax_return
├── views/
│   ├── bir_filing_obligation_views.xml
│   ├── bir_filing_calendar_views.xml
│   ├── bir_filing_evidence_views.xml
│   ├── bir_filing_dashboard_views.xml
│   └── menu.xml
├── security/
│   ├── ir.model.access.csv
│   └── bir_filing_security.xml        # Record rules, groups
├── data/
│   ├── bir_filing_schedule_data.xml   # BIR statutory schedule
│   ├── ir_cron.xml                    # Overdue detection cron
│   └── mail_template.xml             # Notification templates
├── wizard/
│   ├── __init__.py
│   ├── bir_ebirforms_export.py        # eBIRForms export wizard
│   └── bir_filing_calendar_gen.py     # Calendar generation wizard
├── reports/
│   ├── bir_filing_status_report.xml
│   └── bir_filing_evidence_report.xml
└── tests/
    ├── __init__.py
    ├── test_bir_filing_obligation.py
    ├── test_bir_filing_evidence.py
    └── test_bir_ebirforms_export.py
```

## Implementation Phases

### Phase 1: Filing Calendar + Obligation Tracker

**Scope:** Core models and calendar auto-population

**Deliverables:**
- `bir.filing.obligation` model with full status workflow
- `bir.filing.schedule` model with BIR statutory schedule data
- Calendar auto-population wizard (generate obligations for a fiscal year)
- Philippine holiday integration for deadline adjustment
- List and calendar views for obligations
- Security groups: bir_filing_preparer, bir_filing_reviewer, bir_filing_admin
- Basic menu structure under Accounting > BIR Filing

**Dependencies:** `ipai_finance_tax_return`, `account`, `mail`, `calendar`

**Verification:**
- Create obligations for all 9 form types
- Verify deadline adjustment for holidays
- Confirm status workflow enforces transitions
- Security rules prevent unauthorized access

### Phase 2: eBIRForms Export + Evidence Vault

**Scope:** Export functionality and evidence capture

**Deliverables:**
- eBIRForms export wizard (XML/DAT format)
- Pre-export validation (required fields check)
- Export history tracking (version, user, timestamp)
- `bir.filing.evidence` model (immutable)
- Evidence upload form (attachments, confirmation numbers)
- Evidence search and filter views
- Filing status gate: evidence required before status = filed

**Dependencies:** Phase 1 complete

**Verification:**
- Export 1601-C and verify eBIRForms compatibility
- Upload evidence and confirm immutability (no edit/delete)
- Attempt to mark filing as "filed" without evidence (should fail)
- Search evidence by confirmation number

### Phase 3: eFPS Integration + Payment Tracking

**Scope:** Online filing and payment tracking

**Deliverables:**
- eFPS fields on obligation model (transaction ref, filing timestamp)
- Payment tracking fields (ref, amount, date, bank, status)
- Amended return support (link original -> amendment)
- Payment status workflow: pending -> paid -> confirmed
- Payment reconciliation view

**Dependencies:** Phase 2 complete

**Verification:**
- Record eFPS filing with transaction reference
- Track payment against filing
- File amended return linked to original
- Verify payment status transitions

### Phase 4: Dashboard + Alerts + Audit Trail

**Scope:** Monitoring, notifications, and compliance reporting

**Deliverables:**
- Filing status dashboard (kanban + summary cards)
- Penalty exposure widget (estimated penalties for overdue)
- Overdue detection cron job (ir.cron)
- n8n integration: deadline alerts (5-day, 1-day)
- Slack notifications for overdue filings
- Compliance rate report
- Audit trail report (all state changes for a period)
- Integration with close orchestration (filing status as gate input)

**Dependencies:** Phase 3 complete, n8n webhook configured

**Verification:**
- Dashboard loads with accurate counts
- Overdue filing triggers Slack notification
- 5-day advance alert fires correctly
- Close orchestration gate checks filing status
- Audit report shows complete state change history

## Dependencies

| Dependency | Type | Purpose |
|-----------|------|---------|
| `account` | Odoo CE | Accounting periods, journal entries |
| `mail` | Odoo CE | Chatter, notifications, activity tracking |
| `calendar` | Odoo CE | Calendar views |
| `ipai_finance_tax_return` | IPAI | Computed tax returns as input |
| `ph.holiday` | IPAI/Data | Philippine holiday calendar |
| `ipai_close_orchestration` | IPAI (optional) | Close cycle gate integration |

## Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|-----------|
| eBIRForms format changes | Export incompatibility | Version export templates, monitor BIR updates |
| BIR deadline extensions | Calendar inaccuracy | Manual override with audit log |
| Evidence volume growth | Storage pressure | Use Odoo attachments with compression |
| Holiday calendar gaps | Incorrect deadline calculation | Annual review + BIR gazette monitoring |
