# Repo Purpose Definitions

> Canonical purpose for each top-level directory in the InsightPulseAI monorepo.
> Cross-referenced by: `INSIGHTPULSEAI_TARGET_STATE_ARCHITECTURE.md` §5
> Updated: 2026-03-25

---

## Active Directories

| Directory | Purpose | Plane |
|-----------|---------|-------|
| `addons/ipai/` | Custom Odoo modules (69 modules, `ipai_<domain>_<feature>` naming) | ERP |
| `addons/oca/` | OCA community modules (submodule-pinned, read-only) | ERP |
| `agents/` | Pulser behavior: personas, skills, judges, evals, prompt contracts | AI |
| `agent-platform/` | Agent runtime/orchestration engine (Foundry-backed) | AI |
| `apps/` | Application services (ops-console, mcp-jobs, slack-agent) | Platform |
| `azure-pipelines/` | Azure DevOps pipeline definitions | SDLC |
| `data-intelligence/` | Databricks notebooks, DLT pipelines, Unity Catalog schemas, ML | Data |
| `deploy/` | Deployment configurations and scripts | Infrastructure |
| `design/` | Design tokens, brand assets, Figma exports, component specs | Brand |
| `docker/` | Docker configurations (Odoo, services) | Infrastructure |
| `docs/` | Architecture, governance, evidence, decommission authority | Documentation |
| `foundry/` | Foundry-specific configurations and deployments | AI |
| `infra/` | Azure-native IaC: ACA, Front Door, DNS, Key Vault, networking | Infrastructure |
| `packages/` | Shared packages (agents, taskbus, design-tokens) | Shared |
| `platform/` | Control-plane services: API, bridges, contracts, registry | Platform |
| `prompts/` | Versioned prompt library (Gemini image, etc.) | AI |
| `scripts/` | Automation scripts (1000+ in 86 categories) | Tooling |
| `spec/` | Specification bundles (76 spec bundles) | SDLC |
| `ssot/` | Intended-state truth: agents, architecture, creative, governance | Governance |
| `templates/` | Project/module/spec templates | SDLC |
| `web/` | Browser-facing: landing, SaaS, Pulser widget, ops UI, API facade | Frontend |
| `.github/` | GitHub Actions workflows, issue templates, CI orchestration | SDLC |

## Archive / Legacy (Do Not Expand)

| Directory | Status | Notes |
|-----------|--------|-------|
| `archive/` | Frozen | Historical artifacts |
| `automations/` | Retiring | n8n workflows — migrating to Foundry agents |
| `lakehouse/` | Superseded | Replaced by `data-intelligence/` |
| `n8n/` | Retired | See `RETIRED_SERVICES.md` |
| `ops-platform/` | Superseded | Replaced by `platform/` |
| `supabase/` | Retired | See `RETIRED_SERVICES.md` |
| `web-legacy-backup/` | Frozen | Backup of previous web assets |
| `web-site/` | Superseded | Replaced by `web/` |

## Boundary Rules

1. **Odoo modules only in `addons/`** — never in `platform/`, `web/`, or `agents/`
2. **Pulser UI only in `web/`** — specifically `web/packages/pulser-widget/`
3. **Pulser behavior only in `agents/`** — never in `web/` or `odoo/`
4. **Azure IaC only in `infra/`** — never in `platform/` or `docs/`
5. **Databricks code only in `data-intelligence/`** — never in `platform/` or `infra/`
6. **SSOT YAML only in `ssot/`** — never in `docs/` or `platform/`
7. **Design tokens only in `design/`** — `web/` gets derived copies only
8. **Spec bundles only in `spec/`** — never in `docs/` or `platform/`

---

*This document defines what each directory is for. `REPO_OWNERSHIP_DOCTRINE.md` defines the cross-boundary rules.*
