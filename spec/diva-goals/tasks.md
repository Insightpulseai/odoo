# Diva Goals -- Task Breakdown

> Delivery tasks organized in 5 tracks aligned to the implementation plan phases.

---

## Track A: Product Definition

> Establish naming, doctrine, schemas, and agent contracts.

### A1: Product Identity and Naming

- [x] Rename `spec/strategy-control-plane/` to `spec/diva-goals/`
- [x] Rewrite `constitution.md` with Diva Goals identity and 6 invariants
- [x] Rewrite `prd.md` with full product requirements
- [x] Rewrite `plan.md` with architecture and delivery phases
- [x] Rewrite `tasks.md` with 5-track task breakdown
- [x] Create `docs/architecture/DIVA_GOALS_TARGET_STATE.md`
- [x] Create `ssot/platform/diva_goals.yaml` with product metadata
- [ ] Update `ssot/governance/planning_system_index.yaml` to reference Diva Goals

### A2: Strategy Graph Schema

- [ ] Define `objective` entity schema (fields, types, constraints)
- [ ] Define `key_result` entity schema with measurement source binding
- [ ] Define `initiative` entity schema with spec linkage
- [ ] Define relationship model (objective -> KR -> initiative -> spec)
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

- [ ] Define `review_session` entity schema (type, cadence, status)
- [ ] Define `review_input` entity schema (structured JSON content types)
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
- [ ] Implement orphan detector: entities without upstream/downstream links
  - Goals without KRs
  - KRs without initiatives
  - Initiatives without specs
  - Specs without work items
  - Work items without PRs or agent runs
  - PRs without pipeline runs
  - Agent runs without linked work items
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
- [ ] Build governance alert rules (threshold-based notifications)
- [ ] Document governance KPIs in `ssot/governance/diva_goals_governance_kpis.yaml`
- [ ] Write tests for dashboard metric computation

---

## Cross-Track Dependencies

```
Track A (Product Definition)
  └──> Track B (Evidence Model) -- schemas must be defined before ingestion
  └──> Track C (Review Engine) -- schemas must be defined before review templates
  └──> Track D (Agentic SDLC) -- agent schema must be defined before participation model

Track B (Evidence Model)
  └──> Track C (Review Engine) -- evidence must be available for review inputs
  └──> Track D (Agentic SDLC) -- evidence must be available for agent run linking

Track C (Review Engine)
  └──> Track E (Governance) -- review engine must exist for governance policy enforcement

Track D (Agentic SDLC)
  └──> Track E (Governance) -- agent participation must exist for agent audit policies
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
*Version: 1.0*
*Last updated: 2026-03-23*
