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
- [ ] `odoo/scripts/benchmark/run_benchmark.py` — main entry point
- [ ] `odoo/scripts/benchmark/runner.py` — scenario executor (JSON-RPC to Odoo)
- [ ] `odoo/scripts/benchmark/evidence.py` — evidence capture and persistence
- [ ] Demo data seed script for benchmark personas (7 users with correct groups)
- [ ] Demo data seed script for benchmark records (CRM, Sales, Accounting, Inventory)

### Verification
- [ ] Runner connects to Odoo in devcontainer
- [ ] Runner executes 3 CRM example scenarios
- [ ] Evidence envelopes written to `docs/evidence/`
- [ ] Runner handles scenario failures gracefully (logs, continues)

**GATE: Epic 3 — Runner executes scenarios, evidence persisted**

---

## Epic 4: Scoring

### Build
- [ ] `odoo/scripts/benchmark/evaluator.py` — hard gate + soft score logic
- [ ] Configurable weights via `benchmark.config.yaml`
- [ ] Domain aggregation logic
- [ ] Class aggregation logic
- [ ] Overall score computation

### Verification
- [ ] Hard gates produce binary pass/fail
- [ ] Soft scores compute weighted sum
- [ ] Domain/class/overall scores are deterministic
- [ ] Same inputs produce same scores across runs

**GATE: Epic 4 — Scoring deterministic, weights configurable**

---

## Epic 5: Governance Benchmark

### Build
- [ ] Permission gate: verify ORM access check before action
- [ ] Confirmation gate: verify user confirmation prompt before write/create/unlink
- [ ] Audit trace gate: verify trace logged with user_id, model, method, record_id, timestamp
- [ ] Grounding gate: verify source citation in informational responses
- [ ] Governance-specific report section

### Verification
- [ ] Permission gate fails when user lacks access
- [ ] Confirmation gate fails when write executes without confirmation
- [ ] Audit gate fails when trace is missing required fields
- [ ] Grounding gate fails when citation is absent
- [ ] Governance report renders all gate results

**GATE: Epic 5 — All governance gates implemented and tested**

---

## Epic 6: Reporting

### Build
- [ ] `odoo/scripts/benchmark/reporter.py` — summary report generator
- [ ] JSON output (machine-readable)
- [ ] Markdown output (human-readable)
- [ ] Release tagging (version + timestamp in results)
- [ ] Per-domain table with per-class scores

### Verification
- [ ] JSON report parses and contains all required fields
- [ ] Markdown report renders correctly
- [ ] Release tag is included in output
- [ ] Report covers all executed scenarios

**GATE: Epic 6 — Reports generated for full benchmark run**

---

## Epic 7: Extended Benchmark

### Build
- [ ] `odoo/scripts/benchmark/comparator.py` — cross-release comparison
- [ ] Expand scenarios to Purchase, Project/Helpdesk, Settings/Admin domains
- [ ] Expand scenarios to Knowledge/SOP, Documents domains
- [ ] Regression detection logic (flag scenarios that passed before but fail now)
- [ ] CI integration (optional GitHub Actions workflow)

### Verification
- [ ] Comparison report shows deltas between two tagged runs
- [ ] Regressions are flagged explicitly
- [ ] All 9 domains have scenarios
- [ ] Full benchmark run completes end-to-end with evidence + report

**GATE: Epic 7 — Full 9-domain benchmark with comparison and regression detection**

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
