# OCA Must-Have (No CE19 Overlap) — Task Breakdown

**Version:** 1.0.0
**Date:** 2026-02-15
**Status:** Active
**Plan:** [See plan.md](./plan.md)

---

## Phase 1: Seed (Data Preparation)

### Task 1.1: Create `docs/oca/musthave/` directory structure
**Status:** ⏳ Pending
**Owner:** Engineer
**Effort:** 5 minutes

**Actions:**
```bash
mkdir -p docs/oca/musthave
```

**Verification:**
```bash
test -d docs/oca/musthave && echo "✅ Directory created"
```

---

### Task 1.2: Create `docs/oca/musthave/source_lists.md`
**Status:** ⏳ Pending
**Owner:** Engineer
**Effort:** 30 minutes

**Actions:**
- Document all 69 candidate modules organized by 4 categories
- Mark 2 CE overlap exclusions with ⚠️
- Include pre-filter and post-filter counts

**Template:**
```markdown
# OCA Must-Have Source Lists (Pre-Filter)

## Base (28 modules)
- base_technical_features
- **web_advanced_search** ⚠️ EXCLUDE (CE overlap - now included in core v17+)
- **mail_activity_plan** ⚠️ EXCLUDE (CE overlap - now included in core v17+)
- ...

**Pre-Filter Count:** 28 modules
**Explicit Exclusions:** 2
**Post-Filter Count:** 26 modules
```

**Verification:**
```bash
# Count total modules
grep -c "^- " docs/oca/musthave/source_lists.md
# Expected: 69

# Verify exclusion markers
grep -c "⚠️ EXCLUDE" docs/oca/musthave/source_lists.md
# Expected: 2
```

---

### Task 1.3: Validate candidate module counts
**Status:** ⏳ Pending
**Owner:** Engineer
**Effort:** 10 minutes

**Actions:**
- Count modules per category (Base: 28, Accounting: 18, Sales: 11, Purchases: 12)
- Verify total: 69 modules
- Confirm 2 explicit exclusions

**Verification:**
```bash
python -c "
import re
with open('docs/oca/musthave/source_lists.md') as f:
    content = f.read()
    modules = re.findall(r'^- ', content, re.MULTILINE)
    excludes = re.findall(r'⚠️ EXCLUDE', content)
    assert len(modules) == 69, f'Expected 69 modules, got {len(modules)}'
    assert len(excludes) == 2, f'Expected 2 exclusions, got {len(excludes)}'
print('✅ Candidate counts validated')
"
```

---

## Phase 2: Filter (CE19 Overlap Detection)

### Task 2.1: Create `scripts/oca_musthave/` directory
**Status:** ⏳ Pending
**Owner:** Engineer
**Effort:** 5 minutes

**Actions:**
```bash
mkdir -p scripts/oca_musthave
```

**Verification:**
```bash
test -d scripts/oca_musthave && echo "✅ Directory created"
```

---

### Task 2.2: Create `scripts/oca_musthave/check_overlap.py`
**Status:** ⏳ Pending
**Owner:** Engineer
**Effort:** 1 hour

**Actions:**
- Implement filter algorithm with explicit exclusion dictionary
- Support `--dry-run`, `--strict`, `--test-exclusions` flags
- JSON output for audit trail

**Core Implementation:**
```python
EXCLUDED_MODULES = {
    "web_advanced_search": "Absorbed into CE17+ core search functionality",
    "mail_activity_plan": "Absorbed into CE17+ core activity planning"
}

def filter_modules(candidate_list: List[str]) -> Tuple[List[str], Dict]:
    included = []
    excluded = {}
    for module in candidate_list:
        if module in EXCLUDED_MODULES:
            excluded[module] = EXCLUDED_MODULES[module]
        else:
            included.append(module)
    return included, excluded
```

**Verification:**
```bash
# Test exclusion detection
python scripts/oca_musthave/check_overlap.py --test-exclusions
# Expected: ✅ Exclusion tests passed

# Dry-run mode
python scripts/oca_musthave/check_overlap.py --dry-run | jq '.exclusion_count'
# Expected: 2

# Make executable
chmod +x scripts/oca_musthave/check_overlap.py
test -x scripts/oca_musthave/check_overlap.py && echo "✅ Script executable"
```

---

### Task 2.3: Test filter script determinism
**Status:** ⏳ Pending
**Owner:** QA
**Effort:** 15 minutes

**Actions:**
- Run filter 10 times
- Verify identical output each time
- Confirm always 2 exclusions

**Verification:**
```bash
for i in {1..10}; do
  python scripts/oca_musthave/check_overlap.py --dry-run | jq -c '.excluded_modules' >> /tmp/filter_output.txt
done

# Verify all outputs identical
sort /tmp/filter_output.txt | uniq | wc -l
# Expected: 1 (all identical)

rm /tmp/filter_output.txt
```

---

## Phase 3: Generate (Manifest Creation)

### Task 3.1: Create `docs/oca/musthave/decision_matrix.md`
**Status:** ⏳ Pending
**Owner:** Engineer
**Effort:** 1 hour

**Actions:**
- Create markdown table with 69 rows (1 per module)
- Columns: Module | Category | Decision | Rationale | Evidence
- Document all INCLUDE/EXCLUDE decisions

**Template:**
```markdown
| Module | Category | Decision | Rationale | Evidence |
|--------|----------|----------|-----------|----------|
| web_advanced_search | Base | EXCLUDE | Absorbed into CE17+ core | [odoo/odoo#...] |
| mail_activity_plan | Base | EXCLUDE | Absorbed into CE17+ core | [odoo/odoo#...] |
| base_technical_features | Base | INCLUDE | No CE overlap | OCA/server-tools |
```

**Verification:**
```bash
# Count rows (expect 69 + 1 header)
grep -c "^|" docs/oca/musthave/decision_matrix.md
# Expected: 70

# Verify exclusions
grep -c "| EXCLUDE |" docs/oca/musthave/decision_matrix.md
# Expected: 2
```

---

### Task 3.2: Create `docs/oca/musthave/install_sets.yml`
**Status:** ⏳ Pending
**Owner:** Engineer
**Effort:** 1 hour

**Actions:**
- Create YAML with 5 install sets (base, accounting, sales, purchases, all)
- Each set lists filtered modules and excluded modules
- `musthave_all` set contains union of all modules (67 total)

**Template:**
```yaml
meta:
  odoo_version: "19.0"
  generator: "oca_musthave_pipeline_v1"

sets:
  musthave_base:
    modules: [base_technical_features, ...]  # 26 modules
    excluded: [web_advanced_search, mail_activity_plan]

  musthave_all:
    modules: [...]  # 67 modules
    excluded: [web_advanced_search, mail_activity_plan]
```

**Verification:**
```bash
python -c "
import yaml
with open('docs/oca/musthave/install_sets.yml') as f:
    data = yaml.safe_load(f)
    assert len(data['sets']) == 5
    assert len(data['sets']['musthave_all']['modules']) == 67
    assert len(data['sets']['musthave_all']['excluded']) == 2
print('✅ Install sets validated')
"
```

---

### Task 3.3: Update `config/oca/oca_must_have_base.yml`
**Status:** ⏳ Pending
**Owner:** Engineer
**Effort:** 30 minutes

**Actions:**
- Update manifest with 26 base modules (excluding web_advanced_search, mail_activity_plan)
- Document purpose and policy
- Reference OCA repositories

**Verification:**
```bash
# Verify excluded modules NOT present
grep -E "web_advanced_search|mail_activity_plan" config/oca/oca_must_have_base.yml
# Expected: Empty (exit code 1)

# Count modules
grep -c "^  - " config/oca/oca_must_have_base.yml
# Expected: 26
```

---

### Task 3.4: Update `config/oca/oca_must_have_accounting.yml`
**Status:** ⏳ Pending
**Owner:** Engineer
**Effort:** 20 minutes

**Actions:**
- Update manifest with 18 accounting modules
- No exclusions (all included)

**Verification:**
```bash
grep -c "^  - " config/oca/oca_must_have_accounting.yml
# Expected: 18
```

---

### Task 3.5: Update `config/oca/oca_must_have_sales.yml`
**Status:** ⏳ Pending
**Owner:** Engineer
**Effort:** 20 minutes

**Actions:**
- Update manifest with 11 sales modules
- No exclusions (all included)

**Verification:**
```bash
grep -c "^  - " config/oca/oca_must_have_sales.yml
# Expected: 11
```

---

### Task 3.6: Update `config/oca/oca_must_have_purchase.yml`
**Status:** ⏳ Pending
**Owner:** Engineer
**Effort:** 20 minutes

**Actions:**
- Update manifest with 12 purchase modules
- No exclusions (all included)

**Verification:**
```bash
grep -c "^  - " config/oca/oca_must_have_purchase.yml
# Expected: 12
```

---

### Task 3.7: Create `addons/ipai/ipai_oca_musthave_meta/` directory
**Status:** ⏳ Pending
**Owner:** Engineer
**Effort:** 5 minutes

**Actions:**
```bash
mkdir -p addons/ipai/ipai_oca_musthave_meta
```

**Verification:**
```bash
test -d addons/ipai/ipai_oca_musthave_meta && echo "✅ Directory created"
```

---

### Task 3.8: Create `addons/ipai/ipai_oca_musthave_meta/__manifest__.py`
**Status:** ⏳ Pending
**Owner:** Engineer
**Effort:** 1 hour

**Actions:**
- Create manifest with 67 dependencies (generated from install_sets.yml)
- Include inline comments marking exclusions
- Set version to 19.0.1.0.0

**Verification:**
```bash
python -c "
import ast
with open('addons/ipai/ipai_oca_musthave_meta/__manifest__.py') as f:
    manifest = ast.literal_eval(f.read())
    assert len(manifest['depends']) == 67, f\"Expected 67, got {len(manifest['depends'])}\"
    assert 'web_advanced_search' not in manifest['depends']
    assert 'mail_activity_plan' not in manifest['depends']
print('✅ Meta-module manifest validated')
"
```

---

### Task 3.9: Create `addons/ipai/ipai_oca_musthave_meta/__init__.py`
**Status:** ⏳ Pending
**Owner:** Engineer
**Effort:** 2 minutes

**Actions:**
```bash
touch addons/ipai/ipai_oca_musthave_meta/__init__.py
echo "# Empty __init__.py (meta-module has no Python code)" > addons/ipai/ipai_oca_musthave_meta/__init__.py
```

**Verification:**
```bash
test -f addons/ipai/ipai_oca_musthave_meta/__init__.py && echo "✅ __init__.py created"
```

---

### Task 3.10: Create `addons/ipai/ipai_oca_musthave_meta/README.md`
**Status:** ⏳ Pending
**Owner:** Engineer
**Effort:** 20 minutes

**Actions:**
- Document meta-module purpose
- Installation instructions
- Module counts and exclusions
- References to spec bundle

**Verification:**
```bash
test -f addons/ipai/ipai_oca_musthave_meta/README.md && echo "✅ README created"
grep -q "67 modules" addons/ipai/ipai_oca_musthave_meta/README.md
```

---

## Phase 4: Validate (CI Integration)

### Task 4.1: Create `scripts/oca_musthave/validate_install_sets.py`
**Status:** ⏳ Pending
**Owner:** Engineer
**Effort:** 30 minutes

**Actions:**
- Validate install_sets.yml structure
- Check module counts (67 total, 2 exclusions)
- Verify all 5 sets present

**Verification:**
```bash
python scripts/oca_musthave/validate_install_sets.py
# Expected: ✅ Install sets validation passed
```

---

### Task 4.2: Create `scripts/oca_musthave/verify_meta_module.py`
**Status:** ⏳ Pending
**Owner:** Engineer
**Effort:** 30 minutes

**Actions:**
- Compare meta-module manifest with install_sets.yml
- Verify 67 dependencies match musthave_all modules
- Ensure excluded modules NOT in manifest

**Verification:**
```bash
python scripts/oca_musthave/verify_meta_module.py
# Expected: ✅ Meta-module sync verification passed
```

---

### Task 4.3: Extend `.github/workflows/oca-must-have-gate.yml`
**Status:** ⏳ Pending
**Owner:** DevOps
**Effort:** 30 minutes

**Actions:**
- Add drift-detection job
- Run check_overlap.py --strict
- Run validate_install_sets.py
- Run verify_meta_module.py

**Verification:**
```bash
grep -q "drift-detection:" .github/workflows/oca-must-have-gate.yml
# Expected: Exit code 0 (job found)
```

---

### Task 4.4: Test CI drift detection (manual violation)
**Status:** ⏳ Pending
**Owner:** QA
**Effort:** 15 minutes

**Actions:**
- Manually add `web_advanced_search` to `oca_must_have_base.yml`
- Trigger CI workflow
- Verify CI fails with clear error message
- Revert changes

**Verification:**
```bash
# Temporarily add excluded module
echo "  - web_advanced_search  # TEST VIOLATION" >> config/oca/oca_must_have_base.yml

# Run validation locally
python scripts/oca_musthave/check_overlap.py --strict
# Expected: Exit code 1 (failure detected)

# Revert
git checkout config/oca/oca_must_have_base.yml
```

---

### Task 4.5: End-to-end installation test
**Status:** ⏳ Pending
**Owner:** QA
**Effort:** 30 minutes

**Actions:**
- Create test database
- Install meta-module: `odoo-bin -d test_oca_musthave -i ipai_oca_musthave_meta --stop-after-init`
- Verify 67 modules installed
- Check installation log for errors

**Verification:**
```bash
# Install meta-module
odoo-bin -d test_oca_musthave -i ipai_oca_musthave_meta --stop-after-init
# Expected: Exit code 0

# Verify module count
psql test_oca_musthave -c "SELECT COUNT(*) FROM ir_module_module WHERE state='installed';"
# Expected: 67 OCA modules + base modules

# Cleanup
dropdb test_oca_musthave
```

---

## Post-Implementation Tasks

### Task 5.1: Create evidence bundle
**Status:** ⏳ Pending
**Owner:** Engineer
**Effort:** 20 minutes

**Actions:**
```bash
mkdir -p docs/evidence/$(date +%Y%m%d-%H%M)/oca-musthave-no-ce19-overlap
cp spec/oca-musthave-no-ce19-overlap/* docs/evidence/$(date +%Y%m%d-%H%M)/oca-musthave-no-ce19-overlap/
```

**Verification:**
```bash
ls docs/evidence/$(date +%Y%m%d-%H%M)/oca-musthave-no-ce19-overlap/
# Expected: constitution.md prd.md plan.md tasks.md
```

---

### Task 5.2: Commit with OCA-style message
**Status:** ⏳ Pending
**Owner:** Engineer
**Effort:** 10 minutes

**Actions:**
```bash
git add spec/oca-musthave-no-ce19-overlap/
git add docs/oca/musthave/
git add config/oca/oca_must_have_*.yml
git add addons/ipai/ipai_oca_musthave_meta/
git add scripts/oca_musthave/
git add .github/workflows/oca-must-have-gate.yml

git commit -m "feat(oca): add OCA Must-Have module management system (no CE19 overlap)

- Create deterministic filtering pipeline (69 → 67 modules)
- Explicit exclusions: web_advanced_search, mail_activity_plan
- Meta-module for one-command installation
- CI drift detection and overlap enforcement
- Complete audit trail in decision matrix

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

**Verification:**
```bash
git log --oneline -1 | grep "feat(oca):"
# Expected: Commit message visible
```

---

### Task 5.3: Update `/docs/ai/OCA_WORKFLOW.md`
**Status:** ⏳ Pending
**Owner:** Engineer
**Effort:** 30 minutes

**Actions:**
- Add section on meta-module usage
- Document one-command installation
- Reference spec bundle

**Verification:**
```bash
grep -q "ipai_oca_musthave_meta" docs/ai/OCA_WORKFLOW.md
# Expected: Exit code 0 (documentation updated)
```

---

## Summary

**Total Tasks:** 20
- Phase 1 (Seed): 3 tasks
- Phase 2 (Filter): 3 tasks
- Phase 3 (Generate): 10 tasks
- Phase 4 (Validate): 5 tasks
- Post-Implementation: 3 tasks

**Estimated Effort:** 8-12 hours
**Critical Path:** Phase 1 → Phase 2 → Phase 3 → Phase 4 → Post-Implementation

**Success Criteria:**
- ✅ All 20 tasks completed
- ✅ Spec bundle complete (4 files)
- ✅ Filter script functional (2 exclusions)
- ✅ Meta-module installs cleanly (67 modules)
- ✅ CI drift detection passes
- ✅ End-to-end test successful

---

**Last Updated:** 2026-02-15
**Related:** [constitution.md](./constitution.md) | [prd.md](./prd.md) | [plan.md](./plan.md)
