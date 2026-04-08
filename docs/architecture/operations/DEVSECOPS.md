# DevSecOps Operating Model

> **SSOT**: `ssot/governance/operating-model.yaml` (machine-readable authority)
> **Ref**: [Enable DevSecOps with Azure and GitHub](https://learn.microsoft.com/en-us/devops/devsecops/enable-devsecops-azure-github)
> **Constraint**: Does NOT change Epic → Issue → Task hierarchy or tool ownership boundaries.

---

## Control Plane Summary

```
Azure Boards is the execution coordination and traceability system of record.
GitHub is the code and pull-request truth.
Azure Pipelines is the build/deploy and artifact-traceability plane.
Microsoft Entra and Azure RBAC are the identity and access-control plane.
Azure Key Vault is the secrets authority.
Azure Monitor / Application Insights is the runtime quality and rollback signal plane.
Defender and Azure Policy are the container/runtime security enforcement plane.

Detailed specs, architecture doctrine, SSOT files, and runtime evidence remain in the repo.
```

---

## 1. Planning & Traceability

**Tools**: Azure Boards, GitHub

- Every implementation PR must reference an Azure Boards work item (`AB#ID` in title or commit)
- PRs, merge commits, and builds are part of the audit trail
- Security findings (GHAS alerts, Defender findings) must be triaged back to work items
- Work-item state is not "done" until security and runtime evidence exist
- Branch/PR/work-item associations are delivery evidence (per `operating-model.yaml` traceability rules)

## 2. Shift-Left Security

**Tools**: GitHub (GHAS), GitHub Actions

Security is integrated at the earliest point in the lifecycle, not bolted on after deployment.

| Layer | Tool | When |
|-------|------|------|
| Secret scanning | GHAS + GitLeaks | On push, PR |
| Code scanning (SAST) | GHAS + Semgrep | On push, PR |
| Dependency review | GHAS + Trivy | On push, PR |
| Container image scanning | Trivy + Defender | On ACR push |

CI gates are required status checks on protected branches. A PR cannot merge if security scans fail.

## 3. Secure Build & Release

**Tools**: Azure Pipelines, GitHub Actions

- GitHub Actions handles CI (linting, tests, SSOT guards, security scans)
- Azure Pipelines handles CD (Azure resource deployment)
- Pipeline definitions are stored in repo (`.azure/pipelines/`), never portal-only
- Build metadata (commit hash, `AB#` work-item ID) is embedded in container image labels
- Environment promotion: `dev` (auto) → `staging` (approval gate) → `prod` (approval gate)
- No manual Azure portal deployments in steady state

## 4. Identity & Access

**Tools**: Microsoft Entra ID, Azure RBAC

See [identity_and_secrets.md](identity_and_secrets.md) for detailed guidance.

- Managed identities preferred over service principals for service-to-service auth
- Workload identity federation (OIDC) for AzDo ↔ ARM service connections
- Named accounts with MFA for all platform admins
- Zero day-to-day Global Admin usage

## 5. Secrets Authority

**Tool**: Azure Key Vault (`kv-ipai-dev`)

See [identity_and_secrets.md](identity_and_secrets.md) for detailed guidance.

- Key Vault is the canonical secret store — no secrets in code
- Runtime binding: managed identity → Key Vault → environment variables
- AzDo variable groups reference Key Vault, not inline secrets
- GitHub Actions uses GitHub Secrets (scoped to workflows)
- Secret rotation documented for: Zoho SMTP, PostgreSQL, API keys

## 6. Runtime Quality & Observability

**Tools**: Azure Monitor, Application Insights

See [runtime_security.md](runtime_security.md) for container-specific controls.

- Application Insights enabled for all Azure Container Apps workloads
- Log Analytics workspace active for centralized log aggregation
- Health/smoke checks defined for every production endpoint
- Quality gates: alert threshold → investigate → rollback decision
- Deployment completion requires green health check evidence in `docs/evidence/`

## 7. Container & Runtime Security

**Tools**: Defender for Containers, Azure Policy

See [runtime_security.md](runtime_security.md) for detailed guidance.

- Defender for Cloud enabled for active container estate
- Azure Policy enforces allowed container registries (`cripaidev`, `ipaiodoodevacr`)
- Container vulnerability scanning on push to ACR
- Runtime anomaly detection active for production workloads

---

## Traceability Contract

```
Code change → PR (AB#ID) → CI gates pass → Security scans green →
CD pipeline deploys → Health check green → Work item updated →
Evidence captured → Definition of Done met
```

A work item is not "done" until:
1. All acceptance criteria verified with evidence
2. Links to PRs, specs, or evidence docs present
3. Security scans green (no open critical/high findings)
4. Runtime health check passing
5. No open Blocked By links

---

## Cross-References

- [operating-model.yaml](../../ssot/governance/operating-model.yaml) — machine-readable authority
- [azdo-execution-hierarchy.yaml](../../ssot/governance/azdo-execution-hierarchy.yaml) — work item hierarchy
- [runtime_security.md](runtime_security.md) — container/runtime controls
- [identity_and_secrets.md](identity_and_secrets.md) — identity/secrets guidance
- [AZURE_DEVOPS_OPERATING_MODEL.md](AZURE_DEVOPS_OPERATING_MODEL.md) — local/remote workflow

---

*Last updated: 2026-03-17*
