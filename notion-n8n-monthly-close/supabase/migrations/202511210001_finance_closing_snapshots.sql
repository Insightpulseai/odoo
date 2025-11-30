-- Finance Closing Snapshots Table
-- Purpose: Store nightly closing state snapshots from Odoo via n8n W101 workflow
-- Triggered by: n8n workflow (11 PM PHT daily) → Supabase Edge Function

CREATE TABLE IF NOT EXISTS finance_closing_snapshots (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  captured_at timestamptz NOT NULL DEFAULT now(),
  source text NOT NULL DEFAULT 'n8n',
  odoo_db text NOT NULL,
  period_label text NOT NULL,
  total_tasks int NOT NULL,
  open_tasks int NOT NULL,
  blocked_tasks int NOT NULL,
  done_tasks int NOT NULL,
  cluster_a_open int NOT NULL DEFAULT 0,
  cluster_b_open int NOT NULL DEFAULT 0,
  cluster_c_open int NOT NULL DEFAULT 0,
  cluster_d_open int NOT NULL DEFAULT 0,
  raw_payload jsonb NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);

-- Indexes for common queries
CREATE INDEX IF NOT EXISTS idx_finance_closing_snapshots_period
  ON finance_closing_snapshots (period_label, captured_at DESC);

CREATE INDEX IF NOT EXISTS idx_finance_closing_snapshots_source
  ON finance_closing_snapshots (source, captured_at DESC);

-- Row Level Security (RLS)
ALTER TABLE finance_closing_snapshots ENABLE ROW LEVEL SECURITY;

-- Policy: Allow service role full access
CREATE POLICY "Allow service role full access"
  ON finance_closing_snapshots
  FOR ALL
  USING (auth.role() = 'service_role');

-- Policy: Allow authenticated read access
CREATE POLICY "Allow authenticated read access"
  ON finance_closing_snapshots
  FOR SELECT
  USING (auth.role() = 'authenticated');

-- Comments for documentation
COMMENT ON TABLE finance_closing_snapshots IS 'Nightly snapshots of Odoo monthly closing state for historical analysis and dashboard visualization';
COMMENT ON COLUMN finance_closing_snapshots.captured_at IS 'Timestamp when snapshot was captured (PHT)';
COMMENT ON COLUMN finance_closing_snapshots.source IS 'Source of snapshot: n8n, manual, or pg_cron';
COMMENT ON COLUMN finance_closing_snapshots.odoo_db IS 'Odoo database name (production, staging, dev)';
COMMENT ON COLUMN finance_closing_snapshots.period_label IS 'Closing period identifier (YYYY-MM format)';
COMMENT ON COLUMN finance_closing_snapshots.total_tasks IS 'Total closing tasks for period';
COMMENT ON COLUMN finance_closing_snapshots.open_tasks IS 'Tasks in Not Started or In Progress stage';
COMMENT ON COLUMN finance_closing_snapshots.blocked_tasks IS 'Tasks in Blocked stage requiring attention';
COMMENT ON COLUMN finance_closing_snapshots.done_tasks IS 'Tasks in Done or Posted stage';
COMMENT ON COLUMN finance_closing_snapshots.cluster_a_open IS 'Open tasks for cluster A';
COMMENT ON COLUMN finance_closing_snapshots.cluster_b_open IS 'Open tasks for cluster B';
COMMENT ON COLUMN finance_closing_snapshots.cluster_c_open IS 'Open tasks for cluster C';
COMMENT ON COLUMN finance_closing_snapshots.cluster_d_open IS 'Open tasks for cluster D';
COMMENT ON COLUMN finance_closing_snapshots.raw_payload IS 'Full JSON payload from n8n including all metrics and metadata';
