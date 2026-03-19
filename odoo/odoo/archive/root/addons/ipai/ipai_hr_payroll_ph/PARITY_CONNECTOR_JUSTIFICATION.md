# Connector Justification: ipai_hr_payroll_ph

## What this module does
Philippine payroll module providing Enterprise Edition payroll parity for CE deployments, with 2025 SSS, PhilHealth, and Pag-IBIG contribution table computation, BIR TRAIN Law withholding tax calculation, payslip generation, and integration with `ipai_bir_tax_compliance` for forms 1601-C and 2316.

## What it is NOT
- Not an OCA parity addon
- Not an EE-module reimplementation

## Why LOC exceeds 1000
The module reaches 1,046 LOC because Philippine statutory payroll requires five distinct model classes: payslip computation (421 LOC) with multi-step salary rule evaluation, contribution table lookups (226 LOC) encoding SSS/PhilHealth/Pag-IBIG bracket tables from government circulars, employee extensions (119 LOC) for PH-specific fields (TIN, SSS number, PhilHealth ID), contract extensions (133 LOC) for de minimis and compensation structures, and salary rule definitions (70 LOC). Each government agency mandates its own rate table and computation formula.

## Planned reduction path
- Extract contribution tables (`ph_contribution_table.py`) into XML data records instead of Python-encoded bracket lookups
- Move shared Philippine employee fields (TIN, SSS, PhilHealth, Pag-IBIG IDs) into a common `ipai_ph_hr` mixin used by both this module and `ipai_bir_tax_compliance`
- Split payslip computation into per-agency mixins (SSS mixin, PhilHealth mixin, Pag-IBIG mixin, BIR WHT mixin)
