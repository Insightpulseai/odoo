# Hosting Policy

## Purpose
Define the canonical hosting policy for the InsightPulseAI platform.

## Status
Canonical.

## Default Rule
All core platform systems are self-hosted by default. This includes all stateful, system-of-record, and primary application runtime components unless explicitly listed as an approved managed exception.

## Core Systems That Must Remain Self-Hosted
- Odoo runtime and workers
- Operational databases
- Internal APIs
- Control-plane services
- Backend application origins
- Automation runtimes
- Workflow engines
- Lakehouse processing and storage layers
- Internal observability backends unless separately approved
- Internal schedulers, queues, and integration runtimes

## Approved Managed Exceptions

### 1. Tableau Cloud
Allowed: BI consumption, dashboards, governed analytics presentation.
Not allowed: raw landing zone, primary transformation engine, transactional source-of-truth system.

### 2. Cloudflare Edge Services (Including Workers)
Allowed: DNS, CDN, WAF, edge routing, public API facade, advisory copilot proxy, webhook ingress, request validation/normalization, lightweight auth/session helpers, edge caching, geo-aware routing, rate limiting.
Not allowed: core ERP runtime, transactional databases, long-lived stateful workflows, primary internal APIs as sole SOR, lakehouse processing, control-plane SOR storage.

## Canonical Architecture
```
Clients
  -> Cloudflare edge layer (DNS / WAF / CDN / optional Workers)
    -> self-hosted application origins
      -> self-hosted backend services / Odoo / databases / automation / lakehouse
        -> Tableau Cloud (BI consumption only)
```

## Public Copilot Pattern
```
Browser -> Cloudflare Worker (optional edge proxy) -> self-hosted backend adapter -> Azure AI Foundry
```
Allowed because Worker is acting as edge/API facade, browser secrets not exposed, core logic remains behind self-hosted boundary.

## Prohibited Interpretations
- Treating Cloudflare Workers as "self-hosted"
- Moving Odoo runtime into Workers
- Using Workers as primary home for core business logic
- Placing operational databases behind Workers as application runtime
- Using Tableau Cloud as raw data landing zone
