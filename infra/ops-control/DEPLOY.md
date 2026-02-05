# 🚀 Deployment Guide - Ops Control Room

## Quick Deploy Checklist

- [ ] 1. Set up Supabase environment variables in `.env`
- [ ] 2. Click **Deploy** in Figma Make
- [ ] 3. Set Edge Function secrets in Supabase dashboard
- [ ] 4. Enable realtime replication
- [ ] 5. Test with a sample runbook

---

## Step 1: Environment Variables

You should have already created `.env` with:

```env
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key-here
```

Get these values from: **Supabase Dashboard → Settings → API**

---

## Step 2: Deploy via Figma Make

### 2.1 Click the Deploy Button

In Figma Make, click **Deploy** in the top-right corner.

This will:
✅ Apply the database migration (`20250103000000_ops_schema.sql`)
✅ Deploy the Edge Function (`ops-executor`)
✅ Create necessary database tables and functions

### 2.2 What Gets Deployed

**Database Schema:**
- `ops.runs` table (execution queue)
- `ops.run_events` table (real-time logs)
- `ops.artifacts` table (generated outputs)
- Helper functions for enqueue/claim/complete
- Row Level Security policies

**Edge Function:**
- `ops-executor` - Server-side runbook executor
- 5-phase pipeline (validate → preflight → action → verify → summarize)
- Adapter stubs for Vercel, GitHub, DigitalOcean, Supabase

---

## Step 3: Configure Edge Function Secrets

After deployment, set environment variables for the Edge Function:

### 3.1 Via Supabase Dashboard

1. Go to **Edge Functions → ops-executor → Settings**
2. Add these secrets:

| Secret Name | Description | Where to Get It |
|------------|-------------|-----------------|
| `SUPABASE_URL` | Your project URL | Dashboard → Settings → API |
| `SUPABASE_SERVICE_ROLE_KEY` | Service role key | Dashboard → Settings → API (⚠️ NEVER expose in browser) |
| `VERCEL_TOKEN` | Vercel API token (optional) | [vercel.com/account/tokens](https://vercel.com/account/tokens) |
| `GITHUB_TOKEN` | GitHub PAT (optional) | [github.com/settings/tokens](https://github.com/settings/tokens) |
| `DIGITALOCEAN_TOKEN` | DO API token (optional) | [cloud.digitalocean.com/account/api](https://cloud.digitalocean.com/account/api/tokens) |

### 3.2 Via Supabase CLI (Alternative)

```bash
supabase secrets set \
  SUPABASE_URL="https://your-project.supabase.co" \
  SUPABASE_SERVICE_ROLE_KEY="your-service-role-key" \
  VERCEL_TOKEN="your-vercel-token" \
  GITHUB_TOKEN="your-github-token" \
  DIGITALOCEAN_TOKEN="your-do-token"
```

---

## Step 4: Enable Realtime Replication

### 4.1 Via Supabase Dashboard

1. Go to **Database → Replication**
2. Find these tables and enable replication:
   - ✅ `ops.runs`
   - ✅ `ops.run_events`
   - ✅ `ops.artifacts`

3. Click **Save**

### 4.2 Via SQL (Alternative)

Run this in **SQL Editor**:

```sql
alter publication supabase_realtime add table ops.runs;
alter publication supabase_realtime add table ops.run_events;
alter publication supabase_realtime add table ops.artifacts;
```

---

## Step 5: Set Up Automatic Execution

The Edge Function needs to be triggered periodically to check for queued runs.

### Option A: Supabase Cron (Recommended)

Run this in **SQL Editor**:

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
      url := 'https://YOUR-PROJECT-REF.supabase.co/functions/v1/ops-executor',
      headers := '{"Authorization": "Bearer YOUR-ANON-KEY"}'::jsonb
    )
  $$
);
```

**Replace:**
- `YOUR-PROJECT-REF` with your project reference (e.g., `abcdefg`)
- `YOUR-ANON-KEY` with your anon key from Settings → API

### Option B: External Cron

Set up a cron job on your server or use a service like [cron-job.org](https://cron-job.org):

```bash
* * * * * curl -X POST https://YOUR-PROJECT-REF.supabase.co/functions/v1/ops-executor \
  -H "Authorization: Bearer YOUR-ANON-KEY"
```

### Option C: Manual Trigger (Testing)

For testing, you can manually trigger execution:

```bash
curl -X POST https://YOUR-PROJECT-REF.supabase.co/functions/v1/ops-executor \
  -H "Authorization: Bearer YOUR-ANON-KEY"
```

---

## Step 6: Test the Deployment

### 6.1 Open Your App

Visit your Figma Make published URL or run locally:

```bash
npm run dev
# or
pnpm run dev
```

### 6.2 Create a Test Run

1. Type in the command bar: **"check prod status"**
2. Click **Run** on the generated runbook card
3. Watch the fullscreen log viewer populate in real-time

### 6.3 Verify Database

Check your Supabase dashboard:

1. **Table Editor → ops → runs**
   - Should see your run with `status = 'success'`

2. **Table Editor → ops → run_events**
   - Should see multiple log entries with levels (info, success, etc.)

3. **Table Editor → ops → artifacts** (optional)
   - May have generated artifacts (links, diffs, files)

---

## Troubleshooting

### "No Supabase code to deploy"

✅ **FIXED!** You now have `/supabase/migrations/` and `/supabase/functions/` folders.

### "Missing environment variables"

- Check that `.env` file exists and has correct values
- Restart dev server after editing `.env`

### "RPC function not found"

- Make sure migration was applied successfully
- Check **SQL Editor → ops** schema for `enqueue_run`, `claim_run`, `complete_run` functions

### "No events appearing in UI"

1. **Check Edge Function logs:**
   - Dashboard → Edge Functions → ops-executor → Logs
   
2. **Verify secrets are set:**
   - Dashboard → Edge Functions → ops-executor → Settings
   
3. **Manually trigger executor:**
   ```bash
   curl -X POST https://YOUR-PROJECT.supabase.co/functions/v1/ops-executor \
     -H "Authorization: Bearer YOUR-ANON-KEY"
   ```

4. **Check realtime is enabled:**
   - Dashboard → Database → Replication
   - Verify `ops.run_events` is published

### "CORS errors"

- Edge Function includes CORS headers by default
- If still seeing errors, check browser console for specific origin issues

---

## Security Checklist

✅ **Safe in browser:**
- `VITE_SUPABASE_URL`
- `VITE_SUPABASE_ANON_KEY`

❌ **NEVER in browser:**
- `SUPABASE_SERVICE_ROLE_KEY` (Edge Function only!)
- `VERCEL_TOKEN`, `GITHUB_TOKEN`, etc. (Edge Function only!)

✅ **RLS protects you:**
- Users can read/write their own runs
- Only service_role (Edge Function) can write events/artifacts
- Prevents users from faking execution logs

---

## Next Steps

### Replace Adapter Stubs

The Edge Function currently has stub adapters. To enable real integrations:

1. **Open:** `/supabase/functions/ops-executor/index.ts`
2. **Find:** Functions like `vercel_list_deployments`, `github_open_pr`, etc.
3. **Replace:** Stub returns with actual API calls using tokens from `Deno.env.get()`

Example:

```typescript
async function github_open_pr(args: any) {
  const token = Deno.env.get("GITHUB_TOKEN");
  const response = await fetch("https://api.github.com/repos/.../pulls", {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${token}`,
      "Accept": "application/vnd.github.v3+json"
    },
    body: JSON.stringify({
      title: args.title,
      head: args.head,
      base: args.base,
      body: args.body
    })
  });
  const data = await response.json();
  return { url: data.html_url, head: data.head.ref };
}
```

See `/docs/ADAPTER_GUIDE.md` for detailed integration examples.

---

## Production Deployment

### Frontend (Figma Make)

1. Click **Publish** in Figma Make
2. Your app will be live at `https://your-app.figma.site`

### Backend (Already Deployed!)

✅ Supabase Edge Function is already in production
✅ Database schema is already applied
✅ No additional deployment needed

---

## Monitoring

### View Logs

**Edge Function Logs:**
```bash
supabase functions logs ops-executor --tail
```

**Database Activity:**
- Dashboard → Database → Logs
- Look for INSERT operations on `ops.runs`, `ops.run_events`

**Realtime Connections:**
- Dashboard → Database → Replication
- Monitor active subscriptions

---

## 🎉 You're Live!

Your Ops Control Room is now:

✅ Connected to Supabase backend
✅ Streaming logs in real-time
✅ Executing runbooks server-side with secure secrets
✅ Ready for production use

**Share with your team and start automating operations!**
