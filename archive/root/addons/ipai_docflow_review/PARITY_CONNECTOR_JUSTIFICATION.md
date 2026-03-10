# Connector Justification: ipai_docflow_review

## What this module does
Manual review queue for OCR+LLM-extracted expenses and vendor bills, providing document ingestion, configurable routing rules, duplicate detection, bank statement reconciliation, SLA tracking, and snapshot-based audit trails.

## What it is NOT
- Not an OCA parity addon
- Not an EE-module reimplementation

## Why LOC exceeds 1000
The module totals 1,619 LOC because it implements eight distinct subsystems: document lifecycle management (555 LOC core model), rule-based routing engine (233 LOC), bank statement reconciliation (186 LOC), duplicate detection tools (127 LOC), REST ingestion controllers (205 LOC), line-item parsing, snapshot auditing, and SLA enforcement via cron. Each subsystem addresses a different stage of the document review pipeline.

## Planned reduction path
- Extract `dupe_tools.py` and `recon.py` into a shared `ipai_accounting_utils` package
- Split `docflow_document.py` (555 LOC) by extracting state-machine transitions and approval workflow into a mixin
- Move the ingestion controller and routing rule loader script into subpackages
