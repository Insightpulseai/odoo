# Delivery Governance — Azure DevOps Pipeline Operating Model

## Authority hierarchy

1. **Repo YAML** = pipeline definition truth
2. **Azure DevOps CLI / REST** = automation and control surface
3. **Azure DevOps UI** = inspection surface, not the primary authoring surface

## Principles

- YAML pipeline definitions are the authoritative build/release definition.
- Azure DevOps CLI is the default automation surface for pipeline lifecycle operations.
- REST may be used for advanced run control where CLI coverage is insufficient.
- The Azure DevOps portal is an observation and administration surface, not the primary
  authoring surface.

## Supported operational actions

| Action | Surface | Command |
|--------|---------|---------|
| List pipelines | CLI | `az pipelines list` |
| Show pipeline details | CLI | `az pipelines show` |
| Queue runs | CLI | `az pipelines run` |
| Update pipeline metadata | CLI | `az pipelines update` |
| Delete retired pipelines | CLI | `az pipelines delete` |
| Create YAML-backed pipelines | CLI | `az pipelines create` |
| Skip stages (emergency) | REST | `stagesToSkip` parameter |

## Exception handling

Any emergency-only run behavior such as stage skipping must be:

- Explicitly documented
- Audited via pipeline run logs
- Constrained to named exception scenarios
- Never treated as normal workflow

## Pipeline definition location

| Pipeline | Path | Target |
|----------|------|--------|
| Odoo deploy | `odoo/.azure-pipelines/deploy-odoo.yml` | ACA revision rollout |

## Canonical Azure Pipelines delivery shape

### Required stage graph

- **Build** — compile, lint, package
- **Test** — unit tests, integration tests, compliance checks
- **Deploy to Staging** — deploy to staging ACA revision, smoke test
- **Deploy to Production** — manual validation gate, branch-gated, deploy to production ACA revision

### Required controls

- Non-skippable stages for mandatory quality/security checks
- Manual validation for protected deployment boundaries
- Explicit branch conditions for production (at minimum `main` and approved release branches)
- Documented rollback or alternate deployment path as manual exception stages

### Security controls

- Use YAML instead of Classic pipelines
- Prefer Microsoft-hosted agents by default
- Restrict protected resources with approvals/checks
- Restrict service connections to authorized branches where applicable
- Authorize secret-bearing variable groups explicitly for YAML pipelines

## Constraints

- Do not treat Azure DevOps classic/manual pipeline config as canonical.
- Do not allow pipeline behavior to drift from repo-authored YAML.
- Do not require manual Azure DevOps portal edits for standard release operations.

---

---

## Canonical AI platform shape for Pulser

Pulser uses a Foundry-first enterprise AI architecture.

### Core platform roles

- **Foundry**: model, agent, evaluation, and governed AI application platform
- **Foundry Agent Service**: managed runtime for agent execution and tool orchestration
- **Foundry IQ / Azure AI Search-backed retrieval**: grounding layer for enterprise knowledge
- **Odoo**: transactional system of record and action plane
- **Azure-managed identity / secret / monitoring controls**: production control plane

### Preferred execution pattern

- Retrieval and tool use before unsupported generation
- Internal/private service connectivity where feasible
- Monitored and evaluated production behavior
- Explicit separation between:
  - user-facing interaction surfaces
  - orchestration logic
  - knowledge/retrieval plane
  - transactional action plane

---

*Last updated: 2026-04-10*
