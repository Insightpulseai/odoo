# Diva Goals -- Implementation Plan

> Architecture, delivery phases, and technical design for the Diva Goals control plane.

---

## Architectural Position

Diva Goals is a **control plane OVER existing authority systems**. It does not replace any source system. It reads from them, derives status, detects anomalies, and provides structured review surfaces.

```
                    ┌─────────────────────────────┐
                    │        DIVA GOALS            │
                    │   (Orchestration + Review)   │
                    └──────────┬──────────────────┘
                               │
          ┌────────────────────┼────────────────────┐
          │                    │                     │
    ┌─────▼─────┐     ┌───────▼───────┐    ┌───────▼───────┐
    │  Strategy  │     │  Execution    │    │   Runtime     │
    │  Sources   │     │  Sources      │    │   Sources     │
    ├────────────┤     ├───────────────┤    ├───────────────┤
    │ Azure Bds  │     │ GitHub        │    │ App Insights  │
    │ (Goals,    │     │ (PRs, Code)   │    │ (Metrics)     │
    │  KRs,      │     │               │    │               │
    │  Initvs)   │     │ Azure DevOps  │    │ Databricks    │
    │            │     │ (Pipelines)   │    │ (Lakehouse)   │
    │ Spec Kit   │     │               │    │               │
    │ (spec/)    │     │ Eval Frmwk    │    │ Power BI      │
    │            │     │ (evals/)      │    │ (Dashboards)  │
    └────────────┘     └───────────────┘    └───────────────┘
```

### Key Architectural Decisions

1. **Diva Goals owns orchestration and review, not source data.** It maintains references (IDs, URIs) and derived state, never copies of source records.
2. **Event-driven ingestion for delivery events** (PR merged, pipeline completed, eval scored). Batch ingestion for runtime metrics (daily/hourly).
3. **Databricks as the persistence layer** for the goal graph, evidence index, and review records. Delta tables with Unity Catalog governance.
4. **Power BI as the primary read surface** for dashboards and portfolio views. Custom UI only for interactive review ceremonies.
5. **Existing platform components** (Foundry, Azure DevOps, GitHub Actions) are used for agent orchestration -- Diva Goals observes and reviews, it does not orchestrate agent execution.

---

## 4 Logical Layers

### Layer 1: Strategy Graph

**Purpose**: Model the top of the goal hierarchy.

**Entities**:
- `objective`: Strategic goal. Source: Azure Boards Epic. Fields: id, title, description, owner, time_horizon, status (derived), evidence_summary.
- `key_result`: Measurable outcome. Source: Azure Boards Feature. Fields: id, title, metric_source, target_value, current_value, threshold, status (derived), measurement_cadence.
- `initiative`: Delivery vehicle. Source: Azure Boards User Story. Fields: id, title, owner, spec_ref, status (derived), linked_work_items.

**Relationships**:
- objective -> key_result (1:N)
- key_result -> initiative (1:N)
- initiative -> spec_bundle (1:1 or 1:0)

**Storage**: `catalog.diva_goals.strategy_graph` (Delta table, Databricks Unity Catalog)

**Ingestion**: Azure Boards API (batch, daily sync + webhook for state changes)

### Layer 2: Execution Graph

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

### Layer 3: Agent Graph

**Purpose**: Model agent participation as first-class entities.

**Entities**:
- `agent_identity`: Registered agent. Fields: id, name, type (maker/judge/ops), capability_declaration, active (boolean), registration_date.
- `agent_participation`: Link between agent and work. Fields: agent_id, entity_type (work_item/pr/eval_gate), entity_id, role (producer/reviewer/evaluator), confidence_score, timestamp.
- `approval_record`: Human approval of agent output. Fields: id, agent_run_id, approver (human), decision (approve/reject/request_changes), justification, timestamp.

**Relationships**:
- agent_identity -> agent_participation (1:N)
- agent_run -> approval_record (1:0..1)
- agent_participation -> work_item | pull_request | eval_gate (polymorphic link)

**Storage**: `catalog.diva_goals.agent_graph` (Delta tables)

**Ingestion**: Derived from execution graph + CI/CD metadata.

### Layer 4: Review Engine

**Purpose**: Structured review ceremonies with evidence-backed decisions.

**Entities**:
- `review_session`: A review ceremony instance. Fields: id, type (execution/portfolio/exception), cadence, scheduled_date, actual_date, status (scheduled/in_progress/completed), facilitator.
- `review_input`: Pre-populated evidence for a review. Fields: id, review_session_id, input_type (progress_summary/drift_flags/orphan_report/stale_evidence/agent_output_pending), content (structured JSON).
- `review_decision`: Decision made during review. Fields: id, review_session_id, entity_ref (goal/KR/initiative), decision_type (approve/defer/escalate/close/override), justification, decided_by.
- `review_action_item`: Follow-up action. Fields: id, review_session_id, assignee, description, due_date, status, linked_entity.

**Relationships**:
- review_session -> review_input (1:N)
- review_session -> review_decision (1:N)
- review_session -> review_action_item (1:N)

**Storage**: `catalog.diva_goals.review_engine` (Delta tables)

**Ingestion**: Generated by Diva Goals itself during review ceremonies.

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
| Flag drift/orphan/stale | No (automated) | Detection is non-destructive |
| Propose status change | No (agent may propose) | Proposal requires human approval to take effect |
| Create review input summary | No (agent may generate) | Read-only preparation |

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
- Source system (e.g., "github", "azure-devops", "app-insights")
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

---

## 5 Delivery Phases

### Phase 1: Core Strategy Graph (Weeks 1-3)

**Objective**: Import goals, KRs, and initiatives from Azure Boards. Establish the strategy graph with derived status.

**Deliverables**:
1. Azure Boards API integration (read Epics, Features, User Stories)
2. Strategy graph schema in Databricks (`catalog.diva_goals.strategy_graph`)
3. KR measurement source definitions
4. Initiative-to-spec linkage (scan `spec/` directory, match to Azure Boards items)
5. Basic derived status computation (goal progress = KR completion percentage)
6. Power BI dashboard: strategy graph overview

**Exit criteria**: All active Azure Boards epics/features visible in strategy graph. Derived status matches manual calculation.

### Phase 2: SDLC Evidence Chain (Weeks 4-6)

**Objective**: Ingest execution artifacts (PRs, pipelines, evals) and compute derived status through the delivery chain.

**Deliverables**:
1. GitHub API integration (webhooks for PR events)
2. Azure DevOps API integration (webhooks for pipeline events)
3. Spec bundle scanner (parse `spec/` directory, compute completeness)
4. Execution graph schema in Databricks (`catalog.diva_goals.execution_graph`)
5. Derived status through chain: spec -> work items -> PRs -> pipelines
6. Staleness detection for all evidence types
7. Drill-through Power BI report: goal -> evidence chain

**Exit criteria**: For any initiative, drill from goal to pipeline run with evidence links. Stale evidence flagged within 1 hour.

### Phase 3: Agent Participation (Weeks 7-9)

**Objective**: Model agent identity, runs, and participation as first-class graph entities.

**Deliverables**:
1. Agent identity registry (`catalog.diva_goals.agent_graph.agent_identity`)
2. Agent run ingestion from CI/CD logs and Foundry metadata
3. Confidence scoring model (0.0-1.0 with routing thresholds)
4. Maker/judge role attribution on work items and PRs
5. Approval workflow for agent outputs (human approval required above work-item level)
6. Agent participation dashboard in Power BI

**Exit criteria**: All agent runs from past 30 days visible in graph. Confidence scores computed. Approval records linked.

### Phase 4: Review Engine (Weeks 10-12)

**Objective**: Build structured review ceremonies with evidence-backed inputs and decision outputs.

**Deliverables**:
1. Execution review template (weekly cadence)
2. Portfolio review template (monthly cadence)
3. Exception review trigger (drift, eval failure, stale evidence)
4. Drift detection engine (status vs. evidence inconsistency)
5. Orphan detection engine (goals without execution, execution without goals)
6. Review session persistence and decision tracking
7. Agent-assisted review preparation (pre-populate evidence summaries)

**Exit criteria**: One full execution review cycle completed with structured output. Drift and orphan reports generated automatically.

### Phase 5: Governance Automation (Weeks 13-16)

**Objective**: Automate policy enforcement, audit, and compliance.

**Deliverables**:
1. Stale evidence auto-flagging with configurable policies
2. Override audit trail (every manual override logged with justification)
3. Export/snapshot for compliance reporting
4. Policy gates (block status transitions without required evidence)
5. Integration with Azure DevOps Boards for backlog priority signals
6. Governance dashboard in Power BI

**Exit criteria**: All policy flags automated. Override audit complete. Compliance export functional.

---

## Tech Stack Mapping

| Diva Goals Component | Platform Component | Usage |
|---------------------|-------------------|-------|
| Graph persistence | Databricks Unity Catalog | Delta tables for all graph entities |
| Evidence ingestion | Azure Functions + Event Grid | Webhook receivers for GitHub, Azure DevOps |
| Batch ingestion | Databricks Jobs | Scheduled sync for Azure Boards, runtime metrics |
| Read surface | Power BI | Dashboards, drill-through reports |
| Review ceremony UI | Custom web app (Azure Container Apps) | Interactive review sessions |
| Agent orchestration | AI Foundry + GitHub Actions | Existing agent runtime (Diva Goals observes, doesn't orchestrate) |
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

---

*Product: Diva Goals*
*Version: 1.0*
*Last updated: 2026-03-23*
