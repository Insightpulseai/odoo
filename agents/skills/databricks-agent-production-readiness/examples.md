# Examples — databricks-agent-production-readiness

## Example 1: Sales copilot agent (PASS)

**Input**: Agent built on Databricks Agent Framework. Three tools registered: search_orders, get_customer_info, create_quote. MLflow tracing enabled for all invocations. Eval suite covers 50 test cases with accuracy threshold 0.92 and latency P95 < 5s. Content filtering enabled. Deployed on Databricks Apps with A/B rollout. User feedback (thumbs up/down) captured and stored in Delta table. Dev/staging/prod workspaces.

**Output**:
- Readiness: PRODUCTION-READY
- All dimensions PASS
- Eval coverage: 50 test cases, 3 critical paths covered
- Trust/safety: Content filtering active, tool boundaries scoped, escalation to human available
- No blocking gaps

## Example 2: Data analysis agent without evals (CONDITIONALLY-READY)

**Input**: Agent using Agent Framework with SQL generation tool. MLflow tracing enabled. No formal eval suite — tested manually with 5 queries. Deployed on Databricks Apps. No content filtering. No user feedback mechanism. Single workspace.

**Output**:
- Readiness: CONDITIONALLY-READY
- Blocking gaps:
  - No formal eval suite — must create evaluation dataset with measurable thresholds
  - No content filtering — must add safety guardrails for SQL injection prevention
  - No user feedback loop — must implement feedback capture
- Advisory gaps:
  - Manual testing insufficient — automate eval runs in CI
  - Single workspace — recommend environment separation
- Remediation: Create eval dataset (minimum 30 test cases), add SQL sanitization guardrails, implement feedback UI

## Example 3: Ad-hoc LLM wrapper (NOT-READY)

**Input**: Python notebook making direct OpenAI API calls. No tool registry. No eval suite. No tracing. Running as a scheduled notebook job. No safety guardrails.

**Output**:
- Readiness: NOT-READY
- Blocking gaps:
  - Not using Agent Framework (ad-hoc LLM calls)
  - No tool registry or scope boundaries
  - No evaluation suite
  - No monitoring/tracing
  - Notebook execution — not deployed as Databricks App
  - No safety guardrails
- Remediation: Restructure using Agent Framework template. Register tools with scoped permissions. Create eval suite. Enable MLflow tracing. Deploy on Databricks Apps. Add content filtering and escalation path.
