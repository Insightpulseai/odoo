# EE-OCA Parity — Tasks

> **Spec**: `spec/ee-oca-parity/`
> **Status**: Active
> **Last updated**: 2026-02-17

---

## Completed

- [x] **T-1** Generate initial EE module mapping (151 modules) via `scripts/ee_oca_parity_proof.py`
- [x] **T-2** Create `reports/ee_oca_parity_proof.json` with T1 evidence
- [x] **T-3** Write constitution with taxonomy (Parity Addon / Bridge / Thin Connector / Meta-module)
- [x] **T-4** Write PRD with evidence tier definitions (T1-T4)
- [x] **T-5** Classify OCA repos by kind (addons_repo, infra_repo, core_fork, migration_tooling)

## In Progress

- [ ] **T-6** Create `scripts/ci/test_oca_install.sh` for automated T2 installability checks
- [ ] **T-7** Run T2 Batch 1 (top 20 OCA modules) against Odoo 18 CE baseline
- [ ] **T-8** Create `scripts/ci/check_parity_boundaries.sh` CI gate

## Backlog

- [ ] **T-9** Create bundle meta-modules (`ipai_bundle_finance`, `ipai_bundle_hr`, etc.)
- [ ] **T-10** Run T2 Batch 2+ (remaining mapped OCA modules)
- [ ] **T-11** Create functional checklists for Accounting domain
- [ ] **T-12** Create functional checklists for Helpdesk domain
- [ ] **T-13** Deploy Accounting bundle to staging for T3 validation
- [ ] **T-14** Deploy Helpdesk bundle to staging for T3 validation
- [ ] **T-15** Create `scripts/ci/check_staging_drift.sh` for staging/production parity
- [ ] **T-16** 30-day production soak for Accounting domain (T4)
- [ ] **T-17** 30-day production soak for Helpdesk domain (T4)
