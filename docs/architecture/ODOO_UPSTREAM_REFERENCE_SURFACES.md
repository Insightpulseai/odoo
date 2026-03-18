# Odoo Upstream Reference Surfaces

> Classification of official Odoo repositories by engineering utility.
> These are **reference surfaces only** — not CI/CD sources, not submodule targets.

---

## Executive Summary

Official Odoo upstream repos contain valuable engineering patterns for runtime packaging, migration, testing, and module development. However, their CI/CD implementation (runbot, GitHub Actions) is not applicable to our Azure-native platform.

**Key findings:**
- **6 Tier 1 repos** directly inform current work: `odoo/odoo`, `odoo/docker`, `odoo/upgrade-util`, `odoo/documentation`, `odoo/runbot` (test topology only), `odoo/tutorials`
- **3 Tier 2 repos** are selectively useful: `odoo/owl`, `odoo/OdooLocust`, `odoo/design-themes`
- **Upstream CI intent** maps to 3 of our 5 Azure DevOps pipelines: `ci-validation` (most), `runtime-delivery`, `quality-governance`
- **No upstream patterns** map to `platform-shared-delivery` or `stamp-delivery` (Azure-native concerns)
- **GitHub Actions must not be reintroduced.** All useful upstream workflow intent is translated into Azure DevOps pipeline stages.

**Categories of upstream value:**
1. **Workflow intent** — what tests to run, what to lint, what to validate (→ `ci-validation`)
2. **Packaging/runtime** — Dockerfile patterns, entrypoint logic, dependency management (→ `runtime-delivery`)
3. **Migration/upgrade** — upgrade-util helpers, pre/post-migrate patterns (→ `runtime-delivery`)
4. **Testing/CI topology** — test class hierarchy, tagging, environment separation (→ `ci-validation`, `quality-governance`)
5. **Documentation authority** — ORM API, OWL reference, module spec (→ developer reference, no pipeline)

---

## Policy

1. **No upstream CI/CD adoption.** Do not copy GitHub Actions, Dockerfiles, or CI scripts from upstream repos into this repo. Our CI/CD authority is Azure DevOps (`ssot/azure/azure_devops.yaml`).
2. **Reference, not fork.** Read upstream for patterns, schemas, and API contracts. Do not fork or vendor upstream repos (except `vendor/odoo/` which is the CE runtime mirror).
3. **Translation rule.** If an upstream pattern is useful, translate it into our stack: Azure DevOps pipeline YAML, `scripts/ci/` shell scripts, or `addons/ipai/` module code. Never import verbatim.

---

## Tier 1 — Active Engineering Reference

High-value repos that directly inform current platform work.

| Repo | What We Use It For | Engineering Surface |
|------|--------------------|---------------------|
| [`odoo/odoo`](https://github.com/odoo/odoo) | CE runtime source, ORM API, core addon reference, upgrade migration scripts | `vendor/odoo/` (mirrored), module `_inherit` patterns, field/model API |
| [`odoo/docker`](https://github.com/odoo/docker) | Official Dockerfile patterns, entrypoint script, wait-for-psql logic | Reference for `odoo/Dockerfile`, `scripts/odoo/entrypoint.sh` |
| [`odoo/upgrade-util`](https://github.com/odoo/upgrade-util) | Migration script helpers (rename_field, rename_model, merge_module) | Pre/post-migrate patterns in `ipai_*` modules |
| [`odoo/documentation`](https://github.com/odoo/documentation) | Official API docs, OWL reference, RPC protocol spec | Developer reference for ORM, frontend, API integrations |
| [`odoo/runbot`](https://github.com/odoo/runbot) | Test topology concepts (tagging, env separation, matrix logic) | Test strategy patterns for `ci-validation` — do NOT adopt runbot itself |
| [`odoo/tutorials`](https://github.com/odoo/tutorials) | Canonical module development patterns, progressive examples | Module scaffold and onboarding reference |
| [`OCA/maintainer-quality-tools`](https://github.com/OCA/maintainer-quality-tools) | OCA linting rules, manifest checks, pylint plugin config | Reference for `scripts/ci/` lint stages, pre-commit config |
| [`OCA/maintainer-tools`](https://github.com/OCA/maintainer-tools) | `oca-port` migration tool, `setuptools-odoo`, copier templates | Porting workflow (`addons/oca/` 18.0→19.0), module scaffold |

---

## Tier 2 — Selective Reference

Useful for specific features or patterns. Consult when working in their domain.

| Repo | What We Use It For | When to Consult |
|------|--------------------|-----------------|
| [`odoo/upgrade`](https://github.com/odoo/upgrade) | Migration script patterns (rename fields, merge models, data transforms) | Writing `pre-migrate.py` / `post-migrate.py` in `ipai_*` modules |
| [`odoo/documentation`](https://github.com/odoo/documentation) | Official API docs, OWL component reference, RPC protocol spec | Implementing frontend widgets, JSON-RPC integrations, OWL components |
| [`odoo/design-themes`](https://github.com/odoo/design-themes) | Website theme structure, asset bundle patterns | Working on `ipai_web_branding` or website templates |
| [`OCA/server-tools`](https://github.com/OCA/server-tools) | `queue_job`, `sentry`, `base_technical_user`, `auditlog` patterns | Adding async job processing, error tracking, audit features |
| [`OCA/server-ux`](https://github.com/OCA/server-ux) | `date_range`, `base_import_security_group`, UX enhancement patterns | Improving admin/user experience in custom modules |
| [`OCA/account-financial-tools`](https://github.com/OCA/account-financial-tools) | `account_asset_management`, `mis_builder`, financial report patterns | Building `ipai_finance_ppm` and accounting features |
| [`OCA/account-financial-reporting`](https://github.com/OCA/account-financial-reporting) | Financial report templates, balance sheet / P&L patterns | Tax/BIR reporting, financial dashboards |
| [`OCA/rest-framework`](https://github.com/OCA/rest-framework) | `fastapi` module — canonical REST API surface for Odoo | Agent-to-Odoo API endpoints, external integrations |
| [`OCA/connector`](https://github.com/OCA/connector) | Connector framework patterns, sync job architecture | Building external system integrations (n8n, Slack, Azure) |
| [`OCA/web`](https://github.com/OCA/web) | `web_responsive`, `web_dialog_size`, frontend widget patterns | UI/UX improvements, responsive layout fixes |

---

## Ignore for Now

Repos with no current engineering value. Re-evaluate if scope changes.

| Repo | Why Ignored |
|------|-------------|
| `odoo/o-spreadsheet` | No spreadsheet features in current scope |
| `odoo/odoosh` | Odoo.sh-specific tooling — we use Azure, not Odoo.sh |
| `odoo/industry` | Vertical industry modules — not relevant to current platform |
| `OCA/l10n-*` (most) | Localization repos outside Philippines — not in scope |
| `OCA/vertical-*` | Vertical industry modules — evaluate only if entering specific vertical |
| `OCA/website-*` | Website/e-commerce modules — not in current product scope |
| `OCA/pos` | Point of Sale — not in scope |
| `OCA/stock-logistics-*` | Warehouse/logistics — not in current scope |

---

## Surface Mapping

How upstream patterns translate to our stack:

| Upstream Pattern | Our Translation | Location |
|-----------------|-----------------|----------|
| GitHub Actions workflow | Azure DevOps pipeline YAML | `.azure/pipelines/` |
| `Dockerfile` | Adapted Dockerfile with our entrypoint | `odoo/Dockerfile` |
| OCA `pre-commit-config.yaml` | AzDO `ci-validation` lint stage + local pre-commit | `.azure/pipelines/ci-cd.yml` lint stage |
| `oca-port` migration commands | Shell scripts wrapping oca-port | `scripts/odoo/` |
| OCA module test patterns | Devcontainer test scripts with disposable DBs | `scripts/ci/run_odoo_tests.sh` |
| Odoo `runbot` CI | Not applicable — we do not use runbot | Azure DevOps `ci-validation` |
| Enterprise module patterns | CE + OCA + `ipai_*` delta (never EE source) | `addons/ipai/` |

---

## Categories of Upstream Value

### Workflow Intent

Upstream repos contain CI workflows (GitHub Actions, runbot configs) that reveal **what** should be validated — not **how** to implement the CI.

| Intent | Source | Our AzDO Translation |
|--------|--------|----------------------|
| Python lint (flake8, pylint-odoo) | odoo/odoo, OCA/MQT | `ci-validation` → Lint stage |
| JS lint (eslint) | odoo/odoo, odoo/owl | `ci-validation` → Lint stage |
| Manifest validation | OCA/MQT | `ci-validation` → Lint stage |
| Module install smoke | odoo/odoo | `ci-validation` → Test stage |
| Module upgrade validation | odoo/odoo, odoo/upgrade-util | `ci-validation` → Test stage |
| Security scanning | — | `ci-validation` → Security stage |
| SSOT consistency | — | `ci-validation` → SSOTValidation stage |

**Do not copy workflow YAML.** Extract the validation intent and implement in AzDO.

### Packaging / Runtime

| Pattern | Source | Our Translation |
|---------|--------|-----------------|
| Multi-stage Dockerfile | odoo/docker | `odoo/Dockerfile` — adapted for ACA |
| `wait-for-psql.py` entrypoint | odoo/docker | `scripts/odoo/entrypoint.sh` |
| wkhtmltopdf installation | odoo/docker | Dockerfile RUN stage |
| `requirements.txt` baseline | odoo/odoo | Dependency management in Dockerfile |
| Runtime entrypoint flags | odoo/docker | Container command/args in ACA spec |

### Migration / Upgrade

| Pattern | Source | Our Translation |
|---------|--------|-----------------|
| `rename_field()`, `rename_model()` | odoo/upgrade-util | `ipai_*` pre/post-migrate scripts |
| `merge_module()` | odoo/upgrade-util | Module consolidation migrations |
| Version-stamped migration scripts | odoo/odoo | `migrations/` dirs in `ipai_*` modules |
| `--update` validation | odoo/odoo | `ci-validation` Test stage |

### Testing / CI Topology

| Pattern | Source | Our Translation |
|---------|--------|-----------------|
| `TransactionCase` / `SavepointCase` | odoo/odoo | Python unit tests in `ci-validation` |
| `HttpCase` (browser-based) | odoo/odoo | Integration tests (headless browser) |
| `@tagged()` test selection | odoo/odoo | Test matrix / selective test runs |
| `--test-enable --stop-after-init` | odoo/odoo | Module install smoke in `ci-validation` |
| Locust task patterns | odoo/OdooLocust | Load tests in `quality-governance` |
| OWL component tests | odoo/owl | Frontend tests in `ci-validation` |

### Documentation Authority

| Surface | Source | Our Use |
|---------|--------|---------|
| ORM API reference | odoo/documentation | Developer reference for `ipai_*` modules |
| OWL component docs | odoo/documentation | Frontend widget development |
| JSON-RPC protocol spec | odoo/documentation | External API integrations |
| Module manifest spec | odoo/documentation | `__manifest__.py` structure |
| Security model (ACL, rules) | odoo/documentation | `ir.model.access.csv` + record rules |
| Upgrade documentation | odoo/documentation | Version migration planning |

---

## Per-Repo Inspection Notes (Verified 2026-03-18)

Findings from direct GitHub API inspection of each upstream repo.

### `odoo/odoo` (Tier 1)

**`.github/`**: Contains only `ISSUE_TEMPLATE/` (bug form) and `PULL_REQUEST_TEMPLATE.md`. **No GitHub Actions workflows.** Odoo uses runbot for CI, not GitHub Actions.

**Packaging**: `setup/` contains `debinstall.sh`, `package.py`, `requirements-check.py` (validates Python deps against distro versions), RPM/DEB packaging scripts, and `odoo-wsgi.example.py`.

**Test topology**: `odoo/tests/` contains the full test framework:
- `common.py` — base test classes (`BaseCase`, `TransactionCase`, `HttpCase`, `SavepointCase`), ~80 imports, browser integration via websocket
- `tag_selector.py` — `TagsSelector` class: parses `[+-]tag/module:class.method[params]` spec for selective test runs. Supports include/exclude, file paths, parameterized tests
- `case.py`, `suite.py`, `loader.py`, `result.py` — full test orchestration
- Key insight: Odoo's test selection is tag-based (`@tagged('post_install', '-at_install')`) — translate to AzDO test stage filtering

**Issue template**: Structured YAML form with version checkboxes (17.0, 18.0, 19.0), reproduction steps, expected/current behavior.

### `odoo/docker` (Tier 1)

**Structure**: Version-branched (`17.0/`, `18.0/`, `19.0/`). Each contains exactly 4 files.

**`19.0/Dockerfile`**: Ubuntu Noble base, installs wkhtmltopdf (SHA-verified per arch), PostgreSQL client from PGDG repo, `pip install odoo` from nightly. Key patterns:
- Multi-arch support (`TARGETARCH` arg for amd64/arm64/ppc64le)
- `COPY ./entrypoint.sh /` and `COPY wait-for-psql.py /usr/local/bin/`
- Runs as non-root user `odoo` (uid 101)
- Exposes port 8069 (web) and 8072 (longpolling)

**`19.0/entrypoint.sh`**: Shell script that reads `PASSWORD_FILE` (Docker secrets support), extracts DB config from env vars with sensible defaults (`HOST=db`, `PORT=5432`, `USER=odoo`), checks `odoo.conf` for overrides, calls `wait-for-psql.py` before exec.

**`19.0/wait-for-psql.py`**: Polls PostgreSQL with timeout — pattern we should replicate.

**No `.github/`** directory — no GitHub Actions.

### `odoo/upgrade-util` (Tier 1)

**Structure**: `src/` (library code), `tools/` (development utilities), pre-commit config.

**`src/util/`** — 29 modules including:
- `fields.py` — field rename/remove/transform operations with SQL-level helpers
- `helpers.py` — `table_of_model()`, version gating (`version_between()`, `version_gte()`)
- `models.py`, `orm.py`, `records.py` — model-level migration helpers
- `domains.py` — domain expression adaptation
- `accounting.py`, `hr_payroll.py` — domain-specific migration helpers
- `modules.py` — module merge/rename/remove
- `pg.py` — PostgreSQL-level utilities
- `snippets.py` — website snippet migration
- `data.py`, `json.py` — data transformation helpers

**`tools/`**: `compile23.py` (Python 2/3 compat check), `generate-inherit.py`, `graph-upgrade-timing.py`, `fetch-release-notes-video-id.py`

**Pre-commit**: Uses `ruff` (linter + formatter), `typos` (spell check), `check-xml`, `check-yaml`, `end-of-file-fixer`, `trailing-whitespace`, `debug-statements`. Also has custom hook blocking `from odoo.upgrade` imports in test/`0.0.0` scripts.

**No GitHub Actions.** Quality enforced via pre-commit hooks.

### `odoo/documentation` (Tier 1)

**Structure**: Sphinx/RST-based. Key content areas:
- `content/developer/` — tutorials, howtos, API reference
- `content/administration/` — install, upgrade, maintenance
- `content/applications/` — functional docs per app
- `content/contributing/` — development standards, documentation standards, install from git

**`tests/`**: Has `main.py`, `requirements.txt`, and `checkers/` — documentation validation tests (link checking, RST syntax, etc.)

**Build system**: `Makefile` + `conf.py` (Sphinx config) + `requirements.txt` for doc build dependencies.

**No GitHub Actions.** Docs built by Odoo's internal systems.

### `odoo/runbot` (Tier 1 — test topology reference only)

**Structure**: Multiple Odoo modules — `runbot`, `runbot_builder`, `runbot_merge`, `runbot_cla`, `runbot_populate`.

**`runbot_builder/`** — reveals CI agent architecture:
- `builder.py` — `BuilderClient` class: manages Docker images, source cleanup, build scheduling, PostgreSQL connection monitoring
- `tester.py` — test execution orchestration
- `leader.py` — build queue leader election
- Key insight: runbot manages its own Docker image builds, test isolation, and nginx routing — concepts we handle at the AzDO/ACA layer instead

**`runbot/tests/`** — 15+ test files covering builds, branches, commits, Dockerfiles, config steps. Reveals test organization by concern.

**`runbot_merge/`** — merge bot logic (PR merging, forward-porting, CLA checks). Not applicable to us.

**Key takeaway**: Extract test topology concepts (per-build DB isolation, tagged test selection, Docker-based test environments) but do NOT adopt runbot itself.

### `odoo/tutorials` (Tier 1)

**Structure**: 6 tutorial modules — `awesome_clicker`, `awesome_dashboard`, `awesome_gallery`, `awesome_kanban`, `awesome_owl`, `website_airproof`. Progressive OWL/frontend learning examples.

**No CI, no `.github/`**. Pure reference material for module development patterns.

### `odoo/owl` (Tier 2)

**`.github/workflows/deploy.yml`**: Single GitHub Actions workflow — Node.js CI on PR to master:
- Matrix: Node 20.x, 22.x
- Steps: `npm ci`, `npm run test`, `npm run check-formatting`, `npm run lint`, `npm run build`
- **Translation**: OWL CI intent = "lint + format + test + build" → maps to `ci-validation` Lint + Test stages for frontend code

**Structure**: TypeScript source in `src/`, tests in `tests/`, docs in `doc/` and `docs/`, build via `rollup.config.js`.

### `odoo/OdooLocust` (Tier 2)

**Structure**: `src/OdooLocust/` contains:
- `OdooLocustUser.py` — Odoo-specific Locust user class with XML-RPC/JSON-RPC client
- `OdooTaskSet.py` — base task set with `model_name`, form/list/kanban field definitions, `_get_user_context()`
- `crm/` — CRM-specific load test tasks
- `samples/` — example configurations

**Test files**: `test.py`, `test_sale.py` at repo root — sale order load test examples.

**Key patterns for `quality-governance`**: Locust `@task` decorators, model-specific task sets, user session simulation, random data generation via `names` library.

### `odoo/design-themes` (Tier 2)

**Structure**: 30 website themes (`theme_anelusia`, `theme_bistro`, `theme_clean`, etc.) + `theme_common` (shared assets) + `test_themes` (test module).

**Pattern**: Each theme is a standalone Odoo module with `__manifest__.py`, SCSS, templates, and static assets. Useful reference only for `ipai_web_branding`.

---

## Anti-Patterns (Never Do)

1. **Do not copy upstream `.github/workflows/`** into this repo. GitHub Actions is decommissioned.
2. **Do not add upstream repos as git submodules** (except OCA repos under `addons/oca/` per existing convention).
3. **Do not fork `odoo/odoo`** for patches. Use `_inherit` overrides in `ipai_*` modules.
4. **Do not import upstream Dockerfiles verbatim.** Adapt patterns to our Azure Container Apps runtime.
5. **Do not reference `runbot` or Odoo.sh CI patterns** as architectural precedent. Our CI is Azure DevOps.

---

## Related

- `ssot/odoo/upstream_reference_map.yaml` — machine-readable repo classification
- `ssot/odoo/upstream_ci_translation.yaml` — machine-readable CI intent mapping
- `docs/architecture/ODOO_UPSTREAM_TO_AZDO_TRANSLATION.md` — translation table
- `ssot/azure/azure_devops.yaml` — CI/CD authority
- `docs/architecture/AZDO_TARGET_PIPELINE_ARCHITECTURE.md` — target pipeline topology
- `docs/architecture/GITHUB_ACTIONS_DECOMMISSION_2026-03-18.md` — GHA decommission record
- `ssot/repo/github_hygiene.yaml` — GitHub role definition
