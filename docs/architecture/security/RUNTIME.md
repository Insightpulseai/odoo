# Runtime Security

> Container, runtime, and observability security controls for the InsightPulse AI platform.
> **SSOT**: `ssot/governance/operating-model.yaml` § `devsecops_control_planes`
> **Ref**: [Enable DevSecOps with Azure and GitHub](https://learn.microsoft.com/en-us/devops/devsecops/enable-devsecops-azure-github)

---

## 1. Container Security Posture

### Registry Controls

- Allowed registries: `cripaidev.azurecr.io`, `ipaiodoodevacr.azurecr.io`
- Azure Policy enforces that only images from allowed registries can run in ACA
- Container images are scanned for vulnerabilities on push to ACR

### Image Hygiene

- Base images pinned to specific digests, not floating tags
- Multi-stage builds minimize attack surface (build deps excluded from runtime image)
- No secrets baked into images — runtime injection via managed identity → Key Vault

### Defender for Containers

- Defender for Cloud enabled for the active container estate (`rg-ipai-dev`)
- Runtime anomaly detection active for production workloads
- Vulnerability findings triage back to Azure Boards work items

## 2. Policy Enforcement

### Azure Policy

| Policy | Scope | Effect |
|--------|-------|--------|
| Allowed container registries | `rg-ipai-dev` | Deny |
| Container Apps must use managed identity | `rg-ipai-dev` | Audit |
| HTTPS-only ingress | `cae-ipai-dev` | Deny |
| Key Vault for secrets (no inline env secrets) | `rg-ipai-dev` | Audit |

Policies are defined in Bicep/Terraform and tracked in `infra/`. No portal-only policy assignments.

## 3. Monitoring & Alerting

### Health Checks

Every production workload has:
- A liveness probe (container-level)
- A readiness probe (traffic-level)
- A smoke test endpoint (application-level, `/health` or equivalent)

Deployment is not complete until the smoke test returns healthy.

### Azure Monitor Alerts

| Signal | Threshold | Action |
|--------|-----------|--------|
| Container restart count | > 3 in 15 min | Alert → investigate |
| HTTP 5xx rate | > 5% over 5 min | Alert → rollback candidate |
| Response latency P95 | > 2s sustained | Alert → investigate |
| CPU utilization | > 80% sustained | Alert → scale review |

### Application Insights

- Enabled for all ACA workloads via auto-instrumentation
- Distributed tracing correlates requests across Odoo, MCP, and agent services
- Log Analytics workspace for centralized log aggregation and KQL queries

## 4. Rollback & Quality Gates

Deployment quality gates:
1. **Pre-deploy**: CI gates pass, security scans green, image vulnerability scan clean
2. **Post-deploy**: Health check green within 90 seconds
3. **Sustained**: No alert triggers within 15-minute bake period

Rollback triggers:
- Health check fails after deploy
- 5xx rate exceeds threshold
- Defender alerts on runtime anomaly

Rollback mechanism: ACA revision management (traffic shift to previous healthy revision).

## 5. Network Security

- Azure Front Door (`ipai-fd-dev`) terminates TLS at the edge
- WAF policy active on Front Door
- ACA workloads are not directly internet-accessible (Front Door → ACA ingress only)
- Service-to-service communication within the ACA environment uses internal DNS
- **Odoo Azure Blob Storage**:
    - Roles: Prefer custom role or `Storage Blob Data Reader/Writer` over broad `Contributor`.
    - CORS: Scoped to `erp.insightpulseai.com` and dev/staging origins; wildcard `*` is prohibited.

---

## Cross-References

- [devsecops_operating_model.md](devsecops_operating_model.md) — parent DevSecOps model
- [identity_and_secrets.md](identity_and_secrets.md) — identity/secrets controls
- [RUNTIME_CONTRACT_AZURE_ODOO.md](RUNTIME_CONTRACT_AZURE_ODOO.md) — Odoo-specific runtime

---

*Last updated: 2026-03-17*
