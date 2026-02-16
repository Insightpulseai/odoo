# Bridge: AI Journal Posting

> **Type**: Platform bridge (n8n workflow + Claude API)
> **Replaces**: SAP Smart Journal / Odoo IAP AI features
> **Decision record**: `spec/finance-ppm/decisions/0005-platform-bridges.md`

## Contract

| Field | Value |
|-------|-------|
| **Trigger** | Weekday 6AM PHT cron + Webhook |
| **Input** | Odoo XML-RPC: pending journal entry data |
| **Output** | `account.move` records in DRAFT state (never auto-posted) |
| **Failure mode** | AI validation error logged. No draft created. Manual JE fallback. |

## Safety Guards

- Claude API validates journal entries but **never auto-posts**
- All AI-generated entries created as `account.move` in **DRAFT** state
- Finance Director (CKVC) must manually approve and post
- Full audit trail stored in Supabase

## Required Environment Variables

See `env.example` in this directory.

## Workflow

Source: `scripts/n8n_ai_journal_posting.json`

1. Cron trigger (weekday 6AM) or webhook
2. Query Odoo for pending JE data
3. Send to Claude API for validation (debit/credit balance, account mapping, etc.)
4. If valid: create `account.move` in DRAFT state via Odoo XML-RPC
5. If invalid: log validation errors, notify via Slack
6. Log all actions to Supabase audit trail
