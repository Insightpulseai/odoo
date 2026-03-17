# Tasks — Odoo.sh × Supabase Platform Kit

**Work breakdown with priorities and dependencies.**

---

## P0: Must Ship (Template Compilation)

### UI Components
- [ ] **TASK-001**: Install shadcn/ui CLI and initialize
  - Depends on: None
  - Effort: 10min
  - Command: `npx shadcn@latest init`

- [ ] **TASK-002**: Add required UI components
  - Depends on: TASK-001
  - Effort: 15min
  - Components: `dialog`, `button`, `card`, `label`, `input`
  - Command: `npx shadcn@latest add dialog button card label input`

- [ ] **TASK-003**: Re-enable SupabaseManagerDialog
  - Depends on: TASK-002
  - Effort: 5min
  - Action: Rename `SupabaseManagerDialog.tsx.skip` → `SupabaseManagerDialog.tsx`

- [ ] **TASK-004**: Update settings page import
  - Depends on: TASK-003
  - Effort: 5min
  - File: `app/(app)/projects/[projectId]/settings/page.tsx`
  - Action: Uncomment dialog import and usage

- [ ] **TASK-005**: Verify build passes
  - Depends on: TASK-004
  - Effort: 5min
  - Command: `pnpm build`
  - Success Criteria: Zero TypeScript errors, clean build output

---

## P1: Core Schema + RLS

### Database Setup

- [ ] **TASK-101**: Create ops schema migration
  - Depends on: None
  - Effort: 30min
  - File: `supabase/migrations/YYYYMMDDHHMMSS_ops_schema.sql`
  - Deliverable: All 7 core tables (tenants, memberships, supabase_projects, odoo_envs, jobs, run_events, audit_log)

- [ ] **TASK-102**: Implement RLS policies
  - Depends on: TASK-101
  - Effort: 45min
  - File: Same migration file
  - Deliverable: RLS enabled on all ops.* tables with tenant isolation

- [ ] **TASK-103**: Create seed data
  - Depends on: TASK-101
  - Effort: 15min
  - File: `supabase/seed.sql` or inline in migration
  - Deliverable: Initial tenant, membership, project mapping

- [ ] **TASK-104**: Test RLS enforcement
  - Depends on: TASK-102, TASK-103
  - Effort: 30min
  - File: `tests/rls/ops-schema.test.ts`
  - Success Criteria: Cross-tenant queries return zero rows

- [ ] **TASK-105**: Create helper RPCs
  - Depends on: TASK-101
  - Effort: 1h
  - File: Same migration or separate
  - Deliverable: `ops.ui_projects()`, `ops.ui_environments()`, `ops.ui_jobs()` RPCs

---

## P1: Platform Kit Integration

### Supabase Manager Dialog

- [ ] **TASK-201**: Install Platform Kit package
  - Depends on: TASK-005
  - Effort: 5min
  - Command: `pnpm add @supabase/platform-kit-nextjs`

- [ ] **TASK-202**: Update SupabaseManagerDialog component
  - Depends on: TASK-201
  - Effort: 15min
  - File: `components/SupabaseManagerDialog.tsx`
  - Deliverable: PlatformKit with apiUrl + aiSqlUrl props

- [ ] **TASK-203**: Test proxy route authZ
  - Depends on: TASK-104 (RLS), TASK-202
  - Effort: 30min
  - File: `tests/api/proxy.test.ts`
  - Success Criteria: Authorized requests pass, unauthorized return 403

- [ ] **TASK-204**: Implement AI SQL route (optional)
  - Depends on: TASK-202
  - Effort: 45min
  - File: `app/api/ai/sql/route.ts`
  - Env Var: `OPENAI_API_KEY`
  - Success Criteria: Generates valid SQL, audits request

---

## P1: Environment Dashboard

### Odoo Environment Registry

- [ ] **TASK-301**: Create environments page
  - Depends on: TASK-105 (RPC)
  - Effort: 1h
  - File: `app/(app)/environments/page.tsx`
  - Deliverable: Server Component fetching via RPC

- [ ] **TASK-302**: Create environment card component
  - Depends on: None
  - Effort: 30min
  - File: `components/env-card.tsx`
  - Features: Health status badge, last deploy, quick actions

- [ ] **TASK-303**: Implement health check API route
  - Depends on: None
  - Effort: 30min
  - File: `app/api/odoo/health/route.ts`
  - Action: Fetch health_url, update ops.odoo_envs

- [ ] **TASK-304**: Wire up job triggers
  - Depends on: TASK-301, TASK-303
  - Effort: 45min
  - File: `app/api/odoo/jobs/route.ts`
  - Action: POST creates ops.jobs record

---

## P2: GitHub Integration

### Webhook + Build Registry

- [ ] **TASK-401**: Create GitHub webhook endpoint
  - Depends on: TASK-101
  - Effort: 1h
  - File: `app/api/webhooks/github/route.ts`
  - Deliverable: Validate signature, create ops.jobs (type: build)

- [ ] **TASK-402**: Extend ops.jobs schema for builds
  - Depends on: TASK-401
  - Effort: 15min
  - File: New migration
  - Fields: `meta.commit_sha`, `meta.branch_name`, `meta.branch_class`

- [ ] **TASK-403**: Create builds dashboard
  - Depends on: TASK-402
  - Effort: 2h
  - File: `app/(app)/builds/page.tsx`
  - Features: Runbot-style grid, latest build per branch

- [ ] **TASK-404**: Create build detail page
  - Depends on: TASK-403
  - Effort: 1h
  - File: `app/(app)/builds/[id]/page.tsx`
  - Features: Logs, status, commit info

---

## P2: Logs + Real-time Stream

### Log Aggregation

- [ ] **TASK-501**: Create run_events table
  - Depends on: None
  - Effort: 15min
  - File: New migration
  - Table: `ops.run_events (id, tenant_id, job_id, env_id, level, source, message, meta, created_at)`

- [ ] **TASK-502**: Create log append API
  - Depends on: TASK-501
  - Effort: 30min
  - File: `app/api/logs/append/route.ts`
  - Action: Insert into ops.run_events

- [ ] **TASK-503**: Create log viewer component
  - Depends on: TASK-501
  - Effort: 2h
  - File: `components/log-viewer.tsx`
  - Features: Filters, real-time tail, search, export

- [ ] **TASK-504**: Create logs page
  - Depends on: TASK-503
  - Effort: 30min
  - File: `app/(app)/logs/page.tsx`
  - Features: Server Component + Client log viewer

---

## P2: Audit Timeline

### Audit Log UI

- [ ] **TASK-601**: Create audit page
  - Depends on: TASK-101
  - Effort: 1h
  - File: `app/(app)/audit/page.tsx`
  - Features: Timeline view, filters (action, target, date)

- [ ] **TASK-602**: Create audit event card
  - Depends on: None
  - Effort: 30min
  - File: `components/audit-event.tsx`
  - Display: Actor, action, target, outcome, timestamp

- [ ] **TASK-603**: Implement Realtime subscription (optional)
  - Depends on: TASK-601
  - Effort: 45min
  - Action: Subscribe to ops.audit_log inserts

---

## P3: Promotions + Backups

### Promotion Workflow

- [ ] **TASK-701**: Create promotions table
  - Depends on: None
  - Effort: 15min
  - File: New migration
  - Table: `ops.promotions (id, tenant_id, source_env, target_env, approver_user_id, status, created_at)`

- [ ] **TASK-702**: Implement token scrubbing logic
  - Depends on: None
  - Effort: 1h
  - File: Server-side utility
  - Action: Identify and scrub sensitive credentials

- [ ] **TASK-703**: Create promotion UI
  - Depends on: TASK-701, TASK-702
  - Effort: 2h
  - File: `app/(app)/promote/page.tsx`
  - Features: Preflight checks, approval, execute

- [ ] **TASK-704**: Create backups page
  - Depends on: None
  - Effort: 1.5h
  - File: `app/(app)/backups/page.tsx`
  - Features: List backups, restore to staging, danger restore to prod

---

## P3: Web Shell

### Exec Sessions

- [ ] **TASK-801**: Create exec_sessions tables
  - Depends on: None
  - Effort: 20min
  - File: New migration
  - Tables: `ops.exec_sessions`, `ops.exec_events`

- [ ] **TASK-802**: Create SSH keys CRUD
  - Depends on: None
  - Effort: 1h
  - File: `app/api/ssh-keys/route.ts`
  - Action: Add/list/delete SSH keys

- [ ] **TASK-803**: Implement session issuance
  - Depends on: TASK-801
  - Effort: 1h
  - File: `app/api/shell/sessions/route.ts`
  - Action: Create exec session with TTL

- [ ] **TASK-804**: Create web shell UI
  - Depends on: TASK-803
  - Effort: 2h
  - File: `app/(app)/shell/page.tsx`
  - Features: Terminal emulator, command streaming, transcript audit

---

## P4: Mail Catcher

### Dev/Staging Email Capture

- [ ] **TASK-901**: Create mailbox table
  - Depends on: None
  - Effort: 15min
  - File: New migration
  - Table: `ops.mailbox_messages`

- [ ] **TASK-902**: Create mail capture endpoint
  - Depends on: TASK-901
  - Effort: 30min
  - File: `app/api/mail/capture/route.ts`
  - Action: Store email metadata + body

- [ ] **TASK-903**: Create mailbox UI
  - Depends on: TASK-902
  - Effort: 1.5h
  - File: `app/(app)/mailbox/page.tsx`
  - Features: Email list, viewer, download raw EML

---

## P4: Constraint Gates

### Preflight Checks

- [ ] **TASK-1001**: Create preflight API
  - Depends on: None
  - Effort: 2h
  - File: `app/api/preflight/route.ts`
  - Checks: PG extensions, object count, cron runtime, system packages

- [ ] **TASK-1002**: Create constraint status dashboard
  - Depends on: TASK-1001
  - Effort: 1h
  - File: `components/constraint-status.tsx`
  - Display: Pass/fail/warn badges per check

- [ ] **TASK-1003**: Wire into build pipeline
  - Depends on: TASK-1001, TASK-403
  - Effort: 30min
  - Action: Call preflight before deploy, fail build if critical

---

## Testing & CI

### E2E Tests

- [ ] **TASK-1101**: Write RLS tests
  - Depends on: TASK-104
  - Effort: 1h
  - File: `tests/rls/ops-schema.test.ts`

- [ ] **TASK-1102**: Write proxy authZ tests
  - Depends on: TASK-203
  - Effort: 1h
  - File: `tests/api/proxy.test.ts`

- [ ] **TASK-1103**: Write E2E Platform Kit test
  - Depends on: TASK-202
  - Effort: 1.5h
  - File: `tests/e2e/platform-kit.test.ts`
  - Tool: Playwright

---

## Summary

**Total Tasks**: 53
**P0 (Must Ship)**: 5 tasks, ~40 minutes
**P1 (Core)**: 18 tasks, ~10 hours
**P2 (Important)**: 14 tasks, ~12 hours
**P3 (Nice-to-Have)**: 12 tasks, ~11 hours
**P4 (Optional)**: 4 tasks, ~4.5 hours

**Estimated Total**: ~38 hours (1 week with focused work)

---

**Version**: 1.0
**Last Updated**: 2026-02-15
