# Control Room Platform -- Product Requirements

> **Version**: 1.0.0
> **Status**: Active
> **Last Updated**: 2026-03-07
> **Spec Bundle**: `spec/control-room-platform/`
> **Constitution**: `spec/control-room-platform/constitution.md`

---

## Problem Statement

InsightPulse AI operates across 7 bounded contexts (Odoo, Supabase, Databricks, Plane, n8n, Azure/Foundry, GitHub). Each context has its own operational state, health metrics, and lifecycle. Without a unified governance layer:

1. **No single view of platform health** -- operators must check 7 different systems manually
2. **State overclaiming** -- documents may claim "deployed" when reality is "repo-only"
3. **No KPI tracking** -- operational metrics are scattered or unmeasured
4. **No event audit trail** -- cross-system interactions are opaque
5. **No governance compliance** -- constitutional rules have no automated enforcement

---

## Users

| Persona | Description | Key Actions |
|---------|-------------|-------------|
| **Platform Operator** | Monitors health and state of all bounded contexts | View dashboard, check KPIs, investigate alerts |
| **Finance Lead** | Ensures finance-related KPIs are on target | Monitor approval turnaround, close cycle, BIR compliance |
| **DevOps Engineer** | Manages CI/CD, deployments, and infrastructure state | Validate governance, promote contexts, collect evidence |
| **Engineering Lead** | Oversees integration health and event contracts | Review event audit trail, verify schema compliance |
| **Executive Stakeholder** | Needs high-level platform health summary | View KPI trends, bounded context status overview |

---

## Use Cases

### UC-1: Platform Health Dashboard

**Description**: A single view showing the promotion state, health status, and key metrics for all 7 bounded contexts.

**Acceptance Criteria**:
- [ ] Displays all 7 bounded contexts with current promotion state (`repo-only`, `configured`, `deployed`, `live`)
- [ ] Each context shows last health check timestamp and result
- [ ] State transitions are logged with evidence references
- [ ] Dashboard data is sourced from machine-readable YAML/JSON, not hardcoded
- [ ] Stale health checks (>24h for `live` contexts) trigger visual warnings

**Data Sources**:
- `docs/architecture/CONTROL_ROOM_RUNTIME_STATE.md` (current state)
- `platform/data/contracts/control_room_kpis.yaml` (KPI definitions)
- Health check endpoints per context (when deployed)

---

### UC-2: KPI Tracking

**Description**: Track 17 operational KPIs across bounded contexts with threshold alerting.

**Acceptance Criteria**:
- [ ] All 17 KPIs defined in `platform/data/contracts/control_room_kpis.yaml`
- [ ] Each KPI has `target`, `threshold_warn`, and `threshold_critical` values
- [ ] KPIs are grouped by owning bounded context
- [ ] Historical KPI values are stored for trend analysis (when Databricks is `live`)
- [ ] KPI breaches generate events (`kpi.threshold.breached`)
- [ ] Dashboard shows current vs. target for each KPI

**KPI Categories**:

| Category | Count | Owner |
|----------|-------|-------|
| Finance & Approvals | 4 | odoo-erp |
| Tax & Compliance | 2 | odoo-erp |
| Document Processing | 2 | odoo-erp, n8n |
| Automation | 2 | n8n |
| Agent Platform | 2 | azure-foundry |
| Integration | 3 | supabase, github |
| Analytics | 2 | databricks |

---

### UC-3: Event Audit Trail

**Description**: Immutable log of all cross-system events with schema validation.

**Acceptance Criteria**:
- [ ] All 11 event contracts defined in `platform/data/contracts/control_room_events.yaml`
- [ ] Each event has a JSON Schema for payload validation
- [ ] Events are linked to KPIs they feed (`kpi_linkage`)
- [ ] Event log is append-only (per `spec/integration-control-plane/constitution.md` Rule 3)
- [ ] Events are stored in Supabase `ctrl.integration_events` (when Supabase is `deployed`)
- [ ] Events older than 90 days are archived to Databricks bronze tables (when Databricks is `live`)

---

### UC-4: Governance Compliance

**Description**: Automated enforcement of constitutional rules across the repository.

**Acceptance Criteria**:
- [ ] CI validator checks that no document claims a promotion state without evidence
- [ ] CI validator checks that KPI YAML is syntactically valid and complete
- [ ] CI validator checks that event contracts have valid JSON Schema
- [ ] CI validator checks that `CONTROL_ROOM_RUNTIME_STATE.md` matches actual evidence files
- [ ] PR labels auto-applied for governance-related changes
- [ ] Weekly governance report generated (when CI is `live`)

---

### UC-5: Bounded Context Inventory

**Description**: Machine-readable inventory of all repositories, bounded contexts, and their relationships.

**Acceptance Criteria**:
- [ ] Repository taxonomy defined in `docs/governance/repository_taxonomy.yaml`
- [ ] Taxonomy validates against `docs/governance/repository_taxonomy.schema.json`
- [ ] Each repository has: name, slug, type, primary language, bounded contexts, status
- [ ] At least 10 repositories cataloged from the Insightpulseai org
- [ ] CI validator checks taxonomy on every push

---

## Data Model

### Bounded Context

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique identifier (e.g., `odoo-erp`) |
| `name` | string | Human-readable name |
| `system` | string | System of record |
| `promotion_state` | enum | `repo-only`, `configured`, `deployed`, `live` |
| `health_status` | enum | `healthy`, `degraded`, `unhealthy`, `unknown` |
| `last_health_check` | datetime | ISO 8601 timestamp |
| `kpi_ids` | array[string] | KPIs owned by this context |
| `event_ids` | array[string] | Events produced by this context |
| `evidence_path` | string | Path to latest evidence directory |

### KPI

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | `kpi_NNN` format |
| `name` | string | Human-readable name |
| `owner` | string | Bounded context ID |
| `source` | string | Data source reference |
| `target` | string | Target value with unit |
| `threshold_warn` | number | Warning threshold |
| `threshold_critical` | number | Critical threshold |
| `unit` | string | Measurement unit |
| `frequency` | string | Collection cadence |
| `current_value` | number | Latest measured value (null if unmeasured) |
| `evidence` | string | How to verify |

### Event

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | `evt_NNN` format |
| `name` | string | Dot-notation name |
| `source` | string | Producing bounded context |
| `schema` | object | JSON Schema |
| `kpi_linkage` | array[string] | KPIs this event feeds |

### Promotion Record

| Field | Type | Description |
|-------|------|-------------|
| `context_id` | string | Bounded context |
| `from_state` | enum | Previous state |
| `to_state` | enum | New state |
| `timestamp` | datetime | When transition occurred |
| `actor` | string | Who initiated |
| `evidence_path` | string | Evidence directory path |
| `verification` | enum | `pass`, `fail` |

---

## Integration Points

### Plane (Workspace OS)

- **What**: Tasks and issues for Control Room development tracked in Plane
- **Sync direction**: Plane --> Supabase `ctrl.identity_map` (via n8n webhook)
- **Current state**: repo-only (spec exists at `spec/odoo-workspace-os/`)
- **Relevant spec**: `docs/architecture/CANONICAL_ENTITY_MAP.yaml` (Plane section)

### Databricks (Intelligence Plane)

- **What**: KPI historical data stored in gold tables; anomaly detection on metrics
- **Sync direction**: Supabase/Odoo --> Databricks bronze --> silver --> gold
- **Current state**: repo-only (spec exists at `spec/databricks-apps-control-room/`)
- **Relevant spec**: `spec/databricks-apps-control-room/prd.md`

### Azure/Foundry (Agent Platform)

- **What**: Copilot tools for querying Control Room state; agent actions for remediation
- **Sync direction**: Control Room KPIs --> Foundry tool context
- **Current state**: repo-only (spec exists at `spec/odoo-copilot-azure/`)
- **Relevant spec**: `spec/odoo-copilot-azure/constitution.md`

### Supabase (Control Plane)

- **What**: Integration state store; `ctrl.*` schema for identity map and event log
- **Sync direction**: All systems --> Supabase `ctrl.*` for integration metadata
- **Current state**: repo-only (spec exists at `spec/integration-control-plane/`)
- **Relevant spec**: `spec/integration-control-plane/constitution.md`

### n8n (Automation Layer)

- **What**: Workflow execution for syncs, alerts, and event routing
- **Current state**: repo-only (workflow templates exist in `n8n/`)
- **Note**: n8n is self-hosted on the DO droplet at `n8n.insightpulseai.com`

### GitHub (Source Control & CI/CD)

- **What**: Repository governance, CI validators, workflow execution
- **Current state**: repo-only (workflows exist in `.github/workflows/`)
- **Note**: CI validators for KPI/event contracts are a Phase 0 deliverable

---

## Non-Goals

1. **Not a general-purpose BI tool** -- Superset and Databricks handle analytics
2. **Not a replacement for system-specific monitoring** -- each system keeps its own observability
3. **Not an ETL orchestrator** -- n8n and Databricks DLT handle data movement
4. **Not a user-facing application** -- this is an internal operations platform
5. **Not an alternative to Odoo for financial data** -- financial transactions stay in Odoo

---

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Bounded contexts with accurate state tracking | 7/7 | `CONTROL_ROOM_RUNTIME_STATE.md` |
| KPIs with machine-readable contracts | 17/17 | `control_room_kpis.yaml` |
| Event contracts with JSON Schema | 11/11 | `control_room_events.yaml` |
| CI validator pass rate | 100% on main | GitHub Actions |
| Time from state change to evidence | < 4 hours | Promotion records |
| Governance violations detected | 0 on main branch | CI lint |

---

## Cross-References

- `spec/control-room-platform/constitution.md` -- Non-negotiable rules
- `spec/control-room-platform/plan.md` -- Phased rollout plan
- `spec/control-room-platform/tasks.md` -- 48 tasks across 9 workstreams
- `spec/control-room-api/prd.md` -- Control Room API (job orchestration)
- `spec/integration-control-plane/prd.md` -- Supabase integration control plane
- `spec/databricks-apps-control-room/prd.md` -- Databricks connector monitoring
- `spec/odoo-copilot-azure/prd.md` -- Azure copilot integration
- `docs/architecture/CANONICAL_ENTITY_MAP.yaml` -- Entity ownership contract
