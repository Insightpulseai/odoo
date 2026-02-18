# MCP Registry - InsightPulse AI Selection

**Last Updated**: 2026-02-17
**Status**: CANONICAL
**Related**: `spec/mcp-provider-system/`

---

## Current State

### Deployed Infrastructure
- ✅ **MCP Hub**: `mcp.insightpulseai.com` (live, healthy)
- ✅ **Supabase**: Control plane for ops, auth, Vault
- ✅ **GitHub**: Repo operations, workflows, issues
- ✅ **Terraform**: Cloudflare DNS management (IaC)
- ✅ **Playwright**: Browser testing (`web/alpha-browser/`, `web/web-legacy-backup/`)
- ❌ **Sentry**: Not deployed (but should be for web surfaces)
- ❌ **Netdata**: Not deployed (manual SSH troubleshooting only)

### Current Pain Points
1. No unified observability (debugging "why is n8n serving Plane?" required manual SSH)
2. Supply-chain risk blind (no dependency scanning in CI)
3. Sentry would help web/ops-console reliability but not set up yet
4. Netdata would eliminate SSH-first debugging

---

## Recommended MCP Selection

Based on InsightPulse AI's **Supabase-first + Odoo CE + Cloudflare/Vercel/n8n/MCP hub** reality:

### Tier 1: Platform Ops (Immediate Value)

#### 1. **Supabase MCP** (supabase-community)
**Status**: ✅ PRIORITY 1
**Why**: Supabase is your control plane. This becomes your "ops console automation API."

**Use Cases**:
- Inspect projects, migrations, Edge Functions, Storage
- Validate runtime identifiers and environment drift
- Automate ops-runner patterns / RBAC checks
- Query ops.run_events from agents

**Integration**: Provider #1 in `spec/mcp-provider-system/`

**Security**: Service-role only in CI, anon/client tokens for reads

---

#### 2. **GitHub MCP** (github)
**Status**: ✅ PRIORITY 1
**Why**: PR hygiene, workflow status, issues/projects automation without `gh` auth everywhere.

**Use Cases**:
- PR creation/comments, label automation, workflow reruns
- Fetch repo metadata for health checks
- Update check-runs / artifacts links
- Issue triage automation

**Integration**: Provider #2 in spec

**Security**: Least-privilege PAT or GitHub App token

---

#### 3. **Socket MCP** (SocketDev/socket-mcp)
**Status**: ✅ PRIORITY 2 (already specified)
**Why**: Supply-chain risk detection before runtime. Complements Sentry (runtime) and Netdata (infra).

**Use Cases**:
- PR dependency gate (block critical findings)
- Release candidate scan (high+ severity blocks)
- Dependency audit in CI
- Agent-assisted vulnerability triage

**Integration**: Provider #3 in spec (see `spec/mcp-provider-system/plan.md`)

**Security**: Read-only API access, hostname allowlist

---

#### 4. **Netdata MCP** (netdata) - OR - **Sentry MCP** (getsentry)
**Status**: ⚠️ CHOOSE ONE FOR TIER 1

**Option A: Netdata** (infrastructure focus)
- Confirm droplet health, CPU/mem spikes, network issues
- Anomaly detection around deploy windows
- Replaces SSH-first debugging ("why is n8n/mcp serving Plane?")
- **Decision**: Best if infra issues > web errors

**Option B: Sentry** (web reliability focus)
- Fetch latest regressions, group by release
- Generate fix PR hints from error traces
- Triage web/ops-console issues
- **Decision**: Best if web errors > infra issues

**Recommendation**: Start with **Netdata** (fixes immediate pain), add Sentry later for web surfaces.

**Integration**: Provider #4 in spec

---

### Tier 2: Engineering/CI (High Leverage)

#### 5. **Playwright MCP** (microsoft)
**Status**: ✅ ALREADY USED (web/alpha-browser/, web/web-legacy-backup/)
**Why**: Automation-first verification, aligns with healthcheck strategy.

**Use Cases**:
- Smoke test key surfaces (login pages, status pages)
- Screenshot evidence bundles in CI (for SSOT docs)
- Real browser checks in staging gates

**Integration**: Standalone (already working) or wrap as provider

**Security**: Constrained to critical-only checks

---

#### 6. **Serena MCP** (oraios)
**Status**: 🤔 EVALUATE
**Why**: Repo-scale semantic code retrieval/editing in monorepo.

**Use Cases**:
- Faster "find the real place to change" across huge trees
- Safer refactors with fewer hallucinated paths
- Agent-assisted code navigation

**Decision**: Evaluate if agents frequently struggle with monorepo navigation. If not, defer.

**Integration**: If adopted, wrap as provider

---

#### 7. **SonarQube MCP** (SonarSource) - OR - **Snyk MCP**
**Status**: ❌ NOT DEPLOYED (neither SonarQube nor Snyk)
**Why**: Code quality/security signals for agents.

**Use Cases**:
- Explain failing quality gates
- Propose minimal diffs for scanner issues
- Automate technical debt triage

**Decision**: **Defer until SonarQube or Snyk deployed**. Socket MCP covers supply-chain risk for now.

**Integration**: If adopted, wrap as provider

---

### Tier 3: Data & Docs Ingestion

#### 8. **Markitdown MCP** (microsoft)
**Status**: ✅ PRIORITY 3
**Why**: Convert PDFs/Docs/Excel templates → Markdown for docs/ + RAG.

**Use Cases**:
- Turn vendor docs, specs, xlsx templates into repo artifacts
- Knowledge ingestion for context
- Evidence documentation automation

**Integration**: Standalone tool or provider (low risk, high utility)

**Security**: None major, just version pinning

---

#### 9. **DBHub MCP** (bytebase)
**Status**: 🤔 EVALUATE
**Why**: Universal DB MCP for Postgres (DO managed + Supabase) + MySQL.

**Use Cases**:
- Schema discovery, quick SQL read checks
- Compatibility checks across DB instances
- Agent-assisted schema queries

**Decision**: Evaluate if agents need direct DB schema access. If not, Supabase MCP sufficient.

**Integration**: If adopted, wrap as provider

**Security**: Read-only credentials only

---

### Tier 4: Design-to-code

#### 10. **Figma MCP** (figma)
**Status**: 🤔 DEPENDS ON DESIGN WORKFLOW
**Why**: You stated "Figma-native + token parity" SDLC.

**Use Cases**:
- Pull frames/components/tokens into design/ SSOT
- Diff token changes and open PRs
- Automated design-code sync

**Decision**: **Only if Figma is truly SSOT for design tokens**. Otherwise defer.

**Integration**: If adopted, dedicated "design sync" lane (not general provider)

**Security**: Token exposure + scope creep risk

---

## Recommended Starter Pack

**Minimum set for immediate ops + coding + evidence improvements**:

1. ✅ **Supabase MCP** (control plane)
2. ✅ **GitHub MCP** (repo automation)
3. ✅ **Socket MCP** (supply-chain risk)
4. ✅ **Netdata MCP** (infra visibility)
5. ✅ **Playwright MCP** (UI proof) - already have, just formalize
6. ✅ **Markitdown** (docs ingestion)

**Total**: 6 MCPs (5 new + 1 formalized)

**Timeline**: 2-3 weeks (Socket first, then parallel on others)

---

## NOT Recommended

| MCP | Reason |
|-----|--------|
| Zapier/Apify/Webflow/Wix | Pulls away from Supabase-first, repo-governed approach |
| Desktop Commander | Duplicates controlled CLI/CI runners, higher blast radius |
| Notion MCP | Not operational SSOT (repo/Supabase is) |
| Vercel MCP | GitHub Actions + Vercel integration covers most needs |
| Terraform MCP | Nice-to-have, but doctl + Terraform CLI sufficient for now |
| Miro MCP | Only if Miro becomes design SSOT (unlikely) |

---

## Implementation Priority

### Phase 1 (Week 1-2): Foundation + Socket
1. **Implement Provider SDK** (`packages/mcp-provider-sdk/`)
2. **Socket Provider** (scan.repo, findings.list, health)
3. **Hub Router** (JWT validation, RBAC enforcement)
4. **CI Gates** (PR dependency check, release candidate scan)

**Deliverable**: Socket MCP live, dependency scanning in CI

---

### Phase 2 (Week 3): Core Ops Providers
1. **Supabase Provider** (project info, migrations, Edge Functions)
2. **GitHub Provider** (PR/issue ops, workflow automation)
3. **Netdata Provider** (infra metrics, anomaly detection)

**Deliverable**: Core ops automation via MCP hub

---

### Phase 3 (Week 4): Engineering & Docs
1. **Playwright Provider** (wrap existing tests, add CI smoke tests)
2. **Markitdown** (standalone tool, not provider - simpler)
3. **Ops Dashboard** (health + audit trail)

**Deliverable**: Full observability + evidence automation

---

### Phase 4 (Later): Evaluate & Expand
1. **Sentry Provider** (if web errors become priority)
2. **Serena** (if monorepo navigation pain increases)
3. **DBHub** (if direct DB schema access needed)
4. **Figma** (if design-code sync becomes bottleneck)

**Deliverable**: Ecosystem expands based on real needs

---

## Governance Model

All MCPs follow `spec/mcp-provider-system/constitution.md`:

1. ✅ Single gateway (`mcp.insightpulseai.com`)
2. ✅ Supabase RBAC (ops_viewer/operator/admin)
3. ✅ Event sourcing (ops.run_events)
4. ✅ Vault secrets only
5. ✅ Hostname allowlist
6. ✅ Health checks mandatory
7. ✅ Provider independence
8. ✅ Rate limiting by role
9. ✅ Schema versioning
10. ✅ Provider SDK standardization

**No exceptions** for rules 1-4 (gateway, RBAC, events, vault).

---

## Installation Template

```bash
# Add to agents/mcp/ (SSOT manifest)
cat > agents/mcp/provider-manifest.yaml << 'EOF'
version: '1.0'
registry: 'insightpulseai-curated'

providers:
  supabase:
    package: '@supabase/mcp'
    enabled: true
    vault_key: supabase_service_role_key
    allowed_hosts:
      - '*.supabase.co'
      - 'supabase.com'
    min_role: ops_viewer

  github:
    package: '@modelcontextprotocol/server-github'
    enabled: true
    vault_key: github_token
    allowed_hosts:
      - 'api.github.com'
      - 'github.com'
    min_role: ops_operator

  socket:
    package: '@socketsecurity/socket-mcp'
    enabled: true
    vault_key: socket_api_key
    allowed_hosts:
      - 'api.socket.dev'
      - 'socket.dev'
    min_role: ops_operator

  netdata:
    package: '@netdata/mcp'
    enabled: true
    vault_key: netdata_token
    allowed_hosts:
      - 'app.netdata.cloud'
      - '*.netdata.cloud'
    min_role: ops_viewer

  playwright:
    package: '@modelcontextprotocol/server-playwright'
    enabled: true
    vault_key: null  # no external API
    allowed_hosts: []
    min_role: ops_operator

  markitdown:
    package: '@microsoft/markitdown-mcp'
    enabled: true
    vault_key: null  # no external API
    allowed_hosts: []
    min_role: ops_viewer
EOF

# Generate runtime config
pnpm tsx scripts/generate-mcp-config.ts

# Update healthcheck
pnpm tsx scripts/health/all_services_healthcheck.py --include-mcp
```

---

## Success Criteria

✅ **Phase 1**:
- Socket MCP live via hub
- PR dependency gate active
- 100% ops actions audited
- Zero secrets in code/env

✅ **Phase 2**:
- 4 providers operational (Supabase, GitHub, Socket, Netdata)
- Agents using providers (5+ agent integrations)
- Hub health dashboard live

✅ **Phase 3**:
- 6 MCPs integrated
- Playwright formalized
- Evidence automation working
- Ops team trained

✅ **Phase 4**:
- Ecosystem scaled based on real needs
- <2 hour integration time for new providers
- Provider marketplace evaluation complete

---

## Current vs. Target State

### Current (2026-02-17)
```
Claude / Agents
    ↓
Direct API calls (no governance)
    ↓
Socket, GitHub, Supabase APIs
```

**Issues**: No RBAC, no audit, secrets scattered, no health checks

---

### Target (2026-03-15)
```
Claude / Agents
    ↓
Agent SDK (@ipai/agent-sdk)
    ↓
mcp.insightpulseai.com (Hub)
    ├─ Supabase Provider (RBAC, events, vault)
    ├─ GitHub Provider
    ├─ Socket Provider
    ├─ Netdata Provider
    ├─ Playwright Provider
    └─ Markitdown (standalone)
        ↓
    ops.run_events (audit trail)
    vault.secrets (keys)
    auth.users (RBAC)
```

**Benefits**: Unified RBAC, complete audit, secret rotation, health monitoring, provider independence

---

## Related Documents

- `spec/mcp-provider-system/constitution.md` - Governance rules
- `spec/mcp-provider-system/prd.md` - Product requirements
- `spec/mcp-provider-system/plan.md` - Implementation plan
- `spec/mcp-provider-system/tasks.md` - Task breakdown
- `infra/mcp/provider-config.yaml` - SSOT config (to be created)
- `scripts/generate-mcp-config.ts` - Config generator (to be created)

---

**Next Action**: Implement Provider SDK + Socket Provider (Phase 1, Week 1-2)
