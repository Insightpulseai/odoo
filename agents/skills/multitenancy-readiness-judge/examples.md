# Examples: Multitenancy Readiness Judge

## Example 1: Readiness Scorecard

| Area | Score (1-5) | Evidence | Status |
|------|------------|----------|--------|
| SLO/SLA | 4 | SLOs defined for all tiers, monitoring active, burn rate alerts configured | PASS |
| Isolation | 5 | Cross-tenant tests for all layers, running in CI, all passing | PASS |
| Scale | 3 | Load test completed but only 2x expected load (target: 5x) | CONDITIONAL |
| Chaos | 2 | Only compute failure tested, no DB or network failure injection | BLOCKER |
| Operations | 4 | Deployment rings defined, rollback tested, monitoring tenant-aware | PASS |

**Verdict**: NO-GO

**Blockers**:
1. Chaos testing incomplete: DB failure and network partition not tested
2. Scale test insufficient: Only 2x load tested, need 5x for SLO confidence

**Remediation timeline**: 2 weeks for chaos testing, 1 week for extended load test

---

## Example 2: GO Verdict

| Area | Score (1-5) | Evidence |
|------|------------|----------|
| SLO/SLA | 5 | All tiers defined, dashboards live, burn rate alerts tested |
| Isolation | 5 | All layers tested, CI green, pen test completed |
| Scale | 4 | 5x load tested, all SLOs met, noisy neighbor simulated |
| Chaos | 4 | Compute, DB, and network failures tested, blast radius contained |
| Operations | 5 | Ring deployment active, rollback tested weekly, full observability |

**Verdict**: GO

**Recommendations** (non-blocking):
1. Add quarterly chaos testing schedule
2. Automate SLO compliance reporting for enterprise tenants
3. Document escalation path for multi-tenant incidents affecting > 10 tenants

---

## Example 3: Evidence Gap Inventory

| Gap | Required Evidence | Current State | Priority |
|-----|-------------------|---------------|----------|
| Network isolation test | Automated test proving NSG blocks cross-tenant traffic | Manual verification only | P1 |
| Chaos: DB failover | Test proving tenant blast radius during PG failover | Not tested | P1 |
| Load test: 5x peak | Load test report at 5x expected tenant count | Only 2x completed | P2 |
| Rollback time | Measured rollback completion time | Procedure documented but not timed | P2 |
