# Odoo Upstream Adoption Backlog

> Bridge from upstream reference research to implementation.
> Each item maps an upstream pattern to a concrete Azure DevOps pipeline action.

---

## Runtime Contract Items

| # | Upstream Pattern | Source | Target Pipeline | Target Stage | Status |
|---|-----------------|--------|-----------------|--------------|--------|
| R1 | Dockerfile multi-arch build (amd64/arm64) | odoo/docker `19.0/Dockerfile` | runtime-delivery | Build | Not started |
| R2 | `wait-for-psql.py` readiness probe | odoo/docker `19.0/wait-for-psql.py` | runtime-delivery | Deploy | Not started |
| R3 | Entrypoint DB config from env vars | odoo/docker `19.0/entrypoint.sh` | runtime-delivery | Deploy | Partial — adapted |
| R4 | Non-root runtime user (uid 101) | odoo/docker `19.0/Dockerfile` | runtime-delivery | Build | Not started |
| R5 | wkhtmltopdf SHA-verified install | odoo/docker `19.0/Dockerfile` | runtime-delivery | Build | Existing — verify |

## Migration / Upgrade Items

| # | Upstream Pattern | Source | Target Pipeline | Target Stage | Status |
|---|-----------------|--------|-----------------|--------------|--------|
| M1 | `rename_field()` / `rename_model()` helpers | odoo/upgrade-util `src/util/fields.py` | runtime-delivery | Migrate | Available — use as needed |
| M2 | `merge_module()` for consolidation | odoo/upgrade-util `src/util/modules.py` | runtime-delivery | Migrate | Available — use as needed |
| M3 | `version_between()` / `version_gte()` guards | odoo/upgrade-util `src/util/helpers.py` | ci-validation | Test | Available — use as needed |
| M4 | Domain expression adaptation | odoo/upgrade-util `src/util/domains.py` | runtime-delivery | Migrate | Available — use as needed |
| M5 | `--update` validation in CI | odoo/odoo | ci-validation | Test | Not started |

## Test Topology Items

| # | Upstream Pattern | Source | Target Pipeline | Target Stage | Status |
|---|-----------------|--------|-----------------|--------------|--------|
| T1 | `TransactionCase` / `SavepointCase` unit tests | odoo/odoo `odoo/tests/common.py` | ci-validation | Test | Partial — module tests exist |
| T2 | `@tagged()` test selection and filtering | odoo/odoo `odoo/tests/tag_selector.py` | ci-validation | Test | Not started |
| T3 | `--test-enable --stop-after-init` smoke | odoo/odoo | ci-validation | Test | Existing — verify CI integration |
| T4 | `HttpCase` browser-based integration tests | odoo/odoo `odoo/tests/common.py` | ci-validation | Test | Not started |
| T5 | OWL component test patterns | odoo/owl `tests/` | ci-validation | Test | Not started |
| T6 | Locust load test task sets | odoo/OdooLocust `src/OdooLocust/` | quality-governance | LoadTest | Not started |
| T7 | Per-build disposable DB isolation | odoo/runbot concept | ci-validation | Test | Existing — `test_<module>` pattern |

## Lint / Static Validation Items

| # | Upstream Pattern | Source | Target Pipeline | Target Stage | Status |
|---|-----------------|--------|-----------------|--------------|--------|
| L1 | `pylint-odoo` plugin | OCA/maintainer-quality-tools | ci-validation | Lint | Not started |
| L2 | `ruff` linter + formatter | odoo/upgrade-util `.pre-commit-config.yaml` | ci-validation | Lint | Not started |
| L3 | Manifest validation | OCA/maintainer-quality-tools | ci-validation | Lint | Not started |
| L4 | `check-xml` / `check-yaml` pre-commit | odoo/upgrade-util `.pre-commit-config.yaml` | ci-validation | ConfigValidation | Not started |
| L5 | `typos` spell check | odoo/upgrade-util `.pre-commit-config.yaml` | ci-validation | Lint | Not started |

## Documentation Authority Items

| # | Upstream Surface | Source | Our Use | Status |
|---|-----------------|--------|---------|--------|
| D1 | ORM API reference | odoo/documentation `content/developer/reference/` | Developer reference | Available |
| D2 | OWL component docs | odoo/documentation `content/developer/` | Frontend development | Available |
| D3 | Module manifest spec | odoo/documentation | `__manifest__.py` validation | Available |
| D4 | Upgrade documentation | odoo/documentation `content/administration/` | Migration planning | Available |
| D5 | Contributing standards | odoo/documentation `content/contributing/` | Code review standards | Available |

## Explicitly Ignored Upstream Items

| # | Upstream Pattern | Source | Why Ignored |
|---|-----------------|--------|-------------|
| X1 | Runbot CI system | odoo/runbot | We use Azure DevOps — extract concepts only |
| X2 | Odoo.sh deployment | odoo/odoosh | We deploy to Azure Container Apps |
| X3 | GitHub Actions workflows | odoo/owl `deploy.yml` | GHA decommissioned in our repo |
| X4 | Enterprise module patterns | odoo/enterprise | CE-only policy |
| X5 | Odoo.com IAP integrations | odoo/odoo | No IAP dependency policy |
| X6 | Spreadsheet component | odoo/o-spreadsheet | Not in current scope |
| X7 | Industry vertical modules | odoo/industry | Not in current scope |

---

## Priority Order

1. **L1-L4** (Lint) — lowest effort, highest CI signal improvement
2. **T1-T3** (Core test patterns) — validate existing module tests in CI
3. **R1-R2** (Runtime contract) — Dockerfile hardening
4. **M5** (Upgrade validation) — `--update` in CI
5. **T6** (Load testing) — quality-governance scheduled runs
6. **T4-T5** (Browser/OWL tests) — higher effort, lower priority

---

## Related

- `docs/architecture/ODOO_UPSTREAM_REFERENCE_SURFACES.md` — per-repo inspection notes
- `ssot/odoo/upstream_ci_translation.yaml` — machine-readable CI intent mapping
- `docs/architecture/AZDO_TARGET_PIPELINE_ARCHITECTURE.md` — target pipeline topology
- `spec/azure-devops-pipeline-baseline/prd.md` — pipeline baseline PRD
