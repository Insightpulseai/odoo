# CAF Plan — Prepare Your Organization for Cloud (Complete)

> Tailored rewrite of Microsoft CAF "Plan → Prepare your organization for cloud."
> Cross-references: `CAF_STRATEGY_COMPLETE.md`, `CAF_TEAM_MODEL.md`, `cloud_operating_model.yaml`

---

## 1. What this stage is

The bridge between strategy and execution. Converts strategic objectives into an actionable adoption plan by choosing the right operating model, planning responsibilities, and documenting ownership.

---

## 2. Cloud journey classification

| Product plane | Repo | Journey type |
|---|---|---|
| ERP / transactions | `odoo` | Migrate and modernize |
| Control plane | `platform` | Foundational / shared services |
| Agent runtime | `agent-platform` | Cloud-native (greenfield) |
| Data / intelligence | `data-intelligence` | Modernize + build new |
| Experience / web | `web` | Cloud-native |
| Automation | `automations` | Rationalize and migrate |
| Infrastructure | `infra` | Foundational / shared services |

---

## 3. Operating model decision

### Decision

**Shared management with centralized human accountability.**

### What this means

- **Platform products** (`infra`, `platform`) establish landing zones, shared services, governance guardrails, and delivery controls
- **Workload products** (`odoo`, `agent-platform`, `data-intelligence`, `web`, `automations`) operate autonomously within those controls
- **Enablement products** (`.github`, `agents`, `design`, `docs`, `templates`) provide doctrine, knowledge, and scaffolding
- **Judge agents** represent stakeholder review functions
- **Final authority** on priorities, risk, and exceptions remains human

### Operating model statement

> The platform uses a shared-management cloud operating model with centralized human accountability. Platform products establish landing zones, shared services, governance guardrails, and delivery controls. Workload products operate autonomously within those controls. Stakeholder review functions are represented by judge agents, while final approval, risk acceptance, and exception handling remain human responsibilities.

---

## 4. Governance responsibilities

| Role | Owner |
|---|---|
| Accountable | Jake |
| Responsible (implementation) | azure-platform, release-ops |
| Consulted (review) | governance-judge, architecture-judge |

Scope: assess risk, define policies, monitor progress, enforce CI gates, validate SSOT consistency.

---

## 5. Security responsibilities

| Role | Owner |
|---|---|
| Accountable | Jake |
| Responsible (implementation) | azure-platform |
| Consulted (review) | security-judge |
| Workload conformance | odoo-runtime, foundry-agent, data-intelligence |

Scope: identity-first rollout, secret boundaries, RBAC, secure-by-default surfaces, security as early judge function.

---

## 6. Cloud management responsibilities

| Role | Owner |
|---|---|
| Accountable | Jake |
| Responsible (implementation) | release-ops |
| Supporting platform | platform |

Scope: deploy, evidence capture, post-deploy health, rollback, SRE feedback loop, issue creation.

---

## 7. AI adoption responsibilities

| Role | Owner |
|---|---|
| Accountable | Jake |
| Runtime / platform | foundry-agent |
| Data readiness | data-intelligence |
| Guardrails | security-judge, governance-judge |
| Public advisory boundary | web + foundry-agent |

Scope: AI use cases mapped to business friction, Foundry as primary agent platform, MCP as tool boundary, governed data lineage, advisory-only public copilots.

---

## 8. Partner responsibilities

| Partner | Role | Responsibility |
|---|---|---|
| Microsoft Azure | Cloud platform | Compute, identity, AI Foundry, DevOps, monitoring |
| Databricks | Data platform | Unity Catalog, lakehouse, medallion pipelines |
| OCA / Odoo | ERP ecosystem | CE modules, OCA community addons, parity |
| Cloudflare | Edge | DNS (authoritative, DNS-only mode for Front Door) |
| GitHub | Source control | Repos, CI/CD, org governance, Copilot |
| TBWA/SMP | Client context | Packaging requirements, offering fit |

---

## 9. Review cadence

Responsibilities are reviewed on these triggers:

- New product plane added
- Production cutover milestone
- New external partner onboarded
- New agent or tool boundary introduced
- Change in security posture
- New environment tier provisioned
- Monthly: operating-model health check

---

## 10. Product-plane ownership summary

### Platform products (guardrails + shared services)

- `infra` — landing zones, networking, RBAC, observability
- `platform` — Supabase, service catalog, ops console backend

### Workload products (autonomous within guardrails)

- `odoo` — ERP transactions, addons, runtime
- `agent-platform` — Foundry agents, tools, workflows, evals
- `data-intelligence` — Databricks, governed data products, BI
- `web` — websites, portals, browser extensions
- `automations` — n8n, schedulers, jobs

### Enablement products (doctrine + scaffolding)

- `.github` — org governance, reusable workflows
- `agents` — personas, skills, judges, knowledge
- `design` — tokens, Figma exports, brand assets
- `docs` — cross-repo architecture, strategy, evidence
- `templates` — starter kits, repo templates

---

## SSOT reference

Machine-readable operating model: `ssot/governance/cloud_operating_model.yaml`
