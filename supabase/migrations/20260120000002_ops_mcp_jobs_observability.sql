-- MCP Jobs & Observability Schema
-- Provides job queue, run tracking, and event logging for infrastructure operations
-- Uses pgmq for message queuing and pg_cron for scheduled execution

-- =============================================================================
-- SCHEMAS
-- =============================================================================

CREATE SCHEMA IF NOT EXISTS ops;
CREATE SCHEMA IF NOT EXISTS ops_mcp;

-- =============================================================================
-- JOBS TABLE (Job Definitions)
-- =============================================================================

CREATE TABLE IF NOT EXISTS ops.jobs (
  id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  slug          text NOT NULL UNIQUE,              -- e.g. 'infra_scan_vercel'
  description   text NOT NULL,
  enabled       boolean NOT NULL DEFAULT true,
  schedule_cron text,                              -- optional: for pg_cron scheduling
  job_type      text NOT NULL,                     -- enum-ish: 'infra', 'mcp', 'kg', 'sync'
  handler       text NOT NULL DEFAULT 'default',   -- which handler to invoke
  payload_schema jsonb DEFAULT '{}'::jsonb,        -- JSON schema for payload validation
  timeout_seconds int DEFAULT 300,                 -- max execution time
  retry_count   int DEFAULT 0,                     -- number of retries on failure
  created_at    timestamptz NOT NULL DEFAULT now(),
  updated_at    timestamptz NOT NULL DEFAULT now()
);

COMMENT ON TABLE ops.jobs IS 'Job definitions for MCP and infrastructure operations';
COMMENT ON COLUMN ops.jobs.slug IS 'Unique identifier for the job type';
COMMENT ON COLUMN ops.jobs.job_type IS 'Category: infra (infrastructure scans), mcp (agent introspection), kg (knowledge graph), sync (data sync)';
COMMENT ON COLUMN ops.jobs.handler IS 'Handler function name in ops-job-worker Edge Function';

-- =============================================================================
-- JOB RUNS TABLE (Execution Instances)
-- =============================================================================

CREATE TABLE IF NOT EXISTS ops.job_runs (
  id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  job_id        uuid NOT NULL REFERENCES ops.jobs(id) ON DELETE CASCADE,
  status        text NOT NULL DEFAULT 'queued',    -- queued|running|success|error|timeout
  requested_by  text,                              -- user/email/agent id
  payload       jsonb DEFAULT '{}'::jsonb,         -- input parameters
  result        jsonb,                             -- output data
  error_message text,                              -- error details if failed
  retry_attempt int DEFAULT 0,                     -- current retry attempt
  started_at    timestamptz,
  finished_at   timestamptz,
  created_at    timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_job_runs_job_id ON ops.job_runs(job_id);
CREATE INDEX IF NOT EXISTS idx_job_runs_status ON ops.job_runs(status);
CREATE INDEX IF NOT EXISTS idx_job_runs_created_at ON ops.job_runs(created_at DESC);

COMMENT ON TABLE ops.job_runs IS 'Individual job execution instances';
COMMENT ON COLUMN ops.job_runs.status IS 'Execution status: queued, running, success, error, timeout';

-- =============================================================================
-- JOB EVENTS TABLE (Append-Only Log)
-- =============================================================================

CREATE TABLE IF NOT EXISTS ops.job_events (
  id            bigserial PRIMARY KEY,
  job_run_id    uuid NOT NULL REFERENCES ops.job_runs(id) ON DELETE CASCADE,
  event_type    text NOT NULL,                     -- queued|started|log|warning|error|done|timeout
  message       text,
  data          jsonb,
  occurred_at   timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_job_events_run_id ON ops.job_events(job_run_id);
CREATE INDEX IF NOT EXISTS idx_job_events_type ON ops.job_events(event_type);
CREATE INDEX IF NOT EXISTS idx_job_events_occurred ON ops.job_events(occurred_at DESC);

COMMENT ON TABLE ops.job_events IS 'Append-only event log for job execution';
COMMENT ON COLUMN ops.job_events.event_type IS 'Event type: queued, started, log, warning, error, done, timeout';

-- =============================================================================
-- MCP TOOLS TABLE (Tool Registry)
-- =============================================================================

CREATE TABLE IF NOT EXISTS ops_mcp.tools (
  id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  server_name   text NOT NULL,                     -- e.g. 'odoo-erp', 'supabase', 'github'
  tool_name     text NOT NULL,                     -- e.g. 'search_read', 'query', 'get_file'
  description   text,
  input_schema  jsonb,                             -- JSON schema for tool inputs
  last_invoked_at timestamptz,
  invocation_count bigint DEFAULT 0,
  avg_duration_ms numeric,
  error_rate    numeric DEFAULT 0,
  created_at    timestamptz NOT NULL DEFAULT now(),
  updated_at    timestamptz NOT NULL DEFAULT now(),
  UNIQUE(server_name, tool_name)
);

COMMENT ON TABLE ops_mcp.tools IS 'Registry of MCP tools and their usage statistics';

-- =============================================================================
-- VIEWS
-- =============================================================================

-- Latest run status per job
CREATE OR REPLACE VIEW ops.v_job_latest AS
SELECT
  j.id AS job_id,
  j.slug,
  j.description,
  j.enabled,
  j.job_type,
  j.schedule_cron,
  jr.id AS last_run_id,
  jr.status AS last_status,
  jr.started_at AS last_started,
  jr.finished_at AS last_finished,
  EXTRACT(EPOCH FROM (jr.finished_at - jr.started_at)) AS last_duration_seconds,
  jr.error_message AS last_error
FROM ops.jobs j
LEFT JOIN LATERAL (
  SELECT *
  FROM ops.job_runs r
  WHERE r.job_id = j.id
  ORDER BY r.created_at DESC
  LIMIT 1
) jr ON true;

COMMENT ON VIEW ops.v_job_latest IS 'Jobs with their most recent run status';

-- Job run history with event counts
CREATE OR REPLACE VIEW ops.v_job_run_history AS
SELECT
  jr.id AS run_id,
  j.slug AS job_slug,
  jr.status,
  jr.requested_by,
  jr.started_at,
  jr.finished_at,
  EXTRACT(EPOCH FROM (jr.finished_at - jr.started_at)) AS duration_seconds,
  jr.error_message,
  (SELECT COUNT(*) FROM ops.job_events e WHERE e.job_run_id = jr.id) AS event_count,
  (SELECT COUNT(*) FROM ops.job_events e WHERE e.job_run_id = jr.id AND e.event_type = 'error') AS error_count
FROM ops.job_runs jr
JOIN ops.jobs j ON j.id = jr.job_id
ORDER BY jr.created_at DESC;

COMMENT ON VIEW ops.v_job_run_history IS 'Job run history with event statistics';

-- Dashboard summary
CREATE OR REPLACE VIEW ops.v_dashboard_summary AS
SELECT
  (SELECT COUNT(*) FROM ops.jobs WHERE enabled = true) AS active_jobs,
  (SELECT COUNT(*) FROM ops.job_runs WHERE status = 'running') AS running_jobs,
  (SELECT COUNT(*) FROM ops.job_runs WHERE status = 'queued') AS queued_jobs,
  (SELECT COUNT(*) FROM ops.job_runs WHERE status = 'error' AND created_at > now() - interval '24 hours') AS errors_24h,
  (SELECT COUNT(*) FROM ops.job_runs WHERE status = 'success' AND created_at > now() - interval '24 hours') AS success_24h,
  (SELECT AVG(EXTRACT(EPOCH FROM (finished_at - started_at))) FROM ops.job_runs WHERE finished_at IS NOT NULL AND created_at > now() - interval '24 hours') AS avg_duration_24h;

COMMENT ON VIEW ops.v_dashboard_summary IS 'Summary statistics for ops dashboard';

-- MCP tools summary
CREATE OR REPLACE VIEW ops_mcp.v_tools_summary AS
SELECT
  server_name,
  COUNT(*) AS tool_count,
  SUM(invocation_count) AS total_invocations,
  AVG(avg_duration_ms) AS avg_duration_ms,
  AVG(error_rate) AS avg_error_rate,
  MAX(last_invoked_at) AS last_activity
FROM ops_mcp.tools
GROUP BY server_name
ORDER BY total_invocations DESC;

COMMENT ON VIEW ops_mcp.v_tools_summary IS 'MCP tools grouped by server with usage statistics';

-- =============================================================================
-- PGMQ QUEUE SETUP
-- =============================================================================

-- Enable pgmq extension
CREATE EXTENSION IF NOT EXISTS pgmq WITH SCHEMA public;

-- Create the ops_jobs queue
DO $$
BEGIN
  PERFORM pgmq.create('ops_jobs');
EXCEPTION
  WHEN OTHERS THEN
    -- Queue may already exist
    NULL;
END $$;

-- =============================================================================
-- FUNCTIONS
-- =============================================================================

-- Enqueue a job for execution
CREATE OR REPLACE FUNCTION ops.enqueue_job(
  p_slug text,
  p_payload jsonb DEFAULT '{}'::jsonb,
  p_requested_by text DEFAULT NULL
)
RETURNS uuid
LANGUAGE plpgsql
AS $$
DECLARE
  v_job_id uuid;
  v_run_id uuid;
BEGIN
  -- Get job definition
  SELECT id INTO v_job_id
  FROM ops.jobs
  WHERE slug = p_slug AND enabled = true;

  IF v_job_id IS NULL THEN
    RAISE EXCEPTION 'Unknown or disabled job slug: %', p_slug;
  END IF;

  -- Create job run record
  INSERT INTO ops.job_runs(job_id, status, requested_by, payload)
  VALUES (v_job_id, 'queued', p_requested_by, p_payload)
  RETURNING id INTO v_run_id;

  -- Send message to queue
  PERFORM pgmq.send('ops_jobs', jsonb_build_object(
    'job_run_id', v_run_id,
    'job_slug', p_slug
  ));

  -- Log queued event
  INSERT INTO ops.job_events(job_run_id, event_type, message, data)
  VALUES (v_run_id, 'queued', format('Enqueued job %s', p_slug), p_payload);

  RETURN v_run_id;
END;
$$;

COMMENT ON FUNCTION ops.enqueue_job IS 'Enqueue a job for execution by the worker';

-- Dequeue jobs for processing (called by worker)
CREATE OR REPLACE FUNCTION ops.dequeue_jobs(p_limit int DEFAULT 10)
RETURNS TABLE(msg_id bigint, message jsonb)
LANGUAGE plpgsql
AS $$
BEGIN
  RETURN QUERY
  SELECT m.msg_id, m.message
  FROM pgmq.read('ops_jobs', p_limit, 60) m; -- 60s visibility timeout
END;
$$;

COMMENT ON FUNCTION ops.dequeue_jobs IS 'Dequeue jobs from the queue for processing';

-- Acknowledge (delete) a processed message
CREATE OR REPLACE FUNCTION ops.ack_job(p_msg_id bigint)
RETURNS boolean
LANGUAGE plpgsql
AS $$
BEGIN
  RETURN pgmq.delete('ops_jobs', p_msg_id);
END;
$$;

COMMENT ON FUNCTION ops.ack_job IS 'Acknowledge a job message after successful processing';

-- Mark job run as started
CREATE OR REPLACE FUNCTION ops.mark_run_started(p_run_id uuid)
RETURNS void
LANGUAGE plpgsql
AS $$
BEGIN
  UPDATE ops.job_runs
  SET status = 'running', started_at = now()
  WHERE id = p_run_id;

  INSERT INTO ops.job_events(job_run_id, event_type, message)
  VALUES (p_run_id, 'started', 'Job execution started');
END;
$$;

-- Mark job run as successful
CREATE OR REPLACE FUNCTION ops.mark_run_success(p_run_id uuid, p_result jsonb DEFAULT NULL)
RETURNS void
LANGUAGE plpgsql
AS $$
BEGIN
  UPDATE ops.job_runs
  SET status = 'success', finished_at = now(), result = p_result
  WHERE id = p_run_id;

  INSERT INTO ops.job_events(job_run_id, event_type, message, data)
  VALUES (p_run_id, 'done', 'Job completed successfully', p_result);
END;
$$;

-- Mark job run as failed
CREATE OR REPLACE FUNCTION ops.mark_run_error(p_run_id uuid, p_error text, p_data jsonb DEFAULT NULL)
RETURNS void
LANGUAGE plpgsql
AS $$
BEGIN
  UPDATE ops.job_runs
  SET status = 'error', finished_at = now(), error_message = p_error
  WHERE id = p_run_id;

  INSERT INTO ops.job_events(job_run_id, event_type, message, data)
  VALUES (p_run_id, 'error', p_error, p_data);
END;
$$;

-- Log an event during job execution
CREATE OR REPLACE FUNCTION ops.log_event(
  p_run_id uuid,
  p_event_type text,
  p_message text,
  p_data jsonb DEFAULT NULL
)
RETURNS bigint
LANGUAGE plpgsql
AS $$
DECLARE
  v_event_id bigint;
BEGIN
  INSERT INTO ops.job_events(job_run_id, event_type, message, data)
  VALUES (p_run_id, p_event_type, p_message, p_data)
  RETURNING id INTO v_event_id;

  RETURN v_event_id;
END;
$$;

COMMENT ON FUNCTION ops.log_event IS 'Log an event during job execution';

-- Record MCP tool invocation
CREATE OR REPLACE FUNCTION ops_mcp.record_tool_invocation(
  p_server_name text,
  p_tool_name text,
  p_duration_ms numeric,
  p_success boolean,
  p_description text DEFAULT NULL,
  p_input_schema jsonb DEFAULT NULL
)
RETURNS void
LANGUAGE plpgsql
AS $$
BEGIN
  INSERT INTO ops_mcp.tools (server_name, tool_name, description, input_schema, last_invoked_at, invocation_count, avg_duration_ms, error_rate)
  VALUES (p_server_name, p_tool_name, p_description, p_input_schema, now(), 1, p_duration_ms, CASE WHEN p_success THEN 0 ELSE 1 END)
  ON CONFLICT (server_name, tool_name) DO UPDATE SET
    last_invoked_at = now(),
    invocation_count = ops_mcp.tools.invocation_count + 1,
    avg_duration_ms = (ops_mcp.tools.avg_duration_ms * ops_mcp.tools.invocation_count + p_duration_ms) / (ops_mcp.tools.invocation_count + 1),
    error_rate = (ops_mcp.tools.error_rate * ops_mcp.tools.invocation_count + CASE WHEN p_success THEN 0 ELSE 1 END) / (ops_mcp.tools.invocation_count + 1),
    description = COALESCE(p_description, ops_mcp.tools.description),
    input_schema = COALESCE(p_input_schema, ops_mcp.tools.input_schema),
    updated_at = now();
END;
$$;

COMMENT ON FUNCTION ops_mcp.record_tool_invocation IS 'Record MCP tool invocation statistics';

-- =============================================================================
-- SEED DEFAULT JOBS
-- =============================================================================

INSERT INTO ops.jobs (slug, description, job_type, handler, schedule_cron) VALUES
  ('infra_scan_vercel', 'Scan Vercel projects, deployments, and domains', 'infra', 'infra_scan_vercel', '0 */6 * * *'),
  ('infra_scan_supabase', 'Scan Supabase schemas, tables, and Edge Functions', 'infra', 'infra_scan_supabase', '0 */6 * * *'),
  ('infra_scan_odoo', 'Scan Odoo modules and dependencies', 'infra', 'infra_scan_odoo', '0 */6 * * *'),
  ('infra_scan_digitalocean', 'Scan DigitalOcean droplets and databases', 'infra', 'infra_scan_digitalocean', '0 */6 * * *'),
  ('infra_scan_docker', 'Scan Docker containers, images, and networks', 'infra', 'infra_scan_docker', '0 */6 * * *'),
  ('infra_scan_github', 'Scan GitHub repos and workflows', 'infra', 'infra_scan_github', '0 */6 * * *'),
  ('mcp_introspect_tools', 'Introspect MCP server tools and capabilities', 'mcp', 'mcp_introspect_tools', '0 */12 * * *'),
  ('kg_generate_docs', 'Generate LLM-friendly documentation from KG', 'kg', 'kg_generate_docs', '0 4 * * *'),
  ('sync_odoo_shadow', 'Sync Odoo data to shadow tables', 'sync', 'sync_odoo_shadow', '*/30 * * * *')
ON CONFLICT (slug) DO NOTHING;

-- =============================================================================
-- CRON SCHEDULE
-- =============================================================================

-- Schedule worker invocation every 5 minutes
-- Note: The worker URL must be configured via app.settings
DO $$
BEGIN
  -- Check if cron job exists
  IF NOT EXISTS (SELECT 1 FROM cron.job WHERE jobname = 'ops_job_worker_5min') THEN
    PERFORM cron.schedule(
      'ops_job_worker_5min',
      '*/5 * * * *',
      $$SELECT pg_notify('ops_job_worker', '{"trigger": "cron"}')$$
    );
  END IF;
END $$;

-- =============================================================================
-- RLS POLICIES
-- =============================================================================

ALTER TABLE ops.jobs ENABLE ROW LEVEL SECURITY;
ALTER TABLE ops.job_runs ENABLE ROW LEVEL SECURITY;
ALTER TABLE ops.job_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE ops_mcp.tools ENABLE ROW LEVEL SECURITY;

-- Service role bypass
CREATE POLICY "service_role_all" ON ops.jobs FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY "service_role_all" ON ops.job_runs FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY "service_role_all" ON ops.job_events FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY "service_role_all" ON ops_mcp.tools FOR ALL TO service_role USING (true) WITH CHECK (true);

-- Authenticated users can read
CREATE POLICY "authenticated_read" ON ops.jobs FOR SELECT TO authenticated USING (true);
CREATE POLICY "authenticated_read" ON ops.job_runs FOR SELECT TO authenticated USING (true);
CREATE POLICY "authenticated_read" ON ops.job_events FOR SELECT TO authenticated USING (true);
CREATE POLICY "authenticated_read" ON ops_mcp.tools FOR SELECT TO authenticated USING (true);

-- =============================================================================
-- GRANTS
-- =============================================================================

GRANT USAGE ON SCHEMA ops TO authenticated, service_role;
GRANT USAGE ON SCHEMA ops_mcp TO authenticated, service_role;
GRANT ALL ON ALL TABLES IN SCHEMA ops TO service_role;
GRANT ALL ON ALL TABLES IN SCHEMA ops_mcp TO service_role;
GRANT SELECT ON ALL TABLES IN SCHEMA ops TO authenticated;
GRANT SELECT ON ALL TABLES IN SCHEMA ops_mcp TO authenticated;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA ops TO authenticated, service_role;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA ops_mcp TO authenticated, service_role;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA ops TO service_role;
