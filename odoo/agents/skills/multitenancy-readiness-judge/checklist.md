# Checklist: Multitenancy Readiness Judge

## SLO/SLA Verification

- [ ] SLOs defined for every tenant tier (free, standard, enterprise)
- [ ] SLOs are measurable with current monitoring infrastructure
- [ ] SLO burn rate alerting configured and tested
- [ ] SLA commitments aligned with SLO targets (with error budget)
- [ ] Evidence: SLO dashboard shows current compliance

## Isolation Verification

- [ ] Cross-tenant data access tests passing (all database isolation models)
- [ ] Cross-tenant compute access tests passing
- [ ] Cross-tenant network access tests passing
- [ ] Cross-tenant key/secret access tests passing
- [ ] Tests run automatically in CI/CD pipeline
- [ ] Evidence: Test results from most recent run

## Scale Verification

- [ ] Multi-tenant load test executed with realistic tenant distribution
- [ ] Load test validates SLO compliance under expected peak load
- [ ] Load test includes noisy neighbor simulation
- [ ] Results documented with per-tenant performance metrics
- [ ] Evidence: Load test report with per-tenant breakdown

## Chaos Verification

- [ ] Failure injection tests executed (compute failure, DB failure, network partition)
- [ ] Blast radius contained to affected tenant(s)
- [ ] Graceful degradation verified (not cascading failures)
- [ ] Recovery time meets SLO targets
- [ ] Evidence: Chaos test report with blast radius analysis

## Operational Verification

- [ ] Control plane and data plane clearly separated in architecture
- [ ] Deployment strategy is tenant-aware (ring-based or equivalent)
- [ ] Rollback procedure tested within the last 30 days
- [ ] Monitoring is tenant-dimensioned (metrics, logs, traces)
- [ ] Incident management includes tenant context
- [ ] Evidence: Runbook and most recent rollback test
