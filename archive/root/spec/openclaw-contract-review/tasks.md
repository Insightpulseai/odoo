# Tasks: Contract Review & Clause Extraction (OpenClaw)

## Task 1: Add contract document type to DocFlow
- Extend `docflow.document` model with `contract` type selection.
- Add contract-specific fields: parties, dates, value, clause_ids.
- Create `docflow.contract.clause` model (type, text, confidence, risk_score).
- Status: TODO

## Task 2: Define clause extraction schema
- Create `config/docflow/contract_clause_schema.json` with 8 clause types.
- Define JSON Schema for extraction output (parties, dates, values, clauses).
- Version the schema for future extensibility.
- Status: TODO

## Task 3: Implement clause classifier
- Build LLM prompt templates for clause identification and classification.
- Support 8 standard types: termination, liability, confidentiality, payment, indemnification, IP, governing law, force majeure.
- Add confidence scoring per clause (0.0–1.0).
- Status: TODO

## Task 4: Implement entity extractor
- Extract party names and roles from contract text.
- Extract dates: effective, expiry, renewal.
- Extract financial values: total value, payment terms, currency.
- Validate extracted entities against Odoo master data (res.partner, calendar).
- Status: TODO

## Task 5: Implement risk scoring engine
- Define configurable risk rules per clause type.
- Compute per-clause and overall contract risk scores.
- Flag high-risk clauses for priority review.
- Status: TODO

## Task 6: Integrate with DocFlow review queue
- Route contract extractions to `ipai_docflow_review` queue.
- Enforce two-eye review for contracts above configurable value threshold.
- Build complete audit trail from intake to Odoo record creation.
- Status: TODO

## Task 7: Implement Odoo model integration
- Create mapping: contract type -> target Odoo model.
- Build wizard for committing reviewed extractions to purchase.order, hr.contract, etc.
- Implement duplicate detection (partner + date + value matching).
- Status: TODO

## Task 8: Testing and accuracy benchmarks
- Create test fixtures with sample contracts (PDF/text).
- Write unit tests for clause classification and entity extraction.
- Run accuracy benchmarks and compare against PRD targets.
- Status: TODO
