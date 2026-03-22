# Plan — Strategy Control Plane

## Status

Draft

## Document Info

| Field | Value |
|-------|-------|
| Spec bundle | `spec/strategy-control-plane/` |
| PRD | `prd.md` |
| Constitution | `constitution.md` |
| Created | 2026-03-23 |

---

## 1. Architecture Overview

### 1.1 System Position

Strategy Control Plane sits **above** execution systems and **below** executive decision-making. It is a read-heavy, write-light system that aggregates evidence from source systems and presents it through a review-first interface.

```
Executive Decision Layer
        |
        v
+---------------------------+
| Strategy Control Plane    |
|  - Strategic Model        |
|  - Evidence Engine        |
|  - Review Engine          |
|  - Agent Layer            |
+---------------------------+
   |      |      |      |      |
   v      v      v      v      v
Azure   GitHub  Databricks  Odoo  Foundry
Boards                            (Agents)
```

### 1.2 Design Principles

1. **Adapter pattern for all integrations.** No source system is directly coupled. Every connection goes through a versioned adapter contract.
2. **Eventual consistency for evidence.** Adapters sync on a schedule. Evidence is timestamped. Staleness is explicit.
3. **Append-only evidence store.** Evidence records are never mutated. New evidence appends; confidence is recomputed.
4. **Compute-on-read for confidence.** Confidence scores are derived at query time from the latest evidence. No pre-aggregated scores that can go stale.
5. **Drafts are first-class objects.** Agent outputs, pending check-ins, and proposed status changes all exist as drafts with their own lifecycle.

---

## 2. Data Model

### 2.1 Strategic Objects

```
Theme
  |-- id: UUID
  |-- name: string
  |-- description: text
  |-- owner_id: UUID (-> User)
  |-- status: enum (active, archived)
  |-- created_at, updated_at: timestamp

Objective
  |-- id: UUID
  |-- theme_id: UUID (-> Theme)
  |-- name: string
  |-- description: text
  |-- owner_id: UUID (-> User)
  |-- period_start: date
  |-- period_end: date
  |-- status: enum (draft, active, completed, cancelled, archived)
  |-- created_at, updated_at: timestamp

KeyResult
  |-- id: UUID
  |-- objective_id: UUID (-> Objective)
  |-- name: string
  |-- description: text
  |-- owner_id: UUID (-> User)
  |-- metric_type: enum (percentage, count, currency, boolean, custom)
  |-- start_value: decimal
  |-- target_value: decimal
  |-- current_value: decimal
  |-- unit: string
  |-- weight: decimal (contribution to objective, default 1.0)
  |-- cadence: enum (weekly, biweekly, monthly, quarterly)
  |-- status: enum (on_track, at_risk, off_track, completed, cancelled)
  |-- created_at, updated_at: timestamp

KPI
  |-- id: UUID
  |-- objective_id: UUID (-> Objective)
  |-- name: string
  |-- description: text
  |-- owner_id: UUID (-> User)
  |-- metric_type: enum (percentage, count, currency, ratio, custom)
  |-- current_value: decimal
  |-- unit: string
  |-- threshold_red: decimal
  |-- threshold_yellow: decimal
  |-- threshold_green: decimal
  |-- cadence: enum (daily, weekly, monthly)
  |-- created_at, updated_at: timestamp

Initiative
  |-- id: UUID
  |-- name: string
  |-- description: text
  |-- owner_id: UUID (-> User)
  |-- status: enum (planned, active, completed, cancelled)
  |-- created_at, updated_at: timestamp

InitiativeOutcomeLink (N:M join)
  |-- id: UUID
  |-- initiative_id: UUID (-> Initiative)
  |-- outcome_type: enum (key_result, kpi)
  |-- outcome_id: UUID (-> KeyResult or KPI)
  |-- contribution_weight: decimal

Milestone
  |-- id: UUID
  |-- initiative_id: UUID (-> Initiative)
  |-- name: string
  |-- description: text
  |-- target_date: date
  |-- actual_date: date (nullable)
  |-- status: enum (pending, done, missed)
  |-- created_at, updated_at: timestamp
```

### 2.2 Evidence Objects

```
EvidenceSource
  |-- id: UUID
  |-- adapter_type: enum (azure_boards, github, databricks, odoo, telemetry, manual)
  |-- config: jsonb (adapter-specific connection details)
  |-- last_sync_at: timestamp
  |-- sync_status: enum (ok, error, stale)
  |-- error_message: text (nullable)

EvidenceRecord
  |-- id: UUID
  |-- source_id: UUID (-> EvidenceSource)
  |-- target_type: enum (key_result, kpi, initiative, milestone)
  |-- target_id: UUID
  |-- evidence_type: enum (metric_value, work_item_completion, deployment_status, milestone_gate, manual_entry)
  |-- value: decimal
  |-- metadata: jsonb (source-specific details: work item IDs, query results, etc.)
  |-- recorded_at: timestamp
  |-- created_at: timestamp

ConfidenceDerivation
  |-- id: UUID
  |-- target_type: enum (key_result, kpi, objective)
  |-- target_id: UUID
  |-- confidence_score: decimal (0.0 - 1.0)
  |-- evidence_count: integer
  |-- freshest_evidence_at: timestamp
  |-- stalest_evidence_at: timestamp
  |-- derivation_method: jsonb (weights, sources, computation details)
  |-- computed_at: timestamp
```

### 2.3 Review and Check-in Objects

```
CheckIn
  |-- id: UUID
  |-- target_type: enum (key_result, kpi, objective)
  |-- target_id: UUID
  |-- author_id: UUID (-> User)
  |-- status: enum (on_track, at_risk, off_track)
  |-- narrative: text
  |-- metric_override: decimal (nullable — manual progress override)
  |-- blocker_description: text (nullable)
  |-- help_needed: text (nullable)
  |-- created_at: timestamp

ReviewPacket
  |-- id: UUID
  |-- name: string (e.g., "MBR March 2026")
  |-- period_start: date
  |-- period_end: date
  |-- status: enum (draft, finalized, locked)
  |-- generated_at: timestamp
  |-- finalized_at: timestamp (nullable)
  |-- locked_at: timestamp (nullable)
  |-- content: jsonb (structured packet data)

ReviewSection
  |-- id: UUID
  |-- packet_id: UUID (-> ReviewPacket)
  |-- objective_id: UUID (-> Objective)
  |-- narrative: text (human-edited or agent-drafted)
  |-- narrative_source: enum (manual, agent_draft, agent_approved)
  |-- confidence_snapshot: decimal
  |-- evidence_summary: jsonb
  |-- exceptions: jsonb (list of flagged issues)

Draft
  |-- id: UUID
  |-- draft_type: enum (narrative, check_in, status_change, corrective_proposal)
  |-- target_type: enum (key_result, kpi, objective, initiative)
  |-- target_id: UUID
  |-- author_type: enum (human, agent)
  |-- author_id: string (user UUID or agent identity)
  |-- content: jsonb
  |-- status: enum (pending, approved, rejected, expired)
  |-- version: integer
  |-- created_at, reviewed_at: timestamp
  |-- reviewed_by: UUID (nullable -> User)
```

### 2.4 Governance Objects

```
AuditEntry
  |-- id: UUID
  |-- actor_type: enum (human, agent, system)
  |-- actor_id: string
  |-- action: enum (create, update, delete, approve, reject, lock, sync)
  |-- target_type: string
  |-- target_id: UUID
  |-- before_state: jsonb (nullable)
  |-- after_state: jsonb (nullable)
  |-- timestamp: timestamp

Snapshot
  |-- id: UUID
  |-- packet_id: UUID (-> ReviewPacket)
  |-- snapshot_data: jsonb (full strategic graph at point in time)
  |-- locked: boolean
  |-- created_at: timestamp
  |-- locked_by: UUID (nullable -> User)

Permission
  |-- id: UUID
  |-- user_id: UUID (-> User)
  |-- role: enum (viewer, contributor, owner, admin)
  |-- scope_type: enum (global, theme, objective)
  |-- scope_id: UUID (nullable — null for global)
```

---

## 3. Integration Architecture

### 3.1 Adapter Contract

Every adapter implements the following interface:

```python
class SourceAdapter:
    """Base contract for evidence source adapters."""

    def configure(self, config: dict) -> None:
        """Set adapter-specific connection configuration."""

    def test_connection(self) -> AdapterHealthStatus:
        """Verify connectivity. Returns status, latency, error message."""

    def sync(self, since: datetime | None = None) -> list[EvidenceRecord]:
        """Fetch evidence records since the given timestamp.
        If since is None, perform full sync."""

    def get_health(self) -> AdapterHealthStatus:
        """Return current adapter health (last sync, error count, record count)."""
```

Adapters are stateless. Connection configuration is stored in `EvidenceSource.config`. Sync results are appended to the `EvidenceRecord` table.

### 3.2 Azure Boards Adapter

**Source**: Azure DevOps REST API (`/_apis/wit/wiql` and `/_apis/wit/workitems`)
**Evidence type**: Work-item completion ratio per initiative
**Sync logic**:
1. Query work items linked to each initiative (via initiative -> work-item mapping stored in `InitiativeWorkItemLink`)
2. For each initiative, compute: total items, completed items, in-progress items, blocked items
3. Emit `EvidenceRecord` with `evidence_type=work_item_completion`, `value=completed/total`
4. Emit additional metadata: state distribution, average cycle time, blocked item list

**Authentication**: Service principal with `vso.work` scope, credentials from Azure Key Vault.

### 3.3 GitHub Adapter

**Source**: GitHub REST/GraphQL API
**Evidence type**: Repository activity, PR merge rate, release/deployment status
**Sync logic**:
1. For each initiative-linked repository, fetch: open PRs, merged PRs (since last sync), releases, deployment statuses
2. Emit `EvidenceRecord` with `evidence_type=deployment_status` for releases
3. Emit milestone gate evidence when a tagged release corresponds to an initiative milestone

**Authentication**: GitHub App installation token, scoped to organization repositories.

### 3.4 Databricks Adapter

**Source**: Databricks SQL Warehouse via REST API or JDBC
**Evidence type**: Metric values for KPIs and KRs
**Sync logic**:
1. Each KPI/KR with a Databricks evidence source has a configured SQL query stored in `EvidenceSource.config`
2. Execute the query against the designated SQL warehouse
3. Map result columns to evidence fields (value, timestamp, metadata)
4. Emit `EvidenceRecord` with `evidence_type=metric_value`

**Authentication**: Service principal with workspace-level permissions, token from Azure Key Vault.

### 3.5 Odoo Adapter

**Source**: Odoo JSON-RPC API (`/jsonrpc`)
**Evidence type**: Financial metrics for budget KPIs (spend vs. budget, invoice totals, expense ratios)
**Sync logic**:
1. Query `account.analytic.line` for cost tracking per project/initiative
2. Query `account.move` for invoice and payment evidence
3. Map financial data to KPI evidence records

**Authentication**: API key via `ipai_odoo_copilot` service user, credentials from Azure Key Vault.

### 3.6 Telemetry Adapter

**Source**: Azure Application Insights REST API
**Evidence type**: Runtime KPI values (uptime, error rate, latency percentiles)
**Sync logic**:
1. Execute KQL queries configured per KPI
2. Map query results to evidence records

**Authentication**: Managed identity with Application Insights reader role.

### 3.7 Manual Adapter

**Source**: Check-in form submissions
**Evidence type**: Manual metric entries and narrative updates
**Sync logic**: Direct insert on check-in submission. No scheduled sync.

---

## 4. Evidence Computation

### 4.1 Confidence Scoring

Confidence score for a KR or KPI is computed at query time using the following formula:

```
confidence = evidence_quality * freshness_factor * completeness_factor
```

Where:

- **evidence_quality** (0.0-1.0): Based on derivation method. System-derived evidence scores higher than manual.
  - System-derived (adapter): 1.0
  - Manual with recent check-in: 0.7
  - Manual with stale check-in: 0.4
  - No evidence: 0.0

- **freshness_factor** (0.0-1.0): Decays based on time since last evidence relative to cadence.
  - Within cadence: 1.0
  - 1-2x cadence overdue: 0.7
  - 2-4x cadence overdue: 0.4
  - Beyond 4x cadence: 0.1

- **completeness_factor** (0.0-1.0): Ratio of evidence sources that have reported vs. expected.
  - All configured sources reporting: 1.0
  - Proportional reduction for missing sources

### 4.2 Objective-Level Rollup

Objective confidence = weighted average of constituent KR/KPI confidences:

```
objective_confidence = sum(kr.confidence * kr.weight) / sum(kr.weight)
```

### 4.3 Freshness Tracking

Every evidence record carries a `recorded_at` timestamp. The evidence engine computes:
- `freshest_evidence_at`: Most recent evidence for a target
- `stalest_evidence_at`: Oldest evidence still contributing to confidence
- `is_stale`: Boolean flag when `freshest_evidence_at` is older than the target's cadence

Stale evidence is flagged in the UI and in review packets, not silently dropped.

### 4.4 Derivation Methods

Each KR/KPI can configure one or more derivation methods:

| Method | Source | Computation |
|--------|--------|-------------|
| `work_item_ratio` | Azure Boards adapter | `completed_items / total_items` |
| `metric_threshold` | Databricks / Telemetry adapter | `current_value` compared to `target_value` |
| `milestone_gate` | Manual / GitHub adapter | `completed_milestones / total_milestones` |
| `financial_ratio` | Odoo adapter | `actual_spend / budgeted_spend` or `revenue / target_revenue` |
| `manual_override` | Check-in form | Owner-provided value, subject to freshness decay |
| `composite` | Multiple | Weighted combination of other methods |

When multiple methods are configured, the composite method combines them with user-defined weights.

---

## 5. Review Generation

### 5.1 MBR Packet Structure

A generated MBR packet contains:

```yaml
packet:
  name: "MBR March 2026"
  period: { start: 2026-03-01, end: 2026-03-31 }
  generated_at: 2026-03-28T14:00:00Z
  summary:
    total_objectives: 12
    on_track: 7
    at_risk: 3
    off_track: 2
    average_confidence: 0.72
  sections:
    - objective_id: uuid
      objective_name: "Achieve 80% EE parity"
      owner: "Engineering"
      confidence: 0.68
      status: at_risk
      kr_progress:
        - kr_name: "OCA module coverage"
          progress: 0.45
          target: 0.80
          confidence: 0.82
          evidence_freshness: "2 days ago"
        - kr_name: "Custom module test coverage"
          progress: 0.30
          target: 0.70
          confidence: 0.55
          evidence_freshness: "12 days ago (STALE)"
      narrative: "..." # Human-edited or agent-drafted
      exceptions:
        - type: stale_evidence
          detail: "KR 'Custom module test coverage' has no evidence update in 12 days"
        - type: drift
          detail: "Current trajectory projects 55% by period end vs. 80% target"
      initiatives:
        - name: "OCA 19.0 porting sprint"
          progress: 0.60
          work_items: { total: 42, completed: 25, blocked: 3 }
```

### 5.2 Exception Detection

The review engine flags exceptions based on configurable thresholds:

| Exception type | Default threshold | Description |
|----------------|-------------------|-------------|
| `low_confidence` | confidence < 0.5 | KR or objective with low evidence quality |
| `stale_evidence` | freshness > 2x cadence | No recent evidence update |
| `off_track` | status = off_track | Explicitly marked off-track by owner or system |
| `drift` | projected < 80% of target at period end | Trajectory analysis shows likely miss |
| `no_evidence` | evidence_count = 0 | KR has no evidence source configured |
| `no_initiative` | linked_initiatives = 0 | Objective has no linked initiatives |
| `blocked_work` | blocked_items > 20% | High percentage of blocked work items |

### 5.3 Forecast and Drift

For KRs with time-series evidence (metric values over time), the review engine computes:

1. **Linear projection**: Extrapolate current trend to period end
2. **Velocity**: Rate of change over last 3 data points
3. **Drift**: Difference between projected value and target value at period end
4. **Drift direction**: Accelerating, decelerating, or steady

Drift is surfaced as an exception when projected completion falls below 80% of target.

---

## 6. Agent Integration

### 6.1 Agent Architecture

Agents are Foundry-backed services that consume the Strategy Control Plane API. They operate under the constraints defined in Constitution principle 4 and PRD section 9.9.

```
+-------------------+     +-------------------+
| Foundry Agent     |     | Foundry Agent     |
| (Narrative Draft) |     | (Risk Summary)    |
+--------+----------+     +--------+----------+
         |                          |
         v                          v
+------------------------------------------+
| Strategy Control Plane API               |
|  GET  /objectives, /evidence, /reviews   |
|  POST /drafts (agent-scoped)             |
+------------------------------------------+
         |
         v
+------------------------------------------+
| Draft Review Queue (human approval)      |
+------------------------------------------+
```

### 6.2 Agent Capabilities

| Agent | Input | Output | Trigger |
|-------|-------|--------|---------|
| **Narrative Drafter** | Objective evidence, KR progress, recent check-ins | Draft narrative text for review section | Pre-MBR generation (T-3 days) |
| **Risk Summarizer** | Exception list across all objectives | Cross-cutting risk summary with patterns | Pre-MBR generation (T-3 days) |
| **Corrective Proposal** | Off-track objectives, drift analysis | Proposed re-scoping, re-prioritization, or escalation actions | On-demand or when drift exceeds threshold |
| **Goal Hygiene** | Full strategic graph | List of objectives with no initiatives, KRs with no evidence, stale items | Weekly scheduled |

### 6.3 Agent Constraints

1. **Read access**: Agents can read the full strategic graph, evidence records, check-ins, and review history.
2. **Write access**: Agents can only write to the `Draft` table. They cannot modify objectives, KRs, evidence, or review packets directly.
3. **Identity**: Every agent action is logged with the agent's service principal identity. Agent actions are never attributed to a human user.
4. **Rate limiting**: Maximum 100 API calls per minute per agent identity.
5. **Draft lifecycle**: Agent drafts expire after 14 days if not approved or rejected.

---

## 7. Tech Stack

| Component | Technology | Rationale |
|-----------|------------|-----------|
| Strategic model storage | Azure PostgreSQL (Odoo DB or dedicated) | Relational model fits the hierarchical data. Existing managed PG in platform. |
| Evidence aggregation | Databricks SQL Warehouse | Evidence queries run against lakehouse tables. Metric KPIs often already in Databricks. |
| Evidence store | PostgreSQL (append-only tables) | Timestamped evidence records with JSONB metadata. |
| API layer | FastAPI (Python) or Odoo JSON-RPC extension | Depends on deployment model. Standalone FastAPI for portability; Odoo extension if deeply integrated. |
| Agent runtime | Azure AI Foundry | Existing agent infrastructure. Agents are Foundry deployments with tool-use. |
| Review generation | Python service (scheduled or on-demand) | Compute confidence, detect exceptions, assemble packet structure. |
| UI | Odoo web client (embedded views) or standalone SPA | Phase 1: Odoo views for fast delivery. Phase 3+: evaluate standalone if Odoo UX is limiting. |
| Auth | Entra ID (service principals for agents, user tokens for humans) | Platform standard. |
| Secrets | Azure Key Vault | Platform standard. |
| Adapter scheduling | Azure Container Apps Jobs or Odoo cron | Adapter sync runs on schedule. ACA Jobs for standalone; Odoo cron if integrated. |

---

## 8. Delivery Phases

### Phase 1 — Core Strategy Graph (4 weeks)

**Goal**: Replace spreadsheet OKR tracking with a structured, queryable graph.

**Deliverables**:
- PostgreSQL schema for all strategic objects (themes through milestones)
- CRUD API for strategic hierarchy
- Ownership assignment and basic RBAC (admin, owner, viewer)
- Manual check-in submission (web form)
- Basic review view: list of objectives with KR progress (manual values only)
- JSON/YAML export of strategic graph
- Audit logging for all mutations

**Dependencies**: None (greenfield).

**Validation**:
- All active objectives from current planning cycle entered into the system
- At least one check-in submitted per objective
- Export produces valid, re-importable JSON

### Phase 2 — Evidence Connectors (6 weeks)

**Goal**: Derive progress from connected systems instead of self-report.

**Deliverables**:
- Adapter interface contract (documented, versioned)
- Azure Boards adapter (work-item sync, completion ratio)
- GitHub adapter (PR/release sync, deployment evidence)
- Databricks adapter (metric query execution)
- Evidence computation engine (confidence scoring, freshness tracking)
- Adapter health dashboard (last sync, error count, status)
- Evidence timeline view per KR/KPI

**Dependencies**: Phase 1 schema. Azure Boards project with work items. GitHub repos. Databricks workspace.

**Validation**:
- >= 50% of KRs have at least one system-derived evidence source
- Confidence scores computed and displayed for all KRs with evidence
- Adapter health dashboard shows green for all configured adapters
- Stale evidence correctly flagged

### Phase 3 — Review Engine (4 weeks)

**Goal**: Automate MBR packet generation.

**Deliverables**:
- MBR packet generator (structured JSON -> PDF/Markdown)
- Exception detection engine (low confidence, stale, drift, missing links)
- Forecast/drift computation for time-series KRs
- Period comparison view
- Review workspace UI (PMO-oriented: filter, edit narratives, export)
- Notification: remind owners of pending check-ins before review deadline

**Dependencies**: Phase 2 evidence engine. At least 2 review cycles of evidence history.

**Validation**:
- MBR packet generated in < 60 seconds
- All configured exception types detected and surfaced
- Forecast drift computed for KRs with >= 3 data points
- PMO confirms packet replaces manual assembly

### Phase 4 — Agent Layer (4 weeks)

**Goal**: Augment review preparation with AI-generated drafts and risk analysis.

**Deliverables**:
- Foundry agent: Narrative Drafter (objective status narratives from evidence)
- Foundry agent: Risk Summarizer (cross-cutting risk patterns from exceptions)
- Foundry agent: Corrective Proposal (re-scoping/escalation suggestions for off-track items)
- Foundry agent: Goal Hygiene (flag unlinked, stale, or malformed strategic objects)
- Draft review queue (human approval workflow for agent outputs)
- Agent audit logging (all agent actions attributed to agent identity)

**Dependencies**: Phase 3 review engine. Foundry workspace with agent deployment capability.

**Validation**:
- Agent-drafted narratives available for all objectives with sufficient evidence
- Drafts enter review queue and are not visible in packets until approved
- Goal hygiene agent correctly identifies unlinked objectives and stale KRs
- Agent actions logged with agent identity in audit trail

### Phase 5 — Governance Hardening (3 weeks)

**Goal**: Enterprise-grade governance for strategic data.

**Deliverables**:
- Approval workflows for objective status changes
- Locked snapshots: freeze review period data (immutable after lock)
- Full audit trail viewer (filter by actor, action, target, time range)
- Policy automation: auto-flag objectives without linked initiatives after 14 days
- Policy automation: auto-escalate off-track objectives with no check-in in 2x cadence
- Odoo adapter (financial evidence for budget KPIs) — moved here due to lower initial priority
- Telemetry adapter (Application Insights for runtime KPIs) — moved here due to lower initial priority

**Dependencies**: Phase 4 agent layer. Established review cadence with at least 3 completed cycles.

**Validation**:
- Locked snapshot cannot be modified (API returns 403)
- Approval workflow enforced for status changes on active objectives
- Policy automation flags fire correctly on test data
- Audit trail shows complete history for any strategic object

---

## 9. Migration from Current State

### 9.1 Data Migration

Current strategic data lives in:
- `ssot/governance/enterprise_okrs.yaml` — current OKR definitions
- `ssot/governance/planning_system_index.yaml` — planning system inventory
- `ssot/governance/platform-capabilities-unified.yaml` — capability tracking
- Notion pages (deprecated as data source, but contain historical context)
- Spreadsheets (ad-hoc, untracked)

Migration approach:
1. Parse `enterprise_okrs.yaml` into the strategic model schema
2. Map existing YAML structure (themes, objectives, KRs) to database records
3. Establish initiative links from existing spec bundles and Azure Boards backlogs
4. Historical check-in data: not migrated (start fresh with the new cadence)

### 9.2 Adapter Bootstrapping

| Adapter | Bootstrap data needed |
|---------|----------------------|
| Azure Boards | Area path to initiative mapping, project/team identifiers |
| GitHub | Repository to initiative mapping, release tag convention |
| Databricks | SQL queries per KPI, warehouse endpoint, catalog/schema paths |
| Odoo | Analytic account to initiative mapping, budget line identifiers |
| Telemetry | KQL queries per KPI, Application Insights resource ID |

---

## 10. Open Design Decisions

| # | Decision | Options | Recommendation | Status |
|---|----------|---------|----------------|--------|
| D1 | Standalone service vs. Odoo module | (a) FastAPI microservice, (b) Odoo module with OWL frontend | (a) for portability, with Odoo adapter for ERP data | Open |
| D2 | Evidence store: same DB as strategic model or separate | (a) Same PostgreSQL, (b) Dedicated evidence DB, (c) Databricks Delta tables | (a) for simplicity in Phase 1-2, migrate to (c) if volume requires | Open |
| D3 | Review packet format | (a) PDF only, (b) Markdown + PDF, (c) Interactive web view + export | (c) for Phase 3, with PDF export as a feature | Open |
| D4 | Agent hosting model | (a) Foundry agents only, (b) Foundry + local fallback | (a) — Foundry is the canonical agent runtime | Decided |
| D5 | UI framework for standalone option | (a) Odoo OWL views, (b) React SPA, (c) Next.js | Defer until D1 is resolved | Open |
