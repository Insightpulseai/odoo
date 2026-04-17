# Plan — DocFlow Agentic Finance

## Phase 1 — Foundation

- File watcher
- OCR pipeline
- Invoice/expense classification
- Draft creation (expense/vendor bill)
- Artifact persistence + idempotency

## Phase 2 — Intelligence

- Vendor fuzzy match + auto-create partner
- Line items improvements
- Duplicate detection (vendor+number+total)

## Phase 3 — Automation

- Confidence thresholds
- Auto-submit expenses
- Reporting

## Architecture

Viber Desktop → File Watcher → OCR → LLM Agent → Validation → Odoo Draft

## Risks

- OCR noise
- Layout variance
- LLM hallucination

## Mitigations

- Rule checks
- Schema enforcement
- Numeric reconciliation
