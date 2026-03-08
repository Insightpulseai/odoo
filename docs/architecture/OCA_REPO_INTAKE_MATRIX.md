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
| Odoo 19 branch exists | Yes |
| At least one module needed for active P0/P1 feature | Yes |
| Not already covered by existing repo | Yes |
| Has installable modules (not empty 19.0 branch) | Yes |
| Active maintenance (commits in last 6 months) | Preferred |

---

## Candidate Repos

| # | Repo | Research Reference | Current Need | Decision | Rationale |
|---|------|--------------------|--------------|----------|-----------|
| 1 | **OCA/payroll** | HR payroll (P0) | `ipai_hr_payroll_ph` depends on OCA payroll engine for base salary rules | **EVALUATE** | High priority. Check if 19.0 branch has `payroll`, `payroll_account`. ipai_hr_payroll_ph already exists as PH overlay. |
| 2 | **OCA/field-service** | Field Service (P2) | No current ipai_* module for FSM | **DEFER** | P2 priority. No active FSM use case. Include when FSM feature is scoped. |
| 3 | **OCA/hr-attendance** | Attendance tracking (P1) | `ipai_planning_attendance` is DEPRECATED | **EVALUATE** | OCA attendance modules could replace deprecated ipai module. Check 19.0 status. |
| 4 | **OCA/hr-holidays** | Leave management (P1) | No current ipai_* for leave | **EVALUATE** | Standard HR need. Check if 19.0 branch has usable modules. |
| 5 | **OCA/sign** | E-signature (P2) | `ipai_sign` is DEPRECATED | **DEFER** | P2 priority. `ipai_sign` already deprecated. OCA sign_oca may not have 19.0 port. |
| 6 | **OCA/commission** | Sales commission (P3) | No current need | **REJECT** | P3 low priority. No active commission use case. |
| 7 | **OCA/delivery-carrier** | Shipping (P3) | No current need | **REJECT** | P3 low priority. No active shipping/logistics use case. |
| 8 | **OCA/stock-logistics-barcode** | Warehouse barcode (P3) | No current need | **REJECT** | P3 low priority. No warehouse operations. |
| 9 | **OCA/stock-logistics-workflow** | Stock workflow (P3) | No current need | **REJECT** | P3 low priority. No warehouse operations. |

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
3. Test installation on Odoo 19 CE baseline (`--stop-after-init`)
4. If installable, add to `oca-aggregate.yml` and `vendor/oca.lock.ce19.json`
5. Run `python3 scripts/oca/validate_aggregate.py` to confirm sync
6. Update `ssot/parity/ee_oca_verification_matrix.yaml` tier from T1 to T2

## Blocked Inclusions

Do **not** add repos to aggregate/lock based on research reference alone.
Each inclusion must pass the decision criteria above and have a documented
installation test result.

---

*Intake screening — not an automatic inclusion list.*
