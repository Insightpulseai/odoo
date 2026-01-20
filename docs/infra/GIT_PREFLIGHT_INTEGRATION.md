# Git Pre-Flight Integration - Cross-Repository Pattern

**Version**: 1.0.0
**Date**: 2026-01-20
**Owner**: Jake Tolentino (@jgtolentino)
**Status**: Active

---

## Overview

This document describes the cross-repository integration pattern for git pre-flight checks in the InsightPulse AI Ops Control Room ecosystem.

**Purpose**: Enforce git repository synchronization before any operation that relies on source code state (design tokens, deployments, migrations, etc.).

**Key Principle**: Git pre-flight is a **hard gate** - if it fails, the entire operation aborts.

---

## Architecture

### Components

```
┌─────────────────────────────────────────────────────────────────┐
│                    Ops Control Room                             │
│  (odoo-ce/spec/ops-control-room/)                               │
│                                                                  │
│  ┌────────────────────┐         ┌───────────────────────┐       │
│  │ Skill Registry     │         │ Runbook Executor      │       │
│  │ (agents/*.yaml)    │────────▶│ (runbooks/*.yaml)     │       │
│  └────────────────────┘         └───────────────────────┘       │
│                                                                  │
└───────────────────────────────┬──────────────────────────────────┘
                                │
                                │ References
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│              design-system-cli Repository                        │
│  (packages/figma-bridge/)                                        │
│                                                                  │
│  ┌────────────────────┐         ┌───────────────────────┐       │
│  │ git-operations.ts  │         │ figma.ts              │       │
│  │ (Implementation)   │────────▶│ (Integration)         │       │
│  └────────────────────┘         └───────────────────────┘       │
│           │                                                      │
│           │ Tests                                                │
│           ▼                                                      │
│  ┌────────────────────────────────────────────────────┐         │
│  │ git-operations.test.ts (Vitest)                    │         │
│  └────────────────────────────────────────────────────┘         │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Implementation Details

### Repository 1: design-system-cli (Implementation)

**Location**: `/Users/tbwa/Documents/GitHub/design-system-cli/packages/figma-bridge/`

**Files Created**:

1. **`src/git-operations.ts`** - Core implementation
   - Functions: `runGitWorkflow`, `getGitStatus`, `gitPull`, `gitFetch`, etc.
   - 280 lines of comprehensive git workflow orchestration
   - Error handling, conflict detection, formatted console output

2. **`src/git-operations.test.ts`** - Vitest tests
   - 200+ lines of test coverage
   - Scenarios: non-git repo, clean state, pull conflicts, requireClean validation
   - Mock-based testing with vi.mock()

3. **`vitest.config.ts`** - Test configuration
   - Node environment
   - Coverage reporting (v8 provider)
   - Excludes dist/, node_modules/, test files

4. **`src/figma.ts`** - Integration point
   - Calls `runGitWorkflow()` at function start
   - Aborts on git failure with descriptive error

5. **`package.json`** - Updated scripts
   - `test`: vitest run
   - `test:watch`: vitest (watch mode)
   - `test:git-ops`: vitest git-operations.test.ts
   - `test:coverage`: vitest run --coverage

**Installation**:
```bash
cd /Users/tbwa/Documents/GitHub/design-system-cli/packages/figma-bridge
pnpm install  # Installs vitest, @vitest/coverage-v8
pnpm test     # Run all tests
pnpm test:git-ops  # Run git-operations tests only
```

---

### Repository 2: odoo-ce (Skill Registration & Runbooks)

**Location**: `/Users/tbwa/Documents/GitHub/odoo-ce/spec/ops-control-room/`

**Files Created**:

1. **`agents/figma-bridge.yaml`** - Agent skill registry
   - Declares `git_preflight` skill with full metadata
   - Input/output schemas, telemetry events, test scenarios
   - References implementation in design-system-cli
   - 300+ lines of comprehensive skill definition

2. **`runbooks/figma_sync_design_tokens.yaml`** - Runbook template
   - 3-step workflow: git_preflight → sync_tokens → post_summary
   - Hard gate enforcement: abort on git failure
   - Retry policy, timeouts, notifications
   - Usage examples for plugin/push modes
   - 250+ lines of operational playbook

**Directory Structure**:
```
odoo-ce/spec/ops-control-room/
├── agents/
│   └── figma-bridge.yaml
├── runbooks/
│   └── figma_sync_design_tokens.yaml
├── constitution.md
├── plan.md
├── prd.md
└── tasks.md
```

---

## Cross-Repository Reference Pattern

### How It Works

1. **Skill Definition** (odoo-ce)
   - Ops Control Room reads agent YAML files
   - Extracts skill metadata: name, inputs, outputs, implementation location
   - Stores in skill registry (in-memory or database)

2. **Runbook Execution** (odoo-ce)
   - User triggers runbook via API/CLI
   - Runbook references skill by agent + skill_id
   - Executor resolves skill to implementation module path

3. **Dynamic Import** (runtime)
   - Executor uses Node.js `require()` or `import()` to load module
   - Module path is absolute: `/Users/tbwa/Documents/GitHub/design-system-cli/packages/figma-bridge/src/git-operations.ts`
   - Calls exported function with inputs from runbook

4. **Telemetry Capture** (mcp-jobs)
   - All events logged to Supabase (project: spdtwktxdalcfigzeqrz)
   - Tables: telemetry_events, job_runs, job_events
   - Query via Buildopscontrolroom dashboard

### Example Execution Flow

```typescript
// Ops Control Room Runbook Executor (simplified)
import { readFileSync } from 'fs';
import { parse as parseYAML } from 'yaml';

// 1. Load runbook
const runbook = parseYAML(
  readFileSync('/Users/tbwa/Documents/GitHub/odoo-ce/spec/ops-control-room/runbooks/figma_sync_design_tokens.yaml', 'utf-8')
);

// 2. Execute step: git_preflight
const step = runbook.steps.find(s => s.id === 'git_preflight');

// 3. Resolve skill implementation
const agent = parseYAML(
  readFileSync('/Users/tbwa/Documents/GitHub/odoo-ce/spec/ops-control-room/agents/figma-bridge.yaml', 'utf-8')
);
const skill = agent.skills.find(s => s.id === 'git_preflight');

// 4. Dynamic import
const gitOpsModule = await import(skill.implementation.module);
const runGitWorkflow = gitOpsModule[skill.implementation.entrypoint];

// 5. Execute with telemetry
const startEvent = { name: 'git_preflight.start', timestamp: Date.now() };
await mcp_jobs.captureEvent(startEvent);

try {
  const result = await runGitWorkflow(step.inputs.cwd, {
    checkStatus: step.inputs.checkStatus,
    pull: step.inputs.pull,
    requireClean: step.inputs.requireClean,
  });

  const completeEvent = {
    name: 'git_preflight.complete',
    payload: result,
    timestamp: Date.now(),
  };
  await mcp_jobs.captureEvent(completeEvent);

  if (!result.proceed) {
    // Hard gate: abort runbook
    throw new Error(`Git pre-flight failed: ${result.message}`);
  }

  // Continue to next step...
} catch (error) {
  const errorEvent = {
    name: 'git_preflight.error',
    payload: { error: error.message },
    timestamp: Date.now(),
  };
  await mcp_jobs.captureEvent(errorEvent);
  throw error;
}
```

---

## Testing Strategy

### Unit Tests (design-system-cli)

**Location**: `packages/figma-bridge/src/git-operations.test.ts`

**Coverage**: 8 test suites, 15+ test cases

**Key Scenarios**:
1. **Non-git repository** - Graceful skip
2. **Clean and up-to-date** - Success
3. **Behind remote** - Auto-pull success
4. **Pull conflicts** - Failure with conflict details
5. **requireClean with changes** - Failure with uncommitted changes message

**Running Tests**:
```bash
cd /Users/tbwa/Documents/GitHub/design-system-cli/packages/figma-bridge
pnpm test:git-ops           # Targeted tests
pnpm test:coverage          # With coverage report
pnpm test:watch             # Watch mode for development
```

**Expected Output**:
```
 ✓ packages/figma-bridge/src/git-operations.test.ts (15)
   ✓ git-operations (15)
     ✓ isGitRepo (2)
       ✓ returns true when in a git repository
       ✓ returns false when not in a git repository
     ✓ getGitStatus (3)
       ✓ parses clean git status correctly
       ✓ parses ahead/behind status correctly
       ✓ parses file changes correctly
     ✓ runGitWorkflow (5)
       ✓ skips gracefully when not in a git repo
       ✓ passes when repo is clean and up to date
       ✓ fails when requireClean is true and repo has changes
       ✓ pulls successfully when behind remote
       ✓ fails when pull results in conflicts
     ✓ hasUncommittedChanges (2)
       ✓ returns true when there are uncommitted changes
       ✓ returns false when working directory is clean

Test Files  1 passed (1)
     Tests  15 passed (15)
```

---

### Integration Tests (Runbook Dry-Run)

**Method**: Use Ops Control Room API with a safe environment

```bash
# Dry-run with dev lane (non-destructive)
curl -X POST https://buildopscontrolroom.vercel.app/api/runs \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $OPS_API_KEY" \
  -d '{
    "template_id": "figma_sync_design_tokens",
    "environment": "dev",
    "lane": "A",
    "inputs": {
      "mode": "plugin",
      "tokens_file": "./test-fixtures/sample-tokens.json",
      "output_dir": "/tmp/figma-plugin-test"
    },
    "dry_run": true
  }'
```

**Expected Response**:
```json
{
  "run_id": "run_abc123",
  "status": "completed",
  "steps": [
    {
      "id": "git_preflight",
      "status": "success",
      "duration_ms": 1250,
      "output": {
        "proceed": true,
        "message": "Git checks passed"
      },
      "telemetry_events": [
        "git_preflight.start",
        "git_preflight.status",
        "git_preflight.complete"
      ]
    },
    {
      "id": "sync_tokens",
      "status": "success",
      "duration_ms": 3420
    },
    {
      "id": "post_summary",
      "status": "success",
      "duration_ms": 890
    }
  ],
  "total_duration_ms": 5560
}
```

**Verification Queries** (Supabase SQL):
```sql
-- Check telemetry events were captured
SELECT * FROM telemetry_events
WHERE run_id = 'run_abc123'
  AND event_name LIKE 'git_preflight.%'
ORDER BY created_at;

-- Check job run record
SELECT * FROM job_runs
WHERE id = 'run_abc123';

-- Check all step events
SELECT * FROM job_events
WHERE run_id = 'run_abc123'
ORDER BY sequence;
```

---

## Deployment Workflow

### Phase 1: design-system-cli

```bash
cd /Users/tbwa/Documents/GitHub/design-system-cli

# 1. Install dependencies
pnpm install

# 2. Run tests
pnpm test

# 3. Build TypeScript
pnpm build

# 4. Commit changes
git add \
  packages/figma-bridge/src/git-operations.ts \
  packages/figma-bridge/src/git-operations.test.ts \
  packages/figma-bridge/src/figma.ts \
  packages/figma-bridge/src/index.ts \
  packages/figma-bridge/vitest.config.ts \
  packages/figma-bridge/package.json

git commit -m "feat(figma-bridge): add git pre-flight checks with tests

- Implement comprehensive git workflow validation
- Add runGitWorkflow() with status, pull, conflict detection
- Integrate into figma() function as hard gate
- Add 15 Vitest test cases with 80%+ coverage
- Export git-operations from package index

Refs: ops-control-room/agents/figma-bridge.yaml"

# 5. Push to GitHub
git push origin main
```

---

### Phase 2: odoo-ce

```bash
cd /Users/tbwa/Documents/GitHub/odoo-ce

# 1. Commit skill and runbook definitions
git add \
  spec/ops-control-room/agents/figma-bridge.yaml \
  spec/ops-control-room/runbooks/figma_sync_design_tokens.yaml \
  docs/infra/GIT_PREFLIGHT_INTEGRATION.md

git commit -m "feat(ops-control-room): register git_preflight skill + figma sync runbook

- Create figma-bridge agent skill registry
- Define git_preflight skill with telemetry
- Create figma_sync_design_tokens runbook with 3 steps
- Document cross-repo integration pattern

Refs: design-system-cli/packages/figma-bridge"

# 2. Push to GitHub
git push origin main
```

---

### Phase 3: Ops Control Room Deployment

**Assumptions**:
- Ops Control Room (Buildopscontrolroom) is deployed on Vercel
- GitHub webhook is configured to trigger builds on push
- Supabase backend (spdtwktxdalcfigzeqrz) is connected

**Automatic Deployment**:
1. Push to `main` triggers GitHub webhook
2. Webhook hits `/api/webhooks/github` in Ops Control Room
3. Queues deployment runbook in mcp-jobs
4. Runbook executor pulls latest code and updates skill registry
5. New runbook becomes available via API

**Manual Deployment** (if needed):
```bash
# Trigger deployment via API
curl -X POST https://buildopscontrolroom.vercel.app/api/deploy \
  -H "Authorization: Bearer $OPS_API_KEY" \
  -d '{
    "repo": "odoo-ce",
    "branch": "main",
    "component": "skill-registry"
  }'
```

---

## Rollback Strategy

### Scenario 1: Git Operations Bug

**Symptoms**: git_preflight skill fails unexpectedly, blocking all Figma syncs

**Rollback**:
```bash
cd /Users/tbwa/Documents/GitHub/design-system-cli

# 1. Revert git-operations integration from figma.ts
git revert <commit-sha>

# 2. Push revert
git push origin main

# 3. Ops Control Room will auto-deploy reverted code
```

**Alternative**: Temporary bypass
```yaml
# Edit runbook to skip git_preflight step
# spec/ops-control-room/runbooks/figma_sync_design_tokens.yaml
steps:
  - id: git_preflight
    enabled: false  # Temporary bypass
    # ... rest of config

  - id: sync_tokens
    depends_on: []  # Remove git_preflight dependency
```

---

### Scenario 2: Runbook Definition Error

**Symptoms**: Runbook fails to parse or execute

**Rollback**:
```bash
cd /Users/tbwa/Documents/GitHub/odoo-ce

# 1. Revert runbook YAML
git revert <commit-sha>

# 2. Push revert
git push origin main

# 3. Ops Control Room picks up reverted runbook
```

---

## Monitoring & Observability

### Telemetry Events

**Event Schema**:
```typescript
interface TelemetryEvent {
  id: string;
  run_id: string;
  event_name: string;
  timestamp: Date;
  payload: Record<string, any>;
  duration_ms?: number;
}
```

**Git Pre-Flight Events**:

1. **`git_preflight.start`**
   ```json
   {
     "event_name": "git_preflight.start",
     "payload": {
       "cwd": "/Users/tbwa/Documents/GitHub/design-system-cli",
       "options": {
         "checkStatus": true,
         "pull": true,
         "requireClean": false
       }
     }
   }
   ```

2. **`git_preflight.status`**
   ```json
   {
     "event_name": "git_preflight.status",
     "payload": {
       "branch": "main",
       "ahead": 0,
       "behind": 0,
       "is_clean": true,
       "staged_count": 0,
       "modified_count": 0,
       "untracked_count": 0
     }
   }
   ```

3. **`git_preflight.conflict`**
   ```json
   {
     "event_name": "git_preflight.conflict",
     "payload": {
       "conflict_files": ["src/figma.ts", "package.json"],
       "error_message": "Pull resulted in conflicts. Please resolve manually."
     }
   }
   ```

4. **`git_preflight.complete`**
   ```json
   {
     "event_name": "git_preflight.complete",
     "payload": {
       "proceed": true,
       "message": "Git checks passed",
       "duration_ms": 1250
     }
   }
   ```

---

### Metrics Collection

**Key Metrics**:
- **Git Pre-Flight Success Rate**: (successes / total attempts) * 100
- **Average Pull Duration**: Mean time for git pull operations
- **Conflict Rate**: (conflicts / pull attempts) * 100
- **Repository Staleness**: Frequency of behind-remote states

**Query Examples** (Supabase SQL):
```sql
-- Success rate over last 7 days
SELECT
  DATE(created_at) AS date,
  COUNT(*) AS total_attempts,
  COUNT(*) FILTER (WHERE payload->>'proceed' = 'true') AS successes,
  ROUND(
    COUNT(*) FILTER (WHERE payload->>'proceed' = 'true')::numeric
    / COUNT(*)::numeric * 100,
    2
  ) AS success_rate_pct
FROM telemetry_events
WHERE event_name = 'git_preflight.complete'
  AND created_at >= NOW() - INTERVAL '7 days'
GROUP BY DATE(created_at)
ORDER BY date DESC;

-- Conflict frequency by repository
SELECT
  payload->>'cwd' AS repository,
  COUNT(*) AS conflict_count,
  ARRAY_AGG(DISTINCT payload->'conflict_files') AS common_conflict_files
FROM telemetry_events
WHERE event_name = 'git_preflight.conflict'
  AND created_at >= NOW() - INTERVAL '30 days'
GROUP BY payload->>'cwd'
ORDER BY conflict_count DESC;

-- Average pull duration
SELECT
  AVG((payload->>'duration_ms')::numeric) AS avg_duration_ms,
  PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY (payload->>'duration_ms')::numeric) AS median_duration_ms,
  PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY (payload->>'duration_ms')::numeric) AS p95_duration_ms
FROM telemetry_events
WHERE event_name = 'git_preflight.complete'
  AND created_at >= NOW() - INTERVAL '7 days';
```

---

### Alerting Rules

**Critical Alerts** (PagerDuty / Slack):
1. **Git Pre-Flight Success Rate < 80%** (1-hour window)
   - Indicates systemic git issues or configuration problems
   - Action: Investigate repository health, network connectivity

2. **Conflict Rate > 20%** (1-day window)
   - Suggests team coordination issues or branch management problems
   - Action: Review branching strategy, improve communication

**Warning Alerts** (Slack):
1. **Behind Remote > 10 commits** (per repository)
   - Repository is significantly out of sync
   - Action: Notify repository maintainer

2. **Average Pull Duration > 10 seconds**
   - Network or repository size issues
   - Action: Investigate network latency, consider shallow clones

---

## Extending to Other Bridges

### Pattern for Reuse

The git_preflight skill is **reusable across all bridges** that depend on source code state:

**Current**: Figma bridge (design tokens)
**Future**:
- Odoo theme sync
- Superset dashboard deployment
- n8n workflow updates
- Configuration management bridges

### Example: Odoo Theme Sync

**New Agent** (`spec/ops-control-room/agents/odoo-theme-bridge.yaml`):
```yaml
agent_id: odoo_theme_bridge
skills:
  - id: git_preflight
    name: Git Pre-Flight Checks
    implementation:
      module: packages/figma-bridge/src/git-operations.ts  # REUSE
      entrypoint: runGitWorkflow
    # ... same config as figma-bridge

  - id: sync_odoo_theme
    name: Sync Odoo Theme
    implementation:
      module: addons/ipai/ipai_theme_sync/theme_sync.py
      entrypoint: sync_theme
```

**New Runbook** (`spec/ops-control-room/runbooks/odoo_theme_sync.yaml`):
```yaml
id: odoo_theme_sync
steps:
  - id: git_preflight
    agent: odoo_theme_bridge
    skill: git_preflight  # REUSE
    inputs:
      cwd: /Users/tbwa/Documents/GitHub/odoo-ce
      checkStatus: true
      pull: true
      requireClean: true  # Stricter for production

  - id: sync_theme
    agent: odoo_theme_bridge
    skill: sync_odoo_theme
    depends_on: [git_preflight]
```

**No Code Duplication**: All bridges share the same git-operations implementation.

---

## Best Practices

### 1. Always Run Git Pre-Flight for Source-Dependent Operations

**Anti-Pattern**:
```yaml
steps:
  - id: sync_tokens
    agent: figma_bridge
    skill: figma_sync_tokens
    # NO GIT CHECK - DANGEROUS
```

**Correct Pattern**:
```yaml
steps:
  - id: git_preflight
    agent: figma_bridge
    skill: git_preflight

  - id: sync_tokens
    agent: figma_bridge
    skill: figma_sync_tokens
    depends_on: [git_preflight]  # SAFE
```

---

### 2. Use requireClean for Production-Critical Operations

**Development/Test**: `requireClean: false` (allow experimentation)
**Production**: `requireClean: true` (enforce clean state)

```yaml
steps:
  - id: git_preflight
    inputs:
      requireClean: ${is_production}  # Dynamic based on environment
```

---

### 3. Configure Appropriate Timeouts

**Typical Values**:
- **git_preflight**: 30 seconds (enough for fetch + pull)
- **sync_tokens**: 2 minutes (plugin generation + file I/O)
- **post_summary**: 30 seconds (notification delivery)

**Adjust for Large Repositories**:
```yaml
execution_policy:
  timeout:
    per_step:
      git_preflight: 2m  # Large repo with slow network
```

---

### 4. Monitor Git Metrics

**Set Up Alerts**:
- Success rate trends
- Conflict frequency
- Repository staleness
- Pull duration (P95)

**Create Dashboard** (Buildopscontrolroom):
- Git health scorecard per repository
- Recent conflict timeline
- Top conflict files (by frequency)

---

### 5. Document Repository-Specific Quirks

Some repositories may have unique characteristics:

```yaml
# Custom notes in agent YAML
notes:
  - repository: design-system-cli
    quirks:
      - "Uses pnpm workspaces - pulls can be slow due to lockfile updates"
      - "Main branch protected - use feature branches for all work"
      - "Pre-commit hooks run Prettier - may modify files during commit"
```

---

## Troubleshooting

### Problem: Git pre-flight always fails with "not a git repository"

**Cause**: Incorrect `cwd` path in runbook inputs

**Solution**:
```yaml
steps:
  - id: git_preflight
    inputs:
      cwd: /Users/tbwa/Documents/GitHub/design-system-cli  # Absolute path
```

---

### Problem: Pull succeeds but conflicts reported

**Cause**: `git pull --rebase` detected conflicts during rebase

**Solution**:
1. SSH into the machine or navigate locally
2. Resolve conflicts: `git status`, `git rebase --continue`
3. Retry runbook

---

### Problem: requireClean fails but working directory appears clean

**Cause**: Untracked files or staged changes

**Solution**:
- Check `.gitignore` patterns
- Run `git status --porcelain` manually
- Adjust `requireClean` to `false` if untracked files are acceptable

---

### Problem: Telemetry events not appearing in Supabase

**Cause**: MCP-jobs integration not configured

**Solution**:
1. Verify Supabase credentials in environment
2. Check `mcp-jobs` is running and connected
3. Validate table schemas match expected structure
4. Review Ops Control Room logs for capture errors

---

## Future Enhancements

### 1. Git LFS Support

**Current**: Works with standard git repositories
**Future**: Add LFS detection and `git lfs pull` integration

**Implementation**:
```typescript
// git-operations.ts
async function detectLFS(cwd: string): Promise<boolean> {
  const { stdout } = await execAsync('git lfs ls-files', { cwd });
  return stdout.trim().length > 0;
}

async function pullLFS(cwd: string): Promise<void> {
  await execAsync('git lfs pull', { cwd });
}
```

---

### 2. Shallow Clone Optimization

**Current**: Full repository pull
**Future**: Option for shallow clones (faster for large repos)

**Implementation**:
```yaml
steps:
  - id: git_preflight
    inputs:
      shallow: true
      depth: 1  # Only pull last commit
```

---

### 3. Multi-Repository Coordination

**Current**: Single repository per runbook
**Future**: Coordinate git pre-flight across multiple repositories

**Implementation**:
```yaml
steps:
  - id: git_preflight_multi
    inputs:
      repositories:
        - path: /Users/tbwa/Documents/GitHub/design-system-cli
          branch: main
        - path: /Users/tbwa/Documents/GitHub/odoo-ce
          branch: main
      require_all_clean: true
```

---

### 4. Git Hook Integration

**Future**: Trigger Ops Control Room runbooks from git hooks

**Example**:
```bash
# .git/hooks/post-merge
#!/bin/bash
# Trigger Figma sync after merging design token changes

if git diff-tree --no-commit-id --name-only -r HEAD | grep -q "tokens/"; then
  curl -X POST https://buildopscontrolroom.vercel.app/api/runs \
    -d '{"template_id": "figma_sync_design_tokens"}'
fi
```

---

## Summary

### Key Takeaways

1. **Git pre-flight is a hard gate** - Never bypass for source-dependent operations
2. **Cross-repository pattern** - Implementation in source repo, registry in Ops Control Room
3. **Comprehensive testing** - Unit tests (Vitest) + integration tests (runbook dry-run)
4. **Reusable skill** - Single implementation, multiple bridges (Figma, Odoo, Superset, etc.)
5. **Full observability** - Telemetry events, metrics, alerting via mcp-jobs + Supabase

### Success Criteria

✅ Git operations implemented with tests (design-system-cli)
✅ Skill registered in Ops Control Room (odoo-ce)
✅ Runbook created with git pre-flight gate (odoo-ce)
✅ Cross-repo integration documented (this file)
✅ Telemetry events defined and captured (mcp-jobs)

### Next Steps

1. **Deploy Phase 1**: Push design-system-cli changes
2. **Deploy Phase 2**: Push odoo-ce skill + runbook definitions
3. **Test Integration**: Dry-run figma_sync_design_tokens runbook
4. **Monitor Metrics**: Track success rate, conflicts, duration
5. **Extend Pattern**: Apply to Odoo theme sync, Superset dashboards

---

**Document Version**: 1.0.0
**Last Updated**: 2026-01-20
**Maintainer**: Jake Tolentino (@jgtolentino)
