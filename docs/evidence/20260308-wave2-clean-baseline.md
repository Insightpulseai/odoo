# Wave2-Clean Baseline — Snapshot Evidence

> **Branch**: `claude/wave2-clean`
> **Commit**: `d31d1e3b`
> **Date**: 2026-03-08
> **Type**: Branch-local snapshot metrics (not canonical SSOT)

---

## Verified Counts

These counts are observed on branch `claude/wave2-clean` at commit `d31d1e3b`.
They are **snapshot metrics**, not canonical platform state.

| Metric | Count | Command |
|--------|-------|---------|
| IPAI custom modules | 70 | `ls addons/ipai/*/__manifest__.py \| wc -l` |
| OCA aggregate repos | 36 | `python3 -c "import yaml; print(len(yaml.safe_load(open('oca-aggregate.yml'))))"` |
| OCA lock repos | 36 | `python3 -c "import json; print(len(json.load(open('vendor/oca.lock.ce19.json'))['repos']))"` |
| OCA sync status | IN SYNC | `python3 scripts/oca/validate_aggregate.py` |
| Spec bundles | 75 | `ls -d spec/*/ \| wc -l` |
| GitHub workflows | 361 | `ls .github/workflows/*.yml \| wc -l` |
| Scripts | 984 | `find scripts/ -type f \| wc -l` |
| Evidence bundles | 94 | `ls -d docs/evidence/*/ \| wc -l` |
| Lakehouse files | 24 | `find infra/lakehouse/ scripts/lakehouse/ src/lakehouse/ contracts/delta/ spec/lakehouse/ docs/lakehouse/ -type f \| wc -l` |
| Marketplace files | 21 | `find marketplace/ -type f \| wc -l` |

## API Create-Method Audit

**State after stream A3 fixes** (not the discovery state):

| Classification | Count |
|----------------|-------|
| ALREADY_CORRECT | 9 |
| SAFE_AUTO_FIX | 0 (2 were fixed during this stream) |
| MANUAL_REVIEW | 0 (1 was auto-fixed; needs behavior test) |

Two files were migrated to `@api.model_create_multi` during this stream:
- `ipai_hr_expense_liquidation/models/hr_expense_liquidation.py` — sequence-only create
- `ipai_agent/models/agent_run.py` — sequence + idempotency key

One file was adapted beyond plan scope:
- `ipai_finance_ppm/models/project_task_integration.py` — post-create event emission was refactored to iterate the returned recordset. **Needs targeted behavior testing** to confirm event emission semantics are preserved under batch create.

## IPAI Module Classification (from delta audit)

| Category | Count | % |
|----------|-------|---|
| JUSTIFIED_CUSTOM | 17 | 24% |
| THIN_GLUE | 15 | 21% |
| OCA_CANDIDATE | 16 | 23% |
| THEME_UI | 18 | 26% |
| CONSOLIDATION_CANDIDATE | 12 | 17% |
| DEPRECATED (installable=False) | 25 | 36% |

Note: categories overlap (a deprecated module may also be an OCA candidate).

## Research Carry-Forward Status

| Research | Date | Key Metric | Status |
|----------|------|------------|--------|
| EE-OCA Parity Proof | 2026-02-17 | 150/150 mapped (T1) | **Historical**. Zero at T2-T4. |
| EE Parity Analysis | 2026-01-28 | 88.2% weighted score | **Stale**. Not recomputed on current branch. |
| Odoo.sh Parity | 2026-01-29 | 89% platform score | **Stable**. No significant platform changes since. |
| OCA repos referenced in research | 2026-02-17 | 45 repos | **9 candidates** for intake screening, not automatic inclusion. |

## What This Stream Shipped

| Stream | Deliverable | Verification |
|--------|-------------|-------------|
| A1: OCA Validate | validate_aggregate.py + CI gate, aggregate/lock synced 36/36 | `python3 scripts/oca/validate_aggregate.py` → PASS |
| A3: API Audit | api_model_audit.py, 2 safe fixes, 1 adapted | `python3 -m py_compile` on all 3 files → PASS |
| B1: Lakehouse | spec bundle (4 files) + docs (3 files) | Files exist with correct headers |
| MKT: Marketplace | checklist (71 checks) + per-offer Level 0 | Files exist at expected paths |

---

*Snapshot evidence — not a live metric. Re-derive before citing in architecture docs.*
