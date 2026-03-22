# Test Strategy Target State

> **Status**: Live baseline
> **Date**: 2026-03-22
> **Purpose**: Defines the canonical test strategy for the InsightPulse AI platform. All test tooling, frameworks, and processes must align to this document. It governs repo-native automation, Azure Pipelines CI/CD gates, Databricks data validation, and Azure Test Plans UAT.

---

## One-Line Target

```text
Azure Test Plans = bounded requirement-traceability and manual/UAT surface.
Repo-native tests + Azure Pipelines = primary automated testing and release gate.
Databricks validation = analytical control tower integrity.
```

---

## Core Principles

| # | Principle | Rationale |
|---|-----------|-----------|
| 1 | **Tests live next to the code they validate** | Colocation ensures tests are maintained with the code, never drift. |
| 2 | **CI runs on every PR; merge requires green** | No untested code reaches the main branch. |
| 3 | **Test databases are disposable** | `test_<module>` databases are created per run, never shared, never reused. |
| 4 | **Classify failures before reporting** | Raw pass/fail without classification (env issue, migration gap, real defect) is not actionable. See `.claude/rules/testing.md`. |
| 5 | **Evidence is mandatory** | Every test run produces evidence saved to `docs/evidence/<YYYYMMDD-HHMM>/<scope>/`. No claim without proof. |
| 6 | **Azure Test Plans is bounded** | Test Plans is for manual UAT, requirement traceability, and release signoff only. It is not the primary automation framework. |
| 7 | **Databricks validation is data-plane native** | Data quality assertions run where the data lives (SQL Statement API, DLT expectations), not in external test harnesses. |
| 8 | **No test duplication across lanes** | Each test exists in exactly one lane. Repo-native tests are not duplicated as Azure Test Plans cases. Databricks assertions are not duplicated as pytest unit tests. |

---

## Scope

| In scope | Out of scope |
|----------|-------------|
| Odoo CE 19 module tests (`odoo-bin --test-enable`) | Enterprise module testing |
| Python library tests (`pytest`) | Third-party SaaS integration tests |
| Frontend / E2E tests (Playwright) | Load / performance testing (deferred) |
| Databricks bronze/silver/gold assertions | Fabric mirroring validation (deferred) |
| Infrastructure validation (Bicep `what-if`) | Penetration testing (separate engagement) |
| Azure Test Plans manual UAT | Azure Test Plans as primary automation |
| Azure Pipelines CI/CD gates | GitHub Actions CI (deprecated) |

---

## Canonical Test Layers

### Layer 1: Repo-Native Tests

Tests authored in the repository, executed locally and in CI.

| Stack | Framework | Runner | Location |
|-------|-----------|--------|----------|
| Odoo modules | `odoo-bin --test-enable` | Devcontainer / Azure Pipelines | `addons/ipai/*/tests/` |
| Python libraries | `pytest` | Local / Azure Pipelines | `*/tests/` |
| Frontend / E2E | Playwright | VS Code Testing / Azure Pipelines | `web/apps/*/tests/` |
| Databricks transforms | `pytest` (local mode) | Local / Azure Pipelines | `databricks/bundles/*/tests/` |
| Infrastructure | Bicep `what-if` / Terraform `plan` | Azure Pipelines | `infra/azure/` |

**Rules**:
- Tests live next to the code they validate
- CI runs on every PR; merge requires green
- Test databases are disposable (`test_<module>`) and never shared
- Classify failures per `.claude/rules/testing.md` before reporting
- Evidence saved to `docs/evidence/<YYYYMMDD-HHMM>/<scope>/`

### Layer 2: Azure Pipelines CI/CD

Azure Pipelines is the **execution and gate surface** for repo automation:

- Runs repo-native tests as pipeline tasks
- Enforces environment checks and approvals for promotion
- Reports test results as pipeline artifacts
- Does **not** author or manage test cases — that stays in code
- Publishes test results via `PublishTestResults@2` task

**Pipeline structure**:

| Pipeline | Trigger | Tests executed |
|----------|---------|---------------|
| `ci-odoo.yml` | PR to main | Odoo module tests, Python lint, manifest validation |
| `ci-web.yml` | PR to main | Playwright E2E, TypeScript typecheck |
| `ci-databricks.yml` | PR to main | `databricks bundle validate`, pytest seed tests |
| `deploy-*.yml` | Merge to main | Environment promotion gates, smoke tests |

### Layer 3: Databricks Validation

Validation of the Databricks analytical control tower: bronze -> silver -> gold mart integrity.

| Layer | Validation | Location |
|-------|-----------|----------|
| Bronze seed | FK consistency, GL balance | `databricks/bundles/foundation_python/tests/test_seed_*.py` |
| Silver conform | Row count parity, type correctness | `databricks/bundles/foundation_python/tests/` |
| Gold marts | Row counts, scenario assertions, rollup correctness | `e2e_assertions.py` (SQL Statement API) |
| Bundle structure | `databricks bundle validate` | All 3 bundles |

**Execution model**:

| Context | How |
|---------|-----|
| Local dev | `pytest` against seed fixtures (no cluster required) |
| CI | Azure Pipelines task with `AzureCLI@2` + Databricks auth |
| E2E on cluster | `e2e_assertions.py` via SQL Statement API against live warehouse |

**Current gold mart assertions (8 checks)**:

1. `row_count:gold.project_profitability` = 3
2. `row_count:gold.project_budget_vs_actual` = 9
3. `row_count:gold.expense_liquidation_health` = 5
4. `row_count:gold.ap_ar_cash_summary` = 11
5. `row_count:gold.policy_compliance_scorecard` = 4
6. `row_count:gold.portfolio_financial_health` = 1
7. `project_scenarios` — Alpha/Beta/Gamma budget, actual, margin checks
8. `expense_liquidation` — row count validation

### Layer 4: Azure Test Plans

Bounded acceptance-testing and requirement-traceability surface. Not the primary automation framework.

**Use it for**:
- Manual UAT and business validation
- Requirement-linked acceptance tests
- Release signoff evidence
- Cross-functional validation tied to backlog items

**Do not use it for**:
- Primary automated test authoring
- Replacing repo-native test frameworks
- Replacing CI test execution in Azure Pipelines

**Suite policy**:

| Suite type | When to use |
|-----------|-------------|
| Requirement-based | When end-to-end traceability to backlog items is required |
| Static | Ad hoc grouping where traceability is not the primary need |
| Query-based | Dynamic test case selection by criteria |

Requirement-based suites are the **only** type that support end-to-end requirement traceability.

**Access policy**:

| Access level | Role |
|-------------|------|
| Basic + Test Plans | Plan/suite/test-case authors and test managers |
| Basic | Execution and reporting users |
| Stakeholder | Feedback-only users (browser extension, no portal) |

**Runner policy**:
- Prefer the **web-based test runner** for manual testing
- Do not build new dependencies on the retiring Windows Test Runner client

**Priority acceptance packs**:

| Pack | Backlog linkage | Frequency |
|------|----------------|-----------|
| Finance PPM dashboard acceptance | Finance PPM epic | Per release |
| Budget vs actual validation | Databricks gold mart stories | Per data refresh |
| Odoo finance/expense acceptance | Odoo finance epic | Per release |
| Cross-repo release signoff | Release milestone | Per release |
| Odoo critical business workflows | Operations epic | Per release |

---

## Test Ownership by Plane

Each Plane project owns its test surface. Test ownership follows code ownership.

| Plane project | Test framework | Test location | CI pipeline | UAT pack |
|--------------|---------------|---------------|-------------|----------|
| **Odoo** | `odoo-bin --test-enable`, `pytest` | `addons/ipai/*/tests/` | `ci-odoo.yml` | Odoo finance/expense acceptance |
| **Web** | Playwright, TypeScript typecheck | `web/apps/*/tests/` | `ci-web.yml` | — |
| **Platform** | `pytest`, Bicep `what-if` | `platform/*/tests/`, `infra/azure/` | `ci-platform.yml` | Cross-repo release signoff |
| **Data-intelligence** | `pytest`, SQL assertions, `databricks bundle validate` | `databricks/bundles/*/tests/` | `ci-databricks.yml` | Budget vs actual validation |
| **Agents** | `pytest` | `agents/*/tests/` | `ci-agents.yml` | — |
| **Infra** | Bicep `what-if`, Terraform `plan` | `infra/azure/`, `infra/terraform/` | `deploy-*.yml` | — |

**Rules**:
- Each project maintains its own test suite
- Cross-project integration tests live in the consuming project
- Test ownership transfers with code ownership during refactors

---

## Canonical Test Flow

### PR flow (pre-merge)

```
Developer pushes branch
       │
       ▼
Azure Pipelines CI triggers
       │
       ├── Lint (flake8, eslint, yamllint)
       ├── Typecheck (mypy, tsc)
       ├── Unit tests (pytest, odoo --test-enable)
       ├── Manifest validation (addons.manifest.yaml)
       ├── Databricks bundle validate
       └── Playwright E2E (if web changes)
       │
       ▼
All green? ──► PR eligible for review + merge
Any red?   ──► Classify failure, fix, re-push
```

### Post-merge flow

```
Merge to main
       │
       ▼
Azure Pipelines deploy triggers
       │
       ├── Build container image
       ├── Push to ACR
       ├── Deploy to dev environment
       ├── Smoke tests against dev
       └── Databricks E2E assertions (if data changes)
       │
       ▼
All green? ──► Promote to staging (manual approval gate)
Any red?   ──► Block promotion, alert, investigate
```

### Environment deployment flow

```
Staging promotion approved
       │
       ▼
Azure Pipelines staging deploy
       │
       ├── Deploy to staging
       ├── Smoke tests against staging
       ├── Azure Test Plans UAT execution (manual)
       └── Release signoff evidence captured
       │
       ▼
All passed? ──► Promote to production (manual approval gate)
Any failed? ──► Block, triage, retest
```

---

## Databricks-Specific Target Model

### Test pyramid

```
         ┌────────────┐
         │   E2E      │  SQL Statement API assertions
         │  (8 checks)│  against live warehouse
         ├────────────┤
         │  Integration│  pytest with Databricks Connect
         │            │  against shared dev cluster
         ├────────────┤
         │   Unit     │  pytest against seed fixtures
         │            │  no cluster required
         └────────────┘
```

### DLT expectations (future)

When DLT pipelines are adopted, data quality expectations will be defined inline:

```python
@dlt.expect_or_drop("valid_amount", "amount > 0")
@dlt.expect("valid_date", "date IS NOT NULL")
```

These replace external assertion scripts for tables managed by DLT.

### Evidence artifacts

| Artifact | Location | Format |
|----------|----------|--------|
| Assertion results | `docs/evidence/<stamp>/databricks-*/assertion_evidence.json` | JSON |
| Load evidence | `docs/evidence/<stamp>/databricks-*/load_evidence.json` | JSON |
| Bundle validate | Pipeline artifact | Text log |

---

## Azure Test Plans Usage Model

### When to create a test plan

- A release milestone requires formal UAT signoff
- A backlog epic has acceptance criteria that cannot be automated
- Regulatory or compliance evidence requires manual verification with traceability

### When NOT to create a test plan

- The validation can be expressed as a repo-native test
- The check is already covered by CI pipeline assertions
- The test has no backlog item linkage (use ad hoc testing instead)

### Test plan lifecycle

```
Backlog item created (Boards)
       │
       ▼
Requirement-based suite created (Test Plans)
       │
       ▼
Test cases authored with steps + expected results
       │
       ▼
Test run executed (web-based runner)
       │
       ▼
Results linked back to backlog item
       │
       ▼
Release signoff evidence captured
```

---

## Evidence Model

All test evidence follows the canonical evidence pattern:

```
docs/evidence/<YYYYMMDD-HHMM>/<scope>/
├── logs/
│   ├── test_output.log
│   └── ci_pipeline.log
├── assertion_evidence.json    (Databricks)
├── load_evidence.json         (Databricks)
├── test_results.xml           (JUnit format from CI)
└── screenshots/               (Playwright / UAT)
```

**Rules**:
- Timestamp is Asia/Manila (UTC+08:00)
- Never claim "all tests pass" without citing the evidence path
- Evidence is derived proof, not SSOT — source of truth is the test code
- CI pipelines publish test results as pipeline artifacts in addition to evidence directory

---

## Target-State Matrix

| Dimension | Current state | Target state | Gap |
|-----------|--------------|-------------|-----|
| Odoo module tests | Partial coverage, manual runs | All `ipai_*` modules have `tests/` with CI | Medium |
| Playwright E2E | Not yet wired | Critical user flows covered | High |
| Databricks assertions | 8 gold mart checks, manual | CI-integrated via `AzureCLI@2` task | Low |
| Databricks DLT expectations | Not started | Inline expectations on all DLT tables | High |
| Azure Pipelines CI | GitHub Actions (deprecated) | Azure Pipelines as sole CI surface | Medium |
| Azure Test Plans | Not yet created | 5 priority acceptance packs | Medium |
| Test evidence | Ad hoc | Canonical evidence model for all runs | Low |
| Failure classification | Informal | Mandatory per `.claude/rules/testing.md` | Low |

---

## Anti-Patterns

| # | Anti-pattern | Why it is wrong | Correct approach |
|---|-------------|-----------------|------------------|
| 1 | Using Azure Test Plans as the primary automation framework | Test Plans is for manual UAT and traceability, not automation | Use repo-native frameworks for automated tests |
| 2 | Duplicating repo-native tests as Azure Test Plans test cases | Creates maintenance burden and drift | Each test exists in exactly one lane |
| 3 | Creating Azure Test Plans suites without backlog item linkage | Suites without traceability have no value over ad hoc testing | Use requirement-based suites linked to epics/stories |
| 4 | Using the retiring Windows Test Runner for new test plans | Microsoft is retiring the desktop client | Use the web-based test runner |
| 5 | Running Databricks validation only through the UI with no CI parity | Manual-only validation cannot gate releases | Wire assertions into Azure Pipelines via `AzureCLI@2` |
| 6 | Treating pipeline green as sufficient without acceptance signoff | CI tests cover code quality, not business acceptance | Release-gated features require UAT signoff via Test Plans |
| 7 | Claiming "all tests pass" without evidence artifacts | Unsubstantiated claims are not actionable | Cite evidence path or log file for every claim |
| 8 | Running tests against shared databases (`odoo_dev`, `odoo`) | Shared databases cause flaky tests and data pollution | Use disposable `test_<module>` databases per run |

---

## Immediate Target Actions

| # | Action | Owner | Lane | Priority |
|---|--------|-------|------|----------|
| 1 | Wire `ci-odoo.yml` pipeline with `odoo-bin --test-enable` for all `ipai_*` modules | Odoo | Repo-native | P0 |
| 2 | Create `ci-databricks.yml` pipeline with `databricks bundle validate` + seed pytest | Data-intelligence | Databricks | P0 |
| 3 | Create first Azure Test Plans plan with Finance PPM acceptance pack | Platform | Test Plans | P1 |
| 4 | Add Playwright E2E for Odoo login + copilot systray + finance dashboard | Web | Repo-native | P1 |
| 5 | Wire `e2e_assertions.py` into Azure Pipelines via `AzureCLI@2` task | Data-intelligence | Databricks | P1 |
| 6 | Add `tests/` directories to all `ipai_*` modules missing them | Odoo | Repo-native | P2 |
| 7 | Create Budget vs Actual acceptance pack in Azure Test Plans | Data-intelligence | Test Plans | P2 |
| 8 | Establish canonical evidence model with CI artifact publishing | Platform | All | P2 |

---

## How the Lanes Connect

```
┌──────────────────────────────────────────────────────────────┐
│                    Azure DevOps Boards                        │
│              (Epics, Features, User Stories)                  │
└──────────┬───────────────────────────────────┬───────────────┘
           │                                   │
           │ requirement linkage               │ work item gates
           ▼                                   ▼
┌─────────────────────┐            ┌─────────────────────────┐
│  Azure Test Plans   │            │   Azure Pipelines       │
│  (Manual UAT)       │            │   (CI/CD + gates)       │
│                     │            │                         │
│  requirement-based  │            │  ┌─────────────────┐   │
│  suites → runs →    │            │  │ Repo automation  │   │
│  results → evidence │            │  │ (pytest, Playwright, │
│                     │            │  │  odoo --test-enable) ││
└─────────────────────┘            │  └─────────────────┘   │
                                   │  ┌─────────────────┐   │
                                   │  │ Databricks E2E  │   │
                                   │  │ (AzureCLI@2 +   │   │
                                   │  │  SQL assertions) │   │
                                   │  └─────────────────┘   │
                                   └─────────────────────────┘
```

- **Boards** provides the requirement/epic context
- **Test Plans** provides traceability from requirements to manual acceptance results
- **Pipelines** executes automated tests and enforces promotion gates
- Repo code and Databricks bundles are the **source of truth** for all automated validation

---

## Definition of Done

A feature is test-complete when:

- [ ] All repo-native tests pass in CI (Azure Pipelines green)
- [ ] Failure classification applied to any failures per `.claude/rules/testing.md`
- [ ] Evidence artifacts committed to `docs/evidence/<YYYYMMDD-HHMM>/<scope>/`
- [ ] Databricks assertions pass (if data-plane changes are involved)
- [ ] Azure Test Plans UAT executed and passed (if release-gated feature)
- [ ] Test results linked to backlog items in Azure DevOps Boards
- [ ] No test duplication across lanes

---

*Last updated: 2026-03-22*
