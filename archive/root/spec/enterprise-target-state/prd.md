# PRD — Enterprise Target State

## Overview

Codify the consolidated enterprise operating model as machine-readable SSOT artifacts with CI validation. Covers KPI/OKR framework, 5-layer org model, Plane project taxonomy, Databricks maturity phases, and system-of-record boundaries.

## Acceptance Criteria

### AC-1: Strategic OKR YAML

- [ ] `ssot/governance/enterprise_okrs.yaml` exists with schema_version
- [ ] 5 strategic objectives (A-E) with key_results and kpi_ref
- [ ] 3 canonical OKRs (O1-O3) with parent_objectives and key_results
- [ ] kpi_index maps objectives to KPI IDs from `control_room_kpis.yaml`
- [ ] Every kpi_ref resolves to a valid KPI ID (kpi_001 through kpi_017)

### AC-2: 5-Layer Org Model

- [ ] `ssot/github/desired-end-state.yaml` has `org_layers` section
- [ ] 5 layers defined with repos/systems assigned
- [ ] `repo_metadata_required` lists mandatory fields
- [ ] All 9 active repos appear in exactly one layer (1-3)

### AC-3: Plane Project Taxonomy

- [ ] `ssot/plane/config.yaml` has `project_taxonomy` section
- [ ] 6 areas defined with layer_ref cross-references
- [ ] `work_item_hierarchy` defines 4 levels with required_fields

### AC-4: Databricks Maturity Phases

- [ ] `ssot/databricks/workspace.yaml` has `maturity_phases` section
- [ ] 3 phases defined (shared sandbox, dev/prod split, full dev/stage/prod)
- [ ] `current` field set to `phase_1`
- [ ] Each phase has trigger and prerequisites

### AC-5: Governance Anchor Document

- [ ] `docs/governance/ENTERPRISE_OPERATING_MODEL.md` expanded with:
  - 5-layer org model summary
  - Strategic OKR summary
  - System-of-record matrix (Slack as interaction surface)
  - Roadmap linking model
  - Azure maturity benchmark
  - Databricks progression cross-ref
  - Canonical references table

### AC-6: ERP Positioning Update

- [ ] `docs/governance/ERP_POSITIONING.md` has SAP maturity framing section
- [ ] Pricing positioning section added

### AC-7: CI Validator

- [ ] `scripts/ci/validate_enterprise_okrs.py` validates YAML structure
- [ ] Validates kpi_ref references against control_room_kpis.yaml
- [ ] Validates parent_objectives references
- [ ] Exit 0 on success, exit 1 on failure

### AC-8: Cross-References

- [ ] `docs/architecture/PLATFORM_REPO_TREE.md` has `ssot/governance/` row
- [ ] `docs/governance/ENTERPRISE_KPI_MODEL.md` cross-refs OKR YAML
- [ ] `docs/governance/ENTERPRISE_STACK_INDEX.md` lists spec bundle

## Out of Scope

- Pricing YAML (business strategy, not machine-enforceable)
- Monolithic dump file (content distributed to existing SSOT domains)
- New cross-boundary contracts (no new data flows introduced)
