# OCA Repo Intake Matrix

> **Source**: 45 OCA repos referenced in `docs/evidence/20260217-1820/parity/ee_oca_parity_proof.md`
> **Curated baseline**: 36 repos in `oca-aggregate.yml` + `vendor/oca.lock.ce19.json`
> **Delta**: 9 candidate repos for evaluation
> **Date**: 2026-03-08
> **Branch**: `claude/wave2-clean`

---

## Purpose

The parity proof references 45 OCA repos. Our curated aggregate/lock has 36.
These 9 candidates need screening before inclusion — not all referenced repos
belong in the curated baseline.

## Decision Criteria

| Criterion | Required for INCLUDE |
|-----------|---------------------|
| Odoo 18 branch exists | Yes |
| At least one module needed for active P0/P1 feature | Yes |
| Not already covered by existing repo | Yes |
| Has installable modules (not empty 19.0 branch) | Yes |
| Active maintenance (commits in last 6 months) | Preferred |

---

## Candidate Repos

| # | Repo | Target EE Gap | Odoo 18 Compat | Dependency Impact | Decision | Rationale |
|---|------|---------------|----------------|-------------------|----------|-----------|
| 1 | **OCA/payroll** | `hr_payroll` (P0) | Unknown — needs 19.0 branch check | `ipai_hr_payroll_ph` depends on OCA payroll engine | **EVALUATE** | High priority. Check `payroll`, `payroll_account` on 19.0. |
| 2 | **OCA/field-service** | `industry_fsm` (P2) | Unknown | None — no ipai_* module exists | **DEFER** | P2. No active FSM use case. |
| 3 | **OCA/hr-attendance** | `hr_attendance` (P1) | Unknown — needs 19.0 branch check | Replaces DEPRECATED `ipai_planning_attendance` | **EVALUATE** | OCA attendance replaces deprecated ipai module. |
| 4 | **OCA/hr-holidays** | `hr_holidays` (P1) | Unknown — needs 19.0 branch check | No existing ipai_* — net new capability | **EVALUATE** | Standard HR need. Check 19.0 module availability. |
| 5 | **OCA/sign** | `sign` (P2) | Likely no 19.0 port | `ipai_sign` already DEPRECATED | **DEFER** | P2. OCA sign_oca may not have 19.0 port. |
| 6 | **OCA/commission** | None (P3) | N/A | None | **REJECT** | No active commission use case. |
| 7 | **OCA/delivery-carrier** | None (P3) | N/A | None | **REJECT** | No active shipping/logistics use case. |
| 8 | **OCA/stock-logistics-barcode** | None (P3) | N/A | None | **REJECT** | No warehouse operations. |
| 9 | **OCA/stock-logistics-workflow** | None (P3) | N/A | None | **REJECT** | No warehouse operations. |

---

## Decision Summary

| Decision | Count | Repos |
|----------|-------|-------|
| **EVALUATE** | 3 | payroll, hr-attendance, hr-holidays |
| **DEFER** | 2 | field-service, sign |
| **REJECT** | 4 | commission, delivery-carrier, stock-logistics-barcode, stock-logistics-workflow |

## Next Steps for EVALUATE Repos

For each EVALUATE candidate:

1. Check if OCA repo has a `19.0` branch with installable modules
2. Identify specific modules needed
3. Test installation on Odoo 18 CE baseline (`--stop-after-init`)
4. If installable, add to `oca-aggregate.yml` and `vendor/oca.lock.ce19.json`
5. Run `python3 scripts/oca/validate_aggregate.py` to confirm sync
6. Update `ssot/parity/ee_oca_verification_matrix.yaml` tier from T1 to T2

## Blocked Inclusions

Do **not** add repos to aggregate/lock based on research reference alone.
Each inclusion must pass the decision criteria above and have a documented
installation test result.

---

*Intake screening — not an automatic inclusion list.*
