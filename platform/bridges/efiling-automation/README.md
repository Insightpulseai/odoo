# Bridge: e-Filing Automation

> **Type**: Platform bridge (n8n workflow)
> **Replaces**: SAP Tax Filing Integration (eFPS/eBIRForms/eAFS)
> **Decision record**: `spec/finance-ppm/decisions/0005-platform-bridges.md`

## Contract

| Field | Value |
|-------|-------|
| **Trigger** | Webhook (manual initiation) |
| **Input** | Generated .dat files + Odoo tax return records |
| **Output** | Filing confirmation from eFPS/eBIRForms/eAFS portals |
| **Failure mode** | Portal submission error logged. Manual filing fallback required. |

## Required Environment Variables

See `env.example` in this directory.

## Workflow

Source: `scripts/n8n_bir_efiling_automation.json`

1. Webhook trigger with form type and period
2. Retrieve generated .dat files from Odoo attachments
3. Package submission for target portal (eFPS, eBIRForms, or eAFS)
4. Submit to government portal
5. Capture confirmation number
6. Update Odoo record with filing status
7. Log to Supabase audit trail
