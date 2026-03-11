# PRD — DocFlow v2 (Bank Statements + Reconciliation + SLA)

## 1. Goals

1. Ingest bank statements (PDF/CSV/OFX) into Odoo 19 via DocFlow.
2. Reconcile statements against Odoo transactions (payments, invoices, bank journal entries).
3. Enforce approval SLA with automatic assignment and escalations.

## 2. Users

- Finance Reviewer: reconciles statement lines, approves suggested matches.
- Finance Manager: handles escalations, breaches.
- System Operator: runs daemon and monitors failures.

## 3. Scope

### 3.1 Bank Statement Ingestion

Inputs:

- PDF bank statements (scanned or digital)
- CSV exports
- OFX/QIF (optional v2.1)

Outputs:

- `docflow.document` doc_type="bank_statement"
- `docflow.bank.statement` record with:
  - bank account/journal
  - statement period
  - lines (date, amount, sign, memo, ref, counterparty)
- Snapshot + diff saved per ingestion.

### 3.2 Reconciliation

- Generate match candidates for each statement line:
  - Match against `account.bank.statement.line` candidates OR
  - Direct matching to `account.move` (invoices), `account.payment`, and open receivables/payables.
- Provide scoring breakdown:
  - amount closeness
  - date proximity
  - reference similarity (rapidfuzz)
  - counterparty match (partner fuzzy match)
- Auto-reconcile if confidence >= threshold and no conflicts.
- Otherwise create review tasks.

### 3.3 SLA (Activity-driven)

- Every docflow record in `needs_review` creates `mail.activity` with due date SLA.
- Auto-assign by:
  - company/journal routing rule
  - load balancing across reviewer group
- Escalate on breach:
  - create manager activity
  - set docflow.state="sla_breached"
  - log breach event
- SLA metrics dashboard (v2.2) via list filters and computed fields.

## 4. Non-Functional Requirements

- Odoo 19 compliant
- Idempotent ingestion
- Deterministic scoring
- Auditability: store evidence + match reasons
- Safe concurrency (daemon can run multiple workers)

## 5. Success Metrics

- % statement lines auto-matched
- mean time to reconcile
- breach rate < target
- duplicate reconciliation rate near 0

## 6. Out of Scope

- Bank API integrations
- Third-party statement providers
- End-user consumer banking apps
