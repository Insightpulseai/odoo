# BIR Filing Bridge: Odoo to eBIRForms

This spec defines the "Extraction-Validation-Transformation" (EVT) layer that bridges Odoo 18 PH transactional data to the Bureau of Internal Revenue (BIR) submission channels.

## 1. Architectural Doctrine
- **Odoo as SSoT**: All tax figures must originate from Odoo `account.move` and `l10n_ph` reports.
- **eBIRForms as Target**: The bridge must produce outputs compatible with the offline eBIRForms package.
- **Stateless Bridge**: The bridge is a transformation logic layer, not a persistent database.

## 2. EVT Workflow

### A. Extraction
- **Scope**: VAT (2550Q), Withholding (2307, 1601EQ), and Sales/Purchase Schedules (SLSP).
- **Invariants**: Data must match the **Posted** state in Odoo.
- **Mechanism**: JSON-RPC calls via `odoo_search_read` or specialized compliance MCP tools.

### B. Validation
- **Metadata Checks**: Ensure TIN (12 digits), RDO codes, and Branch codes are present.
- **ATC Mapping**: Validate that every withholding line has a corresponding Alphanumeric Tax Code (ATC).
- **Math Sanity**: Verify that `Base Amount * Rate = Tax Amount` within 1 PHP rounding difference.

### C. Transformation
- **Form 2307**: Export to **Standard XLS** format compatible with Odoo's built-in generator.
- **SLSP / SAWT / QAP**: Generate **DAT files** using the exact BIR fixed-width or comma-separated requirements.
- **2550Q**: Generate a **Review PDF** and a JSON payload for manual entry into eBIRForms.

## 3. Tool Plane (MCP Integration)

| Tool | Action | Phase |
| :--- | :--- | :--- |
| `bir_extract_schedule` | Pulls raw ledger lines for a specific form. | Extraction |
| `bir_validate_master_data` | Checks TIN/ATC compliance for extracted lines. | Validation |
| `bir_generate_dat_file` | Produces the final BIR-ready binary/text file. | Transformation |

## 4. Submission Path
1. **Prepare**: User triggers `bir_prepare_filing` from Pulser.
2. **Review**: Pulser provides a summary of Extraction/Validation results.
3. **Execute**: User approves; Bridge generates the download link for XLS/DAT files.
4. **File**: User imports/uploads files to eBIRForms or eFPS.
