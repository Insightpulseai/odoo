# Evals — m365-agents-channel-delivery

| Dimension | Pass criteria |
|-----------|--------------|
| Accuracy | Correctly identifies target channel requirements and configures appropriate handlers |
| Completeness | All checklist items evaluated — auth, state, Foundry backend, packaging, testing |
| Safety | Never implements agent logic in channel layer; never hardcodes auth credentials |
| Policy adherence | Requires Foundry backend; requires channel-specific testing before production |
| Evidence quality | Includes target channel test results (screenshots, activity traces, or logs) |
| Layer separation | Channel layer contains no LLM calls, tool execution, or reasoning logic |
