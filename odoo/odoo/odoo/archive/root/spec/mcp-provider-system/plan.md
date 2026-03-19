# MCP Provider System - Implementation Plan

**Status**: READY FOR IMPLEMENTATION
**Estimated Effort**: 3-5 days
**Dependencies**: mcp-coordinator container, Supabase Vault, ops RBAC

---

## Phase 1: Foundation (Day 1)

### 1.1 Provider SDK Package

**Location**: `packages/mcp-provider-sdk/`

**Deliverables**:
```
packages/mcp-provider-sdk/
├── src/
│   ├── ProviderBase.ts           # Abstract base class
│   ├── types.ts                  # Shared types (OpsRole, HealthStatus, etc.)
│   ├── middleware/
│   │   ├── rbac.ts              # requireOpsAccess()
│   │   ├── events.ts            # emitEvent()
│   │   ├── vault.ts             # getVaultSecret()
│   │   └── hostnames.ts         # validateHostname()
│   └── index.ts
├── package.json
├── tsconfig.json
└── README.md
```

**Key Classes**:

```typescript
// src/ProviderBase.ts
export abstract class ProviderBase {
  protected name: string;
  protected allowedHosts: string[];
  protected vaultKeyPrefix: string;

  constructor(config: ProviderConfig) {
    this.name = config.name;
    this.allowedHosts = config.allowedHosts;
    this.vaultKeyPrefix = config.vaultKeyPrefix;
  }

  async requireOpsAccess(minRole: OpsRole): Promise<void> {
    // Get user from context (Supabase JWT)
    // Check app_metadata.ops_role >= minRole
    // Throw 403 if insufficient
  }

  async emitEvent(tool: string, payload: any, result: any, duration: number): Promise<void> {
    // INSERT INTO ops.run_events
  }

  async getVaultSecret(key: string): Promise<string> {
    // SELECT decrypted_secret FROM vault.secrets WHERE name = vaultKeyPrefix + key
  }

  validateHostname(url: string): void {
    // Parse URL, check hostname against allowedHosts
    // Support wildcards: *.ingest.sentry.io
  }

  abstract health(): Promise<HealthStatus>;
}
```

**Tests**: Unit tests for each middleware function

**Success Criteria**:
- ✅ SDK compiles with TypeScript
- ✅ All middleware functions tested
- ✅ Package published to workspace (pnpm)

---

### 1.2 Database Schema

**Location**: `supabase/migrations/20260216_mcp_provider_system.sql`

**Schema**:

```sql
-- ops.run_events table
CREATE TABLE IF NOT EXISTS ops.run_events (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  provider text NOT NULL,
  tool text NOT NULL,
  caller_id uuid REFERENCES auth.users(id),
  caller_role text NOT NULL,
  payload jsonb,
  result jsonb,
  error text,
  duration_ms int,
  hostname text,
  created_at timestamptz DEFAULT now()
);

CREATE INDEX idx_run_events_provider ON ops.run_events(provider, created_at DESC);
CREATE INDEX idx_run_events_caller ON ops.run_events(caller_id, created_at DESC);
CREATE INDEX idx_run_events_tool ON ops.run_events(provider, tool, created_at DESC);

-- RLS policies
ALTER TABLE ops.run_events ENABLE ROW LEVEL SECURITY;

CREATE POLICY "ops_viewer_own_events" ON ops.run_events
  FOR SELECT USING (
    caller_id = auth.uid() OR
    (SELECT app_metadata->>'ops_role' FROM auth.users WHERE id = auth.uid()) = 'ops_admin'
  );

-- Rate limiting table
CREATE TABLE IF NOT EXISTS ops.provider_rate_limits (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  provider text NOT NULL,
  tool text NOT NULL,
  user_id uuid REFERENCES auth.users(id),
  window_start timestamptz NOT NULL,
  call_count int NOT NULL DEFAULT 1,
  created_at timestamptz DEFAULT now(),
  UNIQUE(provider, tool, user_id, window_start)
);

CREATE INDEX idx_rate_limits_lookup ON ops.provider_rate_limits(provider, tool, user_id, window_start);
```

**Migration**:
```bash
supabase db push
```

**Success Criteria**:
- ✅ Schema deployed to dev/staging/prod
- ✅ RLS policies tested with different roles
- ✅ Indexes verified for performance

---

### 1.3 Provider Config SSOT

**Location**: `infra/mcp/provider-config.yaml`

**Format**:
```yaml
version: '1.0'
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
        schema_version: '1.0'
      - name: findings.list
        min_role: ops_viewer
        timeout_ms: 5000
        schema_version: '1.0'
      - name: health
        min_role: ops_viewer
        timeout_ms: 5000
        schema_version: '1.0'
```

**Generator Script**: `scripts/generate-mcp-artifacts.sh`
- Reads `provider-config.yaml`
- Generates TypeScript types for hub
- Generates docs for each provider

**Success Criteria**:
- ✅ YAML validates against schema
- ✅ Generator produces correct TypeScript
- ✅ CI enforces YAML-to-code sync

---

## Phase 2: Socket Provider (Day 2)

### 2.1 Socket Provider Implementation

**Location**: `mcp/coordinator/src/providers/socket/`

**Structure**:
```
mcp/coordinator/src/providers/socket/
├── index.ts                # SocketProvider class
├── types.ts                # Socket-specific types
├── tools/
│   ├── scan-repo.ts       # scan.repo implementation
│   ├── findings-list.ts   # findings.list implementation
│   └── health.ts          # health check
└── __tests__/
    ├── socket-provider.test.ts
    ├── scan-repo.test.ts
    └── health.test.ts
```

**Implementation**:

```typescript
// index.ts
import { ProviderBase, OpsRole } from '@ipai/mcp-provider-sdk';
import { scanRepo } from './tools/scan-repo';
import { findingsList } from './tools/findings-list';
import { health } from './tools/health';

export class SocketProvider extends ProviderBase {
  constructor() {
    super({
      name: 'socket',
      allowedHosts: ['api.socket.dev', 'socket.dev'],
      vaultKeyPrefix: 'socket_',
    });
  }

  async scanRepo(input: ScanRepoInput): Promise<ScanRepoOutput> {
    await this.requireOpsAccess('ops_operator');
    const start = Date.now();
    try {
      const result = await scanRepo(this, input);
      await this.emitEvent('scan.repo', input, result, Date.now() - start);
      return result;
    } catch (error) {
      await this.emitEvent('scan.repo', input, { error: error.message }, Date.now() - start);
      throw error;
    }
  }

  async findingsList(input: FindingsListInput): Promise<FindingsListOutput> {
    await this.requireOpsAccess('ops_viewer');
    const start = Date.now();
    try {
      const result = await findingsList(this, input);
      await this.emitEvent('findings.list', input, result, Date.now() - start);
      return result;
    } catch (error) {
      await this.emitEvent('findings.list', input, { error: error.message }, Date.now() - start);
      throw error;
    }
  }

  async health(): Promise<HealthStatus> {
    return await health(this);
  }
}
```

**Tool Implementations** (example: `scan-repo.ts`):

```typescript
export async function scanRepo(
  provider: SocketProvider,
  input: ScanRepoInput
): Promise<ScanRepoOutput> {
  const apiKey = await provider.getVaultSecret('api_key');
  const url = `https://api.socket.dev/v0/report`;

  provider.validateHostname(url);

  const response = await fetch(url, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${apiKey}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      repo: input.repo,
      ref: input.ref || 'HEAD'
    }),
    signal: AbortSignal.timeout(30000)
  });

  if (!response.ok) {
    throw new Error(`Socket API error: ${response.status} ${response.statusText}`);
  }

  return await response.json();
}
```

**Success Criteria**:
- ✅ All tools implemented and tested
- ✅ Error handling for API failures
- ✅ Timeout handling (5s-30s per tool)
- ✅ Unit tests coverage >80%

---

### 2.2 Hub Integration

**Location**: `mcp/coordinator/src/hub/`

**Router**:

```typescript
// mcp/coordinator/src/hub/router.ts
import { SocketProvider } from '../providers/socket';

const providers = {
  socket: new SocketProvider(),
  // future: sentry, netdata
};

app.post('/providers/:provider/:tool', async (req, res) => {
  const { provider: providerName, tool } = req.params;
  const provider = providers[providerName];

  if (!provider) {
    return res.status(404).json({ error: 'Provider not found' });
  }

  // Extract JWT from Authorization header
  const token = req.headers.authorization?.replace('Bearer ', '');
  if (!token) {
    return res.status(401).json({ error: 'Unauthorized' });
  }

  // Validate token and set context
  const user = await validateSupabaseJWT(token);
  setCurrentUser(user);

  // Call provider tool
  const method = tool.replace('.', '_'); // scan.repo -> scan_repo
  if (typeof provider[method] !== 'function') {
    return res.status(404).json({ error: 'Tool not found' });
  }

  try {
    const result = await provider[method](req.body);
    res.json(result);
  } catch (error) {
    if (error.statusCode === 403) {
      res.status(403).json({ error: 'Forbidden' });
    } else {
      res.status(500).json({ error: error.message });
    }
  }
});

app.get('/providers/:provider/health', async (req, res) => {
  const { provider: providerName } = req.params;
  const provider = providers[providerName];

  if (!provider) {
    return res.status(404).json({ error: 'Provider not found' });
  }

  const health = await provider.health();
  res.json(health);
});

// Aggregated health check
app.get('/health', async (req, res) => {
  const healthChecks = await Promise.all(
    Object.entries(providers).map(async ([name, provider]) => ({
      provider: name,
      ...await provider.health()
    }))
  );

  const allHealthy = healthChecks.every(h => h.status === 'ok');
  res.status(allHealthy ? 200 : 503).json({
    status: allHealthy ? 'ok' : 'degraded',
    providers: healthChecks
  });
});
```

**Success Criteria**:
- ✅ Router handles all provider/tool combinations
- ✅ JWT validation works
- ✅ Error responses follow standard format
- ✅ Aggregated health check returns all provider statuses

---

### 2.3 Vault Setup

**Action**: Store Socket API key in Supabase Vault

```bash
# Via Supabase CLI
supabase secrets set socket_api_key=<actual_key>

# Or via SQL
INSERT INTO vault.secrets (name, secret)
VALUES ('socket_api_key', 'your-socket-api-key-here');
```

**Access Control**:
```sql
-- Grant mcp-coordinator service role access to vault
GRANT SELECT ON vault.decrypted_secrets TO service_role;
```

**Success Criteria**:
- ✅ Key stored securely
- ✅ SDK can retrieve key
- ✅ No key visible in code/logs

---

## Phase 3: Agent Integration (Day 3)

### 3.1 Agent SDK Wrapper

**Location**: `packages/agent-sdk/src/providers/`

**Wrapper**:

```typescript
// packages/agent-sdk/src/providers/socket.ts
import { createClient } from '@supabase/supabase-js';

const supabase = createClient(
  process.env.SUPABASE_URL!,
  process.env.SUPABASE_SERVICE_ROLE_KEY!
);

export async function socketScanRepo(repo: string, ref?: string) {
  const { data: { session } } = await supabase.auth.getSession();
  if (!session) throw new Error('Not authenticated');

  const response = await fetch('https://mcp.insightpulseai.com/providers/socket/scan.repo', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${session.access_token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ repo, ref })
  });

  if (!response.ok) {
    throw new Error(`Socket scan failed: ${response.statusText}`);
  }

  return await response.json();
}

export async function socketFindingsList(severity?: string) {
  const { data: { session } } = await supabase.auth.getSession();
  if (!session) throw new Error('Not authenticated');

  const response = await fetch('https://mcp.insightpulseai.com/providers/socket/findings.list', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${session.access_token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ severity })
  });

  if (!response.ok) {
    throw new Error(`Socket findings failed: ${response.statusText}`);
  }

  return await response.json();
}
```

**Success Criteria**:
- ✅ Agent can call providers with simple API
- ✅ Auth handled transparently
- ✅ Errors propagated correctly

---

### 3.2 Example Agent Usage

**Location**: `agents/security-scanner/src/scan-dependencies.ts`

```typescript
import { socketScanRepo } from '@ipai/agent-sdk/providers/socket';

export async function scanDependencies(repo: string, ref: string) {
  console.log(`Scanning ${repo}@${ref} for supply-chain risks...`);

  const findings = await socketScanRepo(repo, ref);

  const critical = findings.filter(f => f.severity === 'critical');
  const high = findings.filter(f => f.severity === 'high');

  if (critical.length > 0) {
    console.error(`🚨 ${critical.length} critical vulnerabilities found!`);
    // Create GitHub issue
    // Block PR merge
  }

  if (high.length > 0) {
    console.warn(`⚠️ ${high.length} high-severity vulnerabilities found`);
    // Add PR comment
  }

  return {
    critical: critical.length,
    high: high.length,
    total: findings.length
  };
}
```

**Success Criteria**:
- ✅ Agent successfully scans repos
- ✅ Audit trail visible in ops.run_events
- ✅ RBAC enforced (ops_operator required)

---

## Phase 4: CI Integration (Day 4)

### 4.1 PR Dependency Gate

**Location**: `.github/workflows/pr-dependency-check.yml`

```yaml
name: PR Dependency Check

on:
  pull_request:
    branches: [main, develop]

jobs:
  socket-scan:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      pull-requests: write

    steps:
      - uses: actions/checkout@v4

      - name: Scan dependencies
        env:
          SUPABASE_URL: ${{ secrets.SUPABASE_URL }}
          SUPABASE_SERVICE_ROLE_KEY: ${{ secrets.SUPABASE_SERVICE_ROLE_KEY }}
        run: |
          npx tsx agents/security-scanner/src/scan-dependencies.ts \
            --repo="${{ github.repository }}" \
            --ref="${{ github.event.pull_request.head.sha }}"

      - name: Check results
        if: failure()
        uses: actions/github-script@v7
        with:
          script: |
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: '🚨 Critical supply-chain vulnerabilities detected. Review Socket findings before merging.'
            })
```

**Success Criteria**:
- ✅ Workflow runs on every PR
- ✅ Blocks merge if critical findings
- ✅ Comments on PR with results
- ✅ Audit trail in ops.run_events

---

### 4.2 Release Candidate Gate

**Location**: `.github/workflows/release-candidate.yml`

```yaml
name: Release Candidate Validation

on:
  push:
    branches: [release/*]

jobs:
  security-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Full security scan
        env:
          SUPABASE_URL: ${{ secrets.SUPABASE_URL }}
          SUPABASE_SERVICE_ROLE_KEY: ${{ secrets.SUPABASE_SERVICE_ROLE_KEY }}
        run: |
          npx tsx agents/security-scanner/src/scan-dependencies.ts \
            --repo="${{ github.repository }}" \
            --ref="${{ github.sha }}" \
            --severity=high \
            --fail-on-findings

      - name: Upload findings
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: socket-findings
          path: socket-findings.json
```

**Success Criteria**:
- ✅ Release branches scanned before deploy
- ✅ High+ severity blocks release
- ✅ Findings archived as artifacts

---

## Phase 5: Documentation & Monitoring (Day 5)

### 5.1 Provider Documentation

**Location**: `docs/architecture/MCP_PROVIDERS.md`

**Auto-Generated From**:
- `infra/mcp/provider-config.yaml`
- Provider SDK type definitions
- Example usage from agents

**Content**:
- Provider purpose and use cases
- Tool catalog with schemas
- RBAC requirements per tool
- Rate limits
- Health check endpoints
- Example agent code

**Generator**: `scripts/generate-provider-docs.sh`

**Success Criteria**:
- ✅ Docs generated from SSOT config
- ✅ Examples work copy-paste
- ✅ RBAC requirements clear

---

### 5.2 Ops Dashboard

**Location**: `web/ops-console/src/pages/providers/`

**Features**:
- Provider health status (live)
- Recent operations (ops.run_events)
- Rate limit status per user
- Provider API quota usage
- Error rate graphs

**Success Criteria**:
- ✅ Real-time health monitoring
- ✅ Audit trail searchable
- ✅ Alerts on provider degradation

---

## Phase 6: Sentry & Netdata (Days 6-8)

**Repeat Phase 2-3 for each provider**:

1. Implement `SentryProvider` extending `ProviderBase`
2. Add to hub router
3. Store DSN in Vault
4. Create agent SDK wrapper
5. Add CI integration examples
6. Update docs

**Success Criteria**:
- ✅ 3 providers operational (Socket, Sentry, Netdata)
- ✅ <2 hour integration time (proves SDK works)
- ✅ All providers follow same patterns

---

## Rollout Strategy

### Development
- ✅ Socket provider on staging
- ✅ Test with non-critical repos
- ✅ Verify audit trail

### Staging
- ✅ All 3 providers enabled
- ✅ CI gates active
- ✅ Ops team trained

### Production
- ✅ Gradual rollout (Socket → Sentry → Netdata)
- ✅ Monitor error rates
- ✅ 7-day burn-in period per provider

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Provider API outage | Agents fail | Health checks + graceful degradation |
| RBAC misconfiguration | Unauthorized access | Comprehensive tests + staging validation |
| Rate limit exceeded | 429 errors | Per-role quotas + dashboard monitoring |
| Secret rotation | Service disruption | Vault + automated credential refresh |
| Schema breaking changes | Agent failures | Versioned tools + backward compatibility |

---

## Success Metrics

- ✅ 3 providers operational
- ✅ 100% ops actions audited
- ✅ <100ms RBAC overhead
- ✅ <5s health checks
- ✅ Zero secrets in code/env
- ✅ 5+ agents using providers
- ✅ CI dependency gate active on all repos

---

## Related Documents

- `spec/mcp-provider-system/constitution.md` - Governance rules
- `spec/mcp-provider-system/prd.md` - Product requirements
- `spec/mcp-provider-system/tasks.md` - Task breakdown
