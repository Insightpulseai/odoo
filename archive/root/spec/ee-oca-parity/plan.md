# EE-OCA Parity — Implementation Plan

> **Version**: 1.0.0
> **Spec**: `spec/ee-oca-parity/`
> **Status**: Active

---

## Overview

This plan covers progressing from Tier 1 (Mapped) through Tier 4 (Verified)
for all 151 EE module replacements. Work is organized in phases aligned with
the evidence tier model defined in `constitution.md`.

---

## Phase 1: T1 Maintenance (Ongoing)

1. Keep `reports/ee_oca_parity_proof.json` up to date as OCA repos evolve.
2. Run `scripts/ee_oca_parity_proof.py` weekly in CI to detect repo renames or deletions.
3. Ensure every EE module has a `strategy` field (oca | bridge | config | delta).

---

## Phase 2: T2 — Installability Verification (Batch)

### Batch 1 (Top 20 modules by IPAI workflow priority)

1. Create `scripts/ci/test_oca_install.sh` to run `odoo-bin -i <module> --stop-after-init`.
2. Run Batch 1 against Odoo 18 CE + PostgreSQL 16 baseline.
3. Record per-module install evidence (exit code, log hash, date).
4. Update `reports/ee_oca_parity_proof.json` tier field from T1 to T2 for passing modules.
5. File issues for modules that fail install (dependency gaps, 19.0 port needed).

### Batch 2+ (Remaining modules)

6. Extend `test_oca_install.sh` to iterate all mapped OCA modules.
7. Run in CI on weekly schedule.
8. Target: all mapped modules at T2 by end of Q2 2026.

---

## Phase 3: T3 — Functional Verification (Per Domain)

1. Identify priority domains: Accounting, Helpdesk, Project, HR.
2. Create per-domain functional checklists in `docs/evidence/<date>/parity/<domain>_functional.md`.
3. Deploy domain bundle modules (`ipai_bundle_finance`, etc.) to staging.
4. Execute functional checklists against staging environment.
5. Promote passing domains to T3 in the parity report.

---

## Phase 4: T4 — Production Verification

1. Deploy T3-verified domains to production via bundle modules.
2. Monitor for 30-day soak period (no regressions).
3. Document rollback plan per domain.
4. Promote to T4 upon successful soak completion.

---

## CI Gates

| Gate | Script | Blocks |
|------|--------|--------|
| Parity boundaries | `scripts/ci/check_parity_boundaries.sh` | PR merge |
| Install proof required for main | `scripts/ci/test_oca_install.sh` | Merge to main (new OCA modules) |
| Staging drift check | `scripts/ci/check_staging_drift.sh` | T3 promotion |

---

## Dependencies

- OCA repos must have 19.0 branches (or latest available).
- Staging environment must mirror production topology.
- Bundle modules must be created per domain before T3 testing.
