# Diva Goals -- Task Breakdown

> Delivery tasks organized in 11 tracks aligned to the implementation plan.

---

## Track A: Product Definition

> Establish naming, doctrine, schemas, and agent contracts.

### A1: Product Identity and Naming

- [x] Rename `spec/strategy-control-plane/` to `spec/diva-goals/`
- [x] Rewrite `constitution.md` with Diva Goals identity and 10 invariants
- [x] Rewrite `prd.md` with full product requirements including capability axis
- [x] Rewrite `plan.md` with architecture, Agent Framework topology, and delivery phases
- [x] Rewrite `tasks.md` with 11-track task breakdown
- [x] Create `docs/architecture/DIVA_GOALS_TARGET_STATE.md`
- [x] Create `ssot/platform/diva_goals.yaml` with product metadata
- [ ] Update `ssot/governance/planning_system_index.yaml` to reference Diva Goals

### A2: Strategy Graph Schema

- [ ] Define `objective` entity schema (fields, types, constraints, capability_requirements)
- [ ] Define `key_result` entity schema with measurement source binding
- [ ] Define `initiative` entity schema with spec linkage and capability requirements
- [ ] Define relationship model (objective -> KR -> initiative -> spec -> capability_requirement)
- [ ] Document schema in `docs/architecture/DIVA_GOALS_SCHEMA.md`
- [ ] Create Delta table DDL for `catalog.diva_goals.strategy_graph`

### A3: Execution Graph Schema

- [ ] Define `spec_bundle` entity schema (hash-based completeness)
- [ ] Define `work_item` entity schema with agent/human assignee
- [ ] Define `agent_run` entity schema with confidence scoring
- [ ] Define `pull_request` entity schema with review status
- [ ] Define `pipeline_run` entity schema with artifact links
- [ ] Define `eval_gate` entity schema with threshold model
- [ ] Define `release` entity schema with environment binding
- [ ] Document relationship chain: spec -> work_item -> agent_run -> PR -> pipeline -> eval -> release
- [ ] Create Delta table DDL for `catalog.diva_goals.execution_graph`

### A4: Agent Identity Schema

- [ ] Define `agent_identity` entity schema (name, type, capabilities)
- [ ] Define `agent_participation` polymorphic link schema
- [ ] Define `approval_record` entity schema
- [ ] Define confidence scoring model (thresholds for auto-approve, human-review, reject)
- [ ] Document agent contracts in `agents/contracts/diva_goals_agent_contract.md`
- [ ] Create Delta table DDL for `catalog.diva_goals.agent_graph`

### A5: Review Engine Schema

- [ ] Define `review_session` entity schema (type, cadence, status -- including capability and agent_readiness types)
- [ ] Define `review_input` entity schema (structured JSON content types including capability_gap_report and agent_readiness_report)
- [ ] Define `review_decision` entity schema (decision types, justification)
- [ ] Define `review_action_item` entity schema
- [ ] Document review ceremony templates in `docs/operations/DIVA_GOALS_REVIEW_CEREMONIES.md`
- [ ] Create Delta table DDL for `catalog.diva_goals.review_engine`

---

## Track B: Evidence Model

> Map source system entities to Diva Goals evidence references.

### B1: Azure Boards Integration

- [ ] Implement Azure Boards API client (Epics, Features, User Stories, Tasks)
- [ ] Map Epic -> objective, Feature -> key_result, User Story -> initiative, Task -> work_item
- [ ] Build daily batch sync job (Databricks notebook: `ingest_azure_boards.py`)
- [ ] Implement webhook receiver for state change events (Azure Function)
- [ ] Build field mapping configuration (which Boards fields map to which Diva Goals fields)
- [ ] Handle multi-project sync (if goals span multiple Azure DevOps projects)
- [ ] Write integration tests with mock Boards API responses
- [ ] Document sync contract in `agents/contracts/azure_boards_sync_contract.md`

### B2: Spec Kit Integration

- [ ] Build spec directory scanner (parse `spec/*/` for constitution, prd, plan, tasks)
- [ ] Compute spec completeness score (presence and hash of each file)
- [ ] Link spec bundles to initiatives via naming convention or explicit mapping
- [ ] Build task extraction from `tasks.md` (parse checkbox items as work item candidates)
- [ ] Trigger on git push to `spec/` paths (GitHub Actions workflow or webhook)
- [ ] Write tests for spec parsing with edge cases (missing files, malformed markdown)
- [ ] Document spec-to-goal mapping rules

### B3: GitHub Integration

- [ ] Implement GitHub webhook receiver (PR opened, merged, closed; Actions run completed; Release published)
- [ ] Map PR to work_items via commit message conventions or linked issues
- [ ] Map Actions runs to pipeline_run entities
- [ ] Map Releases to release entities
- [ ] Extract author identity (human vs. agent via bot username detection)
- [ ] Build PR-to-spec traceability (PR references spec slug in description or branch name)
- [ ] Write integration tests with mock GitHub webhook payloads
- [ ] Document GitHub evidence contract

### B4: CI/CD Pipeline Integration

- [ ] Implement Azure DevOps pipeline webhook receiver
- [ ] Map pipeline runs to pipeline_run entities
- [ ] Extract pipeline artifacts and link to evidence
- [ ] Map pipeline stages to granular status (build passed, test passed, deploy passed)
- [ ] Detect eval gate stages within pipelines (stages with eval/benchmark in name)
- [ ] Write integration tests with mock pipeline event payloads
- [ ] Document pipeline evidence contract

### B5: Runtime Evidence Integration

- [ ] Implement Application Insights metric reader (batch, hourly)
- [ ] Implement Databricks SQL reader for lakehouse metrics (batch, daily)
- [ ] Map runtime metrics to KR measurement sources
- [ ] Compute KR current_value from metric time series
- [ ] Implement freshness detection (metric age vs. freshness policy)
- [ ] Write integration tests with sample metric data
- [ ] Document runtime evidence contract

---

## Track C: Review Engine

> Build structured review ceremonies and anomaly detection.

### C1: Execution Review (Weekly)

- [ ] Define execution review template (inputs, agenda, outputs)
- [ ] Build review input generator: initiative progress summary
- [ ] Build review input generator: blocked items report
- [ ] Build review input generator: agent output pending review
- [ ] Build review input generator: drift flags from last 7 days
- [ ] Build review input generator: action items from last review (status update)
- [ ] Build review decision capture (approve, defer, escalate, close)
- [ ] Build review action item creator with assignee and due date
- [ ] Build review session persistence (Delta table write)
- [ ] Write tests for review input generation with sample graph data

### C2: Portfolio Review (Monthly)

- [ ] Define portfolio review template (inputs, agenda, outputs)
- [ ] Build review input generator: goal/KR progress summary
- [ ] Build review input generator: coverage gap report (goals without execution)
- [ ] Build review input generator: strategic alignment check
- [ ] Build review input generator: resource allocation summary
- [ ] Build review input generator: exception log from past month
- [ ] Build portfolio health score computation
- [ ] Write tests for portfolio review generation

### C3: Exception Review (On-Demand)

- [ ] Define exception triggers: drift detected, eval gate failed, stale evidence threshold, manual escalation
- [ ] Build trigger routing (which exceptions go to which reviewers)
- [ ] Build exception review input generator (evidence for the specific exception)
- [ ] Build exception resolution workflow (decision -> action item -> follow-up)
- [ ] Build escalation path (exception -> portfolio review if unresolved)
- [ ] Write tests for exception trigger detection

### C4: Drift and Orphan Detection

- [ ] Implement drift detector: status vs. evidence inconsistency
  - Initiative marked "complete" but linked spec has incomplete tasks
  - KR marked "achieved" but metric below target
  - Work item marked "done" but PR not merged
  - Release marked "deployed" but eval gate failed
  - Capability marked "ready" but assessment stale or insufficient
- [ ] Implement orphan detector: entities without upstream/downstream links
  - Goals without KRs
  - KRs without initiatives
  - Initiatives without specs
  - Specs without work items
  - Work items without PRs or agent runs
  - PRs without pipeline runs
  - Agent runs without linked work items
  - Learning paths without capability requirements
  - Skill packs without agent role assignments
- [ ] Implement stale evidence detector (evidence age > freshness policy)
- [ ] Build anomaly dashboard in Power BI
- [ ] Write comprehensive tests for each drift/orphan pattern

---

## Track D: Agentic SDLC

> Model agent participation, confidence, and approval workflows.

### D1: Agent Identity Registry

- [ ] Design agent identity schema (name, type, version, capabilities, active status)
- [ ] Register existing agents: Claude Code (maker), Foundry agents (maker), eval runners (judge), ops agents (ops)
- [ ] Build agent capability declaration format (JSON schema)
- [ ] Build agent registration API/CLI
- [ ] Persist in `catalog.diva_goals.agent_graph.agent_identity`
- [ ] Write tests for agent registration and lookup

### D2: Agent Run Evidence

- [ ] Build agent run ingestion from GitHub Actions logs (detect agent-authored commits via bot usernames)
- [ ] Build agent run ingestion from Foundry agent metadata
- [ ] Build agent run ingestion from Claude Code session logs (if available)
- [ ] Link agent runs to work items via commit messages or PR references
- [ ] Compute run duration, input context size, output artifact count
- [ ] Persist in `catalog.diva_goals.agent_graph` tables
- [ ] Write tests for agent run parsing and linking

### D3: Confidence Scoring Model

- [ ] Define confidence score range (0.0 - 1.0)
- [ ] Define routing thresholds:
  - `>= 0.9`: Auto-approve (human notified, can override within 24h)
  - `0.7 - 0.89`: Human review required
  - `0.5 - 0.69`: Human review required, flagged as low-confidence
  - `< 0.5`: Auto-reject, return to agent with feedback
- [ ] Build confidence score extraction from agent run metadata
- [ ] Build threshold-based routing logic
- [ ] Build confidence calibration dashboard (actual outcomes vs. predicted confidence)
- [ ] Write tests for routing logic at each threshold boundary

### D4: Approval Workflow

- [ ] Build approval request creation (when agent output crosses human-review threshold)
- [ ] Build approval decision capture (approve, reject, request changes)
- [ ] Build approval justification capture (free text, linked evidence)
- [ ] Build approval notification (Teams/Slack notification to designated reviewer)
- [ ] Build approval timeout policy (escalate if no decision within SLA)
- [ ] Link approval records to agent runs and work items
- [ ] Persist in `catalog.diva_goals.agent_graph.approval_record`
- [ ] Write tests for approval workflow lifecycle

### D5: Agent Participation Views

- [ ] Build "agent activity" view: all agent runs in last 7/30 days
- [ ] Build "agent effectiveness" view: confidence vs. approval rate per agent
- [ ] Build "pending review" view: agent outputs awaiting human approval
- [ ] Build "agent contribution" view: percentage of work items with agent participation
- [ ] Build Power BI dashboard for agent participation metrics
- [ ] Write tests for view computation

---

## Track E: Governance

> Policy automation, audit, export, and compliance.

### E1: Stale Evidence Policy

- [ ] Define freshness policies per evidence type (see plan.md policy table)
- [ ] Implement freshness check job (Databricks scheduled notebook, hourly)
- [ ] Implement auto-flagging: mark entity status as "unverified" when evidence stale
- [ ] Build stale evidence notification (alert to entity owner)
- [ ] Build freshness policy configuration (YAML in `ssot/governance/diva_goals_freshness.yaml`)
- [ ] Write tests for staleness detection and auto-flagging

### E2: Override Audit

- [ ] Implement override detection: any status set manually (not derived from evidence)
- [ ] Require justification for all overrides (free text, minimum 20 characters)
- [ ] Log overrides in append-only audit table
- [ ] Build override report: all overrides in last 7/30/90 days
- [ ] Build override dashboard in Power BI
- [ ] Write tests for override detection and logging

### E3: Export and Snapshot

- [ ] Build goal graph export (full graph as JSON for compliance archival)
- [ ] Build evidence chain export (for any goal, export complete evidence chain as PDF)
- [ ] Build periodic snapshot job (weekly full graph snapshot to Azure Blob Storage)
- [ ] Build snapshot comparison (diff between two snapshots to detect unintended changes)
- [ ] Document export format in `docs/contracts/DIVA_GOALS_EXPORT_CONTRACT.md`
- [ ] Write tests for export completeness and format

### E4: Policy Gates

- [ ] Implement "no status without evidence" gate (block status transitions without evidence link)
- [ ] Implement "no silent agent mutation" gate (block agent status changes without audit record)
- [ ] Implement "no orphan creation" gate (warn when creating entities without upstream links)
- [ ] Implement "freshness required for review" gate (block review ceremony if critical evidence stale)
- [ ] Implement "no readiness without evidence" gate (block capability readiness claims without linked assessment/eval)
- [ ] Implement "no autonomy upgrade without eval" gate (block agent tier promotion without passing eval)
- [ ] Build gate violation report (all gate violations in last 7/30 days)
- [ ] Write tests for each policy gate

### E5: Governance Dashboard

- [ ] Build "governance health" Power BI dashboard
  - Evidence coverage: % of entities with fresh evidence
  - Override rate: % of status transitions that are overrides
  - Orphan count: entities without upstream/downstream links
  - Stale evidence count: entities with stale evidence
  - Agent approval rate: % of agent outputs approved on first review
  - Review ceremony completion: % of scheduled reviews completed on time
  - Capability gap count: unmet capability requirements on active priorities
  - Agent re-eval needed: agents with stale eval scores
- [ ] Build governance alert rules (threshold-based notifications)
- [ ] Document governance KPIs in `ssot/governance/diva_goals_governance_kpis.yaml`
- [ ] Write tests for dashboard metric computation

---

## Track F: Microsoft Agent Framework

> Build Diva Goals internal agent orchestration using Microsoft Agent Framework.

### F1: Orchestrator Graph

- [ ] Design workflow graph for goal-status-synthesis workflow
- [ ] Design workflow graph for review-pack-generation workflow
- [ ] Design workflow graph for capability-readiness-review workflow
- [ ] Design workflow graph for drift-orphan-detection workflow
- [ ] Implement orchestrator agent using Microsoft Agent Framework SDK
- [ ] Define event routing rules (source system event -> workflow)
- [ ] Write tests for orchestrator graph routing

### F2: Executor Contracts

- [ ] Define input/output contract for Azure Boards evidence collector
- [ ] Define input/output contract for GitHub evidence collector
- [ ] Define input/output contract for pipeline evidence collector
- [ ] Define input/output contract for runtime metrics collector
- [ ] Define input/output contract for L&D records collector
- [ ] Define input/output contract for Foundry eval results collector
- [ ] Define input/output contract for review synthesis agent
- [ ] Document all contracts in `agents/contracts/diva_goals_executor_contracts.md`

### F3: Judge Contracts

- [ ] Define input/output contract for evidence chain validator
- [ ] Define input/output contract for capability readiness validator
- [ ] Define input/output contract for agent eval score validator
- [ ] Define input/output contract for drift anomaly scorer
- [ ] Implement maker/judge separation enforcement (no agent both produces and validates its own output)
- [ ] Document judge contracts in `agents/contracts/diva_goals_judge_contracts.md`

### F4: Approval Checkpoints

- [ ] Design human-approval checkpoint in workflow graph
- [ ] Implement checkpoint pause/resume mechanism
- [ ] Implement approval timeout and escalation
- [ ] Implement approval notification (Teams, Slack, email)
- [ ] Wire approval records to audit trail
- [ ] Write tests for checkpoint lifecycle (pause, approve, reject, timeout)

### F5: Workflow Events

- [ ] Define event schema for workflow-started, workflow-completed, workflow-failed
- [ ] Define event schema for checkpoint-reached, checkpoint-approved, checkpoint-rejected
- [ ] Define event schema for evidence-ingested, drift-detected, orphan-detected
- [ ] Emit all events to Foundry tracing for observability
- [ ] Wire events to Azure Monitor for alerting
- [ ] Write tests for event emission and schema validation

---

## Track G: Foundry Deployment

> Deploy Diva Goals agents on Azure AI Foundry Agent Service.

### G1: Hosted Agents

- [ ] Create Foundry project for Diva Goals agents
- [ ] Deploy orchestrator agent as Foundry-hosted agent
- [ ] Deploy evidence collector agents (one per source system)
- [ ] Deploy review synthesis agent
- [ ] Deploy judge agents (evidence validator, readiness validator)
- [ ] Configure agent versioning and rollback
- [ ] Write deployment smoke tests

### G2: Project Connections

- [ ] Configure Foundry project connection to Azure Boards (via PAT in Key Vault)
- [ ] Configure Foundry project connection to GitHub (via App token in Key Vault)
- [ ] Configure Foundry project connection to Azure DevOps Pipelines
- [ ] Configure Foundry project connection to Application Insights
- [ ] Configure Foundry project connection to Databricks SQL
- [ ] Verify all connections with health checks
- [ ] Document connections in `agents/contracts/diva_goals_foundry_connections.md`

### G3: IQ Knowledge Base

- [ ] Create Foundry IQ knowledge base for Diva Goals domain knowledge
- [ ] Index spec kit content (all spec bundles)
- [ ] Index architecture docs (platform target state, contracts)
- [ ] Index governance policies (constitution, review ceremonies)
- [ ] Configure MCP `knowledge_base_retrieve` endpoint
- [ ] Test knowledge retrieval for review synthesis scenarios
- [ ] Document KB scope and refresh cadence

### G4: Tracing

- [ ] Enable Foundry tracing for all Diva Goals agent invocations
- [ ] Configure trace retention policy (90 days dev, indefinite prod)
- [ ] Build trace query dashboard (agent invocations, latency, errors)
- [ ] Wire trace events to Azure Monitor alerts (error rate, latency thresholds)
- [ ] Write tests for trace completeness (every agent run produces a trace)

### G5: Eval Pipeline

- [ ] Define eval suite for Diva Goals agents (task_completion, task_adherence, intent_resolution, tool_call_accuracy)
- [ ] Create golden test set for evidence collection accuracy
- [ ] Create golden test set for review synthesis quality
- [ ] Create golden test set for judge agent precision/recall
- [ ] Run baseline eval and record scores
- [ ] Configure eval pipeline in Foundry (run on agent version change)
- [ ] Set pass/fail thresholds per eval dimension
- [ ] Write CI gate: block agent deployment if eval fails

---

## Track H: Skills

> Package Diva Goals agent capabilities as reusable skills.

### H1: Strategy Review Skill

- [ ] Define skill contract: input (goal graph subset, evidence), output (review summary, drift flags)
- [ ] Implement strategy review logic (progress computation, gap detection)
- [ ] Package as Agent Skill with metadata
- [ ] Write unit tests for review logic
- [ ] Register in agent skill registry

### H2: Capability Review Skill

- [ ] Define skill contract: input (capability graph, assessment evidence), output (gap report, readiness heat map)
- [ ] Implement capability gap scoring algorithm
- [ ] Implement readiness heat map generation
- [ ] Package as Agent Skill with metadata
- [ ] Write unit tests for gap scoring
- [ ] Register in agent skill registry

### H3: Boards/Spec/GitHub Traceability Skill

- [ ] Define skill contract: input (entity ID, entity type), output (full trace chain with evidence links)
- [ ] Implement drill-through logic (traverse graph from any node to all connected evidence)
- [ ] Package as Agent Skill with metadata
- [ ] Write unit tests for trace completeness
- [ ] Register in agent skill registry

### H4: Policy Check Skill

- [ ] Define skill contract: input (proposed action, entity context), output (pass/fail, violation details)
- [ ] Implement checks for all policy gates (no status without evidence, no silent mutation, no orphan creation, no readiness without evidence, no autonomy upgrade without eval)
- [ ] Package as Agent Skill with metadata
- [ ] Write unit tests for each policy rule
- [ ] Register in agent skill registry

---

## Track I: Capability Model

> Define and implement the human capability taxonomy and scoring model.

### I1: Capability Taxonomy

- [ ] Define capability taxonomy YAML schema (`ssot/governance/diva_goals_capability_taxonomy.yaml`)
- [ ] Enumerate initial capability domains (engineering, finance, compliance, operations, AI/ML)
- [ ] Define 10-20 core capabilities per domain
- [ ] Validate taxonomy with stakeholder review
- [ ] Document taxonomy in `docs/architecture/DIVA_GOALS_CAPABILITY_TAXONOMY.md`

### I2: Role Families

- [ ] Define role family schema (id, name, description, required_capabilities with levels)
- [ ] Create initial role family catalog (platform engineer, finance analyst, compliance officer, L&D specialist, etc.)
- [ ] Map role families to capability requirements
- [ ] Create Delta table DDL for `catalog.diva_goals.human_capability_graph.role_family`
- [ ] Write tests for role-family-to-capability linkage

### I3: Proficiency Ladders

- [ ] Define 5-level proficiency model (awareness, foundational, competent, advanced, expert)
- [ ] Define evidence requirements per level per capability
- [ ] Create proficiency-level descriptions for each capability in taxonomy
- [ ] Create Delta table DDL for `catalog.diva_goals.human_capability_graph.proficiency_level`
- [ ] Write tests for proficiency level validation

### I4: Gap Scoring

- [ ] Define gap score formula: required_level - assessed_level per capability per entity
- [ ] Implement aggregated gap score per strategic priority (sum of gaps across required capabilities)
- [ ] Implement organizational gap heat map (capabilities x role families)
- [ ] Implement gap-as-blocker surfacing in goal graph
- [ ] Build gap score Power BI report
- [ ] Write tests for gap computation with edge cases (missing assessments, partial coverage)

---

## Track J: Learning/OD

> Model learning paths, evidence, adoption measures, and readiness review.

### J1: Learning-Path Model

- [ ] Define learning_path entity schema (capability_requirement_id, interventions, target_date, status, evidence_links)
- [ ] Define intervention types (course, project assignment, mentoring, certification, self-study)
- [ ] Implement learning-path-to-capability-requirement linkage
- [ ] Create Delta table DDL for `catalog.diva_goals.human_capability_graph.learning_path`
- [ ] Write tests for learning path lifecycle (created, in_progress, completed, abandoned)

### J2: Evidence Model

- [ ] Define learning evidence types (completion record, assessment score, project evidence, peer review, certification)
- [ ] Implement evidence ingestion from L&D system (batch, daily)
- [ ] Implement evidence-to-capability-assessment mapping
- [ ] Build evidence freshness policy for learning evidence (90-day window)
- [ ] Write tests for evidence ingestion and mapping

### J3: Adoption Measures

- [ ] Define learning adoption metrics (enrollment rate, completion rate, assessment pass rate, time-to-completion)
- [ ] Implement metric computation from learning evidence
- [ ] Build learning effectiveness metric: capability gap closure rate (% of gaps reduced after intervention)
- [ ] Build learning ROI metric: outcome improvement per learning investment
- [ ] Build Power BI dashboard for L&D metrics
- [ ] Write tests for metric computation

### J4: Readiness Review

- [ ] Define capability/readiness review ceremony template (quarterly)
- [ ] Build review input generator: capability gap summary by strategic priority
- [ ] Build review input generator: readiness heat map (role families x capabilities)
- [ ] Build review input generator: learning effectiveness summary
- [ ] Build review input generator: capability debt tracker (growing gaps)
- [ ] Implement readiness certification workflow (assessment + evidence + human approval)
- [ ] Write tests for review generation

---

## Track K: Agent Development

> Model agent role catalog, skill-pack metadata, eval/readiness tiers, supervision model, and degradation rules.

### K1: Agent Role Catalog

- [ ] Define agent_role entity schema (id, name, type, capability_declaration, autonomy_tier, active)
- [ ] Create initial agent role catalog (code maker, spec maker, eval judge, review synthesizer, evidence collector, policy checker)
- [ ] Define capability declarations per agent role (tools, knowledge bases, output types)
- [ ] Create Delta table DDL for `catalog.diva_goals.agent_capability_graph.agent_role`
- [ ] Write tests for agent role registration and lookup

### K2: Skill-Pack Metadata

- [ ] Define skill_pack entity schema (id, name, agent_role_id, tools, knowledge_bases, eval_suite_id, version)
- [ ] Create skill pack definitions for each agent role
- [ ] Implement skill-pack versioning (new version = new eval required)
- [ ] Implement skill-pack dependency tracking (which knowledge bases, which tools)
- [ ] Create Delta table DDL for `catalog.diva_goals.agent_capability_graph.skill_pack`
- [ ] Write tests for skill pack lifecycle

### K3: Eval/Readiness Tiers

- [ ] Define autonomy tiers: supervised (human reviews every output), semi-autonomous (human reviews exceptions), autonomous (human reviews samples)
- [ ] Define eval requirements per tier:
  - Supervised: task_completion >= 0.7
  - Semi-autonomous: task_completion >= 0.85, task_adherence >= 0.85, tool_call_accuracy >= 0.9
  - Autonomous: all metrics >= 0.9, groundedness >= 0.95
- [ ] Implement tier promotion logic (eval pass at target tier -> promote with human approval)
- [ ] Implement tier demotion logic (eval fail -> demote automatically, notify owner)
- [ ] Create Delta table DDL for `catalog.diva_goals.agent_capability_graph.autonomy_change`
- [ ] Write tests for promotion and demotion workflows

### K4: Supervision Model

- [ ] Define supervision rules per autonomy tier (review frequency, escalation triggers)
- [ ] Implement review routing based on autonomy tier (supervised = all outputs reviewed, semi = exceptions, autonomous = samples)
- [ ] Implement supervision dashboard (which agents are at which tier, review backlog per tier)
- [ ] Wire supervision rules to approval workflow (Track D4)
- [ ] Write tests for supervision routing

### K5: Degradation Rules

- [ ] Define degradation triggers:
  - Eval score drops below tier threshold
  - 3+ rejected outputs in 7-day window
  - Evidence of hallucination flagged by judge agent
  - Manual demotion by human governance decision
- [ ] Implement automatic degradation (demotion + notification)
- [ ] Implement degradation recovery path (re-eval after remediation)
- [ ] Build degradation history dashboard (which agents were demoted, when, why)
- [ ] Write tests for each degradation trigger

---

## Cross-Track Dependencies

```
Track A (Product Definition)
  └──> Track B (Evidence Model) -- schemas must be defined before ingestion
  └──> Track C (Review Engine) -- schemas must be defined before review templates
  └──> Track D (Agentic SDLC) -- agent schema must be defined before participation model
  └──> Track I (Capability Model) -- capability schema must be defined before gap scoring
  └──> Track K (Agent Development) -- agent role schema must be defined before skill packs

Track B (Evidence Model)
  └──> Track C (Review Engine) -- evidence must be available for review inputs
  └──> Track D (Agentic SDLC) -- evidence must be available for agent run linking

Track C (Review Engine)
  └──> Track E (Governance) -- review engine must exist for governance policy enforcement

Track D (Agentic SDLC)
  └──> Track E (Governance) -- agent participation must exist for agent audit policies
  └──> Track K (Agent Development) -- agent identity must exist for role/tier management

Track F (Agent Framework)
  └──> Track G (Foundry Deployment) -- framework design must precede deployment
  └──> Track H (Skills) -- orchestration must exist before skills are wired

Track I (Capability Model)
  └──> Track J (Learning/OD) -- taxonomy must exist before learning paths reference capabilities

Track K (Agent Development)
  └──> Track G (Foundry Deployment) -- agent roles must exist before eval pipelines
```

---

## Definition of Done (per task)

A task is "done" when:

1. Code/config is committed to the repository
2. Tests pass (unit tests for logic, integration tests for API interactions)
3. Schema changes are applied via migration (not ad-hoc)
4. Documentation is updated if the task changes contracts or schemas
5. The task's checkbox in this file is checked
6. Evidence of completion is verifiable (test output, deployment log, screenshot)

---

*Product: Diva Goals*
*Version: 2.0*
*Last updated: 2026-03-23*
