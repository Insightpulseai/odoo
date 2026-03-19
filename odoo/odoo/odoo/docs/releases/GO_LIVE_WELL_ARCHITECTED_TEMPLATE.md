# Go-Live Checklist Template (Well-Architected)

> **Purpose**: A repeatable, auditable go-live readiness checklist aligned to the Well-Architected pillars (Reliability, Security, Cost Optimization, Operational Excellence, Performance Efficiency) and cross-pillar go-live disciplines (Incident Mgmt, Monitoring, Release Mgmt, Configuration).
>
> **How to use**:
> 1. Copy this template per release: `docs/releases/go-live/GO_LIVE_<release>.md`
> 2. Complete all applicable items; attach evidence links/command outputs
> 3. Collect sign-offs from required roles
> 4. Store as a release artifact alongside the release manifest and runbook
>
> **Based on**: [Azure Well-Architected Framework](https://learn.microsoft.com/en-us/azure/well-architected/) and [Go-Live Assessment](https://learn.microsoft.com/en-us/assessments/b0f9a229-5f82-4f19-ae61-b7be31131f4e/)

---

## 0) Release Metadata

| Field | Value |
|-------|-------|
| Workload / Product | InsightPulse AI Platform |
| Release Name / Version | |
| Environment | (prod / staging) |
| Change Type | (feature / infra / data / config / hotfix) |
| Planned Go-Live Window (UTC) | |
| Owner (Release Captain) | |
| Approvers | (Eng / Sec / Data / Ops / Business) |
| Links | PR(s): • Runbook: • Dashboard: • Incident Channel: • Status Page: |

### Scope & Non-Goals
- **In scope**:
- **Out of scope**:

### Risk Summary (Top 5)

| Risk | Likelihood | Impact | Mitigation | Owner |
|------|------------|--------|------------|-------|
| | H/M/L | H/M/L | | |
| | | | | |
| | | | | |

---

## 1) Go/No-Go Decision Gate

### Entry Criteria (must be true before go-live)

- [ ] Release artifact created from this template and stored with release docs
- [ ] All required reviews completed (security, architecture, data, ops) with links
- [ ] Rollback strategy documented and tested (see Section 6)
- [ ] Monitoring/alerting in place and validated (see Section 3.2)
- [ ] Incident response ready (on-call, paging, comms) (see Section 3.1)
- [ ] Change window approved by stakeholders

### Go/No-Go Meeting Notes

- **Decision**: GO / NO-GO
- **Attendees**:
- **Notes / exceptions (if any)**:

---

## 2) Pillar Checklists (Well-Architected)

> Mark N/A explicitly where not applicable.

### 2.1 Reliability

| Check | Status | Evidence |
|-------|--------|----------|
| Availability targets defined (SLO/SLA) and communicated | ⬜ | |
| Dependency map created (critical upstream/downstream) | ⬜ | |
| Capacity plan validated against expected load | ⬜ | |
| Fault handling: retries/timeouts/circuit breakers defined | ⬜ | |
| Data durability: backups enabled, restore documented | ⬜ | |
| DR plan defined (RPO/RTO); DR runbook exists | ⬜ | |
| Deployment resiliency: canary/blue-green/rolling selected | ⬜ | |
| Known failure modes documented with mitigations | ⬜ | |

**Evidence Links**:
- SLO doc:
- Load test report:
- Backup/restore proof:
- DR runbook:

### 2.2 Security

| Check | Status | Evidence |
|-------|--------|----------|
| Identity model reviewed (least privilege, roles) | ⬜ | |
| Secrets managed via secure store (not in repo) | ⬜ | |
| Network boundaries validated (ingress/egress rules) | ⬜ | |
| Data protection: encryption in transit + at rest | ⬜ | |
| Tenant isolation / RLS validated (if multi-tenant) | ⬜ | |
| Security testing completed (SAST/DAST/deps scan) | ⬜ | |
| Audit logging enabled with retention set | ⬜ | |

**Evidence Links**:
- IAM/RBAC policy:
- Secret store references:
- Scan reports:
- RLS tests:

### 2.3 Cost Optimization

| Check | Status | Evidence |
|-------|--------|----------|
| Cost owners + tags/labels set for chargeback | ⬜ | |
| Resource sizing reviewed (right-sizing) | ⬜ | |
| Autoscaling policies defined | ⬜ | |
| Non-prod schedules defined (sleep/scale-down) | ⬜ | |
| Budget alerts and anomaly detection configured | ⬜ | |
| High-cost queries/jobs identified and bounded | ⬜ | |

**Evidence Links**:
- Cost dashboard:
- Budget alerts:
- Sizing notes:

### 2.4 Operational Excellence

| Check | Status | Evidence |
|-------|--------|----------|
| Runbooks completed: deploy, rollback, incident, failures | ⬜ | |
| CI/CD pipeline is deterministic and repeatable | ⬜ | |
| Config is versioned; drift detection in place | ⬜ | |
| On-call coverage, escalation, comms plan defined | ⬜ | |
| Break-glass / emergency access procedures defined | ⬜ | |
| Post-deploy verification steps documented | ⬜ | |

**Evidence Links**:
- Runbook links:
- CI pipeline run:
- Config audit:

### 2.5 Performance Efficiency

| Check | Status | Evidence |
|-------|--------|----------|
| Performance budgets set (p95 latency, throughput) | ⬜ | |
| Critical paths profiled; bottlenecks addressed | ⬜ | |
| Caching strategy defined (where applicable) | ⬜ | |
| DB query plans reviewed; indexes validated | ⬜ | |
| Rate limits / backpressure strategies implemented | ⬜ | |

**Evidence Links**:
- APM trace links:
- Query plans:
- Perf test results:

---

## 3) Cross-Pillar Go-Live Disciplines

### 3.1 Incident Management

| Check | Status | Evidence |
|-------|--------|----------|
| Incident severity definitions documented | ⬜ | |
| Paging/alerts routing verified (test page done) | ⬜ | |
| War room process defined (channel, bridge, roles) | ⬜ | |
| Customer comms templates prepared | ⬜ | |
| Post-incident review template ready | ⬜ | |

**Evidence Links**:
- Test page proof:
- IR runbook:
- Comms templates:

### 3.2 Monitoring

| Check | Status | Evidence |
|-------|--------|----------|
| Golden signals defined (latency, traffic, errors, saturation) | ⬜ | |
| Dashboards created and shared | ⬜ | |
| Alerts configured with sensible thresholds | ⬜ | |
| Synthetic checks implemented (if applicable) | ⬜ | |
| Logging/metrics/traces correlated (request IDs) | ⬜ | |

**Evidence Links**:
- Dashboard link:
- Alert rules:
- Synthetic check proof:

### 3.3 Release Management

| Check | Status | Evidence |
|-------|--------|----------|
| Release notes prepared (internal + external) | ⬜ | |
| Deployment method selected and rehearsed | ⬜ | |
| Feature flags documented (default states) | ⬜ | |
| Database migrations reviewed (forward/rollback) | ⬜ | |
| Freeze window observed (if applicable) | ⬜ | |

**Evidence Links**:
- Release notes:
- Rehearsal logs:
- Migration plan:

### 3.4 Configuration

| Check | Status | Evidence |
|-------|--------|----------|
| Config inventory documented (env vars, secrets, flags) | ⬜ | |
| Config changes peer-reviewed and versioned | ⬜ | |
| Safe defaults and validation checks in place | ⬜ | |
| Drift detection and auditing enabled | ⬜ | |

**Evidence Links**:
- Config diff:
- Validation logs:

---

## 4) Service/Platform Readiness

> Select applicable blocks; mark others N/A.

### 4.1 App Runtime (Odoo CE / Next.js)

| Check | Status | Evidence |
|-------|--------|----------|
| Health endpoints implemented (liveness/readiness) | ⬜ | |
| Timeouts configured at gateway + app layers | ⬜ | |
| Horizontal scaling configured and tested | ⬜ | |
| Rate limiting/WAF rules reviewed | ⬜ | |

### 4.2 Background Jobs / Queues (n8n)

| Check | Status | Evidence |
|-------|--------|----------|
| Idempotency keys used for at-least-once delivery | ⬜ | |
| Retry policies bounded (max retries, DLQ, backoff) | ⬜ | |
| Poison message handling and replay defined | ⬜ | |

### 4.3 Database (PostgreSQL / Supabase)

| Check | Status | Evidence |
|-------|--------|----------|
| Backup schedule and retention configured | ⬜ | |
| PITR enabled (if available) | ⬜ | |
| Connection pooling configured; max connections safe | ⬜ | |
| Migration rehearsal completed in staging | ⬜ | |
| RLS/tenant isolation validated | ⬜ | |

### 4.4 Edge / Serverless (Vercel / Supabase Functions)

| Check | Status | Evidence |
|-------|--------|----------|
| Cold start impact assessed | ⬜ | |
| Concurrency and timeout limits set | ⬜ | |
| Retry behavior understood | ⬜ | |

### 4.5 Networking / Gateway / CDN

| Check | Status | Evidence |
|-------|--------|----------|
| TLS certs valid and auto-renewing | ⬜ | |
| DNS cutover plan prepared | ⬜ | |
| DDoS/WAF posture validated | ⬜ | |
| Origin protection configured | ⬜ | |

### 4.6 Observability Platform

| Check | Status | Evidence |
|-------|--------|----------|
| Central log sink configured | ⬜ | |
| Trace sampling configured | ⬜ | |
| Audit log retention set | ⬜ | |

---

## 5) Cutover Plan & Validation

### 5.1 Pre-Cutover (T-7d to T-1h)

- [ ] Announce maintenance window (if any)
- [ ] Lower DNS TTL (if DNS cutover)
- [ ] Final backup taken (label: ____________)
- [ ] Staging is green and matches prod config
- [ ] Freeze non-essential changes

### 5.2 Cutover Steps

| Step | Owner | Command/Action | Expected Result | Duration | Evidence |
|------|-------|----------------|-----------------|----------|----------|
| 1 | | | | | |
| 2 | | | | | |
| 3 | | | | | |

### 5.3 Post-Deploy Validation (Must-Pass)

- [ ] Smoke tests passed (critical user journeys)
- [ ] Key metrics within thresholds (errors, latency)
- [ ] Data integrity checks passed
- [ ] Billing/entitlements checks passed (if applicable)
- [ ] Support readiness confirmed

**Evidence Links**:
- Smoke test output:
- Dashboard snapshots:
- Data checks output:

---

## 6) Rollback Strategy (Mandatory)

### 6.1 Rollback Criteria

| Condition | Threshold | Action |
|-----------|-----------|--------|
| Error rate | > ___% for ___ min | Rollback |
| p95 latency | > ___ms for ___ min | Rollback |
| Data corruption risk | Detected | Immediate rollback |
| Security regression | Detected | Immediate rollback |

### 6.2 Rollback Steps

| Step | Owner | Command/Action | Expected Result | Evidence |
|------|-------|----------------|-----------------|----------|
| 1 | | `git checkout <prev-tag>` | | |
| 2 | | `docker compose up -d` | | |
| 3 | | Verify health | | |

### 6.3 Rollback Validation

- [ ] Service restored to previous stable version
- [ ] Data state verified (no partial migrations)
- [ ] Customer comms updated

---

## 7) Sign-Offs

| Role | Name | Decision | Date | Notes |
|------|------|----------|------|-------|
| Engineering | | GO / NO-GO | | |
| Security | | GO / NO-GO | | |
| Data/DB | | GO / NO-GO | | |
| Operations/SRE | | GO / NO-GO | | |
| Business Owner | | GO / NO-GO | | |

---

## 8) Post-Go-Live Follow-Ups (T+1h to T+14d)

- [ ] Hypercare schedule defined (who watches what, when)
- [ ] Incident log reviewed daily during hypercare
- [ ] Cost and performance review at T+7d
- [ ] Post-implementation review (PIR) at T+14d
- [ ] Backlog created for improvements found

---

## References

- [Azure Well-Architected Framework](https://learn.microsoft.com/en-us/azure/well-architected/)
- [Go-Live | Well-Architected Review](https://learn.microsoft.com/en-us/assessments/b0f9a229-5f82-4f19-ae61-b7be31131f4e/)
- [Well-Architected Go-Live Assessment](https://techcommunity.microsoft.com/blog/azuremigrationblog/well-architected-go-live-now-available-on-the-microsoft-assessment-platform/3521561)
