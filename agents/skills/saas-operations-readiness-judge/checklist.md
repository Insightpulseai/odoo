# Checklist: SaaS Operations Readiness Judge

## Provisioning Domain

- [ ] Tenant provisioning fully automated (zero manual steps)
- [ ] Provisioning success rate > 95% over last 30 days
- [ ] Provisioning SLA met for > 95% of recent provisions
- [ ] Idempotency verified (re-run does not create duplicates)
- [ ] Rollback tested (partial failure cleanup confirmed)
- [ ] Concurrent provisioning tested (10+ simultaneous)

## Monitoring Domain

- [ ] Per-tenant metrics collected (request rate, latency, errors)
- [ ] SLA dashboard operational with per-tenant breakdown
- [ ] Alerting configured for SLA breaches
- [ ] Distributed tracing working across all services
- [ ] Log aggregation with tenant_id filtering
- [ ] Infrastructure metrics (CPU, memory, connections) per stamp

## Incident Response Domain

- [ ] Runbooks exist for top 10 failure scenarios
- [ ] Escalation path defined (L1 -> L2 -> L3)
- [ ] On-call schedule active with coverage 24/7 (or agreed hours)
- [ ] Post-incident review process defined
- [ ] MTTD measured and within target (< 5 minutes for critical)
- [ ] MTTR measured and within target (< 30 minutes for critical)
- [ ] Communication templates for tenant notification during incidents

## Scaling Domain

- [ ] Auto-scaling rules configured for compute (Container Apps)
- [ ] Auto-scaling tested under load (target capacity validated)
- [ ] Capacity planning documented with 12-month projection
- [ ] New stamp provisioning automated (if stamp-based scaling)
- [ ] Database connection scaling tested under peak load
- [ ] Scaling triggers aligned with SLA requirements

## Billing Domain

- [ ] Usage metering accuracy > 99.9%
- [ ] Invoice generation automated
- [ ] Billing reconciliation process defined and running
- [ ] Billing dispute rate < 1%
- [ ] Free tier enforcement working in real-time
- [ ] Marketplace metering submission (if applicable) on schedule

## Compliance Domain

- [ ] Required certifications current (SOC2, GDPR registration)
- [ ] Last audit clean (no critical findings)
- [ ] Open compliance gaps < 5 (none critical)
- [ ] Data residency enforced via Azure Policy
- [ ] GDPR DSR procedures tested (export and delete)
- [ ] Audit log retention meets compliance requirements

## Verdict Assignment

- [ ] All six domains assessed with specific metrics
- [ ] Each domain assigned a score (Strong, Acceptable, Weak, Blocker)
- [ ] Verdict derived from domain scores
- [ ] Conditions documented with acceptance criteria (if CONDITIONAL)
- [ ] Blockers documented with remediation timeline (if NOT_READY)
- [ ] Assessment reviewed by operations team lead
