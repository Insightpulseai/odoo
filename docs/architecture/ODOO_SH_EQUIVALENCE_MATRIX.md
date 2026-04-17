# Odoo.sh Equivalence Matrix for Azure

## Purpose

Define the minimum Azure-native operating model required to reproduce the important platform guarantees of Odoo.sh for a self-hosted Odoo ERP deployment.

This document does **not** attempt to replicate the Odoo.sh product UX. It maps the operational guarantees that matter.

## Matrix

| Odoo.sh capability | What it means on Odoo.sh | Azure equivalent | Required now | Later | Owning repo |
|---|---|---|---:|---:|---|
| GitHub integration | every commit / PR / merge triggers build lifecycle | GitHub Actions or Azure Pipelines driving image build + deploy | Yes |  | `odoo` + `.github` + `infra` |
| Clear logs | real-time logs in browser | ACA logs + Azure Monitor / Log Analytics | Yes |  | `infra` |
| Web shell | shell access to build/runtime containers | controlled ACA exec / diagnostics shell | Yes |  | `infra` + `odoo` |
| Module dependencies | Python deps + extra addons handled by platform | deterministic Docker build + addon path contract | Yes |  | `odoo` |
| Continuous integration | automated tests on branches | GitHub Actions / Azure Pipelines CI | Yes |  | `.github` + `odoo` |
| SSH | connect to container/build | controlled admin/ops access pattern; not ad hoc mutation | Yes |  | `infra` |
| Mail catcher | outbound mail disabled/captured on non-prod | staging/dev mail suppression or catcher | Yes |  | `infra` + `odoo` |
| Staging branches | production-like test builds | `odoo-staging` full topology (web+worker+cron) | Yes |  | `infra` + `odoo` |
| Manual test builds | feature-branch deploys for testing | optional non-prod deploy lane / dev environment |  | Yes | `infra` + `odoo` |
| Community modules | easy addon inclusion | OCA layer in addons path / image build / hydration workflow | Yes |  | `odoo` |
| Staging to production promotion | controlled pre-prod to prod promotion | `odoo-staging` -> `odoo-production` gated release flow | Yes |  | `infra` + `.github` + `odoo` |
| High availability / managed ops | Odoo.sh manages servers/ops | Azure-managed runtime posture + operational runbooks |  | Yes | `infra` |
| Incremental backups | daily managed backups | PostgreSQL Flexible Server backups + PITR + restore drill | Yes |  | `infra` |
| Mail servers setup | mail configured by platform | Key Vault + SMTP config + environment-specific controls | Yes |  | `infra` + `odoo` |
| Great performance | tuned Odoo/Postgres runtime | right-sized ACA + PG + image/runtime tuning | Yes |  | `infra` + `odoo` |
| Monitoring | availability/performance visibility | Azure Monitor / Log Analytics / health checks | Yes |  | `infra` |
| Instant recovery | easy restore from backups | documented restore path + verified PITR / restore procedure | Yes |  | `infra` + `docs` |
| DNS | custom prod domain + dev subdomains | custom domain + HTTPS for `erp.insightpulseai.com` | Yes |  | `infra` |
| Security | managed hosting security posture | Key Vault, secrets discipline, HTTPS, backup/restore, controlled access | Yes |  | `infra` + `platform` |

## Minimum Azure runtime topology

The minimum Azure runtime topology that functionally replaces Odoo.sh for ERP is:

- `odoo-web`
- `odoo-worker`
- `odoo-cron`
- Azure Database for PostgreSQL Flexible Server
- Azure Container Registry
- Azure Key Vault
- DNS + HTTPS for `erp.insightpulseai.com`

## Notes

### Non-negotiables
A deployment is not complete if only the web app exists.

Staging and production should model the full topology:
- web
- worker
- cron

### Staging safety controls
To approximate Odoo.sh non-prod safety, staging/dev should explicitly enforce:
- outbound mail suppression/capture
- sandboxed or disabled payment providers
- disabled or sanitized external integrations
- production-like testing without live destructive side effects

### What Azure does not give automatically
Unlike Odoo.sh, Azure does not automatically provide:
- Odoo-aware build lifecycle
- addon dependency handling
- staging neutralization behavior
- mail catcher behavior
- Odoo-specific safe defaults

These must be implemented deliberately.

## Bottom line

To "be Odoo.sh on Azure", replicate the guarantees:

1. reproducible image build
2. web + worker + cron topology
3. managed Postgres with proven restore path
4. logs + controlled shell access
5. safe staging/dev behavior
6. correct HTTPS/domain/proxy handling
7. Git-driven deploy lifecycle
