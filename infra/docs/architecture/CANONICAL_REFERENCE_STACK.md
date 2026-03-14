# Canonical Reference Stack

## Purpose

Define the canonical reference stack for the InsightPulseAI platform.

This document clarifies which external references are authoritative for:
- runtime architecture
- scaffolding patterns
- domain capability modeling
- assistant interaction design

It also defines what each reference is **allowed** to influence and what it must **not** override.

## Status

Canonical.

## Core Rule

No single sample, template, marketplace listing, or vendor solution page is allowed to become the platform architecture by default.

The platform uses a **reference stack**:

1. Azure AI Foundry SDK + Foundry Agent Service for production AI runtime
2. Azure Developer CLI templates as selective scaffolding inputs only
3. Databricks industry solution pages as domain capability references only
4. SAP Joule capability model as assistant interaction-pattern reference only

## Platform Baseline

The reference stack sits inside this platform baseline:

- self-hosted core by default
- Azure-native identity and control plane
- Azure DevOps as CI/CD and release control plane
- Azure AI Foundry as production AI runtime
- Cloudflare edge services as an approved edge exception only
- Tableau Cloud as an approved BI exception only

## Canonical Architecture Shape

```text
Identity / control plane
  -> Microsoft 365 + Entra ID
  -> Azure DevOps
  -> workload identity federation
  -> RG-scoped RBAC

Edge
  -> Cloudflare DNS / WAF / CDN
  -> optional Workers for edge/API/proxy only

Self-hosted core
  -> Odoo
  -> backend adapters / APIs
  -> Postgres
  -> automations runtime
  -> ops-platform

AI runtime
  -> Azure AI Foundry
     -> ipai-odoo-copilot-azure

Analytics
  -> CDC / logical replication
  -> self-hosted lakehouse
  -> Tableau Cloud
```

## Reference Layer 1 — Azure AI Foundry SDK + Foundry Agent Service

### Role

This is the **canonical production AI runtime reference**.

### What it governs

* agent runtime model
* agent creation/update model
* project endpoint assumptions
* authentication approach
* tool/agent integration model
* runtime ownership boundaries
* production deployment notes for `ipai-odoo-copilot-azure`

### Canonical interpretation

* Azure AI Foundry is the production runtime SSOT
* repo-side runtime contract lives in `agents/`
* local orchestration experiments do not replace the production runtime
* runtime changes must be reflected in repo-side contract artifacts

### Not allowed to override

* self-hosted core rule
* repo boundaries
* web/frontend ownership
* automation ownership
* data architecture ownership

## Reference Layer 2 — Azure Developer CLI Templates

### Role

These are **selective scaffolding references only**.

### What they are allowed to influence

* `infra/` directory layout ideas
* `azure.yaml` mapping ideas
* managed identity deployment patterns
* production support service composition
* app-shell organization ideas

### Canonical interpretation

* templates are starting points, not architecture authority
* no template is adopted wholesale
* only the useful parts are extracted
* sample-specific hosting or business logic must be stripped
* self-hosted core remains the default even if a template assumes Azure-hosted app runtime

### Not allowed to override

* target repo structure
* target hosting policy
* runtime ownership
* public/advisory assistant mode rules

## Reference Layer 3 — Databricks Industry Capability Pages

### Role

These are **domain capability references only**.

### What they are allowed to influence

* business-domain lanes in `lakehouse`
* KPI families
* decisioning outputs
* alert and automation trigger ideas
* semantic layer priorities

### Canonical interpretation

These pages help define **what the data platform should do**, not **where the platform should run**.

They inform the following domain lanes:

* Customer and Identity Intelligence
* Campaign and Marketing Intelligence
* Retail and Commerce Intelligence
* Media, Audience, and Monetization Intelligence
* Financial Governance Intelligence
* Operations and Productivity Intelligence
* Supply Chain and Inventory Intelligence

### Not allowed to override

* self-hosted core rule
* Azure control-plane decisions
* Foundry runtime decisions
* repo boundaries
* CI/CD control-plane choices

## Reference Layer 4 — SAP Joule Capability Model

### Role

This is the **assistant interaction-pattern reference**.

### What it is allowed to influence

* capability typing for assistant experiences
* public vs authenticated vs operator interaction modes
* product language around assistant capabilities
* task classification in assistant UX design

### Canonical capability model

The platform assistant model uses three capability types:

#### Informational

* answer questions
* summarize
* explain
* cite or reference sources where applicable

#### Navigational

* guide users to the correct module, function, workflow, or page
* explain where to perform a task
* route the user to the correct operational surface

#### Transactional

* prepare or execute bounded actions
* create drafts
* trigger controlled workflows
* write or update state only when explicitly allowed, authenticated, and auditable

### Canonical interpretation by mode

#### Public advisory mode

Allowed: informational, light navigational.
Not allowed: privileged transactional actions, tenant-private retrieval.

#### Authenticated user mode

Allowed: informational, navigational, bounded transactional drafts/actions.

#### Internal operator mode

Allowed: informational, navigational, controlled transactional actions with audit and approval boundaries.

### Not allowed to override

* security model
* auth and authorization boundaries
* write-path restrictions
* public/private mode separation

## Reference-to-Repo Mapping

| Repo | Primary reference source | Outputs |
|------|------------------------|---------|
| `agents` | Foundry SDK + Agent Service | runtime contracts, prompts, metadata, eval notes |
| `web` | azd app-shell patterns, capability model | copilot shell, backend adapter, UX mode docs |
| `infra` | Azure service composition, Cloudflare | deployment baselines, env contracts, RBAC docs |
| `lakehouse` | Databricks industry capabilities | domain model, semantic priorities, Tableau contracts |

## Adoption Rules

1. Every imported idea must be mapped to a canonical repo owner before adoption
2. Every external reference must be classified as runtime, scaffold, capability, or interaction-pattern
3. No external sample may override hosting policy, repo boundaries, identity model, or CI/CD control plane
4. If a reference conflicts with the platform baseline, the platform baseline wins

## Related Documents

* `ssot/governance/platform-strategy-2026.yaml`
* `docs/architecture/HOSTING_POLICY.md`
* `agents` runtime contract docs
