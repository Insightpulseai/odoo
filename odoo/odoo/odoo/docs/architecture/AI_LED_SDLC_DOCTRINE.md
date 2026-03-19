# AI-Led SDLC Doctrine

> Benchmark: [Microsoft Tech Community — AI-led SDLC](https://techcommunity.microsoft.com/blog/appsonazureblog/an-ai-led-sdlc-building-an-end-to-end-agentic-software-development-lifecycle-wit/4491896)

## Canonical lifecycle

```
1. Problem statement
2. Spec-driven decomposition
3. Maker-agent implementation
4. Judge-agent validation
5. CI/CD deploy + evidence capture
6. SRE-agent monitoring + issue creation
```

Specs are first-class, versioned artifacts. Code changes without spec linkage are incomplete.

## Repo mapping

| Lifecycle step | Repo / surface | Output |
|---|---|---|
| Problem statement | `spec/<slug>/constitution.md` | Non-negotiable constraints |
| Spec decomposition | `spec/<slug>/{prd,plan,tasks}.md` | Acceptance criteria, task breakdown |
| Maker implementation | `odoo/`, `agents/`, `infra/`, `web/`, `data-intelligence/` | Code diff |
| Judge validation | CI gates, judge agents | Quality report |
| Deploy + evidence | GitHub Actions, Azure DevOps pipelines | Deploy proof in `docs/evidence/` |
| SRE feedback | App Insights, Azure Monitor, release-ops | Issue or green status |

## Platform planes

| Plane | Repo | Role |
|---|---|---|
| Transaction | `odoo/` | ERP system of record |
| Agent/Control | `agents/` | Foundry agent policies, skills, MCP manifests |
| Data/Intelligence | `lakehouse/` (target: `data-intelligence/`) | Databricks, Unity Catalog, medallion pipelines |
| Infrastructure | `infra/` | Azure IaC, DNS, Bicep, Terraform |
| Delivery | `.github/`, Azure DevOps | CI/CD, pipelines, evidence fabric |
| Web | `web/` | Public site, marketing copilot |
| Operations | `ops-platform/` | Ops console, platform tooling |
| Automation | `automations/` | n8n workflows, cron jobs |

## Agent mapping

### Makers (implement)

- `chief-architect` — cross-cutting architecture decisions
- `odoo-runtime` — Odoo CE module development
- `foundry-agent` — Azure AI Foundry agent/copilot work
- `data-intelligence` — Databricks pipelines, data contracts
- `azure-platform` — infrastructure, networking, identity
- `release-ops` — deployment, evidence, rollback

### Judges (validate)

- `architecture-judge` — boundary and contract compliance
- `security-judge` — secrets, RBAC, vulnerability posture
- `governance-judge` — SSOT consistency, CI gate coverage
- `finops-judge` — cost, resource efficiency
- `customer-value-judge` — business outcome alignment
- `tbwa-fit-judge` — client packaging and offering fit

## SRE feedback loop

Release-ops / observability is responsible for:

- Post-deploy health verification
- Evidence capture to `docs/evidence/<date>/`
- Regression detection via App Insights / Azure Monitor
- Automatic issue creation for failed health/SLO/runtime checks
- Issues link back to the originating spec bundle

## Rule

Every change flows through: **spec → maker → judge → pipeline → evidence → monitor**.
No step is optional. Skipping spec = incomplete. Skipping evidence = unverified.
