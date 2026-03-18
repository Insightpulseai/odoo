# Continue+ "All Green" Acceptance Criteria

**Version**: 1.0.0
**Date**: 2025-12-22

---

## Overview

This document defines the measurable acceptance criteria for a production-ready ("all green") Continue.dev implementation. All criteria must pass before the system is considered deployment-grade.

---

## Acceptance Criteria

### AC-1: Spec Kit Validation (MUST)

| ID | Criterion | Measurement | Target |
|----|-----------|-------------|--------|
| AC-1.1 | Spec bundle structure valid | `validate-spec-kit.sh` exit code | 0 |
| AC-1.2 | Required files present | 4 files per bundle | 100% |
| AC-1.3 | Minimum content met | ≥10 non-empty lines | 100% |
| AC-1.4 | No placeholder text | grep for TODO/TBD/LOREM | 0 matches |
| AC-1.5 | YAML files valid | yaml.safe_load() passes | 100% |

**Verification Command**:
```bash
./scripts/validate-spec-kit.sh --strict
```

---

### AC-2: Continue Configuration (MUST)

| ID | Criterion | Measurement | Target |
|----|-----------|-------------|--------|
| AC-2.1 | config.json valid | JSON schema validation | PASS |
| AC-2.2 | Rules files loadable | YAML parse success | 100% |
| AC-2.3 | Prompts defined | 4 prompts exist | 100% |
| AC-2.4 | Schema reference present | $schema in config | Present |

**Verification Command**:
```bash
./scripts/validate-continue-config.sh
```

---

### AC-3: Policy Compliance (MUST)

| ID | Criterion | Measurement | Target |
|----|-----------|-------------|--------|
| AC-3.1 | No hardcoded secrets | grep patterns | 0 matches |
| AC-3.2 | No Enterprise deps | manifest.py check | 0 violations |
| AC-3.3 | Tool allowlist respected | command audit | 100% |
| AC-3.4 | No forbidden paths | diff classification | 0 violations |

**Verification Command**:
```bash
./scripts/policy-check.sh
```

---

### AC-4: CI Gate Pass Rate (MUST)

| ID | Criterion | Measurement | Target |
|----|-----------|-------------|--------|
| AC-4.1 | Spec validation passes | CI job status | PASS |
| AC-4.2 | Policy check passes | CI job status | PASS |
| AC-4.3 | Tests pass | pytest/npm test | PASS |
| AC-4.4 | No CI on docs-only | Agent preflight | SKIP |

**Verification**: All CI checks green on PR.

---

### AC-5: Deterministic Execution (SHOULD)

| ID | Criterion | Measurement | Target |
|----|-----------|-------------|--------|
| AC-5.1 | Same input → same plan | Hash comparison | Match |
| AC-5.2 | Role boundaries enforced | Audit log | 100% |
| AC-5.3 | Output format stable | Schema validation | PASS |

**Note**: Full determinism requires temperature=0 and seed values.

---

### AC-6: Lineage & Traceability (SHOULD)

| ID | Criterion | Measurement | Target |
|----|-----------|-------------|--------|
| AC-6.1 | Runs logged | control_room.runs count | >0 |
| AC-6.2 | Artifacts stored | control_room.artifacts count | >0 |
| AC-6.3 | Lineage edges created | control_room.lineage_edges | >0 |
| AC-6.4 | Spec→PR link | PR description | Present |

---

### AC-7: Failure Handling (MUST)

| ID | Criterion | Measurement | Target |
|----|-----------|-------------|--------|
| AC-7.1 | Errors captured | Artifact upload | PASS |
| AC-7.2 | Retry logic works | 3 attempts max | Implemented |
| AC-7.3 | Alerts on failure | Webhook fired | PASS |
| AC-7.4 | Timeout defined | workflow timeout | ≤15 min |

---

## Test Matrix

| Scenario | Expected Outcome | Actual | Status |
|----------|------------------|--------|--------|
| Valid spec bundle | CI PASS | | |
| Missing constitution.md | CI FAIL | | |
| Placeholder in plan.md | CI WARN/FAIL | | |
| Docs-only PR | Skip Odoo CI | | |
| Code change PR | Run full CI | | |
| Hardcoded secret | Policy FAIL | | |
| Enterprise dependency | Policy FAIL | | |

---

## Sign-off

| Role | Name | Date | Signature |
|------|------|------|-----------|
| Platform Owner | | | |
| CI/CD Owner | | | |
| Security Review | | | |

---

## Revision History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-12-22 | Initial criteria definition |
