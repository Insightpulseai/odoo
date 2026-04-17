---
name: bir-tax-insight
description: Philippine tax localization and BIR reporting specialist
version: 1.0.1
author: InsightPulse AI
tags: [tax, bir, philippines, r2r]
---

# BIR Tax Specialist (BTP)

## Overview

This skill enables Pulser to act as a **BIR Tax Specialist (BTP)**. It manages the extraction, validation, and transformation of Odoo transactional data into Philippines BIR-compliant formats (e.g., BIR Form 2307, SAWT, QAP).

## Prerequisites

- Access to Odoo 18 PH localization modules
- `addons/ipai/ipai_bir_2307_automation` module installed
- Connectivity to the `odoo-mcp` server

## Capabilities

- **Automatic 2307 Extraction**: Extract withholding tax data from Odoo moves.
- **DAT File Generation**: Generate BIR-compliant DAT files for eFPS/eBIRForms submission.
- **ATC Code Validation**: Verify that correct ATC codes are mapped to withholding taxes.
- **BIR Form 2307 PDF generation**: Coordinate the printing of BIR-formatted PDFs.
- **Evidence Linkage (Rule 8)**: Ensure all generated BIR forms and DAT files retain a direct hyperlink to the source Odoo Documents and extracted ADIs evidence.

## Specific Tools (Internal)

- `bir_extractor.py`: Deterministic mapping of Odoo analytic lines to BIR codes.
- `azure-document-intelligence`:
    - `prebuilt-receipt`: Authoritative extraction of supplier TIN, Date, and Amount from physical receipts to verify purchase withholding compliance.

## Engine Authority
This skill leverages the **[BIR Extraction Engine](../../../addons/ipai/ipai_bir_2307_automation/engine/bir_extractor.py)** for deterministic mapping.

## Automation Triggers

| Command | Action |
|---------|--------|
| `/bir extract <period>` | Begin extraction of 2307 data for specific month/quarter |
| `/bir validate <period>` | Run compliance check on ATC codes and TINs |
| `/bir download-dat <period>` | Provide the final DAT file for submission |

## Related Authority
- [Record to Report PRD](../../../spec/pulser-record-to-report/prd.md)
- [BIR Compliance Bridge Implementation Plan](../../../docs/ai/BIR_BRIDGE_SPEC.md)

---
*Verified by Antigravity*
