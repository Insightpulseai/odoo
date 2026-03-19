# Bridge: BIR Form Generation

> **Type**: Platform bridge (n8n workflow)
> **Replaces**: SAP Tax Compliance form generation
> **Decision record**: `spec/finance-ppm/decisions/0005-platform-bridges.md`

## Contract

| Field | Value |
|-------|-------|
| **Trigger** | Weekly cron + Webhook |
| **Input** | Odoo XML-RPC: `bir.tax_return`, `bir.vat.return`, `bir.withholding.return` |
| **Output** | .dat files per eBIRForms specification |
| **Failure mode** | Workflow error logged. Odoo data unaffected. Manual generation fallback. |

## Required Environment Variables

See `env.example` in this directory.

## Workflow

Source: `scripts/n8n_bir_form_generation.json`

1. Weekly cron or webhook trigger
2. Query Odoo for pending tax returns by form type
3. Transform data to eBIRForms .dat format
4. Generate .dat files (1601-C, 0619-E, 2550M, etc.)
5. Attach generated files to Odoo records
6. Log to Supabase audit trail
