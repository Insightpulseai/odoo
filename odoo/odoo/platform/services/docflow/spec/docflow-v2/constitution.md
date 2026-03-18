# Constitution — DocFlow v2 (Odoo 19)

## Purpose

DocFlow v2 automates bank statement ingestion and reconciliation in Odoo 19 using local OCR/parsing plus LLM-assisted classification/extraction, and enforces an activity-driven SLA for manual approvals.

## Non-Negotiables

- Odoo 19 compatible (views use <list>, view_mode="list,form").
- No third-party Document AI APIs (Azure DI, Google DI, etc.).
- LLMs (OpenAI/Gemini/Anthropic) are allowed for reasoning/extraction only.
- All decisions must be explainable and auditable (confidence + evidence stored).
- Idempotent ingestion: deterministic document_id + file_hash.
- Security: ingestion endpoint uses shared token; no public auth.

## System of Record

- Odoo is SSOT for:
  - docflow.document + snapshots
  - reconciliation sessions and match candidates
  - SLA state and breach logs
  - links to created accounting entries

## Data Contracts

- OCR output: plain text + optional structured tables (if locally available).
- LLM output: strict JSON matching schemas.
- All ingestion payloads accepted by /docflow/ingest must be backward compatible.

## Operational Guarantees

- Safe retries: no duplicate creates on reprocessing.
- Deterministic scoring: confidence + dupe risk + match risk.
- Human review is first-class: review UI shows structured fields and computed diffs.
