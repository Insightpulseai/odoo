# PRD — Seed Bundle

## Executive Summary

The seed bundle provides machine-readable, version-controlled configuration data for TBWA Philippines financial operations, structured using SAP canonical taxonomy with Odoo CE18 mapping layer.

## Problem Statement

Finance teams need:
- Deterministic task and check definitions
- Consistent naming across documentation and systems
- Country-specific customizations without forking base definitions
- CI-enforceable validation to prevent configuration drift

## Solution

A YAML-based seed bundle with:
- SAP-aligned naming for SOP consistency
- Schema validation for integrity
- Separate Odoo mapping for system translation
- Localization overlays for country-specific patches

## Workstreams

### AFC - Advanced Financial Closing

33 month-end closing tasks across 4 phases:
- Phase I: Initial & Compliance (Payroll, Tax, VAT)
- Phase II: Accruals & Amortization (Revenue, Expenses, Depreciation)
- Phase III: WIP & Reclassification
- Phase IV: Final Adjustments & Close

### STC - SAP Tax Compliance

16 compliance checks across 4 worklist types:
- S4_VAT: VAT compliance
- S4_VND: Vendor master quality
- S4_INV: Invoice compliance
- S4_WHT: Withholding tax

## Success Criteria

1. All seed files pass schema validation in CI
2. YAML-to-payload converter produces valid JSON
3. Odoo import wizard successfully loads seeds
4. No manual data entry required for standard setup

## Non-Goals

- Real-time sync (handled by n8n workflows)
- UI for seed editing (use YAML files)
- Multi-tenant support (single company focus)
