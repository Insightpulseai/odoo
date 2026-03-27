# Release Management Model

> Defines safe deployment doctrine: progressive exposure, exposure controls,
> bake time, hotfix routing, and deployment window policy.
>
> **SSOT**: `ssot/governance/azdo-execution-hierarchy.yaml` § `quality_risk_contract`
> **Ref**: [Safe deployment practices](https://learn.microsoft.com/en-us/devops/operate/safe-deployment-practices)
>
> Cross-references:
>   - [quality_engineering_model.md](quality_engineering_model.md) — release readiness, rollback criteria
>   - [reliability_operating_model.md](reliability_operating_model.md) — SLOs, incident response
>   - [platform_delivery_contract.md](platform_delivery_contract.md) — tooling consistency, automation
>   - `ssot/governance/operating-model.yaml` — tool authority boundaries

---

## 1. Safe Deployment Doctrine

Production releases use **progressive exposure** by default. No change reaches
the full production audience in a single step. Each rollout stage must prove
itself with production quality signals before exposure is widened.

```
Build → Dev → Staging → Prod (Ring 0) → Prod (Ring 1) → Full Production
                                ↑                ↑
                          Bake + observe    Bake + observe
```

### Core Principles

- Broaden audience only after production quality signals remain healthy
- Every stage is a decision point: proceed, hold, or rollback
- Deployment is not complete until monitoring confirms stability (see reliability model)
- Same deployment tooling and automation across dev, test, and production

---

## 2. Progressive Exposure Model

### Exposure Stages

| Stage | Audience | Purpose | Minimum Bake Time |
|-------|----------|---------|-------------------|
| Dev | Developer(s) | Functional verification | Until CI green |
| Staging | Internal test | Integration verification against staging data | 1 hour |
| Prod Ring 0 | Platform team / canary | Production validation with real traffic | 4 hours |
| Prod Ring 1 | Expanded internal | Broader production validation | 24 hours |
| Full Production | All users | General availability | — |

> **Note**: Current solo-operator model collapses Ring 0 and Ring 1 into a
> single canary stage. The ring structure is documented so it scales correctly
> when the team grows. At minimum, staging → production is always a two-step
> deploy with bake time between steps.

### Progression Criteria

Proceed to the next ring only when ALL of these hold:

- Health checks passing for the bake-time duration
- Error rate within SLO (see reliability model § SLOs)
- No new critical/high alerts fired
- No degradation in P95 latency
- Container restart count within normal bounds

---

## 3. Exposure Controls

### Rings

Ring-based deployment uses ACA revision management to control traffic split:

| Ring | Traffic Share | Mechanism |
|------|-------------|-----------|
| Ring 0 (canary) | 10% | ACA traffic splitting (new revision) |
| Ring 1 (early) | 50% | ACA traffic weight adjustment |
| Full | 100% | ACA revision promotion |

Rollback at any ring = shift 100% traffic back to previous healthy revision.

### Feature Flags

For changes that need finer-grained control than ring-based deployment:

- Feature flags gate functionality within a single deployed revision
- Flags are managed via Odoo `ir.config_parameter` or environment variables
- Flags follow the naming convention: `feature.<domain>.<capability>` (e.g., `feature.ai.copilot_advisory`)
- Flags must have a documented expiration — no permanent feature flags without justification

### User Opt-In

Where appropriate, new capabilities may be exposed via explicit user opt-in:

- User-facing preference or module install (Odoo context)
- Channel-level activation (Slack agent context)
- Opt-in is the most conservative exposure control and is preferred for high-risk user-facing changes

---

## 4. Bake Time

Each exposure stage requires sufficient observation time to surface latent faults.

### Bake Time Requirements

| Workload Type | Minimum Bake Time | Observation Window |
|--------------|-------------------|-------------------|
| Stateless API / web | 4 hours | At least 1 business-peak period |
| Background worker / cron | 24 hours | At least 1 full cron cycle |
| Database migration | 48 hours | At least 2 business-peak periods |
| Security-sensitive change | 48 hours | At least 1 full business day |

### Business-Peak Observation

Business-peak observation is required for business-hour-sensitive services
(Odoo ERP, finance modules, BIR compliance). A change deployed Friday evening
does not satisfy bake time until it has been observed through Monday business hours.

---

## 5. Hotfix Policy

Hotfixes bypass normal ring progression based on severity:

| Severity | Path | Bake Time | Approval |
|----------|------|-----------|----------|
| P1 — Critical (service outage) | Direct to impacted production units | Shortened: 1 hour post-fix monitoring | Platform lead |
| P2 — High (major feature broken) | Accelerated: staging → prod (skip Ring 0/1 split) | 2 hours | Platform lead |
| P3 — Medium | Normal ring progression | Standard bake time | Engineering lead |
| P4 — Low | Normal ring progression, next scheduled release | Standard bake time | Engineering lead |

### Hotfix Rules

- P1 hotfixes may target only the impacted service/revision — not a broad redeployment
- Even P1 hotfixes require: CI green, security scan, and a post-deploy health check
- Every hotfix produces a post-incident evidence pack (see reliability model § Incident Response)
- Hotfix PRs use the `hotfix` label and reference the incident work item (AB#ID)

---

## 6. Deployment Window Policy

### Standard Deployments

- **Preferred window**: Working hours, early in day and early in week
- **Rationale**: Lower blast radius and faster coordinated remediation when the team is available
- **Avoid**: Friday afternoon, weekends, holidays, and hours before business-critical deadlines (e.g., BIR filing dates)

### Hotfix Deployments

- Hotfixes deploy when needed regardless of window
- Post-deploy monitoring must be active for the duration of bake time
- If deploying outside working hours, the deployer must be available for the full bake period

### Freeze Windows

- No deployments during BIR filing windows (last 3 business days before filing deadline)
- No deployments during planned Azure maintenance windows
- Freeze exceptions require platform-lead approval and explicit risk acceptance

---

## 7. Azure Boards Integration

Release management items tracked in Azure Boards:

| Work Item Type | Content |
|---------------|---------|
| Issue (per release) | Release scope, ring progression plan, bake-time targets |
| Task | Ring-specific deploy, monitor, promote/rollback decisions |
| Linked PRs | Implementation PRs with AB# references |
| Evidence | Links to `docs/evidence/<stamp>/deploy/` artifacts |

### Acceptance Criteria (Release Issues)

- Rollout strategy defined (rings, flags, or opt-in)
- Bake-time requirement documented per workload type
- Rollback path documented (ACA revision ID or feature flag kill switch)
- Working-hours deployment window confirmed
- Post-deploy monitoring evidence captured

---

## Cross-References

- [quality_engineering_model.md](quality_engineering_model.md) — release readiness checklist, rollback criteria
- [reliability_operating_model.md](reliability_operating_model.md) — SLOs, incident response, DR
- [platform_delivery_contract.md](platform_delivery_contract.md) — tooling consistency, automation, isolation
- [devsecops_operating_model.md](devsecops_operating_model.md) — security gates in release pipeline
- [runtime_security.md](runtime_security.md) — container security posture
- `ssot/governance/operating-model.yaml` — tool authority, GitHub traceability

---

*Last updated: 2026-03-17*
