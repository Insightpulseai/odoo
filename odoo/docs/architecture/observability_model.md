# Observability Model

> Defines telemetry sources, synthetic monitoring, real user monitoring (RUM), and pipeline separation.
> **SSOT**: `ssot/governance/operating-model.yaml` § `devsecops_control_planes.runtime_quality_observability`
> **Ref**: [What is monitoring?](https://learn.microsoft.com/en-us/devops/operate/what-is-monitoring)

---

## 1. Telemetry

Telemetry is the primary data source for monitoring. It flows through two distinct pipelines
depending on purpose.

### Telemetry Sources

| Source | What it collects | Tool |
| ------ | ---------------- | ---- |
| Application Insights SDK | Request traces, dependencies, exceptions, custom events | Application Insights |
| Auto-instrumentation agents | HTTP metrics, DB calls, container metrics (no code changes) | Azure Monitor agent |
| Server/container logs | stdout/stderr, structured application logs | Log Analytics |
| Infrastructure metrics | CPU, memory, network, disk for ACA and PG | Azure Monitor |

### Pipeline Separation

| Pipeline | Purpose | Latency | Retention |
| -------- | ------- | ------- | --------- |
| Real-time alerting | Detect incidents, trigger rollback | Seconds | 30 days (hot) |
| Troubleshooting / analytics | Root-cause investigation, usage analysis, validated learning | Minutes | 90 days (warm) |

The real-time pipeline feeds Azure Monitor alerts and Slack notifications.
The analytics pipeline feeds Log Analytics KQL queries, Application Insights dashboards,
and backlog prioritization.

---

## 2. Synthetic Monitoring

Synthetic monitoring runs predictable, repeatable transaction tests against production
endpoints on a schedule — independent of real user traffic.

### Purpose

- Detect availability and performance regressions before users report them
- Provide consistent baseline measurements across deploys
- Validate critical flows (login, API health, Odoo ERP load) continuously

### Implementation

| Check | Target | Frequency | Alert on |
| ----- | ------ | --------- | -------- |
| Health endpoint | `https://<service>.insightpulseai.com/health` | 1 min | Non-200 or timeout > 5s |
| Odoo login flow | `https://erp.insightpulseai.com/web/login` | 5 min | Non-200 or latency > 3s |
| API availability | `https://mcp.insightpulseai.com/api/health` | 2 min | Non-200 or timeout > 5s |
| Front Door probe | Azure Front Door built-in health probe | Configured per origin | Origin marked unhealthy |

### Tooling

- **Azure Monitor availability tests** (URL ping and multi-step) for public endpoints
- **Front Door health probes** for origin-level availability
- Future: Playwright-based synthetic tests for critical UI flows

---

## 3. Real User Monitoring (RUM)

RUM captures telemetry from actual user sessions — real network conditions, device types,
browser versions, and geographic distribution.

### Purpose

- Measure actual user experience (not just server-side metrics)
- Identify client-side performance bottlenecks (slow renders, JS errors)
- Compare experience across user segments (device, location, browser)

### Implementation

| Signal | Source | Tool |
| ------ | ------ | ---- |
| Page load timing | Browser SDK | Application Insights (JavaScript SDK) |
| Client-side exceptions | Browser SDK | Application Insights |
| User session flow | Browser SDK | Application Insights user flows |
| Network conditions | Browser performance API | Application Insights |

### Current Status

RUM is a **gap** — not yet instrumented. Priority for implementation:

1. Odoo web client (`erp.insightpulseai.com`) — highest user traffic
2. Public-facing pages (if/when deployed via ACA)

> **Note**: RUM requires adding the Application Insights JavaScript SDK to the frontend.
> For Odoo, this means a thin `ipai_*` module injecting the SDK snippet into the web asset bundle.

---

## 4. Dashboard & Evidence Links

Every production service must have:

| Artifact | Location | Owner |
| -------- | -------- | ----- |
| Service dashboard | Application Insights (linked from Azure Boards work item) | platform-lead |
| Alert rules | Azure Monitor (defined in IaC) | platform-lead |
| Incident evidence | `docs/evidence/<stamp>/incidents/` | responder |
| Post-deploy health | `docs/evidence/<stamp>/deploy/` | deployer |

Dashboard URLs are linked from Azure Boards Issues (FEAT-001-03 and related) so that
acceptance criteria verification can point to live evidence.

---

## 5. Validated Learning from Monitoring

Monitoring is not only for reliability — it closes the product feedback loop:

- After each release, compare usage telemetry against pre-release baseline
- Use funnel analysis (Application Insights user flows) to measure feature adoption
- Feed monitoring data into backlog prioritization: high-traffic, high-error paths get investment first
- Document learning in evidence bundles: `docs/evidence/<stamp>/learning/`

---

## Cross-References

- [reliability_operating_model.md](reliability_operating_model.md) — SLI/SLO, TTD/TTM/TTR, incident response
- [runtime_security.md](runtime_security.md) — container security and alert thresholds
- [devops_operating_model.md](../governance/devops_operating_model.md) — Pillar 4 mapping
- [devsecops_operating_model.md](devsecops_operating_model.md) — security monitoring

---

*Last updated: 2026-03-17*
