# OCA Must-Have (No CE19 Overlap) — Product Requirements Document

**Version:** 1.0.0
**Date:** 2026-02-15
**Status:** Active
**Owner:** InsightPulse AI
**Constitution:** [See constitution.md](./constitution.md)

---

## Executive Summary

Create a **deterministic OCA Must-Have module management system** that explicitly excludes modules absorbed into Odoo 19 CE core, preventing installation conflicts and maintaining a clean, minimal OCA layer for production deployments.

**Key Deliverables:**
- Spec Kit bundle documenting governance and filtering pipeline
- Deterministic CE19 overlap filter with explicit exclusion list (2 modules)
- Filtered install sets (69 candidates → 67 post-filter)
- Meta-module for one-command installation
- CI workflow detecting drift and enforcing overlap policy

---

## Problem Statement

### Current Pain Points

**1. CE19 Overlap Conflicts**
- OCA Must-Have lists contain modules now included in CE19 core
- Installing overlapping modules causes dependency conflicts
- Example: `web_advanced_search` conflicts with CE19 core search improvements
- Example: `mail_activity_plan` duplicates CE19 core activity planning

**2. Manual Tracking Overhead**
- No systematic tracking of which OCA modules overlap with CE19
- Developers manually research conflicts during installation
- Inconsistent decisions across environments (dev, staging, prod)

**3. Installation Fragility**
- `odoo-bin -i module1,module2,...module69` error-prone for 69 modules
- No validation that selected modules are conflict-free
- Difficult to rollback bad installations

**4. Drift Detection Gap**
- OCA repos change (new modules, deprecations)
- CE releases absorb more OCA functionality over time
- No automated detection when manifests become stale

### Business Impact

- **Deployment Risk**: Installation conflicts block production deployments
- **Maintenance Burden**: Manual conflict resolution on every install/upgrade
- **Inconsistency**: Different module sets across environments
- **Time Waste**: Developers spend hours researching module conflicts

---

## Proposed Solution

### System Components

**1. Spec Kit Bundle** (`spec/oca-musthave-no-ce19-overlap/`)
- **constitution.md**: Governance principles and hard constraints
- **prd.md**: This document (requirements and scope)
- **plan.md**: 4-phase implementation pipeline
- **tasks.md**: Task breakdown with verification criteria

**2. CE19 Overlap Filter** (`scripts/oca_musthave/check_overlap.py`)
- Explicit exclusion dictionary with rationale strings
- Deterministic filtering: 69 candidates → 67 modules
- JSON output with audit trail
- Exit codes for CI integration

**3. Documentation & Manifests** (`docs/oca/musthave/`)
- **source_lists.md**: Original 69 candidate modules (4 categories)
- **decision_matrix.md**: INCLUDE/EXCLUDE/REVIEW_REQUIRED table
- **install_sets.yml**: Generated manifest-ready module lists

**4. Meta-Module** (`addons/ipai/ipai_oca_musthave_meta/`)
- Single dependency tree with 67 filtered modules
- One-command installation: `odoo-bin -i ipai_oca_musthave_meta`
- Generated from install_sets.yml (single source of truth)

**5. CI Workflow** (`.github/workflows/oca-must-have-gate.yml`)
- Drift detection job validating manifests vs OCA repos
- Overlap enforcement blocking excluded modules
- Meta-module sync verification

---

## Scope

### In Scope

**Module Categories** (4 total):
1. **Base** (28 candidates → 26 post-filter)
2. **Accounting** (18 candidates → 18 post-filter)
3. **Sales** (11 candidates → 11 post-filter)
4. **Purchases** (12 candidates → 12 post-filter)

**Total:** 69 candidates → 67 post-filter (2 explicit exclusions)

**Explicit Exclusions:**
- `web_advanced_search` (CE overlap - absorbed into CE17+ core)
- `mail_activity_plan` (CE overlap - absorbed into CE17+ core)

**Features:**
- Deterministic filtering algorithm
- Human-readable decision matrix
- Manifest-driven install sets
- Meta-module for simplified installation
- CI-based drift detection
- Complete audit trail

### Out of Scope

**Not Included (v1.0):**
- Automated CE19 core module detection (future: parse odoo/addons/)
- Partial overlap handling (modules with some duplicate functionality)
- Version-specific filtering (same exclusion list for all CE19.x)
- Custom module conflict detection (only OCA vs CE19)
- Module recommendation engine (suggest modules based on use case)

**Future Enhancements:**
- `check_overlap.py --auto-detect` (scan CE19 core for overlaps)
- Partial overlap policy (INCLUDE with warnings)
- Version-aware filtering (different exclusions per CE version)
- Cross-module conflict detection (OCA module X conflicts with OCA module Y)

---

## Requirements

### Functional Requirements

**FR1: Zero CE19 Overlapping Modules**
- **Requirement:** Final install sets contain ZERO modules that overlap with CE19 core
- **Validation:** `grep -E "web_advanced_search|mail_activity_plan" config/oca/oca_must_have_*.yml` returns empty
- **Acceptance:** Meta-module installs without dependency conflicts

**FR2: Complete Decision Matrix**
- **Requirement:** All 69 candidate modules documented with INCLUDE/EXCLUDE decision
- **Validation:** Decision matrix has 69 rows (1 per module)
- **Acceptance:** Every module has rationale and evidence

**FR3: Meta-Module Installation**
- **Requirement:** Meta-module installs all 67 filtered modules in single command
- **Validation:** `odoo-bin -d test_db -i ipai_oca_musthave_meta --stop-after-init` exits 0
- **Acceptance:** 67 modules installed, no import errors, no dependency conflicts

**FR4: CI Drift Detection**
- **Requirement:** CI detects when OCA repos change vs manifests
- **Validation:** Manual edit adding excluded module → CI fails
- **Acceptance:** drift-detection job catches all violations

**FR5: Deterministic Filter Output**
- **Requirement:** Filter produces same output for same input every time
- **Validation:** Run `check_overlap.py` 10 times → identical output
- **Acceptance:** Always 2 exclusions (web_advanced_search, mail_activity_plan)

### Non-Functional Requirements

**NFR1: Performance**
- Filter execution: <5 seconds
- CI validation: <3 minutes total
- Meta-module install: <10 minutes

**NFR2: Maintainability**
- Exclusion list in source control (Git)
- All changes require code review
- Documentation updated with code

**NFR3: Auditability**
- Complete audit trail for all decisions
- Git history shows who excluded what and why
- Decision matrix references evidence (GitHub issues, release notes)

**NFR4: Reliability**
- CI validation passes 100% when manifests correct
- Meta-module install succeeds 100% in clean database
- Filter produces deterministic output (no randomness)

---

## User Stories

### Story 1: OCA Installation (Developer)
**As a** developer setting up a new Odoo 19 environment
**I want** to install all OCA Must-Have modules in one command
**So that** I can quickly bootstrap a production-ready environment

**Acceptance Criteria:**
- Single command: `odoo-bin -i ipai_oca_musthave_meta`
- All 67 modules installed
- No dependency conflicts
- Clean installation log (no errors/warnings)

### Story 2: Module Conflict Prevention (DevOps)
**As a** DevOps engineer deploying to production
**I want** automated validation that no CE19 overlapping modules are installed
**So that** I can prevent deployment of conflicting module sets

**Acceptance Criteria:**
- CI fails if excluded module added to manifest
- Clear error message with exclusion rationale
- Manual bypass requires explicit approval

### Story 3: Audit Trail (Compliance Officer)
**As a** compliance officer reviewing system changes
**I want** complete documentation of which modules are excluded and why
**So that** I can verify decision-making process and evidence

**Acceptance Criteria:**
- Decision matrix with all 69 modules
- Each exclusion has rationale + evidence
- Git history shows decision timeline

### Story 4: Drift Detection (Platform Team)
**As a** platform team member maintaining OCA integration
**I want** automated detection when OCA repos change vs our manifests
**So that** I can proactively update our module lists

**Acceptance Criteria:**
- CI runs on OCA repo changes (weekly cron)
- Alerts on manifest drift
- Actionable remediation steps

---

## Acceptance Criteria

### Phase 1: Spec Bundle ✅
- [ ] All 4 spec files exist (constitution, prd, plan, tasks)
- [ ] Constitution defines hard constraints
- [ ] PRD documents requirements and scope
- [ ] Plan outlines 4-phase implementation
- [ ] Tasks break down into 20 concrete actions

### Phase 2: Filter Algorithm ✅
- [ ] `check_overlap.py` excludes 2 modules
- [ ] Dry-run mode produces JSON output
- [ ] Exit code 0 when no violations, 1 when violations found
- [ ] Rationale strings documented for each exclusion

### Phase 3: Documentation ✅
- [ ] `source_lists.md` contains all 69 candidates
- [ ] `decision_matrix.md` has 69 rows with decisions
- [ ] `install_sets.yml` has 5 sets (base, accounting, sales, purchases, all)
- [ ] Post-filter counts: 26, 18, 11, 12, 67

### Phase 4: Meta-Module & CI ✅
- [ ] Meta-module manifest has 67 dependencies
- [ ] `odoo-bin -i ipai_oca_musthave_meta` succeeds
- [ ] CI drift-detection job passes
- [ ] Manual violation test → CI fails

---

## Success Metrics

**Deployment Success Rate**
- **Baseline**: 80% (manual module selection, conflicts common)
- **Target**: 100% (meta-module with deterministic filtering)

**Time to Bootstrap Environment**
- **Baseline**: 2-4 hours (manual module research + install)
- **Target**: <30 minutes (meta-module one-command install)

**Conflict Resolution Time**
- **Baseline**: 1-2 hours per conflict (manual debugging)
- **Target**: 0 hours (zero conflicts by design)

**Audit Trail Completeness**
- **Baseline**: 0% (no documentation)
- **Target**: 100% (decision matrix with evidence)

---

## Dependencies

### Upstream Dependencies
- OCA repositories with 19.0 branches
- Git-Aggregator configuration (`config/oca-repos.yaml`)
- Existing must-have manifests (`config/oca/oca_must_have_*.yml`)

### Downstream Dependencies
- Odoo 19 CE installation
- PostgreSQL database
- CI runner with Python + Odoo dependencies

### External Dependencies
- GitHub API (for OCA repo availability checks)
- OCA release schedule (19.0 branch maturity)

---

## Risks & Mitigation

### Risk 1: OCA 19.0 Branch Availability
**Risk:** OCA repos may not have complete 19.0 branches yet
**Impact:** Cannot install some modules
**Likelihood:** Medium (OCA typically lags CE releases)
**Mitigation:**
- CI validation checks branch availability via GitHub API
- Fallback to 18.0 branches with explicit warnings
- Weekly CI run detects when 19.0 branches become available

### Risk 2: New CE19 Absorptions Undiscovered
**Risk:** Hardcoded exclusion list may miss new CE19 overlaps
**Impact:** Installation conflicts in production
**Likelihood:** Low (CE19 release notes document changes)
**Mitigation:**
- Manual review of OCA module descriptions vs CE19 release notes
- Monitor OCA/community discussions for deprecation notices
- Quarterly audit of exclusion list against CE19 changelog

### Risk 3: Meta-Module Dependency Hell
**Risk:** Circular dependencies or version conflicts in meta-module
**Impact:** Meta-module fails to install
**Likelihood:** Low (OCA modules designed for composition)
**Mitigation:**
- Dependency graph validation script checks for cycles
- Staged installation in dependency order
- CI integration test in clean PostgreSQL database

### Risk 4: Documentation Drift
**Risk:** `decision_matrix.md` gets out of sync with `install_sets.yml`
**Impact:** Audit trail inaccurate
**Likelihood:** Medium (human error during updates)
**Mitigation:**
- Both files generated from same source (`check_overlap.py` output)
- CI validation compares timestamps and content hashes
- Pre-commit hook prevents commit if docs out of sync

---

## Timeline

**Estimated Total:** 8-12 hours

| Phase | Deliverables | Time | Validation |
|-------|-------------|------|--------------|
| 1 | Spec bundle (4 files) | 2-3h | Files exist, content complete |
| 2 | Filter script | 2-3h | 2 exclusions detected |
| 3 | Documentation (3 files) | 2-3h | Decision matrix has 69 rows |
| 4 | Meta-module + CI | 2-3h | Meta-module installs cleanly |

**Milestones:**
- Week 1: Spec bundle + filter algorithm complete
- Week 2: Documentation + meta-module complete
- Week 3: CI integration + end-to-end validation

---

## Appendices

### Appendix A: Initial Allowlist (69 Candidates)

**Base (28):** base_technical_features, base_search_fuzzy, base_exception, base_tier_validation, base_user_role, base_jsonify, base_sparse_field, base_suspend_security, base_custom_info, base_menu_visibility_restriction, base_technical_user, base_fontawesome, base_import_async, queue_job, web_widget_x2many_2d_matrix, **web_advanced_search** ⚠️, **mail_activity_plan** ⚠️, web_refresher, web_domain_field, web_pwa_oca, web_notify, web_m2x_options, web_responsive, web_timeline, web_widget_digitized_signature, web_dialog_size, web_search_with_and, web_ir_actions_act_multi

**Accounting (18):** account_fiscal_year, account_move_line_purchase_info, account_move_line_sale_info, account_invoice_refund_link, account_usability, account_payment_partner, account_tag_menu, account_type_menu, account_move_tier_validation, account_statement_import, account_lock_to_date, account_invoice_constraint_chronology, account_cost_center, account_journal_lock_date, account_reconcile_oca, account_invoice_view_payment, account_chart_update, account_financial_report

**Sales (11):** sale_automatic_workflow, sale_exception, sale_tier_validation, sale_order_type, sale_order_invoicing_grouping_criteria, sale_order_line_date, sale_delivery_state, sale_stock_mto_as_mts_orderpoint, sale_order_priority, sale_force_invoiced, sale_validity

**Purchases (12):** purchase_exception, purchase_tier_validation, purchase_order_type, purchase_order_line_price_history, purchase_order_secondary_unit, purchase_last_price_info, purchase_work_acceptance, purchase_landed_cost, purchase_discount, purchase_order_analytic, purchase_order_approved, purchase_security

### Appendix B: Excluded Modules (2 Total)

1. **web_advanced_search**
   - **Category:** Base
   - **Rationale:** Absorbed into Odoo CE17+ core search functionality
   - **Evidence:** [odoo/odoo#...] (search improvements in CE17 release notes)
   - **Impact:** Dependency conflicts with core web module

2. **mail_activity_plan**
   - **Category:** Base
   - **Rationale:** Absorbed into Odoo CE17+ core activity planning
   - **Evidence:** [odoo/odoo#...] (activity planning in CE17 release notes)
   - **Impact:** Duplicates core mail/activity functionality

### Appendix C: Related Specifications

- **Constitution:** [constitution.md](./constitution.md)
- **Implementation Plan:** [plan.md](./plan.md)
- **Task Breakdown:** [tasks.md](./tasks.md)
- **OCA Workflow:** `/docs/ai/OCA_WORKFLOW.md`
- **Git-Aggregator Config:** `/config/oca-repos.yaml`

---

**Last Updated:** 2026-02-15
**Next Review:** Quarterly (or when CE20 release approaches)
