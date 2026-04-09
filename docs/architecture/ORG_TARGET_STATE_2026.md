# Org Target State 2026

> **Status**: Active
> **SSOT**: `infra/ssot/github/desired-end-state.yaml` (schema 1.2)
> **Date**: 2026-03-23

---

## Doctrine

InsightPulseAI operates on an **11-repo, 9-plane** target state.

- `odoo` is the transactional system of record.
- `platform` is the control plane and SSOT glue layer.
- `agents` is the agent authority surface for personas, skills, judges, evals, and workflow contracts.
- `web` is the user-facing product and documentation surface.
- `data-intelligence` is the governed evidence and analytics plane.
- `infra` is the deployment and cloud substrate.
- `docs` is the cross-repo architecture and runbook authority.
- `design` is the canonical design-system and brand asset repo.
- `automations` is the scheduled workflow and job lane.
- `templates` is bootstrap-only.
- `.github` is org governance and CI policy.

**No separate `agent-platform` repo is required in the current target state.** Agent runtime concerns are distributed across `agents`, `platform`, `web`, `infra`, and `data-intelligence` according to authority boundaries.

---

## 9-Plane Operating Model

| Plane | Repo | Role |
|-------|------|------|
| Governance spine | `.github` | Org-wide policy, reusable workflows, guardrails |
| Transaction SoR | `odoo` | Odoo 18 CE + OCA + IPAI bridge, operational SoR |
| Control plane | `platform` | Metadata, contracts, registry/state glue, vault refs |
| Agent plane | `agents` | Personas, skills, judges, evals, routing, knowledge bases |
| Experience plane | `web` | Product UIs, copilot shells, docs app, operator apps |
| Data intelligence | `data-intelligence` | Databricks, Unity Catalog, medallion, semantic-serving |
| Automation plane | `automations` | Scheduled jobs, workflow runners, batch reconciliations |
| Infrastructure | `infra` | Azure, Cloudflare, network, deploy substrate |
| Documentation | `docs` | Cross-repo architecture, runbooks, evidence, target-state |

Non-plane repos (no runtime authority): `design` (tokens, brand), `templates` (starter kits).

---

## Repo Authority Boundaries

### `odoo`

**Owns**: ERP runtime, addons, ORM/business objects, Odoo Copilot adapter, action queue execution.

**Does not own**: generalized agent orchestration, cross-product copilot personas, strategic review logic, enterprise knowledge segmentation.

### `agents`

**Owns**: agent registry, skill packs, judges, eval contracts, persona shells, workflow definitions, TaxPulse/judge lanes, Diva Copilot family definition, knowledge bases (azure_platform, odoo18_docs, databricks, org-docs).

**Does not own**: ERP business objects, user-facing product surfaces, infrastructure substrate, control-plane state.

### `platform`

**Owns**: control-plane contracts, orchestration metadata, tool registry, state transitions, approval models, vault references, backend glue between agents/web/odoo.

**Does not own**: agent logic, user-facing UI, ERP data, analytics transforms.

### `web`

**Owns**: Diva Goals app, Diva Copilot web shells, Fluent 2 app shell, docs frontend, review and approval UI.

**Does not own**: backend state, agent logic, ERP data, infrastructure.

### `data-intelligence`

**Owns**: evidence lakehouse, bronze/silver/gold transforms, readiness scoring, drift/orphan metrics, semantic-serving prep, BI delivery artifacts.

**Does not own**: agent orchestration, ERP transactions, UI surfaces.

### `infra`

**Owns**: Azure topology, Front Door/WAF/networking, Foundry runtime infrastructure, Databricks infra, private endpoints/firewall/DNS/deploy substrate.

**Does not own**: business logic, agent definitions, UI code.

---

## Cross-Repo Product Placement

Products span multiple repos. Each repo keeps its single authority boundary.

### Diva Goals

| Repo | Owns |
|------|------|
| `web` | UI, dashboards, review surfaces, approval flows |
| `platform` | Backend contracts, state, metadata, orchestration state |
| `agents` | Copilot, judges, skills, workflow contracts |
| `data-intelligence` | Evidence marts, readiness metrics, drift metrics |
| `docs` | Target-state architecture and review doctrine |

### Diva Copilot Family

| Repo | Owns |
|------|------|
| `agents` | Executive Copilot, Strategy Copilot, Tax Guru, TaxPulse, judges |
| `platform` | Runtime metadata, registries, session/state, tool bindings |
| `web` | Chat shells and copilot panels |
| `odoo` | Odoo-side adapter/module |
| `data-intelligence` | Evidence feeds for grounded review and metrics |

### Odoo Copilot

| Repo | Owns |
|------|------|
| `odoo` | Addon, context adapter, record-aware UI hooks, approved action dispatch |
| `agents` | Core strategy logic, judge logic, tax doctrine |
| `platform` | Action/approval routing |
| `data-intelligence` | Governed analytical outputs for grounding |

### Tax Guru / TaxPulse

| Repo | Owns |
|------|------|
| `agents` | Tax agent logic, filing workflow, judge lanes |
| `odoo` | ERP record context + action queue |
| `platform` | Tax workflow state, routing, policy refs |
| `data-intelligence` | Filing readiness metrics, exception analytics |
| `docs` | Tax policy architecture, runbooks |

---

## Why No Separate `agent-platform` Repo

A separate `agent-platform` repo would overlap five existing repos:

1. Agent registries → already in `agents`
2. Orchestration state → already in `platform`
3. Deploy contracts → already in `infra`
4. Copilot shell logic → already in `web`
5. Eval metrics → already in `data-intelligence`

**Add it later only if**:
- A shared runtime service is used by multiple copilots/products
- The agent layer has a distinct deployment lifecycle from `platform` and `agents`
- A single productized orchestration API no longer fits as glue in `platform`
- Multiple repos depend on a shared agent backend beyond metadata, skills, or infra

---

## Revision History

| Date | Change |
|------|--------|
| 2026-03-23 | Revised from 5-layer to 9-plane model. Removed `agent-platform` from target repo map. Added cross-repo product placement. |
| 2026-03-17 | Previous 12-repo target with 5-layer model (superseded). |

---

## Cross-references

- `infra/ssot/github/desired-end-state.yaml` — GitHub repo target state
- `ssot/governance/ado_github_authority_map.yaml` — ADO project ↔ GitHub repo mapping
- `docs/architecture/ADO_GITHUB_AUTHORITY_MAP_2026.md` — authority map (human-readable)
- `ssot/governance/azdo-execution-hierarchy.yaml` — full Epic/Issue/Task hierarchy
- `docs/architecture/AZURE_DEVOPS_OPERATING_MODEL.md` — operating model detail
