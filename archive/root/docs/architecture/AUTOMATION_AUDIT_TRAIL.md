# Automation Audit Trail Architecture

**Last Updated:** 2026-02-20
**Scope:** n8n workflows, Gemini API, Google integrations, automation execution tracking
**SSOT:** Supabase `ops.*` tables

---

## Purpose

This document defines the canonical audit trail structure for all automation and integration actions, ensuring:
- Complete provenance tracking (who, what, when, why, how)
- Compliance readiness (SOC2, GDPR, internal audit)
- Debug-ability (correlation across distributed systems)
- Cost monitoring (API quotas, token usage)

---

## Audit Trail Principles

### 1. Completeness

**Every automation action MUST be logged:**
- Workflow executions (n8n, Edge Functions, scheduled jobs)
- External API calls (Gemini, Google, Odoo RPC)
- Credential usage (OAuth refreshes, service account calls)
- Integration state changes (sync cursors, checkpoints)

**No exceptions:** Missing audit trails are treated as compliance failures.

### 2. Correlation

**Every event MUST include:**
- `correlation_id` (UUID, propagated across systems)
- `run_id` (FK to `ops.runs`)
- `agent_id` or `workflow_id` (which entity initiated)

**Distributed tracing:** Follow `correlation_id` across Supabase → n8n → Google → Odoo

### 3. Immutability

**Audit logs MUST be append-only:**
- No updates to `ops.run_events` after insert
- Corrections are new events with `correction_of` FK
- Retention: 30 days in hot storage, 90 days in cold storage

### 4. Queryability

**Audit data MUST be queryable:**
- SQL-friendly schema (Supabase PostgreSQL)
- Indexed by: `correlation_id`, `run_id`, `event_type`, `created_at`
- Materialized views for common queries (daily API usage, error rates)

---

## Table Schema

### ops.runs (Run Lifecycle)

```sql
CREATE TABLE IF NOT EXISTS ops.runs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  correlation_id TEXT NOT NULL UNIQUE,
  agent_id TEXT,  -- e.g., 'gemini-assistant', 'n8n-drive-sync'
  workflow_id TEXT,  -- n8n workflow ID (if applicable)
  task_name TEXT NOT NULL,  -- e.g., 'summarize-meeting', 'sync-drive-files'
  status TEXT NOT NULL CHECK (status IN ('pending', 'running', 'completed', 'failed')),
  started_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  completed_at TIMESTAMPTZ,
  error_message TEXT,  -- if status = 'failed'
  metadata JSONB,  -- arbitrary context (user_id, org_id, etc.)
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_runs_correlation_id ON ops.runs (correlation_id);
CREATE INDEX idx_runs_status ON ops.runs (status) WHERE status IN ('running', 'failed');
CREATE INDEX idx_runs_created_at ON ops.runs (created_at DESC);
```

### ops.run_events (Detailed Event Log)

```sql
CREATE TABLE IF NOT EXISTS ops.run_events (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  run_id UUID NOT NULL REFERENCES ops.runs(id) ON DELETE CASCADE,
  event_type TEXT NOT NULL,  -- e.g., 'gemini_api_call', 'google_api_call', 'workflow_step_completed'
  event_data JSONB NOT NULL,  -- provider-specific metadata
  correlation_id TEXT NOT NULL,  -- matches ops.runs.correlation_id
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_run_events_run_id ON ops.run_events (run_id);
CREATE INDEX idx_run_events_event_type ON ops.run_events (event_type);
CREATE INDEX idx_run_events_correlation_id ON ops.run_events (correlation_id);
CREATE INDEX idx_run_events_created_at ON ops.run_events (created_at DESC);
```

**event_data Schema Examples:**

**Gemini API Call:**
```json
{
  "provider": "gemini",
  "model": "gemini-1.5-pro",
  "operation": "generateContent",
  "prompt_tokens": 15,
  "completion_tokens": 234,
  "total_tokens": 249,
  "response_status": 200,
  "latency_ms": 1234,
  "finish_reason": "STOP"
}
```

**Google API Call:**
```json
{
  "provider": "google",
  "service": "drive",
  "operation": "files.list",
  "credential_type": "service_account",
  "request_id": "req-xyz789",
  "response_status": 200,
  "quota_consumed": 1,
  "latency_ms": 567
}
```

**n8n Workflow Step:**
```json
{
  "workflow_id": "wf-123",
  "workflow_name": "Drive Sync to Odoo",
  "node_id": "GoogleDrive_1",
  "node_type": "n8n-nodes-base.googleDrive",
  "execution_status": "success",
  "items_processed": 42
}
```

### ops.integration_state (Sync Cursors & Checkpoints)

```sql
CREATE TABLE IF NOT EXISTS ops.integration_state (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  integration_name TEXT NOT NULL,  -- e.g., 'google-drive-sync'
  state_key TEXT NOT NULL,  -- e.g., 'last_sync_token', 'last_processed_file_id'
  state_value JSONB NOT NULL,
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (integration_name, state_key)
);

CREATE INDEX idx_integration_state_name ON ops.integration_state (integration_name);
```

**Example State Values:**
```json
// Drive sync cursor
{
  "token": "abc123",
  "timestamp": "2026-02-20T12:00:00Z",
  "files_processed": 42
}

// Notion last sync
{
  "page_id": "notion-page-id",
  "last_edited_time": "2026-02-20T11:30:00Z"
}
```

### ops.credential_rotations (Credential Lifecycle)

```sql
CREATE TABLE IF NOT EXISTS ops.credential_rotations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  credential_type TEXT NOT NULL,  -- e.g., 'oauth2', 'service_account', 'api_key'
  provider TEXT NOT NULL,  -- e.g., 'google', 'gemini', 'odoo'
  credential_name TEXT NOT NULL,  -- e.g., 'Google Service Account - Drive Sync'
  rotated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  rotated_by TEXT NOT NULL,  -- e.g., 'automation', 'admin@example.com'
  rotation_reason TEXT,  -- e.g., '90-day cadence', 'security incident'
  metadata JSONB
);

CREATE INDEX idx_credential_rotations_provider ON ops.credential_rotations (provider);
CREATE INDEX idx_credential_rotations_rotated_at ON ops.credential_rotations (rotated_at DESC);
```

---

## Event Emission Patterns

### Pattern 1: Supabase Edge Function

```typescript
import { createClient } from '@supabase/supabase-js';

const supabase = createClient(
  Deno.env.get('SUPABASE_URL')!,
  Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!
);

async function emitRunEvent(runId: string, eventType: string, eventData: object) {
  await supabase.from('ops.run_events').insert({
    run_id: runId,
    event_type: eventType,
    event_data: eventData,
    correlation_id: Deno.env.get('CORRELATION_ID')!,
  });
}

// Usage
const { data: run } = await supabase.from('ops.runs').insert({
  correlation_id: crypto.randomUUID(),
  task_name: 'gemini-summarize',
  status: 'running',
}).select().single();

// Call Gemini API
const geminiResponse = await callGemini(prompt);

// Emit audit event
await emitRunEvent(run.id, 'gemini_api_call', {
  provider: 'gemini',
  model: 'gemini-1.5-pro',
  total_tokens: geminiResponse.usageMetadata.totalTokenCount,
  response_status: 200,
});

// Update run status
await supabase.from('ops.runs').update({
  status: 'completed',
  completed_at: new Date().toISOString(),
}).eq('id', run.id);
```

### Pattern 2: n8n Workflow (via HTTP Request Node)

```json
{
  "nodes": [
    {
      "name": "Emit Audit Event",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "url": "={{ $env.SUPABASE_URL }}/rest/v1/ops.run_events",
        "method": "POST",
        "headers": {
          "apikey": "={{ $env.SUPABASE_SERVICE_ROLE_KEY }}",
          "Authorization": "Bearer {{ $env.SUPABASE_SERVICE_ROLE_KEY }}",
          "Content-Type": "application/json"
        },
        "body": {
          "run_id": "={{ $node['Create Run'].json.id }}",
          "event_type": "google_api_call",
          "event_data": {
            "provider": "google",
            "service": "drive",
            "operation": "files.list",
            "response_status": "={{ $node['Google Drive'].json.status }}"
          },
          "correlation_id": "={{ $node['Create Run'].json.correlation_id }}"
        }
      }
    }
  ]
}
```

### Pattern 3: Background Worker (Node.js)

```typescript
import { createClient } from '@supabase/supabase-js';

const supabase = createClient(
  process.env.SUPABASE_URL!,
  process.env.SUPABASE_SERVICE_ROLE_KEY!
);

class AuditLogger {
  constructor(private runId: string, private correlationId: string) {}

  async log(eventType: string, eventData: object) {
    await supabase.from('ops.run_events').insert({
      run_id: this.runId,
      event_type: eventType,
      event_data: eventData,
      correlation_id: this.correlationId,
    });
  }
}

// Usage
const run = await supabase.from('ops.runs').insert({
  correlation_id: crypto.randomUUID(),
  task_name: 'scheduled-drive-sync',
  status: 'running',
}).select().single();

const logger = new AuditLogger(run.data.id, run.data.correlation_id);

try {
  const files = await listDriveFiles();
  await logger.log('google_api_call', {
    provider: 'google',
    service: 'drive',
    operation: 'files.list',
    files_count: files.length,
  });

  // Process files...

  await supabase.from('ops.runs').update({
    status: 'completed',
    completed_at: new Date().toISOString(),
  }).eq('id', run.data.id);
} catch (error) {
  await logger.log('error', { message: error.message });
  await supabase.from('ops.runs').update({
    status: 'failed',
    error_message: error.message,
    completed_at: new Date().toISOString(),
  }).eq('id', run.data.id);
}
```

---

## Compliance Queries

### Daily API Usage Report

```sql
SELECT
  DATE(created_at) AS date,
  event_data->>'provider' AS provider,
  event_data->>'operation' AS operation,
  COUNT(*) AS call_count,
  SUM((event_data->>'total_tokens')::int) AS total_tokens
FROM ops.run_events
WHERE event_type IN ('gemini_api_call', 'google_api_call')
  AND created_at >= NOW() - INTERVAL '30 days'
GROUP BY DATE(created_at), provider, operation
ORDER BY date DESC, call_count DESC;
```

### Failed Runs (Last 7 Days)

```sql
SELECT
  r.id,
  r.correlation_id,
  r.task_name,
  r.agent_id,
  r.error_message,
  r.started_at,
  r.completed_at
FROM ops.runs r
WHERE r.status = 'failed'
  AND r.created_at >= NOW() - INTERVAL '7 days'
ORDER BY r.created_at DESC;
```

### Credential Rotation Compliance

```sql
SELECT
  provider,
  credential_name,
  rotated_at,
  NOW() - rotated_at AS days_since_rotation,
  CASE
    WHEN NOW() - rotated_at > INTERVAL '90 days' THEN 'OVERDUE'
    WHEN NOW() - rotated_at > INTERVAL '75 days' THEN 'WARNING'
    ELSE 'OK'
  END AS rotation_status
FROM ops.credential_rotations
WHERE credential_type = 'service_account'
ORDER BY rotated_at ASC;
```

---

## Cross-References

- **Gemini API Integration:** `docs/integrations/gemini/QUICKSTART_NOTES.md`
- **n8n Google Credentials:** `docs/integrations/n8n/GOOGLE_CREDENTIALS.md`
- **SSOT Policy:** `spec/odoo-ee-parity-seed/constitution.md` (Article 3: Integration Invariants)
- **n8n ↔ Odoo Bridge:** `spec/odoo-sh/prd.md` (FR6: n8n Workflow Automation Layer)
