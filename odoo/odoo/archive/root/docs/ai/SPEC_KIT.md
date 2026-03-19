# Spec Kit Structure

> Integrated from [github/spec-kit](https://github.com/github/spec-kit).
> See [CLAUDE.md](../../CLAUDE.md) for authoritative rules.

---

## Overview

Spec Kit enables **spec-driven development** — specifications are executable and generate implementations, not just describe them. Every significant feature requires a spec bundle.

## Bundle Structure

```
spec/<feature-slug>/
├── constitution.md   # Non-negotiable rules and constraints
├── prd.md            # Product requirements document (the WHAT)
├── plan.md           # Implementation plan (the HOW)
├── tasks.md          # Task breakdown (the WORK)
├── checklist.md      # Quality validation (optional)
└── research.md       # Unknowns resolved (optional)
```

## Slash Commands

| Command | Purpose | Phase |
|---------|---------|-------|
| `/speckit.constitution` | Create governance principles | 1. Govern |
| `/speckit.specify` | Define product requirements (PRD) | 2. Specify |
| `/speckit.clarify` | Resolve ambiguities | 3. Clarify (optional) |
| `/speckit.plan` | Create implementation plan | 4. Plan |
| `/speckit.tasks` | Generate task breakdown | 5. Tasks |
| `/speckit.analyze` | Cross-artifact consistency check | 6. Analyze |
| `/speckit.checklist` | Generate quality validation | 7. Validate |
| `/speckit.implement` | Execute implementation | 8. Build |

### Workflow

```
/speckit.constitution → /speckit.specify → /speckit.clarify (optional)
    → /speckit.plan → /speckit.tasks → /speckit.analyze
    → /speckit.checklist → /speckit.implement
```

## CLI Tools

| Script | Purpose |
|--------|---------|
| `scripts/speckit-scaffold.sh <slug>` | Create new bundle from templates |
| `scripts/check-spec-kit.sh` | Validate bundle completeness |

### Create a New Bundle

```bash
./scripts/speckit-scaffold.sh my-feature-slug
```

### Validate All Bundles

```bash
./scripts/check-spec-kit.sh
```

## Templates

Templates live in `.specify/templates/`:

| Template | Generates |
|----------|-----------|
| `constitution-template.md` | `spec/<slug>/constitution.md` |
| `spec-template.md` | `spec/<slug>/prd.md` |
| `plan-template.md` | `spec/<slug>/plan.md` |
| `tasks-template.md` | `spec/<slug>/tasks.md` |
| `checklist-template.md` | `spec/<slug>/checklist.md` |

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
- `odoo-enterprise-replacement` - CE replacement strategy
- `odoo-19-migration` - Odoo 19 migration plan
- `odoo-devops-master-plan` - DevOps master plan
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
