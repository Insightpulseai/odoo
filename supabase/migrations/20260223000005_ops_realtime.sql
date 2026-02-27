-- supabase/migrations/20260223000005_ops_realtime.sql

-- Enable Realtime broadcase/presence and DB changes
-- The ops console relies on real-time signals from sync_queue and kb_chunks

begin;

-- Publication config for DB changes
create publication supabase_realtime for table
  public.sync_queue,
  public.kb_chunks;

commit;

-- For broadcase/presence, the `realtime` schema is generally managed by Supabase
-- implicitly, but we ensure DB changes are published here.
