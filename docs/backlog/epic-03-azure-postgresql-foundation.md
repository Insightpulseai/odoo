# Epic 03 — Pulser for Odoo: Azure PostgreSQL Foundation and Resilience

> Platform/data backlog establishing Azure Database for PostgreSQL Flexible Server as the canonical transactional database for Odoo. **Not** an Odoo custom-module backlog.

**Success criteria:** canonical Azure PostgreSQL architecture approved; HA/resilience posture selected; environment provisioning standardized; backup/restore/failover/connection policies defined; agent/data sidecar access boundaries documented.

**Reference samples:**
- `Azure-Samples/azure-fastapi-postgres-flexible-appservice` — azd/App Service/GitHub workflow deployment patterns (FastAPI app, not Odoo template)
- `Azure-Samples/Azure-PostgreSQL-Resiliency-Architecture` — zonal/zone-redundant/regional posture (Terraform; adapt architecture choices, not IaC format)
- `Azure-Samples/postgres-agents` — LangGraph/Azure AI Agent Service sidecar pattern (stays OUTSIDE Odoo business modules)

**Doctrine anchor:** Azure Database for PostgreSQL Flexible Server is the **transactional database plane** for Odoo. Not the reporting plane, not the lakehouse plane, not the general agent-runtime plane.

---

## Feature 1 — Plan Azure PostgreSQL Architecture

Tags: `pulser-odoo`, `azure-postgresql`, `architecture`

### Story 1.1 — Define canonical Azure PostgreSQL role in the platform
Azure PG defined as transactional OLTP store for Odoo. Boundaries vs Databricks/Fabric documented. Boundaries vs Foundry/agent runtime documented. Approved + disallowed access paths.

### Story 1.2 — Select HA and resilience topology
Decision recorded: zonal vs zone-redundant vs regional. SLA, RPO, RTO targets. Failover behavior. Trade-offs (cost, latency, complexity).

### Story 1.3 — Define environment topology for PostgreSQL
Dev/staging/prod DB topology. Environment isolation rules. Naming, backup, retention. Connection + secret ownership.

---

## Feature 2 — Provision and Standardize PostgreSQL Platform

Tags: `pulser-odoo`, `azure-postgresql`, `provisioning`

### Story 2.1 — Create canonical provisioning pattern
Canonical IaC path (Bicep + AVM preferred). Required parameters + defaults. Network + identity dependencies. Environment bootstrap sequence.

### Story 2.2 — Define app-to-database connectivity pattern
Connection policy. Secret + credential flow (Azure Key Vault). Rotation/update procedure. Local/dev/test equivalents.

### Story 2.3 — Define GitHub/Azure deployment integration for PostgreSQL-backed services
CI/CD interaction model. Migration execution point in pipeline. Failure/rollback behavior. Environment-specific deployment rules.

---

## Feature 3 — Implement Resilience, Backup, and Recovery

Tags: `pulser-odoo`, `azure-postgresql`, `resilience`

### Story 3.1 — Define backup and restore policy
Backup retention policy. Restore procedures. Recovery validation. Ownership + approval rules.

### Story 3.2 — Define failover and continuity runbook
Failover triggers. Operational steps. Post-failover validation. Failback/stabilization.

### Story 3.3 — Validate resilience posture through rehearsal
Rehearsal plan. Recovery validation criteria. Outcome evidence captured. Remediation items tracked.

---

## Feature 4 — Harden Performance and Operations

Tags: `pulser-odoo`, `azure-postgresql`, `performance`

### Story 4.1 — Define performance baseline for Odoo on Azure PostgreSQL
Baseline metrics. Query + transaction performance targets. App-level + DB-level ownership. Regression thresholds.

### Story 4.2 — Define PostgreSQL observability and alerting model
Core health metrics. Alert conditions. Dashboard ownership. Escalation + response routing.

### Story 4.3 — Define maintenance and upgrade policy
Maintenance windows. Version + extension policy. Pre-change + post-change validation.

---

## Feature 5 — Define Data and Agent Access Boundaries

Tags: `pulser-odoo`, `azure-postgresql`, `boundaries`

### Story 5.1 — Define Odoo transactional access model
Approved direct writers. Read-only + admin categories. Migration/admin exceptions. Audit expectations.

### Story 5.2 — Define agent-side access pattern for PostgreSQL
Agent access model. Allowed read/write behavior. Safe tooling/service boundary. Direct agent-to-OLTP anti-patterns documented.

### Story 5.3 — Define extraction path from PostgreSQL to lakehouse/reporting plane
Extract/sync pattern (to Databricks bronze). Ownership between OLTP + analytics teams. Freshness expectations. Failure/retry.

---

## Feature 6 — Benchmark and Adapt Official Azure References

Tags: `pulser-odoo`, `azure-postgresql`, `benchmark`

### Story 6.1 — Assess Azure FastAPI PostgreSQL sample for reusable deployment patterns
Reusable pieces identified. Non-applicable pieces identified. azd/App Service/GitHub workflow learnings captured. Adaptation notes added to architecture docs.

### Story 6.2 — Assess Azure PostgreSQL resiliency architecture for production standard
Relevant resilience pattern selected. Pattern-to-environment mapping. Required IaC/workflow adaptations (Terraform → Bicep). Gap follow-ups.

### Story 6.3 — Assess PostgreSQL agents sample for sidecar agent pattern
Relevant sidecar patterns. LangGraph/Azure AI Agent Service applicability. Odoo integration boundary. Non-goals documented.

---

## Priority sequencing

**P0:** 1.1, 1.2, 2.1, 2.2, 3.1
**P1:** 2.3, 4.2, 5.1, 5.3, 6.2
**P2:** 3.3, 4.3, 5.2, 6.1, 6.3
