# 🚀 Next Steps - Immediate Actions

**Context:** We just created a comprehensive [Phased Implementation Plan](/PHASED_IMPLEMENTATION_PLAN.md) spanning 8 phases over 5-7 months. This document breaks down the **immediate next steps** to move forward.

---

## ✅ Just Fixed (Now)

1. **Schema Migration Complete** ✅
   - Runboard now uses `public` schema (was `ops`)
   - Executor uses `public` schema
   - All realtime subscriptions updated
   - No more schema errors!

2. **Documentation Created** ✅
   - [PHASED_IMPLEMENTATION_PLAN.md](/PHASED_IMPLEMENTATION_PLAN.md) - Full 8-phase roadmap
   - This file - Immediate action items

---

## 🎯 Immediate Priorities (Next 1-2 Days)

### Priority 1: Finish Phase 0 Foundation Hardening
These are small UX improvements to stabilize the current system before adding new features.

#### Task 1.1: Session Archiving (2 hours)
**Why:** Reduce clutter in session selector

**Implementation:**
1. Add "Archive" button to each session in Runboard
2. Update `sessions.status` to 'archived'
3. Filter out archived sessions by default
4. Add "Show Archived" toggle

**Files to modify:**
- `/src/app/components/Runboard.tsx` - Add archive button + filter
- `/src/lib/runs.ts` - Add `archiveSession(sessionId)` function

#### Task 1.2: Run Filtering (3 hours)
**Why:** Find runs faster in the Runs tab

**Implementation:**
1. Add filter dropdowns: Status (all/queued/running/success/error), Lane (all/A/B/C/D)
2. Add search input (filter by intent/title)
3. Apply filters to SQL query

**Files to modify:**
- `/src/app/App.tsx` - Add filter state + UI in "runs" tab
- `/src/lib/runs.ts` - Update `listRuns()` to accept filter params

#### Task 1.3: Error Recovery (4 hours)
**Why:** Auto-retry transient failures

**Implementation:**
1. Add `retry_count` column to `runs` table
2. Create `retry_run(runId)` function
3. Add "Retry" button in RunLogViewerEnhanced
4. Auto-retry failed runs up to 3 times (with exponential backoff)

**Files to create/modify:**
- `/supabase/migrations/20250109000001_add_retry.sql` - Add retry columns
- `/src/lib/runs.ts` - Add retry logic
- `/src/app/components/RunLogViewerEnhanced.tsx` - Add retry button

---

## 🚀 Quick Wins (Next Week)

### Week 1 Goals
Complete Phase 0 + start Phase 1 (Pulser IR types)

**Monday-Tuesday:** 
- ✅ Finish Task 1.1, 1.2, 1.3 above
- Test thoroughly on Runboard

**Wednesday-Thursday:**
- Create `/src/core/pulser-types.ts` (Tool, Skill, Plan, Step, Verifier types)
- Write unit tests for type validation

**Friday:**
- Create Phase 1 database migration (`pulser_ir.sql`)
- Deploy to Supabase
- Test with seeded data

**Weekend (Optional):**
- Read MCP specification: https://spec.modelcontextprotocol.io
- Explore Desktop Commander MCP server
- Sketch out MCP client interface

---

## 📋 Decision Points

Before starting Phase 2 (MCP Integration), we need to decide:

### Decision 1: MCP Transport Strategy
**Options:**
- A) **Server-side only** - Edge functions connect to MCP servers, frontend never touches MCP
- B) **Hybrid** - Some tools run client-side (Desktop Commander), some server-side (GitHub)
- C) **Client-side only** - Browser connects to MCP servers via proxy

**Recommendation:** **Option A (Server-side only)**
- ✅ Simpler security model (no CORS issues)
- ✅ Consistent execution environment
- ✅ Better audit trail
- ❌ Can't access local desktop tools directly

**Action:** Confirm decision before starting Phase 2

### Decision 2: LLM Integration for Compiler
**Options:**
- A) **Claude API** (via Anthropic)
- B) **OpenAI API** (GPT-4)
- C) **Both** (let user choose)
- D) **Self-hosted** (e.g., Ollama)

**Recommendation:** **Option C (Both)** with Claude as default
- ✅ Claude better at code generation
- ✅ OpenAI better at structured output (JSON mode)
- ✅ Flexibility for users

**Action:** Confirm decision before starting Phase 3

### Decision 3: Odoo Priority
**Question:** Is Odoo integration (Phase 6) high priority or can it be deferred?

**If high priority:**
- Start Phase 6 in parallel with Phase 2-3
- Hire Odoo specialist
- Budget 8-10 weeks

**If low priority:**
- Defer to Q3 2025
- Focus on generic doc→code first
- Add Odoo as "plugin" later

**Action:** Confirm priority by end of week

---

## 🎓 Learning Path (This Week)

### Day 1-2: MCP Deep Dive
**Read:**
- [MCP Specification](https://spec.modelcontextprotocol.io)
- [MCP Server Examples](https://github.com/modelcontextprotocol/servers)
- Desktop Commander docs

**Try:**
- Install Desktop Commander MCP server
- Test via MCP Inspector
- Invoke a few tools (list files, run shell command)

### Day 3-4: Vercel/Supabase/GitHub APIs
**Read:**
- [Vercel API Docs](https://vercel.com/docs/rest-api)
- [Supabase Management API](https://supabase.com/docs/reference/api)
- [GitHub REST API](https://docs.github.com/en/rest)

**Try:**
- Deploy a test app to Vercel via API
- Create a Supabase migration via API
- Open a test PR via GitHub API

### Day 5: Docker + DigitalOcean
**Read:**
- [Docker Compose Docs](https://docs.docker.com/compose/)
- [DigitalOcean Kubernetes](https://docs.digitalocean.com/products/kubernetes/)

**Try:**
- Create `docker-compose.yml` for simple app
- Deploy to DigitalOcean droplet
- Set up basic CI/CD via GitHub Actions

---

## 📊 Weekly Check-in Format

Every Friday, answer these questions:

1. **What shipped this week?** (list PRs/features)
2. **What blocked us?** (technical/decision/resource)
3. **What's next week's goal?** (1-2 sentences)
4. **Risks/concerns?** (anything that might derail timeline)

**Post to:** #ops-control-room channel (or create one)

---

## 🛠️ Development Workflow

### Branch Strategy
```
main           <- production-ready
├─ dev         <- integration branch
   ├─ phase-0  <- foundation hardening
   ├─ phase-1  <- pulser IR types
   ├─ phase-2  <- MCP integration
   └─ ...
```

### PR Process
1. Create feature branch from `dev`
2. Implement + test locally
3. Open PR with:
   - Description of what changed
   - Screenshot/video if UI change
   - Link to relevant task in plan
4. Get 1 approval (if team > 1 person)
5. Merge to `dev`
6. Deploy `dev` to staging
7. Weekly merge `dev` → `main` (after testing)

### Testing Checklist (Before Merge)
- [ ] Runs created successfully
- [ ] Events stream in real-time
- [ ] Artifacts displayed correctly
- [ ] Runboard lanes work
- [ ] No console errors
- [ ] No TypeScript errors
- [ ] Migrations applied cleanly

---

## 📞 Getting Help

### When Stuck (Technical)
1. Check existing docs (`/docs`, `/PHASED_IMPLEMENTATION_PLAN.md`)
2. Search Supabase docs / MCP spec
3. Ask in #ops-control-room (or create Discord/Slack)
4. Post issue in GitHub repo

### When Stuck (Decision)
1. Review "Decision Points" above
2. Draft pros/cons doc
3. Schedule 30-min sync
4. Document decision in `/docs/decisions/`

### When Behind Schedule
1. **Don't panic** - phase estimates are flexible
2. Identify blocker (technical debt? unclear requirements? missing knowledge?)
3. Adjust plan (defer non-critical tasks, split large tasks)
4. Communicate early (don't wait until deadline)

---

## 🎉 Success Milestones

### Milestone 1: Foundation Stable (End of Week 1)
- [ ] No schema errors
- [ ] Sessions archive cleanly
- [ ] Runs filter correctly
- [ ] Retries work
- [ ] All tests pass

**Celebrate:** Ship stickers, team lunch 🎉

### Milestone 2: Pulser IR Live (End of Week 2)
- [ ] Plans stored in database
- [ ] Steps execute in order
- [ ] Verifiers run
- [ ] Proofs recorded

**Celebrate:** Demo to stakeholders, blog post 🚀

### Milestone 3: MCP Connected (End of Week 4)
- [ ] Desktop Commander connected
- [ ] GitHub tools working
- [ ] Docker tools working
- [ ] Real workflows running

**Celebrate:** Case study, demo video 🎬

---

## 🚦 Go/No-Go Criteria (Before Starting Next Phase)

Before starting each phase, all of these must be ✅:

- [ ] Previous phase 100% complete (no TODOs left)
- [ ] Database migrations applied to production
- [ ] All tests passing
- [ ] Documentation updated
- [ ] Team trained on new features
- [ ] Stakeholders demoed and approved
- [ ] Decision points resolved

**If any are ❌:** Don't start next phase. Fix issues first.

---

## 📅 Timeline (Optimistic)

| Date | Milestone |
|------|-----------|
| **Week of Jan 7** | Phase 0 complete, Phase 1 started |
| **Week of Jan 14** | Phase 1 complete (Pulser IR types) |
| **Week of Jan 21** | Phase 2 started (MCP integration) |
| **Week of Feb 4** | Phase 2 complete, Phase 3 started |
| **Week of Feb 25** | Phase 3 complete (Skill system + compiler) |
| **Week of Mar 11** | Phase 4 complete (Verification + proofs) |
| **Week of Apr 1** | Phase 5 complete (Doc→code pipelines) |
| **Week of May 6** | Phase 6 complete (Odoo extender) |
| **Week of May 20** | Phase 7 complete (CI/CD + GitHub gates) |
| **Week of Jun 3** | Phase 8 complete (Production hardening) |
| **Week of Jun 10** | **🎉 Launch v1.0** |

**Note:** This is aggressive. Add 30-50% buffer for real-world delays.

---

## 💬 Communication Norms

### Daily Standup (5 mins, async OK)
**Post in #ops-control-room:**
1. What I shipped yesterday
2. What I'm working on today
3. Any blockers

### Weekly Sync (30 mins, Friday)
**Agenda:**
1. Demo this week's work (10 mins)
2. Review check-in questions (10 mins)
3. Plan next week (5 mins)
4. Open discussion (5 mins)

### Ad-Hoc Deep Dives (As Needed)
**When:** Complex technical decisions, architecture changes, major bugs
**Duration:** 60-90 mins
**Output:** Written decision doc

---

## 🎯 Your Mission (This Week)

**Monday Morning:**
1. Read [PHASED_IMPLEMENTATION_PLAN.md](/PHASED_IMPLEMENTATION_PLAN.md) (30 mins)
2. Review this document (15 mins)
3. Pick Task 1.1, 1.2, or 1.3 above
4. Create feature branch
5. Start coding!

**By Friday:**
- ✅ At least 1 task complete
- ✅ Demo working
- ✅ Ready for Phase 1

**Let's ship it!** 🚀

---

## 📚 Quick Reference Links

- **Main Plan:** [/PHASED_IMPLEMENTATION_PLAN.md](/PHASED_IMPLEMENTATION_PLAN.md)
- **Current Status:** [/STATUS.md](/STATUS.md)
- **Deploy Guide:** [/DEPLOY.md](/DEPLOY.md)
- **Quick Start:** [/QUICKSTART.md](/QUICKSTART.md)
- **MCP Spec:** https://spec.modelcontextprotocol.io
- **Supabase Docs:** https://supabase.com/docs
- **Figma Make Docs:** (internal)

---

**Questions?** Drop them in #ops-control-room or open a GitHub Discussion.

**Ready to build?** Pick a task and let's go! 🔥
