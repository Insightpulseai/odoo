# 🚀 Quick Fix Guide - Database Errors

**Issue:** `Could not find the table 'public.runs' in the schema cache`

**Solution:** ✅ Automated setup wizard built into the app!

---

## How to Fix (2 minutes)

### Option 1: Use the In-App Wizard (Recommended) ⭐

1. **Refresh your app** - The setup wizard should appear automatically
2. **Follow the 3 steps:**
   - Step 1: Click "Copy Setup SQL"
   - Step 2: Click "Open SQL Editor" → Paste → Run
   - Step 3: (Optional) Enable realtime
3. **Click "Refresh App"**
4. **Done!** ✅

---

### Option 2: Manual Setup (If wizard doesn't appear)

1. **Open Supabase Dashboard**
   - Go to https://supabase.com/dashboard
   - Select your project: `svqwvuuhjzxciapxybcv`

2. **Open SQL Editor**
   - Click "SQL Editor" in left sidebar
   - Click "New query"

3. **Copy & Run SQL**
   - Open `/supabase/migrations/FULL_SETUP.sql`
   - Copy all contents
   - Paste into SQL Editor
   - Click "Run"

4. **Enable Realtime** (Optional)
   - Go to Database → Replication
   - Toggle on "supabase_realtime"

5. **Refresh your app**

---

## What Gets Created

- ✅ 7 tables (sessions, runs, run_events, artifacts, run_templates, spec_docs, run_steps)
- ✅ Row Level Security policies
- ✅ 5 helper functions
- ✅ Performance indexes
- ✅ Realtime publication

---

## Verification

Run this in SQL Editor to check:

```sql
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
  AND table_name IN (
    'sessions', 'runs', 'run_events', 
    'artifacts', 'run_templates', 
    'spec_docs', 'run_steps'
  );
```

**Expected:** 7 rows

---

## Still Getting Errors?

### 1. Wrong Supabase Project
- Check if `VITE_SUPABASE_URL` matches your project
- Should be: `https://svqwvuuhjzxciapxybcv.supabase.co`

### 2. SQL Didn't Run
- Check SQL Editor for error messages
- Look for red error text after clicking "Run"
- If error, share the error message

### 3. Tables in Wrong Schema
- Make sure using `public` schema (not `ops`)
- Run: `SELECT * FROM information_schema.tables WHERE table_name = 'runs'`

### 4. Cache Issue
- Hard refresh: Cmd/Ctrl + Shift + R
- Or clear browser cache

---

## Files Reference

- **Setup Wizard UI:** `/src/app/components/DatabaseSetup.tsx`
- **Main App Logic:** `/src/app/App.tsx`
- **SQL Script:** `/supabase/migrations/FULL_SETUP.sql`
- **Detailed Guide:** `/DATABASE_SETUP_FIXED.md`

---

## Need Help?

Check the console (F12 → Console tab) for detailed error messages.

Common errors:
- `PGRST205` = Table doesn't exist → Run setup SQL
- `PGRST301` = RLS blocking → Check policies
- `Connection refused` = Wrong URL → Check credentials

---

**The fix is automatic! Just refresh your app.** 🎉
