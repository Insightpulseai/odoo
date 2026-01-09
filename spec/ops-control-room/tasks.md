# Ops Control Room — Task Checklist

**Spec Bundle**: `spec/ops-control-room/`
**Status**: Canonical
**Last Updated**: 2026-01-08

---

## Legend

- `[ ]` Not started
- `[▶]` In progress
- `[✓]` Completed
- `[✗]` Blocked
- `[○]` Optional/deferred

---

## M0: Fix Schema Access (CRITICAL)

**Duration**: 1 day | **Priority**: P0 - Blocks all other work

### Schema Configuration

- [ ] **M0.1**: Update Supabase PostgREST config
  - [ ] Navigate to Supabase Dashboard → Settings → API
  - [ ] Update `db-schemas` field: `public,ops,graphql_public`
  - [ ] Save config, wait for restart (~2 min)
  - [ ] Verify: `curl https://<project>.supabase.co/rest/v1/ops.runs` returns 200

- [ ] **M0.2**: Create `ops` schema with grants
  ```sql
  CREATE SCHEMA IF NOT EXISTS ops;
  GRANT USAGE ON SCHEMA ops TO anon, authenticated;
  GRANT ALL ON ALL TABLES IN SCHEMA ops TO anon, authenticated;
  GRANT ALL ON ALL SEQUENCES IN SCHEMA ops TO anon, authenticated;
  GRANT ALL ON ALL FUNCTIONS IN SCHEMA ops TO anon, authenticated;
  ```

- [ ] **M0.3**: Verify API access from UI
  - [ ] Test endpoint: `GET /rest/v1/ops.runs`
  - [ ] Confirm no "Invalid schema: ops" errors
  - [ ] Test with `anon` key (read-only)
  - [ ] Test with `authenticated` key (read-write)

- [ ] **M0.4**: Document schema exposure in constitution.md
  - [ ] Add section: "Schema Exposure Configuration"
  - [ ] Include PostgREST config snippet
  - [ ] Document rollback procedure (Option B: public views)

**Acceptance**: ✅ API access works, no schema errors, RLS enforced

---

## M1: Execution Core (Foundation)

**Duration**: 3-5 days | **Priority**: P1 - Core functionality

### Database Schema

- [ ] **M1.1**: Create `ops.sessions` table
  ```sql
  CREATE TABLE ops.sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    name TEXT NOT NULL,
    description TEXT,
    triggered_by TEXT,
    status TEXT NOT NULL DEFAULT 'active',
    total_runs INT DEFAULT 0,
    succeeded_runs INT DEFAULT 0,
    failed_runs INT DEFAULT 0,
    context JSONB DEFAULT '{}'::jsonb,
    CONSTRAINT sessions_status_check CHECK (status IN ('active', 'completed', 'cancelled'))
  );
  CREATE INDEX idx_sessions_status ON ops.sessions(status);
  CREATE INDEX idx_sessions_created_at ON ops.sessions(created_at DESC);
  ```

- [ ] **M1.2**: Create `ops.lane_type` ENUM
  ```sql
  CREATE TYPE ops.lane_type AS ENUM ('A', 'B', 'C', 'D');
  ```

- [ ] **M1.3**: Create `ops.runs` table
  ```sql
  CREATE TABLE ops.runs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES ops.sessions(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    lane ops.lane_type NOT NULL,
    priority INT DEFAULT 0,
    status TEXT NOT NULL DEFAULT 'queued',
    claimed_by TEXT,
    claimed_at TIMESTAMPTZ,
    started_at TIMESTAMPTZ,
    finished_at TIMESTAMPTZ,
    heartbeat_at TIMESTAMPTZ,
    kind TEXT NOT NULL,
    params JSONB NOT NULL DEFAULT '{}'::jsonb,
    result JSONB,
    error JSONB,
    CONSTRAINT runs_status_check CHECK (status IN ('queued', 'claimed', 'running', 'succeeded', 'failed', 'cancelled'))
  );
  CREATE INDEX idx_runs_session ON ops.runs(session_id);
  CREATE INDEX idx_runs_status_lane ON ops.runs(status, lane);
  CREATE INDEX idx_runs_priority ON ops.runs(priority DESC, created_at ASC);
  CREATE INDEX idx_runs_heartbeat ON ops.runs(heartbeat_at) WHERE status IN ('claimed', 'running');
  ```

- [ ] **M1.4**: Create `ops.run_events` table
  ```sql
  CREATE TABLE ops.run_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id UUID NOT NULL REFERENCES ops.runs(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    level TEXT NOT NULL,
    message TEXT NOT NULL,
    data JSONB,
    CONSTRAINT events_level_check CHECK (level IN ('debug', 'info', 'warn', 'error'))
  );
  CREATE INDEX idx_events_run ON ops.run_events(run_id, created_at DESC);
  ```

- [ ] **M1.5**: Create `ops.artifacts` table
  ```sql
  CREATE TABLE ops.artifacts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id UUID NOT NULL REFERENCES ops.runs(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    kind TEXT NOT NULL,
    name TEXT NOT NULL,
    storage_path TEXT,
    content_text TEXT,
    content_url TEXT,
    size_bytes BIGINT,
    mime_type TEXT,
    metadata JSONB
  );
  CREATE INDEX idx_artifacts_run ON ops.artifacts(run_id);
  ```

- [ ] **M1.6**: Enable RLS on all tables
  ```sql
  ALTER TABLE ops.sessions ENABLE ROW LEVEL SECURITY;
  ALTER TABLE ops.runs ENABLE ROW LEVEL SECURITY;
  ALTER TABLE ops.run_events ENABLE ROW LEVEL SECURITY;
  ALTER TABLE ops.artifacts ENABLE ROW LEVEL SECURITY;

  CREATE POLICY "sessions_policy" ON ops.sessions FOR ALL USING (true);
  CREATE POLICY "runs_policy" ON ops.runs FOR ALL USING (true);
  CREATE POLICY "events_policy" ON ops.run_events FOR ALL USING (true);
  CREATE POLICY "artifacts_policy" ON ops.artifacts FOR ALL USING (true);
  ```

### Edge Function: ops-executor

- [ ] **M1.7**: Create Edge Function project
  ```bash
  supabase functions new ops-executor
  ```

- [ ] **M1.8**: Implement `POST /sessions` (create session)
  - [ ] Parse request body (name, description, triggered_by)
  - [ ] Insert into ops.sessions
  - [ ] Return session_id

- [ ] **M1.9**: Implement `POST /runs` (enqueue run)
  - [ ] Parse request body (session_id, kind, lane, priority, params)
  - [ ] Validate session exists
  - [ ] Insert into ops.runs
  - [ ] Increment session.total_runs
  - [ ] Return run_id

- [ ] **M1.10**: Implement `POST /claim` (claim runs - atomic)
  - [ ] Parse request body (worker_id, lanes, limit)
  - [ ] Execute atomic claim query:
    ```sql
    WITH claimed AS (
      SELECT id FROM ops.runs
      WHERE status = 'queued'
        AND (lane = ANY($1) OR $1 IS NULL)
      ORDER BY priority DESC, created_at ASC
      LIMIT $2
      FOR UPDATE SKIP LOCKED
    )
    UPDATE ops.runs
    SET status = 'claimed', claimed_by = $3, claimed_at = now()
    WHERE id IN (SELECT id FROM claimed)
    RETURNING *;
    ```
  - [ ] Return claimed runs array

- [ ] **M1.11**: Implement `PATCH /runs/:id` (update run status)
  - [ ] Parse request body (status, started_at, finished_at, result, error)
  - [ ] Update ops.runs
  - [ ] Update session counters (succeeded_runs, failed_runs)

- [ ] **M1.12**: Implement `POST /runs/:id/heartbeat` (worker heartbeat)
  - [ ] Update heartbeat_at = now()
  - [ ] Return 200

- [ ] **M1.13**: Implement `POST /runs/:id/artifacts` (upload artifact)
  - [ ] Parse request body (kind, name, storage_path, content_text, content_url)
  - [ ] Insert into ops.artifacts
  - [ ] Return artifact_id

- [ ] **M1.14**: Deploy Edge Function
  ```bash
  supabase functions deploy ops-executor
  ```

### Worker Reference Implementation

- [ ] **M1.15**: Create worker project
  ```bash
  mkdir workers/ops-executor
  cd workers/ops-executor
  npm init -y
  npm install @supabase/supabase-js dotenv
  ```

- [ ] **M1.16**: Implement claim loop
  ```typescript
  async function claimAndExecute() {
    const { data: runs } = await supabase.functions.invoke('ops-executor/claim', {
      body: {
        worker_id: WORKER_ID,
        lanes: ['A', 'B', 'C', 'D'],
        limit: 4
      }
    });

    for (const run of runs) {
      await executeRun(run);
    }
  }

  setInterval(claimAndExecute, 5000);
  ```

- [ ] **M1.17**: Implement run execution (mock)
  ```typescript
  async function executeRun(run) {
    // Update to 'running'
    await updateRunStatus(run.id, 'running', { started_at: new Date() });

    // Start heartbeat
    const heartbeatInterval = setInterval(() => sendHeartbeat(run.id), 5000);

    try {
      // Mock execution
      await sleep(Math.random() * 10000);

      // Check for cancellation
      const current = await getRunStatus(run.id);
      if (current.status === 'cancelled') {
        clearInterval(heartbeatInterval);
        return;
      }

      // Update to 'succeeded'
      await updateRunStatus(run.id, 'succeeded', {
        finished_at: new Date(),
        result: { message: 'Mock execution complete' }
      });
    } catch (err) {
      await updateRunStatus(run.id, 'failed', {
        finished_at: new Date(),
        error: {
          type: err.name,
          message: err.message,
          stack: err.stack,
          context: { run_kind: run.kind }
        }
      });
    } finally {
      clearInterval(heartbeatInterval);
    }
  }
  ```

- [ ] **M1.18**: Implement heartbeat sender
  ```typescript
  async function sendHeartbeat(runId) {
    await supabase.functions.invoke(`ops-executor/runs/${runId}/heartbeat`);
  }
  ```

- [ ] **M1.19**: Implement cancellation check
  ```typescript
  async function getRunStatus(runId) {
    const { data } = await supabase
      .from('ops.runs')
      .select('status')
      .eq('id', runId)
      .single();
    return data;
  }
  ```

- [ ] **M1.20**: Add environment variable config
  ```bash
  SUPABASE_URL=https://<project>.supabase.co
  SUPABASE_ANON_KEY=<anon_key>
  WORKER_ID=worker-1
  ```

### Stuck-Run Recovery

- [ ] **M1.21**: Create scheduled Edge Function: `ops-recovery`
  ```typescript
  Deno.cron('recovery', '*/30 * * * * *', async () => {
    // Find stuck runs
    const { data: stuck } = await supabase
      .from('ops.runs')
      .update({
        status: 'failed',
        finished_at: new Date(),
        error: {
          type: 'HeartbeatTimeout',
          message: 'Worker heartbeat timeout (>30s)',
          context: { last_heartbeat: 'heartbeat_at' }
        }
      })
      .in('status', ['claimed', 'running'])
      .lt('heartbeat_at', new Date(Date.now() - 30000))
      .select();

    console.log(`Recovered ${stuck.length} stuck runs`);
  });
  ```

- [ ] **M1.22**: Deploy recovery function
  ```bash
  supabase functions deploy ops-recovery
  ```

### Basic UI (Runboard)

- [ ] **M1.23**: Create UI project
  ```bash
  npx create-next-app@latest ops-control-room --typescript --tailwind --app
  cd ops-control-room
  npm install @supabase/supabase-js
  ```

- [ ] **M1.24**: Implement session list view
  - [ ] Fetch sessions from API
  - [ ] Display in table: name, status, total/succeeded/failed runs
  - [ ] Click to view session details

- [ ] **M1.25**: Implement run list view (4 lanes)
  - [ ] Fetch runs for session
  - [ ] Group by lane (A, B, C, D)
  - [ ] Display status icons: ✓ succeeded, 🔄 running, ⏳ claimed, 📋 queued, ❌ failed

- [ ] **M1.26**: Implement real-time updates
  ```typescript
  supabase
    .channel('runs')
    .on('postgres_changes', {
      event: '*',
      schema: 'ops',
      table: 'runs'
    }, (payload) => {
      updateRunInUI(payload.new);
    })
    .subscribe();
  ```

- [ ] **M1.27**: Implement cancel run button
  - [ ] Call API: `PATCH /runs/:id` with `status='cancelled'`
  - [ ] Verify worker stops within 10s

- [ ] **M1.28**: Deploy UI to Vercel
  ```bash
  vercel --prod
  ```

### M1 Testing

- [ ] **M1.29**: Integration test: Atomic claiming
  - [ ] Enqueue 10 runs
  - [ ] Start 2 workers concurrently
  - [ ] Verify each run claimed by exactly 1 worker
  - [ ] Verify zero double execution

- [ ] **M1.30**: Integration test: Stuck-run recovery
  - [ ] Start worker, claim run
  - [ ] Kill worker mid-execution
  - [ ] Wait 35s
  - [ ] Verify run status = 'failed' with HeartbeatTimeout error

- [ ] **M1.31**: Integration test: Real-time updates
  - [ ] Open UI in browser
  - [ ] Enqueue run via API
  - [ ] Measure time until UI updates
  - [ ] Verify <2s latency

- [ ] **M1.32**: Integration test: Cancellation
  - [ ] Start worker, claim run
  - [ ] Click cancel in UI
  - [ ] Measure time until worker stops
  - [ ] Verify <10s

**M1 Acceptance**: ✅ All integration tests pass, UI shows real-time updates

---

## M2: Scale & Reliability (Production-Ready)

**Duration**: 2-3 days | **Priority**: P2 - Production hardening

### Worker Deployment

- [ ] **M2.1**: Create Dockerfile
  ```dockerfile
  FROM node:20-alpine
  RUN apk add --no-cache git
  WORKDIR /app
  COPY package*.json ./
  RUN npm ci --production
  COPY . .
  EXPOSE 3000
  HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD node healthcheck.js
  CMD ["node", "worker.js"]
  ```

- [ ] **M2.2**: Implement health check endpoint
  ```typescript
  // healthcheck.js
  const http = require('http');
  const options = { host: 'localhost', port: 3000, path: '/health', timeout: 2000 };
  http.get(options, (res) => {
    process.exit(res.statusCode === 200 ? 0 : 1);
  }).on('error', () => process.exit(1));
  ```

- [ ] **M2.3**: Create DigitalOcean App Platform spec
  ```yaml
  name: ops-executor-workers
  region: sgp
  services:
  - name: worker
    dockerfile_path: Dockerfile
    github:
      repo: <username>/odoo-ce
      branch: main
      deploy_on_push: true
    instance_count: 3
    instance_size_slug: basic-xs
    health_check:
      http_path: /health
    envs:
    - key: SUPABASE_URL
      value: ${SUPABASE_URL}
    - key: SUPABASE_ANON_KEY
      type: SECRET
      value: ${SUPABASE_ANON_KEY}
    - key: WORKER_ID
      value: worker-${RANDOM_UUID}
  ```

- [ ] **M2.4**: Deploy workers to DigitalOcean
  ```bash
  doctl apps create --spec ops-workers.yaml
  ```

- [ ] **M2.5**: Verify 3 workers running
  ```bash
  doctl apps list
  doctl apps logs <app_id> --follow
  ```

### Template System

- [ ] **M2.6**: Create `ops.run_templates` table
  ```sql
  CREATE TABLE ops.run_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    name TEXT NOT NULL,
    version INT NOT NULL DEFAULT 1,
    description TEXT,
    kind TEXT NOT NULL,
    steps JSONB NOT NULL,
    timeout_seconds INT DEFAULT 300,
    retry_policy JSONB,
    UNIQUE(name, version)
  );
  CREATE INDEX idx_templates_name ON ops.run_templates(name, version DESC);
  ```

- [ ] **M2.7**: Implement template execution in worker
  ```typescript
  async function executeTemplate(run) {
    const template = await getTemplate(run.kind, run.params.template_version || 1);
    for (const step of template.steps) {
      await executeStep(step, run.params);
    }
  }
  ```

### Artifact Storage

- [ ] **M2.8**: Create Supabase Storage bucket: `artifacts`
  ```sql
  INSERT INTO storage.buckets (id, name, public) VALUES ('artifacts', 'artifacts', false);
  ```

- [ ] **M2.9**: Configure bucket policy
  ```sql
  CREATE POLICY "artifacts_authenticated"
  ON storage.objects FOR ALL
  USING (bucket_id = 'artifacts' AND auth.role() = 'authenticated');
  ```

- [ ] **M2.10**: Implement file upload in worker
  ```typescript
  async function uploadArtifact(runId, file) {
    const path = `runs/${runId}/${Date.now()}_${file.name}`;
    const { data, error } = await supabase.storage
      .from('artifacts')
      .upload(path, file);

    await supabase.functions.invoke('ops-executor/runs/:id/artifacts', {
      body: {
        kind: 'file',
        name: file.name,
        storage_path: path,
        size_bytes: file.size,
        mime_type: file.type
      }
    });
  }
  ```

- [ ] **M2.11**: Configure retention policy (90 days)
  ```sql
  -- Manual cleanup job (run weekly)
  DELETE FROM storage.objects
  WHERE bucket_id = 'artifacts'
    AND created_at < NOW() - INTERVAL '90 days';
  ```

### Error Handling & Logging

- [ ] **M2.12**: Implement structured error format
  ```typescript
  interface RunError {
    type: string;        // Error class name
    message: string;     // Human-readable message
    stack: string;       // Stack trace
    context: Record<string, any>; // Additional context
  }
  ```

- [ ] **M2.13**: Implement event logging
  ```typescript
  async function logEvent(runId, level, message, data = {}) {
    await supabase.from('ops.run_events').insert({
      run_id: runId,
      level,
      message,
      data
    });
  }
  ```

- [ ] **M2.14**: Add error rate monitoring
  ```sql
  SELECT
    COUNT(*) FILTER (WHERE status = 'failed') * 100.0 / COUNT(*) AS error_rate
  FROM ops.runs
  WHERE created_at > NOW() - INTERVAL '1 hour';
  ```

### Health Checks & Monitoring

- [ ] **M2.15**: Implement worker /health endpoint
  ```typescript
  app.get('/health', (req, res) => {
    const healthy = canClaimRuns() && supabaseConnected();
    res.status(healthy ? 200 : 503).json({
      status: healthy ? 'ok' : 'degraded',
      uptime: process.uptime(),
      worker_id: WORKER_ID
    });
  });
  ```

- [ ] **M2.16**: Create metrics dashboard (basic)
  - [ ] Total runs (queued, running, succeeded, failed)
  - [ ] Average execution time
  - [ ] Error rate (last hour)
  - [ ] Worker count

### M2 Testing

- [ ] **M2.17**: Load test: 100+ concurrent runs
  - [ ] Enqueue 100 runs
  - [ ] Monitor completion time
  - [ ] Verify error rate <1%

- [ ] **M2.18**: Load test: 10MB artifact upload
  - [ ] Generate 10MB file
  - [ ] Upload via worker
  - [ ] Verify file in Supabase Storage

- [ ] **M2.19**: Failover test: Worker crash
  - [ ] Start 3 workers
  - [ ] Kill worker mid-execution
  - [ ] Verify run recovered by another worker
  - [ ] Verify <35s recovery time

**M2 Acceptance**: ✅ 100+ runs executed, error rate <1%, workers auto-restart

---

## M3: Spec Kit Integration (Feature Complete)

**Duration**: 2-3 days | **Priority**: P3 - Automation

### Spec Kit Generator Worker

- [ ] **M3.1**: Create kind: `spec_kit_generate`
  - [ ] Input params: `{ feature: string, files: string[] }`
  - [ ] Output: 4 markdown files in `spec/<feature>/`

- [ ] **M3.2**: Implement constitution.md generator
  - [ ] Template with immutable rules
  - [ ] Customization based on feature context

- [ ] **M3.3**: Implement prd.md generator
  - [ ] Template with problem statement, solution, architecture

- [ ] **M3.4**: Implement plan.md generator
  - [ ] Template with milestones, dependencies, risks

- [ ] **M3.5**: Implement tasks.md generator
  - [ ] Template with task checklist, legend

- [ ] **M3.6**: Implement git commit automation
  ```typescript
  await exec('git add spec/<feature>/*');
  await exec('git commit -m "feat(spec): add <feature> spec bundle"');
  await exec('git push origin main');
  ```

### GitHub Integration

- [ ] **M3.7**: Create GitHub App
  - [ ] Navigate to GitHub → Settings → Developer settings → GitHub Apps
  - [ ] Create new app: "Ops Control Room"
  - [ ] Permissions: Repo contents (read/write), Pull requests (read/write)
  - [ ] Subscribe to events: pull_request, push

- [ ] **M3.8**: Install GitHub App to repo

- [ ] **M3.9**: Implement webhook receiver (Edge Function)
  ```typescript
  Deno.serve(async (req) => {
    const payload = await req.json();

    if (payload.action === 'opened' && payload.pull_request) {
      // Enqueue lint + test + build runs
      await createSession({ name: `PR ${payload.pull_request.number}` });
      await enqueueRuns(['lint', 'test', 'build']);
    }

    return new Response('OK');
  });
  ```

- [ ] **M3.10**: Implement status check reporting
  ```typescript
  await octokit.repos.createCommitStatus({
    owner,
    repo,
    sha,
    state: 'pending',
    context: 'ops-control-room/test',
    description: 'Running tests...'
  });
  ```

### CI Enforcement

- [ ] **M3.11**: Create GitHub Actions workflow: `spec-kit-enforce.yml`
  ```yaml
  name: Spec Kit Enforce
  on: [push, pull_request]
  jobs:
    enforce:
      runs-on: ubuntu-latest
      steps:
      - uses: actions/checkout@v3
      - name: Check spec bundles
        run: |
          for dir in spec/*/; do
            test -f "$dir/constitution.md" || exit 1
            test -f "$dir/prd.md" || exit 1
            test -f "$dir/plan.md" || exit 1
            test -f "$dir/tasks.md" || exit 1
          done
  ```

- [ ] **M3.12**: Commit and push workflow
  ```bash
  git add .github/workflows/spec-kit-enforce.yml
  git commit -m "ci: add spec kit enforcement"
  git push origin main
  ```

### UI Enhancements

- [ ] **M3.13**: Create Spec Kit generation form
  - [ ] Input: Feature name
  - [ ] Checkboxes: constitution, prd, plan, tasks
  - [ ] Submit → Enqueue run

- [ ] **M3.14**: Implement file preview (artifact viewer)
  - [ ] Fetch artifact content from Supabase Storage
  - [ ] Display markdown with syntax highlighting

- [ ] **M3.15**: Implement download all artifacts (ZIP)
  ```typescript
  const zip = new JSZip();
  for (const artifact of artifacts) {
    const content = await fetchArtifact(artifact.storage_path);
    zip.file(artifact.name, content);
  }
  const blob = await zip.generateAsync({ type: 'blob' });
  saveAs(blob, 'artifacts.zip');
  ```

### M3 Testing

- [ ] **M3.16**: End-to-end test: Spec Kit generation
  - [ ] Trigger via UI
  - [ ] Verify 4 files created in `spec/<feature>/`
  - [ ] Verify files committed to git
  - [ ] Verify artifacts in Supabase Storage

- [ ] **M3.17**: End-to-end test: GitHub integration
  - [ ] Open PR
  - [ ] Verify runs enqueued
  - [ ] Verify status checks reported
  - [ ] Merge PR when checks pass

- [ ] **M3.18**: CI test: Spec Kit enforcement
  - [ ] Create PR with incomplete spec bundle (missing tasks.md)
  - [ ] Verify CI fails
  - [ ] Add missing file
  - [ ] Verify CI passes

**M3 Acceptance**: ✅ Spec Kit auto-generated, GitHub integration working, CI enforces structure

---

## Post-Launch (Ongoing)

- [ ] **P1**: Monitor error rates daily
- [ ] **P2**: Review stuck-run recovery logs weekly
- [ ] **P3**: Optimize worker resource usage
- [ ] **P4**: Implement advanced scheduling (cron, recurring)
- [ ] **P5**: Add run dependencies (DAG execution)
- [ ] **P6**: Multi-tenancy support
- [ ] **P7**: Advanced analytics dashboard (Grafana)

---

## Checklist Summary

**M0**: 4 tasks (schema access fix)
**M1**: 32 tasks (execution core, Edge Function, worker, UI)
**M2**: 19 tasks (scaling, templates, artifacts, monitoring)
**M3**: 18 tasks (Spec Kit generator, GitHub, CI)

**Total**: 73 tasks

**Status**:
- Not started: 73
- In progress: 0
- Completed: 0
- Blocked: 0

---

**Version**: 1.0.0
**Status**: Ready for Execution
**Next**: Begin M0 (Fix Schema Access)
