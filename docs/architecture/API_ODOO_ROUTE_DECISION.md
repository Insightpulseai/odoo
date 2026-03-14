# ADR: Odoo API Route Transport Decision

> Status: Accepted
> Date: 2026-03-13
> Spec: `spec/unified-api-gateway/`
> Resolves: Open Decision #4

## Context

Odoo CE 19 exposes its API primarily via JSON-RPC (`/jsonrpc`, `/web/dataset/call_kw`).
The unified API gateway defines REST-style routes at `/api/v1/erp/*`. The question:
how does the gateway translate between REST consumers and the JSON-RPC backend?

## Decision

**JSON-2 first, adapter-backed for gaps.**

1. **Phase 1 (read-only)**: Use Odoo 19's native REST-like endpoints where available
   (`/api/` experimental endpoints, web controllers that return JSON). Proxy these
   through APIM with minimal transformation.

2. **Phase 2 (full CRUD)**: For resources not covered by native REST endpoints, deploy
   a thin REST-to-JSON-RPC adapter as an ACA sidecar or standalone microservice.
   The adapter translates standard REST verbs to Odoo JSON-RPC calls.

3. **Not exposed**: Raw JSON-RPC is not the preferred public contract. External
   consumers interact with REST endpoints only. Internal service-to-service calls
   may use JSON-RPC directly (bypassing the gateway).

## Consequences

- External consumers get a clean REST API without needing to understand Odoo internals
- The adapter layer adds latency (~10-50ms) for translated calls
- Adapter must be maintained as Odoo models change
- Native Odoo REST endpoints are preferred when available to minimize adapter surface

## Alternatives Considered

- **JSON-RPC passthrough**: Consumers speak JSON-RPC directly. Rejected -- defeats
  the purpose of a unified REST API surface.
- **Full REST rewrite**: Build a complete REST API independent of Odoo. Rejected --
  too much custom code, duplicates Odoo's data access layer.
- **GraphQL layer**: Rejected -- adds unnecessary complexity for the current consumer base.

## References

- Gateway spec: `spec/unified-api-gateway/`
- SSOT: `ssot/api/unified-api-gateway.yaml`
- Odoo 19 REST API: experimental, available at `/api/` prefix
