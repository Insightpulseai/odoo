# ✅ Production Checklist

**Project:** InsightPulse AI Ops Console
**Stack:** Next.js (Vercel) × Supabase Platform Kit × Odoo CE 19 (Odoo.sh patterns)
**Release Target:** `main` → `console.insightpulseai.com`

---

## 0. Release Metadata (Required)

- [ ] Release ID / Tag: `_____________________`
- [ ] Commit SHA: `_____________________`
- [ ] Date (UTC+08): `_____________________`
- [ ] Approved by: `_____________________`

---

## 1. Vercel Build & Deployment (BLOCKER)

### Build Integrity

- [ ] Production build succeeds on Vercel
- [ ] No `vercel.json` schema violations (❌ no unsupported keys like `projects`)
- [ ] Correct **Root Directory** selected
- [ ] Framework preset = **Next.js**
- [ ] Node.js version pinned (20.x / 24.x)

### Runtime

- [ ] No runtime crashes on first request
- [ ] Server functions execute within memory/CPU limits
- [ ] Cold Start Prevention enabled
- [ ] Correct region configured (`syd1` or intended region)

---

## 2. Environment Variables & Secrets (BLOCKER)

### Client-side

- [ ] `NEXT_PUBLIC_SUPABASE_URL`
- [ ] `NEXT_PUBLIC_SUPABASE_ANON_KEY`
- [ ] No secrets exposed in `NEXT_PUBLIC_*`

### Server-side

- [ ] Supabase **Service Role Key** present (server only)
- [ ] Claude API key present (server only)
- [ ] Odoo admin / RPC credentials stored in **Vault**
- [ ] SSH private keys stored in **Vault**, never in repo

---

## 3. Supabase Platform Kit Readiness (BLOCKER)

### Database & RLS

- [x] All migrations applied to Production (Schema exists)
- [x] RLS enabled on **all** `ops.*` tables
- [ ] JWT role claims enforced (`admin`, `manager`, `supervisor`, `viewer`)
- [x] No direct table access without RLS

### Core Tables

- [x] `ops.environments`
- [x] `ops.runs`
- [x] `ops.run_events`
- [x] `ops.deployments`
- [x] `ops.stage_clones`
- [x] `ops.module_versions`

### Realtime

- [x] Realtime enabled for build + sync status
- [x] Dashboard updates without refresh

---

## 4. Odoo.sh-Style Environment Parity (BLOCKER)

### Environments Exist

- [x] **Production** (`prod`)
- [x] **Staging** (`stage`)
- [x] **Development** (`dev`)

### Core Patterns

- [ ] Staging clone from Production works (`pg_dump → restore`)
- [ ] Mail catcher active on stage/dev
- [ ] Module auto-update based on manifest diffs
- [ ] One-click rollback restores prior state

---

## 5. CI/CD & Deployment Flow

- [x] GitHub Actions trigger on push
- [x] Branch → environment mapping enforced (main → prod, stage/\* → stage)
- [ ] Build status recorded in `ops.deployments` (❌ Needs CI integration)
- [ ] Logs linked to build records (❌ Needs CI integration)
- [x] Failed builds do **not** mutate prod

---

## 6. UI / Console Integrity

### Core Pages

- [x] Dashboard loads (no blank state)
- [x] Environments page renders all stages
- [x] Deployments page shows history
- [x] Sync Monitor reflects live state
- [x] Logs page streams data

### Platform Kit Components

- [ ] SQL Editor works (Claude AI scoped by RLS)
- [ ] Table browser respects role permissions
- [ ] Storage browser loads artifacts
- [ ] Secrets UI does not leak values

---

## 7. Security & Access Control (BLOCKER)

- [ ] Supabase Auth enforced everywhere
- [ ] Role-based UI access works as intended
- [ ] API routes validate JWT server-side
- [ ] No unauthenticated access to ops APIs
- [ ] Audit logs enabled for user actions

---

## 8. Observability & Alerts

- [x] Odoo server logs streaming correctly
- [ ] Edge Function logs visible (❌ Not yet deployed)
- [x] `ops.run_events` populated (Wired in console hooks)
- [ ] Alerting configured (Slack / webhook)
- [x] Error states visible in UI

---

## 9. Backup & Recovery

- [ ] Automated DB backups scheduled
- [ ] Backups stored in Supabase Storage / DO Spaces
- [ ] Restore path tested (staging)
- [ ] Backup metadata visible in console

---

## 10. Performance & Stability

- [ ] No excessive bundle sizes
- [ ] ISR / SSR behavior correct
- [ ] No N+1 query regressions
- [ ] Acceptable TTFB in Production

---

## 11. Documentation & SSOT Alignment

- [x] README reflects current architecture
- [x] CLAUDE.md context is correct and synced
- [x] SSOT vs SOR doctrine respected
- [ ] Runbooks exist for:
  - Deploy
  - Rollback
  - Stage clone
  - Incident response

---

## 12. Final Sign-off

### Release Decision

- [ ] **APPROVE FOR PRODUCTION**
- [ ] **HOLD / FIX REQUIRED**

### Notes

```
____________________________________________________
____________________________________________________
```

**Signed by:** **\*\*\*\***\_\_\_\_**\*\*\*\***
**Date:** **\*\*\*\***\_\_\_\_**\*\*\*\***

---

### Minimal Acceptance Rule

🚀 **Release is allowed ONLY if all BLOCKER sections pass.**
⛔ Any failure in Build, Secrets, RLS, or Deploy flow = **NO-GO**.
