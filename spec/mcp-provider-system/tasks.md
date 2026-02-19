# MCP Provider System - Task Breakdown

**Status**: READY FOR EXECUTION
**Total Tasks**: 28
**Estimated Total Effort**: 3-5 days

---

## Task 1: Create Provider SDK Package Structure
**Effort**: 1 hour
**Dependencies**: None
**Assignee**: Backend

**Actions**:
```bash
mkdir -p packages/mcp-provider-sdk/src/middleware
cd packages/mcp-provider-sdk
pnpm init
```

**Files**:
- `packages/mcp-provider-sdk/package.json`
- `packages/mcp-provider-sdk/tsconfig.json`
- `packages/mcp-provider-sdk/src/index.ts`

**Success Criteria**:
- ✅ Package compiles with TypeScript
- ✅ Added to workspace root `pnpm-workspace.yaml`

---

## Task 2: Implement ProviderBase Class
**Effort**: 2 hours
**Dependencies**: Task 1
**Assignee**: Backend

**Implementation**:
```typescript
// packages/mcp-provider-sdk/src/ProviderBase.ts
export abstract class ProviderBase {
  protected name: string;
  protected allowedHosts: string[];
  protected vaultKeyPrefix: string;

  constructor(config: ProviderConfig);
  async requireOpsAccess(minRole: OpsRole): Promise<void>;
  async emitEvent(tool: string, payload: any, result: any, duration: number): Promise<void>;
  async getVaultSecret(key: string): Promise<string>;
  validateHostname(url: string): void;
  abstract health(): Promise<HealthStatus>;
}
```

**Success Criteria**:
- ✅ Class compiles
- ✅ All methods have type signatures
- ✅ JSDoc comments added

---

## Task 3: Implement RBAC Middleware
**Effort**: 2 hours
**Dependencies**: Task 2
**Assignee**: Backend

**Implementation**:
```typescript
// packages/mcp-provider-sdk/src/middleware/rbac.ts
export async function requireOpsAccess(minRole: OpsRole): Promise<void> {
  const user = getCurrentUser(); // from context
  if (!user) throw new UnauthorizedError();

  const userRole = user.app_metadata?.ops_role;
  if (!hasRole(userRole, minRole)) {
    throw new ForbiddenError(`Requires ${minRole}, has ${userRole}`);
  }
}

function hasRole(userRole: string, minRole: OpsRole): boolean {
  const hierarchy = {
    ops_viewer: 1,
    ops_operator: 2,
    ops_admin: 3
  };
  return hierarchy[userRole] >= hierarchy[minRole];
}
```

**Tests**:
- ✅ ops_viewer cannot call ops_operator tools
- ✅ ops_admin can call all tools
- ✅ Unauthenticated throws 401
- ✅ Insufficient role throws 403

**Success Criteria**:
- ✅ All tests pass
- ✅ Error messages clear

---

## Task 4: Implement Event Emitter
**Effort**: 1.5 hours
**Dependencies**: Task 2
**Assignee**: Backend

**Implementation**:
```typescript
// packages/mcp-provider-sdk/src/middleware/events.ts
export async function emitEvent(
  provider: string,
  tool: string,
  payload: any,
  result: any,
  duration: number
): Promise<void> {
  const user = getCurrentUser();

  await supabase.from('ops.run_events').insert({
    provider,
    tool,
    caller_id: user.id,
    caller_role: user.app_metadata.ops_role,
    payload,
    result,
    duration_ms: duration,
    hostname: extractHostname(payload)
  });
}
```

**Tests**:
- ✅ Event written to database
- ✅ All required fields present
- ✅ Handles errors gracefully

**Success Criteria**:
- ✅ Events visible in Supabase dashboard
- ✅ No data loss on errors

---

## Task 5: Implement Vault Secret Retrieval
**Effort**: 1.5 hours
**Dependencies**: Task 2
**Assignee**: Backend

**Implementation**:
```typescript
// packages/mcp-provider-sdk/src/middleware/vault.ts
export async function getVaultSecret(key: string): Promise<string> {
  const { data, error } = await supabase
    .from('vault.decrypted_secrets')
    .select('decrypted_secret')
    .eq('name', key)
    .single();

  if (error || !data) {
    throw new VaultError(`Secret ${key} not found`);
  }

  return data.decrypted_secret;
}
```

**Tests**:
- ✅ Retrieves existing secret
- ✅ Throws on missing secret
- ✅ Does not log secret value

**Success Criteria**:
- ✅ Secrets never logged
- ✅ Error handling correct

---

## Task 6: Implement Hostname Validation
**Effort**: 1 hour
**Dependencies**: Task 2
**Assignee**: Backend

**Implementation**:
```typescript
// packages/mcp-provider-sdk/src/middleware/hostnames.ts
export function validateHostname(url: string, allowedHosts: string[]): void {
  const hostname = new URL(url).hostname;

  const allowed = allowedHosts.some(pattern => {
    if (pattern.startsWith('*.')) {
      return hostname.endsWith(pattern.slice(2));
    }
    return hostname === pattern;
  });

  if (!allowed) {
    throw new HostnameError(`${hostname} not in allowlist`);
  }
}
```

**Tests**:
- ✅ Exact match allowed
- ✅ Wildcard match allowed
- ✅ Non-match throws error
- ✅ Invalid URL throws error

**Success Criteria**:
- ✅ Prevents SSRF attacks
- ✅ Wildcard support works

---

## Task 7: Create Database Migration
**Effort**: 1 hour
**Dependencies**: None
**Assignee**: Backend

**Migration**:
```sql
-- supabase/migrations/20260216_mcp_provider_system.sql
CREATE TABLE ops.run_events (...);
CREATE TABLE ops.provider_rate_limits (...);
-- See plan.md for full schema
```

**Actions**:
```bash
supabase migration new mcp_provider_system
# Edit migration file
supabase db push
```

**Success Criteria**:
- ✅ Migration applies cleanly
- ✅ Indexes created
- ✅ RLS policies active

---

## Task 8: Create Provider Config SSOT
**Effort**: 1 hour
**Dependencies**: None
**Assignee**: DevOps

**File**: `infra/mcp/provider-config.yaml`

**Content**:
```yaml
version: '1.0'
providers:
  socket:
    enabled: true
    vault_key: socket_api_key
    allowed_hosts:
      - api.socket.dev
      - socket.dev
    # ... (see plan.md)
```

**Success Criteria**:
- ✅ YAML validates against schema
- ✅ Socket config complete

---

## Task 9: Implement Socket Provider Class
**Effort**: 3 hours
**Dependencies**: Tasks 2-6
**Assignee**: Backend

**File**: `mcp/coordinator/src/providers/socket/index.ts`

**Implementation**:
```typescript
export class SocketProvider extends ProviderBase {
  constructor() {
    super({
      name: 'socket',
      allowedHosts: ['api.socket.dev', 'socket.dev'],
      vaultKeyPrefix: 'socket_'
    });
  }

  async scanRepo(input: ScanRepoInput): Promise<ScanRepoOutput> {
    await this.requireOpsAccess('ops_operator');
    // ... implementation
  }

  async findingsList(input: FindingsListInput): Promise<FindingsListOutput> {
    await this.requireOpsAccess('ops_viewer');
    // ... implementation
  }

  async health(): Promise<HealthStatus> {
    // ... implementation
  }
}
```

**Success Criteria**:
- ✅ All tools implemented
- ✅ Extends ProviderBase correctly
- ✅ Type-safe

---

## Task 10: Implement scan.repo Tool
**Effort**: 2 hours
**Dependencies**: Task 9
**Assignee**: Backend

**File**: `mcp/coordinator/src/providers/socket/tools/scan-repo.ts`

**Implementation**: See plan.md

**Tests**:
- ✅ Successful scan returns findings
- ✅ Invalid repo throws error
- ✅ Timeout handled (30s)
- ✅ API errors surfaced

**Success Criteria**:
- ✅ Integration test with Socket API
- ✅ Error handling comprehensive

---

## Task 11: Implement findings.list Tool
**Effort**: 1.5 hours
**Dependencies**: Task 9
**Assignee**: Backend

**File**: `mcp/coordinator/src/providers/socket/tools/findings-list.ts`

**Implementation**: Query Socket API for findings with filters

**Tests**:
- ✅ Filter by severity works
- ✅ Pagination works
- ✅ Empty results handled

**Success Criteria**:
- ✅ Returns correct data structure
- ✅ Filters validated

---

## Task 12: Implement health Tool
**Effort**: 1 hour
**Dependencies**: Task 9
**Assignee**: Backend

**File**: `mcp/coordinator/src/providers/socket/tools/health.ts`

**Implementation**: Ping Socket API, return status

**Tests**:
- ✅ Healthy state returns 'ok'
- ✅ Timeout returns 'degraded'
- ✅ API down returns 'down'
- ✅ Completes in <5s

**Success Criteria**:
- ✅ Never blocks >5s
- ✅ Clear error messages

---

## Task 13: Store Socket API Key in Vault
**Effort**: 15 minutes
**Dependencies**: Task 7
**Assignee**: DevOps

**Actions**:
```bash
supabase secrets set socket_api_key=<actual_key>
```

**Verification**:
```sql
SELECT name FROM vault.secrets WHERE name = 'socket_api_key';
```

**Success Criteria**:
- ✅ Key retrievable by SDK
- ✅ Not visible in logs

---

## Task 14: Implement Hub Router
**Effort**: 2 hours
**Dependencies**: Task 9
**Assignee**: Backend

**File**: `mcp/coordinator/src/hub/router.ts`

**Implementation**: See plan.md

**Tests**:
- ✅ Routes to correct provider
- ✅ JWT validation works
- ✅ Error responses standardized
- ✅ Health endpoint aggregates

**Success Criteria**:
- ✅ All endpoints respond correctly
- ✅ Integration tests pass

---

## Task 15: Add Provider Unit Tests
**Effort**: 2 hours
**Dependencies**: Tasks 10-12
**Assignee**: Backend

**Files**:
- `mcp/coordinator/src/providers/socket/__tests__/socket-provider.test.ts`
- `mcp/coordinator/src/providers/socket/__tests__/scan-repo.test.ts`
- `mcp/coordinator/src/providers/socket/__tests__/health.test.ts`

**Coverage Target**: >80%

**Success Criteria**:
- ✅ All tests pass
- ✅ Coverage meets target
- ✅ Mocks external APIs

---

## Task 16: Update nginx Config for Hub
**Effort**: 30 minutes
**Dependencies**: Task 14
**Assignee**: DevOps

**File**: Already exists at `/etc/nginx/sites-available/mcp.insightpulseai.com`

**Verification**:
```bash
curl https://mcp.insightpulseai.com/health
```

**Success Criteria**:
- ✅ Hub accessible via domain
- ✅ SSL working
- ✅ Reverse proxy correct

---

## Task 17: Create Agent SDK Wrapper
**Effort**: 1.5 hours
**Dependencies**: Task 14
**Assignee**: Backend

**File**: `packages/agent-sdk/src/providers/socket.ts`

**Implementation**: See plan.md

**Tests**:
- ✅ Auth handled transparently
- ✅ Errors propagated correctly

**Success Criteria**:
- ✅ Simple API for agents
- ✅ Documentation complete

---

## Task 18: Create Example Agent
**Effort**: 2 hours
**Dependencies**: Task 17
**Assignee**: Backend

**File**: `agents/security-scanner/src/scan-dependencies.ts`

**Implementation**: See plan.md

**Success Criteria**:
- ✅ Agent scans repos successfully
- ✅ Audit trail visible in Supabase
- ✅ RBAC enforced

---

## Task 19: Add PR Dependency Check Workflow
**Effort**: 1.5 hours
**Dependencies**: Task 18
**Assignee**: DevOps

**File**: `.github/workflows/pr-dependency-check.yml`

**Implementation**: See plan.md

**Tests**:
- ✅ Workflow runs on test PR
- ✅ Blocks merge on critical findings
- ✅ Comments on PR

**Success Criteria**:
- ✅ Workflow operational
- ✅ Comments formatted correctly

---

## Task 20: Add Release Candidate Gate
**Effort**: 1 hour
**Dependencies**: Task 18
**Assignee**: DevOps

**File**: `.github/workflows/release-candidate.yml`

**Implementation**: See plan.md

**Success Criteria**:
- ✅ Release branches scanned
- ✅ High+ severity blocks
- ✅ Findings archived

---

## Task 21: Create Provider Documentation
**Effort**: 2 hours
**Dependencies**: Tasks 9-12
**Assignee**: Technical Writer

**File**: `docs/architecture/MCP_PROVIDERS.md`

**Content**:
- Provider overview
- Tool catalog with schemas
- RBAC requirements
- Example usage
- Health check endpoints

**Success Criteria**:
- ✅ Examples work copy-paste
- ✅ Clear and comprehensive

---

## Task 22: Create Documentation Generator
**Effort**: 2 hours
**Dependencies**: Task 8, 21
**Assignee**: Backend

**File**: `scripts/generate-provider-docs.sh`

**Functionality**:
- Parse `provider-config.yaml`
- Generate Markdown docs
- Include type definitions
- Add example code

**Success Criteria**:
- ✅ Docs auto-generated from SSOT
- ✅ CI validates sync

---

## Task 23: Create Ops Dashboard - Provider Health
**Effort**: 3 hours
**Dependencies**: Task 14
**Assignee**: Frontend

**File**: `web/ops-console/src/pages/providers/health.tsx`

**Features**:
- Real-time provider health status
- Latency graphs
- Error rate monitoring

**Success Criteria**:
- ✅ Updates in real-time
- ✅ Alerts on degradation

---

## Task 24: Create Ops Dashboard - Audit Trail
**Effort**: 3 hours
**Dependencies**: Task 7
**Assignee**: Frontend

**File**: `web/ops-console/src/pages/providers/audit.tsx`

**Features**:
- Search ops.run_events
- Filter by provider, tool, user, date
- Export results

**Success Criteria**:
- ✅ Performant queries
- ✅ Export works

---

## Task 25: Add Rate Limiting
**Effort**: 2 hours
**Dependencies**: Task 14
**Assignee**: Backend

**Implementation**:
```typescript
// Check rate limit before executing tool
async function checkRateLimit(user, provider, tool) {
  const limit = getLimit(user.ops_role, provider, tool);
  const count = await countCalls(user.id, provider, tool, '1 hour');
  if (count >= limit) {
    throw new RateLimitError('Limit exceeded');
  }
}
```

**Success Criteria**:
- ✅ Limits enforced per role
- ✅ 429 errors returned correctly

---

## Task 26: Implement Sentry Provider
**Effort**: 4 hours
**Dependencies**: Task 2-6
**Assignee**: Backend

**File**: `mcp/coordinator/src/providers/sentry/index.ts`

**Implementation**: Follow Socket pattern

**Success Criteria**:
- ✅ All Sentry tools implemented
- ✅ Tests pass
- ✅ <2 hour integration time (validates SDK)

---

## Task 27: Implement Netdata Provider
**Effort**: 4 hours
**Dependencies**: Task 2-6
**Assignee**: Backend

**File**: `mcp/coordinator/src/providers/netdata/index.ts`

**Implementation**: Follow Socket pattern

**Success Criteria**:
- ✅ All Netdata tools implemented
- ✅ Tests pass
- ✅ <2 hour integration time (validates SDK)

---

## Task 28: Update DNS SSOT
**Effort**: 30 minutes
**Dependencies**: Task 16
**Assignee**: DevOps

**File**: `infra/dns/subdomain-registry.yaml`

**Actions**:
```yaml
mcp:
  domain: mcp.insightpulseai.com
  type: A
  target: 178.128.112.214
  service: MCP Hub
  ssl: letsencrypt
  nginx_config: /etc/nginx/sites-available/mcp.insightpulseai.com
```

**Run**: `scripts/generate-dns-artifacts.sh`

**Success Criteria**:
- ✅ DNS SSOT updated
- ✅ Generated artifacts synced
- ✅ CI validates consistency

---

## Task Dependency Graph

```
Task 1 (SDK Package)
  └─> Task 2 (ProviderBase)
       ├─> Task 3 (RBAC)
       ├─> Task 4 (Events)
       ├─> Task 5 (Vault)
       └─> Task 6 (Hostnames)
            └─> Task 9 (Socket Provider)
                 ├─> Task 10 (scan.repo)
                 ├─> Task 11 (findings.list)
                 └─> Task 12 (health)
                      ├─> Task 14 (Hub Router)
                      │    ├─> Task 17 (Agent SDK)
                      │    │    └─> Task 18 (Example Agent)
                      │    │         ├─> Task 19 (PR Check)
                      │    │         └─> Task 20 (Release Gate)
                      │    ├─> Task 23 (Health Dashboard)
                      │    └─> Task 24 (Audit Dashboard)
                      ├─> Task 15 (Tests)
                      └─> Task 21 (Docs)
                           └─> Task 22 (Doc Generator)

Task 7 (Database)
  └─> Task 13 (Vault Setup)

Task 8 (Config SSOT)
  └─> Task 22 (Doc Generator)

Task 16 (nginx)
  └─> Task 28 (DNS SSOT)

Task 2-6 (SDK Complete)
  ├─> Task 26 (Sentry)
  └─> Task 27 (Netdata)
```

---

## Execution Order (Suggested)

**Day 1 - Foundation**:
1. Task 1-6 (SDK + Middleware)
2. Task 7 (Database)
3. Task 8 (Config SSOT)

**Day 2 - Socket Provider**:
1. Task 9-12 (Socket tools)
2. Task 13 (Vault setup)
3. Task 14 (Hub router)
4. Task 15 (Tests)

**Day 3 - Agent Integration**:
1. Task 16 (nginx verification)
2. Task 17-18 (Agent SDK + Example)
3. Task 19-20 (CI workflows)

**Day 4 - Documentation & Monitoring**:
1. Task 21-22 (Docs + Generator)
2. Task 23-24 (Dashboards)
3. Task 25 (Rate limiting)
4. Task 28 (DNS SSOT)

**Day 5 - Additional Providers**:
1. Task 26 (Sentry)
2. Task 27 (Netdata)

---

## Critical Path

Tasks on critical path (longest dependency chain):
- Task 1 → 2 → 9 → 14 → 17 → 18 → 19

Estimated critical path duration: **~16 hours** (spread over 2-3 days)

---

## Parallel Work Opportunities

**Can be done in parallel**:
- Task 7 (Database) || Task 1-6 (SDK)
- Task 8 (Config) || Task 1-6 (SDK)
- Task 21 (Docs) || Task 15 (Tests)
- Task 23-24 (Dashboards) || Task 19-20 (CI)
- Task 26-27 (Additional providers) || Task 21-25 (Docs/Monitoring)

---

## Validation Checklist

After all tasks complete:

- [ ] All provider tools callable via hub
- [ ] RBAC enforced (test with different roles)
- [ ] Audit trail complete (query ops.run_events)
- [ ] Secrets in Vault only (grep codebase for tokens)
- [ ] Health checks <5s (test with degraded provider)
- [ ] CI gates active (create test PR)
- [ ] Docs accurate (follow examples)
- [ ] Dashboards functional (check real-time updates)
- [ ] Rate limiting works (exceed quota test)
- [ ] 3 providers operational (Socket, Sentry, Netdata)

---

## Rollback Plan

If issues arise:

1. **Provider fails**: Disable in `provider-config.yaml`, reload hub
2. **Hub crashes**: Restart mcp-coordinator container, check logs
3. **Database issues**: Rollback migration, investigate schema
4. **Auth broken**: Verify Supabase JWT validation, check RLS policies
5. **CI gates blocking**: Temporarily disable workflow, investigate findings

**Rollback Command**:
```bash
# Disable provider
yq eval '.providers.socket.enabled = false' -i infra/mcp/provider-config.yaml
docker restart mcp-coordinator
```

---

## Related Documents

- `spec/mcp-provider-system/constitution.md` - Governance rules
- `spec/mcp-provider-system/prd.md` - Product requirements
- `spec/mcp-provider-system/plan.md` - Implementation plan
