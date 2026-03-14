# AGENTIC_TARGET_STATE

## Purpose

Define the canonical agentic target state for the InsightPulseAI platform.

This document aligns:
- Azure AI Foundry as the production AI runtime
- Microsoft Agent Framework as the orchestration-in-code target
- spec-driven development as the engineering entry point
- deterministic CI/CD as the deployment model
- agent-assisted day-2 operations as the operational feedback loop

## Status

Canonical.

## Executive Summary

The target state is:

- self-hosted core by default
- Azure-native identity and control plane
- Azure AI Foundry as the production assistant runtime
- Microsoft Agent Framework as the orchestration framework target in code
- Azure DevOps as the delivery and release control plane
- deterministic deployment automation
- agent-assisted review, evaluation, and day-2 operations
- Cloudflare allowed only as an edge exception
- Tableau Cloud allowed only as a BI consumption exception

Microsoft Agent Framework is designed for building and orchestrating agents with graph-based workflows, streaming, checkpointing, human-in-the-loop support, observability, and Python/.NET implementations. Azure AI Foundry's SDK guidance positions Foundry as the runtime surface for models, agents, and tools, and recommends Microsoft Entra ID authentication patterns such as `DefaultAzureCredential` for secure access.

## Core Doctrine

### 1. Runtime doctrine
Production AI assistants run in Azure AI Foundry.

### 2. Orchestration doctrine
Agent orchestration logic belongs in code and targets Microsoft Agent Framework patterns.

### 3. SDLC doctrine
Engineering starts with specifications, not direct implementation.

### 4. Deployment doctrine
Build and deployment flows remain deterministic.

### 5. Operations doctrine
Post-deploy issues, incidents, and drift are summarized and looped back into issues, specs, and PRs with humans remaining in control.

## Canonical Platform Shape

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

## Canonical AI Runtime

### Production runtime

```text
Azure AI Foundry
  -> ipai-odoo-copilot-azure
```

### Why

Azure AI Foundry's SDK model provides a unified surface for models, agents, and tools, with project-level endpoints and agent/runtime capabilities.

### Repo-side SSOT

The production runtime must have a repo-side contract under `agents/`.

Required artifacts:
- description
- instructions
- metadata
- starter prompts
- runtime contract
- eval notes
- knowledge references

## Canonical Orchestration Target

### Framework target

```text
Microsoft Agent Framework
  -> coordinator
  -> specialists
  -> workflow graph
```

### Why

Microsoft Agent Framework explicitly supports graph-based workflows, data flows, checkpointing, human-in-the-loop, middleware, OpenTelemetry observability, and multi-language implementations.

### Role in the stack

Use Microsoft Agent Framework for:
- coordinator/specialist agent structures
- workflow graph design
- local and code-controlled orchestration
- orchestration prototypes that may later influence the production runtime

Do not use it to replace:
- Azure AI Foundry as the current production runtime
- Azure DevOps as the CI/CD control plane
- deterministic infrastructure deployment logic

## Agentic SDLC Model

### Canonical flow

```text
spec/<slug>/
  -> coding agent implementation
  -> PR
  -> AI-assisted code quality review
  -> deterministic CI/CD deploy
  -> smoke checks
  -> SRE/ops agent monitoring
  -> issue / remediation loop
```

### SDLC rules

- spec first
- code second
- PR-based review required
- deterministic build and deploy
- human approval at release boundaries
- post-deploy operational feedback becomes backlog/spec input

## Deterministic vs Non-Deterministic Boundary

### Deterministic systems

These remain deterministic by default:
- CI/CD pipelines
- infrastructure deployment
- RBAC assignment flows
- identity bootstrap
- payment/financial control logic
- policy engines
- critical document ingestion controls

### Non-deterministic / agentic systems

These are appropriate for agentic assistance:
- requirements translation
- scoped implementation tasks
- review summarization
- advisory analysis
- anomaly explanation
- operations investigation support
- issue summarization and remediation suggestions

## Assistant Capability Model

### Informational
- answer questions
- summarize
- explain
- cite or reference where applicable
- interpret KPIs, workflows, or outputs

### Navigational
- guide users to the correct module, page, function, or workflow
- explain where a task belongs
- route the user to the right operational surface

### Transactional
- prepare drafts
- trigger bounded actions
- create or update state only when explicitly permitted
- require authentication, authorization, and auditability

## Assistant Modes

### Public advisory mode
Allowed:
- informational
- light navigational

Not allowed:
- privileged transactional actions
- tenant-private retrieval
- internal operator actions

### Authenticated user mode
Allowed:
- informational
- navigational
- bounded transactional drafts/actions

### Internal operator mode
Allowed:
- informational
- navigational
- controlled transactional actions with audit trail and approvals where needed

## Repo Responsibilities

### Canonical active repos

```text
Insightpulseai/
  .github/
  odoo/
  web/
  agents/
  infra/
  ops-platform/
  automations/
  lakehouse/
  design-system/
  templates/
```

### .github
Owns: governance, reusable workflow patterns, policy enforcement conventions

### odoo
Owns: ERP runtime, Odoo modules, Odoo-specific business logic, runtime health checks

### web
Owns: public and authenticated web surfaces, public advisory assistant shell, frontend integration with backend/edge endpoints

### agents
Owns: Foundry runtime contracts, orchestration target experiments, prompts/instructions/metadata, eval artifacts, agent registries

### infra
Owns: identity/bootstrap docs, Azure provisioning and env contracts, Cloudflare configuration, RBAC and service-connection contracts, monitoring and supporting-service baselines

### ops-platform
Owns: self-hosted control-plane services, internal admin/control APIs

### automations
Owns: n8n workflows, cron jobs, webhook-triggered operational automations, schedules and runbooks

### lakehouse
Owns: CDC and ingestion, bronze/silver/gold, semantic layer, Tableau publication contracts

### design-system
Owns: design tokens, component primitives, icons and brand assets

### templates
Owns: scaffolds only, bootstrap generators only

## Required Repo Structures

### agents

```text
agents/
  foundry/
    ipai-odoo-copilot-azure/
      description.md
      instructions.md
      metadata.yaml
      starter-prompts.yaml
      runtime-contract.md
      evals/
      docs/
  orchestration/
    microsoft-agent-framework/
      docs/
      python/
      dotnet/
      workflows/
      spec/
```

### web

```text
web/
  apps/
    marketing-site/
      src/
      server/
      tests/
  docs/
    architecture/
      LANDING_PAGE_AGENT_EXPOSURE.md
      ASSISTANT_INTERACTION_MODES.md
      AGENTIC_SDLC_WEB_BOUNDARY.md
```

### infra

```text
infra/
  azure/
    foundry/
    identity/
    monitor/
    devops/
    sre/
      docs/
      runbooks/
  docs/
    architecture/
      CLOUD_NATIVE_PLATFORM_PLAN.md
      CANONICAL_REFERENCE_STACK.md
      AGENTIC_SDLC_PLATFORM_MODEL.md
```

### automations

```text
automations/
  n8n/
  jobs/
  schedules/
  runbooks/
  docs/
    architecture/
      DETERMINISTIC_AUTOMATION_POLICY.md
```

## Delivery Control Plane

### Canonical delivery plane

Azure DevOps is the CI/CD and release control plane.

### Required control-plane elements

- dev, staging, prod environments
- self-hosted agent pools
- workload identity federation service connections
- smoke checks
- rollback procedures
- release gating at appropriate boundaries

## Identity and Auth Model

### Human identity

- Microsoft 365 + Entra ID
- named accounts only
- emergency access accounts
- least-privilege admin roles
- MFA baseline

### Machine identity

- workload identity federation preferred
- managed identities where applicable
- no PAT-first automation path
- no client-secret-first deployment default where avoidable

## Operations and SRE Loop

### Day-2 target pattern

```text
production telemetry
  -> investigation / summarization
  -> issue creation
  -> remediation proposal
  -> spec / task / PR
```

### SRE agent role

SRE-style agents may:
- inspect logs, metrics, and traces
- summarize incidents and likely root causes
- suggest or trigger bounded remediation actions
- create issues or structured feedback for follow-up

### Constraint

SRE agents do not replace:
- IaC as source of truth
- formal approval boundaries
- deterministic deployment controls

## What is explicitly not allowed

- no wholesale adoption of external samples as platform architecture
- no replacement of self-hosted core with template-hosted defaults
- no use of agents to make uncontrolled deployment or infrastructure decisions
- no public exposure of privileged secrets
- no mixing of runtime ownership across web, agents, and infra
- no direct analytics-at-scale against transactional Odoo as the default pattern

## Adoption Phases

### Phase 1 — foundation
- identity baseline
- Azure DevOps control plane
- Foundry runtime contract
- observability baseline

### Phase 2 — runtime and exposure
- production hardening of ipai-odoo-copilot-azure
- public advisory assistant shell
- backend adapter and optional edge proxy
- assistant mode separation

### Phase 3 — orchestration maturity
- Microsoft Agent Framework orchestration experiments
- coordinator/specialist workflow graphs
- evaluation and observability of orchestration flows

### Phase 4 — operational feedback loop
- SRE-style issue generation
- remediation loop into specs/PRs
- stronger agent-assisted release and runbook support

## Canonical reference interpretation

The platform uses this reference stack:
- Azure AI Foundry SDK + Agent Service for production runtime
- Microsoft Agent Framework for orchestration-in-code
- Spec-first / spec-driven development for engineering entry
- deterministic CI/CD for build and deployment
- agent-assisted review and day-2 operations

## Related Documents

- docs/architecture/ODOO_FOUNDRY_DATABRICKS_TARGET_STATE.md
- docs/architecture/HOSTING_POLICY.md
- docs/architecture/REPO_BOUNDARIES.md
- infra/docs/architecture/CLOUD_NATIVE_PLATFORM_PLAN.md
- infra/docs/architecture/CANONICAL_REFERENCE_STACK.md
- web/docs/architecture/LANDING_PAGE_AGENT_EXPOSURE.md
- lakehouse/docs/architecture/CDC_AND_ANALYTICS_SEPARATION.md

## Verification checklist

- Foundry remains the production runtime SSOT
- Microsoft Agent Framework is the orchestration target, not the runtime replacement
- spec-driven development is the engineering entry point
- CI/CD remains deterministic
- SRE agents are treated as day-2 augmentation, not source-of-truth deployment control

---

*Last updated: 2026-03-14*
