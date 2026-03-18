# Prompt: Tenant Provisioning Design

## Context

You are the SaaS Platform Architect designing automated tenant provisioning for a multi-tenant platform on Azure.

## Task

Given the tenant tiers, target provisioning SLA, and automation platform, produce a tenant provisioning design covering:

1. **Registration flow**: End-to-end sequence from tenant signup to provisioning trigger, including validation and approval gates
2. **Resource allocation**: ARM/Bicep templates parameterized by tenant tier, with resource naming that embeds tenant identifier
3. **Configuration templates**: Schema for tenant-specific configuration applied after resource creation (feature flags, limits, branding)
4. **Onboarding automation**: Orchestration workflow (Durable Functions, Logic Apps, or equivalent) with idempotent steps, retry logic, and compensation actions
5. **Provisioning SLA**: Target duration per tier, measurement points, monitoring dashboard, and alerting thresholds
6. **Rollback procedures**: Compensation logic for partial provisioning failures — resource cleanup, state reset, notification

## Constraints

- Provisioning must be fully idempotent — re-running the same request must not create duplicate resources
- Partial failure must not leave orphaned resources — compensation actions must clean up
- Resource naming must follow the organization naming convention (see saas-resource-organization skill)
- Identity setup must follow tenant-identity-isolation patterns
- All provisioning actions must emit audit events for observability

## Output Format

Produce a structured document with:
- Sequence diagram (Mermaid) for the provisioning workflow
- ARM/Bicep template skeleton for one tenant tier
- Configuration schema (JSON Schema)
- Monitoring query for SLA tracking
- Rollback procedure for each provisioning step
