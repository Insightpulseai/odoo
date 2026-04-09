# Azure Platform Maturity Benchmark — PRD

**Version**: 1.0.0
**Status**: Draft
**Last Updated**: 2026-03-11
**Owner**: InsightPulse AI Platform Team

---

## Executive Summary

A structured benchmark for evaluating Azure platform maturity across six domains. Produces a weighted score used as a cutover readiness gate for production workloads (Odoo 18 CE, n8n, Superset, Keycloak) migrating to or operating on Azure infrastructure.

---

## Personas

| Persona | Role | Uses Benchmark For |
|---------|------|--------------------|
| Platform Engineer | Builds/maintains Azure infra | Gap analysis, remediation tracking |
| DevOps Engineer | Operates CI/CD + deployments | Deployment discipline scoring |
| Security Engineer | Reviews identity/networking posture | Governance and network hardening |
| Project Manager | Tracks cutover readiness | Go/no-go decision gate |

---

## Benchmark Domains

### Domain 1: Identity & Governance (20%)

| Criterion | Weight | L0 (0%) | L1 (25%) | L2 (50%) | L3 (75%) | L4 (100%) |
|-----------|--------|---------|----------|----------|----------|-----------|
| Entra ID tenant config | 3 | No tenant | Tenant exists, no MFA | MFA enforced for admins | MFA all users + conditional access | PIM + break-glass + JIT |
| Managed identities | 3 | Hardcoded credentials | Service principal + secret | System-assigned MI for ACA | User-assigned MI with least-privilege | MI for all services + no secrets |
| RBAC assignments | 2 | Owner on all resources | Contributor broadly | Role-scoped per resource group | Custom roles + PIM | Custom roles + PIM + access reviews |
| Resource tagging | 1 | No tags | Partial tags | env + owner tags on all RGs | Full tag policy enforced | Tag inheritance + cost allocation |
| Policy assignments | 1 | No policies | Audit-only policies | Deny policies on critical resources | Initiative-level enforcement | Remediation tasks automated |

### Domain 2: Networking (15%)

| Criterion | Weight | L0 | L1 | L2 | L3 | L4 |
|-----------|--------|----|----|----|----|-----|
| VNet topology | 3 | Flat/public | Single VNet, no NSGs | Hub-spoke or segmented | NSG per subnet + flow logs | Private endpoints + no public IPs |
| Cloudflare integration | 3 | Direct IP exposure | DNS only | DNS + proxy | DNS + proxy + WAF rules | Full stack: DNS + proxy + WAF + rate limit + bot mgmt |
| TLS termination | 2 | No TLS | Self-signed | Cloudflare edge TLS | Edge + origin TLS (Full Strict) | mTLS where applicable |
| DNS management | 2 | Manual records | Cloudflare UI-only | YAML-first + CI apply | YAML + Terraform + drift detection | Automated subdomain lifecycle |

### Domain 3: Compute & Runtime (20%)

| Criterion | Weight | L0 | L1 | L2 | L3 | L4 |
|-----------|--------|----|----|----|----|-----|
| Container runtime | 4 | Manual docker run | Docker Compose on VM | ACA single revision | ACA with revision management + scaling | ACA with Dapr + KEDA + zone redundancy |
| Image lifecycle | 3 | No registry | ACR exists, manual push | CI pushes to ACR | CI + image signing + vulnerability scan | Signed + scanned + auto-prune + SBOM |
| Resource limits | 2 | No limits | CPU/memory set | Autoscale rules defined | Scale-to-zero + burst limits | Cost-optimized scaling profiles |
| Health probes | 1 | None | Liveness only | Liveness + readiness | L + R + startup probe | Probes + dependency health cascade |

### Domain 4: Monitoring & Observability (15%)

| Criterion | Weight | L0 | L1 | L2 | L3 | L4 |
|-----------|--------|----|----|----|----|-----|
| Log aggregation | 3 | No logging | Container stdout only | Log Analytics workspace | Structured logs + queries | Alerts on log patterns + dashboards |
| Metrics collection | 3 | None | Basic Azure metrics | App Insights instrumented | Custom metrics + SLI definition | SLO dashboards + burn-rate alerts |
| Tracing | 2 | None | Request IDs | Distributed tracing (App Insights) | Cross-service correlation | Full trace context propagation |
| Alerting | 2 | None | Email on error | Action groups + severity levels | PagerDuty/Slack integration | Runbook-linked auto-remediation |

### Domain 5: Backup & Disaster Recovery (15%)

| Criterion | Weight | L0 | L1 | L2 | L3 | L4 |
|-----------|--------|----|----|----|----|-----|
| Database backup | 4 | No backups | Manual pg_dump | Scheduled automated backups | Automated + tested restore | PITR + cross-region + verified RTO |
| Filestore backup | 2 | No backup | Manual copy | Scheduled rsync/snapshot | Versioned storage + lifecycle | Cross-region replication |
| DR runbook | 2 | None | Documented | Documented + reviewed | Tested quarterly | Tested + automated failover |
| RTO/RPO targets | 2 | Undefined | Defined | Defined + measured | Met consistently | Exceeded with margin |

### Domain 6: Deployment & Promotion Discipline (15%)

| Criterion | Weight | L0 | L1 | L2 | L3 | L4 |
|-----------|--------|----|----|----|----|-----|
| CI/CD pipeline | 4 | Manual deploy | Basic GH Actions | Build + test + deploy | Branch-based environments + gates | Full GitOps with policy engine |
| Environment promotion | 3 | No staging | dev → prod direct | dev → staging → prod | Promotion gates + approval | Automated promotion with rollback |
| IaC coverage | 2 | No IaC | Partial Terraform/Bicep | All infra in IaC | IaC + drift detection | IaC + drift + auto-remediation |
| Rollback capability | 1 | No rollback | Manual revert | Automated rollback trigger | Blue-green or canary | Zero-downtime rollback + verification |

---

## Scoring Formula

```
domain_score = Σ(criterion_score × criterion_weight) / Σ(criterion_weight) × 100

aggregate_score = Σ(domain_score × domain_weight)

pass = aggregate_score ≥ 70 AND min(domain_scores) ≥ 50
cutover_ready = aggregate_score ≥ 85 AND min(domain_scores) ≥ 60
```

---

## Output Artifacts

| Artifact | Format | Path |
|----------|--------|------|
| Benchmark scorecard | YAML | `infra/ssot/azure/platform_maturity_benchmark.yaml` |
| Evidence pack | Markdown + JSON | `docs/evidence/<timestamp>/azure-maturity/` |
| Domain gap report | Markdown | `docs/evidence/<timestamp>/azure-maturity/gap_report.md` |
| CI gate result | JSON | CI artifact output |

---

## Dependencies

| Dependency | Source | Purpose |
|------------|--------|---------|
| Azure CLI (`az`) | Runtime | Evidence collection |
| Terraform state | `infra/terraform/` | IaC coverage analysis |
| GitHub Actions logs | CI | Deployment discipline evidence |
| Cloudflare API | Runtime | DNS/WAF configuration evidence |

---

## Constraints

- Benchmark rubric is SAP-on-Azure-inspired, not SAP-on-Azure-cloned
- All scoring criteria must be automatable via CLI/API probes
- No manual assessment steps in production gate mode
- Odoo-specific checks are out of scope (deferred to `odoo/` spec bundles)
