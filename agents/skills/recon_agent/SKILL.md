---
name: pulser-recon-agent
version: 0.1.0
runtime: microsoft-agent-framework
epic_id: "524"
benchmark: D365 Account Reconciliation Agent
status: v0
plane: B (Copilot Finance agent)
author: InsightPulse AI
tags: [finance, reconciliation, bank, intercompany, hitl]
---

# Pulser Account Reconciliation Agent — SKILL

## Purpose

Automates bank statement reconciliation and intercompany WHT clearing for Odoo companies.
Benchmarks against the D365 Account Reconciliation Agent (Plane B: Copilot Finance).
All mutating actions require explicit human approval before execution.

## Tools

| Tool | Type | Description |
|------|------|-------------|
| `get_bank_statement_lines` | read-only | Fetch unreconciled bank statement lines for a period |
| `get_open_ar_lines` | read-only | Fetch open AR lines (outstanding customer invoices) |
| `get_open_ap_lines` | read-only | Fetch open AP lines (outstanding vendor bills) |
| `get_intercompany_transactions` | read-only | Get intercompany transactions between two Odoo companies |
| `match_bank_line_to_move` | read-only | Propose a match between a bank line and a move line (no post) |
| `reconcile_bank_line` | **mutating** | Mark a bank line reconciled against an account.move.line |
| `clear_intercompany_transaction` | **mutating** | Clear an intercompany WHT transaction (affects two companies) |

## Mutating Tool Guardrails

Both mutating tools are decorated with `@tool(approval_mode="always_require")`.

- `reconcile_bank_line` — requires approval before any reconciliation post.
  If `writeoff_amount > 0`, a second approval is required for the writeoff account.
- `clear_intercompany_transaction` — requires approval before intercompany clearing.
  Primary scenario: Dataverse (Pasig) ↔ TBWA\SMP WHT clearing (Form 2307).

No mutating action runs silently. The agent will always surface amounts, dates,
Odoo record IDs, and a confidence score before requesting approval.

## Inputs

| Parameter | Type | Description |
|-----------|------|-------------|
| `company_id` | str | Odoo company xmlid (e.g. `dataverse_pasig`) |
| `period` | str | ISO period string `YYYY-MM` (e.g. `2026-04`) |

## Outputs

- Matched bank line list with reconciliation status per line
- Unmatched / low-confidence exceptions list (escalated to Finance Director if > 30 days)
- Intercompany clearing summary (Dataverse ↔ TBWA\SMP WHT)
- Checkpoint file per workflow run (FileCheckpointStorage, resumable)

## HITL Contract

All write operations require human-in-the-loop approval:

1. Agent presents match proposal: amounts, dates, Odoo IDs, confidence score
2. Human approves or rejects
3. On approval: agent calls mutating tool and confirms result
4. On rejection: agent routes to ExceptionHandler for human decision

Unmatched items older than 30 days are always escalated — never auto-cleared.

## Failure Modes

| Condition | Behavior |
|-----------|----------|
| Low-confidence match (< 95%) | Routed to ExceptionHandler, surfaced for human decision |
| Unmatched line > 30 days | Escalated to Finance Director |
| Approval denied | Item added to exceptions report; no state change |
| Missing bank statement | BankMatcher halts; requests manual import |
| Missing Form 2307 | IntercompanyClearer blocks clearing until confirmed received |

## How to Invoke

```python
from agents.workflows.payment_reconcile_workflow import build_reconcile_workflow

workflow = build_reconcile_workflow("dataverse_pasig", "2026-04")
# Resumes from checkpoint when new bank data arrives
```

Workflow is durable via `FileCheckpointStorage` — safe to call again when new
bank data arrives; it resumes from the last checkpoint.

## Test Command

```bash
pytest agents/tests/test_payment_reconcile_workflow.py -m unit -v
```

## Anchors

- Implementation: `agents/workflows/payment_reconcile_workflow.py`
- Tests: `agents/tests/test_payment_reconcile_workflow.py`
- ADO Epic: [#524 Finance Agents Parity](https://dev.azure.com/insightpulseai/ipai-platform/_workitems/edit/524)
- Reference adaptation: `docs/architecture/reference-adaptations/finance-recon-agent-v0.md`
- D365 benchmark: Account Reconciliation Agent (preview, Wave 1)
- Doctrine: `CLAUDE.md` §"Pulser — canonical classification", Plane B
