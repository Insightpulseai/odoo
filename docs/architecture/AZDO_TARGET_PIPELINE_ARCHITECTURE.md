# Azure DevOps target pipeline architecture

## Architecture premise

The target platform is a multitenant SaaS architecture on Azure with:

- shared control plane
- selectively shared application/runtime plane
- tenant-aware data isolation
- deployment stamps for scale, isolation, region, or customer class when needed
- deployment rings and feature flags for progressive rollout

This follows Azure multitenant guidance:
- multitenancy does not require every component to be shared
- deployment stamps are the preferred scale/isolation pattern
- deployment rings and feature flags should be used for controlled rollout

## Pipeline topology

Use five top-level pipelines.

### 1. ci-validation

Purpose:
- PR validation only
- docs/spec/SSOT checks
- YAML/template validation
- Odoo unit/module tests that do not require private reachability
- benchmark smoke tests
- packaging and static analysis

Agent policy:
- hosted by default (`ubuntu-latest`)

### 2. platform-shared-delivery

Purpose:
- deploy shared control-plane and shared platform services

Scope:
- Front Door / WAF
- DNS/IaC
- Entra / identity wiring
- Key Vault
- shared observability
- shared service connections and shared config surfaces
- shared Databricks / Foundry / platform integration foundations where appropriate

Deployment model:
- deployment jobs
- environment approvals/checks
- no tenant-specific payloads mixed into this pipeline

### 3. stamp-delivery

Purpose:
- deploy or update one deployment stamp at a time

Scope:
- stamp-scoped infra
- stamp-scoped Odoo runtime
- stamp-scoped data plane resources
- stamp-scoped tenant routing metadata
- stamp-scoped observability

Required inputs:
- `stamp_id`
- `environment`
- `region`
- `ring`
- optional `tenant_segment`

Design rule:
- one run targets one stamp or one bounded stamp batch
- never couple all tenants/stamps into one global deploy job

### 4. runtime-delivery

Purpose:
- build/push/promote application runtime artifacts

Scope:
- Odoo image build/push
- ACA runtime update
- migration jobs
- runtime smoke checks
- rollback-safe promotion

Design rule:
- runtime delivery is separate from infra delivery
- app rollout cadence and infra rollout cadence must remain independent

### 5. quality-governance

Purpose:
- benchmark, eval, and production-quality control

Scope:
- TaxPulse / tax-compliance benchmark runs
- Foundry evals
- custom tax evaluators
- red-team/adversarial tests
- production trace replay
- nightly/scheduled health checks
- regression scorecards and evidence packs

This pipeline must not be coupled directly to infra promotion.

## Stage model

### ci-validation

1. bootstrap
2. static validation
3. unit/module tests
4. SSOT/spec/docs validation
5. benchmark smoke
6. publish validation artifacts

### platform-shared-delivery

1. validate / lint / what-if
2. deploy dev shared plane
3. validate dev shared plane
4. deploy staging shared plane
5. validate staging shared plane
6. deploy prod shared plane
7. validate prod shared plane

### stamp-delivery

1. resolve target stamp metadata
2. validate stamp IaC
3. deploy stamp infra
4. validate stamp infra
5. deploy stamp runtime
6. validate stamp runtime
7. update stamp routing metadata
8. publish stamp evidence

### runtime-delivery

1. build
2. test
3. scan
4. push artifact/image
5. migrate
6. deploy runtime
7. smoke
8. rollback metadata

### quality-governance

1. load eval dataset
2. run deterministic evaluators
3. run model/agent evaluators
4. run tax/compliance custom evaluators
5. generate scorecard
6. publish evidence pack
7. fail or alert on regression

## Agent pool policy

- hosted agents by default
- self-hosted / Managed DevOps Pool only for jobs that require:
  - private network reachability
  - private endpoints
  - internal-only validation targets
  - custom runner image/tooling

Do not bind an entire pipeline to a self-hosted pool unless every job truly requires it.

## Environment and approval policy

Use Azure DevOps Environments for:
- shared-dev
- shared-staging
- shared-prod
- stamp-dev
- stamp-staging
- stamp-prod

Apply:
- approvals/checks to protected environments
- branch control to staging/prod
- exclusive lock for prod and any sensitive stamp deployment

## Tenant/stamp rollout policy

Use:
- deployment stamps for scale/isolation/region/customer class
- deployment rings for progressive release
- feature flags for tenant/user-level enablement without redeploying

## Secret/isolation policy

Use variable groups and Key Vault-backed secrets.

Secret handling should support:
- shared secret surfaces where valid
- per-stamp or per-tenant secret isolation where required by compliance or customer class

## Data-plane policy

Model the data plane explicitly:

- shared multitenant data stores only where justified
- sharded or stamp-scoped data stores where isolation/noisy-neighbor/compliance requires it
- tenant-to-stamp resolution must be explicit and machine-readable

## Observability policy

Every deployable plane must emit:
- traces
- latency
- run success
- error rate
- benchmark/eval outputs where applicable

Per-stamp observability is preferred for meaningful multitenant operations.

## Plane-to-pipeline mapping

### Shared plane → platform-shared-delivery

- Azure Front Door / WAF
- Entra / identity foundations
- Key Vault shared foundations
- shared monitoring / Application Insights / Log Analytics
- Foundry / Databricks foundational platform services where shared
- Azure DevOps service connections / variable-group governed surfaces

### Stamp plane → stamp-delivery

- Odoo ACA runtime slice for a stamp
- stamp-scoped PostgreSQL / data resources where isolated
- stamp-scoped routing metadata
- stamp-scoped tenant onboarding config
- stamp-scoped health validation

### Runtime plane → runtime-delivery

- Odoo images
- migrations
- runtime rollout
- runtime smoke/rollback

### Quality plane → quality-governance

- TaxPulse benchmark
- Foundry evals
- custom tax evaluators
- adversarial tests
- production continuous evaluation

## Template architecture

```text
.azure/pipelines/
  ci-validation.yml
  platform-shared-delivery.yml
  stamp-delivery.yml
  runtime-delivery.yml
  quality-governance.yml

infra/pipelines/templates/
  bootstrap.yml
  lint-python.yml
  test-odoo.yml
  validate-bicep.yml
  deploy-bicep.yml
  build-container.yml
  deploy-aca.yml
  run-benchmark.yml
  publish-evidence.yml
```

Template rules:
- top-level pipelines define orchestration
- templates define reusable job/stage logic
- keep template paths deterministic
- keep template repo/branch aligned to the running branch when externalized

## PR and deployment blocking policy

### PR block

Block PR merge on:
- YAML/template parse errors
- lint/test failures
- spec/SSOT contract failures
- broken benchmark smoke
- broken docs governance checks

### Prod deploy block

Block prod deploy on:
- failed what-if / validation
- failed environment approval
- failed runtime smoke
- failed migration check
- failed benchmark gate for agent/tax-compliance releases

### TaxPulse-specific hard block

Do not allow tax/compliance agent promotion if:
- ATC mapping is unresolved
- tax accuracy evaluator is below threshold
- critical compliance failures > 0
- no evidence pack was produced

## Upstream Odoo alignment

This pipeline topology is derived from official Odoo upstream engineering patterns
(runtime discipline, packaging, migration, testing, and documentation authority),
translated into Azure DevOps.

Upstream workflow intent is treated as reference only and is not adopted as GitHub
Actions in this repository. Official Odoo upstream barely uses GitHub Actions for
core runtime/release discipline — only `odoo/owl` has a visible GHA workflow. The
main Odoo surfaces lean on runbot, pre-commit hooks, packaging/runtime discipline,
and repo conventions.

See:
- `docs/architecture/ODOO_UPSTREAM_REFERENCE_SURFACES.md` — per-repo analysis
- `docs/architecture/ODOO_UPSTREAM_TO_AZDO_TRANSLATION.md` — intent translation table
- `ssot/odoo/upstream_reference_map.yaml` — machine-readable repo map
- `ssot/odoo/upstream_ci_translation.yaml` — machine-readable CI translation

## References

- [Azure SaaS and Multitenant Solution Architecture](https://learn.microsoft.com/en-us/azure/architecture/guide/saas-multitenant-solution-architecture/)
- [Deployment Stamps pattern](https://learn.microsoft.com/en-us/azure/architecture/guide/multitenant/approaches/overview)
- [Azure DevOps Environments and approvals](https://learn.microsoft.com/en-us/azure/devops/pipelines/process/approvals)
- [Key Vault in multitenant solutions](https://learn.microsoft.com/en-us/azure/architecture/guide/multitenant/service/key-vault)
- [Managed DevOps Pools](https://learn.microsoft.com/en-us/azure/devops/release-notes/2024/sprint-243-update)
