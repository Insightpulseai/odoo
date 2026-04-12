---
name: pulser-odoo-deploy
description: Controlled deployment of Pulser for Odoo MVP to the existing Azure runtime — reuse existing infra, gate every rollout step
version: "1.0"
compatibility:
  hosts: [github-copilot, claude-code, codex-cli, cursor, gemini-cli]
tags: [deploy, odoo, azure, pulser, aca, release, rollout]
---

# pulser-odoo-deploy

**Impact tier**: P1 -- Operational Readiness

## Purpose

Guide the controlled deployment of Pulser for Odoo (addon: `ipai_odoo_copilot`
and its MVP companion modules) to the existing Azure runtime. This skill enforces
repo-first deployment discovery, reuses all existing infrastructure surfaces, and
gates every rollout step with a build-package-deploy-verify-evidence-rollback
sequence. No greenfield infra by default.

## When to Use

- Before executing any Pulser for Odoo release to dev, staging, or production.
- When module install or update order is unclear for the MVP release scope.
- When a deployment fails and rollback or evidence is required.
- Before adding any new Azure resource to the Pulser runtime.

## When Not to Use

- For Foundry agent registration or runtime config (use `pulser-odoo-foundry-runtime`).
- For architecture boundary decisions (use `pulser-odoo-architecture`).
- For modules outside the MVP release scope (see Inputs Expected below).

## Inputs Expected

- Committed, tested code in the repo (never deploy from local state).
- The target environment: `dev` / `staging` / `prod`.
- MVP release scope modules: `ipai_odoo_copilot`, `ipai_copilot_actions`,
  `ipai_ai_agent_sources`, `ipai_tax_intelligence`, `ipai_hr_expense_liquidation`,
  `ipai_expense_ops`, `ipai_expense_wiring`.

## Source Priority

1. Repo SSOT / `AGENTS.md` / release manifests / IaC before acting
2. Existing architecture anchor docs in repo (`docs/architecture/`, `docs/release/`)
3. Microsoft Learn MCP official documentation
4. Official Microsoft GitHub samples only when needed
5. Anything else only if absolutely necessary, clearly marked secondary

## Required Evidence (inspect these repo paths first)

| Path | What to look for |
|------|-----------------|
| `ssot/odoo/mvp_matrix.yaml` | MVP module list, install order, feature flags |
| `ssot/odoo/module_install_manifest.yaml` | Module dependencies, install/update sequence |
| `docs/release/RELEASE_OBJECTIVE.md` | Release scope, go/no-go criteria |
| `docs/release/MVP_SHIP_CHECKLIST.md` | Ship-readiness gates (Product, Correctness, Runtime, Safety, Evidence) |
| `ssot/azure/runtime_topology.yaml` | Existing ACA apps, PG server, KV, Front Door topology |
| `ssot/azure/stamp_topology.yaml` | Environment/stamp layout, VNET, origin group config |
| `scripts/odoo/` | Authoritative deploy/install/update shell scripts |
| `docker/` | Dockerfiles — base image, EXPOSE, HEALTHCHECK |
| `.github/workflows/deploy-*.yml` | CI/CD deploy workflow triggers and gates |

## Microsoft Learn MCP Usage

Run at least these queries:

1. `microsoft_docs_search("Azure Container Apps deploy revision update image")`
   -- retrieves `az containerapp update`, revision suffix strategy, traffic split.
2. `microsoft_docs_search("Azure Database for PostgreSQL Flexible Server migration online")`
   -- retrieves PG connection strings, migration validation, schema pre-check.
3. `microsoft_docs_search("Azure Key Vault managed identity secret retrieval Container Apps")`
   -- retrieves KV secret binding to ACA via managed identity, no hardcoded credentials.
4. `microsoft_docs_search("Azure Container Apps rollback revision activate traffic")`
   -- retrieves rollback to previous revision: `az containerapp revision activate`.

## Microsoft Learn MCP Topic Keys

- azure_container_apps
- azure_database_for_postgresql_flexible_server
- key_vault
- managed_identity

## Workflow

1. **Inspect repo** -- Read `ssot/odoo/mvp_matrix.yaml` and
   `ssot/odoo/module_install_manifest.yaml`. Confirm which modules are in the
   MVP release scope and their install order. Read `ssot/azure/runtime_topology.yaml`
   to identify existing ACA apps (`ipai-odoo-dev-web`, `ipai-odoo-dev-worker`,
   `ipai-odoo-dev-cron`), the PG server (`pg-ipai-odoo`), Key Vault (`kv-ipai-dev`),
   and Front Door (`afd-ipai-dev`). Never create new resources without SSOT first.
2. **Query MCP** -- Run queries 1-4. Capture: ACA revision update command,
   rollback command, PG migration pre-check pattern, KV secret binding syntax.
3. **Compare** -- Identify gaps: (a) Missing module in install manifest for any
   MVP scope addon? (b) Any Dockerfile or compose change that modifies the base
   image without a vulnerability scan gate? (c) Any deploy workflow bypassing the
   ship-readiness checklist? (d) New Azure resource proposed without a SSOT entry?
4. **Patch** -- Update `ssot/odoo/module_install_manifest.yaml` with correct
   install order. Confirm `scripts/odoo/` scripts reference the runtime topology.
   Add any missing deploy gate to the workflow. Document rollback steps explicitly.
5. **Verify** -- Run `az containerapp show` for each app to confirm current
   revision and replica count. Confirm `odoo-bin -u <module> --stop-after-init`
   exits 0 on staging before prod gate. Confirm rollback revision is documented
   with its label.

## Output Contract

| Artifact | Location | Format |
|----------|----------|--------|
| Module install manifest (updated) | `ssot/odoo/module_install_manifest.yaml` | YAML |
| Deploy gate additions | `.github/workflows/deploy-*.yml` | YAML |
| Rollback plan | `docs/release/MVP_SHIP_CHECKLIST.md` | Markdown |
| Evidence pack | `docs/evidence/<stamp>/pulser-odoo-deploy/` | Logs + diffs |

## Safety and Guardrails

- Never deploy from local state. Only from committed, CI-passing revisions.
- Never create greenfield Azure resources without a SSOT entry and explicit approval.
- Never deploy modules outside the MVP release scope to production.
- Never bypass the ship-readiness checklist (5 gates: Product, Correctness, Runtime, Safety, Evidence).
- Rollback plan must be documented before any production promotion begins.
- Database names are runtime args: `odoo_dev` / `odoo_staging` / `odoo` -- never baked into Dockerfiles.
- No `from . import tests` in module root `__init__.py`. Odoo discovers tests via `tests/__init__.py`.
- Secrets via managed identity + Key Vault only. No hardcoded credentials in any file.

## Verification

- [ ] All MVP scope modules present in `ssot/odoo/module_install_manifest.yaml` with correct order.
- [ ] `odoo-bin -u <module> --stop-after-init` exits 0 on staging before prod gate.
- [ ] ACA apps show expected revision and `minReplicas >= 1` for Odoo web app.
- [ ] Rollback revision label documented and activation command confirmed via MCP.
- [ ] No new Azure resource deployed without a `ssot/azure/runtime_topology.yaml` entry.
- [ ] Ship-readiness checklist (5 gates) signed off before production promotion.
- [ ] Evidence directory contains deployment logs and rollback plan.

## Related Skills

- `pulser-odoo-architecture` -- architecture boundary decisions before deployment
- `pulser-odoo-foundry-runtime` -- Foundry agent registration alongside Odoo deploy
- `odoo-release-promotion` -- dev-to-staging-to-prod gate process
- `azure-aca-runtime` -- ACA scaling, probes, managed identity, revision management
- `odoo-image-supply-chain` -- ACR build, vuln scanning, image signing

## Completion Criteria

- [ ] MVP module install order confirmed in SSOT and matches deploy script sequence.
- [ ] All MVP scope modules installed and health-checked in the target environment.
- [ ] Rollback plan documented with specific ACA revision activation commands.
- [ ] No greenfield infrastructure created without SSOT classification and approval.
- [ ] Evidence directory contains install logs, health check output, and rollback plan.
- [ ] Ship-readiness checklist (5 gates) fully signed off.
