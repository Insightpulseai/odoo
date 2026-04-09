# Tasks — Unified Finance System

> Checklist for unifying the finance system. Each task is independently
> committable. Order reflects dependency — earlier tasks unblock later ones.

---

## Phase 1: Classification and Alignment

- [x] **T1.1** Create unified spec bundle (`spec/finance-unified/`)
- [x] **T1.2** Classify active vs. deprecated modules in spec constitution
- [x] **T1.3** Define canonical seed strategy (XML = canonical, JSON = derived, SQL = deprecated)
- [x] **T1.4** Define canonical dependency graph
- [x] **T1.5** Verify `ipai_bir_tax_compliance` version is `18.0.1.0.0` (already aligned)
- [ ] **T1.6** Add `DEPRECATED` note to `ipai_finance_workflow` manifest description (if not already present)
- [ ] **T1.7** Add derivation note to `ipai_finance_closing_seed.json` (repo root)

## Phase 2: Canonical Documentation

- [x] **T2.1** Create `docs/modules/FINANCE_UNIFIED_SYSTEM.md`
- [ ] **T2.2** Verify existing module doc stubs do not contradict unified doc
- [ ] **T2.3** Add cross-reference from `finance_ppm_technical_guide.md` to unified doc

## Phase 2.5: Cross-Repo Capability Discovery (NEW)

- [ ] **T2.5.1** Build a cross-repo CE/OCA 18 capability inventory for PPM
- [ ] **T2.5.2** Map each PPM capability to one of: direct / composable / unresolved
- [ ] **T2.5.3** Prove candidate compositions for issue, risk, governance, and dashboards
- [ ] **T2.5.4** Only then open custom-delta tasks for unresolved capabilities

### Specific discovery lanes

- [ ] **T2.5.5** Evaluate OCA/helpdesk as issue-register substrate
- [ ] **T2.5.6** Evaluate OCA/knowledge as approval / decision-log / governance substrate
- [ ] **T2.5.7** Evaluate OCA/spreadsheet + MIS Builder for portfolio dashboarding
- [ ] **T2.5.8** Evaluate project-agile for demand/backlog approximation
- [ ] **T2.5.9** Evaluate accounting / analytic budget surfaces for financial rollups

## Phase 3: Seed Validation Tests

- [ ] **T3.1** Create `ipai_finance_close_seed/tests/__init__.py` and `test_seed_integrity.py`
  - Validate stages (6), tags (33), team (9), projects (2), milestones (11)
  - Validate close tasks (39) and BIR tasks (50)
  - Validate all XML ID references resolve
- [ ] **T3.2** Create `ipai_bir_tax_compliance/tests/test_bir_schedules.py`
  - Validate monthly/quarterly/annual form coverage
  - Validate tax rate data loaded
  - Validate filing deadline data loaded
- [ ] **T3.3** Create `ipai_finance_ppm/tests/test_ppm_smoke.py`
  - Module install smoke test
  - Field extension existence checks
  - Wizard and dashboard action checks

## Phase 4: Contract Tests

- [ ] **T4.1** Create `tests/contracts/test_finance_system.py`
  - Deprecated modules remain `installable: False`
  - Active modules version-aligned to 18.0
  - Canonical doc and spec bundle existence checks
- [ ] **T4.2** Add finance system contract tests to CI workflow

## Phase 5: Satellite Module Activation (Deferred)

- [ ] **T5.1** Validate `ipai_bir_notifications` mail templates and cron jobs
  - Set `installable: True` only after validation passes
- [ ] **T5.2** Validate `ipai_bir_plane_sync` API connectivity
  - Set `installable: True` only after end-to-end sync is tested
- [ ] **T5.3** Add tests for notification delivery and Plane sync

## Phase 6: Cleanup (Optional)

- [ ] **T6.1** Consolidate overlapping docs (if any contradict unified doc)
- [ ] **T6.2** Add `002_finance_seed.sql` deprecation to Supabase migration notes
- [ ] **T6.3** Integrate finance system with Power BI (via Databricks SQL / Unity Catalog)

---

## Status Key

- [x] = complete (shipped in this spec creation pass)
- [ ] = pending (requires implementation work)

## Dependency Map

```
T1.1–T1.4 ──► T2.1 ──► T2.2, T2.3
T1.5–T1.7 ──► T4.1 (version alignment needed before contract tests)
T2.1 ──► T2.5.1–T2.5.9 (cross-repo scan before custom build decisions)
T2.5.* ──► T3.3 (PPM smoke tests depend on sourcing decisions)
T2.1 ──► T3.1, T3.2 (tests reference canonical doc for expected counts)
T3.* ──► T4.2 (tests must exist before adding to CI)
T4.1 ──► T5.* (contract tests gate satellite activation)
```
