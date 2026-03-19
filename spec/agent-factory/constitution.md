# Agent Factory Constitution

> Platform doctrine and invariant rules for the InsightPulse AI Agent Orchestration Platform.
> This document is normative. All agent tooling, runtime infrastructure, CI gates, and
> governance workflows must comply with every rule stated here.
> Violations require an audit record. No exceptions.

---

## 1. Architectural Principles

These principles are ordered by priority. When two principles conflict, the lower-numbered principle wins.

| # | Principle | Rationale |
|---|-----------|-----------|
| P1 | **Agents are products, not prompts.** Every agent has a passport, contract, evaluation history, and promotion record. Ad-hoc prompt chains are not agents. | Prevents sprawl. Forces lifecycle discipline. |
| P2 | **Typed contracts over loose conventions.** Agent inputs, outputs, tool bindings, and policies are declared in schema-validated manifests. No implicit behavior. | Enables machine verification. Eliminates "it works on my machine." |
| P3 | **Repo-first.** Every agent definition, policy, evaluation result, and promotion record exists as a committed artifact. Console-only or runtime-only state is not authoritative. | Single source of truth. Full auditability via git history. |
| P4 | **Automation-first.** If a human must click a button to promote, deploy, or evaluate an agent, the process is broken. Human judgment is for policy exceptions, not routine operations. | One-man-team cannot afford manual ceremony. |
| P5 | **Evaluation before promotion.** No agent advances to a higher maturity level without machine-verifiable evaluation evidence. "It seems to work" is not evidence. | Prevents regression. Builds trust incrementally. |
| P6 | **Task bus is the orchestration backbone.** Agents do not call agents directly. Work flows through the task bus as typed task messages. Direct agent-to-agent coupling is banned. | Loose coupling. Observable routing. Kill-switch enforcement. |
| P7 | **Deterministic stage gates.** Promotion criteria are codified. A stage gate either passes or fails. No "soft" gates, no "conditional" promotions. | Removes ambiguity. Enables CI enforcement. |
| P8 | **Modular for one-man-team.** Every component must be operable by a single person with CLI tools, CI pipelines, and agent assistance. No process that requires synchronous multi-person coordination. | Reflects actual team topology. |
| P9 | **Maker-judge separation.** The agent that produces work must never be the agent that evaluates it. Judge agents are structurally independent from maker agents. | Prevents self-validation bias. |
| P10 | **Cloud-agnostic core, Azure-native runtime.** Agent contracts, policies, and evaluation schemas are portable. Runtime bindings (Foundry, ACA, Key Vault) are Azure-specific. | Protects against vendor lock-in at the design layer while exploiting platform services at runtime. |
| P11 | **Observability is not optional.** Every agent execution emits structured telemetry. Silent agents are broken agents. | Debugging and audit require traces. |
| P12 | **Fail closed, not open.** Missing policy = denied. Missing evaluation = not promoted. Missing contract = not deployable. | Safe defaults. |
| P13 | **Append-only lifecycle records.** Promotion, demotion, and retirement records are immutable once written. Corrections create new records. | Audit trail integrity. |
| P14 | **Human override always available.** Every automated decision has a manual bypass path. Bypasses create audit records. | Safety net for edge cases. |

---

## 2. Canonical Terminology

Every first-class object in the Agent Factory. Terms used inconsistently across the platform must resolve to these definitions.

| Term | Definition | Artifact Location |
|------|------------|-------------------|
| **Agent** | A named, versioned, evaluable unit of autonomous capability with a passport, contract, and lifecycle stage. Not a prompt. Not a script. | `agents/foundry/agents/` |
| **Skill** | A reusable capability module that an agent can bind. One skill may serve multiple agents. Skills have their own schema and test surface. | `agents/skills/` |
| **Tool** | An external function an agent can invoke at runtime. Tools are declared in manifests with input/output schemas and policy constraints. | `agents/foundry/tools/` |
| **Workflow** | A multi-step orchestration pattern composed of tasks routed through the task bus. Workflows are declarative, not imperative. | `spec/*/workflow.yaml` |
| **Task** | A single unit of work with a typed payload, routed by the task bus to a qualified agent. Tasks are the atomic unit of agent work. | Runtime (task bus messages) |
| **Task Bus** | The central message broker for all inter-agent work. Accepts tasks, routes them by type to qualified agents, tracks completion. No direct agent-to-agent calls. | `packages/taskbus/` |
| **Agent Contract** | A schema-validated manifest declaring an agent's inputs, outputs, tool bindings, policies, and promotion criteria. The machine-readable identity of an agent. | `agents/foundry/agents/*.manifest.yaml` |
| **Stage Gate** | A set of codified, deterministic criteria that must pass before an agent advances to the next lifecycle stage. Gates are binary: pass or fail. | `agents/foundry/gates/` |
| **Evaluation** | A structured test of agent behavior against defined scenarios. Produces machine-verifiable evidence. Evaluations are versioned and reproducible. | `agents/evals/` |
| **Promotion** | The act of advancing an agent from one maturity level to the next. Irreversible as a record. Requires evaluation evidence and (for L3+) judge sign-off. | `agents/promotions/` |
| **Runtime** | The execution environment where an agent runs. Currently Azure AI Foundry + Azure Container Apps. Runtime is a deployment target, not part of the agent definition. | Azure Foundry / ACA |
| **Registry** | The authoritative list of all agents, their current lifecycle stage, and their contract references. YAML in repo, JSON generated for runtime consumption. | `agents/registry/agents.yaml` |
| **Control Plane** | The set of services governing agent lifecycle: registry, policies, stage gates, promotions, evaluations. Does not execute agent work. | `packages/agents/` + CI workflows |
| **Memory** | Persistent state an agent accumulates across task executions. Externalized to Supabase `ops.*` tables, never held in-process. | `ops.agent_memory` (Supabase) |
| **Observability** | Structured telemetry emitted by agent executions: traces, metrics, logs. Routed to Azure Monitor + Sentry. | OTLP / Azure Monitor |
| **Policy** | A declarative constraint applied to agent behavior at runtime. Policies govern tool access, write permissions, model routing, and escalation rules. | `agents/foundry/policies/` |
| **Release Lane** | One of four deployment tracks: `canary`, `staging`, `production`, `hotfix`. Each lane has its own promotion requirements. | CI workflow configuration |
| **Factory Assembly Line** | The end-to-end pipeline from agent blueprint to production deployment: define, build, evaluate, promote, deploy, observe. | This document (section 8) |
| **Agent Passport** | The complete identity document of an agent: ID, version, maturity level, promotion history, evaluation results, policy bindings, ownership. Every agent must have one. | `agents/passports/<agent-id>.yaml` |
| **Promotion Record** | An append-only record of a single promotion event: from-level, to-level, evidence references, gate results, approver, timestamp. | `agents/promotions/<agent-id>/` |

---

## 3. Plane Separation

The platform is partitioned into three planes. Components must not cross plane boundaries except through defined interfaces.

```
┌──────────────────────────────────────────────────────────────────┐
│                        CONTROL PLANE                              │
│  Registry | Policies | Stage Gates | Promotions | Evaluations     │
│  (governs what agents exist and what they are allowed to do)      │
├──────────────────────────────────────────────────────────────────┤
│                        RUNTIME PLANE                              │
│  Task Bus | Agent Execution | Memory | Tool Binding | Telemetry   │
│  (executes agent work and manages operational state)              │
├──────────────────────────────────────────────────────────────────┤
│                        ARTIFACT PLANE                             │
│  Specs | Contracts | Configs | Manifests | Runbooks | Evidence    │
│  (stores all declarative definitions and audit records)           │
└──────────────────────────────────────────────────────────────────┘
```

### Plane Responsibilities

| Plane | Owns | Does Not Own |
|-------|------|--------------|
| **Control** | Agent registry, lifecycle state machine, policy enforcement, gate evaluation, promotion decisions | Task execution, runtime state, artifact storage |
| **Runtime** | Task routing, agent process lifecycle, memory persistence, tool invocation, telemetry emission | Policy authoring, promotion decisions, contract definitions |
| **Artifact** | Contract schemas, evaluation scenarios, promotion records, runbooks, spec bundles, evidence logs | Policy enforcement, task routing, agent execution |

### Cross-Plane Interfaces

| From | To | Interface | Example |
|------|----|-----------|---------|
| Control -> Runtime | Task bus configuration, kill switch commands | Control plane publishes routing rules; runtime plane consumes them |
| Control -> Artifact | Promotion records, gate results | Control plane writes evaluation outcomes to artifact store |
| Runtime -> Control | Telemetry, health signals | Runtime plane reports agent health; control plane decides lifecycle transitions |
| Runtime -> Artifact | Execution logs, evidence bundles | Runtime plane writes trace data to evidence directories |
| Artifact -> Control | Contract definitions, policy manifests | Artifact plane provides schemas that control plane enforces |

---

## 4. Naming Doctrine

All identifiers follow strict patterns. Non-conforming names are rejected by CI validation.

### 4.1 Agent IDs

Format: `<domain-noun>` or `<domain>-<role>` in kebab-case. Stable across versions.

| Pattern | Examples | Anti-patterns |
|---------|----------|---------------|
| `kebab-case`, 2-4 segments | `odoo-sage`, `tax-pulse`, `devops-prime`, `data-forge` | `OdooSage`, `odoo_sage`, `agent-1`, `my-agent` |
| Domain-aligned | `finance-auditor`, `deploy-guardian` | `helper`, `assistant`, `bot` |
| Version-free | `odoo-sage` (version is metadata, not part of ID) | `odoo-sage-v2` |

### 4.2 Lifecycle Stages

Stages are numbered with zero-padded IDs. Every agent traverses this sequence (stages may be skipped only forward, never backward without a demotion record).

| Stage ID | Name | Description |
|----------|------|-------------|
| `S01` | `intake` | Blueprint submitted. Passport created. Not yet buildable. |
| `S02` | `design` | Contract drafted. Input/output schemas defined. |
| `S03` | `build` | Implementation in progress. Agent code exists. |
| `S04` | `unit-test` | Unit-level evaluations written and passing. |
| `S05` | `integration-test` | Cross-agent and tool-binding tests passing. |
| `S06` | `eval-sandbox` | Full evaluation suite runs in isolated sandbox. |
| `S07` | `judge-review` | Judge agent(s) evaluate outputs. Security review complete. |
| `S08` | `canary` | Deployed to canary lane. Receives shadow traffic or limited real traffic. |
| `S09` | `staging` | Full staging deployment. Pre-production validation. |
| `S10` | `production` | Live production deployment. Full traffic. |
| `S11` | `scaling` | Horizontal scaling or performance optimization phase. |
| `S12` | `hardening` | Security hardening, edge case coverage, policy tightening. |
| `S13` | `mature` | Stable, proven, fully evaluated. Baseline for domain. |
| `S14` | `deprecation-notice` | Successor identified. 30-day sunset clock starts. |
| `S15` | `sunset` | Read-only. Task bus stops routing new work. Existing tasks drain. |
| `S16` | `retired` | Permanently decommissioned. Passport archived. No execution. |

### 4.3 Task Types

Format: `task.<domain>.<action>` using dot-delimited lowercase.

| Domain | Examples |
|--------|----------|
| `odoo` | `task.odoo.deploy-module`, `task.odoo.run-tests`, `task.odoo.migrate-data` |
| `devops` | `task.devops.build-image`, `task.devops.apply-terraform`, `task.devops.rotate-secret` |
| `data` | `task.data.run-pipeline`, `task.data.validate-schema`, `task.data.backfill` |
| `finance` | `task.finance.reconcile`, `task.finance.generate-report`, `task.finance.tax-compute` |
| `platform` | `task.platform.health-check`, `task.platform.scale-out`, `task.platform.dns-update` |
| `eval` | `task.eval.run-suite`, `task.eval.judge-review`, `task.eval.benchmark` |

### 4.4 Maturity Levels

Maturity levels map to lifecycle stages and determine what an agent is allowed to do.

| Level | Name | Stage Range | Permissions |
|-------|------|-------------|-------------|
| `L0` | `concept` | S01-S02 | No execution. Design only. |
| `L1` | `prototype` | S03-S05 | Sandbox execution only. No real data. No real tools. |
| `L2` | `evaluated` | S06-S07 | Sandbox with evaluation data. Judge review required. |
| `L3` | `deployed` | S08-S09 | Canary/staging with real data. Kill switch mandatory. |
| `L4` | `production` | S10-S12 | Full production. Observability mandatory. Human override available. |
| `L5` | `mature` | S13 | Proven production. May serve as baseline for derived agents. |

---

## 5. Governance Invariants

Rules that apply universally. No role, agent, or process may violate these.

### 5.1 Identity

| Rule | Enforcement |
|------|-------------|
| Every agent must have a passport before it can receive tasks. | Registry CI validation rejects unregistered agent IDs. |
| Agent IDs are globally unique and immutable once assigned. | Registry schema enforces uniqueness. Renames create new agents. |
| Every agent must declare an owner (human or team). | Passport schema requires `owners` field. |

### 5.2 Execution

| Rule | Enforcement |
|------|-------------|
| Agents communicate only through the task bus. Direct inter-agent calls are banned. | Runtime plane rejects non-task-bus invocations. |
| Agent state must be externalized. In-process state is ephemeral and unreliable. | Memory contract requires Supabase `ops.*` persistence. |
| Agents must be idempotent. Re-execution of the same task must not produce side effects. | Evaluation suites include idempotency scenarios. |
| Maximum task execution time: 10 minutes. Exceeding triggers timeout and escalation. | Runtime plane enforces hard timeout. |

### 5.3 Safety

| Rule | Enforcement |
|------|-------------|
| Kill switch is mandatory for L3+ agents. | Deployment pipeline rejects L3+ without kill-switch binding. |
| Human override is always available. No agent can lock out human intervention. | Runtime plane exposes manual override endpoint for every agent. |
| Destructive operations require explicit human approval. | Policy engine blocks `DROP`, `DELETE`, `rm -rf`, `--force` patterns without approval token. |
| No policy bypass without audit record. | Policy engine logs all override events to `ops.policy_overrides`. |
| Secrets are never accessible to agent code. Tool bindings resolve secrets via Key Vault at runtime. | Runtime plane injects resolved values; agent process sees opaque references. |

### 5.4 Quality

| Rule | Enforcement |
|------|-------------|
| No production promotion without evaluation evidence. | Stage gate S09->S10 requires `agents/evals/<agent-id>/results/` with passing outcomes. |
| Judge agent sign-off required for L3+ promotions. | Promotion pipeline blocks without judge evaluation record. |
| Maker agents never evaluate their own output. | Evaluation routing rules exclude the producing agent from the judge pool. |
| Evidence must be machine-verifiable. Narrative-only evidence is insufficient. | Gate validators parse structured evaluation results, not prose. |

---

## 6. Promotion Invariants

### 6.1 Record Integrity

- **Promotion records are append-only.** Once a promotion record is written, it is never modified or deleted.
- **Rollback creates a demotion record.** Moving an agent to a lower maturity level produces a new `demotion` record referencing the original promotion. The original promotion record remains intact.
- **Every promotion record contains:** agent ID, from-level, to-level, timestamp, evidence references (file paths), gate results (pass/fail per criterion), approver (human or judge agent ID).

### 6.2 Evidence Requirements

| Promotion | Required Evidence |
|-----------|-------------------|
| L0 -> L1 | Contract schema validates. Blueprint complete. |
| L1 -> L2 | Unit + integration evaluations pass. Sandbox execution log exists. |
| L2 -> L3 | Full evaluation suite passes. Judge agent review record exists. Security review complete. |
| L3 -> L4 | Canary/staging metrics within thresholds. No critical incidents during canary period (minimum 48 hours). |
| L4 -> L5 | 30-day production track record. Zero critical incidents. Coverage >= 80% of declared scenarios. |

### 6.3 Promotion Record Schema

```yaml
schema: ipai.promotion.v1
agent_id: "<kebab-case>"
timestamp: "<ISO8601>"
from_level: "L<n>"
to_level: "L<n+1>"
type: "promotion"          # or "demotion"
evidence:
  - path: "agents/evals/<agent-id>/results/<run-id>.json"
    hash: "<sha256>"
gate_results:
  - gate: "<gate-name>"
    result: "pass"         # or "fail"
    detail: "<one-line>"
approver:
  type: "judge-agent"      # or "human"
  id: "<approver-id>"
reason: "<one-line justification>"
```

---

## 7. Retirement Invariants

### 7.1 Lifecycle Rules

| Rule | Detail |
|------|--------|
| Retirement is a formal lifecycle stage (`S16`). | Agents are never silently removed. |
| Deprecated agents get a 30-day sunset period (`S14` -> `S15`). | Clock starts when `S14` record is created. |
| Task bus stops routing new tasks to agents at `S15` (sunset). | Existing in-flight tasks are allowed to complete. |
| Retirement record is permanent and append-only. | Includes: retirement reason, successor agent ID (if any), final evaluation summary. |
| Retired agent passports are archived, not deleted. | Moved to `agents/passports/retired/`. Remain queryable for audit. |
| Successor agents must be at L2+ before the predecessor enters `S15`. | Prevents premature retirement without a replacement. |

### 7.2 Retirement Record Schema

```yaml
schema: ipai.retirement.v1
agent_id: "<kebab-case>"
timestamp: "<ISO8601>"
reason: "<one-line>"
successor_agent_id: "<kebab-case or null>"
final_stage: "S16"
sunset_start: "<ISO8601>"         # when S14 was entered
sunset_end: "<ISO8601>"           # when S16 was entered (>= sunset_start + 30d)
tasks_drained: true
passport_archived_to: "agents/passports/retired/<agent-id>.yaml"
```

---

## 8. Factory Assembly Line

The end-to-end pipeline for bringing an agent from concept to production.

```
  DEFINE           BUILD            EVALUATE         PROMOTE          DEPLOY           OBSERVE
┌──────────┐   ┌──────────┐   ┌──────────────┐   ┌──────────┐   ┌──────────┐   ┌──────────────┐
│ Blueprint │──>│ Contract │──>│ Eval Suite   │──>│ Stage    │──>│ Runtime  │──>│ Telemetry    │
│ Passport  │   │ Skills   │   │ Sandbox Run  │   │ Gate     │   │ Binding  │   │ Health       │
│ Owner     │   │ Tools    │   │ Judge Review │   │ Evidence │   │ Task Bus │   │ Alerting     │
│           │   │ Policy   │   │              │   │ Record   │   │ Config   │   │              │
└──────────┘   └──────────┘   └──────────────┘   └──────────┘   └──────────┘   └──────────────┘
   S01-S02        S03             S04-S07           S07-S09        S08-S10         S10+
    L0              L1              L2                L3             L4             L4-L5
```

### Stage-to-Artifact Mapping

| Stage | Required Artifacts |
|-------|-------------------|
| S01 | `agents/passports/<id>.yaml` |
| S02 | `agents/foundry/agents/<id>.manifest.yaml` |
| S03 | Agent implementation (skill code, tool bindings) |
| S04 | `agents/evals/<id>/scenarios/*.yaml` |
| S05 | `agents/evals/<id>/integration/*.yaml` |
| S06 | `agents/evals/<id>/results/<run-id>.json` |
| S07 | `agents/evals/<id>/judge-reviews/<run-id>.json` |
| S08 | `agents/promotions/<id>/<timestamp>-L3.yaml` |
| S09 | Staging deployment evidence + metrics |
| S10 | `agents/promotions/<id>/<timestamp>-L4.yaml` |
| S14 | `agents/retirements/<id>/deprecation-notice.yaml` |
| S16 | `agents/retirements/<id>/retirement-record.yaml` |

---

## 9. Agent Passport Schema

The passport is the complete identity document. One file per agent.

```yaml
schema: ipai.passport.v1
agent_id: "<kebab-case>"
name: "<UPPER-KEBAB display name>"
version: "<semver>"
domain: "<erp|devops|data|frontend|platform|finance>"
purpose: "<one-line description>"
owners:
  - "<github-team-or-user>"
current_stage: "S<nn>"
maturity_level: "L<n>"
contract_ref: "agents/foundry/agents/<id>.manifest.yaml"
skills:
  - "agents/skills/<skill-name>/SKILL.md"
tools:
  - "agents/foundry/tools/<tool-name>.manifest.yaml"
policies:
  - "agents/foundry/policies/<policy-name>.policy.yaml"
memory_contract:
  store: "supabase"
  table: "ops.agent_memory"
  retention_days: 90
kill_switch:
  enabled: true                 # mandatory for L3+
  endpoint: "/agents/<id>/kill"
  fallback: "task-bus-drain"
promotion_history:
  - ref: "agents/promotions/<id>/<timestamp>.yaml"
evaluation_history:
  - ref: "agents/evals/<id>/results/<run-id>.json"
created_at: "<ISO8601>"
updated_at: "<ISO8601>"
```

---

## 10. Policy Framework

### 10.1 Policy Types

| Type | Governs | Example |
|------|---------|---------|
| `tool-allowlist` | Which tools an agent may invoke | Finance agents cannot access deployment tools |
| `write-scope` | What data an agent may write | Read-only agents have `write_access: none` |
| `model-routing` | Which LLM backend an agent uses | Production agents use `gpt-4.1`; sandbox uses `gpt-4.1-mini` |
| `escalation` | When an agent must defer to a human | Destructive operations, budget > threshold |
| `rate-limit` | Execution frequency caps | Max 100 tasks/hour per agent |
| `data-boundary` | What data an agent may read | PII-handling agents restricted to specific tables |

### 10.2 Policy Resolution Order

When multiple policies apply to an agent, they resolve in this order (most restrictive wins):

1. Platform-wide policies (this constitution)
2. Domain-level policies (`agents/foundry/policies/agents__policy__<domain>_*.yaml`)
3. Agent-specific policies (declared in passport)
4. Task-level overrides (only with audit record)

---

## 11. Task Bus Contract

### 11.1 Task Message Schema

```yaml
schema: ipai.task.v1
task_id: "<uuid>"
type: "task.<domain>.<action>"
priority: "low|normal|high|critical"
payload: {}                        # typed per task type
source_agent_id: "<kebab-case>"    # or "human"
target_agent_id: "<kebab-case>"    # resolved by router if omitted
correlation_id: "<uuid>"           # groups related tasks
created_at: "<ISO8601>"
timeout_ms: 600000                 # 10 minutes max
idempotency_key: "<string>"        # prevents duplicate execution
```

### 11.2 Routing Rules

| Rule | Detail |
|------|--------|
| Tasks route by `type` to agents that declare that type in their contract. | Agent contract `task_types` field is the routing table. |
| If multiple agents qualify, the highest-maturity agent wins. | L5 > L4 > L3. Ties broken by explicit priority in registry. |
| Tasks for retired agents (`S15`+) are rejected with `AGENT_RETIRED` error. | Source agent receives error and must re-route or escalate. |
| Unroutable tasks escalate to human via notification. | Slack notification + `ops.unroutable_tasks` log entry. |

---

## 12. Observability Contract

Every agent execution must emit:

| Signal | Format | Destination | Retention |
|--------|--------|-------------|-----------|
| **Trace** | OTLP spans | Azure Monitor | 30 days |
| **Metrics** | `agent.<id>.task.{count,duration,error_rate}` | Azure Monitor | 90 days |
| **Logs** | Structured JSON | Azure Monitor + Sentry | 30 days |
| **Evidence** | Evaluation results, promotion records | Git repo (`docs/evidence/`) | Permanent |
| **Health** | Heartbeat + readiness probe | Task bus health endpoint | Real-time |

### Required Trace Attributes

Every span must include: `agent.id`, `task.id`, `task.type`, `correlation.id`, `maturity.level`.

---

## 13. CI Enforcement

The following CI checks run on every PR that touches `agents/`:

| Check | Gate Type | Fails On |
|-------|-----------|----------|
| `agent-registry-validate` | Hard | Invalid passport schema, duplicate IDs, missing required fields |
| `agent-contract-validate` | Hard | Contract schema violations, undeclared tool bindings |
| `agent-policy-lint` | Hard | Policy conflicts, missing escalation rules for L3+ |
| `agent-eval-required` | Hard | Promotion PR without evaluation evidence |
| `agent-naming-lint` | Hard | Non-conforming agent IDs, stage IDs, or task types |
| `agent-retirement-check` | Soft | Deprecated agents past 30-day sunset without retirement record |

---

## 14. Compatibility

### Relationship to Existing Artifacts

| Existing Artifact | Relationship to This Constitution |
|-------------------|-----------------------------------|
| `agents/foundry/agentic-sdlc-constitution.md` | Predecessor. This document supersedes it for agent lifecycle governance. The SDLC constitution remains authoritative for coding agent behavior rules (sections 3-9 of that document). |
| `agents/registry/agents.yaml` | Continues as the registry SSOT. Must add `current_stage` and `maturity_level` fields per this constitution. |
| `agents/templates/builder-factory/agent-blueprint.yaml` | Continues as the blueprint template. Passport generation derives from blueprints. |
| `ssot/ai/agents.yaml` | Foundry-specific agent definitions. Remains authoritative for Azure Foundry runtime configuration. This constitution governs lifecycle; that file governs runtime binding. |
| `packages/agents/` | Implementation target for the control plane components defined here. |
| `packages/taskbus/` | Implementation target for the task bus contract defined here. |

### Migration Path

Existing agents (6 registered in `agents/registry/agents.yaml`) must be assigned:
1. A passport (section 9 schema) within 14 days of this constitution's adoption.
2. A maturity level based on current deployment state.
3. A stage assignment reflecting actual lifecycle position.

No existing agent is grandfathered into production (L4) without evaluation evidence. Existing production agents receive a 30-day grace period to produce retroactive evaluation evidence or be demoted to L2.

---

## Canonicality Invariant

The following rules ensure cross-document consistency across the Agent Factory bundle.

| Rule | Detail |
|------|--------|
| **Stage SSOT** | `ssot/agent-platform/stage_gates.yaml` is the canonical source for stage IDs (S01-S16) and their ordering. All other documents derive stage references from this file. |
| **Maturity stage bounds** | `ssot/agent-platform/agent_maturity_model.yaml` must only reference stages defined in the canonical stage set. The `allowed_stages` for each maturity level must match the constitution section 4.4 mapping exactly. |
| **Task decomposition derivation** | Azure Boards decomposition must derive from `spec/agent-factory/tasks.md` and `ssot/agent-platform/boards_mapping.yaml`. Ad-hoc board items without spec traceability are not authoritative. |
| **Atomic cross-reference updates** | Any pull request that changes stage IDs, maturity level caps, task-bus states, or artifact names must update all dependent spec and SSOT references in the same change. Partial updates that leave cross-document drift are rejected by CI. |

---

*Schema version: 1.0*
*Effective date: 2026-03-19*
*Owner: @Insightpulseai-net/platform*
*Review cadence: Quarterly or on any structural change to the agent platform*
