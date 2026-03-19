# API Authority Boundaries Contract

> **Contract ID**: C-API-AUTH-01
> **Status**: Active
> **Created**: 2026-03-13
> **Scope**: Unified API Gateway -- data authority ownership across Odoo, Supabase, Foundry, Plane, n8n

---

## 1. Purpose

Prevent authority drift where the API gateway obscures which system is the single source of truth
for a given data domain. The gateway is a routing and policy enforcement layer -- it must never
become a shadow data store or allow writes to bypass the authoritative system.

---

## 2. Authority Map

| Domain | Authoritative System | Write Path | Read Path | Replicas Allowed | Forbidden |
|--------|---------------------|------------|-----------|-----------------|-----------|
| ERP / Finance / Projects / Tasks | Odoo | Odoo JSON-RPC via gateway | Odoo via gateway (cached) | Read replicas in Supabase (sync only) | Direct Supabase writes to ERP data |
| Control-plane / Config / Registry | Supabase | Supabase PostgREST via gateway | Supabase via gateway | None | Odoo writes to control-plane tables |
| Agent Runtime / Conversations | Foundry | Foundry API via gateway | Foundry via gateway | Conversation summaries in Supabase | Direct DB writes to Foundry tables |
| Docs / Work Tracking | Plane | Plane API (not via gateway) | Read-only summaries via gateway | Static repo-derived content | Gateway writes to Plane data |
| Workflow Triggers | n8n | Webhook POST via gateway | Status polling via gateway | None | Business state mutations via n8n |

---

## 3. Cross-Boundary Rules

1. **Odoo to Supabase (read replicas)**: Supabase may hold read replicas of Odoo data for
   dashboards and agent context. Sync direction is Odoo --> Supabase only. Supabase tables
   holding Odoo-derived data must be prefixed `replica_` and marked read-only at the
   PostgREST policy level.

2. **Foundry to Supabase (config reads)**: Foundry may read agent configuration, tool
   definitions, and prompt templates from Supabase control-plane tables. Foundry must never
   write to these tables -- config changes flow through the control-plane API.

3. **n8n to Odoo (action triggers)**: n8n may trigger Odoo actions (create invoice, update
   task status) via the gateway's `/api/v1/erp/*` routes. n8n must never write directly to
   the Odoo PostgreSQL database or call Odoo JSON-RPC outside the gateway.

4. **No transitive authority**: No system may write to another system's authoritative tables
   except through declared sync contracts. A sync contract must specify: source system,
   target system, sync direction, conflict resolution strategy, and frequency.

---

## 4. Violation Handling

Any write that bypasses authority boundaries constitutes a governance violation:

- The gateway must log all requests with source identity, target route, and method.
- APIM policies must reject writes to routes owned by a system the caller is not authorized for.
- Violations are logged to `ops.platform_events` with `event_type = 'authority_violation'`.
- Alerts fire to the `#ops-alerts` Slack channel via n8n webhook.
- Repeated violations from a single consumer trigger automatic API key suspension.

---

## 5. Review Cadence

This contract is reviewed quarterly. Any new cross-boundary data flow requires an amendment
before implementation.

---

*Governed by: `docs/architecture/SSOT_BOUNDARIES.md`*
