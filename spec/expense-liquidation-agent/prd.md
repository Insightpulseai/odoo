# Expense Liquidation Agent - PRD

## 1. Product Summary
> Expense Liquidation Agent: a policy-governed, multi-channel submission and liquidation capability for cash advances, reimbursements, and supporting receipts, with Telegram as the first mobile edge, n8n as the orchestration bridge, Odoo as the system of record, and Foundry Document Intelligence as extraction/audit support.

## 2. User Stories
- **Employee Submits via Telegram**: As an employee, I want to submit my advance liquidation by sending a photo/PDF of my receipt to a Telegram bot so that I can comply with financial obligations instantly without manual data entry.
- **n8n Normalization**: As a system administrator, I want n8n to normalize inbound payloads into a canonical submission envelope so that Odoo receives clean, structured data regardless of the source.
- **Idempotent Case Creation**: As a finance manager, I want Odoo to create/update liquidation cases idempotently to prevent duplicate entries from multiple submission attempts.
- **Foundry Extraction**: As a finance auditor, I want Foundry to extract merchant name, date, amount, category, and receipt-confidence automatically to speed up the verification process.
- **Policy Engine Audit**: As a controller, I want the policy engine to flag missing receipts, over-limit spend, late liquidations (>30 days), and client-chargeability gaps so that I can focus only on exceptions.
- **Finance Settlement**: As an accountant, I want to post settlement outcomes (Employee owes company, Company owes employee, or Net zero) with one click once the agent confirms compliance.

## 3. Functional Requirements
- **`source_channel` & `source_message_id`**: Capture the origin of the submission for auditability.
- **`submission_envelope_id`**: Maintain a canonical ID for cross-system tracking.
- **Attachment Ingestion Metadata**: Store original file metadata and ingestion timestamps.
- **Extraction Result + Confidence**: Persist Foundry OCR data alongside confidence scores.
- **Policy Findings + Waiver Path**: Explicitly log policy passes/fails and provide a workflow for authorized waivers.
- **Computed Settlement Outcome**: Automatically calculate balance due vs. advance amount.
- **SLA Timers**: Monitor the 30-day liquidation window and alert on overdue obligations.
- **Immutable Audit Trail**: Log every transition from submission -> extraction -> audit -> approval -> posting.

## 4. Business Rules
- **Liquidation SLA**: All cash advances must be accounted for within a 30-day liquidation window from the date of release.
- **Payroll Deduction**: Overdue balances are eligible for payroll deduction only when both policy conditions and manager approval for deduction are satisfied.
- **Evidence Requirement**: No finance posting is permitted without evidence completeness (Receipt attached + OCR match) or an explicitly approved waiver.
- **Client Chargeability**: Expenses marked as client-related must include valid client references (Project/Task) to pass the audit.

## 5. Workflow (8-State Primary Lifecycle)
The 8-state primary lifecycle remains the contract of truth. We add **orthogonal dimensions** to support agentic operations without overloading the state machine:
- **`channel_state`**: `received` / `normalized` / `failed`
- **`document_state`**: `pending` / `extracted` / `review_needed` / `accepted`
- **`policy_state`**: `pending` / `pass` / `fail` / `waived`
- **`settlement_state`**: `net_zero` / `employee_owes_company` / `company_owes_employee`

## 6. Non-Functional Requirements
- **Idempotency**: All inbound processing must use correlation IDs to prevent duplicate writes.
- **Retry-Safety**: Webhook handling must be safe for retries in case of transient Odoo/Foundry downtime.
- **Environment Isolation**: Strategy for isolating test/prod Telegram bots to avoid webhook delivery collision.
- **Observability**: Real-time logging of each stage (n8n, Odoo, Foundry) for rapid troubleshooting.
- **Replayability**: Ability to re-process an Odoo record from the raw inbound payload.
