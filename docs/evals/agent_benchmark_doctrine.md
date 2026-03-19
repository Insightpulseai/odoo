# Agent Benchmark Doctrine

> Governance framework for evaluating AI agents and copilots across the InsightPulse AI platform.
> Grounded in peer-reviewed benchmarks, not vendor demos.
> Extends `CLAUDE.md` operating contract. Never contradicts it.

---

## Core Doctrine

### Principle 1: Evaluate outcomes, not conversation quality

Benchmark business-task success, not eloquence. A copilot that produces a
correct journal entry with awkward phrasing outranks one that writes beautiful
prose but posts to the wrong account. Fluency is a secondary signal; task
completion, correctness, and groundedness are primary.

### Principle 2: Prefer the simplest viable architecture first

One agent with clear tools before multi-agent. Orchestration overhead,
routing errors, and observability gaps multiply with every additional agent
hop. Start with a single agent that has well-defined tool access. Only add
agent layers when a single agent demonstrably fails the benchmark.

### Principle 3: Benchmarks must reflect real operating conditions

Not synthetic toy prompts. Use production-representative data, realistic
role permissions, actual ERP state, and genuine user intent patterns.
Benchmarks run against sanitized copies of real databases, not hand-crafted
five-row tables.

### Principle 4: Use multiple judges

Deterministic + model-based + human expert. No single judge is sufficient.
Deterministic checks catch structural failures (schema violations, missing
fields, unauthorized mutations). Model-based judges assess groundedness and
clarity. Human experts verify finance correctness, ERP practicality, and
trustworthiness.

### Principle 5: Production telemetry is part of evaluation

Traces, tool calls, retries, costs, latency. A benchmark that ignores
operational cost, retry storms, or P95 latency is incomplete. Every
benchmark run must emit structured traces that can be audited after the fact.

### Principle 6: Safety and access control override benchmark wins

Unauthorized actions block claims. If an agent achieves 100% task success
but bypasses role-based access controls, creates records it should not have
access to, or mutates production data without authorization, the benchmark
result is invalidated. Safety is a hard gate, not a weighted dimension.

---

## Research Mapping

These peer-reviewed benchmarks ground our expectations. Agent capabilities
are far below vendor marketing claims.

### WebArena

**Finding**: Long-horizon web tasks are much harder than demos imply.

- Agent success rate: 14.41%
- Human success rate: 78.24%
- Gap: ~5.4x

**Implication**: Multi-step ERP workflows (create PO, receive goods, match
invoice, post payment) will have compounding failure rates. Each step is a
potential failure point. Do not assume linear difficulty scaling.

**Eval rules derived**:
- Benchmark multi-step workflows end-to-end, not individual steps
- Measure completion rate at each step to identify failure cascades
- Report both partial and full completion rates

### GAIA

**Finding**: General tool-using assistants are far from human reliability.

- GPT-4 (with tools) success rate: 15%
- Human success rate: 92%
- Gap: ~6.1x

**Implication**: Tool-using agents fail on tasks humans find straightforward.
Do not assume that providing tools (search, calculator, API access) closes
the gap. Tool selection, parameter construction, and result interpretation
are each failure-prone steps.

**Eval rules derived**:
- Test tool selection accuracy separately from task completion
- Measure tool call correctness (right tool, right parameters, right interpretation)
- Include tasks that require choosing NOT to use a tool

### tau-bench

**Finding**: User interaction and policy-following are first-class eval targets.

- Even strong agents score under 50% on policy-compliant interaction tasks

**Implication**: Copilots that interact with users (clarifying questions,
confirmations, handoffs) must be evaluated on whether they follow
organizational policy, not just whether they complete the task. A copilot
that completes an expense report but skips the approval workflow is a
compliance failure.

**Eval rules derived**:
- Include policy-compliance as a required dimension, not optional
- Test multi-turn interactions where the agent must follow branching policies
- Measure whether the agent correctly identifies when to escalate to a human

### TheAgentCompany

**Finding**: Digital worker claims need workplace proof.

- Autonomous completion: 30.3%
- Partial completion (with hints): 39.3%
- Remaining: ~30% failure even with assistance

**Implication**: Claims of "autonomous digital workers" must be backed by
workplace-realistic benchmarks, not cherry-picked demos. Most agents need
significant human guidance to complete realistic workplace tasks.

**Eval rules derived**:
- Report autonomous vs. assisted completion separately
- Measure human intervention rate as a primary metric
- Do not count hint-assisted completions as autonomous success

---

## Required Dimensions

All eight dimensions are required for every agent benchmark. Omitting any
dimension invalidates the benchmark.

| # | Dimension | Description | Measurement |
|---|-----------|-------------|-------------|
| 1 | `task_success` | Did the agent complete the requested business task? | Binary per task, aggregated as rate |
| 2 | `correctness` | Is the output factually and structurally correct? | Expert review + deterministic checks |
| 3 | `groundedness` | Is every claim supported by retrieved/provided context? | Model judge + human spot-check |
| 4 | `policy_compliance` | Did the agent follow organizational rules and access controls? | Deterministic policy checks + audit log review |
| 5 | `latency` | Time from request to completed action | P50, P95, P99 in seconds |
| 6 | `stability` | Does the agent produce consistent results across runs? | Variance across repeated runs |
| 7 | `human_intervention_rate` | How often did a human need to correct or guide the agent? | Count of interventions / total tasks |
| 8 | `auditability` | Can every action be traced and explained after the fact? | Trace completeness check |

---

## Judge Framework

### A) Deterministic Judge (Required)

Automated checks that produce binary pass/fail results. No model inference
involved. These are hard gates — any failure blocks a passing score.

Checks include:
- Schema validation (output matches expected structure)
- Required fields present (no null where required)
- No unauthorized mutations (agent did not write to tables/records outside its scope)
- Data type correctness (amounts are numbers, dates are dates)
- Referential integrity (foreign keys resolve)
- Idempotency (re-running does not create duplicates)
- Permission boundary (agent operated within its declared role)

### B) Model-Based Judge (Required)

An LLM evaluates qualitative aspects of the agent's output. The judge model
must be different from the agent model to avoid self-evaluation bias.

Evaluates:
- **Groundedness**: Every factual claim traces to a source document or database record
- **Clarity**: The output is understandable by the target user persona
- **Usefulness**: The output advances the user's goal
- **Completeness**: No critical information is missing
- **Conciseness**: No unnecessary verbosity or irrelevant information

Scoring: 1-5 Likert scale per dimension, with rubric definitions for each level.

### C) Human Expert Judge (Required)

Domain experts evaluate a stratified sample of agent outputs. Required for
any benchmark that will be used to make deployment decisions.

Evaluates:
- **Finance correctness**: Account codes, tax rates, journal entry structure, regulatory compliance
- **ERP practicality**: Does the action make sense in the context of real ERP operations?
- **Trustworthiness**: Would a finance professional trust this output without re-checking?
- **Edge case handling**: How does the agent behave with ambiguous or incomplete inputs?
- **Failure mode quality**: When the agent fails, does it fail safely and transparently?

Minimum sample: 20% of benchmark cases, stratified by difficulty tier.

---

## Repeated-Run Doctrine

Single-run benchmarks are not acceptable. Agent behavior varies across runs
due to model sampling, tool latency, and environmental state.

### Requirements

| Task Type | Minimum Runs | Preferred Runs |
|-----------|-------------|----------------|
| Bounded (deterministic input, clear output) | 5 | 5 |
| Interactive (multi-turn, user simulation) | 5 | 8 |

### Required Outputs

For every benchmark, report all of the following:

- **pass@1**: Success rate on first attempt
- **pass@n**: Success rate across all n runs (at least one success)
- **variance**: Standard deviation of scores across runs
- **critical_failure_count**: Number of runs with safety violations, data corruption, or unauthorized actions
- **mean_score**: Average weighted score across all runs
- **worst_run_score**: Score of the lowest-performing run (cannot be hidden)

### Rules

- Never report only the best run
- Never discard runs that "didn't count" unless there was a genuine infrastructure failure (documented with evidence)
- If variance exceeds 0.15 (on a 0-1 scale), the agent is unstable and must be flagged

---

## Release Gates

### Production-Ready Gate

All six conditions must be met. Any failure blocks deployment.

| # | Condition | Description |
|---|-----------|-------------|
| 1 | `benchmark_threshold_met` | Weighted score >= default threshold (0.80) |
| 2 | `no_critical_safety_failures` | Zero safety violations across all benchmark runs |
| 3 | `traces_available` | Every agent action has a structured trace in the telemetry system |
| 4 | `monitoring_enabled` | Production monitoring dashboards and alerts are configured |
| 5 | `rollback_path` | A tested rollback procedure exists and has been verified |
| 6 | `permissions_reviewed` | Agent's tool access and role permissions have been reviewed by a human |

### Surpass-Benchmark Gate

When claiming one agent/copilot is better than another (e.g., IPAI Copilot
vs. SAP Joule), all five conditions must be met:

| # | Condition | Description |
|---|-----------|-------------|
| 1 | `higher_weighted_score` | Candidate's weighted score exceeds incumbent's weighted score |
| 2 | `equal_or_better_success` | Candidate's task_success >= incumbent's task_success |
| 3 | `equal_or_better_groundedness` | Candidate's groundedness >= incumbent's groundedness |
| 4 | `no_worse_safety` | Candidate has zero additional safety failures vs. incumbent |
| 5 | `evidence_pack_committed` | Full evidence pack is committed to `docs/evals/evidence/` |

---

## Stack Profiles

Each stack in the platform has a tailored set of priority metrics. The
universal dimensions (above) always apply; these profiles add stack-specific
emphasis.

### Odoo (ERP)

| Priority | Metric | Why |
|----------|--------|-----|
| 1 | `task_completion` | Did the copilot complete the ERP transaction? |
| 2 | `wrong_action_rate` | Did it post to the wrong account, wrong partner, wrong period? |
| 3 | `role_access` | Did it respect the user's Odoo role and record rules? |
| 4 | `groundedness` | Are referenced documents, amounts, and dates traceable? |
| 5 | `human_correction` | How often did a user need to fix the copilot's output? |

### Foundry (Azure AI Foundry)

| Priority | Metric | Why |
|----------|--------|-----|
| 1 | `run_success` | Did the Foundry pipeline/prompt flow complete without error? |
| 2 | `tool_correctness` | Did the agent call the right tools with correct parameters? |
| 3 | `retrieval_relevance` | Did RAG retrieve the right documents? |
| 4 | `trace_completeness` | Are all steps visible in Application Insights? |
| 5 | `latency` | Is the response time acceptable for the use case? |

### Power BI (Reporting)

| Priority | Metric | Why |
|----------|--------|-----|
| 1 | `factual_accuracy` | Are the numbers in the report correct? |
| 2 | `metric_correctness` | Are calculated metrics (ratios, growth rates) computed correctly? |
| 3 | `source_groundedness` | Can every number be traced to a source table/query? |

### Teams / M365 (Collaboration)

| Priority | Metric | Why |
|----------|--------|-----|
| 1 | `source_support` | Is every response backed by a retrievable source? |
| 2 | `actionability` | Can the user act on the response without further research? |
| 3 | `permission_correctness` | Did the copilot respect M365 permissions and DLP policies? |
| 4 | `handoff_quality` | When escalating to a human, is the context complete and accurate? |

---

## Evidence Pack

Every benchmark produces the following artifacts. All are committed to the
repository under `docs/evals/evidence/<YYYYMMDD-HHMM>/<benchmark_name>/`.

| # | File | Description |
|---|------|-------------|
| 1 | `prompts.jsonl` | All prompts sent to the agent, one JSON object per line |
| 2 | `cases.yaml` | Test case definitions with expected outcomes |
| 3 | `outputs/` | Directory of agent outputs, one file per case per run |
| 4 | `judge_scores.json` | Scores from all three judge types |
| 5 | `human_review.csv` | Human expert review results |
| 6 | `failure_log.md` | Detailed analysis of every failed case |
| 7 | `benchmark_summary.md` | Aggregated results, charts, analysis |
| 8 | `final_scorecard.md` | One-page scorecard for decision-makers |

---

## Default Thresholds

These thresholds apply unless a stack profile specifies stricter values.

| Metric | Threshold | Direction |
|--------|-----------|-----------|
| `weighted_score` | >= 0.80 | Higher is better |
| `task_success` | >= 0.85 | Higher is better |
| `groundedness` | >= 0.90 | Higher is better |
| `critical_safety_failures` | = 0 | Must be zero |
| `run_success` | >= 0.95 | Higher is better |
| `hallucination_rate` | <= 0.05 | Lower is better |

---

## Anti-Patterns

These are explicitly prohibited in any benchmark conducted under this doctrine.

### 1. Best-Case Benchmarking

**Prohibited**: Running 20 benchmark iterations and reporting only the best 5.

**Required**: Report all runs. The worst run is as important as the best run.
If you need to exclude a run, document the infrastructure failure with evidence.

### 2. Hiding Failed Runs

**Prohibited**: Omitting runs where the agent failed, crashed, or produced
incorrect output.

**Required**: Every run appears in the evidence pack. Failed runs get detailed
analysis in `failure_log.md`.

### 3. Using Demos as Proof

**Prohibited**: Treating a curated demo (hand-picked inputs, controlled
environment, cherry-picked outputs) as benchmark evidence.

**Required**: Benchmarks use randomized or stratified test cases from
production-representative data. No hand-picking inputs to make the agent
look good.

### 4. Vendor-Native Trivia Comparison

**Prohibited**: Comparing agents on tasks trivially easy for one vendor's
platform (e.g., "navigate to SAP transaction MIRO" for SAP Joule vs. a
non-SAP agent).

**Required**: Compare on business outcomes that are platform-agnostic
(e.g., "process this vendor invoice and post the correct journal entry").

### 5. Claiming Autonomy from Partial Completion

**Prohibited**: Reporting 39.3% hint-assisted completion as "autonomous"
capability.

**Required**: Report autonomous completion and assisted completion as
separate metrics. Only autonomous completion counts toward autonomy claims.

### 6. Collapsing "Exists in UI" into "Works End-to-End"

**Prohibited**: Claiming a feature "works" because a button exists in the
UI, without verifying the end-to-end flow produces correct results.

**Required**: Every claimed capability must be verified with an end-to-end
test case that checks the final output, not just the UI surface.

---

*Last updated: 2026-03-18*
