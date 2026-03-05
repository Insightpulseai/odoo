# ADR-007: n8n MCP Gateway Authentication Strategy

**Status**: Accepted
**Date**: 2026-03-05
**Context**: MCP OAuth auth error — "authorized but integration rejected credentials"

---

## Problem

ChatGPT connector completes OAuth handshake with the MCP gateway but gets
rejected on the first authenticated request (reference id: 1aa4f7db14cb7610).

## Root Cause

The Supabase Edge Function (`supabase/functions/mcp-gateway/index.ts`)
validates Bearer tokens exclusively via `supabase.auth.getUser()`, which only
accepts Supabase-issued JWTs. When ChatGPT sends its own OAuth access token,
validation fails silently and returns 403 with no diagnostic info.

## Decision

### Short-term (implemented)

Multi-path Bearer token validation in the Supabase Edge Function:

1. **Supabase JWT** — `supabase.auth.getUser(token)` for native users
2. **External JWKS** — Fetch provider's JWKS, validate signature + claims
   (configured via `AUTH_JWKS_URL`, `AUTH_ISSUER`, `AUTH_AUDIENCE` env vars)
3. **Opaque token** — Hash lookup in `api_keys` table as fallback

Plus: structured error codes (`AUTH_MISSING`, `AUTH_TOKEN_INVALID`,
`AUTH_JWKS_FAIL`, etc.) and `/auth/check` self-test endpoint.

### Medium-term (recommended)

Use **n8n's native instance-level MCP server** instead of the Supabase Edge
Function gateway for external AI clients (ChatGPT, Claude Desktop):

- n8n provides built-in OAuth2 and Access Token authentication
- Supports SSE and Streamable HTTP transports
- Per-workflow enablement (allowlist equivalent)
- No custom middleware needed for auth
- Reference: https://docs.n8n.io/advanced-ai/accessing-n8n-mcp-server/

The Supabase Edge Function gateway remains valuable for:
- Rate limiting (n8n native MCP has no built-in rate limits)
- Audit logging to `ops.run_events`
- Allowlist enforcement beyond n8n's per-workflow toggle
- Cross-cutting concerns (request routing, job queuing)

### Architecture

```
External AI Client (ChatGPT)
    ↓ OAuth2 / Access Token
n8n Native MCP Server (instance-level)
    ↓ Per-workflow enablement
n8n Workflow Execution
    ↓ Webhook callback
Supabase Edge Function (audit + rate limit)
    ↓
ops.run_events (audit ledger)
```

## Consequences

- ChatGPT can connect using n8n's native OAuth2 flow (no JWKS config needed)
- The Supabase gateway becomes an **audit/governance layer**, not the auth layer
- Existing API key users continue working via the Supabase gateway directly
- n8n's per-workflow toggle replaces manual allowlist for external clients

## References

- n8n MCP Server docs: https://docs.n8n.io/advanced-ai/accessing-n8n-mcp-server/
- MCP Server Trigger node: https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-langchain.mcptrigger/
- Fix commit: `fix(mcp): add deterministic auth error codes and external JWT support`
- Spec: `spec/n8n-mcp-gateway/constitution.md`
