# Tax/BIR Benchmark Migration Plan

> Inventory: `ssot/evals/tax_bir_benchmark_test_inventory.yaml`
> Gap analysis: `ssot/evals/tax_bir_benchmark_gap_analysis.yaml`
> Consolidation report: `docs/architecture/TAX_BIR_BENCHMARK_TEST_CONSOLIDATION.md`

---

## Overview

This plan consolidates 21 discovered benchmark/test assets (17 active, 4 legacy)
into a canonical evaluation pipeline for the IPAI tax/compliance copilot. The plan
closes 12 identified gaps across five phases.

---

## Phase 0: Freeze (Immediate)

**Goal**: Stop creating benchmark assets outside canonical locations.

| Action | Owner | Status |
|--------|-------|--------|
| All new benchmark specs go to `ssot/evals/` | All contributors | Enforced |
| All new test tasks go to `ssot/evals/tasks/` | All contributors | Enforced |
| All new evaluators go to `scripts/benchmark/evaluators/` | All contributors | Enforced |
| No new eval scripts in `scripts/eval/` (legacy path) | All contributors | Enforced |
| No new benchmark assets in `agents/` repo without cross-ref in odoo SSOT | All contributors | Enforced |

**Canonical paths**:

```
ssot/evals/                          # Benchmark specs, inventory, gap analysis
ssot/evals/tasks/                    # Task suites (JSONL)
ssot/evals/rubrics/                  # Human review rubrics
ssot/evals/baselines/                # Score baselines for CI gating
scripts/benchmark/                   # Orchestrator, harness
scripts/benchmark/evaluators/        # Custom evaluator implementations
docs/evals/                          # Human-readable doctrine and reports
docs/architecture/                   # Consolidation report, migration plan
spec/odoo-copilot-benchmark/         # Benchmark spec bundle
spec/tax-pulse-sub-agent/            # TaxPulse agent spec bundle
spec/copilot-target-state/           # Copilot target state spec bundle
addons/ipai/ipai_bir_tax_compliance/tests/  # Odoo module-level tests
```

---

## Phase 1: Inventory (Done)

**Goal**: Complete asset scan and gap analysis.

| Deliverable | Path | Status |
|-------------|------|--------|
| Consolidation report | `docs/architecture/TAX_BIR_BENCHMARK_TEST_CONSOLIDATION.md` | Done |
| Machine-readable inventory | `ssot/evals/tax_bir_benchmark_test_inventory.yaml` | Done |
| Gap analysis | `ssot/evals/tax_bir_benchmark_gap_analysis.yaml` | Done |
| Migration plan | `docs/architecture/TAX_BIR_BENCHMARK_MIGRATION_PLAN.md` | Done |
| Evidence pack | `docs/evidence/tax-bir-benchmark-scan/README.md` | Done |

**Findings**:
- 14 assets verified on disk
- 5 assets reported but not found locally (flagged `unverified_local`)
- 2 legacy assets confirmed in `archive/`
- 2 legacy assets referenced in docs but removed from disk
- 12 gaps identified (4 critical, 3 high, 4 medium, 1 medium)

---

## Phase 1A: Canonical Tax-Code Reconciliation (BLOCKING)

**Priority**: Blocking — no benchmark, evaluator, or agent recommendation involving withholding tax can be trusted until ATC code mapping is canonical.

**Gap reference**: `GAP-ATC-001` in `ssot/evals/tax_bir_benchmark_gap_analysis.yaml`

| Action | Deliverable | Status |
|--------|-------------|--------|
| Enumerate all observed Odoo ATC codes | Code inventory from `ipai_bir_tax_compliance` | Not started |
| Enumerate all observed platform ATC codes | Code inventory from Supabase tables | Not started |
| Define canonical namespace | Decision in `ssot/domain/atc_code_mapping.yaml` | Draft created |
| Create explicit crosswalk mapping | Mapping table in `atc_code_mapping.yaml` | Not started |
| Add deterministic validation tests | Tests that fail on unmapped codes | Not started |
| Update agent rule pack to use canonical codes | Rule pack patch | Not started |

**Rationale**: The Odoo module uses W-series codes (W010, W020) while Supabase uses WI/WC-series (WI010, WC010). This divergence means any withholding-related benchmark task will produce unreliable results, and any agent recommendation touching EWT/FWT codes could be wrong.

**Exit criteria**: `ssot/domain/atc_code_mapping.yaml` status changes from `draft` to `resolved`, with a complete mapping table and passing validation tests.

---

## Phase 2: Consolidate Specs

**Goal**: Merge overlapping specifications and resolve unverified assets.

### 2.1 Resolve Unverified Assets

| Asset | Action |
|-------|--------|
| `scripts/benchmark/evaluator.py` (EVAL-005) | Search all branches. If found, restore to canonical path. If not, create stub. |
| `scripts/benchmark/run_benchmark.py` (EVAL-006) | Search all branches. If found, restore to canonical path. If not, create stub. |
| `agents/scripts/lib/lib_benchmark.py` (EVAL-007) | Check agents repo remote. Decide: consolidate into odoo or keep with cross-ref. |
| `.github/workflows/odoo-copilot-eval.yml` (EVAL-017) | Search workflow history. If deleted, recreate in Phase 4. |
| `scripts/parity/evaluate_goals.py` (EVAL-020) | Confirm removed. Remove references from capability_map.json. |

### 2.2 Clarify Spec Bundle Boundaries

| Spec Bundle | Owns | Does NOT Own |
|-------------|------|-------------|
| `spec/odoo-copilot-benchmark/` | Benchmark task definitions, scoring rubrics, dimension weights | Agent architecture, tool bindings |
| `spec/tax-pulse-sub-agent/` | TaxPulse agent architecture, tool bindings, capability map | Benchmark scoring, evaluation methodology |
| `spec/copilot-target-state/` | Copilot target architecture, integration points | Task-level definitions, scoring |

Add `boundary_note` to each spec bundle's `constitution.md` clarifying ownership.

### 2.3 Consider Splitting copilot_marketplace_benchmark.yaml

Current state: single YAML covers both general copilot and tax-specific dimensions.

Decision criteria:
- If a non-tax copilot benchmark is needed within 3 months: split now
- If tax-only for the foreseeable future: keep unified, add a `scope: tax` filter

**Recommendation**: Keep unified for now. Add `scope` field to task sets so they
can be filtered at runtime. Split when a non-tax copilot benchmark is actually needed.

---

## Phase 3: Consolidate Fixtures and Evaluators

**Goal**: Build the missing evaluation infrastructure.

### 3.1 Create Gold-Output Task Suite (GAP-001)

**Deliverable**: `ssot/evals/tasks/tax_compliance_tasks.jsonl`

Format per line:
```json
{
  "task_id": "TAX-001",
  "category": "ewt_computation",
  "prompt": "Compute EWT for a PHP 100,000 professional fee payment to a domestic corporation",
  "context": {"vendor_type": "domestic_corp", "service_type": "professional_fee", "amount": 100000},
  "expected_output": {"ewt_rate": 0.10, "ewt_amount": 10000, "atc_code": "WI100", "net_payment": 90000},
  "scoring_rubric": {"accuracy": "exact_match", "tolerance": 0.01},
  "difficulty": "basic",
  "bir_form": "1601-C",
  "source": "BIR RR 2-98 as amended"
}
```

Target: 25-40 tasks covering EWT, VAT, FWT, mixed transactions, edge cases.

### 3.2 Build Custom Foundry Evaluators (GAP-002)

| Evaluator | Path | Validates |
|-----------|------|-----------|
| `tax_accuracy_evaluator.py` | `scripts/benchmark/evaluators/` | Computed amounts vs gold outputs (tolerance: 0.01 PHP) |
| `bir_compliance_evaluator.py` | `scripts/benchmark/evaluators/` | BIR form field mapping, ATC codes, filing periods |
| `withholding_evaluator.py` | `scripts/benchmark/evaluators/` | EWT/FWT rate selection against Revenue Regulations |

### 3.3 Build BIR Form Evaluator (GAP-009)

**Deliverable**: `scripts/benchmark/evaluators/bir_form_evaluator.py`

Validates agent-generated BIR forms (1601-C, 2550M/Q, 1702-RT) against
BIR form schemas. Checks field mappings, computed totals, ATC codes.

### 3.4 Create Human Review Rubric (GAP-003)

**Deliverable**: `ssot/evals/rubrics/tax_expert_review_rubric.yaml`

5 dimensions, 5-point scale each, with calibration examples.

### 3.5 Create Agent Demo Fixtures (GAP-011)

**Deliverable**: `addons/ipai/ipai_bir_tax_compliance/tests/fixtures/agent_demo/`

Realistic business documents for agent-level simulation.

---

## Phase 4: Wire CI Gate

**Goal**: Benchmark results gate deployments.

### 4.1 Create Benchmark Gate Workflow (GAP-006)

**Deliverable**: `.github/workflows/benchmark-gate.yml`

Triggers on PR to main when tax-related paths change. Runs the task suite,
compares against baselines, fails if hard-gate dimensions regress.

### 4.2 Create Evidence-Pack Contract (GAP-008)

**Deliverable**: `docs/contracts/BENCHMARK_EVIDENCE_CONTRACT.md`

Standard format for benchmark evidence packs. Register in
`docs/contracts/PLATFORM_CONTRACTS_INDEX.md`.

### 4.3 Build Repeated-Run Harness (GAP-004)

**Deliverable**: `scripts/benchmark/repeated_run_harness.py`

Runs each task N times, computes pass@k, variance, failure mode distribution.

### 4.4 Build Integration Tests (GAP-010)

**Deliverable**: Integration test suite connecting Odoo tax module to agent eval pipeline.

---

## Phase 5: Production

**Goal**: Continuous evaluation and adversarial testing in production.

### 5.1 Continuous Evaluation (GAP-012)

Weekly cron job running the tax benchmark suite against staging.
Results stored in `docs/evidence/benchmark-runs/`. Regression alerts to Slack.

### 5.2 Production Trace Replay (GAP-005)

Trace capture format (JSONL). Replay harness for regression testing against
recorded production interactions.

### 5.3 Red-Team Scheduling (GAP-007)

**Deliverable**: `ssot/evals/tasks/tax_adversarial_tasks.jsonl`

10-15 adversarial scenarios: prompt injection, hallucination probing,
ambiguity exploitation, authorization bypass, edge-case tax scenarios.

### 5.4 Monitoring Dashboard

Benchmark trend dashboard (Superset or static HTML) showing score trends
over time, per-dimension breakdown, and regression alerts.

---

## Dependency Graph

```
Phase 0 (Freeze)
    |
Phase 1 (Inventory) ---- DONE
    |
Phase 2 (Consolidate Specs)
    |
Phase 3 (Fixtures + Evaluators)
    |         |
    |    GAP-001 (task suite) ---> GAP-002 (Foundry evaluators)
    |         |                         |
    |    GAP-011 (demo fixtures)   GAP-009 (BIR form evaluator)
    |         |
    |    GAP-003 (human rubric)
    |
Phase 4 (CI Gate)
    |         |
    |    GAP-006 (CI gate) <--- depends on GAP-001, GAP-002
    |         |
    |    GAP-004 (repeated-run harness)
    |         |
    |    GAP-008 (evidence-pack contract)
    |         |
    |    GAP-010 (integration tests)
    |
Phase 5 (Production)
    |         |
    |    GAP-012 (continuous eval) <--- depends on GAP-001, GAP-006
    |         |
    |    GAP-005 (trace replay)
    |         |
    |    GAP-007 (red-team)
```

---

## Effort Summary

| Phase | Estimated Effort | Gaps Closed |
|-------|-----------------|-------------|
| Phase 0 | 0 (policy only) | 0 |
| Phase 1 | Done | 0 (inventory) |
| Phase 2 | 1-2 days | 0 (cleanup) |
| Phase 3 | 10-16 days | 5 (GAP-001, 002, 003, 009, 011) |
| Phase 4 | 7-11 days | 4 (GAP-004, 006, 008, 010) |
| Phase 5 | 9-14 days | 3 (GAP-005, 007, 012) |
| **Total** | **27-43 days** | **12 gaps** |

---

*Generated by tax/BIR benchmark scan, 2026-03-18*
