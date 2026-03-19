# PRD — n8n DevOps Templates Integration

## Problem
n8n's DevOps template library contains valuable automation patterns (infra
provisioning, webhook routing, deployment notifications, incident intake)
but they are:
- Unregistered in our SSOT
- Not normalized to our ops.runs/run_events telemetry model
- Missing idempotency guarantees
- Using ad-hoc secret handling instead of SSOT-declared consumers

## Solution
A curated template catalog at ssot/integrations/n8n_devops_templates.yaml
that imports, validates, and normalizes n8n DevOps templates into our
SSOT-governed automation stack with mandatory telemetry, idempotency,
and secret consumer registration.

## Users
- **Platform engineer**: imports and activates templates, monitors via Advisor
- **DevOps operator**: triggers templates (manual/webhook/cron), inspects run logs
- **Advisor engine**: scores automation coverage, failure rates, cost signals

## Core Capabilities

### 1. Template Catalog (SSOT)
- Machine-readable catalog at ssot/integrations/n8n_devops_templates.yaml
- Each entry: slug, trigger, idempotency_key, secrets_consumed, ops_mapping, advisor_signals
- Status lifecycle: evaluating → planned → active → deprecated

### 2. Import + Validation Pipeline
- Fetch from n8n template API (list/search/fetch)
- Validate against template_policy (no forbidden patterns)
- Register secret consumers in ssot/secrets/registry.yaml
- Store normalized workflow JSON in automations/n8n/workflows/

### 3. Ops Ledger Integration
- Every execution writes ops.runs (run_type from catalog)
- Step events write ops.run_events (events list from catalog)
- Idempotency key prevents duplicate processing

### 4. Advisor Scoring
- automation_coverage: % of DevOps outcomes with active templates
- failure_rate: template execution failure rate
- cost_signals: infra churn, resource waste detection
- security_compliance: secrets rotation, policy violation count

## Priority Templates (5 DevOps Outcomes)

| Priority | Outcome | Template Slug | Status |
|----------|---------|---------------|--------|
| 1 | Deploy notification | deploy-notify-pipeline | active |
| 2 | GitHub webhook routing | github-webhook-ops-router | planned |
| 3 | DO infra provisioning | do-droplet-provisioning | planned |
| 4 | Incident intake | incident-intake-router | planned |
| 5 | Secrets rotation | secrets-rotation-reminder | planned |

## Non-Goals
- Building a general n8n template marketplace
- Replacing n8n's own template UI
- Importing non-DevOps templates (finance, HR, etc. are separate catalogs)

## Success Criteria
- All imported templates emit deterministic idempotency keys
- All external calls constrained by ssot/integrations/ allowlists
- Advisor can score automation coverage, failure rate, cost signals
- Zero secrets-policy violations in activated templates
