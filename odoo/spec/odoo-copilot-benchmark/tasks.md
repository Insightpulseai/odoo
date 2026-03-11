# Odoo Copilot Benchmark — Task Checklist

Tasks organized by epic. Each epic ends with a hard verification gate.

---

## Epic 1: Schema + Registry Foundation

### Build
- [x] Define benchmark scenario YAML schema (`scenarios/_schema.yaml`)
- [x] Define evidence envelope JSON schema (`scenarios/_evidence_schema.yaml`)
- [x] Define scoring model with weighted dimensions (`benchmark.config.yaml`)
- [x] Create scenario registry directory structure for all 9 domains
- [x] Seed 9 CRM scenarios (3 transactional, 3 navigational, 3 informational)
- [x] Implement scenario validator (`odoo/scripts/benchmark/validate_scenarios.py`)
- [x] Implement runner skeleton with dry-run (`odoo/scripts/benchmark/run_benchmark.py`)

### Verification
- [x] Schema validates all 9 CRM example scenarios (3 files, 9 scenarios, 0 errors)
- [x] Evidence envelope schema is machine-parseable (JSON Schema draft-07)
- [x] Scoring weights configured per capability class in `benchmark.config.yaml`
- [x] Registry directory structure has all 9 domains
- [x] Runner dry-run lists all 9 scenarios correctly

**GATE: Epic 1 — PASSED. Schema validates, scenarios parse, runner skeleton functional.**

---

## Epic 2: Scenario Catalog v1

### Build
- [ ] CRM scenarios: 3 transactional, 3 navigational, 3 informational
- [ ] Sales scenarios: 3 transactional, 3 navigational, 3 informational
- [ ] Accounting scenarios: 3 transactional, 3 navigational, 3 informational
- [ ] Inventory scenarios: 3 transactional, 3 navigational, 3 informational
- [ ] Persona assignments for all 36 scenarios (5 of 7 personas used)
- [ ] Expected behavior with concrete model/method references
- [ ] Edge-case scenarios included:
  - BM-SAL-T-003: permission-denied (exec_readonly cancels quotation)
  - BM-SAL-I-003: ambiguity-handling (copilot must define conversion formula)
  - BM-ACC-I-003: grounded evidence (P&L with explicit account group citations)

### Verification
- [ ] All 36 scenarios validate against schema (12 files, 0 errors)
- [ ] Every scenario has a persona assignment
- [ ] Every transactional scenario has confirmation + audit + permission gates
- [ ] Every informational scenario has a grounding gate
- [ ] No scenario references Enterprise modules

**GATE: Epic 2 — Scenario Catalog v1**

---

## Epic 3: Runner + Evidence Contract

### Build
- [x] `scripts/benchmark/run_benchmark.py` — main entry point (wired to runner/evaluator/reporter/evidence)
- [x] `scripts/benchmark/runner.py` — scenario executor (JSON-RPC to Odoo, per-persona auth, copilot chat endpoint)
- [x] `scripts/benchmark/evidence.py` — evidence capture (envelopes, scores, report, summary to `docs/evidence/`)
- [x] `scripts/benchmark/seed_personas.py` — seed 6 benchmark users + admin with correct group memberships
- [ ] Demo data seed script for benchmark records (CRM, Sales, Accounting, Inventory)

### Verification
- [x] All modules compile cleanly (`runner`, `evidence`, `evaluator`, `reporter`, `comparator`, `seed_personas`)
- [x] Runner dry-run lists all 36 scenarios
- [ ] Runner connects to Odoo in devcontainer (requires running Odoo instance)
- [ ] Evidence envelopes written to `docs/evidence/` (requires live run)

**GATE: Epic 3 — Runner framework built. Live execution pending Odoo instance.**

---

## Epic 4: Scoring

### Build
- [x] `scripts/benchmark/evaluator.py` — hard gate + soft score logic
- [x] Configurable weights via `benchmark.config.yaml` (per capability class)
- [x] Domain aggregation logic (`compute_domain_scores`)
- [x] Class aggregation logic (per-class breakdown within domains)
- [x] Overall score computation with certification threshold (`compute_overall_scores`)
- [x] Hard gate aggregation (`evaluate_hard_gates` — per-gate pass counts and rates)

### Verification
- [x] Hard gates produce binary pass/fail per scenario
- [x] Soft scores compute weighted sum per capability class
- [x] Domain/class/overall scores computed deterministically
- [x] Certification check against configurable threshold (default 70%)

**GATE: Epic 4 — PASSED. Scoring engine built with deterministic aggregation.**

---

## Epic 5: Governance Benchmark

### Build
- [x] Permission gate: verify user context via persona auth (runner authenticates per scenario)
- [x] Confirmation gate: detect confirmation signals in copilot response
- [x] Audit trace gate: check for action trace data in response
- [x] Grounding gate: detect source citation signals in informational responses
- [x] Governance-specific report section (hard gate summary table in reporter)

### Verification
- [ ] Permission gate fails when user lacks access (requires live run with exec_readonly persona)
- [ ] Confirmation gate fails when write executes without confirmation (requires live copilot)
- [ ] Audit gate fails when trace is missing required fields (requires live copilot)
- [ ] Grounding gate fails when citation is absent (requires live copilot)
- [x] Governance report renders hard gate summary table

**GATE: Epic 5 — Gates implemented. Live verification pending Odoo instance.**

---

## Epic 6: Reporting

### Build
- [x] `scripts/benchmark/reporter.py` — summary report generator
- [x] JSON output: `envelopes.json`, `scores.json`, `summary.json`
- [x] Markdown output: `report.md` with summary, domain scores, hard gates, scenario table
- [x] Release tagging (benchmark version + odoo version + copilot version + timestamp)
- [x] Per-domain table with per-class scores (transactional / navigational / informational)
- [x] Comparison report generator (`generate_comparison_report`)

### Verification
- [x] JSON evidence artifacts have correct schema
- [x] Markdown report includes all required sections
- [x] Release tag included in all output artifacts
- [x] Report covers all executed scenarios

**GATE: Epic 6 — PASSED. Reporting engine built with JSON + Markdown output.**

---

## Epic 7: Extended Benchmark

### Build
- [x] `scripts/benchmark/comparator.py` — cross-release comparison CLI
- [ ] Expand scenarios to Purchase, Project/Helpdesk, Settings/Admin domains
- [ ] Expand scenarios to Knowledge/SOP, Documents domains
- [ ] Regression detection logic (flag scenarios that passed before but fail now)
- [ ] CI integration (optional GitHub Actions workflow)

### Verification
- [ ] Comparison report shows deltas between two tagged runs
- [ ] Regressions are flagged explicitly
- [ ] All 9 domains have scenarios
- [ ] Full benchmark run completes end-to-end with evidence + report

**GATE: Epic 7 — Comparator built. Extended scenarios and CI pending.**

---

## Exit Criteria (Overall)

The benchmark framework is complete when:

- [ ] Scenario registry covers all 9 domains × 3 capability classes
- [ ] Runner executes scenarios and captures evidence
- [ ] Scoring produces deterministic results with configurable weights
- [ ] Governance checks enforced as hard gates with evidence
- [ ] Reporting generates per-domain and per-class summaries
- [ ] Cross-release comparison functional
- [ ] At least one full benchmark run completed with evidence committed
