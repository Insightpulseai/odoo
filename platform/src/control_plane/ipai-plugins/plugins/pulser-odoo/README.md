# pulser-odoo plugin

AI-augmented product and control layer for Odoo CE/OCA 18 on Azure.

## Install

```bash
claude plugin marketplace add InsightPulseAI/ipai-plugins
claude plugin install pulser-odoo@ipai-plugins
/reload-plugins
```

## Prerequisites

- Azure CLI authenticated: `az login`
- Azure Developer CLI: `azd auth login`
- Node.js 18+ for MCP servers
- Access to `rg-ipai-dev-odoo-runtime` or equivalent stamp resource group

## Skills (22)

| Skill | Invoke | Purpose |
|---|---|---|
| `/pulser-odoo:pulser-constitution` | auto | Enforce IPAI doctrine |
| `/pulser-odoo:pulser-scenario-map` | auto | Map items to E2E lanes |
| `/pulser-odoo:pulser-iac-scaffold` | **manual** | Generate/audit Bicep modules |
| `/pulser-odoo:pulser-stamp-deploy` | **manual** | Stamp promotion and rollback |
| `/pulser-odoo:pulser-runtime-classify` | **manual** | ACA app keep/merge/decommission |
| `/pulser-odoo:pulser-control-plane` | auto | Tenant lifecycle operations |
| `/pulser-odoo:pulser-tenant-admin` | auto | Tenant settings and health |
| `/pulser-odoo:pulser-onboarding` | **manual** | Onboarding stage management |
| `/pulser-odoo:pulser-go-live` | **manual** | Go-live factory and cutover |
| `/pulser-odoo:pulser-uat-gate` | **manual** | UAT execution and signoff |
| `/pulser-odoo:pulser-ppm` | auto | Finance PPM / Project-to-Profit |
| `/pulser-odoo:pulser-expense-intel` | auto | Expense accrual and card exceptions |
| `/pulser-odoo:pulser-finance-rbac` | auto | Role groups and approval bands |
| `/pulser-odoo:pulser-behavior-resolve` | auto | Policy matrix behavior resolver |
| `/pulser-odoo:pulser-prisma` | auto | PrismaLab research tools |
| `/pulser-odoo:pulser-rag-wire` | auto | RAG index routing and Foundry wiring |
| `/pulser-odoo:pulser-livesite` | auto | Health checks and incident response |
| `/pulser-odoo:pulser-run-trace` | auto | Agent run event instrumentation |
| `/pulser-odoo:pulser-self-heal` | auto | Failure taxonomy and recovery policy |
| `/pulser-odoo:pulser-publish` | **manual** | PPTX/DOCX/XLSX publishable outputs |
| `/pulser-odoo:pulser-eval` | **manual** | Domain scorecards and replay evals |
| `/pulser-odoo:pulser-devops-gate` | **manual** | Authority chain and tag audit |
| `/pulser-odoo:pulser-ga-gate` | **manual** | 41-criteria GA readiness assessment |
| `/pulser-odoo:odoo-docs-enhance` | auto | Enhance Odoo 18 docs with IPAI context |

## Agents (4)

| Agent | Purpose |
|---|---|
| `pulser-ap-agent` | AP invoice processing and expense routing |
| `pulser-close-agent` | Month-end/year-end close and close pack generation |
| `pulser-research-agent` | PrismaLab systematic review workflows |
| `pulser-ops-agent` | Platform operations and incident response |

## MCP servers

| Server | Purpose |
|---|---|
| `azure` | 200+ Azure tools via Azure MCP Server |
| `azure-foundry` | Foundry model catalog, deployments, evals |
| `pulser-n8n` | n8n workflow automation at n8n.insightpulseai.com |

## Hooks

| Hook | Trigger | Action |
|---|---|---|
| `PreToolUse` | `az deployment` or ACA traffic set | Confirm before infrastructure mutation |
| `PreToolUse` | Odoo `action_post` or `button_confirm` | Confirm before record posting |
| `PostToolUse` | Any `az containerapp` command | Prompt health check |
| `PreToolUse` | Write to `infra/azure/*.bicep` | Doctrine check |
| `PreToolUse` | `git push main` or `gh pr merge` | Authority chain reminder |

## Architecture doctrine

- Odoo CE/OCA 18 = system of action
- Direct ACA custom-domain binding = canonical ingress (no proxy, no AFD)
- Deployment stamps = scale unit (dedicated PG per stamp)
- `infra/azure/` = IaC truth (Bicep modules)
- `platform/` repo = SSOT (Supabase control plane)
- `agents/` repo = skills, judges, evals, prompt contracts

## License

MIT — see [LICENSE](../../LICENSE)
