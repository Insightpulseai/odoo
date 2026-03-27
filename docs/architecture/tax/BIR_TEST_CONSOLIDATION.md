# Tax/BIR Benchmark and Test Asset Consolidation Report

> Scan date: 2026-03-18 | Repos scanned: odoo (primary), agents (secondary)
> Inventory SSOT: `ssot/evals/tax_bir_benchmark_test_inventory.yaml`
> Gap analysis: `ssot/evals/tax_bir_benchmark_gap_analysis.yaml`

---

## Decision Note

This consolidation is sufficient for planning and migration, but **not yet sufficient for benchmark execution**.

Blocking conditions:

1. **6 discovered assets are not verified on disk** and must not be treated as canonical. They are reclassified as `unverified_local` with `recommended_action: verify_or_drop`.
2. **ATC namespace divergence** between Odoo (W-series: W010, W020) and platform/Supabase (WI/WC-series: WI010, WC010) **invalidates withholding-related benchmark trust** until reconciled. See `GAP-ATC-001` and `ssot/domain/atc_code_mapping.yaml`.

---

## Executive Summary

A filesystem scan of the `Insightpulseai/odoo` repo and `agents` working directory
identified **17 active** and **4 legacy** assets related to tax/BIR benchmarking
and compliance testing. Assets span six categories: benchmark specifications,
governance doctrine, implementation scripts, Odoo unit tests with fixtures,
spec bundles, and CI workflows. Four legacy eval scripts exist in `archive/`
and are superseded by the current benchmark framework.

**Key finding**: The existing assets form a solid foundation but lack the
production-grade evaluation pipeline needed for deployment-gating. Critical gaps
include: no gold-output task suite, no custom Foundry evaluators, no CI gate
that blocks deploys on eval regression, and no repeated-run consistency harness.

---

## Repos Scanned

| Repo | Path | Scan Result |
|------|------|-------------|
| odoo (primary) | `/Users/tbwa/Documents/GitHub/Insightpulseai/odoo` | 17 active + 4 legacy assets |
| agents (secondary) | `/Users/tbwa/Documents/GitHub/Insightpulseai/agents` | 0 benchmark assets found locally (lib_benchmark.py, evaluator.py, run_benchmark.py not present on disk) |

**Note**: The agents repo `scripts/lib/lib_benchmark.py`, `scripts/benchmark/evaluator.py`,
and `scripts/benchmark/run_benchmark.py` were reported in the original inventory but
are not present on the local filesystem as of scan date. They may exist in a different
branch or have been relocated. These are tracked as reported but flagged `unverified_local`.

---

## Assets by Category

### 1. Benchmark Specifications (2 active)

| Asset | Path | Scope |
|-------|------|-------|
| AvaTax vs IPAI Benchmark | `ssot/evals/copilot_marketplace_benchmark.yaml` | Tax/compliance (6 dimensions, 9 task sets) |
| Agent Benchmark Doctrine | `ssot/evals/agent_benchmark_doctrine.yaml` | General governance (research-backed baselines) |

### 2. Documentation (2 active)

| Asset | Path | Scope |
|-------|------|-------|
| Benchmark Doctrine (human-readable) | `docs/evals/agent_benchmark_doctrine.md` | General governance companion |
| TaxPulse Salvage Map | `docs/architecture/TAXPULSE_SALVAGE_MAP.md` | Legacy TaxPulse mapping |

### 3. Implementation (3 reported, 0 verified locally)

| Asset | Reported Path | Status |
|-------|---------------|--------|
| Scoring engine | `scripts/benchmark/evaluator.py` | Not found on local disk |
| Benchmark orchestrator | `scripts/benchmark/run_benchmark.py` | Not found on local disk |
| Shared benchmark library | `agents/scripts/lib/lib_benchmark.py` | Not found in agents working dir |

### 4. Odoo Tax Compliance Tests (3 active)

| Asset | Path |
|-------|------|
| EWT computation tests | `addons/ipai/ipai_bir_tax_compliance/tests/test_bir_ewt_compute.py` |
| VAT computation tests | `addons/ipai/ipai_bir_tax_compliance/tests/test_bir_vat_compute.py` |
| BIR rules engine tests | `addons/ipai/ipai_bir_tax_compliance/tests/test_rules_engine.py` |

### 5. Test Fixtures (3 active)

| Asset | Path |
|-------|------|
| EWT expected withholding | `addons/ipai/ipai_bir_tax_compliance/tests/fixtures/ewt_expected_withholding.csv` |
| VAT expected lines | `addons/ipai/ipai_bir_tax_compliance/tests/fixtures/vat_basic_expected_lines.csv` |
| VAT basic transactions | `addons/ipai/ipai_bir_tax_compliance/tests/fixtures/vat_basic_transactions.csv` |

### 6. Spec Bundles (3 active)

| Asset | Path | Contents |
|-------|------|----------|
| Copilot Benchmark | `spec/odoo-copilot-benchmark/` | constitution, prd, plan, tasks |
| TaxPulse Sub-Agent | `spec/tax-pulse-sub-agent/` | constitution, prd, plan, tasks |
| Copilot Target State | `spec/copilot-target-state/` | constitution, prd, plan, tasks |

### 7. CI Workflows (1 reported, 0 verified)

| Asset | Reported Path | Status |
|-------|---------------|--------|
| Copilot eval workflow | `.github/workflows/odoo-copilot-eval.yml` | Not found on local disk |

### 8. Legacy (4 archived)

| Asset | Path | Status |
|-------|------|--------|
| Action eval runner | `archive/root/scripts/eval/run_action_eval.py` | Archived |
| Knowledge eval runner | `archive/root/scripts/eval/run_knowledge_eval.py` | Archived |
| Action eval config | `archive/eval/action_eval.yaml` | Archived |
| Knowledge eval config | `archive/eval/knowledge_copilot_eval.yaml` | Archived |

**Note**: `scripts/parity/evaluate_goals.py` and `scripts/run_coding_agent_eval.py`
were reported in the inventory but not found at those paths. References exist in
`docs/product/capability_map.json` and `docs/product/repo_inventory.json`.

---

## Duplicate / Conflict Analysis

### Overlap 1: General vs Tax-Specific Benchmark

`copilot_marketplace_benchmark.yaml` covers both general copilot capabilities and
tax-specific compliance. The AvaTax comparison is inherently tax-focused, but
the dimensions (latency, batch quality, explainability) are general-purpose.

**Recommendation**: Keep as-is for now. When a non-tax copilot benchmark is needed,
split the general dimensions into a separate YAML and have the tax benchmark
import them via `$ref` or `extends`.

### Overlap 2: Legacy Eval Scripts vs New Benchmark Framework

The `archive/` eval scripts (`run_action_eval.py`, `run_knowledge_eval.py`) are
superseded by the benchmark framework described in the doctrine. They use different
scoring models and output formats.

**Recommendation**: Mark archived. Do not port forward. Extract any reusable test
case definitions into the new framework's task suite format.

### Overlap 3: Spec Bundle Boundaries

`spec/odoo-copilot-benchmark/` and `spec/tax-pulse-sub-agent/` have overlapping
scope around tax task definitions. The copilot benchmark defines tasks; the
TaxPulse spec defines the agent that executes them.

**Recommendation**: Keep separate. The benchmark spec owns task definitions and
scoring rubrics. The agent spec owns architecture and tool bindings. Cross-reference
via `doctrine_ref` fields.

---

## Canonical Ownership

| Asset Class | Owner | Location |
|-------------|-------|----------|
| BIR tax unit tests + fixtures | odoo repo, `addons/ipai/` | `addons/ipai/ipai_bir_tax_compliance/tests/` |
| Benchmark doctrine (YAML + MD) | odoo repo, `ssot/evals/` + `docs/evals/` | Current locations are canonical |
| AvaTax benchmark spec | odoo repo, `ssot/evals/` | Current location is canonical |
| Spec bundles (benchmark, TaxPulse, target state) | odoo repo, `spec/` | Current locations are canonical |
| Agent-level evaluators (when created) | odoo repo, `scripts/benchmark/` | To be created |
| CI benchmark workflow (when created) | odoo repo, `.github/workflows/` | To be created |
| Legacy eval scripts | odoo repo, `archive/` | Archived, do not resurrect |

---

## Reusable NOW

1. **BIR tax tests + fixtures** -- EWT, VAT, and rules engine tests with CSV fixtures are production-quality and can be extended for agent evaluation scenarios
2. **Benchmark doctrine** (`ssot/evals/agent_benchmark_doctrine.yaml` + `docs/evals/agent_benchmark_doctrine.md`) -- governance framework with research baselines (WebArena 14.41%, GAIA 15%, TheAgentCompany 30%)
3. **AvaTax benchmark spec** (`ssot/evals/copilot_marketplace_benchmark.yaml`) -- 6 fair dimensions, 9 task sets, multi-judge verdict rules
4. **Spec bundles** -- constitution, PRD, plan, and task definitions for benchmark, TaxPulse agent, and target state
5. **TaxPulse Salvage Map** -- mapping of legacy TaxPulse capabilities to current architecture

---

## MISSING (Critical Gaps)

See `ssot/evals/tax_bir_benchmark_gap_analysis.yaml` for the full machine-readable gap list (12 gaps).

Summary of highest-priority gaps:

1. **No canonical tax task suite with gold outputs** (GAP-001) -- need 25-40 tasks with expected correct answers
2. **No custom Foundry evaluators** (GAP-002) -- tax accuracy, BIR compliance, withholding correctness
3. **No CI benchmark gate** (GAP-006) -- deploys are not blocked on eval regression
4. **No repeated-run harness** (GAP-004) -- cannot measure consistency across 5+ runs
5. **No BIR form correctness evaluator** (GAP-009) -- 1601-C, 2550M/Q, 1702-RT form validation

---

## Migration Priority

See `docs/architecture/TAX_BIR_BENCHMARK_MIGRATION_PLAN.md` for the full phased plan.

| Phase | Focus | Status |
|-------|-------|--------|
| 0 | Freeze -- stop creating benchmark assets outside canonical locations | Active |
| 1 | Inventory -- this scan | Done |
| 2 | Consolidate specs and split general/tax benchmark | Next |
| 3 | Build fixtures, gold outputs, and custom evaluators | Planned |
| 4 | Wire CI gate and evidence-pack contract | Planned |
| 5 | Production continuous evaluation and red-team | Planned |

---

*Generated by tax/BIR benchmark scan, 2026-03-18*
