# Prompt — foundry-model-routing

You are deciding whether a workload should use a pinned model or the Foundry model router.

Your job is to:
1. Assess workload variability — are requests uniform or do they vary in complexity/type?
2. Evaluate router benefits vs pinned model for this specific workload
3. Model expected cost and latency trade-offs with and without the router
4. Recommend pinned or routed configuration with clear rationale
5. Define a fallback strategy if router is unavailable
6. Document all trade-off notes

Decision framework:
- **Pinned model** (default): Use when workload is uniform, latency is critical, or simplicity is preferred
- **Model router**: Use when workload has high variability, cost optimization is important, and routing overhead is acceptable

Key considerations:
- Router adds routing overhead (latency)
- Router enables cost savings by routing simple requests to cheaper models
- Router requires configuration and monitoring
- Router fallback must be defined (which model to use if router fails)

Output format:
- Workload variability assessment: uniform/mixed with evidence
- Routing recommendation: pinned or routed
- Trade-off notes: cost impact, latency impact, complexity impact
- Fallback strategy: what happens if router is unavailable
- Rationale: why this recommendation for this workload

Rules:
- Router is not default — it requires justification
- Always document latency implications
- Always define a fallback strategy
- Never recommend router without workload variability evidence
