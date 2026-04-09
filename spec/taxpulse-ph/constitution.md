# Constitution — TaxPulse PH for Odoo 18

## 1. Purpose

TaxPulse PH exists to deliver a Philippines-first tax and compliance layer for Odoo 18 that combines deterministic tax logic, attachment intelligence, and agent-assisted review without delegating financial correctness to non-deterministic AI behavior.

## 2. Product Doctrine

### 2.1 Deterministic before generative
All tax math, payable validation, posting controls, and compliance state transitions must be computed in code and reproducible from fixtures.

### 2.2 Odoo-native operating model
The product must fit Odoo 18 workflows for quotations, invoices, vendor bills, payments, tax reports, and review queues. Users should not need spreadsheets or separate portals for routine compliance work.

### 2.3 Philippines-first scope
The initial product scope is Philippine VAT, withholding-aware AP/AR flows, invoice validation, and BIR-oriented reporting/export readiness. Global tax breadth is not a v1 goal.

### 2.4 Explain every decision
Every approval, rejection, or review flag must include machine-readable findings and human-readable explanations traceable to source fields and rules.

### 2.5 Block bad posting
If extraction confidence is low or deterministic validation fails, the system must block autoposting and mark the document for review.

### 2.6 Bridge-heavy architecture
Odoo remains the transactional system and user surface. Heavy OCR, extraction, agent orchestration, and retrieval/grounding stay in external services and are consumed through thin Odoo bridges.

## 3. Mandatory Architecture Guardrails

### 3.1 In Odoo
Odoo owns:
- transaction models and workflow states
- review queues and user actions
- audit visibility
- tax review records linked to source documents
- posting blockers and override controls

### 3.2 Outside Odoo
External services own:
- attachment ingestion
- OCR and structured extraction
- deterministic validation engine
- agentic explanation and resolution support
- structured compliance payload generation

### 3.3 AI role boundary
AI may:
- classify documents
- extract candidate fields
- explain findings
- propose actions
- draft reviewer notes

AI may not:
- determine whether tax math is correct
- override deterministic compliance rules
- auto-approve posting without rule-engine confirmation

## 4. Data and Compliance Principles

### 4.1 Source preservation
Original attachments and raw extraction outputs must be retained or referenceable for audit and reprocessing.

### 4.2 Normalized schema first
All extracted invoices and tax-relevant documents must be normalized into strict schemas before validation.

### 4.3 Currency and monetary precision
All monetary calculations must use decimal-safe logic with explicit rounding policy.

### 4.4 Multi-entity design
The system must support multiple companies, branches, and tax profiles without hard-coded single-entity assumptions.

## 5. Product Boundaries

### In scope
- Philippine tax computation for targeted Odoo documents
- AP/AR invoice validation
- withholding-aware payable checking
- Odoo-native review workflow
- attachment ingestion for PDF/image/office files
- BIR-oriented reporting/export readiness

### Out of scope for v1
- full global tax engine coverage
- all-country tax content maintenance
- full legal filing automation for every BIR process
- replacement of Odoo accounting core
- replacing human approval for flagged exceptions

## 6. Implementation Principles

### 6.1 OCA-first and thin customizations
Where Odoo capability is needed in-ERP, prefer Odoo/OCA-native patterns before custom code.

### 6.2 Thin IPAI modules only
Custom `ipai_*` modules must remain thin bridges or workflow surfaces, not large parity forks.

### 6.3 API-first external services
Tax computation, invoice validation, extraction, and explanation services must be callable through documented APIs.

### 6.4 Fixture-first development
Every major rule path must have golden fixtures and deterministic tests before automation is trusted.

## 7. Release Gates

A release cannot be considered production-ready unless:
- golden fixtures pass deterministically
- extraction confidence handling is implemented
- validation failures block autoposting
- audit trail fields are populated
- rule findings are explainable in UI/API outputs
- multi-company configuration paths are tested

## 8. Success Criteria

The product is successful when it:
- prevents tax/arithmetic misposting before accounting impact
- reduces manual review time for AP/AR tax checks
- keeps finance users inside Odoo-native workflows
- produces compliance-ready structured outputs
- makes exception handling faster and more auditable than spreadsheet/email processes
