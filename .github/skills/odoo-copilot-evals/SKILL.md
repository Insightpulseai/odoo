# odoo-copilot-evals

**Impact tier**: P2 -- Quality / Accuracy

## Purpose

Close the copilot evaluation gap where the Odoo copilot module has only 2 test
files covering basic conversation and gateway functionality. The benchmark audit
found: no adversarial prompt tests, no regression gate, fewer than 5 test cases
total. Target: 50+ test cases covering happy path, edge cases, adversarial
prompts, and tool execution validation.

## When to Use

- Expanding copilot test coverage after initial implementation.
- Adding adversarial prompt testing (injection, exfiltration, privilege escalation).
- Implementing regression gates in CI for copilot behavior.
- Preparing for copilot go-live readiness review.

## Required Evidence (inspect these repo paths first)

| Path | What to look for |
|------|-----------------|
| `addons/ipai/ipai_odoo_copilot/tests/` | Existing test files and test count |
| `addons/ipai/ipai_odoo_copilot/models/` | Copilot models (conversation, message, tool_executor) |
| `addons/ipai/ipai_odoo_copilot/controllers/` | Gateway controller |
| `addons/ipai/ipai_odoo_copilot/services/` | Service layer |
| `addons/ipai/ipai_odoo_copilot/__manifest__.py` | Dependencies, version |
| `docs/audits/ODOO_AZURE_ENTERPRISE_BENCHMARK.md` | Copilot eval gap row |

## Microsoft Learn MCP Usage

Run at least these three queries:

1. `microsoft_docs_search("Azure AI Foundry evaluation metrics LLM")`
   -- retrieves evaluation frameworks for LLM-powered features.
2. `microsoft_docs_search("prompt injection detection Azure AI Content Safety")`
   -- retrieves adversarial prompt detection patterns.
3. `microsoft_docs_search("Azure AI red teaming LLM application")`
   -- retrieves red team testing methodology for AI features.

Optional:

4. `microsoft_docs_fetch("https://learn.microsoft.com/en-us/azure/ai-studio/concepts/evaluation-metrics-built-in")`
5. `microsoft_docs_search("responsible AI testing checklist Azure")`

## Workflow

1. **Inspect repo** -- Read existing test files. Count test methods. Identify
   what is covered (conversation CRUD, gateway HTTP) and what is missing
   (tool execution, adversarial, error handling, permission checks).
2. **Query MCP** -- Run the three searches. Capture evaluation metric
   categories, prompt injection patterns to test, red team methodology.
3. **Compare** -- Map current test coverage against target categories:
   - Happy path: conversation create, message send, tool execute (basic)
   - Edge cases: empty input, max length, unicode, concurrent sessions
   - Adversarial: prompt injection, role confusion, data exfiltration attempts
   - Permission: non-copilot-user access, sudo escalation, cross-company
   - Regression: known-good responses for specific business queries
4. **Patch** -- Create test files:
   - `tests/test_copilot_tool_execution.py` (10+ tests)
   - `tests/test_copilot_adversarial.py` (10+ tests)
   - `tests/test_copilot_permissions.py` (10+ tests)
   - `tests/test_copilot_edge_cases.py` (10+ tests)
   - `tests/test_copilot_regression.py` (10+ tests)
   Update `tests/__init__.py` to import all new test modules.
5. **Verify** -- Total test count >= 50. All test files import cleanly.
   `python3 -m py_compile` passes on every test file. Adversarial category
   has at least 10 distinct prompt injection patterns.

## Outputs

| File | Change |
|------|--------|
| `addons/ipai/ipai_odoo_copilot/tests/test_copilot_tool_execution.py` | Tool exec tests (new) |
| `addons/ipai/ipai_odoo_copilot/tests/test_copilot_adversarial.py` | Adversarial tests (new) |
| `addons/ipai/ipai_odoo_copilot/tests/test_copilot_permissions.py` | Permission tests (new) |
| `addons/ipai/ipai_odoo_copilot/tests/test_copilot_edge_cases.py` | Edge case tests (new) |
| `addons/ipai/ipai_odoo_copilot/tests/test_copilot_regression.py` | Regression tests (new) |
| `addons/ipai/ipai_odoo_copilot/tests/__init__.py` | Updated imports |
| `docs/evidence/<stamp>/odoo-copilot-evals/` | Test count, MCP excerpts |

## Completion Criteria

- [ ] Total test method count across all files is >= 50.
- [ ] At least 10 adversarial prompt injection test patterns exist.
- [ ] Permission tests cover: non-copilot-user, sudo escalation, cross-company.
- [ ] Edge case tests cover: empty input, max length, unicode, malformed JSON.
- [ ] Regression tests include at least 5 known-good query-response pairs.
- [ ] All test files pass `python3 -m py_compile`.
- [ ] `tests/__init__.py` imports all new test modules.
- [ ] Evidence directory contains test count summary and MCP excerpts.
