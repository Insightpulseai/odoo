# Examples — odoo-maintainer-quality-gate

## Example 1: Approved — Stable module with clean install

**Input**: Evaluate `queue_job` from OCA/queue for adoption

**Output**:
- Module: queue_job, OCA/queue, 19.0 branch
- CI status: passing — PASS
- Development status: Stable — PASS
- Test install: `test_queue_job` — PASS (12 tests, 12 pass)
- Conflict check: no conflicts with ipai_* — PASS
- EE dependencies: none — PASS
- Manifest entry: present in addons.manifest.yaml (tier 0, queue repo) — PASS
- Coverage: 85%
- Verdict: APPROVE
- Required actions: none

## Example 2: Rejected — Beta module

**Input**: Evaluate `web_tree_dynamic_colored_field` from OCA/web for adoption

**Output**:
- Module: web_tree_dynamic_colored_field, OCA/web, 19.0 branch
- CI status: passing — PASS
- Development status: Beta — FAIL (below Stable threshold)
- Test install: `test_web_tree_dynamic_colored_field` — PASS
- Conflict check: no conflicts — PASS
- EE dependencies: none — PASS
- Verdict: REJECT
- Reason: development_status is Beta — does not meet Stable minimum for production
- Required actions: wait for module to reach Stable status, or contribute to stabilization

## Example 3: Conditional — Missing manifest entry

**Input**: Evaluate `account_reconcile_oca` from OCA/account-reconcile for adoption

**Output**:
- Module: account_reconcile_oca, OCA/account-reconcile, 19.0 branch
- CI status: passing — PASS
- Development status: Mature — PASS
- Test install: `test_account_reconcile_oca` — PASS (28 tests, 28 pass)
- Conflict check: no conflicts — PASS
- EE dependencies: none — PASS
- Manifest entry: NOT present in addons.manifest.yaml — FAIL
- Coverage: 92%
- Verdict: CONDITIONAL
- Required actions: add entry to `config/addons.manifest.yaml` with repo=account-reconcile, tier=0, provenance=OCA

## Example 4: Rejected — Enterprise dependency

**Input**: Evaluate a module that depends on `documents_spreadsheet` (EE module)

**Output**:
- Module: hypothetical_spreadsheet_addon
- EE dependencies: depends on `documents_spreadsheet` (Enterprise) — FAIL (BLOCKER)
- Verdict: REJECT
- Reason: Enterprise module dependency violates CE-only policy
- Required actions: find CE-compatible alternative or remove dependency
