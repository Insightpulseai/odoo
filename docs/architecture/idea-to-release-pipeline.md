# Idea-to-Release Pipeline

## Purpose

Define the canonical end-to-end delivery pipe for InsightPulseAI from idea intake to specification, development, governed deployment, AI evaluation, and marketplace publication.

This document is the top-level orchestration contract. It does not replace detailed contracts in `docs/contracts/`.

## Authority model

| Surface | Authority |
|---|---|
| Azure Boards | Execution coordination, objective hierarchy, acceptance criteria, target iteration |
| Repo / Spec Kit | Constitution, PRD, plan, tasks, architecture, contracts |
| GitHub | Code and PR truth |
| Azure Pipelines | Build, test, package, deploy, approvals, checks, evidence |
| Odoo runtime | Staged and production Odoo deployment target |
| Microsoft Foundry | AI eval, tracing, monitoring, continuous evaluation |
| Odoo Apps | Marketplace listing and publication surface |

## Canonical hierarchy

Azure Boards uses the Basic process:

- **Epic** = strategic objective
- **Issue** = scoped requirement / workstream
- **Task** = concrete execution

## Stage model

### Stage 1 — Idea intake

**Primary system:** Azure Boards
**Required artifact:** Epic or Issue
**Exit gate:**

- title, purpose, scope, out-of-scope
- owner, target iteration
- acceptance criteria

### Stage 2 — Product definition

**Primary system:** Repo / Spec Kit
**Required artifact:**

- `spec/<slug>/constitution.md`
- `spec/<slug>/prd.md`
- `spec/<slug>/plan.md`
- `spec/<slug>/tasks.md`

**Exit gate:**

- four-file Spec Kit bundle exists
- cross-linked back to Azure Boards item
- non-goals and dependencies documented

### Stage 3 — Solution design

**Primary system:** Repo docs / SSOT
**Required artifact:** Architecture docs, contracts, runtime decisions, integration boundaries

**Exit gate:**

- all unresolved architecture decisions explicitly listed
- deploy target defined: `azure_runtime` or `odoo_sh`
- AI-enabled paths marked for eval

### Stage 4 — Development

**Primary system:** GitHub
**Required artifact:** Branch, PR, linked Azure Boards work item, code changes, test evidence

**Exit gate:**

- PR open, checks running
- linked to Issue/Task
- code owner review path defined

### Stage 5 — CI/CD

**Primary system:** Azure Pipelines
**Required artifact:** Pipeline run, test results, package/build artifact, deployment evidence, approvals/checks

**Exit gate:**

- required test levels passed
- packaging complete
- staging deploy approved

### Stage 6 — Staging deployment

**Primary system:** Odoo runtime target
**Allowed targets:** Odoo.sh staging branch/build or Azure staging environment

**Exit gate:**

- smoke checks pass
- migration/install passes
- delivery acceptance path validated
- rollback method documented

### Stage 7 — AI evaluation gate

**Primary system:** Microsoft Foundry
**Required when:** Feature contains AI behavior, model output affects user-visible behavior, agent/tool use is part of release, or marketplace listing depends on AI claims

**Exit gate:**

- thresholds pass
- traces collected
- monitoring enabled
- safety and quality within defined bounds

### Stage 8 — Production deployment

**Primary system:** Odoo runtime target

**Exit gate:**

- approvals complete
- rollout strategy applied
- bake time monitored
- rollback path ready
- production smoke checks pass

### Stage 9 — Marketplace publication

**Primary system:** Odoo Apps
**Required artifact:** Package, manifest compliance, listing copy, screenshots/media, support metadata

**Exit gate:**

- production release healthy
- bake time complete
- marketplace checklist complete

### Stage 10 — Observation and feedback

**Primary systems:** Azure Boards + Foundry + runtime evidence

**Exit gate:**

- real signals converted into tracked work (new Issues/Tasks)

## Stage contract table

| Stage | Owner | Input | Output | Exit gate |
|---|---|---|---|---|
| Idea | Product/Platform owner | Idea | Epic/Issue | Acceptance criteria defined |
| Spec | Product/Architecture | Issue | Spec bundle | Four docs complete |
| Design | Architecture | Spec bundle | Contracts/docs | Target path approved |
| Build | Engineering | Plan/tasks | PR/code | Linked PR + checks |
| CI/CD | Release engineering | PR/code | Build/package | Tests + approvals |
| Staging | Runtime owner | Package/build | Staging deployment | Smoke checks green |
| Eval | AI owner | Staging build | Eval report | Thresholds passed |
| Prod | Runtime owner | Approved staging | Production release | Bake/rollback ready |
| Publish | Product owner | Healthy prod | Marketplace listing | Checklist complete |
| Observe | Product/Ops | Production signals | New work items | Follow-up tracked |

## Dual runtime policy

### Azure runtime path

Use when the canonical deploy target is Azure-hosted Odoo (default for this platform).

### Odoo.sh path

Use only when Odoo.sh is the actual deploy target for the Odoo module/app.

Do not pretend Odoo.sh exists in the path if deployment is actually Azure-hosted.

## Reference benchmarks

SAP on Azure, SAP Concur, and Avalara AvaTax are used as architecture and process benchmarks, not mandatory integrations. See `docs/architecture/reference-benchmarks.md`.

## Mandatory cross-links

Every releaseable unit must link:

- Azure Boards Issue
- Spec Kit bundle
- PR
- Pipeline run
- Staging evidence
- Eval result (if AI-enabled)
- Production evidence
- Marketplace checklist (if published)

## Cross-references

- `docs/contracts/boards-to-spec-contract.md`
- `docs/contracts/spec-to-pipeline-contract.md`
- `docs/contracts/pipeline-to-odoo-sh-contract.md`
- `docs/contracts/eval-gate-contract.md`
- `.azuredevops/pipelines/odoo-module.yml`
- `foundry/evals/_template/thresholds.yaml`
- `marketplace/odoo/_template/manifest-checklist.md`

---

*Last updated: 2026-03-17*
