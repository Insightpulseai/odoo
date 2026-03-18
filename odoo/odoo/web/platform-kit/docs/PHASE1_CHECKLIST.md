# Phase 1 Execution Checklist

> Implementation checklist for the Supabase + Vercel + DigitalOcean combined architecture.
>
> Each item is tied to existing repos and infrastructure.

---

## Overview

**Phase 1 Goal**: Production-ready platform with all core integrations operational.

**Timeline**: Sequential execution, each section builds on the previous.

**Repos**:
- `odoo-ce-4l` - This repo (Platform Kit + Supabase schemas)
- DigitalOcean infrastructure - `odoo-erp-prod`, `odoo-db-sgp1`

---

## 1. Supabase Foundation

### 1.1 Database Schema

- [x] Create `ops` schema with telemetry tables
  - File: `supabase/migrations/20260131000001_ops_schema.sql`
  - Tables: `runs`, `events`, `health`, `cost_*`

- [x] Create `advisor` schema with governance tables
  - File: `supabase/migrations/20260131000002_advisor_schema.sql`
  - Tables: `checks`, `findings`, `check_runs`, `recommendations`

- [x] Create `mirror` schema with Odoo read replicas
  - File: `supabase/migrations/20260131000003_mirror_schema.sql`
  - Tables: `res_company`, `res_partner`, `account_move`, etc.

- [x] Add RLS policies to all schemas
  - File: `supabase/migrations/20260131000004_cost_control_and_rls.sql`

- [x] Configure pg_cron jobs
  - File: `supabase/migrations/20260131000005_cron_and_config.sql`

- [x] Add Odoo command logging
  - File: `supabase/migrations/20260131000006_odoo_command_log.sql`

### 1.2 Edge Functions

- [x] Deploy `health-check` function
  - File: `supabase/functions/health-check/index.ts`
  - Endpoints: `full`, `database`, `ops`, `mirror`, `external`, `advisor`

- [x] Deploy `slack-alert` function
  - File: `supabase/functions/slack-alert/index.ts`
  - Actions: `send`, `check_findings`, `check_failures`, `check_all`

- [x] Deploy `odoo-proxy` function
  - File: `supabase/functions/odoo-proxy/index.ts`
  - Pattern: Vercel → Supabase Auth → HMAC → Odoo API

- [x] Deploy `drift-detection` function
  - File: `supabase/functions/drift-detection/index.ts`
  - Systems: GitHub, Mailgun, Supabase, Vercel

- [x] Deploy `repo-auditor` function
  - Files: `supabase/functions/repo-auditor/*.ts`
  - Purpose: GitHub repository governance checks

### 1.3 Vault Secrets

- [ ] Store GitHub App credentials
  ```sql
  SELECT vault.create_secret('<app_id>', 'github_app_id');
  SELECT vault.create_secret('<private_key>', 'github_app_private_key_pem');
  ```

- [ ] Store Supabase project URLs
  ```sql
  SELECT vault.create_secret('<url>', 'project_url');
  SELECT vault.create_secret('<anon_key>', 'anon_key');
  ```

- [ ] Store Odoo connection details
  ```sql
  SELECT vault.create_secret('<odoo_url>', 'odoo_base_url');
  SELECT vault.create_secret('<hmac_secret>', 'ipai_app_hmac_secret');
  ```

- [ ] Store alerting credentials
  ```sql
  SELECT vault.create_secret('<slack_webhook>', 'slack_webhook_url');
  ```

---

## 2. Vercel Deployment

### 2.1 Project Setup

- [x] Configure `vercel.json` with security headers
  - File: `vercel.json`
  - Headers: `nosniff`, `DENY`, `strict-origin-when-cross-origin`

- [x] Set up Next.js with app directory
  - File: `app/layout.tsx`, `app/page.tsx`
  - Analytics: Vercel Analytics enabled

- [x] Configure health endpoints
  - Files: `app/api/health/route.ts`, `app/api/health/db/route.ts`

### 2.2 CI/CD Workflows

- [x] Production deployment workflow
  - File: `.github/workflows/vercel-production.yml`
  - Gates: lint, typecheck, test, deploy, health check

- [x] Preview deployment workflow
  - File: `.github/workflows/vercel-preview.yml`
  - Trigger: Pull requests

- [x] Supabase deployment workflow
  - File: `.github/workflows/supabase-deploy.yml`
  - Pattern: Staging → Production with health gate

### 2.3 Environment Variables

- [ ] Set Vercel environment variables (production)
  ```
  NEXT_PUBLIC_SUPABASE_URL=<supabase_url>
  NEXT_PUBLIC_SUPABASE_ANON_KEY=<anon_key>
  SUPABASE_SERVICE_ROLE_KEY=<service_role_key>
  ```

- [ ] Set Vercel environment variables (preview)
  ```
  # Use staging Supabase project for previews
  NEXT_PUBLIC_SUPABASE_URL=<staging_url>
  NEXT_PUBLIC_SUPABASE_ANON_KEY=<staging_anon_key>
  ```

---

## 3. DigitalOcean Integration

### 3.1 Odoo Configuration

- [ ] Configure Odoo API endpoints
  - Enable `/web/`, `/api/`, `/ipai/` routes
  - Add HMAC verification middleware

- [ ] Set up private networking
  - Configure VPC between Odoo droplet and database
  - Restrict database access to private network only

- [ ] Configure reverse proxy
  - nginx or Caddy with TLS termination
  - Rate limiting on API endpoints

### 3.2 Database (odoo-db-sgp1)

- [ ] Verify backup schedule
  - Daily automated backups enabled
  - Test restore procedure documented

- [ ] Configure connection pooling
  - PgBouncer if needed for high concurrency

- [ ] Set up monitoring
  - Enable DO database metrics
  - Alert on high CPU/memory/connections

---

## 4. Mirror Sync Pipeline

### 4.1 Initial Sync

- [ ] Create sync script for `mirror.res_company`
  ```bash
  # n8n workflow or custom script
  # Fetch from Odoo XML-RPC, upsert to Supabase
  ```

- [ ] Create sync script for `mirror.res_partner`

- [ ] Create sync script for `mirror.account_move`

- [ ] Create sync script for `mirror.sale_order`

- [ ] Create sync script for `mirror.product_template`

### 4.2 Scheduled Sync

- [ ] Configure hourly sync for transaction tables
  - `res_partner`, `account_move`, `sale_order`

- [ ] Configure daily sync for reference tables
  - `res_company`, `product_template`, `res_users`

- [ ] Add sync health monitoring
  - Track last sync time in `mirror.sync_log`
  - Alert if sync is stale (> 2x expected interval)

---

## 5. Security Hardening

### 5.1 Authentication

- [ ] Configure Supabase Auth providers
  - Email/password (baseline)
  - Google OAuth (if needed)
  - SSO/SAML (future)

- [ ] Set up JWT claims for multi-tenancy
  - Add `company_id` to user metadata
  - Use in RLS policies

- [ ] Configure session settings
  - JWT expiry: 1 hour
  - Refresh token: 7 days

### 5.2 RLS Verification

- [ ] Test `ops.*` schema RLS
  - Service role: full access
  - Authenticated: read-only
  - Anon: no access

- [ ] Test `advisor.*` schema RLS
  - Service role: full access
  - Authenticated: read findings
  - Anon: no access

- [ ] Test `mirror.*` schema RLS
  - Filter by `company_id` from JWT claims
  - Prevent cross-tenant access

### 5.3 Secrets Audit

- [ ] Verify no secrets in git history
  ```bash
  git log -p | grep -E "(password|secret|key|token)" | head -50
  ```

- [ ] Verify no secrets in environment files
  - `.env*` files in `.gitignore`
  - No `.env.local` committed

- [ ] Verify Vault is being used
  - Check Edge Functions fetch from Vault
  - No hardcoded credentials

---

## 6. Monitoring & Alerting

### 6.1 Health Checks

- [ ] Verify `health-check` cron runs every 5 minutes
  ```sql
  SELECT * FROM ops.cron_jobs WHERE name = 'health-check-full';
  ```

- [ ] Verify health data is being recorded
  ```sql
  SELECT * FROM ops.health ORDER BY checked_at DESC LIMIT 10;
  ```

### 6.2 Alerting

- [ ] Test Slack integration
  ```bash
  curl -X POST "https://<project>.supabase.co/functions/v1/slack-alert" \
    -H "Authorization: Bearer <service_role_key>" \
    -d '{"action": "send", "message": "Test alert", "severity": "info"}'
  ```

- [ ] Verify critical finding alerts
  - Create a test critical finding
  - Confirm Slack notification received

### 6.3 Cost Monitoring

- [ ] Verify cost metrics are being recorded
  ```sql
  SELECT * FROM ops.cost_edge_invocations ORDER BY recorded_at DESC LIMIT 10;
  SELECT * FROM ops.cost_db_queries ORDER BY recorded_at DESC LIMIT 10;
  ```

- [ ] Set up cost anomaly alerts
  - Edge invocations > 10x baseline
  - Storage growth > 50% month-over-month

---

## 7. Documentation

### 7.1 Architecture Docs

- [x] Create canonical architecture document
  - File: `docs/CANONICAL_ARCHITECTURE.md`

- [x] Create governance document
  - File: `docs/GOVERNANCE.md`

- [x] Create quick reference rules
  - File: `docs/COPILOT_RULES.md`

### 7.2 Operational Docs

- [x] Document CI/CD secrets
  - File: `docs/CI_SUPABASE_SECRETS.md`

- [ ] Create runbook for common operations
  - Deploying schema changes
  - Adding new Edge Functions
  - Rotating secrets

- [ ] Create incident response guide
  - Escalation contacts
  - Recovery procedures
  - Post-mortem template

---

## 8. Validation

### 8.1 End-to-End Tests

- [ ] Test Vercel → Supabase → Odoo flow
  1. Authenticate via Supabase Auth
  2. Call `odoo-proxy` with valid JWT
  3. Verify request reaches Odoo
  4. Verify audit log in `ops.events`

- [ ] Test mirror sync accuracy
  1. Create record in Odoo
  2. Wait for sync interval
  3. Verify record in `mirror.*` table

- [ ] Test alerting pipeline
  1. Trigger a critical advisor finding
  2. Verify Slack notification
  3. Resolve finding, verify status update

### 8.2 Performance Baseline

- [ ] Measure `odoo-proxy` latency
  - Target: < 500ms p95

- [ ] Measure health check duration
  - Target: < 10s for full check

- [ ] Measure mirror sync duration
  - Target: < 60s per table

### 8.3 Security Audit

- [ ] Run advisor security checks
  ```sql
  SELECT * FROM advisor.run_check('SEC-001');
  SELECT * FROM advisor.run_check('SEC-002');
  SELECT * FROM advisor.run_check('SEC-003');
  ```

- [ ] Verify no critical findings
  ```sql
  SELECT * FROM advisor.v_open_findings WHERE severity = 'critical';
  ```

---

## Completion Criteria

Phase 1 is complete when:

1. All Supabase migrations applied to production
2. All Edge Functions deployed and healthy
3. Vercel deployment with health gate passing
4. Mirror sync running on schedule
5. Alerting verified with test notifications
6. No critical security findings
7. Documentation complete and reviewed

---

## Next Steps (Phase 2)

After Phase 1 completion:

- [ ] Enable Supabase database branching
- [ ] Implement AI agent integration with `ops.*` logging
- [ ] Add CDC pipeline for real-time mirror sync
- [ ] Configure SOC-2 evidence collection
- [ ] Set up disaster recovery testing
