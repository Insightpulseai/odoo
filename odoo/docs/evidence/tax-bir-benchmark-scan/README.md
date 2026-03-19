# Tax/BIR Benchmark Scan Evidence

> Scan timestamp: 2026-03-18
> Scan type: Filesystem inventory of benchmark, evaluation, and tax compliance test assets

---

## Scope

### Repos Scanned

| Repo | Local Path | Role |
|------|-----------|------|
| odoo (primary) | `/Users/tbwa/Documents/GitHub/Insightpulseai/odoo` | Main monorepo |
| agents (secondary) | `/Users/tbwa/Documents/GitHub/Insightpulseai/agents` | Agent skills/integration working directory |

### Search Terms

The following terms were used for filesystem search (glob and grep):

- **Benchmark**: benchmark, eval, evaluator, evaluators, run_benchmark, lib_benchmark
- **Tax/BIR**: BIR, tax, compliance, TaxPulse, AvaTax, VAT, EWT, FWT, withholding
- **Evaluation**: rubric, scorecard, fixtures, test_cases, golden, gold_outputs
- **Security**: red_team, PyRIT, adversarial
- **Quality**: groundedness, task_adherence, hallucination
- **Patterns**: `**/benchmark/**`, `**/eval/**`, `**/evals/**`, `**/*tax*/**`, `**/*bir*/**`

### Directories Searched

```
ssot/evals/
docs/evals/
docs/architecture/
scripts/benchmark/
scripts/eval/
scripts/parity/
addons/ipai/ipai_bir_tax_compliance/
spec/odoo-copilot-benchmark/
spec/tax-pulse-sub-agent/
spec/copilot-target-state/
.github/workflows/
archive/root/scripts/eval/
archive/eval/
agents/scripts/lib/
agents/scripts/benchmark/
```

---

## Results Summary

| Category | Found | Verified on Disk | Unverified |
|----------|-------|-----------------|------------|
| Benchmark specs | 1 | 1 | 0 |
| Doctrine docs | 3 | 3 | 0 |
| Evaluators/runners | 3 | 0 | 3 |
| Odoo tax tests | 3 | 3 | 0 |
| Test fixtures | 3 | 3 | 0 |
| Spec bundles | 3 | 3 | 0 |
| CI workflows | 1 | 0 | 1 |
| Legacy scripts | 4 | 2 | 2 |
| **Total** | **21** | **15** | **6** |

---

## Deliverables Produced

| File | Path |
|------|------|
| Consolidation report | `docs/architecture/TAX_BIR_BENCHMARK_TEST_CONSOLIDATION.md` |
| Machine-readable inventory | `ssot/evals/tax_bir_benchmark_test_inventory.yaml` |
| Gap analysis | `ssot/evals/tax_bir_benchmark_gap_analysis.yaml` |
| Migration plan | `docs/architecture/TAX_BIR_BENCHMARK_MIGRATION_PLAN.md` |
| This evidence README | `docs/evidence/tax-bir-benchmark-scan/README.md` |

---

## Assumptions

1. Only the local filesystem was searched. No remote branches, PRs, or external repos were cloned or checked.
2. The `agents` working directory at `/Users/tbwa/Documents/GitHub/Insightpulseai/agents` was searched but yielded no benchmark assets. The reported `lib_benchmark.py`, `evaluator.py`, and `run_benchmark.py` may exist in a different branch or checkout.
3. The `TaxPulse-PH-Pack` (if it exists as a separate artifact) was not locally available and was not searched.
4. Asset statuses are based on filesystem presence. A file marked "active" in the inventory was verified on disk; a file marked "unverified_local" was reported in the original inventory but not found during this scan.
5. The `archive/` directory was treated as a valid search target for legacy assets.

---

## Limitations

1. **Runtime behavior not verified**: `evaluator.py`, `run_benchmark.py`, and `lib_benchmark.py` were not executed. Their correctness and compatibility with current dependencies are unknown.
2. **CI workflow not tested**: `.github/workflows/odoo-copilot-eval.yml` was not found on disk and could not be validated against current GitHub Actions runner configuration.
3. **Legacy scripts not tested**: `archive/root/scripts/eval/run_action_eval.py` and `run_knowledge_eval.py` were not executed. Their compatibility with current Python/Odoo versions is unknown.
4. **Odoo tax tests not executed**: `test_bir_ewt_compute.py`, `test_bir_vat_compute.py`, and `test_rules_engine.py` were verified to exist but were not run. Test pass/fail status is unknown for the current codebase state.
5. **No cross-branch search**: Only the current checked-out branch (`main`) was searched. Assets may exist on feature branches.
6. **No network calls**: No GitHub API, Azure, or other remote service was queried. The scan was entirely local.

---

*Scan completed 2026-03-18*
