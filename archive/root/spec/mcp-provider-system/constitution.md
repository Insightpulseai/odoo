# MCP Provider System - Constitution

**Last Updated**: 2026-02-16
**Status**: CANONICAL
**Scope**: All MCP providers (Socket, Sentry, Netdata, future)

---

## Non-Negotiable Principles

### 1. Single Gateway Architecture

**Rule**: All MCP providers MUST route through `mcp.insightpulseai.com`.

**Rationale**:
- Unified auth/RBAC enforcement
- Centralized audit trail
- Single TLS termination point
- Prevents provider sprawl

**Enforcement**: No provider gets its own subdomain. Period.

---

### 2. Supabase-Native RBAC

**Rule**: All provider operations MUST call `requireOpsAccess(role)` before execution.

**Roles** (canonical):
```yaml
ops_viewer:   read findings, health checks
ops_operator: scan, annotate, tag
ops_admin:    create issues, PR comments, policy changes
```

**Rationale**: Ops actions have production consequences. No cowboy tooling.

**Enforcement**: Provider wrapper checks `auth.users.app_metadata.ops_role` before every tool call.

---

### 3. Event Sourcing Mandatory

**Rule**: Every provider operation MUST emit to `ops.run_events` table.

**Schema** (non-negotiable):
```sql
ops.run_events (
  id uuid primary key,
  provider text not null,        -- 'socket', 'sentry', 'netdata'
  tool text not null,             -- 'scan.repo', 'findings.list'
  caller_id uuid references auth.users,
  payload jsonb,
  result jsonb,
  duration_ms int,
  created_at timestamptz default now()
)
```

**Rationale**: Ops observability, audit compliance, debugging, cost attribution.

**Enforcement**: Provider SDK intercepts all tool calls and emits events automatically.

---

### 4. Secrets in Vault Only

**Rule**: Provider API keys MUST be stored in Supabase Vault, never in env vars or code.

**Naming Convention**:
```
socket_api_key
sentry_dsn
netdata_token
```

**Access Pattern**:
```typescript
const key = await vault.get('socket_api_key', { context: 'mcp-coordinator' });
```

**Rationale**: Rotation, auditing, least-privilege access.

**Enforcement**: CI rejects any provider code with hardcoded tokens.

---

### 5. Hostname Allowlist Enforcement

**Rule**: Providers MUST only call approved external APIs.

**Allowlist** (`infra/mcp/provider-allowlist.yaml`):
```yaml
socket:
  - api.socket.dev
  - socket.dev
sentry:
  - sentry.io
  - *.ingest.sentry.io
netdata:
  - app.netdata.cloud
  - *.netdata.cloud
```

**Rationale**: Prevent data exfiltration, supply-chain attacks.

**Enforcement**: Provider SDK validates all HTTP calls against allowlist before execution.

---

### 6. Health Checks Required

**Rule**: Every provider MUST expose `{provider}.health()` tool.

**Response Format**:
```json
{
  "provider": "socket",
  "status": "ok|degraded|down",
  "latency_ms": 123,
  "last_check": "2026-02-16T15:46:00Z",
  "error": null
}
```

**SLA**: Health checks must complete in <5s or return `degraded`.

**Rationale**: Hub can fail-fast on degraded providers.

**Enforcement**: Hub health endpoint aggregates all provider health checks.

---

### 7. Provider Independence

**Rule**: Providers MUST NOT call each other. All composition happens at agent layer.

**Example** (WRONG):
```typescript
// ❌ Socket provider calling Sentry
socket.scan() → sentry.captureException()
```

**Example** (RIGHT):
```typescript
// ✅ Agent orchestrates both
const findings = await socket.scan();
if (findings.critical > 0) {
  await sentry.captureMessage('Critical findings detected');
}
```

**Rationale**: Prevents circular dependencies, simplifies testing, clear responsibilities.

**Enforcement**: Provider SDK blocks all internal MCP calls.

---

### 8. Rate Limiting by Role

**Rule**: Tool calls MUST be rate-limited per user role.

**Limits** (canonical):
```yaml
ops_viewer:   100 reads/hour
ops_operator: 50 scans/hour, 200 reads/hour
ops_admin:    unlimited (with audit)
```

**Rationale**: Cost control, abuse prevention, API quota management.

**Enforcement**: Hub tracks calls per (user, provider, tool) and blocks when exceeded.

---

### 9. Schema Versioning

**Rule**: Provider tool schemas MUST be versioned and backward-compatible.

**Format**:
```typescript
interface SocketScanInput {
  version: '1.0' | '2.0';  // explicit version
  repo: string;
  ref?: string;
}
```

**Breaking Changes**: Require new tool name (e.g., `scan.repo.v2`).

**Rationale**: Agents depend on stable schemas.

**Enforcement**: CI runs schema validation tests on every provider change.

---

### 10. Provider SDK Standardization

**Rule**: All providers MUST use the canonical provider SDK.

**SDK Location**: `packages/mcp-provider-sdk/`

**Required Exports**:
```typescript
export class ProviderBase {
  requireOpsAccess(role: OpsRole): Promise<void>;
  emitEvent(tool: string, payload: any, result: any): Promise<void>;
  getVaultSecret(key: string): Promise<string>;
  validateHostname(url: string): void;
  health(): Promise<HealthStatus>;
}
```

**Rationale**: DRY, consistent behavior, centralized updates.

**Enforcement**: Providers failing to extend `ProviderBase` are rejected by hub.

---

## Deviation Protocol

**Requesting Exception**:
1. Create spec bundle: `spec/mcp-exception-{provider}-{rule}/`
2. Document why exception needed (technical, not preference)
3. Propose compensating controls
4. Get ops_admin approval
5. Set expiration date (max 90 days)

**Allowed Exceptions**: NONE for rules 1-4 (gateway, RBAC, events, vault).

**Review Cadence**: All exceptions reviewed monthly. Expired exceptions = auto-revoked.

---

## Enforcement Mechanisms

| Rule | Enforcement Layer | Failure Mode |
|------|------------------|--------------|
| 1. Single Gateway | DNS + nginx | 404 on direct provider access |
| 2. RBAC | Provider SDK | 403 Forbidden |
| 3. Event Sourcing | Provider SDK | Tool call blocks until event written |
| 4. Vault Secrets | CI + Runtime | Build failure / runtime error |
| 5. Hostname Allowlist | Provider SDK | Network call rejected |
| 6. Health Checks | Hub aggregator | Provider marked `down` |
| 7. Provider Independence | Provider SDK | Import/call blocked |
| 8. Rate Limiting | Hub middleware | 429 Too Many Requests |
| 9. Schema Versioning | CI tests | Build failure |
| 10. SDK Standard | Hub registration | Provider rejected |

---

## Success Criteria

✅ **All providers follow these rules**
✅ **Zero direct provider access** (everything via hub)
✅ **100% ops event coverage** (no dark operations)
✅ **<100ms RBAC check overhead** per tool call
✅ **Zero secrets in code/env** (all in Vault)

---

## Related Specs

- `spec/ops-rbac-model/` - Ops role definitions
- `spec/supabase-vault-integration/` - Secret management
- `spec/mcp-hub-architecture/` - Hub design
- `infra/mcp/provider-allowlist.yaml` - Hostname allowlist

---

**This constitution is immutable for 90 days from creation. Any changes require ops_admin unanimous approval.**
