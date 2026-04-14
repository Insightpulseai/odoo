# Pulser Account Reconciliation Agent — Operator Guide

The Pulser Account Reconciliation Agent automates bank statement reconciliation and
intercompany WHT clearing inside Odoo. It uses a four-specialist HandoffWorkflow
(BankMatcher → BankClearer / ExceptionHandler, IntercompanyClearer) backed by
FileCheckpointStorage so runs resume safely when new bank data arrives mid-period.

## When to Invoke

- Monthly: after bank statements are downloaded and before the period is locked
- Ad-hoc: when an intercompany WHT transaction (e.g. Form 2307) needs clearing
- Daily incremental: re-invoke with same `company_id` + `period`; checkpoint resumes

## What Approvals to Expect

Every write to Odoo requires explicit approval — there are no silent mutations:

1. **Bank reconciliation** — agent presents: bank line date, amount, partner, matched
   move line, confidence score, and delta. You approve or reject before it posts.
2. **Writeoff** — if a delta exists, agent proposes a writeoff account and amount.
   A second approval is required before the writeoff is posted.
3. **Intercompany clearing** — agent confirms Form 2307 receipt, then presents the
   full clearing detail (source company, target company, invoice ID, WHT amount)
   before requesting approval. Affects two companies simultaneously.

Unmatched items older than 30 days are never auto-cleared — they are escalated to
Finance Director for manual decision.

## Checkpoint and Log Location

Checkpoints write to `$PULSER_CHECKPOINT_PATH` (default: `/var/lib/pulser/checkpoints`).
Each workflow run uses the key `reconcile_{company_id}_{period}`.

## Quick Reference

```
Invoke  : build_reconcile_workflow("dataverse_pasig", "2026-04")
Test    : pytest agents/tests/test_payment_reconcile_workflow.py -m unit -v
Source  : agents/workflows/payment_reconcile_workflow.py
SKILL   : agents/skills/recon_agent/SKILL.md
Epic    : ADO #524
```
