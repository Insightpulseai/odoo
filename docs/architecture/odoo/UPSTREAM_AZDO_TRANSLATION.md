# Odoo Upstream to Azure DevOps Translation

> Maps upstream Odoo CI/workflow intent to our five-pipeline Azure DevOps topology.
> GitHub Actions must NOT be reintroduced. This is a reference translation only.

---

## Translation Rule

Never copy upstream GitHub workflow YAML into this repo. Always translate into Azure DevOps intent:

- PR validation stage → `ci-validation`
- Packaging validation job → `ci-validation` Build stage
- Migration validation job → `ci-validation` Test stage
- Upgrade rehearsal stage → `runtime-delivery` Migrate stage
- Runtime smoke stage → `runtime-delivery` Smoke stage
- Docs/spec governance check → `ci-validation` Lint/SSOTValidation stage
- Quality governance scheduled run → `quality-governance`

---

## Translation Table

| Upstream Workflow Intent | Source Repo(s) | Why It Matters | AzDO Pipeline | AzDO Stage | Priority |
|--------------------------|---------------|----------------|---------------|------------|----------|
| **Python linting** (flake8, pylint-odoo, isort, black) | odoo/odoo, OCA/MQT | Catches syntax/style errors before tests | `ci-validation` | Lint | Must have |
| **JavaScript linting** (eslint for OWL) | odoo/odoo, odoo/owl | Frontend code quality | `ci-validation` | Lint | Should have |
| **Manifest validation** (__manifest__.py) | OCA/MQT | Malformed manifests cause silent failures | `ci-validation` | Lint | Must have |
| **YAML/template validation** | — | Catches pipeline YAML errors | `ci-validation` | ConfigValidation | Must have |
| **Docker image build** | odoo/docker | Validates runtime image builds | `ci-validation` | Build | Must have |
| **Python dependency resolution** | odoo/odoo | Catches dependency conflicts | `ci-validation` | Build | Should have |
| **Module install test** (--init --stop-after-init) | odoo/odoo, OCA/MQT | Validates clean module installation | `ci-validation` | Test | Must have |
| **Module upgrade test** (--update) | odoo/odoo, odoo/upgrade-util | Validates upgrades don't break data | `ci-validation` | Test | Should have |
| **Python unit tests** (TransactionCase) | odoo/odoo | Core business logic validation | `ci-validation` | Test | Must have |
| **JS unit tests** (QUnit/OWL) | odoo/odoo, odoo/owl | Frontend component validation | `ci-validation` | Test | Should have |
| **HTTP integration tests** (HttpCase) | odoo/odoo | E2E web controller validation | `ci-validation` | Test | Nice to have |
| **Security scanning** (SAST, deps, secrets) | — | OWASP top 10, CVEs, leaked secrets | `ci-validation` | Security | Must have |
| **SSOT consistency validation** | — | Ensures SSOT files are valid | `ci-validation` | SSOTValidation | Must have |
| **Documentation build** | odoo/documentation | Docs compile without errors | `ci-validation` | Lint | Nice to have |
| **Container image publish** | odoo/docker | Produces deployable artifacts | `runtime-delivery` | Build | Must have |
| **Database migration** | odoo/upgrade-util | Runs pre/post-migrate scripts | `runtime-delivery` | Migrate | Must have |
| **Runtime smoke validation** | — | Post-deploy health check | `runtime-delivery` | Smoke | Must have |
| **Load testing** (Locust) | odoo/OdooLocust | Performance regression detection | `quality-governance` | LoadTest | Should have |
| **AI/agent benchmark evals** | — | Quality gates for AI releases | `quality-governance` | BenchmarkEval | Must have |
| **Runbot CI orchestration** | odoo/runbot | — | *Ignored* | — | N/A |
| **Odoo.sh deployment** | odoo/odoosh | — | *Ignored* | — | N/A |

---

## Pipeline Coverage Summary

### `ci-validation` (PR validation)

Absorbs the majority of upstream CI intent:

| Stage | Upstream Patterns Absorbed |
|-------|---------------------------|
| Lint | Python linting, JS linting, manifest validation, docs build |
| ConfigValidation | YAML/template validation |
| Build | Docker image build, dependency resolution |
| Test | Module install, module upgrade, Python unit tests, JS tests, HTTP tests |
| Security | SAST, dependency scanning, secret detection |
| SSOTValidation | SSOT file consistency |

### `runtime-delivery` (build → deploy → smoke)

| Stage | Upstream Patterns Absorbed |
|-------|---------------------------|
| Build | Container image build and publish |
| Migrate | Database migration execution (upgrade-util patterns) |
| Smoke | Post-deploy health and route validation |

### `quality-governance` (non-release quality)

| Stage | Upstream Patterns Absorbed |
|-------|---------------------------|
| LoadTest | OdooLocust-style load testing |
| BenchmarkEval | AI/agent evaluations, regression scorecards |

### `platform-shared-delivery` and `stamp-delivery`

No direct upstream patterns. These are Azure-native infrastructure concerns with no Odoo upstream equivalent.

---

## What NOT to Adopt

| Upstream Pattern | Why Not |
|-----------------|---------|
| Runbot CI system | We use Azure DevOps, not a custom CI. Extract test topology concepts only. |
| Odoo.sh deployment patterns | We deploy to Azure Container Apps. |
| Upstream GitHub Actions YAML | GitHub Actions is decommissioned in our repo. |
| Enterprise-specific CI patterns | We are CE-only. |
| Odoo.com IAP integration tests | We do not use odoo.com IAP. |

---

## Related

- `ssot/odoo/upstream_reference_map.yaml` — machine-readable repo classification
- `ssot/odoo/upstream_ci_translation.yaml` — machine-readable CI intent mapping
- `docs/architecture/ODOO_UPSTREAM_REFERENCE_SURFACES.md` — repo-level reference guide
- `docs/architecture/AZDO_TARGET_PIPELINE_ARCHITECTURE.md` — target 5-pipeline topology
- `ssot/azure/azure_devops.yaml` — CI/CD authority declaration
