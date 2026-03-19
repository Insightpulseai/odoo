# IPAI Odoo Copilot — Tooling Matrix

> Version: 1.0.0
> Last updated: 2026-03-14
> Parent: runtime-contract.md (C-30)

## Tool Categories

### Read Tools (Stage 1 — Current)

| Tool | Odoo Model | Permission | Description |
|------|-----------|------------|-------------|
| search_records | any | user ACL | Search records by domain filter |
| read_record | any | user ACL | Read field values from a record |
| get_report | ir.actions.report | user ACL | Generate and return PDF report |
| search_docs | knowledge.article | public | Search knowledge base articles |

### Draft Tools (Stage 2 — Planned)

| Tool | Odoo Model | Permission | Mode Required | Description |
|------|-----------|------------|---------------|-------------|
| create_draft_invoice | account.move | accountant | draft_only | Create invoice in draft state |
| create_draft_order | sale.order | sales user | draft_only | Create sales order in draft |
| create_task | project.task | project user | draft_only | Create project task |

### Action Tools (Stage 3 — Future)

| Tool | Odoo Model | Permission | Mode Required | Description |
|------|-----------|------------|---------------|-------------|
| confirm_order | sale.order | sales manager | full_access | Confirm a draft sales order |
| post_invoice | account.move | accountant | full_access | Post a draft invoice |
| send_email | mail.mail | user | full_access | Send email via Odoo |

## Tool Execution Policy

1. **Stage 1**: Only read tools are wired. No write operations possible.
2. **Stage 2**: Draft tools require `draft_only` mode and user confirmation.
3. **Stage 3**: Action tools require `full_access` mode, user confirmation, and manager approval.

## Current State

**Stage 1 — Read-only tools only.**

No tools are currently wired in the Foundry agent. Chat completion uses the RAG/knowledge grounding path only. Tool wiring is planned for Stage 2 after evaluation evidence exists.

## Tool Safety Contract

- Every tool call is logged in `ipai.copilot.audit`
- Tool results respect Odoo ACL — the copilot cannot access records the user cannot
- Failed tool calls return structured error, never raise exceptions to the user
- Tool execution timeout: 10 seconds per call
