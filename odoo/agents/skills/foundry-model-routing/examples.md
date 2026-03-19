# Examples — foundry-model-routing

## Example 1: Uniform workload — pinned model recommended

**Input**: Customer support chat agent. All requests are similar complexity (FAQ answers, order status). Latency SLA: p95 < 2s.

**Output**:
- Workload variability: LOW — requests are uniform (FAQ, order status)
- Recommendation: PINNED MODEL (GPT-4o-mini)
- Rationale: uniform workload does not benefit from routing; routing overhead would increase latency without cost savings since all requests would route to the same model anyway
- Fallback: N/A (pinned model has no routing dependency)
- Trade-off: simplicity, lower latency, predictable cost

## Example 2: Mixed workload — router recommended

**Input**: Internal copilot agent. Requests range from simple lookups (employee directory) to complex analysis (financial report generation). Cost budget: $1000/mo.

**Output**:
- Workload variability: HIGH — requests range from simple lookups to complex analysis
- Recommendation: MODEL ROUTER
- Rationale: routing simple lookups to GPT-4o-mini and complex analysis to GPT-4o saves ~40% cost vs pinning GPT-4o for all requests; routing overhead (50-100ms) is acceptable for internal tooling
- Fallback: GPT-4o pinned (higher cost but handles all request types)
- Trade-off: cost savings justify routing complexity; latency increase acceptable for internal use

## Example 3: Router rejected — latency-critical workload

**Input**: Real-time fraud detection agent. Latency SLA: p95 < 500ms. All requests are similar (transaction scoring).

**Output**:
- Workload variability: LOW — all requests are transaction scoring
- Recommendation: PINNED MODEL
- Rationale: latency SLA (500ms) leaves no room for routing overhead; uniform workload offers no routing benefit
- Router consideration: REJECTED — routing overhead (~50-100ms) consumes 10-20% of latency budget with no compensating benefit
- Fallback: N/A (pinned model)
