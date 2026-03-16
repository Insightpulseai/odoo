# GitHub Actions Workflow Taxonomy

> **Audited**: 2026-03-08 | **Total**: 362 workflows | **Lines**: 47,203 YAML
> **Reusable workflows**: 2 (0.6%) — root cause of proliferation

---

## Family Distribution

| Family | Count | % | Target After Consolidation |
|--------|------:|--:|---------------------------|
| odoo-module-ci | 132 | 36.5% | ~15-20 |
| spec-policy-gate | 79 | 21.8% | ~5-8 |
| deploy-release | 40 | 11.0% | ~5-6 |
| agent-ai | 29 | 8.0% | ~5-8 |
| infrastructure | 20 | 5.5% | ~5 |
| security-scan | 18 | 5.0% | ~3 |
| docs-gen | 16 | 4.4% | ~3 |
| node-app-ci | 15 | 4.1% | ~3 |
| scheduled-maintenance | 7 | 1.9% | ~3 |
| python-lint | 3 | 0.8% | 1 |
| other | 2 | 0.6% | 1 |
| stub-or-empty | 1 | 0.3% | 0 |
| **TOTAL** | **362** | | **~50-60** |

## Trigger Distribution

| Trigger | Count |
|---------|------:|
| push | 268 |
| pull_request | 236 |
| workflow_dispatch | 199 |
| schedule | 46 |
| issues | 18 |
| release | 4 |
| workflow_run | 4 |
| workflow_call | 2 |

> **Impact**: Every push to main triggers up to 268 workflow runs.

## Top Duplicate Clusters (Priority Consolidation)

### DUP-1: Deploy Production (3 → 1)
- `deploy-prod.yml`, `deploy-production.yml`, `deploy-odoo-prod.yml`

### DUP-2: Deploy Staging (2 → 1)
- `deploy-stage.yml`, `deploy-staging.yml`

### DUP-3: Repo Structure (3 → 1)
- `repo-structure.yml`, `repo-structure-gate.yml`, `repo-structure-guard.yml`

### DUP-4: EE Parity (7 → 2)
- `build-odoo-ce19-ee-parity.yml`, `editions-parity-seed.yml`, `ee-parity-automation.yml`, `ee-parity-gate.yml`, `ee-parity-test-runner.yml`, `ee-parity-tests.yml`, `odoo-ee-parity-gate.yml`

### DUP-5: Parity Tier-0 (5 → 1)
- `parity-gate-tier0.yml`, `parity-governance-gate.yml`, `parity-targets-gate.yml`, `parity-tier0.yml`, `tier0-parity-gate.yml`

### DUP-6: Secrets Scanning (9 → 2)
- `codespaces-secret-guard.yml`, `secret-scan.yml`, `secrets-audit.yml`, `secrets-registry-guard.yml`, `secrets-registry-validate.yml`, `secrets-scan-gate.yml`, `secrets-usage-guard.yml`, `supabase-secrets-deploy.yml`, `validate-secrets-usage.yml`

### DUP-7: Odoo Module Install (6 → 2)
- `odoo-auto-upgrade.yml`, `odoo-azure-upgrade-evidence.yml`, `odoo-install-dry-run.yml`, `odoo-install-set-verify.yml`, `odoo-module-install-gate.yml`, `odoo-overlay-install.yml`

### DUP-8: Docs Gates (6 → 2)
- `docs-current-state-gate.yml`, `docs-drift-gate.yml`, `docs-refresh-gate.yml`, `ipai-doc-drift-gate.yml`, `no-cli-no-docker-gate.yml`, `odoo-docs-platform-gate.yml`

### DUP-9: Meta-Gates (4 → 1)
- `all-green-gates.yml`, `policy-gates.yml`, `ssot-gates.yml`, `stack-gates.yml`

## Deprecated Workflows (23 — delete candidates)

```
agent-skills-gate.yml
canonical-gate.yml
ci-runbot.yml
deploy-do-oca.yml
devcontainer-invariants.yml
docker-context-check.yml
domain-lint.yml
github-apps-ssot-guard.yml
github-auth-surface-contract.yml
github-auth-surface-guard.yml
mcp-ssot-guard.yml
module-gating.yml
naming-gate.yml
no-deprecated-repo-refs.yml
odoo-import-artifacts.yml
orphan-addons-gate.yml
policy-gates.yml
prod-odoo-modules.yml
provider-defaults-gate.yml
repo-structure-gate.yml
repo-top-level-guard.yml
ssot-surface-guard.yml
terraform-cloudflare-dns.yml
```

## Consolidation Strategy (3-Layer Model)

### Layer 1: Reusable Workflows (org-level)
Callable workflows in `Insightpulseai/.github/.github/workflows/`:
- `reusable-odoo-module-ci.yml` — lint, test, gate for ipai_* modules
- `reusable-node-ci.yml` — lint, typecheck, build for Node/TS apps
- `reusable-spec-gates.yml` — spec bundle structure validation
- `reusable-release.yml` — production deploy pipeline
- `reusable-security-scan.yml` — secrets + deps + SAST

### Layer 2: Workflow Templates (org-level)
Starter templates in `Insightpulseai/.github/workflow-templates/`:
- `odoo-module-ci.yml` + `.properties.json`
- `monorepo-node-ci.yml` + `.properties.json`
- `spec-policy-gates.yml` + `.properties.json`

### Layer 3: Repo Wrappers (repo-level)
Thin callers in `odoo/.github/workflows/`:
```yaml
jobs:
  ci:
    uses: Insightpulseai/.github/.github/workflows/reusable-odoo-module-ci.yml@main
    with:
      module_path: addons/ipai/ipai_finance_ppm
```

## Estimated Reduction

| Phase | Action | Workflows Removed |
|-------|--------|------------------:|
| 1 | Delete 23 deprecated | -23 |
| 2 | Collapse 9 duplicate clusters | -30 |
| 3 | Convert to reusable workflow callers | -50 |
| 4 | Matrix-based policy gates | -40 |
| **Total reduction** | | **~143** |
| **Remaining** | | **~219** |
