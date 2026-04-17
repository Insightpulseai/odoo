# Planner Agent Memory

The planner/router decides:
- domain
- task type
- risk level
- tool path
- fallback policy

## Rules
- Prefer deterministic or tool-driven paths where reliability matters
- Route high-risk finance/tax/approval tasks through stricter policy and validator paths
- Use retrieval primarily for explanation and grounding, not for authority
