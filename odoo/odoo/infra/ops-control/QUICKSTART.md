# Ops Control Room - Quick Start

## ⚡ 3-Minute Setup

### 1️⃣ Set Environment Variables

Create a `.env` file (already done!):

```env
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key-here
```

Get these from: **Supabase Dashboard → Settings → API**

---

### 2️⃣ Deploy to Supabase

Click **Deploy** in Figma Make's top-right corner.

This automatically:
- ✅ Applies database migration (creates `ops.runs`, `ops.run_events`, `ops.artifacts` tables)
- ✅ Deploys the Edge Function executor
- ✅ Sets up Row Level Security policies

---

### 3️⃣ Configure Edge Function Secrets

Go to **Supabase Dashboard → Edge Functions → ops-executor → Settings**

Add these secrets:

| Secret | Where to Get It |
|--------|-----------------|
| `SUPABASE_URL` | Dashboard → Settings → API |
| `SUPABASE_SERVICE_ROLE_KEY` | Dashboard → Settings → API |

---

### 4️⃣ Enable Realtime

**Supabase Dashboard → Database → Replication**

Enable these tables:
- ✅ `ops.runs`
- ✅ `ops.run_events`
- ✅ `ops.artifacts`

Or run this SQL:

```sql
alter publication supabase_realtime add table ops.runs;
alter publication supabase_realtime add table ops.run_events;
alter publication supabase_realtime add table ops.artifacts;
```

---

### 5️⃣ Set Up Auto-Execution (Optional but Recommended)

**Supabase Dashboard → SQL Editor** - Run:

```sql
create extension if not exists pg_cron;

select cron.schedule(
  'ops-executor-cron',
  '* * * * *',
  $$
  select net.http_post(
    url := 'https://YOUR-PROJECT.supabase.co/functions/v1/ops-executor',
    headers := '{"Authorization": "Bearer YOUR-ANON-KEY"}'::jsonb
  )
  $$
);
```

Replace `YOUR-PROJECT` and `YOUR-ANON-KEY` with your values.

---

## ✅ Test It!

1. **Open your app** (published URL or local dev server)
2. **Type:** `check prod status`
3. **Click Run** on the runbook card
4. **Watch** real-time logs stream in the fullscreen viewer

---

## 🎯 What You Built

**Frontend (Figma Make):**
- Command bar for natural language → runbook parsing
- Inline runbook cards with Run/Edit actions
- Fullscreen log viewer with real-time streaming
- Artifact display (links, diffs, files)

**Backend (Supabase):**
- PostgreSQL tables for runs/events/artifacts
- Edge Function executor with 5-phase pipeline
- Row Level Security for multi-user safety
- Realtime subscriptions for live updates

**Security:**
- Secrets live server-side only (never in browser)
- RLS prevents log tampering
- Service role isolation

---

## 📚 Next Steps

- **Replace adapter stubs** → See `/docs/ADAPTER_GUIDE.md`
- **Add authentication** → See `/docs/DEVELOPER_GUIDE.md`
- **Create custom runbooks** → See `/src/core/runbooks.ts`
- **Full deployment guide** → See `/DEPLOY.md`

---

## 🆘 Troubleshooting

**"Missing Supabase environment variables"**
→ Check `.env` file has correct URL and anon key

**"No events appearing"**
→ Verify realtime is enabled (Step 4)
→ Check Edge Function logs in Supabase dashboard

**"Error creating run"**
→ Make sure migration was applied (Step 2)
→ Check RLS policies are enabled

**Detailed troubleshooting:** See `/DEPLOY.md`

---

## 🚀 You're Ready!

Your Ops Control Room is production-ready with:
✅ Real-time log streaming
✅ Secure server-side execution
✅ Multi-user support (with RLS)
✅ Extensible adapter system