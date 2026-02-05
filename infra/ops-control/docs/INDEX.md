# 📚 Documentation Index

Welcome to the Ops Control Room documentation! This index will help you find what you need.

---

## 🚀 Getting Started

**New to the project?** Start here:

1. **[README.md](../README.md)** - Architecture overview and introduction
2. **[SETUP.md](../SETUP.md)** - Step-by-step setup guide (Supabase + Edge Function)
3. **[DEMO_MODE.md](./DEMO_MODE.md)** - Test the UI without Supabase (fastest path)

---

## 📖 Core Documentation

### Architecture & Design

- **[README.md](../README.md)**
  - System architecture diagram
  - Security model (what's safe in browser vs server)
  - Data flow (command → execution → logs)
  - File structure
  - Runbook types overview

- **[IMPLEMENTATION_SUMMARY.md](../IMPLEMENTATION_SUMMARY.md)**
  - What's included in v1
  - What works right now
  - Deployment options
  - Testing checklist
  - Success metrics

### Setup & Configuration

- **[SETUP.md](../SETUP.md)**
  - Prerequisites
  - Supabase project setup
  - Database schema installation
  - Edge Function deployment
  - Frontend configuration
  - Troubleshooting guide

- **[.env.example](../.env.example)**
  - Environment variable template
  - Safe vs secret variables
  - Where to find credentials

### Development

- **[DEVELOPER_GUIDE.md](./DEVELOPER_GUIDE.md)**
  - Add new runbook types (step-by-step)
  - Add custom input types
  - Add custom integrations
  - Testing strategy
  - Best practices

- **[ADAPTER_GUIDE.md](./ADAPTER_GUIDE.md)**
  - Implement Vercel adapters (deployments, logs)
  - Implement GitHub adapters (PRs, Actions)
  - Implement Supabase adapters (health checks)
  - Implement DigitalOcean adapters (droplets)
  - Token permissions
  - Error handling

### Deployment

- **[DEPLOYMENT_CHECKLIST.md](./DEPLOYMENT_CHECKLIST.md)**
  - Pre-deployment checklist
  - Frontend deployment (Figma Make, Vercel, Netlify, static)
  - Backend deployment (Supabase, Edge Function)
  - Post-deployment smoke tests
  - Monitoring & alerts
  - Rollback plan
  - Security hardening

### Reference

- **[QUICK_REFERENCE.md](./QUICK_REFERENCE.md)**
  - Command examples
  - Runbook plan structure
  - Execution phases
  - Database schema
  - API endpoints
  - Environment variables
  - Common tasks (deploy, logs, query)
  - Debugging checklist

---

## 🔍 Find What You Need

### I want to...

#### ...understand the system
→ Read **[README.md](../README.md)** for architecture
→ Read **[IMPLEMENTATION_SUMMARY.md](../IMPLEMENTATION_SUMMARY.md)** for what's included

#### ...set it up for the first time
→ Follow **[SETUP.md](../SETUP.md)** step-by-step
→ Use **[.env.example](../.env.example)** for configuration

#### ...test it without Supabase
→ Follow **[DEMO_MODE.md](./DEMO_MODE.md)**

#### ...deploy to production
→ Follow **[DEPLOYMENT_CHECKLIST.md](./DEPLOYMENT_CHECKLIST.md)**

#### ...add a new runbook type
→ Follow **[DEVELOPER_GUIDE.md](./DEVELOPER_GUIDE.md)**

#### ...implement real API calls
→ Follow **[ADAPTER_GUIDE.md](./ADAPTER_GUIDE.md)**

#### ...debug an issue
→ Check **[QUICK_REFERENCE.md](./QUICK_REFERENCE.md)** debugging section
→ Check **[SETUP.md](../SETUP.md)** troubleshooting section

#### ...look up a command or schema
→ Use **[QUICK_REFERENCE.md](./QUICK_REFERENCE.md)** as a cheat sheet

---

## 📂 Code Structure

### Where to Find Things

```
/src/app/                    Frontend UI
  App.tsx                    Main component (Supabase-connected)
  components/
    AppShell.tsx             Layout + header + toasts
    CommandBar.tsx           Natural language input
    RunbookCard.tsx          Inline runbook cards
    LogViewer.tsx            Fullscreen log viewer

/src/core/                   Business logic
  parse.ts                   Natural language → RunbookPlan
  runbooks.ts                Runbook templates
  types.ts                   TypeScript types
  execute.ts                 Local executor (demo mode)

/src/lib/                    Supabase integration
  supabase.ts                Client setup
  database.types.ts          Generated types
  runs.ts                    CRUD + realtime subscriptions

/supabase/                   Backend
  schema.sql                 Database schema (tables, RLS, functions)
  functions/
    ops-executor/            Edge Function executor
      index.ts               Main executor code
      README.md              Deployment guide

/docs/                       Documentation (you are here!)
```

---

## 🎓 Learning Path

### For Stakeholders
1. Read **[README.md](../README.md)** (5 min)
2. Watch a demo (ask developer to run in demo mode)
3. Review **[IMPLEMENTATION_SUMMARY.md](../IMPLEMENTATION_SUMMARY.md)** (10 min)

### For Developers (First Time)
1. Read **[README.md](../README.md)** (10 min)
2. Follow **[DEMO_MODE.md](./DEMO_MODE.md)** to test locally (15 min)
3. Follow **[SETUP.md](../SETUP.md)** to connect Supabase (30 min)
4. Bookmark **[QUICK_REFERENCE.md](./QUICK_REFERENCE.md)** (2 min)

### For Developers (Extending)
1. Read **[DEVELOPER_GUIDE.md](./DEVELOPER_GUIDE.md)** (20 min)
2. Read **[ADAPTER_GUIDE.md](./ADAPTER_GUIDE.md)** (15 min)
3. Implement a test runbook type (1-2 hours)
4. Implement a real adapter (2-4 hours)

### For DevOps (Deploying)
1. Read **[DEPLOYMENT_CHECKLIST.md](./DEPLOYMENT_CHECKLIST.md)** (15 min)
2. Complete pre-deployment checklist (1 hour)
3. Deploy to staging (30 min)
4. Test end-to-end (30 min)
5. Deploy to production (30 min)

---

## 📝 External Documentation

### Supabase
- [Supabase Docs](https://supabase.com/docs)
- [Edge Functions](https://supabase.com/docs/guides/functions)
- [Realtime](https://supabase.com/docs/guides/realtime)
- [Row Level Security](https://supabase.com/docs/guides/auth/row-level-security)

### External APIs
- [Vercel API](https://vercel.com/docs/rest-api)
- [GitHub API](https://docs.github.com/en/rest)
- [DigitalOcean API](https://docs.digitalocean.com/reference/api/)
- [Supabase Management API](https://supabase.com/docs/reference/api/management-api)

### Frontend Tech
- [React](https://react.dev)
- [Vite](https://vite.dev)
- [Tailwind CSS](https://tailwindcss.com)
- [TypeScript](https://www.typescriptlang.org)

---

## 🆘 Need Help?

### For Setup Issues
1. Check **[SETUP.md](../SETUP.md)** troubleshooting section
2. Check **[QUICK_REFERENCE.md](./QUICK_REFERENCE.md)** debugging checklist
3. Review Supabase logs (Dashboard > Logs)
4. Check Edge Function logs (`supabase functions logs ops-executor`)

### For Development Questions
1. Read **[DEVELOPER_GUIDE.md](./DEVELOPER_GUIDE.md)**
2. Check existing runbook implementations in `/src/core/`
3. Review Edge Function code in `/supabase/functions/ops-executor/`

### For Deployment Issues
1. Follow **[DEPLOYMENT_CHECKLIST.md](./DEPLOYMENT_CHECKLIST.md)**
2. Check **[QUICK_REFERENCE.md](./QUICK_REFERENCE.md)** for common tasks
3. Review production settings section

### For API Integration
1. Read **[ADAPTER_GUIDE.md](./ADAPTER_GUIDE.md)**
2. Check external API documentation (links above)
3. Test adapters in isolation before integrating

---

## 📊 Documentation Stats

| Document | Purpose | Length | Audience |
|----------|---------|--------|----------|
| README.md | Architecture overview | ~15 min read | Everyone |
| SETUP.md | Setup guide | ~20 min read | Developers |
| IMPLEMENTATION_SUMMARY.md | Project status | ~10 min read | Everyone |
| DEVELOPER_GUIDE.md | Extend system | ~25 min read | Developers |
| ADAPTER_GUIDE.md | API integration | ~20 min read | Developers |
| DEPLOYMENT_CHECKLIST.md | Deploy guide | ~15 min read | DevOps |
| QUICK_REFERENCE.md | Cheat sheet | Quick lookup | Everyone |
| DEMO_MODE.md | Quick start | ~5 min read | Developers |

**Total reading time:** ~2 hours (but you don't need to read everything!)

---

## 🎯 Most Important Docs (Top 3)

### 1. README.md
Start here to understand the system architecture and design decisions.

### 2. SETUP.md
Everything you need to get the system running locally and in production.

### 3. QUICK_REFERENCE.md
Keep this handy for quick lookups of commands, schemas, and common tasks.

---

## 🔄 Documentation Updates

This documentation is a living guide. As you use the system:

- **Found something unclear?** Update the docs!
- **Added a new feature?** Document it!
- **Fixed a bug?** Add it to troubleshooting!
- **Learned a trick?** Share it in quick reference!

---

## 📜 Version History

- **v1.0** (2026-01-03) - Initial release
  - Complete architecture documentation
  - Setup guide with Supabase integration
  - Developer guide for extensions
  - Adapter implementation guide
  - Deployment checklist
  - Quick reference guide

---

**Happy building! 🚀**

*Questions? Start with [README.md](../README.md) or jump directly to the doc you need above.*
