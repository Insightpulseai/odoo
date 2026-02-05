# 🚀 START HERE - Ops Control Room

**Welcome!** You're about to deploy a production-ready runbook executor that turns natural language commands into structured, audited operations.

---

## 🎯 What Is This?

**Ops Control Room** is a ChatGPT-style interface for executing operational runbooks like:

- **"Deploy to production"** → Builds app, runs migrations, deploys to Vercel
- **"Check prod status"** → Health checks across all services  
- **"Fix payment error"** → Fetches logs, analyzes, creates PR with fix
- **"Generate spec for user auth"** → Creates constitution.md, prd.md, plan.md, tasks.md
- **"Sync database schema"** → Compares dev vs prod, generates ERD + migrations

**Key Features:**
- ✅ Natural language → structured runbooks
- ✅ Real-time log streaming (like ChatGPT responses)
- ✅ Secure server-side execution (secrets never in browser)
- ✅ Audit trail (all runs logged in database)
- ✅ Multi-phase pipeline (validate → preflight → action → verify → summarize)

---

## ⚡ Quick Navigation

### 🟢 First Time Setup (Recommended Path)

**👉 FASTEST PATH: `/ACTION_PLAN.md`** - 5-step deployment checklist (5-10 minutes)

**Alternative detailed guides:**

1. **`/FIGMA_MAKE_DEPLOY.md`** - Figma Make + Supabase deployment (comprehensive)
2. **`/ENV_SETUP.md`** - Get your Supabase credentials
3. **`/SECRETS_SETUP.md`** - Configure secrets in Figma Make

### 🟡 Alternative Paths

**If you want more context:**

4. **`/QUICKSTART.md`** ← 3-minute generic setup
5. **`/DEPLOY.md`** ← Detailed deployment (not Figma Make-specific)

### 🔵 Understanding What Was Fixed

**Read these if you want to know what happened:**

6. **`/FIXED.md`** ← What errors were resolved
7. **`/STATUS.md`** ← Current system status and architecture

### 🟣 Advanced Topics

**For customization and extension:**

8. **`/docs/DEVELOPER_GUIDE.md`** ← How to extend the system
9. **`/docs/ADAPTER_GUIDE.md`** ← How to add new integrations
10. **`/docs/DEPLOYMENT_CHECKLIST.md`** ← Production deployment checklist

---

## 🏃 Fast Track (5 Minutes to Working System)

### Figma Make Workflow (Recommended)

**👉 Follow `/FIGMA_MAKE_DEPLOY.md`** for the complete Figma Make-specific guide.

**Quick overview:**

1. **Connect Supabase** - Figma Make → Settings → Add Backend → Supabase
2. **Set Secrets** - Figma Make → Settings → Secrets → Create secrets
3. **Click Deploy** - Applies migration + deploys Edge Function
4. **Enable Realtime** - Supabase Dashboard → Database → Replication
5. **Test** - Type "check prod status" → Click Run → Watch logs!

### Manual Workflow (Alternative)

**Step 1: Get Credentials (2 min)**

1. Go to https://app.supabase.com
2. Open your project → Settings → API
3. Copy **Project URL** and **anon public key**

**Guide:** `/ENV_SETUP.md`

**Step 2: Edit .env (1 min)**

Open `/.env` and replace placeholders:

```env
VITE_SUPABASE_URL=https://YOUR-PROJECT.supabase.co
VITE_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIs...
```

**Step 3: Deploy (1 min)**

Click **Deploy** button in Figma Make (top-right corner)

This applies the database migration and deploys the Edge Function.

**Step 4: Configure Secrets (1 min)**

**Figma Make → Settings → Secrets**

Create:
- `SUPABASE_SERVICE_ROLE_KEY` (from Supabase Settings → API)

**Step 5: Enable Realtime (30 sec)**

**Supabase Dashboard → Database → Replication**

Enable:
- `ops.runs`
- `ops.run_events`  
- `ops.artifacts`

**Step 6: Test! (30 sec)**

1. Open your app
2. Type: **"check prod status"**
3. Click **Run**
4. Watch real-time logs! 🎉

**Detailed guide:** `/FIGMA_MAKE_DEPLOY.md`