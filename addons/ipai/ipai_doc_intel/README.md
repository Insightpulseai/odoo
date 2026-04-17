# IPAI Document Intelligence

Azure Document Intelligence bridge for Odoo CE 18. Replaces Odoo IAP document digitization.

## What it does

- Upload PDF/image on vendor bill → click "Extract with DocAI" → fields auto-populated
- Extracts: vendor name, TIN, invoice #, date, amounts, line items, tax
- Auto-classifies VAT 12% and EWT (2% contractor / 10% professional)
- Confidence-based routing: auto-create (>90%) or review queue (<90%)

## Azure resource

- **Service:** `docai-ipai-dev` (FormRecognizer, Southeast Asia)
- **Model:** `prebuilt-invoice` (GA, 26+ fields)
- **Auth:** API key from Key Vault (MI-preferred via ACA env var)

## Supported document types

| Type | DocAI Model | Status |
|------|-------------|--------|
| Vendor invoices | prebuilt-invoice | ✅ Working |
| Receipts | prebuilt-receipt | Available |
| TBWA Cash Advance form | Custom model (train) | Planned |
| TBWA Expense Report | Custom model (train) | Planned |

## Configuration

Set in Odoo System Parameters:
- `ipai_doc_intel.endpoint` — DocAI endpoint (default: SEA)
- `ipai_doc_intel.api_key` — API key from Key Vault

## Why not Odoo IAP?

- IAP costs per scan (Odoo cloud pricing)
- IAP can't handle custom forms (TBWA CA form, Expense Report)
- DocAI is already deployed on our Azure sub, MI-auth capable
- Custom model training for client-specific forms is a product moat
