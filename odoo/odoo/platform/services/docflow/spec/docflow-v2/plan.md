# Plan — DocFlow v2

## Phase A: Data Model + UI

- Add doc_type="bank_statement"
- Create models:
  - docflow.bank.statement (header)
  - docflow.bank.statement.line (lines)
  - docflow.recon.session (session)
  - docflow.recon.candidate (candidates per line)
  - docflow.sla.event (breach logs)
- Odoo views:
  - statement form with embedded lines
  - reconciliation workspace (per session)
  - smart buttons from docflow.document to statement + session

## Phase B: Intelligence + Matching

- Local parsing:
  - CSV: deterministic parser
  - PDF: OCR + LLM extraction
- Candidate generation:
  - amount/date/ref similarity using rapidfuzz
  - partner fuzzy match
- Auto-reconcile path + manual review path

## Phase C: SLA Automation

- On state transitions:
  - create/refresh activities
- Scheduled job:
  - detect overdue items
  - escalate + set sla_breached
- Routing rules for assignments

## Phase D: Daemon Integration

- Extend runner.py:
  - new pipeline for bank statements
  - call /docflow/ingest with doc_type=bank_statement and extracted statement JSON
- Optional: push recon candidates periodically.
