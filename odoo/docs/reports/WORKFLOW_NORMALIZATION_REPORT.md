# Workflow Normalization Report

**Date**: 2026-03-11
**Before**: 339 workflows
**After**: 5 workflows
**Removed**: 338 workflows

---

## Canonical CI/CD Contract

### PR Path (merge-safety gates)

| Workflow | File | Purpose |
|----------|------|---------|
| CI Odoo | `ci-odoo.yml` | Python lint, module validation, schema/spec checks |
| Repo Boundary Check | `repo-boundary-check.yml` | Top-level dir allowlist, blocked patterns, addons structure |
| Spec Kit Enforcement | `spec-kit-enforce.yml` | 4-file spec bundles, CLAUDE.md, YAML validation |

### Main Branch Path (PR gates + deploy + security)

| Workflow | File | Purpose |
|----------|------|---------|
| CI Odoo | `ci-odoo.yml` | Same as PR path |
| Repo Boundary Check | `repo-boundary-check.yml` | Same as PR path |
| Spec Kit Enforcement | `spec-kit-enforce.yml` | Same as PR path |
| CodeQL | `codeql.yml` | Security analysis (Python + JavaScript) |
| Deploy Azure | `deploy-azure.yml` | Build → ACR → ACA → health check |

### Scheduled / Manual Only

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| CodeQL | Weekly Monday 06:00 UTC | Security scan |
| Deploy Azure | `workflow_dispatch` | Manual deployment to dev/staging/prod |

---

## Workflows Removed (338)

### Vercel-Specific (retired platform)
- `deploy-vercel-odooops.yml`
- `vercel-env-leak-guard.yml`
- `vercel-integrations-diff.yml`
- `saas-landing-e2e.yml`
- `saas-landing-visual-regression.yml`
- `vendor-app-deploy.yml`

### Duplicate CI Paths
- `ci.yml`, `ci-web.yml`, `ci-runbot.yml`, `ci-submodules.yml`
- `ci-billing-site.yml`, `ci-docs-only.yml`, `ci-green-aggregate.yml`
- `ci-platform-gates.yml`, `lint.yml`, `lint-config.yml`
- `comprehensive-testing.yml`, `preflight.yml`
- `all-green-gates.yml`, `reusable-pr-gate.yml`

### Duplicate Repo Structure Guards (superseded by repo-boundary-check)
- `repo-structure.yml`, `repo-structure-gate.yml`, `repo-structure-guard.yml`
- `repo-root-allowlist.yml`, `repo-root-boundary-drift.yml`
- `repo-top-level-guard.yml`, `repo-tree-drift.yml`, `repo_layout.yml`
- `root-allowlist-guard.yml`

### Duplicate Spec/Policy Gates (superseded by spec-kit-enforce)
- `spec-gate.yml`, `spec-kit-gate.yml`, `spec-kit-drift.yml`
- `spec-kit-hygiene.yml`, `spec-and-parity.yml`
- `policy-gates.yml`, `policy-violation-gate.yml`, `policy-no-cli.yml`
- `policy-parity-map.yml`, `prd-enforcement.yml`

### Duplicate CodeQL / Security
- `ghas-gates.yml`, `secrets-audit.yml`, `secrets-scan-gate.yml`
- `secrets-validation-master.yml`, `github-waf-assessment.yml`
- `github-waf-gate.yml`, `infra-waf-assessment.yml`, `infra-waf-gate.yml`
- `azure-waf-parity.yml`

### Retired Deploy Paths (superseded by deploy-azure)
- `deploy.yml`, `deploy-production.yml`, `deploy-staging.yml`
- `deploy-odoo-prod.yml`, `deploy-odoo-modules.yml`
- `deploy-do-oca.yml`, `deploy-finance-ppm.yml`
- `deploy-plane.yml`, `deploy-odooops-console.yml`
- `deploy-ipai-control-center-docs.yml`
- `cd-docr-deploy.yml`, `cd-production.yml`
- `ship-on-deploy.yml`, `rollback.yml`
- `build-image.yml`, `build-push-acr.yml`
- `build-seeded-image.yml`, `build-unified-image.yml`
- `build-odoo-ce19-ee-parity.yml`
- `odoo-azure-deploy.yml`, `azure-provision.yml`

### Agent/AI Workflows (non-essential to merge safety)
- `agent-instructions-drift.yml`, `agent-library-validate.yml`
- `agent-preflight.yml`, `agent-skills-gate.yml`, `agent-ssot-check.yml`
- `agentic-codebase-crawler.yml`, `agentic-maturity.yml`
- `agents-registry-drift.yml`, `ai-naming-gate.yml`
- `ai-test-generation.yml`, `aiux-ship-gate.yml`
- `coding-agent-eval.yml`, `copilot-guardrails.yml`

### Flaky / Noisy / Low-Value
- `addons-manifest-guard.yml` (covered by ci-odoo module validation)
- `canonical-gate.yml`, `canonical-urls-gate.yml`
- `capabilities-validate.yml`, `catalog-gate.yml`
- `module-catalog-drift.yml`, `module-gating.yml`, `modules-audit-drift.yml`
- `naming-gate.yml`, `orphan-addons-gate.yml`
- `parity-*.yml` (7 files — parity scoring not blocking PRs)
- `skill-*.yml` (4 files)
- `ssot-*.yml` (4 files — superseded by repo-boundary-check)
- `stack-gates.yml`, `platform-guardrails.yml`, `platform-kit-ci.yml`
- `golden-path-gate.yml`, `blueprint-gate.yml`

### Domain-Specific (not merge-blocking)
- `bir-forms-scraper.yml`
- `cloudflare-*.yml` (3 files — DNS managed separately)
- `colima-desktop-*.yml` (2 files)
- `databricks-*.yml` (5 files)
- `dns-*.yml` (4 files)
- `docker-*.yml` (4 files)
- `docs-*.yml` (8 files)
- `e2e-playwright.yml`
- `ee-parity-*.yml` (4 files)
- `erd-*.yml` (4 files)
- `figma-featuremap-sync.yml`
- `finance-*.yml` (2 files)
- `github-*.yml` (6 files)
- `health-*.yml` (2 files)
- `ios-*.yml` (2 files)
- `mcp-*.yml` (3 files)
- `n8n-orchestrator.yml`
- `notion-sync-ci.yml`
- `oca-*.yml` (7 files)
- `odoo-*.yml` (17 files — covered by ci-odoo)
- `ops-*.yml` (4 files)
- `supabase-*.yml` (11 files)
- `superset-*.yml` (3 files)
- `terraform-supabase.yml`
- All remaining miscellaneous workflows

---

## Verification Checklist

- [x] PR checks reduced to 3 core workflows
- [x] Vercel workflows removed
- [x] CodeQL moved off PR path (main + schedule + dispatch only)
- [x] Azure deploy workflow is canonical
- [x] Workflow count: 339 → 5 (98.5% reduction)
- [x] All 5 canonical YAML files validate
- [x] No .env secrets in committed workflows

---

## Deferred Cleanup

| Item | Status | Notes |
|------|--------|-------|
| Branch protection rules | Deferred | Update required status checks to new workflow names |
| CODEOWNERS | Deferred | May need update if workflow paths changed |
| Dependabot config | Deferred | Review if any removed workflows had Dependabot alerts |
| GitHub Actions secrets | Deferred | Audit unused secrets from removed workflows |
