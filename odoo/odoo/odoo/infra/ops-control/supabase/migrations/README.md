# Supabase Migrations

This folder contains database migrations for the Ops Control Room.

## Deployed Migrations

- `20250103000000_ops_schema.sql` - Initial ops schema with tables, RLS policies, and helper functions

## How Migrations Work in Figma Make

When you click **Deploy** in Figma Make:
1. It detects the `/supabase/migrations/` folder
2. Applies any new migrations to your connected Supabase project
3. Deploys Edge Functions from `/supabase/functions/`

## Manual Migration (Alternative)

If you prefer to apply migrations manually via Supabase dashboard:
1. Go to your Supabase project
2. Navigate to **SQL Editor**
3. Copy the contents of `20250103000000_ops_schema.sql`
4. Paste and click **Run**

## What Gets Created

### Tables
- `ops.runs` - Runbook execution queue
- `ops.run_events` - Real-time log entries
- `ops.artifacts` - Generated outputs (links, diffs, files)

### Functions
- `ops.enqueue_run()` - Create a new run
- `ops.claim_run()` - Atomic claim for executor
- `ops.complete_run()` - Mark run as complete

### Security
- Row Level Security (RLS) enabled on all tables
- Users can only see their own runs
- Only service_role (Edge Function) can write events

### Realtime
- All tables published for real-time subscriptions
- UI automatically receives log updates
