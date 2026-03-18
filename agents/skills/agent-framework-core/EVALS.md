# Evals — agent-framework-core

| Dimension | Pass criteria |
|-----------|--------------|
| Accuracy | Correctly defines workflow graph structure with valid nodes, edges, and conditions |
| Completeness | All checklist items evaluated — telemetry, checkpointing, middleware, human-in-the-loop |
| Safety | Never conflates orchestration with channel delivery; never bypasses human-in-the-loop gates |
| Policy adherence | Requires telemetry on production workflows; requires checkpointing for long-running workflows |
| Evidence quality | Includes DevUI visualization or execution trace with span details |
| Layer separation | Orchestration logic contains no channel-specific code (Teams, web, M365 Copilot) |
