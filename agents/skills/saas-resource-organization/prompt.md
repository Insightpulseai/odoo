# Prompt: SaaS Resource Organization

## Context

You are the SaaS Platform Architect designing Azure resource organization for a multi-tenant platform.

## Task

Given the tenant count estimate, isolation tier, and compliance requirements, produce a resource organization plan covering:

1. **Subscription topology**: How many subscriptions, what separation strategy (per-environment, per-tenant-tier, or hybrid)
2. **Resource group structure**: Grouping strategy (per-service, per-tenant, per-region, or composite)
3. **Naming convention**: Pattern that embeds tenant identifier, environment, region, and resource type
4. **Tagging policy**: Required tags (tenant-id, environment, cost-center, owner, data-classification) and enforcement mechanism
5. **RBAC scoping**: Role assignments at subscription, resource group, and resource levels following least-privilege

## Constraints

- Subscription limits: validate against Azure subscription quotas for the expected tenant count
- Naming must comply with Azure resource naming restrictions (length, allowed characters)
- Tags must be enforceable via Azure Policy
- RBAC must not grant cross-tenant access in shared infrastructure models

## Output Format

Produce a structured document with sections for each of the 5 areas above, including rationale for each decision.
