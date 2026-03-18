# Unified API Gateway — Constitution

> Non-negotiable rules governing the InsightPulseAI API Gateway.
> This document is append-only for new rules. Existing rules may only be
> amended via spec-level PR with architecture review.

---

## Rule 1: Single Public Entrypoint

All external API traffic enters through `api.insightpulseai.com`.
No other subdomain serves programmatic integration endpoints.
Internal service origins (`erp.*`, `n8n.*`, `auth.*`, etc.) are UI/app surfaces only.

## Rule 2: No Monolith

The gateway routes requests to bounded domain services. It never merges,
aggregates, or transforms cross-domain data. Each route group maps to exactly
one owner system. Gateway logic is limited to: routing, auth, rate limiting,
audit, versioning, and observability.

## Rule 3: Authority Preservation

Each system retains exclusive write authority over its domain:

| System | Authority Domain | Role |
|--------|-----------------|------|
| Odoo | ERP, operations, finance, invoicing | System of Record |
| Supabase | Control plane, feature flags, agent registry, app config | SSOT for platform state |
| Foundry | Agent runtime, conversations, tool orchestration | Agent execution surface |
| Plane | Specs, plans, work items, documentation | Documentation/work SSOT |
| n8n | Workflow triggers, sync kickoff | Orchestration triggers only |

n8n is never an authoritative write target. It triggers actions in owner systems.

## Rule 4: Route Ownership Declaration

Every route group in the gateway configuration must declare:

- **Owner system** (single, non-shared)
- **Write authority** (who may mutate state)
- **Read authority** (who may query)
- **Forbidden operations** (explicitly denied cross-domain writes)
- **Audit requirement** (required or optional)

Undeclared routes are rejected at configuration validation time.

## Rule 5: No Secrets in Repo

Gateway configuration references secrets by Azure Key Vault reference only.
No API keys, tokens, certificates, or credentials in source control.
Vault: `kv-ipai-dev`. Binding: managed identity to Key Vault to env vars.

## Rule 6: Gateway Responsibilities

The gateway handles exactly these concerns and no others:

1. **Authentication** — OAuth2/JWT validation, API key verification
2. **Rate limiting** — Per-consumer, per-route-group quotas
3. **Audit logging** — Request metadata to Azure Monitor / Log Analytics
4. **API versioning** — Version prefix routing (`/v1/`, `/v2/`)
5. **Observability** — Distributed tracing headers, health probes
6. **TLS termination** — Via Azure Front Door (upstream of gateway)

The gateway does NOT: transform payloads, join cross-service data,
cache authoritative state, or execute business logic.

## Rule 7: No Direct Public Access to Internal Origins

External consumers must never integrate directly against:
`erp.insightpulseai.com`, `n8n.insightpulseai.com`, `auth.insightpulseai.com`,
or any other internal service FQDN.

All programmatic external traffic routes through `api.insightpulseai.com`.
Internal service-to-service traffic uses managed identity and private networking.

## Rule 8: DNS Contract

| Subdomain | Purpose | Traffic Type |
|-----------|---------|-------------|
| `api.insightpulseai.com` | Unified API Gateway | Programmatic integration |
| `erp.insightpulseai.com` | Odoo UI | Browser/app |
| `n8n.insightpulseai.com` | n8n UI | Browser/app |
| All other subdomains | UI/app surfaces | Browser/app |

New API routes are added to the gateway. New subdomains are for UI surfaces only.

## Rule 9: Versioned Deprecation

Breaking changes to any published API route require:

1. New version prefix (e.g., `/v2/erp/*` alongside `/v1/erp/*`)
2. Deprecation header on old version (`Sunset: <date>`, `Deprecation: true`)
3. Minimum 90-day sunset window from announcement to removal
4. Consumer notification via changelog and API response headers

## Rule 10: Azure-Native Governance

Policy enforcement uses Azure-native tooling only:

- **Azure API Management (APIM)** — Rate limiting, subscription keys, policies
- **Azure Front Door rules engine** — Routing, header injection, geo-filtering
- **Entra ID** — OAuth2 token issuance and validation
- **Azure Monitor** — Audit logs, distributed tracing, alerting

No third-party API gateway products (Kong, Apigee, etc.) without architecture review.

---

*Spec: `spec/unified-api-gateway/`*
*Last updated: 2026-03-13*
