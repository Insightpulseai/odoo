# ✅ Database Error Fix - Summary

**Date:** January 7, 2026  
**Issue:** Database tables not found errors  
**Status:** ✅ Fixed - Migration files created

---

## 🎯 What Was Wrong

Your Figma Make app is trying to query database tables that don't exist yet:
- `public.runs`
- `public.run_templates`
- `public.run_events`
- `public.artifacts`
- `public.sessions`
- `public.spec_docs`
- `public.run_steps`

These tables need to be created by running a database migration.

---

## 📁 Solution Files Created

I've created **3 helpful files** to fix this:

### 1. [FIX_DATABASE_ERRORS.md](./FIX_DATABASE_ERRORS.md) ⭐ **Start Here**
- **2-minute quick fix guide**
- Step-by-step instructions with screenshots references
- Troubleshooting tips
- Verification queries

### 2. [supabase/migrations/FULL_SETUP.sql](./supabase/migrations/FULL_SETUP.sql) ⭐ **The SQL File**
- **Complete database setup in one file**
- Creates all 7 tables
- Sets up indexes, RLS policies, realtime
- Creates helper functions
- Includes verification queries
- **This is what you'll copy and paste!**

### 3. [MIGRATION_SETUP.md](./MIGRATION_SETUP.md)
- **Detailed troubleshooting guide**
- Multiple methods (CLI, Dashboard, Manual)
- Step-by-step table creation commands
- Common errors and fixes

---

## 🚀 Quick Fix (2 Minutes)

### Option A: Copy-Paste (Easiest)

1. **Open** `/supabase/migrations/FULL_SETUP.sql`
2. **Copy** all contents (Cmd/Ctrl + A, then Cmd/Ctrl + C)
3. **Go to** https://supabase.com/dashboard
4. **Select** your project
5. **Click** SQL Editor (left sidebar)
6. **Click** "New query"
7. **Paste** the SQL
8. **Click** "Run" (bottom right, green button)
9. **Wait** for success message
10. **Enable** Realtime:
    - Go to Database → Replication
    - Toggle on "supabase_realtime" publication
11. **Refresh** your Figma Make app

✅ **Done!** Errors should be gone.

### Option B: Supabase CLI

```bash
# If you have Supabase CLI installed
supabase link --project-ref YOUR_PROJECT_REF
supabase db push
```

---

## 🔍 How to Verify It Worked

### Test Query

Run this in Supabase SQL Editor:

```sql
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
  AND table_name IN (
    'sessions',
    'runs',
    'run_events',
    'artifacts',
    'run_templates',
    'spec_docs',
    'run_steps'
  )
ORDER BY table_name;
```

**Expected Result:** 7 rows showing all table names

### Check Row Counts

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

**Expected Result:** 7 rows with `0` count (or more if you have data)

---

## 📋 What the Migration Creates

### Tables (7 total)
1. **sessions** - Groups of related runs
2. **runs** - Individual execution tasks
3. **run_events** - Real-time log entries
4. **artifacts** - Generated outputs (links, files, diffs)
5. **run_templates** - Reusable runbook templates
6. **spec_docs** - Spec Kit documentation
7. **run_steps** - Granular step tracking

### Security
- ✅ Row Level Security (RLS) enabled on all tables
- ✅ Policies for anon access (prototyping mode)
- ✅ Service role can bypass RLS (for edge function)

### Realtime
- ✅ Publication created: `supabase_realtime`
- ✅ Tables added to publication for live updates
- ✅ WebSocket streaming enabled

### Functions (5 total)
1. **claim_runs()** - Atomic run claiming (SKIP LOCKED)
2. **heartbeat_run()** - Worker health tracking
3. **cancel_run()** - Cancel running tasks
4. **enqueue_run()** - Create new runs
5. **complete_run()** - Mark runs as done

### Indexes
- ✅ Performance indexes on frequently queried columns
- ✅ Unique constraints where needed
- ✅ Foreign key relationships

---

## 🎉 After Setup - What You Can Do

Once the migration runs successfully, your app will:

✅ **Load without errors** - No more "table not found"
✅ **Create sessions** - Group related tasks
✅ **Run in parallel lanes** - Execute A/B/C/D simultaneously
✅ **Stream logs in real-time** - See events as they happen
✅ **Store artifacts** - Keep generated outputs
✅ **Use templates** - Reusable runbook patterns

### Try It Out

1. Open your app
2. Click **Runboard** tab
3. Click **New Session**
4. Enter: "Test parallel execution"
5. Click **Create**
6. Type something in lane A input
7. Click **Run**
8. **Watch logs stream!** ⚡

---

## 🆘 Still Getting Errors?

### Common Issues

**1. Wrong Supabase credentials**
- Check `.env` file
- Verify `VITE_SUPABASE_URL` matches your project
- Verify `VITE_SUPABASE_ANON_KEY` is correct

**2. Realtime not enabled**
- Go to Supabase Dashboard → Database → Replication
- Make sure "supabase_realtime" is ON (green toggle)

**3. Tables in wrong schema**
- All tables should be in `public` schema (not `ops`)
- Check with: `SELECT * FROM information_schema.tables WHERE table_schema = 'public'`

**4. RLS blocking queries**
- Make sure policies exist for anon role
- Check with: `SELECT * FROM pg_policies WHERE schemaname = 'public'`

### Get More Help

- **Quick guide:** [FIX_DATABASE_ERRORS.md](./FIX_DATABASE_ERRORS.md)
- **Detailed guide:** [MIGRATION_SETUP.md](./MIGRATION_SETUP.md)
- **Full plan:** [PHASED_IMPLEMENTATION_PLAN.md](./PHASED_IMPLEMENTATION_PLAN.md)

---

## 📊 Before vs After

### Before Migration
```
❌ Error: Could not find the table 'public.runs'
❌ Error: Could not find the table 'public.run_templates'
❌ App shows "No data" everywhere
❌ Can't create sessions or runs
❌ Real-time logs don't work
```

### After Migration
```
✅ All tables exist in public schema
✅ App loads without errors
✅ Can create sessions and runs
✅ Real-time logs stream perfectly
✅ Runboard shows lanes A/B/C/D
✅ Ready to start building!
```

---

## 🚀 Next Steps After Fix

Once your database is set up:

1. **Explore the UI**
   - Try all tabs: Chat, Templates, Runs, Spec Kit, Runboard
   - Create a test session
   - Run something in each lane

2. **Read the roadmap**
   - [PHASED_IMPLEMENTATION_PLAN.md](./PHASED_IMPLEMENTATION_PLAN.md) - Where we're going
   - [NEXT_STEPS.md](./NEXT_STEPS.md) - What to do next
   - [QUICK_REFERENCE.md](./QUICK_REFERENCE.md) - Cheat sheet

3. **Start building**
   - Pick a task from Phase 0 (see NEXT_STEPS.md)
   - Session archiving, run filtering, error recovery
   - Then move to Phase 1 (Pulser IR types)

---

## ✅ Summary Checklist

- [ ] Opened `/supabase/migrations/FULL_SETUP.sql`
- [ ] Copied all contents
- [ ] Pasted into Supabase SQL Editor
- [ ] Clicked "Run"
- [ ] Saw success message (7 tables created)
- [ ] Enabled realtime publication
- [ ] Refreshed Figma Make app
- [ ] Verified no errors in console
- [ ] Created test session in Runboard
- [ ] Ran test task in lane A
- [ ] Saw logs streaming in real-time

**All checked?** 🎉 **You're ready to build!**

---

**Questions?** Check [FIX_DATABASE_ERRORS.md](./FIX_DATABASE_ERRORS.md) or [MIGRATION_SETUP.md](./MIGRATION_SETUP.md)
