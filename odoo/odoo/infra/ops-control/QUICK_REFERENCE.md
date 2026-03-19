# 🚀 Ops Control Room - Quick Reference Card

**Last Updated:** January 7, 2026

---

## 🚨 FIRST: Fix Database Errors

If you see errors like `Could not find the table 'public.runs'`:

**Quick Fix (2 minutes):**
1. Open `/supabase/migrations/FULL_SETUP.sql`
2. Copy all contents
3. Go to https://supabase.com/dashboard → SQL Editor
4. Paste and click "Run"
5. Enable Realtime: Database → Replication → Toggle "supabase_realtime" ON
6. Refresh your app

**Full Guide:** [FIX_DATABASE_ERRORS.md](./FIX_DATABASE_ERRORS.md)

---

## 📋 Current Status

| Phase | Status | Next Milestone |
|-------|--------|----------------|
| **Phase 0** | 🟢 90% Complete | Finish remaining tasks (1-2 days) |
| **Phase 1** | 🟡 Ready to Start | Deploy Pulser IR migration (Jan 17) |
| **Overall** | 🎯 On Track | v1.0 Launch (Jun 10, 2026) |

---

## 🎯 This Week's Priorities

### Must Do (By Friday)
1. ✅ Session archiving - [Task 1.1 in NEXT_STEPS.md](/NEXT_STEPS.md#task-11-session-archiving-2-hours)
2. ✅ Run filtering - [Task 1.2](/NEXT_STEPS.md#task-12-run-filtering-3-hours)
3. ✅ Error recovery - [Task 1.3](/NEXT_STEPS.md#task-13-error-recovery-4-hours)

### Nice to Have
- Start reading [MCP Spec](https://spec.modelcontextprotocol.io)
- Experiment with Desktop Commander MCP server
- Draft `/src/core/pulser-types.ts`

---

## 📂 Key Documents

| Document | Purpose | When to Read |
|----------|---------|--------------|
| [PHASED_IMPLEMENTATION_PLAN.md](/PHASED_IMPLEMENTATION_PLAN.md) | Master roadmap (8 phases) | **Read first** (30 mins) |
| [NEXT_STEPS.md](/NEXT_STEPS.md) | Immediate actions | **Read second** (15 mins) |
| [STATUS.md](/STATUS.md) | System status | Check weekly |
| [IMPLEMENTATION_SUMMARY_JAN7.md](/IMPLEMENTATION_SUMMARY_JAN7.md) | What we just did | Reference as needed |
| [DEPLOY.md](/DEPLOY.md) | Deployment guide | Before deploying |

---

## 🛠️ Common Commands

### Local Development
```bash
# Start dev server
npm run dev

# Run type check
npm run typecheck

# Run linter
npm run lint

# Build for production
npm run build
```

### Supabase
```bash
# Push migrations
supabase db push

# Deploy edge functions
supabase functions deploy ops-executor

# View logs
supabase functions logs ops-executor

# Reset database (local)
supabase db reset
```

### Git Workflow
```bash
# Create feature branch
git checkout -b feature/session-archiving

# Commit changes
git add .
git commit -m "feat: add session archiving"

# Push and create PR
git push origin feature/session-archiving
# Then open PR in GitHub UI
```

---

## 🔍 Quick Troubleshooting

### Issue: Schema errors in console
**Fix:** Check that all Supabase client code uses `schema: "public"` (not `ops`)

### Issue: Realtime not working
**Fix:** 
1. Check Supabase Dashboard → Database → Replication
2. Ensure tables are added to `supabase_realtime` publication

### Issue: Edge function not executing
**Fix:**
1. Check Supabase Dashboard → Edge Functions → Logs
2. Verify secrets are set (SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
3. Try invoking directly via Supabase client

### Issue: Runs stuck in "queued"
**Fix:**
1. Manually invoke edge function: `supabase functions invoke ops-executor --body '{"run_id":"<ID>"}'`
2. Check executor logs for errors
3. Verify run_id exists in database

---

## 💡 Key Concepts (1-Sentence Each)

- **Pulser IR** - Structured format for describing work (Plan → Steps → Tools → Verifiers)
- **Atomic Claiming** - PostgreSQL `SKIP LOCKED` prevents race conditions when workers claim runs
- **Heartbeat** - Workers send "alive" signal every 2s; if stopped, run is reclaimed
- **Verifiers** - Every step must prove it worked (HTTP check, shell exit code, SQL result)
- **MCP** - Standard protocol for tools/servers (like LSP for operations)
- **Sessions** - Group related runs together (like Claude Code Web lanes)
- **Lanes** - Visual columns (A/B/C/D) for parallel execution within a session
- **Proofs** - Evidence that a step succeeded (logs, responses, checksums)

---

## 📊 System Architecture (One Diagram)

```
┌─────────────────────────────────────────────────────────┐
│                    Figma Make Frontend                  │
│  ┌────────────┐  ┌──────────┐  ┌────────────────────┐  │
│  │ CommandBar │→│ Runboard │→│ RunLogViewerEnhanced│  │
│  └────────────┘  └──────────┘  └────────────────────┘  │
└─────────────────────┬───────────────────────────────────┘
                      │ Supabase JS Client
                      ↓
┌─────────────────────────────────────────────────────────┐
│                    Supabase Backend                     │
│  ┌──────────────────────────────────────────────────┐  │
│  │ PostgreSQL (public schema)                       │  │
│  │  • sessions                                      │  │
│  │  • runs (with lanes, claiming, heartbeat)       │  │
│  │  • run_events (realtime)                        │  │
│  │  • artifacts                                     │  │
│  │  • run_steps                                     │  │
│  │  • [Phase 1: plans, tools, skills, proofs]     │  │
│  └──────────────────────────────────────────────────┘  │
│                                                         │
│  ┌──────────────────────────────────────────────────┐  │
│  │ Edge Function: ops-executor                      │  │
│  │  • Claim runs (SKIP LOCKED)                     │  │
│  │  • Execute steps                                 │  │
│  │  • Emit events (realtime)                       │  │
│  │  • Generate artifacts                            │  │
│  │  • Heartbeat loop                                │  │
│  └──────────────────────────────────────────────────┘  │
│                                                         │
│  ┌──────────────────────────────────────────────────┐  │
│  │ Realtime (pub/sub)                               │  │
│  │  • Broadcasts events to connected clients       │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
                      │
                      ↓ (Future: Phase 2+)
┌─────────────────────────────────────────────────────────┐
│         External Integrations (via MCP/HTTP)            │
│  • GitHub (PRs, Actions)                                │
│  • Vercel (Deployments)                                 │
│  • DigitalOcean (Droplets, DOKS)                        │
│  • Docker (Containers)                                  │
│  • Odoo (Modules, upgrades)                             │
└─────────────────────────────────────────────────────────┘
```

---

## 🎯 Phase Checklist (At a Glance)

- [x] **Phase 0:** Foundation Hardening (90% done)
  - [x] Schema migration to `public`
  - [x] Parallel execution (lanes + claiming)
  - [x] Runboard UI
  - [ ] Session archiving (in progress)
  - [ ] Run filtering (in progress)
  - [ ] Error recovery (in progress)

- [ ] **Phase 1:** Core Execution Engine (starting Jan 10)
  - [ ] Define Pulser IR types
  - [ ] Create DB migration (plans, tools, skills, proofs)
  - [ ] Update executor to use structured plans
  - [ ] Add verifier system
  - [ ] Create plan compiler stub

- [ ] **Phase 2:** MCP Tool Integration
  - [ ] MCP client library
  - [ ] MCP server registry
  - [ ] Tool discovery pipeline
  - [ ] Executor MCP bridge
  - [ ] Tool sandboxing

- [ ] **Phase 3:** Skill System + Compiler
  - [ ] Create 5-7 stock skills
  - [ ] Skill executor
  - [ ] Spec Kit parser
  - [ ] AI-powered compiler

- [ ] **Phase 4:** Verification + Proofs
- [ ] **Phase 5:** Doc→Code Pipelines
- [ ] **Phase 6:** Odoo Extender
- [ ] **Phase 7:** CI/CD + GitHub Gates
- [ ] **Phase 8:** Production Hardening

---

## 🔗 External Resources

| Resource | URL | Use For |
|----------|-----|---------|
| **MCP Spec** | https://spec.modelcontextprotocol.io | Understanding tool protocol |
| **Supabase Docs** | https://supabase.com/docs | Database, Edge Functions, RLS |
| **Odoo Developer** | https://odoo.com/documentation/18.0 | Odoo addon development |
| **Vercel API** | https://vercel.com/docs/rest-api | Deployment automation |
| **GitHub API** | https://docs.github.com/en/rest | PR creation, CI status |
| **DigitalOcean** | https://docs.digitalocean.com | Droplet + DOKS deployment |

---

## 📞 Who to Contact

| Question Type | Contact | Response Time |
|---------------|---------|---------------|
| **Technical Bug** | #ops-control-room | < 2 hours |
| **Architecture Decision** | Schedule sync | < 1 day |
| **Deployment Issue** | Check /DEPLOY.md first | N/A |
| **General Question** | GitHub Discussions | < 1 day |

---

## 🏁 Quick Start (New Developer)

```bash
# 1. Clone repo
git clone <repo-url>
cd ops-control-room

# 2. Install dependencies
npm install

# 3. Copy environment file
cp .env.example .env
# Edit .env with your Supabase credentials

# 4. Start dev server
npm run dev

# 5. Open browser
open http://localhost:3000

# 6. Read docs (while app loads)
# - Start with PHASED_IMPLEMENTATION_PLAN.md
# - Then NEXT_STEPS.md
# - Then this file

# 7. Pick a task and code!
```

---

## 🎓 Learning Checklist

- [ ] Read PHASED_IMPLEMENTATION_PLAN.md (30 mins)
- [ ] Read NEXT_STEPS.md (15 mins)
- [ ] Explore UI: create session, run in lanes, view logs (20 mins)
- [ ] Read MCP Spec (1 hour)
- [ ] Try Desktop Commander MCP server (30 mins)
- [ ] Read Supabase RLS guide (30 mins)
- [ ] Complete first PR (2-4 hours)

**Total Time:** ~6-8 hours to get up to speed

---

## 💬 Daily Standup Template

Post in #ops-control-room:

```
🏗️ Yesterday: [what you shipped]
🚀 Today: [what you're working on]
🚧 Blockers: [none / describe issue]
```

**Example:**
```
🏗️ Yesterday: Implemented session archiving UI
🚀 Today: Adding backend archiveSession() function
🚧 Blockers: None
```

---

## ✅ Pre-Deploy Checklist

Before deploying to production:

- [ ] All migrations applied locally
- [ ] All tests passing (`npm run test`)
- [ ] No TypeScript errors (`npm run typecheck`)
- [ ] No lint errors (`npm run lint`)
- [ ] Supabase secrets configured
- [ ] Edge function deployed and tested
- [ ] Realtime enabled on tables
- [ ] Demo successful in staging
- [ ] Docs updated
- [ ] Team notified

---

## 🎉 Celebrate Every Win

| Accomplishment | Celebration |
|----------------|-------------|
| PR merged | 🎉 in channel |
| Phase task done | Demo in Friday sync |
| Phase complete | Team lunch 🍕 |
| v1.0 launch | Blog post + swag 👕 |

---

## 🔥 TLDR (30 Seconds)

**What:** Ops Control Room - A deterministic agent runtime for structured workflows

**Status:** Phase 0 (foundation) 90% done, Phase 1 (core engine) starts Jan 10

**This Week:** Finish session archiving, run filtering, error recovery

**Next Week:** Define Pulser IR types, create DB migration, update executor

**Launch Goal:** June 10, 2026 (v1.0)

**Key Docs:**
- 📋 Master Plan: [PHASED_IMPLEMENTATION_PLAN.md](/PHASED_IMPLEMENTATION_PLAN.md)
- 🚀 Action Items: [NEXT_STEPS.md](/NEXT_STEPS.md)
- 📊 Status: [STATUS.md](/STATUS.md)

**Your Task:** Pick something from NEXT_STEPS.md and ship it! 💪

---

**Print this card | Bookmark this page | Share with team**

🚀 **Let's build the future of ops automation!** 🚀