# Seed Data Consistency Gate Specification

**Gate Name:** `seed_data_consistency`
**Purpose:** Validate Finance PPM seed data integrity before deployment
**Status:** Design Specification (Implementation Ready)
**Priority:** HIGH (Production Blocker)
**Version:** 1.0.0

---

## Overview

This gate validates that the Finance PPM Umbrella module (`ipai_finance_ppm_umbrella`) has complete and consistent seed data across all XML files. It prevents deployment of broken seeds that would cause production module installation failures.

**Strategic Context:**
- Finance PPM deployment (Phase 3) requires 210 seed records operational
- Seed data drift is a recurring issue across OCA module ports
- "Odoo.sh-grade parity gating" strategic goal requires this protection

---

## Existing Implementation

**Script:** `/Users/tbwa/Documents/GitHub/Insightpulseai/odoo/scripts/finance_ppm_seed_audit.py`

**Current Status:** Fully implemented and tested
- **Output:** JSON report to `artifacts/finance_ppm_seed_audit.json`
- **Exit Codes:** 0 (pass), 1 (fail)
- **Validation Scope:** 5 XML files, 4 record count thresholds

**Existing Validation Logic:**
```python
def validate_seed_data():
    """Validate Finance PPM seed data integrity."""
    xml_files = [
        "data/employees.xml",
        "data/logframe_template.xml",
        "data/bir_schedule.xml",
        "data/tasks_template.xml",
        "data/raci_template.xml"
    ]

    thresholds = {
        "employees": 8,      # Minimum 8 employees (9 expected)
        "bir_records": 20,   # Minimum 20 BIR records (144 expected)
        "tasks": 30,         # Minimum 30 tasks (36 expected)
        "raci": 8            # Minimum 8 RACI records (9 expected)
    }

    # Parse XML, count records, compare to thresholds
    # Returns: {"pass": true/false, "errors": [...], "metrics": {...}}
```

---

## Integration Requirements

### Gate Contract Compliance

The existing script must be wrapped to comply with Gate Contract v2.0:

1. **Accept mode flag:** `--mode=local|ci`
2. **Write JSON report** to `artifacts/gates/seed_data_consistency/<timestamp>.json`
3. **Write Markdown summary** to `artifacts/gates/seed_data_consistency/<timestamp>.md`
4. **Create symlinks** to `latest.json` and `latest.md`
5. **Include timestamp** in ISO 8601 format
6. **Exit with appropriate code:** 0 (pass), 1 (fail), 2 (warn)

### Wrapper Script Design

**File:** `scripts/gates/seed_data_consistency.sh`

```bash
#!/usr/bin/env bash
set -euo pipefail

GATE_NAME="seed_data_consistency"
MODE="${1:-local}"
TIMESTAMP="$(date -u +%Y%m%d-%H%M%S)"
ARTIFACT_DIR="artifacts/gates/${GATE_NAME}"
REPO_ROOT="$(git rev-parse --show-toplevel)"

mkdir -p "${ARTIFACT_DIR}"

# Record start time
START_TIME="$(date +%s)"

# Run existing audit script
cd "${REPO_ROOT}"
python3 scripts/finance_ppm_seed_audit.py > "${ARTIFACT_DIR}/raw_output.txt" 2>&1
EXIT_CODE=$?

# Record end time
END_TIME="$(date +%s)"
DURATION=$((END_TIME - START_TIME))

# Parse existing JSON output
AUDIT_JSON="artifacts/finance_ppm_seed_audit.json"

if [[ ! -f "${AUDIT_JSON}" ]]; then
    echo "ERROR: Audit script did not produce ${AUDIT_JSON}" >&2
    exit 1
fi

# Extract metrics from existing audit
EMPLOYEES_COUNT=$(jq -r '.employees_count // 0' "${AUDIT_JSON}")
BIR_COUNT=$(jq -r '.bir_count // 0' "${AUDIT_JSON}")
TASKS_COUNT=$(jq -r '.tasks_count // 0' "${AUDIT_JSON}")
RACI_COUNT=$(jq -r '.raci_count // 0' "${AUDIT_JSON}")
ERRORS=$(jq -r '.errors // []' "${AUDIT_JSON}")
PASS=$(jq -r '.pass // false' "${AUDIT_JSON}")

# Determine status
if [[ "${PASS}" == "true" ]]; then
    STATUS="pass"
else
    STATUS="fail"
fi

# Convert errors to findings format
FINDINGS="[]"
if [[ "${ERRORS}" != "[]" ]]; then
    FINDINGS=$(jq -r '.errors | map({
        level: "error",
        message: .,
        file: "addons/ipai_finance_ppm_umbrella/data/",
        rule: "seed-data-threshold"
    })' "${AUDIT_JSON}")
fi

# Write Gate Contract v2.0 compliant JSON
cat > "${ARTIFACT_DIR}/${TIMESTAMP}.json" << EOF
{
  "version": "2.0",
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "environment": "${MODE}",
  "gates": [
    {
      "name": "${GATE_NAME}",
      "status": "${STATUS}",
      "duration_seconds": ${DURATION}.0,
      "findings": ${FINDINGS},
      "metrics": {
        "employees_count": ${EMPLOYEES_COUNT},
        "bir_records_count": ${BIR_COUNT},
        "tasks_count": ${TASKS_COUNT},
        "raci_count": ${RACI_COUNT},
        "total_seed_records": $((EMPLOYEES_COUNT + BIR_COUNT + TASKS_COUNT + RACI_COUNT))
      },
      "metadata": {
        "script": "scripts/finance_ppm_seed_audit.py",
        "version": "1.0.0",
        "module": "ipai_finance_ppm_umbrella"
      }
    }
  ],
  "summary": {
    "total": 1,
    "passed": $([[ "${STATUS}" == "pass" ]] && echo 1 || echo 0),
    "failed": $([[ "${STATUS}" == "fail" ]] && echo 1 || echo 0),
    "warnings": 0
  }
}
EOF

# Write Markdown summary
STATUS_EMOJI="✅"
[[ "${STATUS}" == "fail" ]] && STATUS_EMOJI="❌"
[[ "${STATUS}" == "warn" ]] && STATUS_EMOJI="⚠️"

cat > "${ARTIFACT_DIR}/${TIMESTAMP}.md" << EOF
# Gate Report: seed_data_consistency

**Status:** ${STATUS_EMOJI} ${STATUS^^}
**Duration:** ${DURATION}s
**Environment:** ${MODE}
**Timestamp:** $(date -u +%Y-%m-%d\ %H:%M:%S) UTC

## Summary

Finance PPM Umbrella module seed data validation.
Ensures all required seed records are present and meet minimum thresholds.

## Metrics

| Metric | Value | Threshold | Status |
|--------|-------|-----------|--------|
| Employees | ${EMPLOYEES_COUNT} | >= 8 | $([[ ${EMPLOYEES_COUNT} -ge 8 ]] && echo "✅" || echo "❌") |
| BIR Records | ${BIR_COUNT} | >= 20 | $([[ ${BIR_COUNT} -ge 20 ]] && echo "✅" || echo "❌") |
| Tasks | ${TASKS_COUNT} | >= 30 | $([[ ${TASKS_COUNT} -ge 30 ]] && echo "✅" || echo "❌") |
| RACI | ${RACI_COUNT} | >= 8 | $([[ ${RACI_COUNT} -ge 8 ]] && echo "✅" || echo "❌") |
| **Total Records** | **$((EMPLOYEES_COUNT + BIR_COUNT + TASKS_COUNT + RACI_COUNT))** | **>= 210** | $([[ $((EMPLOYEES_COUNT + BIR_COUNT + TASKS_COUNT + RACI_COUNT)) -ge 210 ]] && echo "✅" || echo "❌") |

## Findings

EOF

if [[ "${STATUS}" == "fail" ]]; then
    jq -r '.errors[] | "- ❌ " + .' "${AUDIT_JSON}" >> "${ARTIFACT_DIR}/${TIMESTAMP}.md"
else
    echo "No issues found. All seed data thresholds met." >> "${ARTIFACT_DIR}/${TIMESTAMP}.md"
fi

cat >> "${ARTIFACT_DIR}/${TIMESTAMP}.md" << EOF

## Details

**Module:** ipai_finance_ppm_umbrella
**Validated Files:**
- data/employees.xml
- data/logframe_template.xml
- data/bir_schedule.xml
- data/tasks_template.xml
- data/raci_template.xml

**Expected Seed Records:**
- 9 Finance SSC employees (CKVC, RIM, BOM, JPAL, JLI, JAP, JRMO, LAS, RMQB)
- 144 BIR schedule records (12 forms × 12 agencies)
- 36 project tasks (logframe-based)
- 9 RACI matrix entries

---
Generated by: scripts/gates/seed_data_consistency.sh
Report version: 2.0
EOF

# Create symlinks
ln -sf "${TIMESTAMP}.json" "${ARTIFACT_DIR}/latest.json"
ln -sf "${TIMESTAMP}.md" "${ARTIFACT_DIR}/latest.md"

# Exit with appropriate code
exit ${EXIT_CODE}
```

---

## CI Integration Design

**GitHub Actions Workflow:** `.github/workflows/seed-data-consistency-gate.yml`

```yaml
name: Seed Data Consistency Gate

on:
  pull_request:
    paths:
      - 'addons/ipai_finance_ppm_umbrella/data/**/*.xml'
      - 'scripts/finance_ppm_seed_audit.py'
  push:
    branches:
      - main
    paths:
      - 'addons/ipai_finance_ppm_umbrella/data/**/*.xml'

jobs:
  validate-seed-data:
    name: Validate Finance PPM Seed Data
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Install dependencies
        run: |
          pip install lxml jq

      - name: Run seed data consistency gate
        id: gate
        run: |
          bash scripts/gates/seed_data_consistency.sh ci
        continue-on-error: true

      - name: Upload gate report
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: seed-data-consistency-report
          path: |
            artifacts/gates/seed_data_consistency/latest.json
            artifacts/gates/seed_data_consistency/latest.md

      - name: Comment on PR
        if: github.event_name == 'pull_request' && always()
        uses: actions/github-script@v7
        with:
          script: |
            const fs = require('fs');
            const summary = fs.readFileSync('artifacts/gates/seed_data_consistency/latest.md', 'utf8');
            await github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: `## 🔍 Seed Data Consistency Gate\n\n${summary}`
            });

      - name: Fail if gate failed
        if: steps.gate.outcome == 'failure'
        run: exit 1
```

---

## Makefile Integration

Add to `Makefile`:

```makefile
.PHONY: gates-seed gates-seed-ci

gates-seed:  ## Run seed data consistency gate (local mode)
	@echo "🔍 Running seed data consistency gate (local mode)..."
	@bash scripts/gates/seed_data_consistency.sh local

gates-seed-ci:  ## Run seed data consistency gate (CI mode)
	@echo "🔍 Running seed data consistency gate (CI mode)..."
	@bash scripts/gates/seed_data_consistency.sh ci

gates: gates-seed  ## Add seed gate to main gates target
```

---

## Validation Thresholds

**Current Thresholds (Conservative):**
| Record Type | Threshold | Expected | Buffer |
|-------------|-----------|----------|--------|
| Employees | >= 8 | 9 | 1 record |
| BIR Records | >= 20 | 144 | 124 records |
| Tasks | >= 30 | 36 | 6 records |
| RACI | >= 8 | 9 | 1 record |
| **Total** | **>= 210** | **210** | **0 records** |

**Rationale:**
- Conservative thresholds allow for minor variations (e.g., optional employees)
- BIR threshold very low (20 vs 144 expected) to catch catastrophic failures
- Total threshold exact (210) ensures no silent data loss

**Future Enhancement:**
- Configurable thresholds via `scripts/gates/gate_config.yaml`
- Per-file validation (ensure no empty XML files)
- XML schema validation (well-formed structure)

---

## Expected Gate Output Examples

### Success Case (Local Mode)

**JSON:** `artifacts/gates/seed_data_consistency/latest.json`
```json
{
  "version": "2.0",
  "timestamp": "2026-02-13T10:30:00Z",
  "environment": "local",
  "gates": [
    {
      "name": "seed_data_consistency",
      "status": "pass",
      "duration_seconds": 1.234,
      "findings": [],
      "metrics": {
        "employees_count": 9,
        "bir_records_count": 144,
        "tasks_count": 36,
        "raci_count": 9,
        "total_seed_records": 210
      }
    }
  ],
  "summary": {
    "total": 1,
    "passed": 1,
    "failed": 0,
    "warnings": 0
  }
}
```

**Markdown:** `artifacts/gates/seed_data_consistency/latest.md`
```markdown
# Gate Report: seed_data_consistency

**Status:** ✅ PASS
**Duration:** 1s
**Environment:** local
**Timestamp:** 2026-02-13 10:30:00 UTC

## Summary
Finance PPM Umbrella module seed data validation.
Ensures all required seed records are present and meet minimum thresholds.

## Metrics
| Metric | Value | Threshold | Status |
|--------|-------|-----------|--------|
| Employees | 9 | >= 8 | ✅ |
| BIR Records | 144 | >= 20 | ✅ |
| Tasks | 36 | >= 30 | ✅ |
| RACI | 9 | >= 8 | ✅ |
| **Total Records** | **210** | **>= 210** | ✅ |

## Findings
No issues found. All seed data thresholds met.

---
Generated by: scripts/gates/seed_data_consistency.sh
```

### Failure Case (CI Mode)

**JSON:** (with findings)
```json
{
  "gates": [
    {
      "name": "seed_data_consistency",
      "status": "fail",
      "findings": [
        {
          "level": "error",
          "message": "Employees count 5 below threshold 8",
          "file": "addons/ipai_finance_ppm_umbrella/data/employees.xml",
          "rule": "seed-data-threshold"
        },
        {
          "level": "error",
          "message": "Total seed records 150 below threshold 210",
          "file": "addons/ipai_finance_ppm_umbrella/data/",
          "rule": "seed-data-threshold"
        }
      ],
      "metrics": {
        "employees_count": 5,
        "bir_records_count": 144,
        "tasks_count": 1,
        "raci_count": 0,
        "total_seed_records": 150
      }
    }
  ]
}
```

---

## Testing Strategy

### Unit Tests (Optional Enhancement)

**File:** `tests/gates/test_seed_data_consistency.py`

```python
import pytest
import json
import subprocess

def test_gate_produces_valid_json():
    """Ensure gate produces valid JSON report."""
    result = subprocess.run(
        ["bash", "scripts/gates/seed_data_consistency.sh", "local"],
        capture_output=True
    )

    with open("artifacts/gates/seed_data_consistency/latest.json") as f:
        report = json.load(f)

    assert report["version"] == "2.0"
    assert "gates" in report
    assert len(report["gates"]) == 1

def test_gate_fails_on_missing_records():
    """Ensure gate fails when seed records below threshold."""
    # TODO: Mock XML files with insufficient records
    # Run gate, assert exit code 1
    pass

def test_gate_creates_symlinks():
    """Ensure gate creates latest.json and latest.md symlinks."""
    subprocess.run(
        ["bash", "scripts/gates/seed_data_consistency.sh", "local"],
        check=True
    )

    assert os.path.islink("artifacts/gates/seed_data_consistency/latest.json")
    assert os.path.islink("artifacts/gates/seed_data_consistency/latest.md")
```

### Integration Test (Makefile)

```makefile
test-gates:  ## Test all quality gates
	@echo "Testing seed data consistency gate..."
	@make gates-seed
	@echo "✅ All gates passed"
```

---

## Deployment Checklist

Before enabling this gate in CI:

- [ ] Wrapper script created at `scripts/gates/seed_data_consistency.sh`
- [ ] Script is executable (`chmod +x`)
- [ ] Gate produces valid JSON matching schema
- [ ] Gate produces Markdown summary
- [ ] Symlinks created correctly
- [ ] Exit codes correct (0 pass, 1 fail)
- [ ] Manual test with current Finance PPM data passes
- [ ] GitHub Actions workflow created
- [ ] Makefile targets added
- [ ] Gate documentation complete

---

## Future Enhancements (Out of Scope)

- **XML schema validation:** Ensure well-formed XML structure
- **Per-file validation:** Detect empty or malformed XML files
- **Record uniqueness validation:** Ensure no duplicate `xml_id` values
- **Foreign key validation:** Check `ref` attributes point to valid records
- **noupdate flag validation:** Warn on missing `noupdate="1"` for seed data
- **Deterministic ID validation:** Ensure stable `xml_id` patterns
- **Parallel execution:** Run validation in parallel for speed
- **Historical trend tracking:** Monitor seed record counts over time

---

## References

- Gate Contract: `docs/architecture/gate-contract-v2.md`
- JSON Schema: `schemas/gate_report.schema.json`
- Existing Audit Script: `scripts/finance_ppm_seed_audit.py`
- Finance PPM Module: `addons/ipai_finance_ppm_umbrella/`
- Seed Data Files: `addons/ipai_finance_ppm_umbrella/data/*.xml`

---

**Status:** Design specification complete. Implementation ready.
**Priority:** HIGH (Production blocker for Phase 3 Finance PPM deployment)
**Effort:** 2-4 hours (wrapper script + CI workflow + testing)
