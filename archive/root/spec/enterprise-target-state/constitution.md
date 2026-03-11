# Constitution — Enterprise Target State

## Non-Negotiable Rules

### Rule 1: 5-Layer Model Is Authoritative

The 5-layer org model defined in `ssot/github/desired-end-state.yaml` (`org_layers`) is the canonical classification for all repositories. Every active repo must belong to exactly one layer (1-3). Layer 4 covers non-repo governance surfaces. Layer 5 repos hold no canonical logic.

### Rule 2: Repo Is System of Record

The Git repository is the single source of truth for all project artifacts. No external system (Plane, Slack, Figma, n8n UI) holds canonical state. Changes in external systems must be exported back to the repo.

### Rule 3: Plane Is SoW-Only

Plane is exclusively a Statement of Work surface. It tracks work items, initiatives, and epics. It is NOT a System of Record. Canonical state for code, infrastructure, and SSOT lives in Git. Plane reflects work status but never becomes authoritative.

### Rule 4: Strategic OKRs Reference Operational KPIs

Every strategic objective in `ssot/governance/enterprise_okrs.yaml` must cross-reference operational KPIs from `platform/data/contracts/control_room_kpis.yaml`. OKR key results without KPI linkage are not measurable and must not be committed.

### Rule 5: Databricks Maturity Is Phase-Gated

Databricks workspace progression follows the maturity phases in `ssot/databricks/workspace.yaml`. Advancing to the next phase requires meeting all listed prerequisites. No phase may be skipped.

### Rule 6: Slack Is Interaction Surface Only

Slack is used for notifications, approvals, and ChatOps. It is NOT a system of record. All state transitions triggered via Slack must flow through the integration backbone (n8n -> Odoo/Supabase) with audit trail in `ops.run_events`.

### Rule 7: SAP Maturity Is Operational Posture

"SAP-grade maturity" means SAP-like operational discipline (IaC, governed runtime, enterprise identity, release evidence, formal contracts). It does NOT mean SAP feature parity. Odoo CE handles ERP; Azure handles enterprise data/AI.

## Enforcement

- CI validator: `scripts/ci/validate_enterprise_okrs.py`
- Spec bundle: `spec/enterprise-target-state/`
- SSOT surface: `docs/architecture/PLATFORM_REPO_TREE.md` (`ssot/governance/` row)
