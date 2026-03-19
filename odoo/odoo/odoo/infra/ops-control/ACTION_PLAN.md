# ✅ Action Plan - Deploy Your Ops Control Room

**Current Status:** 🟢 Ready to Deploy  
**Estimated Time:** 5-10 minutes  
**Last Updated:** January 3, 2026

---

## 🎯 What You Need to Do

Your project is **fully configured** with:
- ✅ Database migration (`/supabase/migrations/20250103000000_ops_schema.sql`)
- ✅ Edge Function (`/supabase/functions/ops-executor/index.ts`)
- ✅ Frontend UI (React components in `/src/app/`)
- ✅ Documentation (this guide + others)

**What's missing:** Just your credentials and one click to deploy!

---

## 📋 5-Step Deployment Checklist

### ✅ Step 0: Install Dependencies (If Running Locally)

**What to do:**

If you're running the dev server locally (not just deploying), you need to install dependencies first:

```bash
# Using pnpm (recommended)
pnpm install

# OR using npm
npm install
```

**Why needed:** The `@supabase/supabase-js` package and other dependencies need to be in `node_modules`

**Skip if:** You're only deploying via Figma Make Deploy button (Figma handles this automatically)

---

### ✅ Step 1: Edit .env File (2 minutes)

**File:** `/.env`

**What to do:**
1. Open `/.env` in your code editor
2. Replace placeholder values with your actual Supabase credentials

**Before:**
```env
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key-here
```

**After:**
```env
VITE_SUPABASE_URL=https://abcdefg123.supabase.co
VITE_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3M...
```

**Where to get these values:**
- 🔗 Go to: https://app.supabase.com
- Select your project
- Navigate to: **Settings → API**
- Copy **Project URL** → `VITE_SUPABASE_URL`
- Copy **Project API keys → anon public** → `VITE_SUPABASE_ANON_KEY`

**Need help?** See `/ENV_SETUP.md`

---

### ✅ Step 2: Click Deploy in Figma Make (1 minute)

**What to do:**
1. In Figma Make, find the **Deploy** button (top-right corner)
2. Click it
3. Wait for deployment to complete (~30 seconds)

**What happens:**
- ✅ Migration `20250103000000_ops_schema.sql` gets applied
  - Creates `ops.runs`, `ops.run_events`, `ops.artifacts` tables
  - Sets up RLS policies
  - Creates helper functions
- ✅ Edge Function `ops-executor` gets deployed
  - Available at `https://YOUR-PROJECT.supabase.co/functions/v1/ops-executor`

**Expected output:**
```
✓ Applied migration: 20250103000000_ops_schema.sql
✓ Deployed function: ops-executor
✓ Deployment complete
```

**Troubleshooting:** If you see "No Supabase code to deploy," you may need to connect Supabase first:
- Figma Make → Settings → Add Backend → Supabase
- Enter your Project URL and anon key

---

### ✅ Step 3: Add Secrets in Figma Make (2 minutes)

**What to do:**
1. In Figma Make: **Settings → Secrets**
2. Click **"Create a secret"** for each required secret

**Required secret:**

| Secret Name | Value | Where to Get |
|------------|-------|--------------|
| `SUPABASE_SERVICE_ROLE_KEY` | `eyJhbG...` | Supabase Dashboard → Settings → API → **service_role** key |

**Optional secrets** (add later if needed):

| Secret Name | Value | Where to Get |
|------------|-------|--------------|
| `VERCEL_TOKEN` | `vercel_...` | https://vercel.com/account/tokens |
| `GITHUB_TOKEN` | `ghp_...` | https://github.com/settings/tokens |
| `DIGITALOCEAN_TOKEN` | `dop_...` | https://cloud.digitalocean.com/account/api/tokens |

**Important:**
- ⚠️ Use **Figma Make's secret UI**, NOT Supabase Dashboard
- ⚠️ Service role key is **different** from anon key - it's on the same Settings → API page

**Need help?** See `/SECRETS_SETUP.md`

---

### ✅ Step 4: Enable Realtime (1 minute)

**What to do:**
1. Go to Supabase Dashboard: https://app.supabase.com
2. Select your project
3. Navigate to: **Database → Replication**
4. Find these tables and **enable** them:
   - ✅ `ops.runs`
   - ✅ `ops.run_events`
   - ✅ `ops.artifacts`
5. Click **Save** (if there's a save button)

**Alternative (SQL method):**

If you don't see a Replication UI, run this in **SQL Editor**:

```sql
alter publication supabase_realtime add table ops.runs;
alter publication supabase_realtime add table ops.run_events;
alter publication supabase_realtime add table ops.artifacts;
```

**Why needed:** This enables real-time log streaming from Edge Function → UI

---

### ✅ Step 5: Set Up Executor Trigger (2 minutes)

**What to do:**

The Edge Function needs to run periodically to check for queued runs.

**Option A: Supabase Cron (Recommended)**

Run this in **Supabase SQL Editor**:

```sql
create extension if not exists pg_cron;

select cron.schedule(
  'ops-executor-cron',
  '* * * * *',  -- Every minute
  $$
  select net.http_post(
    url := 'https://YOUR-PROJECT-REF.supabase.co/functions/v1/ops-executor',
    headers := '{"Authorization": "Bearer YOUR-ANON-KEY"}'::jsonb
  )
  $$
);
```

**Replace these values:**
- `YOUR-PROJECT-REF` → Your project reference ID (e.g., `abcdefg123`)
  - Find it in your Supabase URL: `https://abcdefg123.supabase.co`
- `YOUR-ANON-KEY` → Your anon key from Step 1

**Option B: Manual Trigger (Testing Only)**

For testing, you can trigger manually:

```bash
curl -X POST https://YOUR-PROJECT-REF.supabase.co/functions/v1/ops-executor \
  -H "Authorization: Bearer YOUR-ANON-KEY"
```

**Why needed:** Without a trigger, the executor won't claim queued runs

---

## 🧪 Test Your Deployment

### Quick Test (30 seconds)

1. **Open your app** (Figma Make preview or published URL)
2. **Type:** `"check prod status"`
3. **Verify:** You see a runbook card appear
4. **Click:** The **Run** button
5. **Watch:** Fullscreen log viewer opens
6. **Expect:** Logs start streaming in real-time:
   ```
   ✓ Phase 0: Validate inputs
   ✓ Phase 1: Preflight checks
   ✓ Phase 2: Execute action
   ✓ Phase 3: Verify results
   ✓ Phase 4: Summarize
   ✓ Run complete
   ```

### Detailed Verification

**Check Database:**
1. Go to Supabase Dashboard → **Table Editor**
2. Select schema: **ops**
3. Open table: **runs**
   - Should see 1 row with `status = 'success'`
4. Open table: **run_events**
   - Should see ~10-15 log entries with different levels (info, success, etc.)

**Check Edge Function Logs:**
1. Go to Supabase Dashboard → **Edge Functions**
2. Click: **ops-executor**
3. Navigate to: **Logs**
4. You should see execution logs showing the run was claimed and processed

---

## 🎯 Success Criteria

You've successfully deployed when:

- ✅ `.env` file has your real Supabase credentials
- ✅ Deploy completed without errors
- ✅ Secrets are set in Figma Make
- ✅ Realtime is enabled for ops tables
- ✅ Cron trigger is scheduled
- ✅ Test run shows real-time logs
- ✅ Database has run + event entries

**Status:** 🟢 Production Ready!

---

## 🆘 Troubleshooting

### Issue: "Missing Supabase environment variables"

**Cause:** `.env` file not properly configured

**Fix:**
1. Verify `/.env` file exists
2. Check values are not placeholders
3. Restart dev server (if running locally)
4. Refresh browser

**Guide:** `/ENV_SETUP.md`

---

### Issue: "No Supabase code to deploy"

**Status:** ✅ Should be fixed (you have migrations + functions now)

**If still seeing this:**
1. Verify `/supabase/migrations/20250103000000_ops_schema.sql` exists
2. Verify `/supabase/functions/ops-executor/index.ts` exists
3. Try disconnecting and reconnecting Supabase in Figma Make settings
4. Refresh Figma Make and try Deploy again

**Guide:** `/FIXED.md`

---

### Issue: "No events appearing in UI"

**Cause:** One of several things could be wrong

**Debug checklist:**
- [ ] Did the run get created? (Check Supabase Table Editor → ops.runs)
- [ ] Is realtime enabled? (Database → Replication)
- [ ] Did the executor run? (Edge Functions → ops-executor → Logs)
- [ ] Are secrets set? (Figma Make → Settings → Secrets)
- [ ] Is cron scheduled? (Test manual trigger with curl)

**Detailed guide:** `/FIGMA_MAKE_DEPLOY.md` → Troubleshooting section

---

### Issue: "RPC function not found"

**Cause:** Migration didn't apply successfully

**Fix:**
1. Go to Supabase Dashboard → **SQL Editor**
2. Open a new query
3. Copy entire contents of `/supabase/migrations/20250103000000_ops_schema.sql`
4. Paste and click **Run**
5. Verify success message
6. Check Database → Schema Visualizer for `ops` schema

---

### Issue: "Service role key doesn't work"

**Common mistakes:**
- ❌ Added secret in Supabase Dashboard (use Figma Make UI instead)
- ❌ Used anon key instead of service_role key
- ❌ Copied key incorrectly (truncated)

**Fix:**
1. Go to Supabase Dashboard → Settings → API
2. Find **service_role** (NOT anon public)
3. Click 👁️ Show
4. Copy the **full** key
5. In Figma Make → Settings → Secrets
6. Create/update `SUPABASE_SERVICE_ROLE_KEY`
7. Click Deploy again to re-inject

**Guide:** `/SECRETS_SETUP.md`

---

## 📚 Documentation Reference

| Document | Purpose | When to Read |
|----------|---------|--------------|
| `/ACTION_PLAN.md` | **This file** - Deployment checklist | **Read first!** |
| `/FIGMA_MAKE_DEPLOY.md` | Figma Make-specific deployment | Primary guide |
| `/ENV_SETUP.md` | Get Supabase credentials | Before Step 1 |
| `/SECRETS_SETUP.md` | Configure secrets in Figma Make | During Step 3 |
| `/START_HERE.md` | Navigation hub | Overview |
| `/QUICKSTART.md` | Generic 3-minute setup | Alternative path |
| `/DEPLOY.md` | Detailed deployment | Deep dive |
| `/FIXED.md` | What was fixed | Context |
| `/STATUS.md` | System architecture | Understanding |

---

## 🎉 Next Steps After Deployment

### Immediate (Test Everything)

1. **Test each runbook type:**
   - `"check prod status"` → Healthcheck
   - `"deploy to staging"` → Deploy (stub)
   - `"generate spec for payments"` → Spec generator (stub)
   - `"fix error in auth"` → Incident triage (stub)

2. **Verify real-time streaming works:**
   - Open browser DevTools → Network tab
   - Look for WebSocket connection to Supabase
   - Confirm events arrive in real-time

3. **Check audit trail:**
   - Supabase Table Editor → ops.runs
   - Should see history of all your test runs

### Short-term (Replace Stubs)

The Edge Function currently has **stub adapters** that return mock data.

**To enable real integrations:**

1. Open `/supabase/functions/ops-executor/index.ts`
2. Find adapter functions at bottom of file:
   - `vercel_list_deployments()`
   - `github_open_pr()`
   - `do_droplet_health()`
   - etc.
3. Replace stub returns with real API calls
4. Use tokens from `Deno.env.get("TOKEN_NAME")`
5. Test with real operations

**Detailed guide:** `/docs/ADAPTER_GUIDE.md`

### Long-term (Production Hardening)

- [ ] Add authentication (Supabase Auth)
- [ ] Add user-specific RLS policies
- [ ] Add approval workflow for prod operations
- [ ] Add webhook notifications
- [ ] Set up monitoring/alerting
- [ ] Configure backup/restore
- [ ] Document runbook library

**Detailed guide:** `/docs/DEPLOYMENT_CHECKLIST.md`

---

## ✅ You're Ready to Deploy!

**Start with Step 0:** Install dependencies (if running locally)

**Then:** Follow steps 1-5 in order

**Estimated time:** 5-10 minutes

**Result:** A production-ready runbook executor with real-time logs! 🚀

**Let's go!** 🎯