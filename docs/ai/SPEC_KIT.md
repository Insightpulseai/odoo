# Spec Kit Structure
> Extracted from root CLAUDE.md. See [CLAUDE.md](../../CLAUDE.md) for authoritative rules.

---

All significant features require a spec bundle:

```
spec/<feature-slug>/
├── constitution.md   # Non-negotiable rules and constraints
├── prd.md            # Product requirements document
├── plan.md           # Implementation plan
└── tasks.md          # Task checklist with status
```

## Current Spec Bundles (62+)

### Core Platform

- `pulser-master-control` - Master control plane
- `ipai-control-center` - Control center UI
- `ipai-ai-platform` - AI platform core
- `ipai-ai-platform-odoo18` - Odoo 18 AI platform
- `ipai-ai-agent-builder` - Agent builder framework
- `auto-claude-framework` - Auto Claude framework
- `adk-control-room` - ADK control room

### Finance & Compliance

- `close-orchestration` - Month-end close workflows
- `bir-tax-compliance` - BIR tax compliance
- `expense-automation` - Expense automation
- `ipai-month-end` - Month-end close
- `ipai-tbwa-finance` - TBWA finance integration
- `notion-finance-ppm-control-room` - Finance PPM control

### Odoo & EE Parity

- `odoo-mcp-server` - MCP server integration
- `odoo-ee-parity-matrix` - EE parity tracking
- `odoo-ce-enterprise-replacement` - CE replacement strategy
- `odoo-19-migration` - Odoo 19 migration plan
- `odoo-ce-devops-master-plan` - DevOps master plan
- `odoo-copilot-process-mining` - Process mining
- `odoo-decoupled-platform` - Decoupled architecture
- `upstream-parity` - Upstream parity tracking
- `parity-agent` - Automated parity agent

### Infrastructure & DevOps

- `azure-reference-architecture` - Azure WAF parity
- `platform-kit` - Platform kit scaffold
- `lakehouse-control-room` - Lakehouse control
- `supabase-platform-kit-observability` - Observability
- `supabase-ssot-doctrine` - SSOT doctrine
- `cicd-supabase-n8n` - CI/CD integration

### Knowledge & Docs

- `kapa-plus` - Kapa+ documentation AI
- `knowledge-graph` - Knowledge graph
- `knowledge-hub` - Knowledge hub
- `insightpulse-docs-ai` - Docs AI

### Other

- `hire-to-retire` - HR lifecycle management
- `workos-notion-clone` - WorkOS Notion clone
- `erp-saas-clone-suite` - ERP SaaS clone
- `auth` - Authentication
- `schema` - Schema management
- `seed-bundle` - Seed data bundles
- See `spec/` directory for complete list
