# ADR-0002: BIR Tax Compliance (Delta)

| Field | Value |
|-------|-------|
| **Capability** | Philippine BIR tax compliance — 36 eBIRForms + notifications |
| **Parity target** | Delta (`ipai_bir_tax_compliance`, `ipai_bir_notifications`) |
| **Date** | 2026-02-16 |
| **Status** | Accepted |

## Context

TBWA\SMP Philippines must file 9 BIR form types (1601-C, 0619-E, 2550M, 2550Q,
1601-EQ, 1702Q, 1702-RT, 1604-CF, 1604-E) on monthly/quarterly/annual cadences.

## CE Attempt

Odoo 19 CE Philippine localization (`l10n_ph`) provides:
- Chart of accounts aligned to Philippine GAAP
- Fiscal positions for withholding tax
- Basic tax configuration

It does NOT provide:
- BIR form-specific models (`bir.tax_return`, `bir.vat.return`, etc.)
- Filing deadline tracking with compliance calendar
- .dat file generation for eBIRForms
- Alphalist/SLSP/QAP attachment generation

## OCA Search

No OCA module covers Philippine BIR eBIRForms filing.
OCA localization modules for Philippines (`l10n_ph_*`) are limited to
chart of accounts and withholding tax tables, not filing workflows.

## Decision

Created two delta modules:
- `ipai_bir_tax_compliance`: 36 eBIRForms support with models for
  tax returns, VAT, withholding, filing deadlines, and TIN validation
- `ipai_bir_notifications`: Email digest and urgent alerts for
  BIR filing deadlines with cooldown logic

## Consequences

- Modules are jurisdiction-specific (Philippines only)
- BIR form specifications change periodically — maintenance required
- .dat file format must track eBIRForms version updates
