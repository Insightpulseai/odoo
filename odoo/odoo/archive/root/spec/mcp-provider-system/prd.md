# MCP Provider System - Product Requirements

**Status**: DRAFT
**Target Release**: 2026-Q1
**Owner**: DevOps + Security
**Stakeholders**: All agent developers, Ops team

---

## Problem Statement

### Current Pain Points

1. **MCP Provider Sprawl**: Socket MCP exists, Sentry/Netdata coming, no governance
2. **Auth Chaos**: Each provider has different auth model (API keys, OAuth, tokens)
3. **Dark Operations**: No audit trail for provider actions (who scanned what, when?)
4. **Security Gaps**: Secrets in env vars, no hostname validation, direct external calls
5. **Integration Friction**: Each provider needs custom wrapper, agent-specific patterns

### Impact

- **Security Risk**: Unaudited ops actions, leaked credentials
- **Developer Friction**: 3-5 days to integrate new provider
- **Compliance Gap**: No audit trail for SOC2/ISO27001
- **Cost Opacity**: Can't attribute API costs to users/teams

---

## Goals & Non-Goals

### Goals

✅ **P0**: Unified provider architecture (Socket, Sentry, Netdata via single gateway)
✅ **P0**: RBAC enforcement (ops_viewer/operator/admin)
✅ **P0**: Complete audit trail (ops.run_events for all actions)
✅ **P1**: <2 hour integration time for new providers
✅ **P1**: Zero secrets in code/env (100% Vault)
✅ **P2**: Auto-generated provider docs from schemas

### Non-Goals

❌ Building new MCP providers (use existing: Socket, Sentry, Netdata)
❌ Real-time streaming (batch operations only for now)
❌ Multi-tenant isolation (single org for now)
❌ Provider marketplace (curated list only)

---

## User Stories

### As an Agent Developer

**Story 1**: Integrate Socket MCP into agent
```
GIVEN I need supply-chain risk data
WHEN I call socketProvider.scan.repo('main')
THEN I get findings without managing auth/secrets
AND the operation is automatically audited
```

**Story 2**: Handle provider outages gracefully
```
GIVEN Socket API is down
WHEN I call socketProvider.health()
THEN I get status='down' in <5s
AND can degrade agent behavior accordingly
```

**Story 3**: Debug failed scans
```
GIVEN a scan failed yesterday
WHEN I query ops.run_events
THEN I see payload, error, duration for that scan
AND can reproduce the issue locally
```

### As an Ops Operator

**Story 4**: Scan repo for supply-chain risks
```
GIVEN I have ops_operator role
WHEN I run socket scan on PR branch
THEN I get findings report
AND can annotate false positives
AND the scan is logged to ops.run_events
```

**Story 5**: Review audit trail
```
GIVEN I need to investigate a security incident
WHEN I query ops.run_events for provider='socket'
THEN I see all scans, by whom, when, results
AND can filter by date, user, severity
```

### As an Ops Admin

**Story 6**: Add new provider (Sentry)
```
GIVEN I have Sentry API key
WHEN I:
  1. Store key in Supabase Vault as 'sentry_dsn'
  2. Implement SentryProvider extends ProviderBase
  3. Register in hub config
THEN hub loads provider automatically
AND enforces RBAC/audit/secrets rules
```

**Story 7**: Rotate Socket API key
```
GIVEN Socket API key is compromised
WHEN I update 'socket_api_key' in Vault
THEN all providers pick up new key within 60s
AND old key is revoked
AND no code changes required
```

---

## Architecture Overview

### Component Diagram

```
┌─────────────────────────────────────────────────────────┐
│ mcp.insightpulseai.com (Hub)                            │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌─────────────────┐                                   │
│  │ Hub Router      │  ← nginx reverse proxy            │
│  └────────┬────────┘                                   │
│           │                                            │
│  ┌────────▼────────┐                                   │
│  │ Auth Middleware │  ← Supabase JWT validation       │
│  │ (RBAC Check)    │                                   │
│  └────────┬────────┘                                   │
│           │                                            │
│  ┌────────▼────────┐                                   │
│  │ Provider SDK    │  ← Base class for all providers   │
│  │ - emitEvent()   │                                   │
│  │ - getVaultSecret()                                  │
│  │ - validateHost()│                                   │
│  └────────┬────────┘                                   │
│           │                                            │
│  ┌────────┴────────────────────┐                       │
│  │                             │                       │
│  ▼                             ▼                       │
│ ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │
│ │Socket       │  │Sentry       │  │Netdata      │    │
│ │Provider     │  │Provider     │  │Provider     │    │
│ ├─────────────┤  ├─────────────┤  ├─────────────┤    │
│ │scan.repo    │  │captureError │  │metrics.query│    │
│ │findings.list│  │createIssue  │  │alerts.list  │    │
│ │health       │  │health       │  │health       │    │
│ └──────┬──────┘  └──────┬──────┘  └──────┬──────┘    │
│        │                │                │            │
│        ▼                ▼                ▼            │
│   api.socket.dev   sentry.io      app.netdata.cloud  │
└─────────────────────────────────────────────────────────┘
        │                │                │
        ▼                ▼                ▼
   ┌────────────────────────────────────────┐
   │ Supabase                               │
   ├────────────────────────────────────────┤
   │ ops.run_events (audit trail)           │
   │ vault.secrets (API keys)               │
   │ auth.users (RBAC)                      │
   └────────────────────────────────────────┘
```

### Data Flow (Socket Scan Example)

```
1. Agent → POST /providers/socket/scan.repo
   Headers: Authorization: Bearer {supabase_jwt}
   Body: { repo: 'odoo', ref: 'main' }

2. Hub → Validate JWT, extract user_id

3. Hub → Check RBAC: user.app_metadata.ops_role >= 'ops_operator'

4. Hub → Get secret: vault.get('socket_api_key')

5. Hub → Validate hostname: 'api.socket.dev' in allowlist

6. Hub → Call Socket API with key

7. Socket API → Return findings

8. Hub → Emit event:
   INSERT INTO ops.run_events (provider, tool, caller_id, result)

9. Hub → Return findings to agent
```

---

## Provider SDK API

### ProviderBase Class

```typescript
import { ProviderBase, OpsRole, HealthStatus } from '@ipai/mcp-provider-sdk';

export class SocketProvider extends ProviderBase {
  constructor() {
    super({
      name: 'socket',
      allowedHosts: ['api.socket.dev', 'socket.dev'],
      vaultKeyPrefix: 'socket_',
    });
  }

  async scanRepo(input: ScanRepoInput): Promise<ScanRepoOutput> {
    // Automatic: requireOpsAccess('ops_operator')
    // Automatic: getVaultSecret('socket_api_key')
    // Automatic: validateHostname() on fetch()
    // Automatic: emitEvent() on completion

    const key = await this.getVaultSecret('api_key');
    const url = 'https://api.socket.dev/v0/report';

    await this.validateHostname(url); // throws if not in allowlist

    const response = await fetch(url, {
      headers: { 'Authorization': `Bearer ${key}` }
    });

    const result = await response.json();

    // emitEvent() called automatically by SDK
    return result;
  }

  async health(): Promise<HealthStatus> {
    // Required by ProviderBase
    const start = Date.now();
    try {
      const key = await this.getVaultSecret('api_key');
      const response = await fetch('https://api.socket.dev/health', {
        headers: { 'Authorization': `Bearer ${key}` },
        signal: AbortSignal.timeout(5000)
      });
      return {
        provider: 'socket',
        status: response.ok ? 'ok' : 'degraded',
        latency_ms: Date.now() - start,
        last_check: new Date().toISOString(),
        error: null
      };
    } catch (error) {
      return {
        provider: 'socket',
        status: 'down',
        latency_ms: Date.now() - start,
        last_check: new Date().toISOString(),
        error: error.message
      };
    }
  }
}
```

### Provider Registration

```typescript
// mcp-coordinator/src/providers/index.ts
import { SocketProvider } from './socket';
import { SentryProvider } from './sentry';
import { NetdataProvider } from './netdata';

export const providers = {
  socket: new SocketProvider(),
  sentry: new SentryProvider(),
  netdata: new NetdataProvider(),
};

// Hub auto-loads and validates all providers on startup
```

---

## Database Schema

### ops.run_events

```sql
CREATE TABLE ops.run_events (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  provider text NOT NULL,           -- 'socket', 'sentry', 'netdata'
  tool text NOT NULL,                -- 'scan.repo', 'findings.list'
  caller_id uuid REFERENCES auth.users(id),
  caller_role text NOT NULL,         -- 'ops_viewer', 'ops_operator', 'ops_admin'
  payload jsonb,                     -- input parameters
  result jsonb,                      -- output data
  error text,                        -- error message if failed
  duration_ms int,                   -- execution time
  hostname text,                     -- external API called
  created_at timestamptz DEFAULT now()
);

CREATE INDEX idx_run_events_provider ON ops.run_events(provider, created_at DESC);
CREATE INDEX idx_run_events_caller ON ops.run_events(caller_id, created_at DESC);
CREATE INDEX idx_run_events_tool ON ops.run_events(provider, tool, created_at DESC);

-- RLS: ops_viewer+ can read their own events, ops_admin can read all
ALTER TABLE ops.run_events ENABLE ROW LEVEL SECURITY;

CREATE POLICY "ops_viewer_own_events" ON ops.run_events
  FOR SELECT USING (caller_id = auth.uid() OR
                    (SELECT app_metadata->>'ops_role' FROM auth.users WHERE id = auth.uid()) = 'ops_admin');
```

### Provider Config

```yaml
# infra/mcp/provider-config.yaml
providers:
  socket:
    enabled: true
    vault_key: socket_api_key
    allowed_hosts:
      - api.socket.dev
      - socket.dev
    rate_limits:
      ops_viewer: { reads: 100/hour }
      ops_operator: { scans: 50/hour, reads: 200/hour }
      ops_admin: unlimited
    tools:
      - name: scan.repo
        min_role: ops_operator
        timeout_ms: 30000
      - name: findings.list
        min_role: ops_viewer
        timeout_ms: 5000
      - name: health
        min_role: ops_viewer
        timeout_ms: 5000

  sentry:
    enabled: true
    vault_key: sentry_dsn
    allowed_hosts:
      - sentry.io
      - "*.ingest.sentry.io"
    rate_limits:
      ops_viewer: { reads: 500/hour }
      ops_operator: { writes: 100/hour, reads: 500/hour }
      ops_admin: unlimited
    tools:
      - name: capture.error
        min_role: ops_operator
        timeout_ms: 10000
      - name: issues.list
        min_role: ops_viewer
        timeout_ms: 5000
      - name: health
        min_role: ops_viewer
        timeout_ms: 5000

  netdata:
    enabled: false  # coming soon
    vault_key: netdata_token
    allowed_hosts:
      - app.netdata.cloud
      - "*.netdata.cloud"
```

---

## Security Considerations

### Threat Model

| Threat | Mitigation |
|--------|------------|
| Leaked API keys | Vault storage + rotation |
| Unauthorized scans | RBAC + JWT validation |
| Data exfiltration | Hostname allowlist |
| Audit trail tampering | Immutable events table |
| Provider compromise | SDK validation + health checks |
| SSRF attacks | URL validation before fetch |
| Cost overrun | Rate limiting per role |

### Compliance

- **SOC2**: Complete audit trail (ops.run_events)
- **ISO27001**: RBAC enforcement, secret rotation
- **GDPR**: No PII in provider calls (repo names only)

---

## Success Metrics

### Phase 1 (Socket MCP)

- ✅ Socket provider live via hub
- ✅ 100% ops actions audited
- ✅ <100ms RBAC overhead
- ✅ Zero secrets in code/env
- ✅ Health check <5s

### Phase 2 (Sentry + Netdata)

- ✅ 3 providers operational
- ✅ <2 hour integration time for new providers
- ✅ Agent adoption: 5+ agents using providers
- ✅ CI integration: PR dependency gate

### Phase 3 (Ecosystem)

- ✅ 5+ providers
- ✅ Auto-generated provider docs
- ✅ Provider health dashboard
- ✅ Cost attribution by user/team

---

## Open Questions

1. **Provider Versioning**: How to handle breaking changes in external APIs?
   - **Proposal**: Versioned tool names (`scan.repo.v2`)

2. **Cross-Provider Queries**: Should hub support joins across providers?
   - **Proposal**: No, agents compose (see Constitution Rule 7)

3. **Real-time Events**: Should providers support WebSocket streams?
   - **Proposal**: Defer to Phase 4, batch polling for now

4. **Provider Quotas**: Should we track API usage per provider?
   - **Proposal**: Yes, emit to `ops.provider_quotas` table

---

## Related Documents

- `spec/mcp-provider-system/constitution.md` - Governance rules
- `spec/mcp-provider-system/plan.md` - Implementation plan
- `spec/ops-rbac-model/` - Ops role definitions
- `infra/mcp/provider-allowlist.yaml` - Hostname allowlist
