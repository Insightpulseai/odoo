# 🎯 Ops Control Room - Production Architecture

**A secure, delegated runbook executor with real-time streaming logs.**

**Status:** 🟢 Phase 0 Complete | 🚀 Phase 1 Starting Jan 10, 2026

---

## 🚨 Getting Database Errors?

If you see errors like:
```
Could not find the table 'public.runs' in the schema cache
```

**Quick Fix:** Follow [FIX_DATABASE_ERRORS.md](./FIX_DATABASE_ERRORS.md) (2 minutes)

**TL;DR:** Copy `/supabase/migrations/FULL_SETUP.sql` → Paste into Supabase SQL Editor → Run

---

## 📢 What's New (January 7, 2026)

✨ **Major Updates:**
- ✅ **Parallel Execution Live** - Sessions + lanes (A/B/C/D) working
- ✅ **Schema Migration Complete** - Moved from `ops` to `public` schema
- ✅ **Comprehensive Roadmap** - 8-phase plan to v1.0 launch
- 📋 **New Documentation:**
  - [PHASED_IMPLEMENTATION_PLAN.md](/PHASED_IMPLEMENTATION_PLAN.md) - Full 8-phase roadmap (5-7 months)
  - [NEXT_STEPS.md](/NEXT_STEPS.md) - Immediate action items
  - [QUICK_REFERENCE.md](/QUICK_REFERENCE.md) - One-page cheat sheet
  - [IMPLEMENTATION_SUMMARY_JAN7.md](/IMPLEMENTATION_SUMMARY_JAN7.md) - What we just did

---

## 🚀 Quick Start

### For New Users (5 minutes)
```bash
# 1. Clone and install
git clone <repo-url>
cd ops-control-room
npm install

# 2. Configure Supabase
cp .env.example .env
# Edit .env with your Supabase credentials

# 3. Start dev server
npm run dev

# 4. Open browser
open http://localhost:3000

# 5. Try it out
# - Click "Runboard" tab
# - Create a new session
# - Run something in lane A
# - Watch logs stream in real-time!
```

### For Developers (Deep Dive)
1. **Read the plan:** [PHASED_IMPLEMENTATION_PLAN.md](/PHASED_IMPLEMENTATION_PLAN.md) (30 mins)
2. **Pick a task:** [NEXT_STEPS.md](/NEXT_STEPS.md) (15 mins)
3. **Start coding:** Pick any task from Phase 0 remaining items

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    USER INTERFACE                           │
│  (Figma Make / Vercel / Static Deploy)                     │
│                                                             │
│  • Parse natural language → Runbook Plan                   │
│  • Render inline runbook cards                             │
│  • Subscribe to realtime events                            │
│  • Display fullscreen log viewer                           │
└──────────────────┬──────────────────────────────────────────┘
                   │ Supabase Client SDK
                   │ (anon key - RLS protected)
                   ▼
┌─────────────────────────────────────────────────────────────┐
│                   SUPABASE (State + Queue)                  │
│                                                             │
│  Tables:                                                    │
│  • ops.runs         ← Runbook execution queue              │
│  • ops.run_events   ← Real-time log stream                 │
│  • ops.artifacts    ← Output files/links                   │
│                                                             │
│  Realtime:                                                  │
│  • Postgres CDC → WebSocket → Browser (live logs)          │
│                                                             │
│  RLS:                                                       │
│  • Users can read/create runs (anon key)                   │
│  • Only service_role can write events (executor)           │
└──────────────────┬──────────────────────────────────────────┘
                   │ service_role key
                   │ (secrets in Edge Function)
                   ▼
┌─────────────────────────────────────────────────────────────┐
│         EDGE FUNCTION: ops-executor                         │
│  (Deno runtime on Supabase infrastructure)                 │
│                                                             │
│  1. Claim queued run (atomic lock)                         │
│  2. Execute phases:                                         │
│     • Validate inputs                                       │
│     • Preflight checks (API health)                         │
│     • Action (deploy/PR/sync)                              │
│     • Verify results                                        │
│     • Summarize                                            │
│  3. Write events → ops.run_events (realtime)               │
│  4. Write artifacts → ops.artifacts                        │
│  5. Update run status → success/error                      │
└──────────────────┬──────────────────────────────────────────┘
                   │ HTTP calls (with secrets)
                   ▼
        ┌────────────────────────────────┐
        │   External APIs (privileged)   │
        │                                │
        │  • Vercel (deploy, logs)      │
        │  • GitHub (PRs, Actions)      │
        │  • DigitalOcean (droplets)    │
        │  • Supabase (health checks)   │
        └────────────────────────────────┘
```

---

## 🔐 Security Model

### ✅ What's Safe in the Browser

- `VITE_SUPABASE_URL` - Public project URL
- `VITE_SUPABASE_ANON_KEY` - Protected by Row Level Security (RLS)

**Why it's safe:**
- RLS policies prevent users from writing fake events
- RLS policies prevent users from reading other users' runs
- Anon key has no access to external API secrets

### 🔒 What's Server-Side Only

- `SUPABASE_SERVICE_ROLE_KEY` - Full database access (bypasses RLS)
- `VERCEL_TOKEN` - Deploy and read logs
- `GITHUB_TOKEN` - Create PRs and read Actions
- `DIGITALOCEAN_TOKEN` - Query droplets

**Why it's secure:**
- Edge Function runs in Supabase's isolated runtime (Deno)
- Secrets are environment variables (never in code/browser)
- Only the executor can write events (enforced by RLS)

---

## 🚀 Data Flow

### 1. User Submits Command

```typescript
// Browser (App.tsx)
const plan = planFromPrompt("deploy prod");
const runId = await createRun(plan);
// → INSERT into ops.runs with status='queued'
```

### 2. Executor Claims Run

```typescript
// Edge Function (ops-executor)
const runId = await supabase.rpc("ops.claim_run");
// → UPDATE ops.runs SET status='running' WHERE id=(SELECT ... FOR UPDATE SKIP LOCKED)
```

### 3. Executor Writes Events

```typescript
// Edge Function
await emit("info", "Vercel", "Building application...");
// → INSERT into ops.run_events (realtime trigger)
```

### 4. Browser Receives Events

```typescript
// Browser (App.tsx)
subscribeToRunEvents(runId, (event) => {
  setCurrentEvents(prev => [...prev, event]);
  // → Real-time via Supabase Realtime (WebSocket)
});
```

### 5. Executor Completes

```typescript
// Edge Function
await complete("success");
// → UPDATE ops.runs SET status='success', finished_at=now()
```

---

## 📂 File Structure

```
/
├── src/
│   ├── app/
│   │   ├── App.tsx                      ← Main UI component (wired to Supabase)
│   │   └── components/
│   │       ├── AppShell.tsx            ← Header + layout + toasts
│   │       ├── CommandBar.tsx          ← Natural language input
│   │       ├── RunbookCard.tsx         ← Inline plan cards (Run/Edit)
│   │       └── LogViewer.tsx           ← Fullscreen log viewer with artifacts
│   ├── core/
│   │   ├── parse.ts                    ← Natural language → RunbookPlan
│   │   ├── runbooks.ts                 ← Plan templates (deploy/health/spec/etc)
│   │   └── types.ts                    ← TypeScript types
│   └── lib/
│       ├── supabase.ts                 ← Supabase client setup
│       ├── database.types.ts           ← Generated database types
│       └── runs.ts                     ← CRUD + realtime subscriptions
├── supabase/
│   ├── schema.sql                      ← Database schema (ops.runs, etc)
│   └── functions/
│       └── ops-executor/
│           ├── index.ts                ← Edge Function executor
│           └── README.md               ← Deployment guide
├── docs/
│   └── ADAPTER_GUIDE.md                ← How to implement real API calls
├── SETUP.md                            ← Step-by-step setup guide
└── .env.example                        ← Environment variable template
```

---

## 🧪 Testing Locally

### Without Supabase (local mode)

```bash
# The app still works with the original local executor
# Just comment out Supabase calls in App.tsx and it will use
# the in-memory executor from /src/core/execute.ts

pnpm run dev
```

### With Supabase (production mode)

```bash
# 1. Set up Supabase (see SETUP.md)
# 2. Add credentials to .env
# 3. Deploy Edge Function

pnpm run dev

# In another terminal, trigger the executor manually
curl -X POST https://your-project.supabase.co/functions/v1/ops-executor \
  -H "Authorization: Bearer your-anon-key"
```

---

## 🎨 Runbook Types

| Type | Purpose | Integrations | Risk Level |
|------|---------|--------------|------------|
| `deploy` | Build + migrate + deploy | Vercel, Supabase, GitHub | ⚠️ Prod changes |
| `healthcheck` | Read-only service health | Vercel, Supabase, DigitalOcean | ✅ Safe |
| `spec` | Generate spec kit + PR | GitHub | ✅ Docs only |
| `incident` | Triage error + fix PR | Vercel, GitHub, Supabase | ⚠️ Code changes |
| `schema_sync` | Compare DB schemas | Supabase | ℹ️ Dry-run |

---

## 📊 Execution Phases

All runbooks follow the same deterministic pipeline:

```
Phase 0: Validate inputs
  → Block if missing required fields

Phase 1: Preflight
  → API health checks
  → Latest deployment status
  → Service connectivity

Phase 2: Action
  → Deploy / Open PR / Sync schema
  → (depends on runbook kind)

Phase 3: Verify
  → Re-check health
  → GitHub Actions status
  → Deployment logs

Phase 4: Summarize
  → Generate artifacts (links, diffs)
  → Log "next steps"
```

---

## 🔄 Realtime Event Flow

```
┌──────────────┐
│   Executor   │
│  (Deno Edge) │
└──────┬───────┘
       │ INSERT into ops.run_events
       ▼
┌──────────────────┐
│  PostgreSQL CDC  │ (Change Data Capture)
└──────┬───────────┘
       │ Publish to Realtime
       ▼
┌──────────────────┐
│ Supabase Realtime│ (WebSocket server)
└──────┬───────────┘
       │ Push to subscribed clients
       ▼
┌──────────────────┐
│    Browser UI    │
│  (App.tsx)       │
└──────────────────┘
   setCurrentEvents(prev => [...prev, newEvent])
```

**Latency:** Typically 50-200ms from INSERT to browser update.

---

## 🛠️ Environment Variables

### Browser (Vite)

```env
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=eyJhbGc...
```

### Edge Function (Supabase Secrets)

```bash
supabase secrets set \
  VERCEL_TOKEN=... \
  GITHUB_TOKEN=... \
  DIGITALOCEAN_TOKEN=... \
  SUPABASE_SERVICE_ROLE_KEY=...
```

---

## 📦 Deployment

### Frontend (Figma Make / Vercel)

```bash
pnpm run build
# Upload /dist to Figma Make or deploy to Vercel
```

### Backend (Supabase Edge Function)

```bash
supabase link --project-ref your-ref
supabase functions deploy ops-executor
```

### Database (Supabase SQL)

```bash
# Copy /supabase/schema.sql
# Paste into Supabase SQL Editor > Run
```

---

## 🔧 Adapter Implementation

The Edge Function ships with **stubbed adapters** that return mock data. To connect real APIs:

1. Open `/supabase/functions/ops-executor/index.ts`
2. Find the adapter functions (bottom of file)
3. Replace with real API calls (see `/docs/ADAPTER_GUIDE.md`)

**Example:**

```typescript
// Before (stub)
async function vercel_list_deployments(project: string, limit: number) {
  return [{ id: "dpl_mock", state: "READY", ... }];
}

// After (real)
async function vercel_list_deployments(project: string, limit: number) {
  const token = Deno.env.get("VERCEL_TOKEN");
  const response = await fetch(`https://api.vercel.com/v6/deployments?...`, {
    headers: { Authorization: `Bearer ${token}` }
  });
  return (await response.json()).deployments;
}
```

---

## 🎯 Roadmap

### v1 (Current - MVP)
- ✅ Natural language parsing
- ✅ 5 runbook types
- ✅ Real-time log streaming
- ✅ Inline runbook cards
- ✅ Fullscreen log viewer
- ✅ Supabase state management
- ✅ Edge Function executor
- ⏳ Real API adapters (stubbed)

### v2 (Next)
- [ ] Authentication (Supabase Auth)
- [ ] Run history view
- [ ] Manual retry button
- [ ] Approval workflows (for prod)
- [ ] Webhook notifications

### v3 (Future)
- [ ] Multi-tenant workspaces
- [ ] Custom runbook templates
- [ ] ChatGPT App widget integration
- [ ] Picture-in-Picture mode
- [ ] Audit log export

---

## 📚 Documentation

- [SETUP.md](./SETUP.md) - Step-by-step setup guide
- [docs/ADAPTER_GUIDE.md](./docs/ADAPTER_GUIDE.md) - Implement real API calls
- [supabase/schema.sql](./supabase/schema.sql) - Database schema
- [supabase/functions/ops-executor/README.md](./supabase/functions/ops-executor/README.md) - Edge Function deployment

---

## 🤝 Contributing

This is a v1 prototype. To contribute:

1. **Replace adapter stubs** - Implement real API calls
2. **Add new runbook types** - Extend `/src/core/runbooks.ts`
3. **Improve UI** - Enhance log viewer, add filters, etc.
4. **Add auth** - Integrate Supabase Auth for multi-user support

---

## 📄 License

MIT

---

## 🙏 Credits

Built with:
- **Figma Make** - UI builder
- **Supabase** - Backend + realtime
- **React** - UI framework
- **Tailwind CSS** - Styling
- **TypeScript** - Type safety

---

**Need help?** Check [SETUP.md](./SETUP.md) or open an issue.