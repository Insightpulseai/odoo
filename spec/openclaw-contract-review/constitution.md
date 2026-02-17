# Constitution — Contract Review & Clause Extraction

> Spec bundle: `spec/openclaw-contract-review/`
> Status: Skeleton (awaiting PRD)
> Origin: OpenClaw use-case research → P0 opportunity

---

## Purpose

Extend DocFlow's agentic document processing pipeline to support **contract analysis** — extracting clauses, identifying parties, scoring risk, and integrating with Odoo's purchase, HR, and project modules.

---

## Non-Negotiable Constraints

### Data Privacy
- All contract processing MUST support local-only LLM (Ollama) as a first-class option
- Contract text MUST NOT be logged to external services without explicit opt-in
- Extracted data stored in Odoo only; no Supabase for contract content
- PII redaction MUST be available as a pre-processing step

### Human-in-Loop
- No contract action (PO creation, HR contract link, obligation tracking) may auto-commit
- All extractions route through `ipai_docflow_review` review queue
- Minimum two-eye review for contracts above configurable value threshold
- Audit trail: input document → OCR text → LLM extraction → human decision → Odoo record

### Accuracy
- Clause extraction confidence MUST be reported per-clause (0.0–1.0)
- Clauses below confidence threshold route to manual review, not auto-accept
- Entity extraction (parties, dates, values) validated against Odoo master data (partners, calendar)
- Duplicate detection against existing Odoo contracts/POs

### Architecture
- Extend existing DocFlow pipeline; do NOT create a parallel system
- New document type `contract` in `docflow.document` model
- Reuse existing: OCR layer, LLM client, routing rules, SLA management
- New: clause schema, risk scoring, Odoo model integration

### Security
- Contract documents classified as `confidential` by default
- Access control via Odoo record rules (multi-company aware)
- No contract content in n8n workflow payloads (metadata only)
- LLM prompts MUST NOT include contract content from other contracts (no cross-contamination)

### Integration Boundaries
- Supported Odoo models: `purchase.order`, `hr.contract`, `project.project`, `account.analytic.line`
- Extraction schemas versioned and stored in `config/docflow/`
- API contract for any external consumer documented in `docs/arch/`

---

## Anti-Goals
- NOT building a full contract lifecycle management (CLM) system
- NOT replacing legal review — augmenting it
- NOT supporting contract generation / drafting (extraction only)
- NOT integrating with external legal databases or compliance APIs (phase 1)

---

## Success Criteria
- ≥ 90% accuracy for party extraction (names, roles)
- ≥ 85% accuracy for date extraction (effective, expiry, renewal)
- ≥ 80% accuracy for value extraction (total value, payment terms)
- ≥ 75% accuracy for clause classification (8 standard clause types)
- < 3 minutes per contract end-to-end (OCR → extraction → review queue)
- ≤ 30% manual correction rate (target: reduce to ≤15% within 3 months)

---

## Open Questions (for PRD phase)
- Which contract types are highest volume? (vendor agreements, NDAs, service contracts, leases?)
- What clause taxonomy to use? (start with 8 standard types or custom?)
- Should risk scoring be rule-based or LLM-based?
- Integration with Odoo Sign module — relevant or out of scope?
- Multi-language support needed for phase 1?
