# Copilot Chat Cookbook — Insightpulseai/odoo

> **Source**: <https://docs.github.com/en/copilot/tutorials/copilot-chat-cookbook>
> Repo-specific prompt library adapted from the GitHub Copilot Chat Cookbook.
> All prompts enforce: PR-only · minimal diff · evidence-required · SSOT-first.
>
> **Ready-to-paste prompts**: `prompts/copilot/` (one file per job).

---

## Governance constraints for all prompts

Before using any prompt, confirm:

- You are on a feature branch (never `main`)
- No secret values are in scope (reference by name from `ssot/secrets/registry.yaml`)
- All outputs reference SSOT paths where applicable (`ssot/**`, `spec/**`, `docs/contracts/**`)
- Evidence goes to `web/docs/evidence/<YYYYMMDD-HHMM+0800>/<scope>/logs/`
- Output format: `[CONTEXT]` / `[CHANGES]` / `[EVIDENCE]` / `[DIFF SUMMARY]` / `[ROLLBACK]` / `[NEXT]`

---

## 1. Generating Unit Tests

**When to use**: A model, utility function, or Edge Function exists with no test coverage,
or a new method was added without accompanying tests.

**Inputs to provide**:
- Path to the file under test (e.g. `addons/ipai/ipai_expense_automation/models/expense_receipt.py`)
- Any existing test file in the same module (`tests/test_expense_receipt.py`)
- The failing/missing test scenario described in 1–2 lines

**Prompt (copy/paste)**:
> See `prompts/copilot/unit_tests.prompt.md`

**Expected outputs**:
- New or updated test file in `addons/ipai/<module>/tests/test_<model>.py`
- Tests use `odoo.tests.common.TransactionCase` (not mocks)
- `pre-commit run --all-files` passes
- Evidence log: `web/docs/evidence/<stamp>/unit-tests/logs/test_run.txt`

**Failure modes**:

| Symptom | Response |
|---------|----------|
| Copilot creates `unittest.mock` instead of Odoo TransactionCase | Reject. Re-prompt: "Use `odoo.tests.common.TransactionCase`, no mocks." |
| Test imports Enterprise module | Reject. PR will fail CE-only gate. |
| Copilot modifies source file instead of test file | Reject. Scope is test file only. |
| Copilot suggests running `odoo-bin` interactively | Redirect to CI: `odoo-bin --test-enable --stop-after-init` |

---

## 2. Debugging Invalid JSON

**When to use**: A workflow JSON file (n8n), a config file, a Supabase migration JSONB column,
or an API response fails JSON parsing and the error message is unclear.

**Inputs to provide**:
- The raw JSON string or file path
- The error message (e.g. `SyntaxError: Unexpected token '}' at position 1432`)
- Context: where the JSON originated (n8n export, Supabase seed, API response)

**Prompt (copy/paste)**:
> See `prompts/copilot/invalid_json.prompt.md`

**Expected outputs**:
- The corrected JSON file committed (if a tracked file)
- If a runtime response: a minimal patch to the code that parses it (add error guard)
- `python -c "import json; json.load(open('<file>'))"` passes without exception
- Evidence log: `web/docs/evidence/<stamp>/json-debug/logs/validate.txt`

**Failure modes**:

| Symptom | Response |
|---------|----------|
| Copilot silently strips keys to make JSON valid | Reject. Ask for explanation of each removal. |
| Copilot suggests editing generated files directly | Reject. Identify the upstream source instead. |
| Copilot proposes `eval()` or `ast.literal_eval()` | Reject. Use `json.loads()` only. |

---

## 3. Handling API Rate Limits

**When to use**: A GitHub Actions workflow, n8n workflow, or Edge Function hits HTTP 429
or returns `X-RateLimit-Remaining: 0` and needs backoff/retry logic.

**Inputs to provide**:
- File path of the code hitting the rate limit
- The specific API endpoint and its documented rate limit (e.g. GitHub REST: 5,000/hr for PATs)
- Current retry behaviour (none / naive sleep / exponential)

**Prompt (copy/paste)**:
> See `prompts/copilot/api_rate_limits.prompt.md`

**Expected outputs**:
- Exponential backoff with jitter added to the function/step
- `X-RateLimit-Remaining` and `Retry-After` headers checked before retry
- No sleep longer than 60 s in CI context (add `--max-backoff 60` guard)
- Evidence log: `web/docs/evidence/<stamp>/rate-limits/logs/retry_test.txt`

**Failure modes**:

| Symptom | Response |
|---------|----------|
| Copilot adds `time.sleep(600)` | Reject. Cap at 60 s for CI. |
| Copilot proposes a new library not in `requirements.txt` | Require stdlib only (`time`, `math`), or add dep to requirements first. |
| Copilot uses `GITHUB_TOKEN` directly in output | Reject. Reference by env var name only. |

---

## 4. Diagnosing Test Failures

**When to use**: CI reports a test failure but the error log is cryptic, a test was passing
and now fails after an unrelated change, or a flaky test needs root-cause analysis.

**Inputs to provide**:
- CI run URL or pasted log excerpt (error + traceback, ≤50 lines)
- The test file and failing test method name
- The git diff of the last commit that broke it (`git diff HEAD~1 HEAD -- <file>`)

**Prompt (copy/paste)**:
> See `prompts/copilot/diagnose_tests.prompt.md`

**Expected outputs**:
- Root cause identified (not just "this line failed")
- Minimal fix: the smallest change that makes the test pass
- If flaky: a proposed `@unittest.skipIf` or fixture-level isolation, not test deletion
- Evidence log: `web/docs/evidence/<stamp>/diagnose-tests/logs/diagnosis.txt`

**Failure modes**:

| Symptom | Response |
|---------|----------|
| Copilot deletes the failing test | Reject. Tests are not deleted to make CI green. |
| Copilot adds `# noqa` / `# type: ignore` to silence errors | Reject unless the error is a known false-positive; require justification comment. |
| Copilot modifies unrelated files | Reject. Minimal diff only. |

---

## 5. Creating Templates

**When to use**: A new spec bundle, runbook, migration file, or PR description needs to follow
a standard structure and no existing template exists.

**Inputs to provide**:
- The template type (spec bundle, runbook, migration, PR body, SSOT YAML)
- An example of an existing file of the same type to use as reference
- The specific slug/name for the new instance

**Prompt (copy/paste)**:
> See `prompts/copilot/templates.prompt.md`

**Expected outputs**:
- New file created at the correct canonical path (checked against `docs/architecture/PLATFORM_REPO_TREE.md`)
- Frontmatter / schema matches the reference file
- No placeholder values left (`[TODO]`, `<fill_in>`)
- Evidence log: `web/docs/evidence/<stamp>/templates/logs/created.txt`

**Failure modes**:

| Symptom | Response |
|---------|----------|
| Copilot creates file at wrong path | Reject. Path must be in `PLATFORM_REPO_TREE.md`. |
| Template contains hardcoded secrets | Reject. Use `<from-vault>` or env var placeholders. |
| Copilot generates a `.md` tutorial instead of a template | Reject. Ask for executable template only. |

---

## 6. Creating Tables

**When to use**: A doc, SSOT YAML, or PR description needs a comparison table, matrix,
or structured reference that doesn't exist yet.

**Inputs to provide**:
- The data source (list of items, YAML file, CSV, or plain-text list)
- The target format (GitHub Markdown table, YAML mapping, CSV)
- The columns required and the sorting/grouping preference

**Prompt (copy/paste)**:
> See `prompts/copilot/tables.prompt.md`

**Expected outputs**:
- Rendered Markdown table embedded in the target doc, or standalone YAML/CSV file
- Columns are consistently formatted; no merged cells (Markdown doesn't support them)
- No data dropped silently (row count must match source)
- Evidence log: `web/docs/evidence/<stamp>/tables/logs/row_count.txt`

**Failure modes**:

| Symptom | Response |
|---------|----------|
| Copilot invents data not in the source | Reject. Demand source citation for each cell. |
| Table truncated with "..." | Reject. All rows must be present. |
| Copilot uses HTML tables instead of Markdown | Reject unless the doc is HTML. |

---

## 7. Creating Diagrams

**When to use**: An architecture, data flow, sequence, or entity-relationship needs visualisation
in a format that renders natively in GitHub (Mermaid) or can be committed as source.

**Inputs to provide**:
- The system to diagram (e.g. "n8n → Supabase Edge Function → ops.task_queue → Odoo")
- The diagram type required (flowchart, sequence, ER, class)
- Any existing diagram or doc that partially describes it

**Prompt (copy/paste)**:
> See `prompts/copilot/diagrams.prompt.md`

**Expected outputs**:
- Mermaid code block (````mermaid`) embedded in a `.md` file — renders on GitHub natively
- No external diagram service URLs (no Lucidchart, no draw.io XML in the diff)
- All nodes and edges match the described system — no invented components
- Evidence log: `web/docs/evidence/<stamp>/diagrams/logs/mermaid_lint.txt`

**Failure modes**:

| Symptom | Response |
|---------|----------|
| Copilot generates PlantUML instead of Mermaid | Redirect: "Use Mermaid — GitHub renders it natively." |
| Diagram includes components not in the repo | Reject. Stick to what's in SSOT. |
| Copilot generates a `.png` or base64 image | Reject. Source-only (Mermaid text). |

---

## See also

- [`prompts/copilot/`](../../../prompts/copilot/) — ready-to-paste prompt files
- [`.github/copilot-instructions.md`](../../../.github/copilot-instructions.md) — repo behavioural rules (auto-loaded)
- [`.github/agents/FixBot.agent.md`](../../../.github/agents/FixBot.agent.md) — multi-file fix agent
- [`.github/agents/Reviewer.agent.md`](../../../.github/agents/Reviewer.agent.md) — review-only agent
- [`prompts/fixbot_end_to_end.prompt.md`](../../../prompts/fixbot_end_to_end.prompt.md) — full fix workflow
- [GitHub Copilot Chat Cookbook](https://docs.github.com/en/copilot/tutorials/copilot-chat-cookbook) — upstream source
