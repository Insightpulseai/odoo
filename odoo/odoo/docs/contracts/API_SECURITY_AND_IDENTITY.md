# API Security and Identity Contract

> **Contract ID**: C-API-SEC-01
> **Status**: Active
> **Created**: 2026-03-13
> **Scope**: Unified API Gateway -- authentication, authorization, rate limiting, secrets, audit

---

## 1. Authentication Modes

| Consumer Type | Auth Method | Token Source | Scope Model |
|---------------|------------|-------------|-------------|
| External consumers | OAuth2 (Azure Entra ID) | JWT Bearer token | Per-application scopes |
| Service-to-service | Managed Identity (Azure MI) | MI token endpoint | Role-based (system identity) |
| CI/CD pipelines | API key | APIM subscription key | Restricted scopes (read-only or deploy-only) |
| Agent-to-gateway | OAuth2 with service principal | Client credentials flow | Agent-specific scopes |

All consumers must present a valid credential on every request. Anonymous access is not
permitted on any route group.

---

## 2. Token Validation

APIM validates JWT tokens at the gateway before forwarding to backend services.

- **Issuer**: `https://login.microsoftonline.com/{tenant-id}/v2.0`
- **Audience**: APIM application registration client ID
- **Clock skew tolerance**: 5 minutes
- **Required claims**: `sub`, `aud`, `iss`, `exp`, `iat`

Backend services receive validated identity via forwarded headers:

| Header | Content |
|--------|---------|
| `X-Auth-User-ID` | Authenticated user or service principal ID |
| `X-Auth-Scope` | Comma-separated list of granted scopes |
| `X-Auth-Tenant` | Tenant identifier (for multi-tenant scenarios) |
| `X-Correlation-ID` | Request correlation ID for distributed tracing |

Backend services must not re-validate the JWT. They trust the gateway headers.

---

## 3. API Key Management

- Keys are issued via APIM developer portal (Azure API Management).
- Keys are stored in Azure Key Vault (`kv-ipai-dev`).
- Rotation schedule: every 90 days, enforced by Key Vault expiry policy.
- Revocation: immediate via APIM subscription deactivation.
- Keys must never appear in source code, CI logs, or documentation.
- Key prefixes (first 8 characters) may be used in debug logs for identification.

---

## 4. Rate Limiting Tiers

| Tier | Requests/min | Burst | Use Case | Applied To |
|------|-------------|-------|----------|------------|
| Relaxed | 120 | 200 | Docs, read-only surfaces | `/api/v1/docs/*` |
| Standard | 60 | 100 | ERP operations, control plane | `/api/v1/erp/*`, `/api/v1/control/*` |
| Elevated | 30 | 50 | Agent conversations (long-running) | `/api/v1/agents/*` |
| Strict | 10 | 20 | Integration webhook triggers | `/api/v1/integrations/*` |

Rate limits are enforced per-consumer (by API key or OAuth2 client ID).
Exceeded limits return HTTP 429 with `Retry-After` header.

---

## 5. Secrets Policy

All secrets are managed via Azure Key Vault (`kv-ipai-dev`):

- Runtime binding: Managed Identity --> Key Vault --> environment variables
- No secrets in Odoo database `ir.config_parameter`
- No secrets in repository (any branch, any commit)
- No secrets in APIM named values -- use Key Vault references only
- No secrets in n8n workflow JSON exports -- use credential references
- No secrets in Supabase Edge Function source -- use Supabase Vault

Violation of this policy triggers immediate remediation per `~/.claude/rules/secrets-policy.md`.

---

## 6. Audit Requirements

All API requests are logged with the following fields:

| Field | Description | PII |
|-------|-------------|-----|
| `correlation_id` | Unique request identifier | No |
| `timestamp` | ISO 8601 with timezone | No |
| `consumer_id` | API key prefix or OAuth2 client ID | No |
| `user_id` | Authenticated user (if applicable) | Yes -- redacted in logs |
| `route` | Request path | No |
| `method` | HTTP method | No |
| `status_code` | Response status | No |
| `latency_ms` | End-to-end latency | No |
| `backend_service` | Target ACA service | No |

- PII fields are redacted in long-term storage (hashed or masked).
- Retention: 90 days in Azure Monitor / Log Analytics.
- Compliance: Audit logs are immutable once written.
- Access: Platform team only, via Azure RBAC.

---

## 7. Security Incident Response

- Auth failures exceeding 10/minute from a single consumer trigger an automatic alert.
- 5 consecutive 401/403 responses trigger temporary consumer lockout (15 minutes).
- All security events are forwarded to `#ops-alerts` Slack channel.
- Incident response follows the platform runbook in `docs/runbooks/SECURITY_INCIDENT.md`.

---

*Governed by: `docs/contracts/API_AUTHORITY_BOUNDARIES.md`, `~/.claude/rules/secrets-policy.md`*
