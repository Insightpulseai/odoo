# Tasks — Enterprise Target State

## Top 5 Immediate Actions

From Section 12 of the consolidated target state document.

### Task 1: Lock Canonical Repo Taxonomy

- **Status**: DONE
- **Owner**: Platform team
- **Action**: Assign owner/type/lifecycle to every active repo in `infra/ssot/github/desired-end-state.yaml`
- **Deliverable**: `org_layers` and `repo_metadata_required` sections added
- **Verification**: All 9 active repos classified into layers 1-3

### Task 2: Stand Up Org-Level GitHub Projects + Map Plane Taxonomy

- **Status**: PENDING
- **Owner**: Platform team
- **Action**: Create 3 org-level GitHub Projects (Roadmap, Execution Board, Backlog); map Plane taxonomy areas
- **Deliverable**: GitHub Projects created; `infra/ssot/plane/config.yaml` `project_taxonomy` section
- **Verification**: `gh project list --owner Insightpulseai` shows 3 projects
- **Note**: Iteration values (Quarter/Sprint) require UI setup (GitHub API limitation)

### Task 3: Databricks Shared Sandbox Baseline

- **Status**: PARTIAL (workspace exists, maturity model codified)
- **Owner**: Data team
- **Action**: Ensure shared workspace has IaC + Unity Catalog baseline
- **Deliverable**: `infra/ssot/databricks/workspace.yaml` `maturity_phases` section; Phase 1 active
- **Verification**: Databricks workspace accessible; Unity Catalog catalogs verified

### Task 4: Formalize Slack Integration Contracts

- **Status**: PENDING
- **Owner**: Integration team
- **Action**: Document Slack event routes, audit requirements, approval flows as integration contracts
- **Deliverable**: Integration contract in `docs/contracts/` (when Slack becomes a data flow boundary)
- **Verification**: Slack events routed through n8n with ops.run_events audit trail

### Task 5: OKR/KPI Scorecard from Architecture Docs

- **Status**: DONE
- **Owner**: Platform team
- **Action**: Convert architecture docs into machine-readable OKR/KPI scorecard
- **Deliverable**: `infra/ssot/governance/enterprise_okrs.yaml` with CI validator
- **Verification**: `python3 odoo/scripts/ci/validate_enterprise_okrs.py` passes

## Implementation Tasks

- [x] Phase 1: Create `infra/ssot/governance/enterprise_okrs.yaml`
- [x] Phase 2a: Update `infra/ssot/github/desired-end-state.yaml`
- [x] Phase 2b: Update `infra/ssot/plane/config.yaml`
- [x] Phase 2c: Update `infra/ssot/databricks/workspace.yaml`
- [x] Phase 3: Update governance docs
- [x] Phase 4: Create spec bundle
- [x] Phase 5: Create CI validator
- [x] Phase 6: Cross-reference updates
