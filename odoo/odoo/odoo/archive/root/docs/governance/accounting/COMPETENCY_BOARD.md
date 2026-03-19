# Accounting Competency Boards

## Month End Close

### Levels

- **L1**: Assisted executor (task-level)
- **L2**: Independent owner (process-level)
- **L3**: Close lead (controls + optimization)

### Competencies

#### MEC-01 — Close calendar & workload planning

Predictable close cadence; fewer late adjustments; clearer client expectations.

**Behaviors**

- **L1**: Follows a close checklist; updates task status daily.
- **L2**: Builds/maintains a close calendar; sequences dependencies across teams.
- **L3**: Leads close with SLAs; runs post-close retros and implements improvements.

**Evidence**

- Close calendar with owners + due dates
- Checklist completion logs
- Post-close retro notes + action items

**Tool enablers**

- Project/Tasks for close checklist
- Approvals for high-risk steps (optional)

#### MEC-02 — Bank & cash reconciliation

Cash accuracy is the backbone of financial statements and tax filings.

**Behaviors**

- **L1**: Matches bank lines to invoices/bills; flags exceptions.
- **L2**: Owns reconciliation rules; resolves unreconciled items; documents rationale.
- **L3**: Optimizes reconciliation throughput; monitors exception rates and root causes.

**Evidence**

- Reconciliation exception log
- Rule set / matching logic notes
- Aging of unreconciled items

**Tool enablers**

- Bank synchronization / statement import
- Reconciliation rules and matching

**Notes**

- Odoo positions reconciliation as a core capability (including smart reconciliation & bank connectivity claims).

#### MEC-03 — Accruals, deferrals, and closing entries

Ensures period accuracy and auditability (revenue/expense matching).

**Behaviors**

- **L1**: Prepares accrual support schedules; posts with supervision.
- **L2**: Independently posts recurring/adjusting entries; maintains support packages.
- **L3**: Designs recurring-entry controls; reviews materiality thresholds.

**Evidence**

- Accrual schedules
- JE support pack (source docs + rationale)
- Materiality policy

**Tool enablers**

- Journal entries
- Recurring entries (if applicable)

#### MEC-04 — AP/AR subledger integrity

Subledger tie-outs reduce surprises and client escalations.

**Behaviors**

- **L1**: Runs AR/AP aging; follows up on discrepancies.
- **L2**: Performs subledger-to-GL tie-out; resolves root causes.
- **L3**: Implements preventative controls (cutoff, duplicate checks, posting rules).

**Evidence**

- Tie-out workpaper
- Aging analysis and adjustments
- Control checklist

**Tool enablers**

- Aged receivables/payables reporting

#### MEC-05 — Period locking & close governance

Prevents back-dated changes and protects finalized periods.

**Behaviors**

- **L1**: Understands lock rules; requests changes via documented approvals.
- **L2**: Enforces locking schedule; manages exceptions.
- **L3**: Designs lock policy aligned to audit/tax deadlines; monitors breaches.

**Evidence**

- Lock schedule
- Exception approvals with justification
- Breach log / audit trail

**Tool enablers**

- Lock/closing-date controls


## Tax Compliance

**Locale overlays applied:** PH

### Levels

- **L1**: Preparer (data gathering + drafts)
- **L2**: Reviewer (accuracy + completeness)
- **L3**: Tax lead (risk + planning + defense)

### Competencies

#### TAX-01 — Tax data readiness (source-of-truth integrity)

Clean source data reduces filing risk and rework.

**Behaviors**

- **L1**: Collects invoices/receipts; validates required fields.
- **L2**: Implements data QA checks; resolves exceptions with stakeholders.
- **L3**: Defines data standards; automates readiness checks and evidence retention.

**Evidence**

- Tax data completeness report
- Exception log + resolutions
- Evidence retention policy

**Tool enablers**

- Invoice/bill data capture
- Document attachments / audit trail (if enabled)

#### TAX-02 — Indirect tax (VAT/GST/Sales tax) preparation

Indirect tax is high-frequency and high-penalty if wrong/late.

**Behaviors**

- **L1**: Prepares draft returns from system reports; flags anomalies.
- **L2**: Reviews return logic; verifies rates, exemptions, and mappings.
- **L3**: Owns filing calendar, risk controls, and dispute handling.

**Evidence**

- Return workpapers
- Rate/mapping configuration notes
- Variance analysis vs prior periods

**Tool enablers**

- Tax reports/returns features

**Notes**

- PH overlay: treat this as VAT operations readiness + reconciliation discipline, not just report generation.
- Evidence should include tax↔GL tie-outs and proof-of-filing retention.

#### TAX-03 — Withholding tax & remittances

Withholding errors create vendor/client disputes and audit exposure.

**Behaviors**

- **L1**: Applies correct withholding on payments under supervision.
- **L2**: Reviews withholding computations; ensures proper documentation.
- **L3**: Designs withholding governance (approvals, exceptions, periodic audits).

**Evidence**

- Withholding schedules
- Remittance proofs
- Exception approvals

**Tool enablers**

- Payment processing workflows
- Withholding tax configuration

**Notes**

- PH overlay: emphasize certificate/schedule traceability tied to payment runs and vendor/customer records.

#### TAX-04 — Statutory reporting & audit defense pack

Faster audits and fewer penalties via clear traceability.

**Behaviors**

- **L1**: Builds evidence pack (invoices, JEs, schedules).
- **L2**: Prepares audit-ready tie-outs and narratives.
- **L3**: Leads audit responses; manages risk registers and remediation plans.

**Evidence**

- Audit defense pack index
- Tie-outs (tax ↔ GL ↔ subledger)
- Risk register + remediation status

**Tool enablers**

- Document management system
- Reporting and analytics

**Notes**

- PH overlay: audit defense should include proof-of-filing archives and structured evidence indexing per filing cycle.

#### TAX-05 — Client advisory: compliance + planning

Moves the firm upmarket (strategy > compliance-only).

**Behaviors**

- **L1**: Explains filing status and basic variances.
- **L2**: Recommends process fixes to prevent recurring issues.
- **L3**: Leads planning and scenario work; quantifies savings and risk tradeoffs.

**Evidence**

- Client memo
- Scenario models
- Decision log

**Tool enablers**

- Reporting and dashboards
- Scenario modeling tools

#### PH-TAX-01 — BIR calendar management (monthly/quarterly/annual)

PH filings are deadline-driven; missed deadlines trigger penalties and client escalations.

**Behaviors**

- **L1**: Maintains a filing calendar; tracks due dates per entity and tax type.
- **L2**: Owns the calendar; proactively gathers inputs and validates readiness ahead of deadlines.
- **L3**: Designs calendar governance with SLAs, escalation paths, and coverage plans.

**Evidence**

- BIR filing calendar (per entity) with owners + due dates
- Readiness checklist per filing cycle
- Escalation log + resolution notes

**Tool enablers**

- Project/Tasks to manage filing workflows
- Document management for proof-of-filing artifacts

#### PH-TAX-02 — VAT operations (PH context)

VAT compliance depends on clean invoice/bill data and correct tax mapping across transactions.

**Behaviors**

- **L1**: Prepares draft VAT workpapers from transaction reports; flags anomalies.
- **L2**: Validates VAT mappings/rates, exemptions, and period cutoffs; reconciles VAT to GL.
- **L3**: Defines VAT controls and variance thresholds; leads issue remediation and audit responses.

**Evidence**

- VAT reconciliation (tax ↔ GL ↔ subledger)
- Variance analysis vs prior periods
- Mapping/rate configuration notes

**Tool enablers**

- Tax reports/returns features
- Invoice/bill validation rules (where available)

**Notes**

- BIR Form 2550Q: Quarterly VAT Return (due 25th after quarter-end)
- Standard VAT rate: 12%
- TaxPulse-PH-Pack: Automated 2550Q generation from account.move

#### PH-TAX-03 — Withholding tax certificates & schedules (PH context)

Withholding compliance requires traceability: certificates, schedules, and consistent mapping to payments.

**Behaviors**

- **L1**: Tracks withholding on payments; maintains basic schedules and supporting docs.
- **L2**: Ensures certificate completeness and ties schedules to GL and payment runs.
- **L3**: Designs withholding governance (approvals, exception handling, periodic internal audits).

**Evidence**

- Withholding schedules tied to payment batches
- Certificate request/issuance tracker
- Exception log with approvals

**Tool enablers**

- Payment/bank workflows
- Attachment indexing (evidence packs)

**Notes**

- BIR Form 1601-C: Monthly Withholding Tax on Compensation (due 10th of following month)
- TRAIN Law 2026 tax brackets: ₱20,833/month exempt threshold
- TaxPulse-PH-Pack: Automated 1601-C from hr.payslip

#### PH-TAX-04 — e-Filing operational discipline (eBIR/eFPS-style workflows)

Operational controls reduce filing failure modes: version drift, missing attachments, wrong entity selection.

**Behaviors**

- **L1**: Follows filing runbook; captures proof-of-filing artifacts per submission.
- **L2**: Maintains a filing runbook; validates entity, period, and submission outputs.
- **L3**: Hardens filing controls; automates artifact capture and audit-defense packaging.

**Evidence**

- Runbook + change log
- Proof-of-filing archive (per entity/period)
- Submission failure log + remediation notes

**Tool enablers**

- Runbooks stored in repo/knowledge base
- Automated evidence capture (where applicable)

**Notes**

- eBIRForms: Offline software for non-eFPS filers (latest: v7.9.5)
- eFPS: Online system for large taxpayers
- Mandatory electronic filing per RR No. 6-2014

#### PH-TAX-05 — Regulatory monitoring & change impact assessment

PH compliance changes can invalidate mappings/workpapers; you need controlled updates and client comms.

**Behaviors**

- **L1**: Tracks known changes; updates checklists when instructed.
- **L2**: Assesses impact on processes/mappings; proposes updates with evidence.
- **L3**: Owns change management; trains team; updates controls and client guidance.

**Evidence**

- Change log (what changed, impact, actions, effective date)
- Updated workpapers/checklists
- Training notes or internal bulletin

**Tool enablers**

- Policy docs + version control
- Tasking/workflows for rollout

**Notes**

- Recent changes: EOPT Act (Jan 22, 2024), RR No. 29-2025 de minimis (Jan 6, 2026)
- Monitor BIR website for Revenue Regulations and Memorandum Circulars

#### PH-TAX-06 — TRAIN Law & EOPT Act compliance (2026 updates)

Tax computation accuracy depends on current rates, brackets, and penalty rules.

**Behaviors**

- **L1**: Applies current TRAIN Law tax brackets and de minimis limits in computations.
- **L2**: Validates taxpayer classification (Micro/Small) for EOPT Act reduced penalties.
- **L3**: Advises clients on tax optimization opportunities from TRAIN/EOPT provisions.

**Evidence**

- Tax computation workpapers with 2026 rates
- Taxpayer classification documentation (gross income basis)
- Client advisory memos on tax optimization

**Tool enablers**

- Tax bracket engine (TRAIN Law 2026)
- Penalty calculator (EOPT Act rates for Micro/Small)
- De minimis benefits tracker (RR No. 29-2025)

**Notes**

- TRAIN Law: Tax-exempt up to ₱250,000/year (₱20,833/month)
- EOPT Act: Micro (<₱3M) 10% surcharge, 6% interest; Small (₱3M-₱20M) same
- De minimis 2026: Rice ₱2,500/mo, Medical ₱2,000/sem, Uniform ₱8,000/yr
