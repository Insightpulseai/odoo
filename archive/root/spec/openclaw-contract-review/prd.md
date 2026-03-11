# PRD: Contract Review & Clause Extraction (OpenClaw)

> **Version**: 1.0.0
> **Date**: 2026-03-07
> **Bundle**: `spec/openclaw-contract-review/`

---

## Problem Statement

Organizations process contracts manually — vendor agreements, NDAs, service contracts — with no structured extraction of key clauses, dates, parties, or financial terms. This creates risk through missed obligations, renewal deadlines, and inconsistent review quality.

## Goal

Extend the DocFlow agentic document processing pipeline to support contract analysis: extracting clauses, identifying parties, scoring risk, and linking results to Odoo purchase, HR, and project modules.

## Functional Requirements

1. **Document Intake**: Accept PDF/image contracts via DocFlow upload; OCR as needed.
2. **Clause Extraction**: Identify and classify clauses into 8 standard types (termination, liability, confidentiality, payment, indemnification, IP, governing law, force majeure).
3. **Entity Extraction**: Extract parties (names, roles), dates (effective, expiry, renewal), and financial values (total value, payment terms).
4. **Risk Scoring**: Assign per-clause risk score (0.0–1.0) based on configurable rules.
5. **Review Queue**: Route extractions to `ipai_docflow_review` for human validation before committing to Odoo.
6. **Odoo Integration**: Create or link to `purchase.order`, `hr.contract`, `project.project`, or `account.analytic.line` based on contract type.
7. **Duplicate Detection**: Check extracted contract against existing Odoo records to prevent duplicates.

## Non-Functional Requirements

- Processing time: < 3 minutes per contract (OCR through review queue).
- Accuracy targets: parties >= 90%, dates >= 85%, values >= 80%, clause classification >= 75%.
- Local-only LLM (Ollama) must be a first-class option; no mandatory external API calls.
- PII redaction available as a pre-processing step.

## Non-Goals

- Full contract lifecycle management (CLM).
- Contract generation or drafting.
- External legal database or compliance API integration (phase 1).
- Replacing legal review — this augments human review.

## Success Metrics

| Metric | Target |
|--------|--------|
| Party extraction accuracy | >= 90% |
| Date extraction accuracy | >= 85% |
| Value extraction accuracy | >= 80% |
| Clause classification accuracy | >= 75% |
| Manual correction rate | <= 30% (target <= 15% within 3 months) |
| End-to-end processing time | < 3 minutes |
