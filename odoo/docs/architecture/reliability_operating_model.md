# Reliability Operating Model

> Defines monitoring goals, SLI/SLO, incident response, backup/DR, alerting ownership, and evidence capture.
> **SSOT**: `ssot/governance/operating-model.yaml`
> **Ref**: [What is monitoring?](https://learn.microsoft.com/en-us/devops/operate/what-is-monitoring)

---

## 1. Monitoring Goals

Monitoring collects information about application performance and usage patterns
after deployment. It serves two core outcomes:

### High Availability

Improve three time-based metrics to reduce impact of production incidents:

| Metric | Definition | Target |
|--------|-----------|--------|
| **TTD** — Time to Detect | Time from incident start to first alert | < 5 min (P1/P2) |
| **TTM** — Time to Mitigate | Time from detection to user-impact reduction (rollback, failover) | < 15 min (P1), < 1 hr (P2) |
| **TTR** — Time to Remediate | Time from detection to root-cause fix deployed | < 4 hrs (P1), < 1 sprint (P2) |

These are initial targets. Track actuals per incident and adjust as the platform matures.

### Validated Learning

Production monitoring is not only for reliability — it feeds product decisions:

- Measure usage after every release to confirm or reject hypotheses
- Compare behavior across revisions (A/B, canary, or before/after)
- Use production telemetry to prioritize backlog (high-traffic paths get investment first)
- Dashboard evidence links in Azure Boards work items close the learning loop

### Production Monitoring Contract

- Every deployed service MUST emit health and performance telemetry
- Every service MUST have alerting, dashboards, and an incident evidence path
- Rollback/mitigation triggers MUST be defined before deploy (see § Rollback below)
- Deployment is NOT complete until monitoring is confirmed active

---

## 2. Service Level Indicators (SLIs)

| SLI | Measurement | Source |
|-----|-------------|--------|
| Availability | % of successful HTTP responses (non-5xx) | Application Insights |
| Latency | P95 response time | Application Insights |
| Error rate | 5xx responses / total responses | Application Insights |
| Container health | Restart count per time window | Azure Monitor |

---

## 3. Service Level Objectives (SLOs)

| Service | Availability SLO | Latency SLO (P95) | Error Rate SLO |
|---------|------------------|--------------------|----------------|
| Odoo ERP (`erp.`) | 99.5% monthly | < 2s | < 1% |
| MCP coordinator (`mcp.`) | 99.0% monthly | < 5s | < 2% |
| Auth/Keycloak (`auth.`) | 99.5% monthly | < 1s | < 0.5% |
| Other ACA services | 99.0% monthly | < 3s | < 2% |

**Error budget**: When remaining error budget < 25%, freeze non-critical changes until budget recovers.

> **Note**: These are initial targets for the solo-operator model. Adjust as traffic patterns and business requirements mature.

---

## 4. Monitoring & Alerting Ownership

### Alert Routing

| Severity | Response Time | Channel | Owner |
|----------|--------------|---------|-------|
| Critical (P1) | 15 min | Slack `#alerts-critical` | platform-lead |
| High (P2) | 1 hour | Slack `#alerts` | platform-lead |
| Medium (P3) | Next business day | Slack `#alerts` | engineering-lead |
| Low (P4) | Next sprint | Azure Boards backlog | engineering-lead |

### Alert Definitions

See [runtime_security.md](runtime_security.md) § Monitoring & Alerting for threshold-based alert rules.

### Alerting Stack

- **Azure Monitor**: Infrastructure and ACA metrics
- **Application Insights**: Application-level traces and metrics
- **Slack integration**: Alert notifications via Azure Monitor action groups → Slack webhook

---

## 5. Incident Response

### Severity Classification

| Severity | Definition | Example |
|----------|-----------|---------|
| P1 — Critical | Complete service outage or data loss risk | Odoo unreachable, database corruption |
| P2 — High | Major feature degraded, no workaround | Payment processing broken, auth failures |
| P3 — Medium | Feature degraded with workaround available | Report generation slow, non-critical module error |
| P4 — Low | Minor issue, cosmetic, or non-user-facing | UI alignment, log noise, internal tool issue |

### Response Flow

```
Alert fires → Acknowledge (Slack) → Classify severity →
Investigate (logs, metrics, traces) → Mitigate (rollback / hotfix) →
Resolve → Post-incident evidence → Azure Boards work item
```

### Post-Incident

- Evidence captured in `docs/evidence/<stamp>/incidents/`
- Root cause documented
- Azure Boards work item created for follow-up fixes
- Preventive action tracked as Issue in relevant Epic

---

## 6. Release Reliability Expectations

### Zero-Downtime Target

Releases should target no downtime. The deployment mechanism (ACA revision
management with traffic splitting) supports zero-downtime by design:

- New revision is deployed alongside the current revision
- Health check must pass before any traffic is routed to the new revision
- Traffic is shifted gradually (see [release_management_model.md](release_management_model.md) § Rings)
- Rollback = shift traffic back to previous revision (no downtime)

**Exception**: Database schema migrations that require exclusive locks may cause
brief service interruption. These must be scheduled during low-traffic windows
and documented in the release Issue.

### Working-Hours Deployment Policy

Standard deployments occur during working hours to ensure fast coordinated
remediation if something fails:

| Deployment Type | Preferred Window | Rationale |
|----------------|-----------------|-----------|
| Standard release | Mon–Thu, 09:00–15:00 PHT | Full business day for observation |
| Infrastructure change | Mon–Wed, 09:00–12:00 PHT | Early in week for recovery time |
| Hotfix (P1/P2) | When needed | Incident response overrides windows |
| Database migration | Mon–Tue, 09:00–11:00 PHT | Earliest in week, minimal traffic |

**Avoid**: Friday afternoon, weekends, holidays, and the 3 business days before
BIR filing deadlines.

See [release_management_model.md](release_management_model.md) for progressive
exposure, bake time, and hotfix routing details.

---

## 7. Backup & Restore

### Database Backups

| Database | Backup Method | Frequency | Retention | Restore Target |
|----------|--------------|-----------|-----------|----------------|
| `odoo` (prod) | Azure PG automated backup | Continuous (PITR) | 35 days | < 1 hour |
| `odoo_staging` | Azure PG automated backup | Continuous (PITR) | 7 days | < 2 hours |
| `odoo_dev` | Local pg_dump | On-demand | 3 most recent | Best effort |

### Application State

- Container images are immutable and stored in ACR (versioned by tag + digest)
- Configuration is in repo (IaC) — restore = redeploy from main
- Secrets are in Key Vault — versioned, soft-delete enabled

### Disaster Recovery

| Scenario | Recovery Strategy | RTO | RPO |
|----------|------------------|-----|-----|
| Container failure | ACA auto-restart + revision rollback | < 5 min | 0 (stateless) |
| Database corruption | Azure PG PITR restore | < 1 hour | Minutes (PITR) |
| Region failure | Manual failover to secondary region | < 4 hours | Minutes |
| ACR unavailable | Redeploy from cached images or rebuild | < 1 hour | 0 |

> **Note**: Multi-region is not active. Current DR relies on Azure PG PITR and ACR geo-replication (if enabled). Formal DR plan is a gap to close under OBJ-006.

---

## 8. Evidence Capture

All reliability events produce evidence:

| Event | Evidence Location | Content |
|-------|-------------------|---------|
| Deployment | `docs/evidence/<stamp>/deploy/` | Build log, health check result, commit hash |
| Incident | `docs/evidence/<stamp>/incidents/` | Timeline, root cause, metrics, resolution |
| Backup test | `docs/evidence/<stamp>/backup/` | Restore test result, timing |
| SLO breach | `docs/evidence/<stamp>/slo/` | Error budget status, contributing factors |

---

## Cross-References

- [release_management_model.md](release_management_model.md) — progressive exposure, bake time, hotfix routing
- [platform_delivery_contract.md](platform_delivery_contract.md) — tooling consistency, automation, isolation
- [observability_model.md](observability_model.md) — telemetry, synthetic monitoring, RUM
- [devops_operating_model.md](../governance/devops_operating_model.md) — Pillar 4 mapping
- [runtime_security.md](runtime_security.md) — monitoring alerts and thresholds
- [quality_engineering_model.md](quality_engineering_model.md) — rollback criteria
- [devsecops_operating_model.md](devsecops_operating_model.md) — security incident flow

---

*Last updated: 2026-03-17*
