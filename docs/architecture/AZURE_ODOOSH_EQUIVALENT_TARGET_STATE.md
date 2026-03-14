# Azure Odoo.sh-Equivalent Target State

> Version: 1.0.0
> Last updated: 2026-03-15
> Canonical repo: `infra` (mirrored in `odoo` for runtime alignment)
> Status: Canonical target-state doctrine

## Purpose

Define the Azure-native equivalent of the operational capabilities commonly associated with Odoo.sh, while preserving InsightPulseAI's canonical platform doctrine:

- Odoo is the operational system of action
- Azure is the control plane
- Foundry is the copilot / agent runtime
- Cloudflare remains edge / DNS / protection
- This document treats Odoo.sh as a **benchmark capability model**, not as the deployment target

## Scope

This document defines the target operating model for:

- source-driven build and deployment flow
- stage promotion semantics
- runtime shell / logs / monitoring expectations
- staging data refresh policy
- dependency management model
- backup / restore model
- non-production safety controls
- evidence and audit requirements

This document does **not** define:

- product positioning or marketing copy
- functional business workflows
- Odoo module-level feature parity
- Azure resource-by-resource IaC details

## Canonical Naming

### Databases

- `odoo_dev` — clean control development database
- `odoo_dev_demo` — auxiliary development showroom/demo database
- `odoo_staging` — staging rehearsal database
- `odoo` — production database

### Environments

- `dev` hosts `odoo_dev` and may also host `odoo_dev_demo`
- `staging` hosts `odoo_staging`
- `production` hosts `odoo`

Database names are canonical and must not be renamed to hyphenated environment labels.
Hyphenated forms such as `odoo-dev`, `odoo-staging`, and `odoo-production` may be used only for Azure resource or environment naming where needed.

## Benchmark Model

The benchmark capability set to reproduce on Azure is:

- GitHub-driven build lifecycle
- development / staging / production separation
- staging built from production-derived neutralized data
- isolated runtime per build / environment
- shell and logs for operators
- module dependency management
- Python dependency injection from repo
- automated testing before promotion
- monitored production runtime
- backup / restore and rollback discipline
- non-production email and external integration safety controls

## Canonical Doctrine

```text
Git is the source of code truth.
Azure is the control plane.
Odoo is the runtime system of action.
Foundry is the assistant runtime.
Cloudflare is the edge and DNS layer.
```

## Azure Equivalent Capability Model

### 1. Source and Build Model

Source changes originate in GitHub and trigger controlled CI/CD execution.

Target state:

- GitHub is the source trigger surface
- Azure DevOps Pipelines and/or GitHub Actions perform validation, packaging, promotion, and deployment
- Builds produce traceable artifacts tied to: commit SHA, branch / environment, runtime contract version, addon inventory, dependency manifest
- Every deployment must be attributable to a specific Git revision

### 2. Environment Model

The canonical environments are:

| Environment | Database | Purpose |
|-------------|----------|---------|
| dev | `odoo_dev` | Rapid iteration, validation, test execution, debug |
| dev (aux) | `odoo_dev_demo` | Showroom/demo data, on-demand only |
| staging | `odoo_staging` | Pre-production rehearsal, UAT, release candidate validation |
| production | `odoo` | Authoritative operational runtime |

#### dev (`odoo_dev`)

- Disposable or refreshable database
- Demo data allowed (in `odoo_dev_demo`)
- Relaxed scale settings
- Debug shell permitted
- External side effects suppressed by default

#### staging (`odoo_staging`)

- Production-derived but neutralized data
- Production-like config shape
- Outbound side effects suppressed unless explicitly allowed
- Release evidence generated here before production promotion

#### production (`odoo`)

- Only promoted from validated staging candidate
- Monitored continuously
- Backup and restore procedures verified
- Changes auditable to commit / artifact / approver / run

### 3. Runtime Model

The Azure target runtime must provide operator affordances:

- Live logs
- Shell / exec access
- Runtime metrics and health status
- Restart / recover actions
- Dump / restore workflow
- Controlled dependency loading
- Addon path determinism

Allowed implementation patterns:

- Azure Container Apps
- Azure VM / VMSS-backed containerized runtime
- AKS only if explicitly justified

The runtime contract is more important than the specific Azure compute primitive.

### 4. Data Model

Target state:

- Azure Database for PostgreSQL Flexible Server or approved equivalent
- Environment isolation by canonical database naming and policy
- Production restore path proven
- Staging refresh path proven
- Development reset path proven

### 5. Storage Model

Blob/object storage must cover:

- Filestore equivalents
- Uploaded artifacts
- Release evidence packs
- Dumps / backups / restore inputs
- Exported logs where needed

### 6. Secrets and Identity Model

Target state:

- Microsoft Entra ID for human/operator identity
- Managed Identity for workload-to-service auth
- Azure Key Vault for secrets and certificates
- No plaintext runtime secrets in repo
- No browser-exposed privileged credentials

### 7. Observability Model

Target state:

- Azure Monitor + Application Insights + Log Analytics
- Centralized logs, metrics, application traces
- Deployment history and environment health dashboards
- Failure alerts
- Health probes at runtime and edge

### 8. Edge and DNS Model

- DNS owned in Cloudflare (authoritative)
- Edge policy codified in infra
- Origin routing aligned to stage / service / hostname contract
- Production hostnames only target approved origins

## Capability Parity Table

| Benchmark capability | Azure target equivalent |
|---|---|
| GitHub integration | GitHub + Azure DevOps/GitHub Actions |
| Automatic build per revision | Pipeline run per commit / PR / merge |
| Dev / staging / prod branches | `odoo_dev` / `odoo_staging` / `odoo` environment model |
| Logs in browser | Azure Monitor / container logs / pipeline logs |
| Web shell / SSH-like access | Controlled exec / shell into runtime container or host |
| Module dependencies | Addon path contract + submodule support |
| Python dependencies | Repo-owned `requirements.txt` loading |
| Mail catcher in non-prod | SMTP suppression / sink / safe non-prod mail routing |
| Continuous integration | Repo validation workflow + deploy pipeline |
| Monitoring | App Insights + Log Analytics + health checks |
| Backups | Scheduled dump/backup + restore-tested runbook |
| Staging from prod data | Neutralized production snapshot refresh workflow |

## Non-Production Safety Rules

The Azure equivalent platform must enforce these non-prod controls:

- Outgoing email suppressed, intercepted, or redirected
- Payment / marketplace / shipment / finance side effects disabled or sandboxed
- Cron jobs disabled by default or explicitly allowlisted
- Web indexing disabled for non-prod
- Production credentials never copied into dev without re-scoping
- External callback targets re-pointed to test endpoints where possible

## Promotion Model

```text
feature -> validated branch -> dev (odoo_dev)
dev -> release candidate -> staging (odoo_staging)
staging -> approved promotion -> production (odoo)
```

Promotion requirements:

- Build succeeds
- Runtime contract checks pass
- Addon discovery and dependency checks pass
- Release evidence exists
- Staging validation complete
- Rollback plan recorded

## Backup / Restore Model

| Environment | Backup | Retention | Restore |
|-------------|--------|-----------|---------|
| production (`odoo`) | Daily + PITR | 30 days | Proven restore path |
| staging (`odoo_staging`) | Daily | 7 days | Repeatable refresh from prod |
| dev (`odoo_dev`) | None | Disposable | Rebuild from seed/fixtures |

## Evidence Model

Every release candidate must have an evidence pack including:

- Commit SHA
- Pipeline run ID
- Dependency summary
- Addon inventory
- Test summary
- Migration / upgrade summary if applicable
- Staging validation result
- Production deployment result
- Rollback reference
- Operator / approver identity

## Repo Ownership

| Owner | Scope |
|-------|-------|
| `infra` | Target-state doctrine, environment/promotion doctrine, DNS/identity/backup/ops runbooks, machine-readable platform SSOT |
| `odoo` | Runtime contract, addon/dependency behavior, runtime CI enforcement, release evidence tied to code/runtime |
| `agents` | Copilot / Foundry runtime contracts only |
| `web` | Public experience surfaces only |

## Exit Criteria

This target state is considered materially implemented when:

- Branch-to-environment promotion is deterministic
- Staging refresh from neutralized production data is proven
- Non-prod safety controls are active
- Runtime shell/logs/metrics are available
- Dependency/addon contract is CI-enforced
- Backup/restore evidence exists
- Release evidence packs are consistently generated
