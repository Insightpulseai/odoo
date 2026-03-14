# Cloudflare Edge Policy

## Purpose
Define the approved use, boundaries, and governance for Cloudflare edge services (including Workers) within the InsightPulseAI platform.

## Status
Canonical. Extends `docs/architecture/HOSTING_POLICY.md`.

## Classification
Cloudflare Workers is an **approved managed edge exception**. It is not self-hosted infrastructure. All uses must comply with the hosting policy's managed exception rules.

## Allowed Uses

### Public API Facade
Workers may serve as a public-facing API gateway that routes, validates, and normalizes requests before forwarding them to self-hosted backend origins.

### Advisory Copilot Proxy
Workers may act as an edge proxy between the browser and a self-hosted backend adapter that holds secrets and communicates with Azure AI Foundry. The Worker handles request filtering, rate limiting, and basic validation. It does not hold Foundry credentials or execute core agent logic.

### Webhook Ingress
Workers may receive inbound webhooks from external services (e.g., payment providers, third-party SaaS) and forward them to self-hosted automation runtimes (n8n, internal APIs).

### Request Validation and Normalization
Workers may validate request structure, enforce content-type requirements, strip unnecessary headers, and normalize payloads before forwarding to origins.

### Rate Limiting
Workers may enforce per-client or per-route rate limits at the edge to protect backend services from abuse.

### Geo-Aware Routing
Workers may inspect request geography and route to appropriate backend origins or serve region-specific responses.

### Edge Caching
Workers may cache responses for public, non-personalized content to reduce origin load.

## Disallowed Uses

### Odoo Runtime
Workers must never host Odoo application logic, web controllers, or ORM operations. Odoo runs on self-hosted container infrastructure exclusively.

### Transactional Databases
Workers must never serve as the runtime for transactional database operations. All database access flows through self-hosted backend services.

### Control-Plane SOR
Workers must never be the sole system-of-record for control-plane state, configuration, or platform metadata.

### Long-Running Workflows
Workers must never execute long-running or stateful workflows. These belong in self-hosted automation runtimes (n8n, queue workers).

### Lakehouse Processing
Workers must never perform ETL, CDC, or medallion-layer data transformations. These belong in self-hosted lakehouse infrastructure.

## Canonical Ingress Patterns

### Advisory Copilot
```
Browser -> Cloudflare Worker (edge proxy) -> self-hosted backend adapter -> Azure AI Foundry
```
- Worker: request validation, rate limiting, session correlation
- Backend adapter: secret-bearing Foundry integration, mode enforcement, response normalization
- Foundry: model inference

### API Facade
```
External client -> Cloudflare Worker (API gateway) -> self-hosted API origin
```
- Worker: auth header validation, rate limiting, request normalization
- Origin: business logic, database access, response generation

### Webhook Ingress
```
External service -> Cloudflare Worker (webhook receiver) -> self-hosted automation runtime
```
- Worker: signature verification, payload validation, forwarding
- Automation runtime: workflow execution, state management

## Secret Handling Rules

- No secrets in any repository, including Worker source code
- Secrets are injected at deploy time via Cloudflare dashboard or Wrangler CLI from a secure pipeline
- Worker code must never log, echo, or expose secret values
- API keys for upstream services (Foundry, internal APIs) are held by self-hosted backends, not Workers
- Workers may hold only edge-scoped secrets (e.g., a shared HMAC key for webhook signature verification) injected via environment bindings

## Deployment Ownership

### Canonical Owner: `infra`
- `infra` repo owns all Worker deployment configuration (`wrangler.toml`, route bindings, environment declarations)
- `infra` CI/CD pipelines deploy Workers
- `infra` manages Cloudflare account configuration, DNS, and WAF rules

### Consumers
- **`web`**: Calls Worker endpoints from browser code. Does not deploy Workers.
- **`automations`**: Receives forwarded webhooks from Workers. Does not deploy Workers.
- **`agents`**: Does not use Workers as runtime. May benefit from Worker edge proxy managed by `infra`.
