# AI-Led Engineering Operating Model

## Purpose

Define the canonical engineering lifecycle operating model for the IPAI platform, benchmarked against Microsoft's AI-led SDLC with Azure and GitHub reference architecture.

This document covers spec-driven development, coding agents, quality agents, CI/CD, and SRE feedback loops — the engineering equivalent of what SAP on Azure provides for ERP workloads.

## Scope

- Spec-first delivery workflow (spec bundles as the unit of work)
- Coding agent patterns and boundaries
- Quality agent patterns (review, test generation, drift detection)
- CI/CD pipeline architecture (GitHub Actions + Azure DevOps)
- SRE feedback loops (production signals → backlog)
- Engineering governance and repo policy

Out of scope:
- AI model operations (see `platform/docs/ai-platform/`)
- Data engineering pipelines (see `data-intelligence/docs/`)
- Odoo ERP business logic (see `docs/odoo-on-azure/runtime/`)

## When to Use This

- Designing or modifying the engineering workflow
- Adding a new coding or quality agent
- Reviewing CI/CD pipeline architecture
- Implementing SRE feedback automation
- Onboarding a new contributor to the spec-first workflow

## Benchmark: AI-Led SDLC with Azure and GitHub

| Microsoft Reference | IPAI Equivalent | Status |
|---|---|---|
| Spec-driven development | `spec/` bundles (76 spec bundles) | Operational |
| Coding agents (Copilot, Claude Code) | GitHub Copilot + Claude Code + `.github/agents/` | Operational |
| Quality agents (review, test) | `.github/agents/odoo-platform.agent.md` + skills | Scaffold |
| CI/CD with GitHub Actions | GitHub Actions (CI) + Azure DevOps (deploy) | Operational |
| Preview environments | ACA revision-based previews | Partial |
| SRE feedback loops | Alert → n8n → backlog (scaffold) | Scaffold |
| Repository governance | `.github/` policies, branch protection, CODEOWNERS | Operational |

## Architecture / Concepts

### Spec-First Delivery

```
Spec Bundle (spec/<feature>/prd.md)
  └→ Implementation Plan
       └→ Coding Agent Execution
            └→ Quality Agent Review
                 └→ CI/CD Pipeline
                      └→ Production
                           └→ SRE Feedback → Next Spec
```

Every significant change starts with a spec bundle in `spec/`. The spec is the contract between intent and implementation.

### Coding Agent Boundaries

- **GitHub Copilot**: In-editor completions, inline suggestions
- **Claude Code**: Multi-file implementation, refactoring, exploration
- **Custom agents** (`.github/agents/`): Domain-specific routing (Odoo platform, OCA triage)
- **Skills** (`skills/`): Focused capabilities (models, views, OCA selection, upgrade, external bridge)

Agents do not bypass CI gates. Agent-generated code goes through the same review and test pipeline as human-authored code.

### Quality Agent Patterns

| Agent | Trigger | Action |
|---|---|---|
| OCA Triage | New OCA module proposal | Verify 18.0 availability, check quality gates, check conflicts |
| Module Drift Gate | PR with addon changes | `scripts/ci/module_drift_gate.sh` |
| Spec Validator | PR with spec changes | `scripts/spec_validate.sh` |
| Repo Health | All PRs | `scripts/repo_health.sh` |

### CI/CD Architecture

| Authority | Scope |
|---|---|
| GitHub Actions | CI (lint, test, build), docs/web deploy |
| Azure DevOps | Odoo/Databricks/infra deploy with environment gating |
| Azure Boards | Portfolio planning, sprint tracking |
| GitHub Issues | Engineering execution backlog |

See `ssot/governance/platform-authority-split.yaml` and `ssot/governance/ci-cd-authority-matrix.yaml`.

### SRE Feedback Loops

```
Production Alert (Azure Monitor)
  └→ Action Group → n8n webhook
       └→ Triage automation
            └→ GitHub Issue (if actionable)
                 └→ Next sprint backlog
```

Production signals feed back into the engineering backlog. The loop closes when the fix is deployed and the alert resolves.

## Prerequisites

- GitHub repository with branch protection and CODEOWNERS
- GitHub Actions workflows configured (`.github/workflows/`)
- Azure DevOps project with service connections
- Spec bundle structure (`spec/<feature>/prd.md`)
- Agent definitions (`.github/agents/*.agent.md`)

## Procedure / Guidance

### Creating a New Spec Bundle

1. Create `spec/<feature>/prd.md` with acceptance criteria
2. Add implementation plan if complex
3. Reference in PR description
4. Spec validator runs automatically on PR

### Adding a New Coding Agent

1. Define agent in `.github/agents/<name>.agent.md`
2. Specify tools, model, and routing rules
3. Add hard rules (OCA first, no fat modules, etc.)
4. Reference existing skills or create new ones in `skills/`

### Adding a New Quality Gate

1. Create script in `scripts/ci/`
2. Add workflow in `.github/workflows/`
3. Register in CI matrix
4. Document in this file

### SRE Feedback Automation

1. Define alert rule in `infra/azure/` (Bicep)
2. Configure action group with n8n webhook
3. Create n8n workflow for triage logic
4. Map to GitHub Issue template

## Outputs / Expected State

- Every significant change has a spec bundle
- CI gates enforce code quality, module drift, and repo health
- Agent-generated code passes the same gates as human code
- Production alerts create actionable backlog items
- Engineering governance is codified, not tribal

## MCP-Assisted Planning and Execution

### Agent responsibilities

| Agent role | Planning system interaction | Boundary |
|---|---|---|
| Spec author | Creates/updates spec bundles in `spec/` | Does not create Azure Boards work items directly |
| Implementation agent | Reads committed Stories from Boards (via MCP) | Executes only against committed sprint backlog |
| Evidence agent | Validates claims, produces artifacts | Closes Stories with `Validate AB#<id>` |
| Quality agent | Reviews PRs, runs CI gates | Does not modify Boards state |

### MCP bridge

The Azure DevOps MCP Server provides read/write access to Azure Boards from agent workflows:
- Query work items by iteration, area path, or tag
- Read acceptance criteria before implementation
- Link PRs to work items programmatically
- Update work-item state on merge

### Agent boundaries

1. Agents do not create Epics or Features — those are planning decisions
2. Agents may create Tasks under existing Stories (with human approval)
3. Agents must reference `AB#<id>` in all PR descriptions
4. Agents must not bypass CI gates or skip evidence requirements

## Related Documents

- `docs/architecture/ODOO_ON_AZURE_REFERENCE_ARCHITECTURE.md` — Layer 7: Control Plane and Governance
- `.github/copilot-instructions.md` — repo-wide agent instructions
- `.github/agents/odoo-platform.agent.md` — primary Odoo agent
- `skills/` — focused skill definitions
- `ssot/governance/platform-authority-split.yaml` — CI/CD authority
- `ssot/governance/ci-cd-authority-matrix.yaml` — pipeline ownership
- `platform/docs/ai-platform/index.md` — AI platform (Foundry benchmark)
- `data-intelligence/docs/index.md` — data intelligence (Databricks+Fabric benchmark)
- `docs/planning/DOC_PROGRAM_WORK_ITEM_TEMPLATES.md` — work-item templates
- `docs/planning/DOC_PROGRAM_SPRINT_MODEL.md` — sprint operating model

## Evidence / Source of Truth

- Spec bundles: `spec/` (76 bundles + 5 org-wide target bundles)
- CI workflows: `.github/workflows/` (355 pipelines)
- Agent definitions: `.github/agents/`
- Skills: `skills/`
- Governance SSOT: `ssot/governance/`

---

*Created: 2026-04-05 | Benchmark: AI-led SDLC with Azure and GitHub | Version: 1.1*
