---
paths:
  - "spec/**"
---

# Spec Kit

> Spec kit structure and current bundles inventory.

---

## Structure

All significant features require a spec bundle:

```
spec/<feature-slug>/
|-- constitution.md   # Non-negotiable rules and constraints
|-- prd.md            # Product requirements document
|-- plan.md           # Implementation plan
+-- tasks.md          # Task checklist with status
```

---

## Current Spec Bundles (76 total)

Key bundles:

- `pulser-master-control` - Master control plane
- `close-orchestration` - Month-end close workflows
- `bir-tax-compliance` - BIR tax compliance
- `expense-automation` - Expense automation
- `hire-to-retire` - HR lifecycle management
- `ipai-control-center` - Control center UI
- `odoo-mcp-server` - MCP server integration
- `adk-control-room` - ADK control room
- `auto-claude-framework` - Auto Claude framework
- `ipai-ai-platform` - AI platform core
- `ipai-ai-platform-odoo18` - Odoo 18 AI platform
- `kapa-plus` - Kapa+ documentation AI
- `workos-notion-clone` - WorkOS Notion clone

See `spec/` directory for complete list.

---

*Last updated: 2026-03-16*
