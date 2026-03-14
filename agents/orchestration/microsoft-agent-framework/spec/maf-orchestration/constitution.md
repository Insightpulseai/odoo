# Constitution: MAF Orchestration

## Non-Negotiable Rules
1. Foundry remains current production runtime until explicit graduation
2. MAF is evaluation/prototyping only until Phase 3 comparison is complete
3. No production traffic routes through MAF without explicit approval
4. All agents must respect public/authenticated mode boundaries
5. Execution agents must be tool-mediated only — no implicit mutations
6. Observability (OpenTelemetry) is mandatory for all orchestrated flows
7. Checkpointing is required for any workflow exceeding 30 seconds
8. Human-in-the-loop gates are required for write/mutation actions
