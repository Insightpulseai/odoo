# Parallel Workflow Design — Examples

## Example 1: Multi-Resource Security Check (Sectioning)

```
Parallel branches: 5
Branch 1: KeyVault inventory → security posture → findings
Branch 2: Container Apps → network exposure → findings
Branch 3: PostgreSQL → access audit → findings
Branch 4: Managed identities → orphan check → findings
Branch 5: Front Door → WAF rules → findings

Aggregation: Merge all findings into single security report, deduplicate
Failure policy: Best-effort (report which branches completed)
Concurrency limit: 5
```

## Example 2: Code Review (Voting)

```
Parallel branches: 3
Branch 1: Review PR for security issues → findings
Branch 2: Review PR for performance issues → findings
Branch 3: Review PR for maintainability issues → findings

Aggregation: Union of all findings, flag conflicts
Failure policy: Best-effort (partial review > no review)
Concurrency limit: 3
```
