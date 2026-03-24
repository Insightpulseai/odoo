# odoo-release-promotion

**Impact tier**: P1 -- Operational Readiness

## Purpose

Close the release promotion gap where no formal dev-to-staging-to-prod gate
process exists for Odoo module deployments. The benchmark audit found: no
staging environment verification procedure, no migration pre-check, no rollback
procedure, and no promotion gate between environments.

## When to Use

- Defining the promotion pipeline for Odoo module releases.
- Adding migration verification gates between environments.
- Implementing rollback procedures for failed deployments.
- Preparing for go-live with a repeatable release process.

## Required Evidence (inspect these repo paths first)

| Path | What to look for |
|------|-----------------|
| `infra/azure/odoo-runtime.bicep` | ACA app definitions per environment |
| `infra/ssot/azure/service-matrix.yaml` | Environment definitions |
| `infra/ssot/azure/resources.yaml` | ACA apps, PG servers per environment |
| `docs/runbooks/ODOO19_GO_LIVE_CHECKLIST.md` | Deployment/promotion line items |
| `docs/audits/ODOO_AZURE_ENTERPRISE_BENCHMARK.md` | Release process gap row |
| `addons/ipai/` | Module manifests with version numbers |

## Microsoft Learn MCP Usage

Run at least these three queries:

1. `microsoft_docs_search("Azure Container Apps revision management blue green deployment")`
   -- retrieves ACA revision-based deployment strategies.
2. `microsoft_docs_search("Azure DevOps pipeline environment approval gates")`
   -- retrieves approval gate patterns for multi-environment promotion.
3. `microsoft_docs_search("Azure Container Apps rollback previous revision")`
   -- retrieves rollback mechanics for ACA revisions.

Optional:

4. `microsoft_code_sample_search("azure devops pipeline approval gate yaml", language="yaml")`
5. `microsoft_docs_fetch("https://learn.microsoft.com/en-us/azure/container-apps/revisions-manage")`

## Workflow

1. **Inspect repo** -- Read ACA Bicep for environment separation. Check if
   staging ACA apps exist. Read module manifests for version conventions.
   Check for any existing promotion scripts.
2. **Query MCP** -- Run the three searches. Capture revision management
   commands, approval gate YAML, rollback procedure.
3. **Compare** -- Identify: (a) Do separate staging ACA apps exist? (b) Is
   there a promotion gate (manual approval or automated test)? (c) Is there
   a migration verification step? (d) Is there a rollback procedure?
4. **Patch** -- Create:
   - `docs/runbooks/ODOO_RELEASE_PROMOTION.md` with the full promotion
     pipeline: dev -> staging -> prod.
   - Migration verification script or checklist (run `odoo-bin -u <module>
     --stop-after-init` on staging before prod).
   - Rollback procedure using ACA revision activation.
   - Update go-live checklist with promotion gate items.
5. **Verify** -- Promotion runbook exists with concrete commands. Migration
   verification step is documented. Rollback procedure is documented with
   specific ACA CLI commands.

## Outputs

| File | Change |
|------|--------|
| `docs/runbooks/ODOO_RELEASE_PROMOTION.md` | Full promotion pipeline (new) |
| `docs/runbooks/ODOO19_GO_LIVE_CHECKLIST.md` | Promotion gate line items |
| `infra/azure/odoo-runtime.bicep` | Staging ACA apps if missing |
| `docs/evidence/<stamp>/odoo-release-promotion/` | Runbook, MCP excerpts |

## Completion Criteria

- [ ] Promotion runbook defines 3 environments: dev, staging, prod.
- [ ] Each promotion step has a gate (test pass, manual approval, or health check).
- [ ] Migration verification (`odoo-bin -u <module> --stop-after-init`) is a
      documented gate before production promotion.
- [ ] Rollback procedure uses ACA revision activation with specific CLI commands.
- [ ] Go-live checklist references the promotion runbook.
- [ ] Evidence directory contains the runbook and MCP excerpts.
