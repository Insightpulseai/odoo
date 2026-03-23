# Implementation Plan: AP Invoice / Supplier Bill Agent (AP-01)

## Overview
This plan outlines the development of the AP Invoice Agent, a second-generation finance agent designed to process supplier bills with full TaxPulse compliance.

## Proposed Changes

### [AP Invoice Spec]
#### [NEW] [implementation_plan.md](file:///Users/tbwa/Documents/GitHub/Insightpulseai/spec/ap-invoice-agent/implementation_plan.md)
#### [NEW] [ssot_bundle.yaml](file:///Users/tbwa/Documents/GitHub/Insightpulseai/spec/ap-invoice-agent/ssot_bundle.yaml)
- Defines the `ipai.ap_invoice.v1` contract.
- Links to TaxPulse VAT/EWT rule mappings.
- Defines fail-closed conditions (e.g., mismatched tax, missing vendor info).

### [AP Invoice Runtime]
#### [NEW] `ipai_ap_invoice` (Odoo Module)
- State machine: `ingested` -> `draft` -> `tax_verified` -> `posted`.
- OCR Bridge: Integration point for invoice extraction.
- TaxPulse Specialist integration.

## Verification Plan

### Automated Tests
- Unit tests for tax-rule selection logic.
- Schema validation for the AP evidence pack.
- Negative-path tests for tax mismatch (fail-closed check).

### Manual Verification
- Staging walkthrough of the first 5 test invoices.
