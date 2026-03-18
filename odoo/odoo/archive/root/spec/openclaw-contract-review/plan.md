# Plan: Contract Review & Clause Extraction (OpenClaw)

## Overview

Extend the existing DocFlow pipeline with a `contract` document type, clause extraction schemas, risk scoring, and Odoo model integration while preserving the human-in-loop review workflow.

## Phase 1 — Data Model & Schema

- Add `contract` document type to `docflow.document` model.
- Define clause extraction JSON schema in `config/docflow/contract_clause_schema.json`.
- Create Odoo models: `docflow.contract.clause` (clause type, text, confidence, risk score).
- Add fields to `docflow.document`: `contract_parties`, `contract_dates`, `contract_value`.

## Phase 2 — Extraction Pipeline

- Implement clause classifier using LLM prompt templates (8 standard clause types).
- Implement entity extractor for parties, dates, and financial values.
- Add confidence scoring per extraction (0.0–1.0 scale).
- Support both Ollama (local) and API-based LLM backends via existing DocFlow LLM client.

## Phase 3 — Risk Scoring & Review

- Implement rule-based risk scoring engine with configurable thresholds.
- Route low-confidence extractions to manual review queue.
- Add two-eye review enforcement for contracts above value threshold.
- Build audit trail: input document -> OCR text -> LLM extraction -> human decision -> Odoo record.

## Phase 4 — Odoo Integration

- Map contract types to Odoo models (vendor -> purchase.order, employment -> hr.contract, etc.).
- Implement duplicate detection against existing Odoo records (partner + date + value matching).
- Create wizard for human-reviewed extraction commit to target Odoo model.

## Phase 5 — Testing & Validation

- Unit tests for clause classification with sample contracts.
- Integration tests for full pipeline (OCR -> extraction -> review -> Odoo record).
- Accuracy benchmarks against labeled test set.

## Dependencies

- Existing DocFlow pipeline (OCR, LLM client, routing, SLA management).
- Ollama instance for local LLM inference.
- Odoo modules: purchase, hr_contract, project, analytic.
