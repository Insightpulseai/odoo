-- ===========================================================================
-- OPS RLS HARDENING: Row-Level Security policies
-- Default deny for anon/authenticated; service role bypasses
-- ===========================================================================

-- Enable RLS on all ops tables
alter table ops.runtime_identifiers enable row level security;
alter table ops.deployments enable row level security;
alter table ops.incidents enable row level security;
alter table ops.artifact_index enable row level security;
alter table ops.run_events enable row level security;
alter table ops.ingest_dedupe enable row level security;
alter table ops.ingest_dlq enable row level security;

-- Enable RLS on audit tables
alter table audit.events enable row level security;

-- Enable RLS on mirror tables
alter table mirror.odoo_object_snapshots enable row level security;

-- ---------------------------------------------------------------------------
-- Default: no policies = deny for anon/authenticated.
-- Service role bypasses RLS automatically.
--
-- Add specific policies only if you need anon/authenticated access.
-- For this SSOT pattern, all access is via Edge Functions with service role.
-- ---------------------------------------------------------------------------

-- Optional: read-only policy for authenticated users on ops views
-- Uncomment if needed:
--
-- create policy "authenticated_read_deployments"
--   on ops.deployments for select
--   to authenticated
--   using (true);
--
-- create policy "authenticated_read_incidents"
--   on ops.incidents for select
--   to authenticated
--   using (true);
