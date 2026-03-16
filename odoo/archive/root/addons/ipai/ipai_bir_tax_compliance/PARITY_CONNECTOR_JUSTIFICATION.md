# Connector Justification: ipai_bir_tax_compliance

## What this module does
Complete Philippine Bureau of Internal Revenue (BIR) tax compliance module supporting 36 eBIRForms across VAT, withholding tax, income tax, excise tax, percentage tax, capital gains tax, and documentary stamp tax, with automated computation from Odoo transactions, filing deadline calendars, and TIN validation.

## What it is NOT
- Not an OCA parity addon
- Not an EE-module reimplementation

## Why LOC exceeds 1000
The module reaches 1,418 LOC because Philippine tax law requires separate computation logic for each of seven tax categories, each with distinct rate tables, form fields, and filing rules. The `bir_tax_return.py` (442 LOC) and `bir_withholding.py` (425 LOC) alone account for the bulk, driven by BIR-mandated field mappings and multi-form validation rules that cannot be simplified without losing compliance fidelity.

## Planned reduction path
- Extract shared tax computation utilities (rate lookups, period calculations, TIN validation) into a `bir_utils.py` helper module
- Split `bir_tax_return.py` into per-form-type mixins (VAT mixin, income tax mixin, etc.)
- Move filing deadline logic into a standalone `bir_calendar` subpackage
