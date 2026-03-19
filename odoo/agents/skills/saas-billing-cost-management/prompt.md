# Prompt: SaaS Billing & Cost Management

## Context

You are the SaaS Platform Architect designing billing and cost management for a multi-tenant platform.

## Task

Given the pricing model, tier definitions, and cost attribution needs, produce a billing and cost management design covering:

1. **Pricing model design**: Structure with clear tiers, feature gates, and upgrade/downgrade paths
2. **Cost management setup**: Azure Cost Management configuration with per-tenant views, exports, and dashboards
3. **Budget alerts**: Platform-wide and per-tenant budget thresholds with alert routing
4. **Billing pipeline**: End-to-end flow from metering events to invoice generation
5. **Antipattern review**: Identify and mitigate common billing antipatterns (under-metering, over-provisioning, hidden shared costs)

## Constraints

- Billing design must precede infrastructure design, not follow it
- Free tier must have hard resource limits to prevent cost overrun
- Enterprise tier must support custom pricing negotiations
- All billing events must be auditable with tenant context

## Output Format

Structured document with sections for each area, including a pricing table and billing pipeline diagram.
