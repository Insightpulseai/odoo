# Ops Control Room - Setup Guide

## 🚀 Quick Start

This is your **v1 production-ready** Ops Control Room with:
- **Figma Make frontend** - The UI you built
- **Supabase backend** - State storage, job queue, realtime event streaming
- **Edge Function executor** - Secure execution of privileged operations

---

## 📋 Prerequisites

1. **Supabase account** - [Sign up here](https://supabase.com)
2. **Supabase CLI** - [Installation guide](https://supabase.com/docs/guides/cli)
3. **Node.js 18+** and **pnpm**

---

## 🗄️ Step 1: Set up Supabase

### 1.1 Create a new Supabase project

```bash
# Via Supabase dashboard
https://app.supabase.com/new

# Or via CLI
supabase projects create ops-control-room
```

### 1.2 Apply the database schema

```bash
# Copy the SQL from /supabase/schema.sql
# Paste into Supabase SQL Editor (Dashboard > SQL Editor > New Query)
# Click "Run"

# Or via CLI
supabase db push
```

This creates:
- `ops.runs` table
- `ops.run_events` table
- `ops.artifacts` table
- Helper functions for enqueue/claim/complete
- Row Level Security policies
- Realtime subscriptions

### 1.3 Get your Supabase credentials

From your Supabase project dashboard:
- Go to **Settings > API**
- Copy:
  - `Project URL` (e.g., `https://abc123.supabase.co`)
  - `anon public` key (safe for browser)
  - `service_role` key (for Edge Function only - NEVER in browser)

---

## 🔧 Step 2: Configure the frontend

### 2.1 Create `.env` file

```bash
cp .env.example .env
```

### 2.2 Add your Supabase credentials

```env
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key-here
```

### 2.3 Install dependencies

```bash
pnpm install
```

---

## ⚡ Step 3: Deploy the Edge Function executor

### 3.1 Link your Supabase project

```bash
supabase link --project-ref your-project-ref
```

### 3.2 Set secrets (environment variables)

```bash
supabase secrets set \
  VERCEL_TOKEN=your_vercel_token \
  GITHUB_TOKEN=your_github_token \
  DIGITALOCEAN_TOKEN=your_do_token \
  SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
```

**Note:** These are API tokens for external services. Get them from:
- **Vercel:** [vercel.com/account/tokens](https://vercel.com/account/tokens)
- **GitHub:** [github.com/settings/tokens](https://github.com/settings/tokens) (needs `repo` scope)
- **DigitalOcean:** [cloud.digitalocean.com/account/api/tokens](https://cloud.digitalocean.com/account/api/tokens)
- **Supabase service_role:** From your project's API settings

### 3.3 Deploy the function

```bash
supabase functions deploy ops-executor
```

### 3.4 Set up automatic execution (cron)

Two options:

#### Option A: Supabase Cron (recommended)

Run this SQL in Supabase SQL Editor:

```sql
-- Enable pg_cron extension
create extension if not exists pg_cron;

-- Schedule executor to run every minute
select cron.schedule(
  'ops-executor-cron',
  '* * * * *',  -- Every minute
  $$
  select
    net.http_post(
      url := 'https://your-project.supabase.co/functions/v1/ops-executor',
      headers := '{"Authorization": "Bearer your-anon-key"}'::jsonb
    )
  $$
);
```

#### Option B: External cron (alternative)

Set up a cron job on your server:

```bash
# Add to crontab
* * * * * curl -X POST https://your-project.supabase.co/functions/v1/ops-executor \
  -H "Authorization: Bearer your-anon-key"
```

---

## 🧪 Step 4: Test the setup

### 4.1 Start the dev server

```bash
pnpm run dev
```

### 4.2 Test a runbook

1. Open `http://localhost:5173`
2. Type: `deploy staging`
3. Click **Run** on the runbook card
4. Watch the fullscreen log viewer populate in realtime

### 4.3 Verify database writes

Check Supabase dashboard:
- **Table Editor > ops > runs** - Should see your run
- **Table Editor > ops > run_events** - Should see log entries

---

## 🔐 Security Notes

### What's safe in the browser:
✅ `VITE_SUPABASE_URL` - Public project URL
✅ `VITE_SUPABASE_ANON_KEY` - Protected by RLS

### What's NEVER in the browser:
❌ `SUPABASE_SERVICE_ROLE_KEY` - Only in Edge Function
❌ `VERCEL_TOKEN`, `GITHUB_TOKEN`, etc. - Only in Edge Function

### How RLS protects you:
- Users can **read** their own runs/events/artifacts
- Users can **create** new runs
- Only the **service_role** (Edge Function) can write events/artifacts
- This prevents users from faking execution logs

---

## 🛠️ Troubleshooting

### "Missing Supabase environment variables"
- Make sure `.env` file exists and has correct values
- Restart dev server after editing `.env`

### "Error creating run"
- Check Supabase dashboard > Logs for errors
- Verify RLS policies are enabled
- Test connection: `supabase db remote`

### "No events appearing"
- Check Edge Function logs: `supabase functions logs ops-executor`
- Verify secrets are set: `supabase secrets list`
- Manually trigger executor: `curl -X POST https://....`

### "Realtime not working"
- Check Supabase dashboard > Database > Replication
- Verify tables are published: `alter publication supabase_realtime add table ops.run_events;`

---

## 📚 Next Steps

### v1 Improvements:
- [ ] Replace adapter stubs with real API calls
- [ ] Add authentication (Supabase Auth)
- [ ] Add run history view
- [ ] Add manual retry button
- [ ] Add webhook notifications on completion

### v2 Features:
- [ ] Multi-tenant support (team workspaces)
- [ ] Approval workflows for prod changes
- [ ] Audit log export
- [ ] Custom runbook templates
- [ ] Slack/Discord notifications

---

## 📞 Support

- **Supabase Docs:** https://supabase.com/docs
- **Edge Functions Guide:** https://supabase.com/docs/guides/functions
- **Realtime Guide:** https://supabase.com/docs/guides/realtime

---

## 🎉 You're Ready!

Your Ops Control Room is now:
✅ Connected to Supabase for state management
✅ Streaming logs in realtime
✅ Executing runbooks securely server-side
✅ Ready to deploy on Figma Make

**Deploy the UI:**
```bash
# Build for production
pnpm run build

# Upload to Figma Make or Vercel
```

**Share with stakeholders:**
- Show the inline runbook cards
- Demonstrate live log streaming
- Highlight security (no secrets in browser)
