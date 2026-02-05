# Supabase Setup Guide for Ops Control Room

This guide will help you set up the Supabase database for the Ops Control Room application.

## Prerequisites

- A Supabase project created
- Access to the Supabase Dashboard SQL Editor
- Your Supabase project credentials configured in Figma Make

## Step 1: Run the Database Migration

1. Open your Supabase Dashboard
2. Navigate to **SQL Editor**
3. Click **New Query**
4. Copy the contents of `/supabase/migrations/20250103000000_ops_schema.sql`
5. Paste into the SQL Editor
6. Click **Run** to execute the migration

This will:
- Create the `ops` schema
- Create all necessary tables (`runs`, `run_events`, `artifacts`, `run_templates`, `spec_docs`)
- Set up indexes
- Configure Row Level Security (RLS) policies
- Enable realtime subscriptions
- Seed initial template data and spec kit documents

## Step 2: Verify the Schema

After running the migration, verify that the tables were created:

```sql
-- Check if tables exist
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'ops';
```

You should see:
- `runs`
- `run_events`
- `artifacts`
- `run_templates`
- `spec_docs`

## Step 3: Check Seed Data

Verify that the seed data was inserted:

```sql
-- Check templates
SELECT slug, title FROM ops.run_templates;

-- Check spec docs
SELECT slug, title FROM ops.spec_docs;
```

## Step 4: Configure API Settings

1. In Supabase Dashboard, go to **Settings** → **API**
2. Under **Schema**, ensure `ops` is listed in the **Exposed schemas**
3. If not, add `ops` to the exposed schemas list

## Step 5: Enable Realtime

1. Go to **Database** → **Replication**
2. Ensure the following tables have realtime enabled:
   - `ops.runs`
   - `ops.run_events`
   - `ops.artifacts`

## Step 6: Test Authentication (Optional but Recommended)

The current RLS policies allow authenticated users to access data. For prototyping without auth:

### Option A: Use Anonymous Access (Recommended for Prototyping)

Update the RLS policies to allow anonymous access:

```sql
-- Allow anon role to read spec docs
DROP POLICY IF EXISTS "spec_read" ON ops.spec_docs;
CREATE POLICY "spec_read" ON ops.spec_docs
  FOR SELECT TO anon, authenticated
  USING (true);

-- Allow anon role to update spec docs
DROP POLICY IF EXISTS "spec_update" ON ops.spec_docs;
CREATE POLICY "spec_update" ON ops.spec_docs
  FOR UPDATE TO anon, authenticated
  USING (true)
  WITH CHECK (true);

-- Allow anon role to read templates
DROP POLICY IF EXISTS "templates_read" ON ops.run_templates;
CREATE POLICY "templates_read" ON ops.run_templates
  FOR SELECT TO anon, authenticated
  USING (true);

-- Allow anon role to create runs
DROP POLICY IF EXISTS "runs_insert" ON ops.runs;
CREATE POLICY "runs_insert" ON ops.runs
  FOR INSERT TO anon, authenticated
  WITH CHECK (true);

-- Allow anon role to select runs
DROP POLICY IF EXISTS "runs_select_own" ON ops.runs;
CREATE POLICY "runs_select_own" ON ops.runs
  FOR SELECT TO anon, authenticated
  USING (true);

-- Allow anon role to update runs
DROP POLICY IF EXISTS "runs_update_own" ON ops.runs;
CREATE POLICY "runs_update_own" ON ops.runs
  FOR UPDATE TO anon, authenticated
  USING (true);

-- Allow anon role to read events
DROP POLICY IF EXISTS "events_select" ON ops.run_events;
CREATE POLICY "events_select" ON ops.run_events
  FOR SELECT TO anon, authenticated
  USING (true);

-- Allow anon role to read artifacts
DROP POLICY IF EXISTS "artifacts_select" ON ops.artifacts;
CREATE POLICY "artifacts_select" ON ops.artifacts
  FOR SELECT TO anon, authenticated
  USING (true);
```

### Option B: Set Up Authentication

If you want proper authentication:

1. Go to **Authentication** → **Providers**
2. Enable Email provider (or any OAuth provider)
3. Create a test user in **Authentication** → **Users**
4. Implement sign-in in the frontend (see auth example in `/src/lib/supabase.ts`)

## Step 7: Test the Connection

Run this query to verify everything is working:

```sql
-- Test query
SELECT 
  (SELECT count(*) FROM ops.run_templates) as template_count,
  (SELECT count(*) FROM ops.spec_docs) as spec_doc_count,
  (SELECT count(*) FROM ops.runs) as run_count;
```

## Common Issues

### Issue: "relation ops.spec_docs does not exist"
**Solution**: Run the migration SQL in Step 1.

### Issue: "permission denied for schema ops"
**Solution**: Ensure the `ops` schema is exposed in API settings (Step 4).

### Issue: "new row violates row-level security policy"
**Solution**: Either:
- Follow Option A to enable anonymous access
- Follow Option B to set up authentication

### Issue: "Failed to load spec docs"
**Solution**: 
1. Check that the migration was run successfully
2. Verify RLS policies allow access (use Option A for prototyping)
3. Check browser console for specific error messages

## Next Steps

Once the setup is complete, the Ops Control Room application should be able to:
- ✅ Load runbook templates
- ✅ View and edit Spec Kit documents
- ✅ Create and execute runs
- ✅ Stream realtime logs and artifacts

## Troubleshooting

If you're still having issues:

1. Check the browser console for error messages
2. Check the Supabase Dashboard → **API** → **Logs** for API errors
3. Verify your Supabase credentials in Figma Make are correct
4. Ensure you're using the latest migration file

For more help, refer to:
- [Supabase RLS Documentation](https://supabase.com/docs/guides/auth/row-level-security)
- [Supabase Realtime Documentation](https://supabase.com/docs/guides/realtime)
