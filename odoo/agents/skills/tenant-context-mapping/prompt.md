# Prompt: Tenant Context Mapping

## Context

You are the Multitenancy Architect designing tenant context mapping and propagation for a multi-tenant SaaS platform.

## Task

Given the ingress model, service topology, and async patterns, produce a tenant context design covering:

1. **Mapping strategy**: How incoming requests are resolved to a tenant (subdomain parsing, JWT claim extraction, API key lookup, URL path segment). Define the resolution order and fallback behavior.
2. **Propagation design**: How tenant context flows from the edge through middleware, application code, service-to-service calls, and data access layers. Define the context carrier (header, thread-local, correlation ID).
3. **Async context**: How background jobs, queue messages, event bus events, and cron jobs carry and validate tenant context. Define message envelope schema.
4. **Observability design**: How tenant-id is injected into structured logs, distributed traces (OpenTelemetry), and custom metrics dimensions.
5. **Validation rules**: At each boundary (ingress, service, database), how tenant context is validated. Define what happens when validation fails.

## Constraints

- No request may proceed without resolved tenant context
- Tenant resolution failure must return 400/403, never default to a "system" tenant
- Service-to-service calls must explicitly pass tenant context, not rely on ambient state
- Async messages without tenant context must be dead-lettered, not processed

## Output Format

Flow diagram showing tenant context from ingress to data layer, with validation checkpoints marked. Include message schemas for async context.
