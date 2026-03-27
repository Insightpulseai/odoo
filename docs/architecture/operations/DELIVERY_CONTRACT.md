# Platform Delivery Contract

> Defines deployment tooling consistency, automation rules, service isolation,
> and environment parity requirements.
>
> **SSOT**: `ssot/governance/operating-model.yaml` (tool authority)
> **Ref**: [Safe deployment practices](https://learn.microsoft.com/en-us/devops/operate/safe-deployment-practices)
>
> Cross-references:
>   - [release_management_model.md](release_management_model.md) — progressive exposure, bake time
>   - [quality_engineering_model.md](quality_engineering_model.md) — release gates, rollback
>   - [reliability_operating_model.md](reliability_operating_model.md) — SLOs, incident response
>   - `ssot/governance/operating-model.yaml` § `devsecops_control_planes.secure_build_release`

---

## 1. Tooling Consistency Rule

The same deployment tooling and configuration model must be used across
development, test/staging, and production environments.

### Environment Parity

| Aspect | Dev | Staging | Production |
|--------|-----|---------|------------|
| Container runtime | ACA (local Colima for iteration) | ACA | ACA |
| Container registry | `cripaidev` | `cripaidev` | `cripaidev` |
| Database | Azure PG Flexible (`odoo_dev`) | Azure PG Flexible (`odoo_staging`) | Azure PG Flexible (`odoo`) |
| Secret store | Key Vault (`kv-ipai-dev`) | Key Vault (`kv-ipai-staging`) | Key Vault (`kv-ipai-prod`) |
| Identity | Managed identity | Managed identity | Managed identity |
| Edge | Azure Front Door (shared) | Azure Front Door (shared) | Azure Front Door (shared) |
| Deployment method | AzDo Pipeline | AzDo Pipeline | AzDo Pipeline |
| CI gates | GitHub Actions | GitHub Actions | GitHub Actions |

### Consistency Rules

- Pipeline definitions are stored in repo (`.azure/pipelines/`), never portal-only
- The same Dockerfile builds all environment images — environment-specific config is injected via env vars
- Infrastructure changes use IaC (Bicep/Terraform) with environment parameterization
- No snowflake environments — every environment difference must be documented and justified

---

## 2. Automation Rule

Manual deployment steps are exceptions, not the norm.

### Default: Automated

| Activity | Automation | Manual Exception |
|----------|-----------|-----------------|
| Build + push image | AzDo Pipeline (triggered by merge) | Never |
| Deploy to dev | AzDo Pipeline (auto on push) | Break-glass only |
| Deploy to staging | AzDo Pipeline (auto on tag or manual trigger) | — |
| Deploy to production | AzDo Pipeline (manual approval gate) | Break-glass only |
| Database migration | Pipeline stage (Odoo `--update`) | Emergency schema fix |
| DNS change | Terraform apply via CI | Never |
| Secret rotation | Key Vault + managed identity | Manual rotation with evidence |

### Break-Glass Protocol

When manual deployment is required (pipeline failure, emergency):

1. Document the manual step in the deployment evidence
2. Create a follow-up Issue to automate the manual step
3. Manual steps during incidents are acceptable — manual steps in steady state are debt

---

## 3. Service Isolation

New architecture decisions should prefer better isolation and blast-radius
reduction over monolithic shared-failure patterns.

### Isolation Principles

- Each service runs in its own ACA container app — no shared-process deployments
- Services communicate via well-defined APIs (REST/FastAPI), not shared database tables
- Failure in one service should not cascade to others (circuit-breaker pattern where applicable)
- Deployments are per-service — deploying Service A does not require redeploying Service B

### Current Isolation Model

| Service Group | Isolation Level | Notes |
|--------------|-----------------|-------|
| Odoo (web + worker + cron) | Process isolation (separate ACA apps) | Shared database by design |
| Auth (Keycloak) | Full isolation | Separate ACA app, separate config |
| MCP coordinator | Full isolation | Separate ACA app |
| Superset | Full isolation | Separate ACA app, separate PG |
| AI agents (Foundry) | External SaaS isolation | Azure AI Foundry managed |

### Isolation Gaps (Known)

- Odoo web/worker/cron share a database — a bad migration affects all three
- Front Door is shared across all services — a misconfiguration affects all public endpoints
- These are accepted risks documented here, not ignored risks

---

## 4. Build Metadata Contract

Every deployed container image must carry traceable metadata:

| Metadata | Source | Purpose |
|----------|--------|---------|
| Git commit hash | `$BUILD_SOURCEVERSION` | Trace image to exact code |
| AB# work-item ID | Pipeline variable or commit message | Trace image to work item |
| Build timestamp | Pipeline `$BUILD_BUILDID` | Ordering and audit |
| Branch | `$BUILD_SOURCEBRANCH` | Track promotion path |

### Metadata Injection

```yaml
# In AzDo pipeline
- task: Docker@2
  inputs:
    command: build
    arguments: >
      --label git.commit=$(Build.SourceVersion)
      --label azdo.workitem=$(System.PullRequest.SourceBranch)
      --label build.id=$(Build.BuildId)
```

---

## 5. Environment Promotion Path

```
Feature branch → PR (CI gates) → main → Dev deploy (auto)
                                    ↓
                              Tag/release → Staging deploy (auto)
                                    ↓
                              Approval gate → Prod deploy (manual trigger)
```

### Promotion Rules

- No skip-level promotion (cannot go from dev directly to prod)
- Staging must pass health checks before production deploy is unblocked
- Production deploys require explicit approval in AzDo pipeline
- Rollback is always available via ACA revision management

---

## 6. Identity Registration Rule

Each major app surface must have its own Entra app registration / enterprise app.
No shared "god app" registration for unrelated surfaces.

| Surface | Registration | Rationale |
|---------|-------------|-----------|
| Odoo ERP | `ipai-odoo` | Independent SSO, roles, consent, audit |
| Ops Console | `ipai-ops` | Separate admin privilege boundary |
| Plane | `ipai-plane` | Separate project-management access |
| MCP / Agent | `ipai-mcp` | Agent-specific scopes and controls |
| Superset | `ipai-superset` | BI read-access boundary |

See [identity_and_secrets.md](identity_and_secrets.md) § 3 for full app registration rules.

---

## Cross-References

- [identity_and_secrets.md](identity_and_secrets.md) — identity, sign-in, app isolation
- [release_management_model.md](release_management_model.md) — progressive exposure, rings, bake time
- [quality_engineering_model.md](quality_engineering_model.md) — release readiness, rollback criteria
- [reliability_operating_model.md](reliability_operating_model.md) — SLOs, backup/DR
- [devsecops_operating_model.md](devsecops_operating_model.md) — security in build/release
- `ssot/governance/operating-model.yaml` — tool authority, DevSecOps control planes

---

*Last updated: 2026-03-17*
