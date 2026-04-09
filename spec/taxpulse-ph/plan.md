# Implementation Plan — TaxPulse PH for Odoo 18

## 1. Scope

This plan covers the first productizable release path for TaxPulse PH focused on deterministic AP/AR validation, Odoo-native review workflow, and service-layer extraction/orchestration.

## 2. Architecture

### 2.1 Repositories / ownership
- `odoo`: UI surface, workflow states, review objects, blockers, user actions
- `platform/services/invoice-pipeline`: extraction, validation, API layer
- `addons/ipai/ipai_bir_tax_compliance`: PH tax rules engine
- `infra`: deployment substrate and service infrastructure

### 2.2 Processing pipeline
1. attachment uploaded in Odoo
2. Odoo sends attachment metadata and bytes/reference to invoice-pipeline
3. invoice-pipeline extracts structured fields via Azure Document Intelligence
4. PH validator recomputes math and rule outcomes
5. explanation service summarizes findings (Phase 3)
6. Odoo stores result and routes user workflow

## 3. Delivery Phases

### Phase 1 — Core validation MVP
- normalized invoice schema with PH tax fields
- deterministic PH validator (VAT, EWT, withholding, payable checks)
- `POST /v1/invoices/analyze` endpoint
- Odoo review object + blocking flow
- golden fixture suite

### Phase 2 — Odoo workflow hardening
- review queue views, smart buttons, action menus
- override/comment flow
- multi-company config surface, rule configuration model

### Phase 3 — Agentic assistance
- Foundry-based explanation flow
- suggested resolutions, conversation-linked review notes
- evaluation/tracing hooks

### Phase 4 — Reporting/export readiness
- structured compliance exports
- BIR-oriented reporting datasets
- dashboard-ready outputs

## 4. Testing Strategy

- Unit tests for monetary rounding, validator rules, schema parsing
- Golden fixtures: clean VAT, zero-rated, VAT-exempt, withholding mismatch, total due mismatch, OCR confidence degradation
- Odoo integration tests: attachment submission, result persistence, blocker behavior
- E2E: live upload → analysis → review creation → autopost block
