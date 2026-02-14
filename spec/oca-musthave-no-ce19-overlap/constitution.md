# OCA Must-Have (No CE19 Overlap) — Constitution

**Version:** 1.0.0
**Date:** 2026-02-15
**Status:** Active

---

## Purpose

Define the **OCA Must-Have system** as a **minimal viable OCA layer** for Odoo 19 CE installations, explicitly excluding modules absorbed into Odoo 19 CE core to prevent installation conflicts and maintain deterministic, reproducible deployments.

---

## Core Principles

### 1. Determinism
- **Explicit Exclusions**: All CE19 overlaps documented with rationale
- **Reproducible Installs**: Same install command → same modules every time
- **Version-Controlled Policy**: Exclusion list in source control with audit trail

### 2. Minimal Viable OCA Layer
- **Curated Essentials**: Only foundational OCA modules that enhance CE19 without duplication
- **Quality Over Quantity**: Better 67 reliable modules than 69 with conflicts
- **Progressive Enhancement**: Start minimal, add modules based on proven need

### 3. Manifest-Driven Configuration
- **YAML Manifests**: Declarative configuration for all module sets
- **Install Sets**: Modular installation via manifest-driven workflows
- **Meta-Module Pattern**: Single dependency tree for complete OCA stack

### 4. CI-Validated Compliance
- **Automated Drift Detection**: CI detects when OCA repos change vs manifests
- **Overlap Enforcement**: Block installations with CE19 duplicates
- **Validation Gates**: All changes require passing CI validation

---

## Hard Constraints

### Explicit Exclusions (Non-Negotiable)

**NO `web_advanced_search`**
**Rationale:** Absorbed into Odoo CE17+ core search functionality
**Evidence:** [odoo/odoo#...] (search improvements in CE17 release notes)
**Consequence:** Installing causes dependency conflicts with core web module

**NO `mail_activity_plan`**
**Rationale:** Absorbed into Odoo CE17+ core activity planning
**Evidence:** [odoo/odoo#...] (activity planning in CE17 release notes)
**Consequence:** Installing duplicates core mail/activity functionality

### Validation Requirements

**ALL changes require:**
1. CI validation passing
2. No CE19 overlapping modules in install sets
3. Meta-module installs cleanly without errors
4. Decision matrix updated with rationale

**Forbidden Actions:**
- Manually adding excluded modules to manifests
- Bypassing CI validation (`--no-verify`, `--skip-ci`)
- Installing meta-module in production without testing
- Modifying exclusion list without evidence and approval

---

## Allowed Operations

### Module Management
- ✅ Add new OCA modules (if no CE19 overlap detected)
- ✅ Update module versions via Git-Aggregator
- ✅ Remove modules from install sets (document rationale)
- ✅ Create specialized install sets (accounting-only, sales-only, etc.)

### Exclusion List Management
- ✅ Add new exclusions (with evidence + approval)
- ✅ Remove exclusions (if CE19 no longer includes functionality)
- ✅ Update exclusion rationale (improved evidence)

### CI/CD
- ✅ Extend drift-detection validation
- ✅ Add new validation steps
- ✅ Improve error messages and debugging

---

## Decision Framework

### INCLUDE / EXCLUDE / REVIEW_REQUIRED

**INCLUDE** (Default Policy)
- Module NOT found in CE19 core
- No dependency conflicts detected
- Available in OCA 19.0 branch
- **Action:** Add to install sets

**EXCLUDE** (Explicit Policy)
- Module functionality absorbed into CE19 core
- Installing causes dependency conflicts
- Evidence: CE19 release notes, code inspection, install testing
- **Action:** Add to exclusion list with rationale

**REVIEW_REQUIRED** (Manual Investigation)
- Partial overlap with CE19 (some features duplicate)
- Unclear CE19 parity status
- Conflicting evidence about absorption
- **Action:** Research → Document → Decision (INCLUDE or EXCLUDE)

---

## Enforcement Mechanisms

### CI Validation (`drift-detection` job)
```yaml
drift-detection:
  - check_ce19_overlap.py --strict
  - validate_install_sets.py
  - verify_meta_module.py
```

**Failure Criteria:**
- Excluded module found in install sets
- Meta-module dependencies out of sync
- Manifests reference non-existent OCA modules

### Pre-Commit Hooks (Optional)
```bash
pre-commit: check_overlap.py --local
```

### Code Review Requirements
- All manifest changes require explicit approval
- Exclusion list changes require evidence + 2 approvals
- Meta-module changes require install testing

---

## Governance

### Roles
- **Maintainer**: Approve exclusion list changes, CI configuration
- **Contributor**: Propose module additions/removals with rationale
- **CI System**: Enforce validation, block non-compliant changes

### Change Process
1. **Proposal**: GitHub issue with module name + rationale + evidence
2. **Research**: Investigate CE19 overlap, install conflicts
3. **Decision**: INCLUDE/EXCLUDE/REVIEW_REQUIRED documented in decision matrix
4. **Implementation**: Update manifests, exclusion list, meta-module
5. **Validation**: CI passes, meta-module installs cleanly
6. **Documentation**: Update decision matrix, source lists

---

## Rationale

**Why Explicit Exclusions?**
- **Determinism**: Hardcoded list prevents CI/CD variability
- **Audit Trail**: Git history shows who excluded what and why
- **Transparency**: Non-technical stakeholders can review exclusions
- **Performance**: Fast validation (dictionary lookup vs. module scanning)

**Why Meta-Module?**
- **Simplicity**: `odoo-bin -i ipai_oca_musthave_meta` installs entire stack
- **Dependency Resolution**: Odoo handles module dependency order
- **Rollback**: `odoo-bin -u ipai_oca_musthave_meta` or uninstall reverts changes
- **Testing**: Single install target for CI validation

**Why Manifest-Driven?**
- **Declarative**: YAML describes desired state, not imperative commands
- **Composable**: Create specialized sets (accounting-only, minimal, full)
- **Version-Controlled**: Git tracks all configuration changes
- **Reviewable**: Human-readable diffs for all changes

---

## Examples

### ✅ ALLOWED: Add New Module
```yaml
# Contributor proposal (GitHub issue)
Title: Add server_environment to base set
Rationale: Environment-based configuration for multi-stage deployments
Evidence: OCA/server-tools/server_environment (no CE19 overlap detected)
Decision: INCLUDE (no conflict with core)

# Implementation
# config/oca/oca_must_have_base.yml
modules:
  - server_environment  # NEW
```

### ❌ FORBIDDEN: Add Excluded Module
```yaml
# Attempt (blocked by CI)
# config/oca/oca_must_have_base.yml
modules:
  - web_advanced_search  # EXCLUDED

# CI Output
ERROR: Excluded module 'web_advanced_search' found in oca_must_have_base.yml
Rationale: Absorbed into CE17+ core search functionality
Action: Remove from manifest
```

### ✅ ALLOWED: Update Exclusion Rationale
```python
# scripts/oca_musthave/check_overlap.py
EXCLUDED_MODULES = {
    "web_advanced_search": "Absorbed into CE17+ core search (odoo/odoo#12345)",  # Improved evidence
}
```

---

## Compliance

**This constitution is binding.**
All OCA Must-Have operations MUST comply with these rules.
CI enforces non-negotiable constraints.
Human review validates governance processes.

**Violations:**
- CI blocks non-compliant changes
- Manual bypasses require documented exception approval
- Repeated violations trigger governance review

---

## References

- **Spec Bundle:** `/spec/oca-musthave-no-ce19-overlap/`
- **Exclusion List:** `scripts/oca_musthave/check_overlap.py`
- **Manifests:** `config/oca/oca_must_have_*.yml`
- **Meta-Module:** `addons/ipai/ipai_oca_musthave_meta/`
- **CI Workflow:** `.github/workflows/oca-must-have-gate.yml`

---

**Last Updated:** 2026-02-15
**Next Review:** Quarterly (or when CE20 release approaches)
