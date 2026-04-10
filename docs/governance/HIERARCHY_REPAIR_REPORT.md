# Hierarchy Repair Report

> Date: 2026-04-10 | Auditor: Claude Code | Scope: All 223 Tasks

---

## Methodology

1. Fetched all 223 Tasks, 104 Issues, 25 Epics from Azure Boards
2. For each Task, resolved parent link via `System.LinkTypes.Hierarchy-Reverse`
3. Classified parent as Epic (violation), Issue (correct), or none (unparented)
4. Applied deterministic fixes only — no ambiguous or speculative linking

---

## Pre-Repair State

| Category | Count |
|----------|-------|
| Task→Issue (correct) | 215 |
| Task→Epic (violation) | 3 |
| Unparented | 5 |
| **Total** | **223** |

---

## Repairs Applied

### Category 1: Hierarchy Violations (Task→Epic → Task→Issue→Epic)

Tasks #284, #285, #286 were linked directly to **Epic #63** (Execute Odoo 18 Go-Live Critical Path), bypassing the Issue layer.

**Fix:** Created **Issue #357** "Go-Live Wave C: Load test, smoke suite, and readiness signoff" under Epic #63, then re-parented all 3 tasks to Issue #357.

| Task # | Title | Old Parent | New Parent |
|--------|-------|------------|------------|
| 284 | Wave C1: Run concurrent k6 load test against production path | Epic #63 | Issue #357 |
| 285 | Wave C2: Execute full production-path smoke suite | Epic #63 | Issue #357 |
| 286 | Wave C3: Go-live readiness signoff — all gates green | Epic #63 | Issue #357 |

### Category 2: Unparented Tasks (deterministic match)

All 5 unparented tasks matched a single Issue by domain keyword with no ambiguity.

| Task # | Title | State | Linked To | Match Reason |
|--------|-------|-------|-----------|--------------|
| 280 | Baseline load test — P50=278ms P95=324ms 0% errors | Done | Issue #247 (Go-Live Critical Path) | Load test = go-live verification |
| 281 | Wave A1: Migrate ACA apps to ipai-odoo-ha-env | Done | Issue #353 (VNet-inject ACA environments) | ACA migration = VNet injection scope |
| 282 | Wave A1: Verify private-path PG connectivity from ACA | Done | Issue #349 (Disable PG public access) | Private-path PG = public access closure |
| 283 | Wave A2: Re-disable PG public access after private-path verified | Done | Issue #349 (Disable PG public access) | Exact scope match |
| 293 | Alert routing verification — test notification succeeded | Done | Issue #350 (Wire diagnostic settings) | Alert routing = observability |

### Category 3: Ambiguous / Manual Review

None. All 8 items had deterministic matches.

---

## Post-Repair State

| Category | Count |
|----------|-------|
| Task→Issue (correct) | **223** |
| Task→Epic (violation) | **0** |
| Unparented | **0** |

---

## Governance Prevention

To prevent future orphan Tasks or hierarchy violations:

1. **Board rule (recommended):** Azure Boards supports work item rules — add a rule on Task type requiring `System.Parent` to be set and parent type to be Issue.
2. **CI check:** A scheduled pipeline can run the same WIQL audit query and fail if any Task has no parent or has an Epic parent.
3. **Process:** When creating Tasks via `az boards work-item create`, always include `--relation-type parent --target-id <issue_id>` in the same operation.

---

*Verified: 223/223 Tasks have correct Epic→Issue→Task hierarchy.*
