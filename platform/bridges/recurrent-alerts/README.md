# Bridge: Recurrent Alerts

> **Type**: Platform bridge (n8n workflow)
> **Replaces**: SAP FCC built-in activity scheduling + EE email digests
> **Decision record**: `spec/finance-ppm/decisions/0005-platform-bridges.md`

## Contract

| Field | Value |
|-------|-------|
| **Trigger** | Cron 9AM/5PM PHT |
| **Input** | Odoo XML-RPC: tasks due today, overdue, handover-pending |
| **Output** | Slack message to `#finance-ppm` channel |
| **Failure mode** | Silent failure — Slack message not sent. Odoo data unaffected. |

## Required Environment Variables

See `env.example` in this directory.

## Workflow

Source: `scripts/n8n_finance_ppm_workflow_odoo19.json`

1. Cron triggers at 9AM and 5PM PHT
2. Query Odoo for tasks where `date_deadline <= today` and `stage != Done/Cancelled`
3. Group by assignee and urgency (due today vs overdue)
4. Format Slack blocks with task links
5. Post to configured Slack channel
6. Log to Supabase audit trail
