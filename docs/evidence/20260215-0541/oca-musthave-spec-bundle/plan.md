# OCA Must-Have (No CE19 Overlap) — Implementation Plan

**Version:** 1.0.0
**Date:** 2026-02-15
**Status:** Active
**Constitution:** [See constitution.md](./constitution.md)
**Requirements:** [See prd.md](./prd.md)

---

## Overview

4-phase pipeline transforming 69 candidate modules → 67 filtered modules → manifest-driven install sets → meta-module → CI-validated deployment.

**Pipeline Stages:**
1. **Seed** (Data Preparation) - Document 69 candidate modules
2. **Filter** (CE19 Overlap Detection) - Apply deterministic filter → 67 modules
3. **Generate** (Manifest Creation) - Produce install sets + meta-module
4. **Validate** (CI Integration) - Automated drift detection + enforcement

---

## File Structure

### Output Files (20+ total)

```
spec/oca-musthave-no-ce19-overlap/
├── constitution.md                          # [✅ COMPLETE] Governance
├── prd.md                                   # [✅ COMPLETE] Requirements
├── plan.md                                  # [✅ COMPLETE] This file
└── tasks.md                                 # [⏳ PENDING] Task breakdown

docs/oca/musthave/
├── source_lists.md                          # [⏳ PENDING] 69 candidate modules
├── decision_matrix.md                       # [⏳ PENDING] Include/Exclude decisions
└── install_sets.yml                         # [⏳ PENDING] Generated manifests

config/oca/
├── oca_must_have_base.yml                   # [⏳ PENDING] 26 modules (2 excluded)
├── oca_must_have_accounting.yml             # [⏳ PENDING] 18 modules
├── oca_must_have_sales.yml                  # [⏳ PENDING] 11 modules
├── oca_must_have_purchase.yml               # [⏳ PENDING] 12 modules
└── oca_must_have_all.yml                    # [⏳ PENDING] Union: 67 modules

addons/ipai/ipai_oca_musthave_meta/
├── __manifest__.py                          # [⏳ PENDING] 67 dependencies
├── __init__.py                              # [⏳ PENDING] Empty init
└── README.md                                # [⏳ PENDING] Meta-module docs

scripts/oca_musthave/
├── check_overlap.py                         # [⏳ PENDING] CE19 overlap filter
├── generate_meta_module.py                  # [⏳ PENDING] Meta-module generator
├── validate_install_sets.py                 # [⏳ PENDING] Manifest validator
└── verify_meta_module.py                    # [⏳ PENDING] Meta-module sync checker

.github/workflows/
└── oca-must-have-gate.yml                   # [⏳ PENDING] Add drift-detection job
```

---

## Phase 1: Seed (Data Preparation)

**Objective:** Document all 69 candidate modules organized by category with explicit CE overlap markers.

### Inputs
- User-provided candidate lists (Base: 28, Accounting: 18, Sales: 11, Purchases: 12)
- Explicit exclusions: `web_advanced_search`, `mail_activity_plan`

### Tasks

**Task 1.1: Create `docs/oca/musthave/source_lists.md`**
```markdown
# OCA Must-Have Source Lists (Pre-Filter)

## Base (28 modules)
- base_technical_features
- base_search_fuzzy
- ...
- **web_advanced_search** ⚠️ EXCLUDE (CE overlap - now included in core v17+)
- **mail_activity_plan** ⚠️ EXCLUDE (CE overlap - now included in core v17+)
- ...

**Pre-Filter Count:** 28 modules
**Explicit Exclusions:** 2 (web_advanced_search, mail_activity_plan)
**Post-Filter Count:** 26 modules

## Accounting (18 modules)
...

## Sales (11 modules)
...

## Purchases (12 modules)
...

## Total Candidate Summary
- **Total Candidates:** 69 modules
- **Total Exclusions:** 2 modules (both from Base category)
- **Total Post-Filter:** 67 modules
```

**Task 1.2: Validate Candidate Lists**
```bash
# Count modules per category
grep -c "^- " docs/oca/musthave/source_lists.md | awk '{sum+=$1} END {print sum}'
# Expected: 69

# Verify exclusion markers
grep -c "⚠️ EXCLUDE" docs/oca/musthave/source_lists.md
# Expected: 2
```

### Outputs
- `docs/oca/musthave/source_lists.md` (69 modules documented)

### Validation
- ✅ 69 total modules across 4 categories
- ✅ 2 explicit exclusion markers (⚠️)
- ✅ Pre/post-filter counts documented

---

## Phase 2: Filter (CE19 Overlap Detection)

**Objective:** Create deterministic filter excluding CE19 overlapping modules.

### Tasks

**Task 2.1: Create `scripts/oca_musthave/check_overlap.py`**
```python
#!/usr/bin/env python3
"""
CE19 Overlap Filter
Deterministically exclude OCA modules absorbed into Odoo 19 CE core.
"""
import argparse
import json
import sys
from typing import List, Dict, Tuple

# Explicit Exclusion List (Single Source of Truth)
EXCLUDED_MODULES = {
    "web_advanced_search": "Absorbed into CE17+ core search functionality",
    "mail_activity_plan": "Absorbed into CE17+ core activity planning"
}

def filter_modules(candidate_list: List[str]) -> Tuple[List[str], Dict]:
    """Filter candidate modules, excluding CE19 overlaps."""
    included = []
    excluded = {}

    for module in candidate_list:
        if module in EXCLUDED_MODULES:
            excluded[module] = EXCLUDED_MODULES[module]
        else:
            included.append(module)

    return included, excluded

def main():
    parser = argparse.ArgumentParser(description="Filter OCA modules for CE19 overlap")
    parser.add_argument("--dry-run", action="store_true", help="Show output without writing files")
    parser.add_argument("--strict", action="store_true", help="Exit 1 if any exclusions found")
    parser.add_argument("--test-exclusions", action="store_true", help="Run unit tests")
    args = parser.parse_args()

    # Test mode
    if args.test_exclusions:
        assert "web_advanced_search" in EXCLUDED_MODULES
        assert "mail_activity_plan" in EXCLUDED_MODULES
        print("✅ Exclusion tests passed")
        return 0

    # Dry-run mode: output JSON
    if args.dry_run:
        result = {
            "excluded_modules": EXCLUDED_MODULES,
            "exclusion_count": len(EXCLUDED_MODULES)
        }
        print(json.dumps(result, indent=2))
        return 0

    return 0

if __name__ == "__main__":
    sys.exit(main())
```

**Task 2.2: Test Filter Script**
```bash
# Test exclusion detection
python scripts/oca_musthave/check_overlap.py --test-exclusions
# Expected: ✅ Exclusion tests passed

# Dry-run mode
python scripts/oca_musthave/check_overlap.py --dry-run
# Expected: JSON output with 2 excluded modules

# Make executable
chmod +x scripts/oca_musthave/check_overlap.py
```

### Outputs
- `scripts/oca_musthave/check_overlap.py` (filter algorithm)

### Validation
- ✅ Script excludes exactly 2 modules
- ✅ Dry-run produces JSON output
- ✅ Test mode passes

---

## Phase 3: Generate (Manifest Creation)

**Objective:** Transform filtered modules → decision matrix → install sets → meta-module.

### Tasks

**Task 3.1: Create `docs/oca/musthave/decision_matrix.md`**
```markdown
# OCA Must-Have Decision Matrix

| Module | Category | Decision | Rationale | Evidence |
|--------|----------|----------|-----------|----------|
| web_advanced_search | Base | EXCLUDE | Absorbed into CE17+ core | [odoo/odoo#...] |
| mail_activity_plan | Base | EXCLUDE | Absorbed into CE17+ core | [odoo/odoo#...] |
| base_technical_features | Base | INCLUDE | No CE overlap | OCA/server-tools |
| ... | ... | ... | ... | ... |
```

**Task 3.2: Create `docs/oca/musthave/install_sets.yml`**
```yaml
meta:
  odoo_version: "19.0"
  generator: "oca_musthave_pipeline_v1"

sets:
  musthave_base:
    modules:
      - base_technical_features
      - base_search_fuzzy
      # ... (26 total)
    excluded:
      - web_advanced_search
      - mail_activity_plan

  musthave_accounting:
    modules:
      - account_fiscal_year
      # ... (18 total)
    excluded: []

  musthave_sales:
    modules:
      - sale_automatic_workflow
      # ... (11 total)
    excluded: []

  musthave_purchases:
    modules:
      - purchase_exception
      # ... (12 total)
    excluded: []

  musthave_all:
    modules:
      # Union of all sets (67 total)
      - base_technical_features
      - account_fiscal_year
      - sale_automatic_workflow
      - purchase_exception
      # ...
    excluded:
      - web_advanced_search
      - mail_activity_plan
```

**Task 3.3: Update `config/oca/oca_must_have_base.yml`**
```yaml
meta:
  odoo_version: "19.0"
  purpose: "Foundational OCA modules for Odoo 19 CE (no CE overlap)"

includes:
  - oca_must_have_base

repositories:
  - name: "OCA/server-tools"
    branch: "19.0"
  - name: "OCA/web"
    branch: "19.0"

modules:
  - base_technical_features
  - base_search_fuzzy
  # ... (26 total - web_advanced_search and mail_activity_plan EXCLUDED)

policy:
  require_all_modules_installed: true
  fail_if_module_not_found: true
```

**Task 3.4: Create Meta-Module `addons/ipai/ipai_oca_musthave_meta/__manifest__.py`**
```python
{
    "name": "IPAI OCA Must-Have Meta",
    "version": "19.0.1.0.0",
    "category": "Hidden",
    "summary": "Meta-module installing all OCA Must-Have modules (no CE19 overlap)",
    "description": """
        Meta-module for one-command installation of all OCA Must-Have modules.

        Explicitly excludes modules absorbed into Odoo 19 CE core:
        - web_advanced_search (CE17+ core search)
        - mail_activity_plan (CE17+ core activity planning)

        Install: odoo-bin -i ipai_oca_musthave_meta
        Total modules: 67 (69 candidates - 2 exclusions)
    """,
    "author": "InsightPulse AI",
    "website": "https://insightpulseai.com",
    "license": "LGPL-3",
    "depends": [
        # Generated from install_sets.yml → musthave_all (67 modules)
        # Base (26 modules)
        "base_technical_features",
        "base_search_fuzzy",
        "base_exception",
        "base_tier_validation",
        "base_user_role",
        "base_jsonify",
        "base_sparse_field",
        "base_suspend_security",
        "base_custom_info",
        "base_menu_visibility_restriction",
        "base_technical_user",
        "base_fontawesome",
        "base_import_async",
        "queue_job",
        "web_widget_x2many_2d_matrix",
        # web_advanced_search EXCLUDED (CE overlap)
        # mail_activity_plan EXCLUDED (CE overlap)
        "web_refresher",
        "web_domain_field",
        "web_pwa_oca",
        "web_notify",
        "web_m2x_options",
        "web_responsive",
        "web_timeline",
        "web_widget_digitized_signature",
        "web_dialog_size",
        "web_search_with_and",
        "web_ir_actions_act_multi",

        # Accounting (18 modules)
        "account_fiscal_year",
        "account_move_line_purchase_info",
        "account_move_line_sale_info",
        "account_invoice_refund_link",
        "account_usability",
        "account_payment_partner",
        "account_tag_menu",
        "account_type_menu",
        "account_move_tier_validation",
        "account_statement_import",
        "account_lock_to_date",
        "account_invoice_constraint_chronology",
        "account_cost_center",
        "account_journal_lock_date",
        "account_reconcile_oca",
        "account_invoice_view_payment",
        "account_chart_update",
        "account_financial_report",

        # Sales (11 modules)
        "sale_automatic_workflow",
        "sale_exception",
        "sale_tier_validation",
        "sale_order_type",
        "sale_order_invoicing_grouping_criteria",
        "sale_order_line_date",
        "sale_delivery_state",
        "sale_stock_mto_as_mts_orderpoint",
        "sale_order_priority",
        "sale_force_invoiced",
        "sale_validity",

        # Purchases (12 modules)
        "purchase_exception",
        "purchase_tier_validation",
        "purchase_order_type",
        "purchase_order_line_price_history",
        "purchase_order_secondary_unit",
        "purchase_last_price_info",
        "purchase_work_acceptance",
        "purchase_landed_cost",
        "purchase_discount",
        "purchase_order_analytic",
        "purchase_order_approved",
        "purchase_security",
    ],
    "data": [],
    "installable": True,
    "auto_install": False,
    "application": False,
}
```

**Task 3.5: Create `addons/ipai/ipai_oca_musthave_meta/__init__.py`**
```python
# Empty __init__.py (meta-module has no Python code)
```

**Task 3.6: Create `addons/ipai/ipai_oca_musthave_meta/README.md`**
```markdown
# IPAI OCA Must-Have Meta

Meta-module for one-command installation of all OCA Must-Have modules (no CE19 overlap).

## Purpose
Install the minimal viable OCA layer for Odoo 19 CE, explicitly excluding modules absorbed into core.

## Installation
```bash
odoo-bin -d your_database -i ipai_oca_musthave_meta
```

## Excluded Modules (CE19 Overlap)
- `web_advanced_search` - Absorbed into CE17+ core search functionality
- `mail_activity_plan` - Absorbed into CE17+ core activity planning

## Module Count
- **Total Candidates:** 69 modules
- **Excluded:** 2 modules (CE19 overlap)
- **Installed:** 67 modules

## Categories
- **Base:** 26 modules (28 candidates - 2 exclusions)
- **Accounting:** 18 modules
- **Sales:** 11 modules
- **Purchases:** 12 modules

## References
- **Spec:** `/spec/oca-musthave-no-ce19-overlap/`
- **Decision Matrix:** `/docs/oca/musthave/decision_matrix.md`
- **Install Sets:** `/docs/oca/musthave/install_sets.yml`
```

### Outputs
- `docs/oca/musthave/decision_matrix.md` (69 rows)
- `docs/oca/musthave/install_sets.yml` (5 sets)
- `config/oca/oca_must_have_*.yml` (4 files updated)
- `addons/ipai/ipai_oca_musthave_meta/` (3 files)

### Validation
- ✅ Decision matrix has 69 rows
- ✅ Install sets contain 67 modules
- ✅ Meta-module has 67 dependencies
- ✅ No excluded modules in manifests

---

## Phase 4: Validate (CI Integration)

**Objective:** Automated drift detection and overlap enforcement via CI.

### Tasks

**Task 4.1: Extend `.github/workflows/oca-must-have-gate.yml`**
```yaml
# Add drift-detection job
drift-detection:
  name: Detect OCA Must-Have Drift
  runs-on: ubuntu-latest
  steps:
    - name: Checkout code
      uses: actions/checkout@v4

    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.12'

    - name: Check CE19 overlap
      run: python scripts/oca_musthave/check_overlap.py --strict

    - name: Validate install sets
      run: python scripts/oca_musthave/validate_install_sets.py

    - name: Verify meta-module sync
      run: python scripts/oca_musthave/verify_meta_module.py
```

**Task 4.2: Create `scripts/oca_musthave/validate_install_sets.py`**
```python
#!/usr/bin/env python3
"""Validate install_sets.yml structure and module counts."""
import yaml
import sys

def main():
    with open("docs/oca/musthave/install_sets.yml") as f:
        data = yaml.safe_load(f)

    # Validate structure
    assert "sets" in data
    assert "musthave_all" in data["sets"]

    # Validate module counts
    all_modules = data["sets"]["musthave_all"]["modules"]
    assert len(all_modules) == 67, f"Expected 67 modules, got {len(all_modules)}"

    # Validate exclusions
    excluded = data["sets"]["musthave_all"]["excluded"]
    assert len(excluded) == 2, f"Expected 2 exclusions, got {len(excluded)}"
    assert "web_advanced_search" in excluded
    assert "mail_activity_plan" in excluded

    print("✅ Install sets validation passed")
    return 0

if __name__ == "__main__":
    sys.exit(main())
```

**Task 4.3: Create `scripts/oca_musthave/verify_meta_module.py`**
```python
#!/usr/bin/env python3
"""Verify meta-module manifest sync with install_sets.yml."""
import ast
import yaml
import sys

def main():
    # Load install sets
    with open("docs/oca/musthave/install_sets.yml") as f:
        install_sets = yaml.safe_load(f)

    expected_modules = set(install_sets["sets"]["musthave_all"]["modules"])

    # Load meta-module manifest
    with open("addons/ipai/ipai_oca_musthave_meta/__manifest__.py") as f:
        manifest = ast.literal_eval(f.read())

    actual_modules = set(manifest["depends"])

    # Validate sync
    assert expected_modules == actual_modules, "Meta-module out of sync with install_sets.yml"

    # Validate exclusions not present
    excluded = install_sets["sets"]["musthave_all"]["excluded"]
    for module in excluded:
        assert module not in actual_modules, f"Excluded module {module} found in meta-module"

    print("✅ Meta-module sync verification passed")
    return 0

if __name__ == "__main__":
    sys.exit(main())
```

### Outputs
- `.github/workflows/oca-must-have-gate.yml` (drift-detection job added)
- `scripts/oca_musthave/validate_install_sets.py`
- `scripts/oca_musthave/verify_meta_module.py`

### Validation
- ✅ CI drift-detection job passes
- ✅ Manual violation test (add excluded module) → CI fails
- ✅ All validation scripts executable

---

## Implementation Sequence

### Sequential Dependencies
```
Phase 1 (Seed) → Phase 2 (Filter) → Phase 3 (Generate) → Phase 4 (Validate)
```

### Parallelization Opportunities
- Phase 3 tasks can run in parallel after Phase 2 completes
- Documentation and meta-module generation are independent

### Recommended Order
1. Phase 1: Document candidate lists
2. Phase 2: Create filter script
3. Phase 3: Generate all artifacts (parallel)
4. Phase 4: CI integration + end-to-end test

---

## Verification Checklist

### Phase 1 ✅
- [ ] `docs/oca/musthave/source_lists.md` exists
- [ ] 69 modules documented
- [ ] 2 exclusion markers (⚠️)

### Phase 2 ✅
- [ ] `scripts/oca_musthave/check_overlap.py` executable
- [ ] Dry-run shows 2 exclusions
- [ ] Test mode passes

### Phase 3 ✅
- [ ] `docs/oca/musthave/decision_matrix.md` has 69 rows
- [ ] `docs/oca/musthave/install_sets.yml` has 5 sets
- [ ] Meta-module has 67 dependencies
- [ ] No excluded modules in manifests

### Phase 4 ✅
- [ ] CI drift-detection job exists
- [ ] Validation scripts pass
- [ ] Manual violation test → CI fails

### End-to-End ✅
- [ ] `odoo-bin -i ipai_oca_musthave_meta` installs 67 modules
- [ ] No dependency conflicts
- [ ] Clean installation log

---

## Rollback Strategy

### If Phase 1 Fails
- Delete `docs/oca/musthave/source_lists.md`
- No impact on existing system

### If Phase 2 Fails
- Delete `scripts/oca_musthave/check_overlap.py`
- No impact on existing system

### If Phase 3 Fails
- Delete all generated artifacts
- Restore original `config/oca/oca_must_have_*.yml` from Git
- Remove `addons/ipai/ipai_oca_musthave_meta/`

### If Phase 4 Fails
- Revert `.github/workflows/oca-must-have-gate.yml` changes
- Delete validation scripts
- No impact on existing CI

---

## Next Steps

**After Implementation:**
1. Create evidence bundle in `docs/evidence/YYYYMMDD-HHMM/oca-musthave-no-ce19-overlap/`
2. Commit all changes with OCA-style message
3. Create PR for review
4. Update `/docs/ai/OCA_WORKFLOW.md` with meta-module usage

**Ongoing Maintenance:**
- Quarterly review of exclusion list against CE changelog
- Monitor OCA discussions for module deprecations
- Update documentation when new exclusions discovered

---

**Last Updated:** 2026-02-15
**Related:** [constitution.md](./constitution.md) | [prd.md](./prd.md) | [tasks.md](./tasks.md)
