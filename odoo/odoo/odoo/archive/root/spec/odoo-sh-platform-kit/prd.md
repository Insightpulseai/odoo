# PRD — Odoo.sh × Supabase Platform Kit Integration

**Goal**: Ship an Odoo.sh-like platform console that embeds Supabase Platform Kit for unified database, auth, storage, secrets, and logs management.

---

## Personas

### Developer
**Needs**: CI/build logs, web shell, deploy previews, real-time log tail

**Jobs to be Done**:
- Monitor build status for feature branches
- Debug deployment failures with full logs
- SSH into staging environment for quick fixes
- Preview changes before promoting to production

### Tester
**Needs**: Staging builds, shareable URLs, test data isolation

**Jobs to be Done**:
- Access staging builds with realistic data
- Share preview URLs with stakeholders
- Validate migrations without affecting production
- Reset test data between test runs

### PM/Stakeholder
**Needs**: Promotion approvals, audit timeline, uptime visibility

**Jobs to be Done**:
- Approve staging → prod promotions
- Review deployment history and rollback if needed
- View system health and uptime metrics
- Track who did what and when

### Sysadmin
**Needs**: Backups, monitoring, incident response, constraint validation

**Jobs to be Done**:
- Schedule and verify automated backups
- Monitor system performance and resource usage
- Respond to incidents with audit trail
- Enforce platform constraints (no PG extensions, object count limits)

---

## Core Features

### 1. Embedded Supabase Platform Kit

**What**: Supabase management dialog embedded in OdooOps Console

**Capabilities**:
- Database browser + SQL editor
- Schema viewer + migration history
- Auth users + policies
- Storage buckets
- Secrets vault (view/edit)
- Logs + performance metrics

**Architecture**:
- Client: Platform Kit React components
- Server: `/api/supabase-proxy/[...path]` with authZ
- Security: Management API token server-only, tenant-scoped requests

**Success Criteria**:
- ✅ Dialog opens from project settings
- ✅ DB schema loads successfully
- ✅ Unauthorized project_ref returns 403
- ✅ All requests audited

### 2. GitHub-Integrated Build Pipeline

**What**: Automatic builds per commit/PR with logs and status

**Workflow**:
```
GitHub push → Webhook → Create ops.jobs record → CI builds → Update status → Logs stream
```

**Features**:
- Build card grid (Runbot-style) per branch
- Commit SHA + message + status badge
- Real-time log streaming with filters
- Preview environment URLs for PRs

**Success Criteria**:
- ✅ Push to main triggers build
- ✅ Build logs populate `ops.run_events`
- ✅ Build status visible in dashboard
- ✅ Preview URL accessible

### 3. Environment Promotions

**What**: Dev → Staging → Prod promotion with approvals and audit

**Workflow**:
```
Select build → Run preflight checks → Scrub tokens → Approve → Promote → Verify → Audit
```

**Token Scrubbing**:
- Payment gateway credentials
- IAP tokens (Odoo.com integrations)
- Calendar/Drive sync tokens
- External API keys

**Success Criteria**:
- ✅ Promotion creates immutable audit record
- ✅ Tokens scrubbed for non-prod environments
- ✅ Rollback creates new audit event
- ✅ Approval workflow enforced

### 4. Web Shell + SSH Keys

**What**: Ephemeral shell access with full transcript audit

**Features**:
- SSH key management (add/remove)
- Session issuance with TTL (15-30min)
- Command streaming via WebSocket
- Full transcript saved to `ops.exec_events`

**Success Criteria**:
- ✅ Shell connects and executes commands
- ✅ Transcript captured in DB
- ✅ Expired sessions auto-close
- ✅ Audit event for each session

### 5. Mail Catcher (Dev/Staging)

**What**: Capture outbound emails in non-prod environments

**Use Case**: Prevent accidental emails to customers during development

**Features**:
- Intercept SMTP for dev/staging
- Store in `ops.mailbox_messages`
- View subject/from/to/body
- Download raw EML files
- Disabled for production

**Success Criteria**:
- ✅ Dev emails captured
- ✅ Production emails NOT captured
- ✅ Viewer shows email details
- ✅ Raw EML download works

### 6. Backups + Restore

**What**: Automated backups with staging restore

**Policy**:
- **Production**: Daily backups, retained per schedule
- **Staging/Dev**: Best-effort, explicit disclaimers

**Restore Flows**:
- **Standard**: Restore to staging
- **Danger**: Restore to prod (requires confirmation)

**Success Criteria**:
- ✅ Backups run on schedule
- ✅ Staging restore works
- ✅ Prod restore requires danger confirmation
- ✅ Retention policy enforced

### 7. Clear Logs + Real-time Stream

**What**: Centralized log aggregation with filters and tail

**Schema**: `ops.run_events (id, tenant_id, job_id, env_id, level, source, message, meta, created_at)`

**Features**:
- Filter by: env, job, level, source
- Real-time tail (Supabase Realtime)
- Search/export
- Severity highlighting

**Success Criteria**:
- ✅ Logs stream in real-time
- ✅ Filters work correctly
- ✅ Search returns results
- ✅ Export downloads CSV

### 8. Constraint Preflight Gates

**What**: Enforce Odoo.sh-class platform constraints

**Checks**:
1. PostgreSQL Extensions → Fail if detected
2. Object Count Guardrail → Warn at 8k, fail at 10k
3. Cron Runtime Limits → Auto-disable long-running jobs
4. System Package Detection → Fail if runtime apt/yum detected
5. SMTP Port Validation → Enforce 465/587 only
6. Long-lived Connection Detection → Warn if persistent connections assumed

**Success Criteria**:
- ✅ PG extension check fails builds
- ✅ Object count alerts at thresholds
- ✅ Cron timeout triggers notification
- ✅ System package install fails build

---

## Non-Goals (v1)

1. **Full Odoo.sh Build Farm**: We use DO App Platform, not custom runners
2. **Database Superuser UI**: Read-only DB access via Platform Kit
3. **End-User Billing/Plans**: This is an internal ops tool, not SaaS
4. **Multi-Region**: Single DO region (SGP1)
5. **Direct Platform API**: Odoo.sh explicitly doesn't provide this, we follow suit

---

## Success Metrics

### Technical

- ✅ Build passes: `pnpm build` with zero errors
- ✅ RLS enforced: Cross-tenant tests fail
- ✅ Proxy secure: Unauthorized requests return 403
- ✅ Audit complete: 100% of privileged actions logged

### User

- **Developers**: <1min to view build logs
- **Testers**: <2min to access staging preview
- **PMs**: <30s to approve promotion
- **Sysadmins**: <5min to restore backup to staging

---

**Version**: 1.0
**Last Updated**: 2026-02-15
**Status**: Active
