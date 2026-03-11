# Constitution — DocFlow Agentic Finance

## Purpose

Automate expense and vendor invoice ingestion into Odoo using local OCR and LLM reasoning, while preserving auditability and finance controls.

## Non-Negotiable Constraints

1. No third-party Document AI / OCR SaaS APIs
2. OCR must be self-hosted and deterministic
3. LLMs (OpenAI/Anthropic/Gemini) are allowed **only** for reasoning on OCR text
4. Odoo is the single system of record
5. All writes to Odoo must be idempotent
6. Draft-only writes unless explicitly approved by policy
7. Persist full audit trail: input doc → OCR text → LLM outputs → Odoo record link

## Security

- Do not send images to LLMs (default policy).
- Send only OCR text and structured metadata.

## Failure Handling

- Fail closed (manual review path).
- Never auto-post on uncertainty.
