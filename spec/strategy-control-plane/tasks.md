# Tasks — Strategy Control Plane

## Status

Draft

## Document Info

| Field | Value |
|-------|-------|
| Spec bundle | `spec/strategy-control-plane/` |
| Plan | `plan.md` |
| PRD | `prd.md` |
| Constitution | `constitution.md` |
| Created | 2026-03-23 |

---

## Phase 1 — Core Strategy Graph

**Duration**: 4 weeks
**Goal**: Replace spreadsheet OKR tracking with a structured, queryable graph.

### 1.1 Schema and Storage

- [ ] Design PostgreSQL schema for strategic objects (themes, objectives, KRs, KPIs, initiatives, milestones)
- [ ] Design PostgreSQL schema for check-ins (check-in table with status, narrative, metric override, blocker)
- [ ] Design PostgreSQL schema for audit entries (actor, action, target, before/after state, timestamp)
- [ ] Design PostgreSQL schema for permissions (user, role, scope type, scope ID)
- [ ] Write migration scripts for all Phase 1 tables
- [ ] Add SQL constraints: unique names within parent scope, valid status transitions, non-negative weights
- [ ] Add indexes: theme_id on objectives, objective_id on KRs/KPIs, initiative_id on milestones, target_id on check-ins
- [ ] Seed initial data from `ssot/governance/enterprise_okrs.yaml` (parse YAML into strategic model)

### 1.2 Strategic Hierarchy CRUD

- [ ] Implement Theme CRUD API (create, read, update, archive)
- [ ] Implement Objective CRUD API (create within theme, read, update, archive; enforce period dates)
- [ ] Implement Key Result CRUD API (create within objective, read, update, archive; validate metric type and values)
- [ ] Implement KPI CRUD API (create within objective, read, update, archive; validate thresholds)
- [ ] Implement Initiative CRUD API (create, read, update, archive; manage N:M outcome links)
- [ ] Implement Milestone CRUD API (create within initiative, read, update, archive; manage target/actual dates)
- [ ] Implement InitiativeOutcomeLink management (link/unlink initiatives to KRs/KPIs with weights)
- [ ] Implement strategic hierarchy tree endpoint (return full tree from theme down to milestones)
- [ ] Implement ownership assignment (set owner on any strategic object, validate user exists)

### 1.3 Alignment Visualization

- [ ] Implement objective-to-theme alignment view (list objectives per theme with status summary)
- [ ] Implement KR/KPI list view per objective (progress bars, status indicators)
- [ ] Implement initiative list view with linked KR/KPI indicators
- [ ] Implement milestone timeline view per initiative
- [ ] Implement orphan detection: objectives with no KRs, KRs with no evidence plan, initiatives with no outcome links

### 1.4 Manual Check-ins

- [ ] Implement check-in submission API (target type, target ID, status, narrative, optional metric override, blocker)
- [ ] Implement check-in history API (list all check-ins for a target, ordered by created_at desc)
- [ ] Implement check-in form UI (pre-populated with latest values, minimal fields)
- [ ] Implement check-in reminder logic (flag targets overdue for check-in based on cadence)
- [ ] Validate metric override: must be within plausible range (0 to 2x target, configurable)

### 1.5 Basic Review Views

- [ ] Implement objective summary view: all objectives for a period with status, KR count, latest check-in date
- [ ] Implement objective detail view: description, owner, period, KR progress (manual values), recent check-ins
- [ ] Implement status filter: on-track, at-risk, off-track, all
- [ ] Implement period selector: filter objectives by active period

### 1.6 Export

- [ ] Implement JSON export of full strategic graph (themes through milestones with relationships)
- [ ] Implement YAML export of full strategic graph
- [ ] Implement JSON import (round-trip: export -> modify -> import)
- [ ] Validate export/import round-trip produces identical data

### 1.7 RBAC and Audit (Basic)

- [ ] Implement role-based access: admin (full access), owner (edit own objects), viewer (read-only)
- [ ] Implement permission scoping: global, per-theme, per-objective
- [ ] Implement audit logging: every create, update, delete, status change logged with actor and timestamp
- [ ] Implement audit log query API (filter by actor, action, target, time range)
- [ ] Wire authentication to Entra ID (service principal for system, user token for humans)

### 1.8 Phase 1 Validation

- [ ] All active objectives from `enterprise_okrs.yaml` entered and queryable
- [ ] At least one check-in submitted per objective (test with real data)
- [ ] JSON export produces valid, re-importable file
- [ ] RBAC prevents viewer from creating/modifying objects
- [ ] Audit trail shows all mutations with correct actor attribution

---

## Phase 2 — Evidence Connectors

**Duration**: 6 weeks
**Goal**: Derive progress from connected systems instead of self-report.

### 2.1 Adapter Framework

- [ ] Define adapter interface contract (Python abstract base class: configure, test_connection, sync, get_health)
- [ ] Implement EvidenceSource model (adapter type, config, last sync, status, error message)
- [ ] Implement EvidenceRecord model (source, target, evidence type, value, metadata, recorded_at)
- [ ] Implement adapter registry (register adapter implementations by type, look up by EvidenceSource.adapter_type)
- [ ] Implement adapter health endpoint (list all sources with last sync time, status, record count)
- [ ] Implement scheduled sync runner (iterate sources, call adapter.sync, store records, update last_sync_at)
- [ ] Implement sync error handling (log error, set source status to error, continue to next source)
- [ ] Write adapter integration test harness (mock source system, verify record creation)

### 2.2 Azure Boards Adapter

- [ ] Implement Azure DevOps REST API client (WIQL queries, work item reads)
- [ ] Implement initiative-to-work-item mapping storage (initiative ID -> area path or tag or query)
- [ ] Implement work-item sync: fetch items matching initiative mapping, compute completion ratio
- [ ] Emit EvidenceRecord with evidence_type=work_item_completion, value=completed/total
- [ ] Include metadata: state distribution (new, active, resolved, closed), blocked items, cycle time
- [ ] Implement incremental sync (only fetch items changed since last_sync_at)
- [ ] Handle pagination (Azure DevOps API returns max 200 items per page)
- [ ] Wire authentication via service principal (Azure Key Vault secret: `azdo-pat` or `azdo-sp-secret`)
- [ ] Write integration test with mock Azure DevOps responses

### 2.3 GitHub Adapter

- [ ] Implement GitHub REST/GraphQL API client (repositories, PRs, releases, deployments)
- [ ] Implement initiative-to-repository mapping storage (initiative ID -> repo list)
- [ ] Implement PR sync: fetch merged PRs since last sync, compute merge rate
- [ ] Implement release sync: fetch releases, match to milestones by tag convention
- [ ] Emit EvidenceRecord with evidence_type=deployment_status for releases
- [ ] Include metadata: PR count, review turnaround, release notes summary
- [ ] Wire authentication via GitHub App installation token (Azure Key Vault)
- [ ] Write integration test with mock GitHub API responses

### 2.4 Databricks Adapter

- [ ] Implement Databricks SQL Warehouse query client (REST API or JDBC)
- [ ] Implement KPI/KR-to-query mapping storage (target ID -> SQL query string, warehouse ID, catalog, schema)
- [ ] Implement metric sync: execute configured queries, extract metric values
- [ ] Emit EvidenceRecord with evidence_type=metric_value, value from query result
- [ ] Include metadata: query text, execution time, row count, warehouse ID
- [ ] Handle query timeouts gracefully (set max execution time, flag source as stale on timeout)
- [ ] Wire authentication via service principal (Azure Key Vault secret: `databricks-sp-token`)
- [ ] Write integration test with mock Databricks query responses

### 2.5 Evidence Computation Engine

- [ ] Implement ConfidenceDerivation model (target, confidence score, evidence count, freshness, derivation method)
- [ ] Implement confidence scoring algorithm (evidence_quality * freshness_factor * completeness_factor)
- [ ] Implement evidence quality scoring (system-derived: 1.0, manual recent: 0.7, manual stale: 0.4, none: 0.0)
- [ ] Implement freshness factor computation (within cadence: 1.0, decaying to 0.1 at 4x cadence)
- [ ] Implement completeness factor computation (reporting sources / expected sources)
- [ ] Implement objective-level rollup (weighted average of KR/KPI confidences)
- [ ] Implement conflict detection (flag when system-derived and manual values diverge by > threshold)
- [ ] Implement staleness detection (flag when freshest evidence exceeds cadence)
- [ ] Write unit tests for all confidence computation edge cases

### 2.6 Evidence UI

- [ ] Implement evidence timeline view per KR/KPI (chronological list of evidence records with source attribution)
- [ ] Implement confidence indicator on KR/KPI views (color-coded 0.0-1.0 with tooltip showing derivation)
- [ ] Implement adapter health dashboard (table of all sources with status, last sync, error count)
- [ ] Implement stale evidence badge on objective and KR views
- [ ] Implement evidence drill-down: click confidence score to see contributing evidence records and weights

### 2.7 Phase 2 Validation

- [ ] >= 50% of KRs have at least one system-derived evidence source
- [ ] Confidence scores displayed for all KRs with evidence
- [ ] Adapter health dashboard shows green for all configured adapters
- [ ] Stale evidence correctly flagged (test by disabling adapter sync for > cadence period)
- [ ] Conflict detection fires when manual and system values diverge
- [ ] Evidence timeline shows records from multiple sources in correct chronological order

---

## Phase 3 — Review Engine

**Duration**: 4 weeks
**Goal**: Automate MBR packet generation.

### 3.1 MBR Packet Generation

- [ ] Implement ReviewPacket model (name, period, status, generated_at, content)
- [ ] Implement ReviewSection model (packet, objective, narrative, confidence snapshot, evidence summary, exceptions)
- [ ] Implement packet generator: iterate all active objectives for period, compute sections
- [ ] Implement section content: KR progress table, confidence scores, evidence freshness, initiative status
- [ ] Implement packet summary: total objectives, on-track/at-risk/off-track counts, average confidence
- [ ] Implement narrative field per section (initially empty for human entry; pre-filled by agent in Phase 4)
- [ ] Implement packet status workflow: draft -> finalized -> locked
- [ ] Implement packet generation trigger (manual or scheduled T-3 days before review date)
- [ ] Target: packet generation completes in < 60 seconds for all objectives

### 3.2 Exception Detection

- [ ] Implement exception detection engine (run during packet generation, attach exceptions to sections)
- [ ] Implement low_confidence exception (confidence < 0.5)
- [ ] Implement stale_evidence exception (freshest evidence > 2x cadence)
- [ ] Implement off_track exception (status explicitly off_track)
- [ ] Implement drift exception (projected value < 80% of target at period end)
- [ ] Implement no_evidence exception (KR has zero evidence records)
- [ ] Implement no_initiative exception (objective has zero linked initiatives)
- [ ] Implement blocked_work exception (> 20% of linked work items in blocked state)
- [ ] Implement configurable thresholds for all exception types
- [ ] Implement exception summary: count by type, severity ranking

### 3.3 Exception Views

- [ ] Implement exception filter view: show only objectives/KRs with active exceptions
- [ ] Implement exception detail: click exception to see contributing data and suggested action
- [ ] Implement exception trend: show exception count over last N review periods
- [ ] Implement exception assignment: PMO can assign an exception to an owner for follow-up

### 3.4 Forecast and Drift

- [ ] Implement time-series storage for KR evidence (ordered sequence of metric values)
- [ ] Implement linear projection: extrapolate current trend to period end
- [ ] Implement velocity computation: rate of change over last 3+ data points
- [ ] Implement drift calculation: difference between projected and target at period end
- [ ] Implement drift direction classification: accelerating, decelerating, steady
- [ ] Implement forecast view: chart showing actual values, trend line, and target
- [ ] Require minimum 3 data points before generating forecast (skip KRs with insufficient data)

### 3.5 Period Comparison

- [ ] Implement period-over-period comparison view (current vs. previous review period)
- [ ] Implement delta highlighting: show improvement/regression per KR
- [ ] Implement comparison table: side-by-side KR progress with delta column
- [ ] Implement objective-level comparison: aggregate improvement/regression

### 3.6 Review Workspace UI

- [ ] Implement review workspace: central surface for PMO to prepare MBR
- [ ] Implement objective list with inline status, confidence, exception count
- [ ] Implement narrative editor per section (rich text, save draft)
- [ ] Implement exception sidebar (filterable, collapsible)
- [ ] Implement packet finalization workflow (mark as finalized, prevent further edits)
- [ ] Implement export: PDF, Markdown, structured JSON

### 3.7 Check-in Reminders

- [ ] Implement reminder logic: identify targets overdue for check-in (> cadence since last check-in)
- [ ] Implement reminder notification: email or Slack message to owner
- [ ] Implement reminder escalation: if still overdue after 2x cadence, notify PMO
- [ ] Implement reminder suppression: owner can snooze for one cadence cycle

### 3.8 Phase 3 Validation

- [ ] MBR packet generated in < 60 seconds for all objectives
- [ ] All configured exception types detected and surfaced correctly
- [ ] Forecast/drift computed for KRs with >= 3 data points
- [ ] Period comparison shows correct deltas between two consecutive periods
- [ ] PMO confirms generated packet is usable as MBR input (replaces manual assembly)
- [ ] Export produces valid PDF and Markdown

---

## Phase 4 — Agent Layer

**Duration**: 4 weeks
**Goal**: Augment review preparation with AI-generated drafts and risk analysis.

### 4.1 Agent Infrastructure

- [ ] Implement Draft model (draft type, target, author type/ID, content, status, version)
- [ ] Implement draft review queue API (list pending drafts, approve, reject)
- [ ] Implement draft versioning (each agent revision increments version, previous versions retained)
- [ ] Implement draft expiry (drafts older than 14 days auto-expire if not approved/rejected)
- [ ] Implement agent identity registration (agent service principal -> agent name mapping)
- [ ] Implement agent audit logging (all agent API calls logged with agent identity)
- [ ] Implement agent rate limiting (100 API calls/minute per agent identity)
- [ ] Implement agent permission scoping (read: strategic graph + evidence; write: drafts only)

### 4.2 Narrative Drafter Agent

- [ ] Define Foundry agent deployment for narrative drafter
- [ ] Implement tool: read objective detail (KR progress, evidence, recent check-ins)
- [ ] Implement tool: read exception list for objective
- [ ] Implement tool: read historical narratives for objective (past review sections)
- [ ] Implement prompt: generate concise status narrative from evidence and context
- [ ] Implement output: create Draft with draft_type=narrative, target=objective
- [ ] Implement trigger: scheduled T-3 days before review, or on-demand via API
- [ ] Implement quality check: narrative must reference specific evidence, not generic filler
- [ ] Test: generate narratives for all objectives with evidence, verify they enter draft queue

### 4.3 Risk Summarizer Agent

- [ ] Define Foundry agent deployment for risk summarizer
- [ ] Implement tool: read all exceptions across all objectives for current period
- [ ] Implement tool: read historical exception patterns (recurring exceptions)
- [ ] Implement prompt: identify cross-cutting risks, common root causes, systemic patterns
- [ ] Implement output: create Draft with draft_type=corrective_proposal (risk summary variant)
- [ ] Implement trigger: scheduled T-3 days before review
- [ ] Test: generate risk summary with known exception patterns, verify cross-cutting detection

### 4.4 Corrective Proposal Agent

- [ ] Define Foundry agent deployment for corrective proposals
- [ ] Implement tool: read off-track objectives with drift analysis
- [ ] Implement tool: read initiative status and work-item distribution
- [ ] Implement tool: read resource allocation (if available from Odoo/Boards)
- [ ] Implement prompt: propose re-scoping, re-prioritization, or escalation for off-track items
- [ ] Implement output: create Draft with draft_type=corrective_proposal
- [ ] Implement trigger: when drift exceeds configurable threshold, or on-demand
- [ ] Constraint: proposals must cite specific evidence, not speculate
- [ ] Test: generate proposals for off-track objectives, verify evidence citations

### 4.5 Goal Hygiene Agent

- [ ] Define Foundry agent deployment for goal hygiene
- [ ] Implement tool: scan strategic graph for structural issues
- [ ] Implement checks: objectives with no KRs, KRs with no evidence source, initiatives with no outcome links
- [ ] Implement checks: stale objects (no check-in or evidence in > 2x cadence), duplicate/overlapping KRs
- [ ] Implement checks: milestones past target date with no actual date (missed but not marked)
- [ ] Implement output: create Draft with draft_type=status_change (hygiene findings)
- [ ] Implement trigger: weekly scheduled
- [ ] Test: seed graph with known hygiene issues, verify agent detects all of them

### 4.6 Draft Review UI

- [ ] Implement draft review queue view (list pending drafts grouped by type)
- [ ] Implement draft detail view (show draft content, target context, agent identity, version history)
- [ ] Implement approve action (draft becomes visible in review packet or applied to target)
- [ ] Implement reject action (draft marked rejected with optional reviewer comment)
- [ ] Implement bulk approve/reject (PMO can process multiple drafts in one action)
- [ ] Implement draft comparison: show agent draft vs. current narrative side-by-side

### 4.7 Phase 4 Validation

- [ ] Agent-drafted narratives available for all objectives with sufficient evidence
- [ ] All agent drafts enter review queue (none visible in packets without approval)
- [ ] Goal hygiene agent correctly identifies: unlinked objectives, KRs with no evidence, stale items
- [ ] Risk summarizer identifies cross-cutting patterns from exception data
- [ ] All agent actions logged with agent identity in audit trail
- [ ] Rate limiting enforced (verify 101st call in a minute is rejected)
- [ ] Approved narratives appear in review sections; rejected narratives do not

---

## Phase 5 — Governance Hardening

**Duration**: 3 weeks
**Goal**: Enterprise-grade governance for strategic data.

### 5.1 Approval Workflows

- [ ] Implement approval chain model (target type, required approver role, current approver, status)
- [ ] Implement approval requirement: objective status changes (draft -> active, active -> completed/cancelled) require owner or admin approval
- [ ] Implement approval requirement: KR target value changes require objective owner approval
- [ ] Implement approval notification: notify required approver when approval is pending
- [ ] Implement approval timeout: escalate to admin if not approved within configurable period
- [ ] Implement approval bypass for admin role (emergency override, logged in audit trail)

### 5.2 Locked Snapshots

- [ ] Implement Snapshot model (packet, snapshot data as JSONB, locked flag, created/locked timestamps)
- [ ] Implement snapshot creation: capture full strategic graph state at review period finalization
- [ ] Implement snapshot locking: admin action that makes snapshot immutable
- [ ] Implement lock enforcement: API returns 403 for any mutation targeting a locked period's data
- [ ] Implement snapshot comparison: diff two snapshots to show what changed between periods
- [ ] Implement snapshot export: download locked snapshot as JSON archive

### 5.3 Audit Trail Hardening

- [ ] Implement immutable audit log (append-only table, no UPDATE or DELETE permissions)
- [ ] Implement audit log viewer UI (filter by actor, action type, target, date range)
- [ ] Implement audit log export (CSV, JSON)
- [ ] Implement audit log retention policy (minimum 12 months, configurable)
- [ ] Implement audit log integrity check (periodic hash verification)
- [ ] Ensure all API endpoints emit audit entries (verify with integration tests)

### 5.4 Policy Automation

- [ ] Implement policy rule model (condition, action, threshold, enabled flag)
- [ ] Implement policy: auto-flag objectives with no linked initiatives after 14 days
- [ ] Implement policy: auto-flag KRs with no evidence source after 7 days
- [ ] Implement policy: auto-escalate off-track objectives with no check-in in 2x cadence
- [ ] Implement policy: auto-flag milestones past target date with no actual date
- [ ] Implement policy runner: scheduled evaluation of all active policies
- [ ] Implement policy notification: flagged items notify owner and PMO
- [ ] Implement policy dashboard: view active policies, recent flags, suppressed flags

### 5.5 Additional Adapters

- [ ] Implement Odoo adapter: query `account.analytic.line` for cost tracking per initiative
- [ ] Implement Odoo adapter: query `account.move` for invoice/payment evidence per budget KPI
- [ ] Wire Odoo authentication via service user API key (Azure Key Vault)
- [ ] Test Odoo adapter with real financial data (budget vs. actual for one initiative)
- [ ] Implement Telemetry adapter: execute KQL queries against Application Insights
- [ ] Wire Telemetry authentication via managed identity
- [ ] Test Telemetry adapter with runtime KPI (e.g., uptime percentage, error rate)

### 5.6 Phase 5 Validation

- [ ] Approval workflow enforced: objective status change without approval returns 403
- [ ] Locked snapshot immutable: any mutation returns 403 with clear error message
- [ ] Audit trail complete: every mutation, approval, rejection, lock action has audit entry
- [ ] Policy automation fires correctly: seed test data with known violations, verify flags
- [ ] Odoo adapter produces financial evidence records for budget KPIs
- [ ] Telemetry adapter produces runtime metric evidence for operational KPIs
- [ ] Admin bypass logged in audit trail when used
- [ ] Audit log export produces valid CSV/JSON with all required fields

---

## Cross-Phase Tasks

### Documentation

- [ ] Write adapter interface contract documentation (Phase 2)
- [ ] Write evidence computation methodology documentation (Phase 2)
- [ ] Write review packet format specification (Phase 3)
- [ ] Write agent capability and constraint documentation (Phase 4)
- [ ] Write governance policy reference documentation (Phase 5)
- [ ] Update `ssot/governance/planning_system_index.yaml` to include Strategy Control Plane

### Testing

- [ ] Unit tests for all strategic object CRUD operations (Phase 1)
- [ ] Unit tests for confidence scoring edge cases (Phase 2)
- [ ] Integration tests for each adapter with mock source systems (Phase 2)
- [ ] Integration tests for MBR packet generation (Phase 3)
- [ ] Integration tests for agent draft workflow (Phase 4)
- [ ] End-to-end test: create objective -> link initiative -> sync evidence -> generate packet -> agent draft -> approve -> lock (Phase 5)

### Infrastructure

- [ ] PostgreSQL schema deployment automation (Phase 1)
- [ ] Adapter sync scheduling configuration (Phase 2)
- [ ] Agent deployment to Foundry workspace (Phase 4)
- [ ] Monitoring: adapter health alerts (Phase 2)
- [ ] Monitoring: packet generation latency alerts (Phase 3)
- [ ] Monitoring: agent rate limit alerts (Phase 4)
