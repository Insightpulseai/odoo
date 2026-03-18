# 📚 Ops Control Room - Documentation Index

**Last Updated:** January 7, 2026  
**Purpose:** Central hub for all documentation

---

## 🚨 Getting Started? Start Here

### 1. Fix Database Errors First ⚠️

**If you see:** `Could not find the table 'public.runs'`

👉 **Go to:** [FIX_DATABASE_ERRORS.md](./FIX_DATABASE_ERRORS.md) (2 minutes)

**Quick Fix:**
1. Copy `/supabase/migrations/FULL_SETUP.sql`
2. Paste into Supabase SQL Editor
3. Click "Run"
4. Enable Realtime
5. Refresh app

---

## 📖 Documentation Map

### 🎯 Core Planning Documents

| Document | What's In It | When to Read |
|----------|-------------|--------------|
| [PHASED_IMPLEMENTATION_PLAN.md](./PHASED_IMPLEMENTATION_PLAN.md) | **Master roadmap** - 8 phases to v1.0 launch | **Start here** (30 mins) |
| [NEXT_STEPS.md](./NEXT_STEPS.md) | **Action items** - What to do this week | **Read second** (15 mins) |
| [QUICK_REFERENCE.md](./QUICK_REFERENCE.md) | **Cheat sheet** - Commands, concepts, checklist | **Bookmark this** (quick lookup) |

### 🔧 Setup & Configuration

| Document | What's In It | When to Read |
|----------|-------------|--------------|
| [FIX_DATABASE_ERRORS.md](./FIX_DATABASE_ERRORS.md) | Fix "table not found" errors | **If you have errors** (2 mins) |
| [DATABASE_FIX_SUMMARY.md](./DATABASE_FIX_SUMMARY.md) | What was fixed and why | After running migration |
| [MIGRATION_SETUP.md](./MIGRATION_SETUP.md) | Detailed migration troubleshooting | If quick fix didn't work |
| [SETUP.md](./SETUP.md) | Original setup guide | Full project setup |
| [DEPLOY.md](./DEPLOY.md) | Deployment to production | Before deploying |
| [ENV_SETUP.md](./ENV_SETUP.md) | Environment variables guide | Configuring secrets |

### 📊 Status & History

| Document | What's In It | When to Read |
|----------|-------------|--------------|
| [STATUS.md](./STATUS.md) | Current system status | Check weekly |
| [IMPLEMENTATION_SUMMARY_JAN7.md](./IMPLEMENTATION_SUMMARY_JAN7.md) | What we accomplished today | Reference as needed |
| [MIGRATION_TO_PUBLIC_SCHEMA.md](./MIGRATION_TO_PUBLIC_SCHEMA.md) | Why we moved to public schema | Understanding architecture |

### 🏗️ Architecture & Development

| Document | What's In It | When to Read |
|----------|-------------|--------------|
| [README.md](./README.md) | Project overview + architecture | First-time visitors |
| [STRUCTURE.md](./STRUCTURE.md) | File/folder organization | Understanding codebase |
| [docs/DEVELOPER_GUIDE.md](./docs/DEVELOPER_GUIDE.md) | Development best practices | Before coding |
| [docs/ADAPTER_GUIDE.md](./docs/ADAPTER_GUIDE.md) | Implementing real API calls | Replacing stubs |
| [docs/GITHUB_FIRST_PATTERN.md](./docs/GITHUB_FIRST_PATTERN.md) | GitHub integration pattern | Building GitHub features |

### 🎓 Specialized Guides

| Document | What's In It | When to Read |
|----------|-------------|--------------|
| [PARALLEL_OCR_SUMMARY.md](./PARALLEL_OCR_SUMMARY.md) | Parallel execution system | Understanding Runboard |
| [OCR_IMPLEMENTATION.md](./OCR_IMPLEMENTATION.md) | OCR worker details | OCR features |
| [QUICKSTART_OCR.md](./QUICKSTART_OCR.md) | Quick start for OCR | Using OCR |

---

## 🗺️ Learning Path by Role

### For New Users (Just Trying It Out)

1. **Fix database** → [FIX_DATABASE_ERRORS.md](./FIX_DATABASE_ERRORS.md)
2. **Quick start** → [README.md](./README.md#quick-start)
3. **Play with UI** → Open app, click Runboard tab
4. **Understand vision** → [PHASED_IMPLEMENTATION_PLAN.md](./PHASED_IMPLEMENTATION_PLAN.md) (skim)

**Time:** 30 minutes

### For Developers (Building Features)

1. **Fix database** → [FIX_DATABASE_ERRORS.md](./FIX_DATABASE_ERRORS.md)
2. **Read master plan** → [PHASED_IMPLEMENTATION_PLAN.md](./PHASED_IMPLEMENTATION_PLAN.md)
3. **Pick a task** → [NEXT_STEPS.md](./NEXT_STEPS.md)
4. **Understand codebase** → [STRUCTURE.md](./STRUCTURE.md)
5. **Development practices** → [docs/DEVELOPER_GUIDE.md](./docs/DEVELOPER_GUIDE.md)
6. **Start coding** → Pick Phase 0 task

**Time:** 2-3 hours

### For DevOps (Deploying to Production)

1. **Understand architecture** → [README.md](./README.md#architecture-overview)
2. **Database setup** → [MIGRATION_SETUP.md](./MIGRATION_SETUP.md)
3. **Environment config** → [ENV_SETUP.md](./ENV_SETUP.md)
4. **Deploy steps** → [DEPLOY.md](./DEPLOY.md)
5. **Verify deployment** → [docs/DEPLOYMENT_CHECKLIST.md](./docs/DEPLOYMENT_CHECKLIST.md)

**Time:** 1-2 hours

### For Product Managers (Understanding Roadmap)

1. **Vision overview** → [IMPLEMENTATION_SUMMARY_JAN7.md](./IMPLEMENTATION_SUMMARY_JAN7.md)
2. **Full roadmap** → [PHASED_IMPLEMENTATION_PLAN.md](./PHASED_IMPLEMENTATION_PLAN.md)
3. **Current status** → [STATUS.md](./STATUS.md)
4. **Next milestones** → [NEXT_STEPS.md](./NEXT_STEPS.md#timeline-optimistic)

**Time:** 1 hour

---

## 🎯 Documents by Phase

### Phase 0: Foundation (Current)

- ✅ [PARALLEL_OCR_SUMMARY.md](./PARALLEL_OCR_SUMMARY.md) - Parallel execution
- ✅ [MIGRATION_TO_PUBLIC_SCHEMA.md](./MIGRATION_TO_PUBLIC_SCHEMA.md) - Schema migration
- ✅ [DATABASE_FIX_SUMMARY.md](./DATABASE_FIX_SUMMARY.md) - Database setup
- 🔄 [NEXT_STEPS.md](./NEXT_STEPS.md) - Remaining tasks

### Phase 1: Core Engine (Starting Jan 10)

- 📋 [PHASED_IMPLEMENTATION_PLAN.md](./PHASED_IMPLEMENTATION_PLAN.md#phase-1-core-execution-engine--current-focus) - Phase 1 details
- 📅 Will create: `/docs/pulser-ir.md` (Pulser IR spec)
- 📅 Will create: `/docs/execution-model.md` (How runs execute)

### Phase 2-8: Future Phases

See [PHASED_IMPLEMENTATION_PLAN.md](./PHASED_IMPLEMENTATION_PLAN.md) for all phase details.

---

## 🔍 Finding What You Need

### By Topic

**Architecture & Design**
- [README.md](./README.md#architecture-overview)
- [STRUCTURE.md](./STRUCTURE.md)
- [IMPLEMENTATION_SUMMARY_JAN7.md](./IMPLEMENTATION_SUMMARY_JAN7.md#architecture-evolution)

**Database & Schema**
- [FIX_DATABASE_ERRORS.md](./FIX_DATABASE_ERRORS.md)
- [MIGRATION_SETUP.md](./MIGRATION_SETUP.md)
- [MIGRATION_TO_PUBLIC_SCHEMA.md](./MIGRATION_TO_PUBLIC_SCHEMA.md)
- `/supabase/migrations/FULL_SETUP.sql`

**Parallel Execution**
- [PARALLEL_OCR_SUMMARY.md](./PARALLEL_OCR_SUMMARY.md)
- [IMPLEMENTATION_SUMMARY_JAN7.md](./IMPLEMENTATION_SUMMARY_JAN7.md#current-system-capabilities)

**Deployment**
- [DEPLOY.md](./DEPLOY.md)
- [ENV_SETUP.md](./ENV_SETUP.md)
- [docs/DEPLOYMENT_CHECKLIST.md](./docs/DEPLOYMENT_CHECKLIST.md)

**Development**
- [docs/DEVELOPER_GUIDE.md](./docs/DEVELOPER_GUIDE.md)
- [docs/ADAPTER_GUIDE.md](./docs/ADAPTER_GUIDE.md)
- [NEXT_STEPS.md](./NEXT_STEPS.md)

**Planning**
- [PHASED_IMPLEMENTATION_PLAN.md](./PHASED_IMPLEMENTATION_PLAN.md)
- [STATUS.md](./STATUS.md)
- [NEXT_STEPS.md](./NEXT_STEPS.md)

### By Problem

**Error: "Could not find table"**
→ [FIX_DATABASE_ERRORS.md](./FIX_DATABASE_ERRORS.md)

**Realtime not working**
→ [MIGRATION_SETUP.md](./MIGRATION_SETUP.md#troubleshooting)

**Don't know what to build next**
→ [NEXT_STEPS.md](./NEXT_STEPS.md)

**Deployment failing**
→ [DEPLOY.md](./DEPLOY.md)

**Want to understand vision**
→ [PHASED_IMPLEMENTATION_PLAN.md](./PHASED_IMPLEMENTATION_PLAN.md)

---

## 📁 File Locations

### Root Directory

```
/
├── README.md                              ⭐ Start here
├── PHASED_IMPLEMENTATION_PLAN.md         ⭐ Master roadmap
├── NEXT_STEPS.md                         ⭐ Action items
├── QUICK_REFERENCE.md                    ⭐ Cheat sheet
├── FIX_DATABASE_ERRORS.md                🚨 Fix errors first
├── STATUS.md                             📊 Current status
├── IMPLEMENTATION_SUMMARY_JAN7.md        📝 What we did
├── DATABASE_FIX_SUMMARY.md               📝 Database fix details
├── MIGRATION_SETUP.md                    🔧 Migration guide
├── MIGRATION_TO_PUBLIC_SCHEMA.md         📖 Schema migration
├── DEPLOY.md                             🚀 Deployment
├── SETUP.md                              🔧 Setup
├── ENV_SETUP.md                          🔧 Environment
└── ... (other docs)
```

### Documentation Directory

```
/docs
├── DEVELOPER_GUIDE.md                    📖 Dev practices
├── ADAPTER_GUIDE.md                      📖 API integration
├── DEPLOYMENT_CHECKLIST.md               ✅ Deploy checklist
├── GITHUB_FIRST_PATTERN.md               📖 GitHub pattern
├── QUICK_REFERENCE.md                    📖 Quick ref
└── INDEX.md                              📚 This file
```

### Supabase Directory

```
/supabase/migrations
├── FULL_SETUP.sql                        ⭐ Run this first
├── 20250108000000_move_to_public_schema.sql  📝 Migration
└── README.md                             📖 Migration docs
```

---

## 🆘 Quick Help

### I'm stuck with...

**Database errors**
- [FIX_DATABASE_ERRORS.md](./FIX_DATABASE_ERRORS.md) (2 mins)
- [MIGRATION_SETUP.md](./MIGRATION_SETUP.md) (detailed)

**Understanding the project**
- [README.md](./README.md) (overview)
- [IMPLEMENTATION_SUMMARY_JAN7.md](./IMPLEMENTATION_SUMMARY_JAN7.md) (current state)

**Choosing what to build**
- [NEXT_STEPS.md](./NEXT_STEPS.md) (this week)
- [PHASED_IMPLEMENTATION_PLAN.md](./PHASED_IMPLEMENTATION_PLAN.md) (long-term)

**Deploying**
- [DEPLOY.md](./DEPLOY.md) (full guide)
- [docs/DEPLOYMENT_CHECKLIST.md](./docs/DEPLOYMENT_CHECKLIST.md) (checklist)

**Development setup**
- [SETUP.md](./SETUP.md) (full setup)
- [ENV_SETUP.md](./ENV_SETUP.md) (env vars)

---

## ✅ Must-Read Documents

If you only read **3 documents**, read these:

1. **[FIX_DATABASE_ERRORS.md](./FIX_DATABASE_ERRORS.md)** - Get your app working (2 mins)
2. **[PHASED_IMPLEMENTATION_PLAN.md](./PHASED_IMPLEMENTATION_PLAN.md)** - Understand the vision (30 mins)
3. **[NEXT_STEPS.md](./NEXT_STEPS.md)** - Know what to do next (15 mins)

**Total time:** 47 minutes to get fully oriented.

---

## 🎉 Ready to Start?

### Checklist

- [ ] Read this index (you're doing it now!)
- [ ] Fix database errors → [FIX_DATABASE_ERRORS.md](./FIX_DATABASE_ERRORS.md)
- [ ] Understand vision → [PHASED_IMPLEMENTATION_PLAN.md](./PHASED_IMPLEMENTATION_PLAN.md)
- [ ] Pick a task → [NEXT_STEPS.md](./NEXT_STEPS.md)
- [ ] Bookmark cheat sheet → [QUICK_REFERENCE.md](./QUICK_REFERENCE.md)
- [ ] Start coding! 🚀

---

## 📝 Document Status Legend

- ⭐ **Must read** - Critical for getting started
- 🚨 **Urgent** - Fix issues first
- 📊 **Status** - Check regularly
- 📝 **History** - What happened
- 📖 **Reference** - Look up as needed
- 🔧 **Setup** - One-time configuration
- 🚀 **Deployment** - Production ready
- ✅ **Checklist** - Step-by-step verification
- 📋 **Planning** - Roadmap and strategy
- 🎓 **Guide** - How-to instructions

---

**Questions?** Check the relevant document above or ask in #ops-control-room!

**Ready to build?** Pick a task from [NEXT_STEPS.md](./NEXT_STEPS.md) and let's go! 🔥
