# Diva Goals -- Implementation Plan

> Architecture, delivery phases, and technical design for the Diva Goals control plane.

---

## Architectural Position

Diva Goals is a **control plane OVER existing authority systems**. It does not replace any source system. It reads from them, derives status, detects anomalies, surfaces capability gaps, and provides structured review surfaces.

```
                    ┌─────────────────────────────────────┐
                    │           DIVA GOALS                 │
                    │  (Orchestration + Review + Readiness) │
                    └──────────┬──────────────────────────┘
                               │
      ┌────────────────────────┼──────────────────────────┐
      │                        │                           │
┌─────▼─────┐          ┌──────▼──────┐           ┌────────▼────────┐
│  Strategy  │          │  Execution  │           │   Capability    │
│  Sources   │          │  Sources    │           │   Sources       │
├────────────┤          ├─────────────┤           ├─────────────────┤
│ Azure Bds  │          │ GitHub      │           │ HR/L&D Systems  │
│ (Goals,    │          │ (PRs, Code) │           │ (People Skills) │
│  KRs,      │          │             │           │                 │
│  Initvs)   │          │ Azure DevOps│           │ Agent Registry  │
│            │          │ (Pipelines) │           │ (Skills, Evals) │
│ Spec Kit   │          │             │           │                 │
│ (spec/)    │          │ Eval Frmwk  │           │ Foundry Evals   │
│            │          │ (evals/)    │           │ (Scores, Gates) │
│            │          │             │           │                 │
│            │          │ Runtime     │           │ Learning Records│
│            │          │ (Metrics)   │           │ (Evidence)      │
└────────────┘          └─────────────┘           └─────────────────┘
```

### Key Architectural Decisions

1. **Diva Goals owns orchestration, review, and readiness -- not source data.** It maintains references (IDs, URIs) and derived state, never copies of source records.
2. **Event-driven ingestion for delivery events** (PR merged, pipeline completed, eval scored). Batch ingestion for runtime metrics (daily/hourly).
3. **Databricks as the persistence layer** for the goal graph, evidence index, capability model, and review records. Delta tables with Unity Catalog governance.
4. **Power BI as the primary read surface** for dashboards and portfolio views. Custom UI only for interactive review ceremonies.
5. **Existing platform components** (Foundry, Azure DevOps, GitHub Actions) are used for agent orchestration -- Diva Goals observes and reviews, it does not orchestrate agent execution.
6. **Microsoft Agent Framework for Diva Goals' own agent topology** -- orchestrator, evidence collectors, review synthesis, judges, and approval gates are modeled as Agent Framework workflow graphs.
7. **Foundry Agent Service for hosted agent runtime** -- Diva Goals agents run as Foundry-hosted agents with project connections to source systems.
8. **Foundry IQ / Azure AI Search for knowledge bases** -- domain knowledge accessed via MCP `knowledge_base_retrieve`.
9. **Agent Skills for domain logic** -- each Diva Goals agent capability is packaged as a skill with defined input/output contracts.
10. **Foundry tracing, evaluation, and monitoring** for all Diva Goals agent operations.

---

## 5 Logical Components

### Component 1: Strategy Graph

**Purpose**: Model the top of the goal hierarchy.

**Entities**:
- `objective`: Strategic goal. Source: Azure Boards Epic. Fields: id, title, description, owner, time_horizon, status (derived), evidence_summary, capability_requirements.
- `key_result`: Measurable outcome. Source: Azure Boards Feature. Fields: id, title, metric_source, target_value, current_value, threshold, status (derived), measurement_cadence, capability_requirements.
- `initiative`: Delivery vehicle. Source: Azure Boards User Story. Fields: id, title, owner, spec_ref, status (derived), linked_work_items, capability_requirements.

**Relationships**:
- objective -> key_result (1:N)
- key_result -> initiative (1:N)
- initiative -> spec_bundle (1:1 or 1:0)
- objective | key_result | initiative -> capability_requirement (1:N)

**Storage**: `catalog.diva_goals.strategy_graph` (Delta table, Databricks Unity Catalog)

**Ingestion**: Azure Boards API (batch, daily sync + webhook for state changes)

### Component 2: Execution Graph

**Purpose**: Map the agentic SDLC delivery chain.

**Entities**:
- `spec_bundle`: Spec definition. Source: `spec/` directory. Fields: id, slug, path, constitution_hash, prd_hash, plan_hash, tasks_hash, completeness_score.
- `work_item`: Granular task. Source: Azure Boards Task. Fields: id, title, assignee (human or agent), status (derived), spec_ref, evidence_links.
- `agent_run`: Agent invocation record. Source: CI/CD logs, Foundry logs. Fields: id, agent_identity, agent_type (maker/judge/ops), run_timestamp, input_context, output_artifacts, confidence_score, duration_seconds.
- `pull_request`: Code change. Source: GitHub. Fields: id, url, author (human or agent), status, linked_work_items, review_status, merge_timestamp.
- `pipeline_run`: Build/test/deploy. Source: Azure DevOps, GitHub Actions. Fields: id, pipeline_name, trigger, status, duration, artifact_links.
- `eval_gate`: Quality evaluation. Source: Eval framework. Fields: id, eval_name, target_score, actual_score, pass (boolean), linked_release.
- `release`: Deployment event. Source: GitHub Release, ACA deployment. Fields: id, version, environment, timestamp, artifact_links, eval_gates_passed.

**Relationships**:
- initiative -> spec_bundle (1:1)
- spec_bundle -> work_item (1:N)
- work_item -> agent_run (1:N)
- work_item -> pull_request (1:N)
- pull_request -> pipeline_run (1:N)
- pipeline_run -> eval_gate (1:N)
- eval_gate -> release (N:1)

**Storage**: `catalog.diva_goals.execution_graph` (Delta tables)

**Ingestion**: GitHub API (webhooks for PRs), Azure DevOps API (webhooks for pipelines), file system scan for spec bundles.

### Component 3: Human Capability Graph

**Purpose**: Model human capability requirements, current state, and development paths.

**Entities**:
- `role_family`: Organizational role grouping. Fields: id, name, description, proficiency_levels, required_capabilities.
- `capability`: A discrete human skill or competency. Fields: id, name, domain, description, assessment_method.
- `proficiency_level`: A rung on the proficiency ladder. Fields: id, capability_id, level (1-5), description, evidence_requirements.
- `capability_requirement`: Link from strategic entity to required capability. Fields: id, source_entity_type, source_entity_id, capability_id, required_level, current_assessed_level, gap_score.
- `learning_path`: Development plan to close a gap. Fields: id, capability_requirement_id, interventions, target_date, status, evidence_links.
- `capability_assessment`: Evidence of current proficiency. Fields: id, person_id, capability_id, assessed_level, evidence_uri, assessment_date, assessor.

**Relationships**:
- role_family -> capability (N:M)
- objective | key_result | initiative -> capability_requirement (1:N)
- capability_requirement -> learning_path (1:0..1)
- capability -> capability_assessment (1:N per person)

**Storage**: `catalog.diva_goals.human_capability_graph` (Delta tables)

**Ingestion**: Manual YAML definitions (role families, capabilities), L&D system integration for assessments and learning records.

### Component 4: Agent Capability Graph

**Purpose**: Model agent capability, readiness tiers, skill packs, and governance.

**Entities**:
- `agent_role`: Registered agent role. Fields: id, name, type (maker/judge/ops/synthesis), capability_declaration, autonomy_tier (supervised/semi_autonomous/autonomous), active, registration_date.
- `skill_pack`: Packaged agent capability. Fields: id, name, agent_role_id, description, tools, knowledge_bases, eval_suite_id, version.
- `agent_eval_record`: Evaluation result for an agent. Fields: id, agent_role_id, eval_suite_id, scores (task_completion, task_adherence, intent_resolution, tool_call_accuracy, groundedness), pass, timestamp.
- `agent_participation`: Link between agent and work. Fields: agent_id, entity_type (work_item/pr/eval_gate), entity_id, role (producer/reviewer/evaluator), confidence_score, timestamp.
- `approval_record`: Human approval of agent output. Fields: id, agent_run_id, approver (human), decision (approve/reject/request_changes), justification, timestamp.
- `autonomy_change`: Tier promotion or demotion record. Fields: id, agent_role_id, from_tier, to_tier, trigger (eval_pass/eval_fail/manual), evidence_uri, approved_by, timestamp.

**Relationships**:
- agent_role -> skill_pack (1:N)
- agent_role -> agent_eval_record (1:N)
- agent_role -> agent_participation (1:N)
- agent_run -> approval_record (1:0..1)
- agent_role -> autonomy_change (1:N)

**Storage**: `catalog.diva_goals.agent_capability_graph` (Delta tables)

**Ingestion**: Agent registry YAML definitions, Foundry eval pipeline results, CI/CD metadata.

### Component 5: Review Engine

**Purpose**: Structured review ceremonies with evidence-backed decisions.

**Entities**:
- `review_session`: A review ceremony instance. Fields: id, type (execution/portfolio/capability/agent_readiness/exception), cadence, scheduled_date, actual_date, status (scheduled/in_progress/completed), facilitator.
- `review_input`: Pre-populated evidence for a review. Fields: id, review_session_id, input_type (progress_summary/drift_flags/orphan_report/stale_evidence/agent_output_pending/capability_gap_report/agent_readiness_report), content (structured JSON).
- `review_decision`: Decision made during review. Fields: id, review_session_id, entity_ref (goal/KR/initiative/capability/agent_role), decision_type (approve/defer/escalate/close/override), justification, decided_by.
- `review_action_item`: Follow-up action. Fields: id, review_session_id, assignee, description, due_date, status, linked_entity.

**Relationships**:
- review_session -> review_input (1:N)
- review_session -> review_decision (1:N)
- review_session -> review_action_item (1:N)

**Storage**: `catalog.diva_goals.review_engine` (Delta tables)

**Ingestion**: Generated by Diva Goals itself during review ceremonies.

---

## Agent Topology (Diva Goals Internal Agents)

Diva Goals uses the Microsoft Agent Framework to orchestrate its own internal agents:

### Orchestrator Agent

The top-level agent that manages workflow graphs. Built on Microsoft Agent Framework SDK. Responsibilities:
- Route incoming events to the correct workflow
- Manage sequential and parallel execution of sub-agents
- Enforce approval checkpoints (human-in-the-loop gates)
- Emit workflow events for tracing

### Evidence Collector Agents

Specialized agents that ingest from source systems. One per integration:
- Azure Boards collector
- GitHub collector
- Azure DevOps Pipelines collector
- Runtime metrics collector (App Insights, Databricks)
- L&D/learning records collector
- Foundry eval results collector

### Review Synthesis Agent

Prepares review packs for human ceremonies. Responsibilities:
- Aggregate evidence across graph entities
- Compute drift flags, orphan reports, staleness summaries
- Draft capability gap summaries
- Draft agent readiness summaries
- Produce structured JSON review inputs

### Judge Agents

Evaluate quality of evidence and readiness claims. Responsibilities:
- Validate evidence chain completeness (no broken links)
- Score capability readiness claims against evidence
- Evaluate agent eval scores against promotion thresholds
- Flag anomalies (e.g., readiness claimed but evidence insufficient)

### Human Approval Gate

Not an agent -- a checkpoint in the workflow graph. Pauses execution until a human approves or rejects. Emits approval records to the audit trail.

---

## 4 Core Workflows

### Workflow 1: Goal Status Synthesis

**Trigger**: Source system event (Boards state change, PR merged, pipeline completed, metric updated)
**Flow**: Event -> Evidence Collector -> Graph Update -> Derived Status Computation -> Drift Check -> Notification (if drift detected)
**Output**: Updated entity status in the goal graph, drift flags if applicable

### Workflow 2: Review Pack Generation

**Trigger**: Scheduled (before review ceremony) or on-demand
**Flow**: Review Synthesis Agent -> Aggregate evidence -> Compute summaries -> Draft review inputs -> Store as review_input records
**Output**: Structured review pack ready for human review ceremony

### Workflow 3: Capability/Readiness Review

**Trigger**: Quarterly cadence or on-demand
**Flow**: Capability data aggregation -> Gap scoring -> Readiness assessment -> Learning effectiveness measurement -> Draft capability review pack
**Output**: Capability gap report, readiness heat map, learning effectiveness summary

### Workflow 4: Drift/Orphan Detection

**Trigger**: Continuous (event-driven) + scheduled (daily full scan)
**Flow**: Graph scan -> Status vs. evidence comparison -> Orphan link check -> Staleness check -> Flag generation
**Output**: Drift flags, orphan flags, stale evidence flags -- all surfaced in review engine

---

## Review Cadences

| Review | Cadence | Scope | Key Inputs | Key Outputs |
|--------|---------|-------|------------|-------------|
| **Execution Review** | Weekly | Initiative progress, blocked items, pending reviews | Drift flags, agent output pending, action items from last review | Decisions, new action items, approvals |
| **Portfolio Review** | Monthly | Goal/KR progress, strategic alignment, resource allocation | Coverage gaps, exception log, portfolio health score | Strategic adjustments, priority changes |
| **Capability/Readiness Review** | Quarterly | Human capability gaps, learning effectiveness | Capability gap report, readiness heat map, learning ROI | Capability investment decisions, learning plan adjustments |
| **Agent Readiness Review** | Quarterly | Agent eval scores, autonomy tier appropriateness | Agent eval summary, autonomy tier recommendations | Tier promotions/demotions, skill-pack investment decisions |
| **Learning Effectiveness Review** | Quarterly | L&D program outcomes, capability gap closure rate | Learning completion data, outcome linkage analysis | Program design changes, resource reallocation |
| **Exception Review** | On-demand | Specific drift, eval failure, stale evidence, escalation | Exception-specific evidence | Resolution, escalation, or deferral decision |

---

## Policy and Security Model

### Human Approval Requirements

| Action | Requires Human Approval | Justification |
|--------|------------------------|---------------|
| Set goal status to "complete" | Yes | Material status transition |
| Set KR status to "achieved" | Yes | Material status transition |
| Set initiative status to "complete" | Yes | Material status transition |
| Override derived status | Yes | Evidence override requires justification |
| Approve agent PR for merge | Yes | Code change authority |
| Pass eval gate (release decision) | Yes | Release authority |
| Upgrade agent autonomy tier | Yes | Governance authority |
| Certify human capability readiness | Yes | People authority |
| Flag drift/orphan/stale | No (automated) | Detection is non-destructive |
| Propose status change | No (agent may propose) | Proposal requires human approval to take effect |
| Create review input summary | No (agent may generate) | Read-only preparation |

### Policy Rules

1. **No readiness signal without evidence.** Capability readiness (human or agent) requires linked assessment or eval evidence. Override requires justification in the audit trail.
2. **No agent autonomy upgrade without eval.** Autonomy tier promotion requires passing scores on the target-tier eval suite. Manual promotion is blocked.
3. **Capability gaps surface in reviews.** When a strategic priority has an unmet capability requirement, it appears as a blocker in the relevant review ceremony.
4. **Stale evidence degrades status.** Evidence past its freshness policy moves the entity to "unverified" status.
5. **Override audit is mandatory.** Every manual override is logged with: who, when, why, what evidence was overridden.

### Agent Audit Requirements

Every agent action must log:
- Agent identity (name, type, version)
- Action performed (what was proposed/created/evaluated)
- Evidence cited (URIs to source system artifacts)
- Confidence score (0.0-1.0)
- Outcome (approved/rejected/pending)
- Timestamp (UTC)

Audit logs are append-only. Retention: indefinite for production, 90 days for dev.

### Evidence Provenance

Every evidence reference must include:
- Source system (e.g., "github", "azure-devops", "app-insights", "foundry-eval", "lms")
- Entity ID in source system
- Timestamp of evidence capture
- Freshness policy (how long before stale)
- Current staleness status (fresh/stale)

### Stale Evidence Policy

| Evidence Type | Freshness Window | Action When Stale |
|---------------|-----------------|-------------------|
| Pipeline run result | 7 days | Flag work item as "unverified" |
| Eval gate score | 14 days | Flag release as "unverified" |
| Runtime metric | 24 hours | Flag KR as "unverified" |
| PR status | 3 days | Flag work item as "needs attention" |
| Azure Boards sync | 1 day | Flag affected goals as "sync pending" |
| Capability assessment | 90 days | Flag capability readiness as "assessment stale" |
| Agent eval score | 30 days | Flag agent autonomy tier as "re-eval needed" |

---

## Tech Stack Mapping

| Diva Goals Component | Platform Component | Usage |
|---------------------|-------------------|-------|
| Graph persistence | Databricks Unity Catalog | Delta tables for all graph entities |
| Evidence ingestion | Azure Functions + Event Grid | Webhook receivers for GitHub, Azure DevOps |
| Batch ingestion | Databricks Jobs | Scheduled sync for Azure Boards, runtime metrics |
| Read surface | Power BI | Dashboards, drill-through reports |
| Review ceremony UI | Custom web app (Azure Container Apps) | Interactive review sessions |
| Agent orchestration (internal) | Microsoft Agent Framework SDK | Diva Goals workflow graphs |
| Agent runtime (internal) | Azure AI Foundry Agent Service | Hosted agent execution |
| Agent knowledge | Foundry IQ / Azure AI Search via MCP | Domain knowledge for agents |
| Agent skills | Agent Skills packages | Domain logic for each agent capability |
| Agent evaluation | Foundry evaluators | task_completion, task_adherence, intent_resolution, tool_call_accuracy |
| Agent observability | Foundry tracing + Azure Monitor | Telemetry for all agent operations |
| Secrets | Azure Key Vault | All credentials for source system APIs |
| Identity | Microsoft Entra ID | User authentication for review ceremonies |
| CI/CD | Azure DevOps Pipelines | Diva Goals own deployment pipeline |

---

## Integration Contracts

### Azure Boards -> Diva Goals

- **API**: Azure DevOps REST API v7.0
- **Auth**: Managed Identity -> Azure DevOps PAT (Key Vault)
- **Sync**: Daily batch + webhook for state changes
- **Entities**: Epics -> objectives, Features -> key_results, User Stories -> initiatives, Tasks -> work_items

### GitHub -> Diva Goals

- **API**: GitHub REST API v3 + Webhooks
- **Auth**: GitHub App installation token (Key Vault)
- **Sync**: Webhook-driven (PR events, push events)
- **Entities**: PRs -> pull_request, Actions runs -> pipeline_run, Releases -> release

### Azure DevOps Pipelines -> Diva Goals

- **API**: Azure DevOps REST API v7.0
- **Auth**: Managed Identity -> Azure DevOps PAT (Key Vault)
- **Sync**: Webhook-driven (pipeline completion events)
- **Entities**: Pipeline runs -> pipeline_run

### Application Insights / Databricks -> Diva Goals

- **API**: Application Insights REST API, Databricks SQL
- **Auth**: Managed Identity
- **Sync**: Batch (hourly for App Insights, daily for Databricks metrics)
- **Entities**: Metrics -> runtime_metric (evidence for KRs)

### Spec Kit -> Diva Goals

- **Source**: Local file system scan of `spec/` directory
- **Sync**: Git hook or CI pipeline trigger on spec file changes
- **Entities**: Spec directories -> spec_bundle, task files -> work_item references

### Foundry Eval Pipeline -> Diva Goals

- **API**: Foundry Agent Service API
- **Auth**: Managed Identity
- **Sync**: Event-driven (eval completion)
- **Entities**: Eval results -> agent_eval_record, eval scores -> eval_gate

### L&D / Learning Records -> Diva Goals

- **Source**: L&D system export (batch CSV/JSON) or API
- **Auth**: Service account (Key Vault)
- **Sync**: Batch (daily)
- **Entities**: Learning completions -> learning evidence, assessments -> capability_assessment

---

*Product: Diva Goals*
*Version: 2.0*
*Last updated: 2026-03-23*
