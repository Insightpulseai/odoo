# 🚨 URGENT: Fix Database Errors - 2 Minute Guide

**Error:** `Could not find the table 'public.runs' in the schema cache`

**Cause:** Database tables don't exist yet

**Fix:** Run the migration (choose one method below)

---

## 🎯 Method 1: Copy-Paste SQL (Easiest - 2 minutes)

### Step 1: Copy the SQL File

Open this file and copy ALL of its contents:
```
/supabase/migrations/FULL_SETUP.sql
```

Or click here in VS Code: [FULL_SETUP.sql](./supabase/migrations/FULL_SETUP.sql)

### Step 2: Paste into Supabase

1. Go to https://supabase.com/dashboard
2. Select your project
3. Click **SQL Editor** (left sidebar)
4. Click **New query**
5. Paste the copied SQL
6. Click **Run** (bottom right, green button)

### Step 3: Wait for Success

You should see:
```
✅ Ops Control Room database setup complete!
📋 Created 7 tables
🔒 Enabled RLS policies
⚡ Configured realtime publication
🛠️ Created 5 helper functions
```

### Step 4: Enable Realtime

1. In Supabase Dashboard, go to **Database** → **Replication**
2. Find "supabase_realtime" publication
3. Make sure it's enabled (green toggle)
4. Verify these tables are in the publication:
   - sessions
   - runs
   - run_events
   - artifacts
   - run_steps

### Step 5: Refresh Your App

Go back to your Figma Make app and refresh the page (Cmd/Ctrl + R).

**✅ Errors should be gone!**

---

## 🎯 Method 2: Supabase CLI (If you have it installed)

```bash
# 1. Link to your project (one time)
supabase link --project-ref YOUR_PROJECT_REF

# 2. Push all migrations
supabase db push

# 3. Verify
supabase db diff
```

Get your project ref from the Supabase dashboard URL:
`https://supabase.com/dashboard/project/{YOUR_PROJECT_REF}`

---

## 🔍 Verify It Worked

### Quick Test Query

Run this in SQL Editor:

```sql
SELECT 
  'sessions' as table_name, 
  count(*) as row_count 
FROM public.sessions
UNION ALL
SELECT 'runs', count(*) FROM public.runs
UNION ALL
SELECT 'run_events', count(*) FROM public.run_events
UNION ALL
SELECT 'artifacts', count(*) FROM public.artifacts
UNION ALL
SELECT 'run_templates', count(*) FROM public.run_templates
UNION ALL
SELECT 'spec_docs', count(*) FROM public.spec_docs
UNION ALL
SELECT 'run_steps', count(*) FROM public.run_steps;
```

**Expected:** 7 rows showing table names with `0` count each.

---

## 🆘 Troubleshooting

### Still seeing errors after migration?

1. **Check your `.env` file:**
   ```bash
   # Should have these (with your actual values):
   VITE_SUPABASE_URL=https://YOUR_PROJECT.supabase.co
   VITE_SUPABASE_ANON_KEY=eyJhbGc...
   ```

2. **Verify tables exist:**
   - Go to Supabase Dashboard → Database → Tables
   - You should see 7 tables under "public" schema

3. **Check realtime is enabled:**
   - Supabase Dashboard → Database → Replication
   - "supabase_realtime" should be ON

4. **Clear browser cache:**
   - Hard refresh: Cmd+Shift+R (Mac) or Ctrl+Shift+R (Windows)

5. **Still stuck?**
   - Check browser console for detailed errors
   - See [MIGRATION_SETUP.md](./MIGRATION_SETUP.md) for more troubleshooting

---

## 📚 What This Migration Does

Creates:
- ✅ **7 tables:** sessions, runs, run_events, artifacts, run_templates, spec_docs, run_steps
- ✅ **Indexes:** For fast queries
- ✅ **RLS policies:** For security (anon can read/write during prototyping)
- ✅ **Realtime:** For live log streaming
- ✅ **Functions:** claim_runs(), heartbeat_run(), cancel_run(), etc.

---

## ✅ After Migration Success

Your app can now:
- ✅ Create sessions
- ✅ Run tasks in lanes A/B/C/D
- ✅ Stream logs in real-time
- ✅ Store artifacts
- ✅ Use templates

---

## 🎉 Quick Start After Setup

1. Open your app
2. Click **Runboard** tab
3. Click **New Session**
4. Enter intent: "Test parallel execution"
5. Click **Create**
6. Type something in lane A
7. Click **Run**
8. Watch logs stream! ⚡

---

**Need more help?** See [MIGRATION_SETUP.md](./MIGRATION_SETUP.md) for detailed guide.
