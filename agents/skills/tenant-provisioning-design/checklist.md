# Checklist: Tenant Provisioning Design

## Pre-flight

- [ ] Tenant tiers defined with resource requirements per tier
- [ ] Target provisioning SLA established per tier
- [ ] Resource naming convention established (see saas-resource-organization)
- [ ] Identity provider selected and configured (Entra ID, B2C)
- [ ] Automation platform selected (Durable Functions, Logic Apps)

## Registration Flow

- [ ] Registration intake captures all required tenant metadata
- [ ] Input validation rejects invalid/duplicate tenant requests
- [ ] Approval gate defined for tiers requiring manual review
- [ ] Registration state machine documented (pending, approved, provisioning, active, failed)
- [ ] Duplicate detection prevents re-registration of existing tenants

## Resource Allocation

- [ ] ARM/Bicep templates exist for each tenant tier
- [ ] Templates are parameterized (tenant ID, tier, region, environment)
- [ ] Resource naming follows organizational convention
- [ ] Templates validated via `az deployment group what-if`
- [ ] Resource quotas checked before provisioning starts

## Configuration Templates

- [ ] Configuration schema defined (JSON Schema or equivalent)
- [ ] Default values documented per tier
- [ ] Tenant-specific overrides validated before application
- [ ] Configuration versioned and auditable

## Onboarding Automation

- [ ] Orchestration workflow defined with explicit step ordering
- [ ] Each step is idempotent (safe to re-run)
- [ ] Retry policy defined per step (max retries, backoff)
- [ ] Compensation actions defined per step (rollback on failure)
- [ ] Timeout defined per step and for overall workflow
- [ ] Dead-letter handling for permanently failed provisioning

## Provisioning SLA

- [ ] SLA target defined per tier (e.g., free: 5min, enterprise: 30min)
- [ ] Measurement points instrumented (start, each step, completion)
- [ ] Dashboard shows provisioning duration distribution
- [ ] Alert fires when provisioning exceeds SLA threshold
- [ ] SLA breach triggers incident workflow

## Post-flight

- [ ] End-to-end provisioning tested for each tier
- [ ] Concurrent provisioning tested (10+ simultaneous tenants)
- [ ] Failure injection tested (mid-provisioning abort)
- [ ] Rollback verified — no orphaned resources after failure
- [ ] Provisioning audit trail complete and queryable
