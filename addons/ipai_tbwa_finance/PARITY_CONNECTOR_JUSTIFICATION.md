# Connector Justification: ipai_tbwa_finance

## What this module does
Unified month-end closing and BIR tax compliance module for TBWA Philippines, combining a template-driven 36-task closing checklist with RACI workflows, holiday-aware scheduling, BIR eBIRForms support, and an integrated compliance dashboard. Replaces SAP AFC and SAP Tax Compliance.

## What it is NOT
- Not an OCA parity addon
- Not an EE-module reimplementation

## Why LOC exceeds 1000
The module totals 1,295 LOC because it unifies two domain-heavy subsystems: month-end closing (closing periods, task templates, finance tasks with RACI state machines) and BIR tax compliance (return generation, compliance checks), plus Philippine holiday calendar logic with workday-aware date arithmetic. Seven model classes are required to represent the full closing+compliance lifecycle.

## Planned reduction path
- Extract BIR return logic into `ipai_bir_tax_compliance` to eliminate duplication between the two modules
- Split holiday calendar (`ph_holiday.py`) into a shared `ipai_ph_calendar` utility module
- Move task template seeding from model methods into XML data files to reduce `finance_task_template.py`
