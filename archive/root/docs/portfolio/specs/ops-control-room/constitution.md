# Ops Control Room — Constitution (Non-Negotiable Rules)

**Spec Bundle**: `spec/ops-control-room/`
**Status**: Canonical
**Last Updated**: 2026-01-08

---

## 0) Immutable Constraints

These rules CANNOT be violated. Any PR breaking these is auto-rejected.

---

## 1) Schema Isolation

**Rule**: All ops tables MUST live in `ops` schema, NOT `public`.

**Rationale**: Prevents pollution of public schema, enables clean PostgREST exposure control.

**Enforcement**:
```sql
-- REQUIRED
CREATE SCHEMA IF NOT EXISTS ops;
CREATE TABLE ops.sessions (...);
CREATE TABLE ops.runs (...);

-- FORBIDDEN
CREATE TABLE public.ops_sessions (...);  -- ❌
CREATE TABLE runs (...);                  -- ❌ (defaults to public)
```

**Acceptance**: All ops tables in `ops` schema, PostgREST exposes `ops` OR public views over `ops.*`.

---

## 2) Atomic Claiming (No Double Execution)

**Rule**: Run claiming MUST use `FOR UPDATE SKIP LOCKED`.

**Rationale**: Prevents race conditions when 2+ workers claim same run.

**Enforcement**:
```sql
-- REQUIRED
SELECT * FROM ops.runs
WHERE status = 'queued'
  AND (lane = ANY($1) OR $1 IS NULL)
ORDER BY priority DESC, created_at ASC
LIMIT $2
FOR UPDATE SKIP LOCKED;

-- FORBIDDEN
SELECT * FROM ops.runs WHERE status = 'queued';  -- ❌ No locking
UPDATE ops.runs SET claimed_by = $1 WHERE id = $2;  -- ❌ Race condition
```

**Acceptance**: Concurrent workers never execute same run twice (verified by integration test).

---

## 3) Heartbeat + Stuck Recovery

**Rule**: Workers MUST send heartbeat every 5s. Runs stuck >30s MUST be recovered.

**Rationale**: Detects worker crashes, prevents zombie runs.

**Enforcement**:
```typescript
// REQUIRED
setInterval(() => heartbeat(runId, workerId), 5000);

// Sweeper job
UPDATE ops.runs
SET status = 'failed', error = jsonb_build_object('reason', 'heartbeat_timeout')
WHERE status IN ('claimed', 'running')
  AND NOW() - heartbeat_at > INTERVAL '30 seconds';
```

**Acceptance**: Killing worker mid-run triggers recovery within 35s (30s timeout + 5s sweeper).

---

## 4) Lane Isolation

**Rule**: Each session MUST support exactly 4 lanes: A, B, C, D.

**Rationale**: Standard parallel execution model (like Codex Web lanes).

**Enforcement**:
```sql
-- REQUIRED
CREATE TYPE ops.lane_type AS ENUM ('A', 'B', 'C', 'D');
ALTER TABLE ops.runs ADD COLUMN lane ops.lane_type NOT NULL;

-- FORBIDDEN
lane TEXT CHECK (lane IN ('A', 'B', 'C', 'D'));  -- ❌ Use ENUM
lane VARCHAR(1);                                  -- ❌ No validation
```

**Acceptance**: UI shows 4 lane columns, runs distribute independently per lane.

---

## 5) Realtime Telemetry

**Rule**: Run status changes MUST propagate to UI within 2 seconds.

**Rationale**: Operator needs live visibility, not stale polling.

**Enforcement**:
```typescript
// REQUIRED - Supabase Realtime subscription
supabase
  .channel('runs')
  .on('postgres_changes', { event: '*', schema: 'ops', table: 'runs' }, handleChange)
  .subscribe();

// FORBIDDEN
setInterval(() => fetchRuns(), 5000);  // ❌ Polling only
```

**Acceptance**: Change run status in DB → UI reflects within 2s (measured by E2E test).

---

## 6) Cancellation Propagation

**Rule**: Cancel MUST set `status='cancelled'` AND worker MUST check cancellation between steps.

**Rationale**: Graceful shutdown, avoid wasted execution.

**Enforcement**:
```typescript
// REQUIRED - Worker checks cancellation
for (const step of steps) {
  const run = await getRun(runId);
  if (run.status === 'cancelled') {
    await logEvent(runId, 'info', 'Run cancelled by user');
    return;
  }
  await executeStep(step);
}

// FORBIDDEN
// No cancellation check → runs to completion even after cancel  ❌
```

**Acceptance**: Cancel run in UI → worker stops within 10s (checked in integration test).

---

## 7) Artifact Durability

**Rule**: All artifacts MUST be stored in Supabase Storage with run_id prefix.

**Rationale**: Survives DB resets, enables cleanup policies, supports large files.

**Enforcement**:
```typescript
// REQUIRED
const path = `runs/${runId}/${Date.now()}_${filename}`;
await supabase.storage.from('artifacts').upload(path, file);
await supabase.from('artifacts').insert({
  run_id: runId,
  storage_path: path,
  kind: 'file'
});

// FORBIDDEN
await supabase.from('artifacts').insert({ run_id, content_text: largeFile });  // ❌ >1MB breaks
```

**Acceptance**: 10MB artifact uploads successfully, survives DB migrations.

---

## 8) Spec Kit Compliance

**Rule**: Every spec bundle MUST have exactly 4 files: `constitution.md`, `prd.md`, `plan.md`, `tasks.md`.

**Rationale**: Standardized documentation structure enforced by CI.

**Enforcement**:
```bash
# REQUIRED - CI gate
test -f spec/ops-control-room/constitution.md
test -f spec/ops-control-room/prd.md
test -f spec/ops-control-room/plan.md
test -f spec/ops-control-room/tasks.md

# FORBIDDEN
spec/ops-control-room/README.md only  # ❌ Missing required files
```

**Acceptance**: PR fails CI if any of 4 files missing from spec bundle.

---

## 9) Worker Secrets (Never in DB)

**Rule**: Secrets MUST be passed via env vars or DO/Supabase secrets, NEVER stored in `ops.runs.params`.

**Rationale**: Prevents accidental exposure in logs/UI.

**Enforcement**:
```typescript
// REQUIRED
const apiKey = process.env.GITHUB_TOKEN;  // From DO secrets / Supabase vault

// FORBIDDEN
const params = { github_token: 'ghp_xxx...' };  // ❌ Token in DB
await createRun({ params });
```

**Acceptance**: Audit `ops.runs` table → no secrets in `params` column (verified by script).

---

## 10) Deployment Targets (Locked)

**Rule**: UI on Vercel, Control Plane on Supabase, Workers on DigitalOcean.

**Rationale**: Proven stack, avoid infrastructure drift.

**Enforcement**:
```yaml
# REQUIRED
# .github/workflows/deploy-ui.yml
- vercel deploy --prod

# .github/workflows/deploy-workers.yml
- doctl apps update $APP_ID --spec infra/workers.yaml

# FORBIDDEN
# Deploying to Netlify, Heroku, etc.  ❌
```

**Acceptance**: Production deployments only to Vercel/Supabase/DO (verified by CI).

---

## 11) Idempotency (Retries Safe)

**Rule**: All run execution MUST be idempotent (same params → same result).

**Rationale**: Enables safe retries after transient failures.

**Enforcement**:
```typescript
// REQUIRED - Check if already done
const existing = await checkArtifact(runId, 'deployment_proof.json');
if (existing) {
  await logEvent(runId, 'info', 'Deployment already completed, skipping');
  return;
}
await deploy();

// FORBIDDEN
await deploy();  // ❌ No check, runs twice on retry
```

**Acceptance**: Retry same run 3 times → no duplicate side effects (verified by test).

---

## 12) Error Reporting (Structured)

**Rule**: Errors MUST be stored as `jsonb` in `runs.error` with `{ type, message, stack, context }`.

**Rationale**: Enables structured error analysis, not just strings.

**Enforcement**:
```typescript
// REQUIRED
const error = {
  type: 'DeploymentFailed',
  message: 'Asset build failed',
  stack: err.stack,
  context: { step: 'build_assets', exit_code: 1 }
};
await updateRun(runId, { status: 'failed', error });

// FORBIDDEN
await updateRun(runId, { status: 'failed', error: err.toString() });  // ❌ String only
```

**Acceptance**: Failed run shows error type, message, stack in UI (not just generic string).

---

## 13) Template Versioning

**Rule**: Templates MUST have `version` field, changes create new version (not mutate).

**Rationale**: Prevents breaking deployed runs when template changes.

**Enforcement**:
```sql
-- REQUIRED
CREATE TABLE ops.run_templates (
  id UUID PRIMARY KEY,
  name TEXT NOT NULL,
  version INT NOT NULL DEFAULT 1,
  ...
  UNIQUE(name, version)
);

-- When updating template:
INSERT INTO ops.run_templates (name, version, ...) VALUES ('deploy', 2, ...);  -- New version

-- FORBIDDEN
UPDATE ops.run_templates SET steps = $1 WHERE name = 'deploy';  // ❌ Mutates existing
```

**Acceptance**: Changing template creates new version, old runs reference old version.

---

## 14) Health Checks (Workers)

**Rule**: Workers MUST expose `/health` endpoint returning 200 when ready.

**Rationale**: Enables k8s readiness/liveness probes, load balancer health checks.

**Enforcement**:
```typescript
// REQUIRED
app.get('/health', (req, res) => {
  const healthy = canClaimRuns() && supabaseConnected();
  res.status(healthy ? 200 : 503).json({ status: healthy ? 'ok' : 'degraded' });
});

// FORBIDDEN
// No health endpoint  ❌
```

**Acceptance**: k8s deployment uses `httpGet: /health` probe, worker restarts if unhealthy.

---

## 15) Garbage Collection

**Rule**: Runs older than 90 days MUST be archived/deleted (configurable retention policy).

**Rationale**: Prevents unbounded DB growth.

**Enforcement**:
```sql
-- REQUIRED - Scheduled job (daily)
DELETE FROM ops.runs
WHERE status IN ('succeeded', 'failed', 'cancelled')
  AND finished_at < NOW() - INTERVAL '90 days';

-- FORBIDDEN
-- No cleanup job  ❌
```

**Acceptance**: Test data >90 days old is deleted (verified by scheduled job logs).

---

## Acceptance Gates (All Must Pass)

1. ✅ All ops tables in `ops` schema
2. ✅ Concurrent workers never double-execute (FOR UPDATE SKIP LOCKED)
3. ✅ Worker crash triggers recovery within 35s
4. ✅ 4 lanes (A/B/C/D) shown in UI
5. ✅ Run status change reflects in UI within 2s (Realtime)
6. ✅ Cancel stops worker within 10s
7. ✅ 10MB artifact uploads successfully
8. ✅ Spec bundle has all 4 required files (CI enforced)
9. ✅ No secrets in `ops.runs.params` (audit script passes)
10. ✅ Production deploys only to Vercel/Supabase/DO
11. ✅ Retry run 3x → no duplicate side effects
12. ✅ Failed run shows structured error (type/message/stack/context)
13. ✅ Template change creates new version (old runs unaffected)
14. ✅ Worker `/health` endpoint returns 200 when ready
15. ✅ Runs >90 days deleted (retention policy enforced)

---

**Version**: 1.0.0
**Status**: Enforced by CI
**Violation Handling**: PR auto-rejected if any rule broken
