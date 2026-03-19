# Odoo Copilot Benchmark — Implementation Plan

## 1. Implementation Strategy

Build the benchmark framework in four delivery phases. Each phase ends with a verification gate. The framework is code-first — scenarios are YAML, the runner is Python, evidence is JSON.

The benchmark is **internal tooling**, not a product feature. It lives in the repo, runs in dev environments, and produces evidence artifacts. It does not ship to end users.

---

## 2. Architectural Shape

### 2.1 Scenario Registry

```
spec/odoo-copilot-benchmark/scenarios/
├── crm/
│   ├── transactional.yaml
│   ├── navigational.yaml
│   └── informational.yaml
├── sales/
│   ├── transactional.yaml
│   ├── navigational.yaml
│   └── informational.yaml
├── ...9 domains total
└── _schema.yaml          # JSON Schema for scenario validation
```

Each YAML file contains an array of scenarios following the schema from `constitution.md §6`.

### 2.2 Runner

```
scripts/benchmark/
├── run_benchmark.py       # Main entry point
├── runner.py              # Scenario executor
├── evaluator.py           # Hard gate + soft score logic
├── evidence.py            # Evidence capture and persistence
├── reporter.py            # Summary report generation
└── comparator.py          # Cross-release comparison
```

The runner connects to a running Odoo instance via JSON-RPC, executes scenarios in sequence, and captures evidence.

### 2.3 Evidence Model

Every scenario execution produces an evidence envelope:

```json
{
  "scenario_id": "BM-CRM-T-001",
  "timestamp": "2026-03-11T14:30:00+08:00",
  "odoo_version": "19.0",
  "copilot_version": "1.0.0",
  "prompt": "Create a new opportunity for ACME Corp worth $50,000",
  "action_trace": {
    "model": "crm.lead",
    "method": "create",
    "record_id": 42,
    "user_id": 7,
    "duration_ms": 1200
  },
  "hard_gates": {
    "capability": true,
    "correctness": true,
    "permission": true,
    "confirmation": true,
    "auditability": true
  },
  "soft_scores": {
    "completeness": 0.9,
    "clarity": 0.85,
    "latency": 0.95
  },
  "weighted_score": 0.88,
  "result": "PASS"
}
```

### 2.4 Scoring Model

1. **Hard gates**: All must pass for the scenario to pass. Any failure = FAIL.
2. **Soft scores**: Each dimension scored 0.0–1.0, weighted per configuration.
3. **Scenario score**: Hard gates pass → weighted soft score sum. Hard gates fail → 0.0.
4. **Domain score**: Average of scenario scores within the domain.
5. **Class score**: Average of scenario scores within the capability class.
6. **Overall score**: Weighted average across all domains and classes.

---

## 3. Delivery Phases

### Phase 1: Spec Foundation
- Define scenario YAML schema with JSON Schema validation
- Create registry directory structure for all 9 domains
- Seed 3 example scenarios (1 per capability class) in CRM domain
- Define evidence envelope format
- Define scoring weights configuration
- **GATE**: Schema validates, example scenarios parse, evidence format documented

### Phase 2: Scenario Catalog v1
- Write scenarios for 4 priority domains: CRM, Sales, Accounting, Inventory
- Minimum 3 scenarios per domain × capability class = 36 scenarios
- Include persona assignments
- Include expected_behavior with concrete Odoo model/method references
- **GATE**: 36+ scenarios validate against schema

### Phase 3: Runner + Scoring
- Implement scenario runner (Python, JSON-RPC to Odoo)
- Implement hard gate evaluator
- Implement soft score computation
- Implement evidence capture and persistence
- Implement summary report generator (JSON + Markdown)
- Implement release tagging
- **GATE**: Full benchmark run completes against devcontainer Odoo with evidence

### Phase 4: Governance + Extended
- Implement governance-specific gates (permission, confirmation, audit, grounding)
- Expand scenario catalog to all 9 domains
- Implement cross-release comparison
- Add regression detection
- **GATE**: Governance report generated, comparison between two tagged runs works

---

## 4. Benchmark Domains

| Domain | Odoo Apps | Priority | Phase |
|--------|-----------|----------|-------|
| CRM | `crm` | P0 | 2 |
| Sales | `sale`, `sale_management` | P0 | 2 |
| Purchase | `purchase` | P1 | 4 |
| Accounting | `account` | P0 | 2 |
| Inventory | `stock` | P0 | 2 |
| Project/Helpdesk | `project`, `ipai_helpdesk` | P1 | 4 |
| Settings/Admin | `base`, `base_setup` | P1 | 4 |
| Knowledge/SOP | `ipai_ai_rag` | P2 | 4 |
| Documents | `ipai_documents_ai` | P2 | 4 |

---

## 5. Benchmark Personas

| Persona ID | Role | Access Level | Primary Domains |
|------------|------|-------------|----------------|
| `sales_rep` | Sales Representative | Sales / User | CRM, Sales |
| `sales_mgr` | Sales Manager | Sales / Manager | CRM, Sales |
| `accountant` | Accountant | Accounting / Accountant | Accounting |
| `inv_operator` | Inventory Operator | Inventory / User | Inventory |
| `project_mgr` | Project Manager | Project / Manager | Project/Helpdesk |
| `admin` | System Administrator | Administration / Settings | Settings/Admin |
| `exec_readonly` | Read-Only Executive | Internal User (no write groups) | All (read only) |

Each persona maps to an Odoo user with specific group memberships. Benchmark scenarios specify which persona runs them, and the runner authenticates as that user.

---

## 6. Success Approach

### What "done" looks like per phase:

| Phase | Artifact | Verification |
|-------|----------|-------------|
| 1 | Schema + 3 example scenarios | `python -m jsonschema` validates |
| 2 | 36+ scenario YAML files | Schema validation passes for all |
| 3 | Runner + evidence artifacts | Full run completes, evidence in `docs/evidence/` |
| 4 | Governance report + comparison | Two tagged runs compared, governance gates enforced |

---

## 7. Reporting Outputs

### Per-Run Report

```
Odoo Copilot Benchmark — Run 2026-03-11T14:30:00
Odoo: 19.0 | Copilot: 1.0.0

Domain        | Trans | Nav   | Info  | Overall
─────────────┼───────┼───────┼───────┼────────
CRM           | 85%   | 90%   | 78%   | 84%
Sales         | 80%   | 88%   | 72%   | 80%
Accounting    | 70%   | 85%   | 65%   | 73%
Inventory     | 75%   | 82%   | 68%   | 75%
─────────────┼───────┼───────┼───────┼────────
Overall       | 78%   | 86%   | 71%   | 78%

Hard Gate Summary:
  Permission:    42/42 PASS
  Confirmation:  28/28 PASS (transactional only)
  Auditability:  42/42 PASS
  Grounding:     14/14 PASS (informational only)
```

### Comparison Report

```
Δ Release: v1.0.0 → v1.1.0

Domain        | Δ Trans | Δ Nav  | Δ Info | Δ Overall
─────────────┼─────────┼────────┼────────┼──────────
CRM           | +5%     | +2%    | +8%    | +5%
Sales         | +3%     | 0%     | +4%    | +2%
Accounting    | +10%    | +3%    | +12%   | +8%
Inventory     | 0%      | +1%    | +5%    | +2%

Regressions: 0
New passes:  7 scenarios
```

---

## 8. Design Constraints

- **Odoo 19 / CE only**: No Enterprise module dependencies in scenarios or runner
- **OCA-first**: If an OCA module provides a capability being benchmarked, use it
- **ipai_*-bridge-thin**: Custom modules are thin adapters, not orchestration engines
- **Devcontainer-compatible**: Runner must work inside the standard devcontainer
- **No external services required**: Benchmark works with local Odoo + local DB (RAG scenarios may use mock data)

---

## 9. Open Implementation Choices

| Decision | Options | Recommendation | Status |
|----------|---------|---------------|--------|
| Runner language | Python / Shell | Python (JSON-RPC native) | Decided |
| Evidence format | JSON / YAML | JSON (machine-first) | Decided |
| Scenario format | YAML / JSON | YAML (human-readable) | Decided |
| Report format | JSON + Markdown | Both (machine + human) | Decided |
| Scoring weights | Fixed / Configurable | Configurable via `benchmark.config.yaml` | Open |
| CI integration | GitHub Actions / Manual | Manual first, CI in Phase 4 | Open |
| RAG scenario data | Real docs / Mock data | Mock data for reproducibility | Open |
