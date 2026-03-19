# azure-troubleshooting-ops

Diagnoses runtime issues — container restart loops, DNS resolution failures, Key Vault access denied, TLS errors, and network rule conflicts.

## When to use
- Incident reported (service down or degraded)
- Health check failure detected
- Deployment failure in CI/CD pipeline
- Alert rule triggered (5xx spike, restart loop, latency)

## Key rule
Never expose secrets in diagnostic output. Escalate if root cause is not identified after 3 structured
diagnostic checks. Never restart services or modify network rules as a diagnostic step without
confirming root cause first.

## Cross-references
- `docs/contracts/azure-resource-graph-contract.md`
- `ssot/runtime/resource-graph-query-catalog.yaml`
- `.claude/rules/infrastructure.md`
