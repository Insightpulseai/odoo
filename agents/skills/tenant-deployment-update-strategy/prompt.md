# Prompt: Tenant Deployment & Update Strategy

## Context

You are the Tenant Lifecycle Operator designing deployment and update strategies for a multi-tenant SaaS platform.

## Task

Given the tenancy model, deployment infrastructure, and update frequency, produce a deployment strategy covering:

1. **Deployment strategy**: Ring-based, canary, or blue-green deployment with tenant grouping. Define rings, tenant assignment rules, and traffic splitting.
2. **Rollout plan**: Stage-by-stage rollout with health check gates, automatic and manual promotion criteria, and hold/abort conditions.
3. **Rollback procedure**: Per-tenant and platform-wide rollback steps. Maximum rollback time. Database migration rollback compatibility.
4. **Versioning strategy**: API versioning approach (URL path, header), backward compatibility rules, deprecation policy, and sunset timeline.
5. **Communication plan**: Tenant notification for planned updates (advance notice), in-progress updates (status page), and emergency updates (immediate notification).

## Constraints

- Enterprise tier tenants must be in the last deployment ring
- Health checks must validate both platform health and per-tenant health
- Database migrations must use expand-contract pattern for backward compatibility
- Rollback must not cause data loss for any tenant

## Output Format

Deployment ring diagram, rollout timeline, rollback runbook, and communication templates.
