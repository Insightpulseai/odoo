# Examples: SaaS Operations Readiness Judge

## Example 1: Verdict — READY

**Scenario**: Mature platform preparing for general availability.

```
## Verdict: READY

### Domain Scores
| Domain | Score | Key Metric |
|--------|-------|-----------|
| Provisioning | Strong | Success rate: 99.2%, SLA met: 98.5% |
| Monitoring | Acceptable | Per-tenant coverage: 100%, alert response: < 3min |
| Incident Response | Acceptable | MTTR: 22min, Runbooks: 12/12 top scenarios |
| Scaling | Strong | Load tested to 3x current, auto-scaling verified |
| Billing | Acceptable | Accuracy: 99.95%, Disputes: 0.3% |
| Compliance | Acceptable | SOC2 Type II current, 0 critical gaps |

### Recommendations (non-blocking)
- Monitoring: Add anomaly detection for proactive alerting
- Incident Response: Conduct quarterly game days for disaster recovery
- Billing: Implement real-time billing dashboard for tenant self-service
```

---

## Example 2: Verdict — CONDITIONAL

**Scenario**: Platform ready in most domains but monitoring has gaps.

```
## Verdict: CONDITIONAL

### Domain Scores
| Domain | Score | Key Metric |
|--------|-------|-----------|
| Provisioning | Acceptable | Success rate: 97%, SLA met: 95% |
| Monitoring | Weak | Per-tenant coverage: 60%, no distributed tracing |
| Incident Response | Acceptable | MTTR: 28min, Runbooks: 10/12 |
| Scaling | Acceptable | Load tested to 2x, auto-scaling configured |
| Billing | Strong | Accuracy: 99.98%, Disputes: 0.1% |
| Compliance | Acceptable | SOC2 current, 2 medium gaps |

### Conditions
1. **Per-tenant monitoring coverage must reach 90%**
   Acceptance criteria: All API endpoints emit metrics with tenant_id dimension
   Timeline: 2 weeks

2. **Distributed tracing must be operational**
   Acceptance criteria: OpenTelemetry spans with tenant_id across Odoo web + workers
   Timeline: 1 week

3. **Missing runbooks must be created**
   Acceptance criteria: Runbooks for "database failover" and "stamp capacity exhaustion"
   Timeline: 1 week

### Launch Decision
Proceed with launch after all 3 conditions met and verified.
```

---

## Example 3: Verdict — NOT_READY

**Scenario**: Platform with critical gaps in incident response and scaling.

```
## Verdict: NOT_READY

### Domain Scores
| Domain | Score | Key Metric |
|--------|-------|-----------|
| Provisioning | Acceptable | Success rate: 96%, SLA met: 93% |
| Monitoring | Weak | Per-tenant coverage: 40%, basic alerting only |
| Incident Response | Blocker | No runbooks, no on-call schedule, no escalation path |
| Scaling | Blocker | No auto-scaling, no load testing, no capacity plan |
| Billing | Acceptable | Accuracy: 99.9%, manual invoice review |
| Compliance | Weak | SOC2 planned but not started, 5 medium gaps |

### Blockers
1. **[CRITICAL] No incident response capability**
   Remediation: Create runbooks for top 10 scenarios, establish on-call rotation,
   define escalation path, conduct tabletop exercise
   Timeline: 3 weeks minimum

2. **[CRITICAL] No scaling strategy**
   Remediation: Configure Container Apps auto-scaling, conduct load test to 2x
   projected capacity, document capacity plan
   Timeline: 2 weeks minimum

### Additional Issues (non-blocking but should address)
3. [HIGH] Monitoring coverage at 40% — must reach 80% before GA
4. [MEDIUM] SOC2 certification not started — required within 6 months of GA
5. [MEDIUM] Invoice generation requires manual review — automate

### Launch Decision
DO NOT LAUNCH. Resolve blockers 1 and 2, then re-assess.
Estimated re-assessment date: 4 weeks from now.
```
