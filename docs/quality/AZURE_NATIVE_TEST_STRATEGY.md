# Azure-Native Test Strategy

## Scope

This strategy defines test ownership across:
- `odoo`
- `agent-platform`
- `infra`

It assumes Odoo-native test classes are necessary but insufficient for an Azure-native deployment.

## Why Odoo tests alone are not enough

Odoo provides the right in-repo test surfaces for model logic, HTTP/browser flows, server-side form behavior, tagging, and performance query-count checks.
Use:
- `TransactionCase`
- `HttpCase`
- `Form`
- `browser_js`
- `assertQueryCount()`
- `@tagged('-at_install', 'post_install')` for most end-to-end `HttpCase` scenarios

These prove application correctness, but they do not prove:
- Azure Container Apps readiness
- revision rollout safety
- Front Door origin health behavior
- managed identity and RBAC correctness
- PostgreSQL HA/failover behavior

## Repo ownership

### `odoo`
Owns application-level truth:
- posting blocker logic
- workflow state transitions
- UI/browser flows
- review and approval surfaces

Must include:
- `TransactionCase` tests for tax/compliance blockers
- `Form` tests for onchange/default behavior
- `HttpCase` and `browser_js` for login, upload, review, and reject/block flows
- query-count budgets on expensive accounting/compliance flows

### `agent-platform`
Owns service-level truth:
- extraction schema
- Document Intelligence integration
- Foundry client/service integration
- deterministic validator
- service API contracts
- retry/fallback behavior

Must include:
- offline golden-fixture tests
- live extraction smoke tests
- Foundry project/OpenAI-compatible client smoke tests
- low-confidence and dependency-failure fallback tests

### `infra`
Owns Azure runtime truth:
- Container Apps probes
- revision labels and traffic split safety
- Front Door origin health
- managed identity wiring and RBAC checks
- PostgreSQL HA/failover validation

Must include:
- startup/readiness/liveness probe checks
- labeled revision smoke path
- traffic-shift and rollback checks
- Front Door origin health checks
- managed identity success and denied-path checks
- PostgreSQL reconnect/failover smoke checks

## Mandatory negative fixture

The uploaded Dataverse invoice remains a mandatory negative fixture.
Expected outcome:
- extracted values reconcile for line, VAT, gross, and withholding
- printed total due does not reconcile with expected payable
- verdict must be `needs_review`
- Odoo must block autoposting

## Release gate sequence

### 1. CI before Azure deploy
- Odoo unit/integration green
- Odoo browser/http green
- agent-platform fixture validator green
- performance/query budget green

### 2. Azure staging revision
- Container Apps probes green
- managed identity green
- Foundry smoke green
- Document Intelligence smoke green
- browser flow through real ingress green

### 3. Production cutover
- labeled revision test green
- traffic split green
- rollback green
- Front Door origin health green
- PostgreSQL failover smoke green

## Required gates by stage

| Stage                      | `odoo`                                                            | `agent-platform`                           | `infra`                                            |
| -------------------------- | ----------------------------------------------------------------- | ------------------------------------------ | -------------------------------------------------- |
| **CI pre-deploy**          | `TransactionCase`, `Form`, `HttpCase`, `browser_js`, query budget | fixture validator, schema/API tests        | config/static validation                           |
| **Azure staging revision** | real ingress browser flow                                         | live Document Intelligence + Foundry smoke | probes, managed identity, revision label           |
| **Production cutover**     | final smoke through public ingress                                | dependency smoke only                      | traffic split, rollback, Front Door, PostgreSQL HA |
