# Control Room Platform -- Constitution

> **Version**: 1.0.0
> **Status**: Active
> **Last Updated**: 2026-03-07
> **Activation State**: repo-only (specs and contracts exist, no runtime deployment)

---

## Purpose

The Control Room Platform is the enterprise instrumentation and governance layer for InsightPulse AI. It provides observability, KPI tracking, and governance across 7 bounded contexts that collectively form the IPAI operational stack. This constitution defines the non-negotiable rules that govern all Control Room artifacts, integrations, and runtime behavior.

---

## Non-Negotiables

### 1. Single Source of Truth Per Bounded Context

Each bounded context has exactly ONE system of record. No data duplication across contexts for authoritative state.

| Bounded Context | System of Record | Owns |
|----------------|-----------------|------|
| **Odoo ERP** | Odoo CE 19 + PostgreSQL 16 | Financial transactions, HR, CRM, approvals, expenses |
| **Supabase** | Supabase (`spdtwktxdalcfigzeqrz`) | Identity map, sync state, integration events, entity links |
| **Databricks** | Databricks Unity Catalog | Bronze/silver/gold tables, ML models, analytics |
| **Plane** | Plane workspace | Projects, issues, cycles, coordination |
| **n8n** | n8n self-hosted | Workflow definitions, execution history, credentials |
| **Azure/Foundry** | Azure AI Foundry | Agent definitions, tool registrations, copilot configs |
| **GitHub** | GitHub (`Insightpulseai` org) | Source code, CI/CD pipelines, issue tracking |

**Violation**: Any system storing authoritative data that belongs to another context is a constitutional violation. Read-only replicas for analytics (Databricks) and integration metadata (Supabase `ctrl.*`) are permitted.

---

### 2. Promotion State Machine

Every bounded context and every artifact has a promotion state. States are strictly ordered and transitions require evidence.

```
repo-only --> configured --> deployed --> live
```

| State | Definition | Evidence Required |
|-------|-----------|-------------------|
| `repo-only` | Specs, contracts, and code exist in the repository | File paths in repo |
| `configured` | Environment variables, secrets, and connections are provisioned | Config verification script output |
| `deployed` | Runtime services are running in staging or production | Health check HTTP 200 + container logs |
| `live` | Production traffic is flowing and monitored | Metrics showing real data flow + alerting active |

**Non-negotiable**: No artifact, service, or integration may claim a state it has not achieved with evidence. Overclaiming is a governance violation.

---

### 3. Evidence Requirements

Every state transition produces evidence stored in `docs/evidence/<YYYYMMDD-HHMM>/<scope>/`.

| Transition | Required Evidence |
|------------|-------------------|
| repo-only --> configured | Secrets provisioned (names only, never values), connection test pass |
| configured --> deployed | Container running, health endpoint 200, DB migration applied |
| deployed --> live | Metrics flowing, alerting configured, first real transaction processed |

**Format**: Evidence must include:
- Timestamp (ISO 8601)
- Actor (human or CI job)
- Verification command and output
- Pass/fail determination

---

### 4. KPI Contracts Are Machine-Readable

All KPI definitions MUST be in YAML format at `platform/data/contracts/control_room_kpis.yaml`. Prose descriptions in PRDs or plans do not constitute a KPI contract.

Each KPI contract MUST include:
- `id`: Unique identifier (`kpi_NNN`)
- `name`: Human-readable name
- `owner`: Bounded context that produces the metric
- `source`: Specific table, model, or API endpoint
- `target`: Quantified target value with unit
- `threshold_warn` and `threshold_critical`: Numeric thresholds
- `unit`: Measurement unit
- `frequency`: Collection frequency
- `evidence`: How to verify the metric

---

### 5. Event Contracts Define Schema Before Implementation

No cross-system event may be implemented without a contract in `platform/data/contracts/control_room_events.yaml`.

Each event contract MUST include:
- `id`: Unique identifier (`evt_NNN`)
- `name`: Dot-notation event name
- `source`: Producing bounded context
- `schema`: JSON Schema for the event payload
- `kpi_linkage`: Which KPIs this event feeds

**Enforcement**: CI validators MUST reject PRs that add event handlers without a corresponding contract.

---

### 6. No Overclaiming

This is the most critical rule. The Control Room governance layer exists precisely to prevent false status claims.

**Prohibited phrases in any IPAI document**:
- "deployed" when the state is `repo-only` or `configured`
- "production-ready" without deployment evidence
- "integrated" without a working sync pipeline
- "monitoring active" without alerting configuration proof

**Remediation**: Any document found to overclaim MUST be corrected within 24 hours of detection. CI lint rules enforce this where possible.

---

### 7. Governance Hierarchy

```
constitution.md (this file -- non-negotiable)
    |
    +--> prd.md (product requirements -- what to build)
    |
    +--> plan.md (phased rollout -- when to build)
    |
    +--> tasks.md (concrete tasks -- who does what)
    |
    +--> platform/data/contracts/ (machine-readable contracts)
    |
    +--> docs/architecture/CONTROL_ROOM_RUNTIME_STATE.md (honest status)
    |
    +--> docs/governance/ (taxonomy, schemas, policies)
```

---

## Boundaries

### 8. Bounded Context Independence

Each bounded context:
- Operates independently and can be promoted through states on its own schedule
- Has its own health check endpoint (when deployed)
- Has its own KPI set
- Can be rolled back without affecting other contexts
- Communicates with other contexts ONLY through defined event contracts

---

### 9. Financial Data Sovereignty

All financial transactions, tax filings, and regulatory compliance data MUST remain in Odoo ERP (PostgreSQL 16). This is inherited from `docs/architecture/CANONICAL_ENTITY_MAP.yaml` and is non-negotiable.

Databricks may hold read-only analytical copies in gold tables. No other system may hold authoritative financial records.

---

## Cross-References

- `spec/integration-control-plane/constitution.md` -- Supabase `ctrl.*` schema rules
- `spec/control-room-api/constitution.md` -- Control Room API orchestration rules
- `spec/databricks-apps-control-room/prd.md` -- Databricks connector monitoring
- `docs/architecture/CANONICAL_ENTITY_MAP.yaml` -- Cross-system ownership contract
- `docs/architecture/INTEGRATION_BOUNDARY_MODEL.md` -- System boundary definitions
- `spec/odoo-copilot-azure/constitution.md` -- Azure/Foundry agent platform rules
- `spec/odoo-approval-inbox/constitution.md` -- Approval workflow governance
