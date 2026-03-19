# Examples — foundry-model-benchmark-judge

## Example 1: Complete selection — approved

**Input**: Model selection for customer support agent. All four dimensions covered. GPT-4o-mini recommended. Budget $500/mo. Safety: high.

**Output**:
- Verdict: APPROVE
- Dimension coverage: 4/4 (quality, safety, cost, throughput)
- Workload specificity: PASS — selection references "customer support chat, latency-sensitive, customer-facing"
- Safety assessment: PASS — GPT-4o-mini meets content safety threshold for customer-facing use
- Cost assessment: PASS — $150/mo estimated, within $500/mo budget
- Rejection review: GPT-4 Turbo rejected (latency SLA exceeded), o1-preview rejected (cost prohibitive) — both verifiable
- Findings: none
- Recommendations: none

## Example 2: Missing safety dimension — rejected

**Input**: Model selection for public-facing summarization agent. Three dimensions covered (quality, cost, throughput). Safety not evaluated.

**Output**:
- Verdict: REJECT
- Dimension coverage: 3/4 — MISSING: safety
- Workload specificity: PASS — references "public-facing summarization"
- Safety assessment: FAIL — safety dimension not evaluated (automatic reject for public-facing workload)
- Cost assessment: PASS — within budget
- Findings: safety dimension missing for a public-facing agent — this is a hard reject
- Recommendations: re-evaluate with safety dimension covering content safety, jailbreak resistance, and harmful content filtering

## Example 3: Generic "best model" — rejected

**Input**: Model selection recommends "GPT-4o is the best model for all agent workloads in the platform."

**Output**:
- Verdict: REJECT
- Dimension coverage: 1/4 — only quality discussed
- Workload specificity: FAIL — "best model for all workloads" is generic, not workload-specific
- Safety assessment: FAIL — not evaluated per workload
- Cost assessment: FAIL — not evaluated per workload
- Findings: selection uses "best model everywhere" pattern, which violates workload-specific selection policy
- Recommendations: re-evaluate per-workload with all four dimensions; each agent/workload must have its own selection rationale

## Example 4: Stale leaderboard data — conditional

**Input**: Model selection uses leaderboard data from 45 days ago. Selection is otherwise complete.

**Output**:
- Verdict: CONDITIONAL
- Dimension coverage: 4/4
- Workload specificity: PASS
- Safety assessment: PASS
- Cost assessment: PASS
- Findings: leaderboard data is 45 days old (threshold: 30 days) — new models or pricing changes may affect selection
- Recommendations: refresh leaderboard data and re-validate selection; if no material changes, approve
