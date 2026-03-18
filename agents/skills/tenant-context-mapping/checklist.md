# Checklist: Tenant Context Mapping

## Request Mapping

- [ ] Primary mapping strategy defined (subdomain, header, token, path)
- [ ] Mapping resolution logic implemented at API gateway/ingress
- [ ] Fallback behavior defined (reject, not default)
- [ ] Mapping tested for edge cases (missing header, invalid subdomain)
- [ ] Mapping performance validated (lookup latency < 5ms)

## Context Propagation

- [ ] Context carrier defined (HTTP header, gRPC metadata, thread-local)
- [ ] Middleware injects tenant context into request pipeline
- [ ] Application code accesses tenant context via consistent API
- [ ] Service-to-service calls propagate tenant context explicitly
- [ ] Database connections configured with tenant context (RLS session var)

## Async Context

- [ ] Message envelope includes tenant-id field
- [ ] Queue consumers validate tenant-id before processing
- [ ] Messages without tenant-id are dead-lettered
- [ ] Cron jobs resolve tenant context before execution
- [ ] Event bus events include tenant-id in metadata

## Observability

- [ ] Structured logs include tenant-id field
- [ ] Distributed traces include tenant-id as span attribute
- [ ] Custom metrics include tenant-id as dimension
- [ ] Dashboards support filtering by tenant-id
- [ ] Alerting rules can scope to specific tenants

## Validation

- [ ] Ingress validates tenant-id presence and format
- [ ] Service boundary validates tenant-id matches expected tenant
- [ ] Database layer enforces tenant-id via RLS or connection scoping
- [ ] Validation failures logged with request context for debugging
- [ ] Cross-tenant access attempts trigger security alert
