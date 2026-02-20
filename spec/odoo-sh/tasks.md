# Tasks: Odoo.sh-Equivalent Platform

## P0: Contracts + Guardrails (Critical Path)

These tasks MUST be completed before any environment automation. They establish the foundation for deterministic builds and safe deployments.

### P0.1: Dev Runtime Contract
**Owner:** Architect
**Deliverable:** `docs/development/DEV_ENVIRONMENT.md`

**Tasks:**
- [ ] Document current `docker-compose.yml` setup (services, volumes, networks)
- [ ] Document `.devcontainer/devcontainer.json` configuration
- [ ] Specify `--dev=all` flags and asset build toolchain (Webpack/esbuild)
- [ ] Define hot reload expectations (<3s Python, <5s JS/CSS)
- [ ] List required environment variables (`ODOO_STAGE=development`, `POSTGRES_URL`, etc.)
- [ ] Document addons path order (odoo, oca, ipai, ipai_meta)
- [ ] Add troubleshooting section (common errors, restart procedures)

**Acceptance:** Dev contract published, peer-reviewed, no ambiguities.

---

### P0.2: Staging Runtime Contract
**Owner:** Architect
**Deliverable:** `docs/deployment/STAGING_ENVIRONMENT.md`

**Tasks:**
- [ ] Document neutralization requirements (email, crons, integrations)
- [ ] Specify staging-specific configuration (`.env.staging`, `odoo.conf.staging`)
- [ ] Define staging data source (production snapshot workflow)
- [ ] Document manual cron trigger procedure
- [ ] Specify test API keys for external services (Slack, payment gateways)
- [ ] Add configuration validation checklist

**Acceptance:** Staging contract published, neutralization requirements clear.

---

### P0.3: Production Runtime Contract
**Owner:** Architect
**Deliverable:** `docs/deployment/PRODUCTION_ENVIRONMENT.md`

**Tasks:**
- [ ] Document current production deployment process (manual steps)
- [ ] Specify production configuration (`.env.production`, `odoo.conf.production`)
- [ ] Define rollback procedure (manual in v1)
- [ ] Document health check endpoints (HTTP, database)
- [ ] Specify resource limits (workers, connection pool, memory)
- [ ] Add disaster recovery procedure

**Acceptance:** Production contract published, rollback procedure tested.

---

### P0.4: Environment Variable Inventory
**Owner:** DevOps
**Deliverable:** `docs/deployment/ENVIRONMENT_VARIABLES.md`

**Tasks:**
- [ ] Catalog all env vars across dev/staging/production
- [ ] Mark required vs. optional for each environment
- [ ] Document source (`.env` file, CI secrets, runtime injection)
- [ ] Specify default values where applicable
- [ ] Add security notes (which vars contain secrets)
- [ ] Create `.env.template` files for each environment

**Acceptance:** Complete inventory, all env vars documented, templates created.

---

### P0.5: CI Guard - Addons Path Invariants
**Owner:** DevOps
**Deliverable:** Extend `scripts/ci/check_addons_path.sh`

**Tasks:**
- [ ] Extract addons path from `docker-compose.yml`
- [ ] Extract addons path from `.devcontainer/devcontainer.json`
- [ ] Extract addons path from deployment manifests (if applicable)
- [ ] Compare paths, fail CI if divergence detected
- [ ] Add to `.github/workflows/ci.yml` (run on all PRs)
- [ ] Document expected addons path order in error message

**Acceptance:** CI guard passing, prevents configuration drift.

---

### P0.6: CI Guard - Environment Consistency
**Owner:** DevOps
**Deliverable:** `scripts/ci/check_environment_consistency.sh`

**Tasks:**
- [ ] Parse `.env.staging` and verify `ODOO_STAGE=staging`
- [ ] Verify staging has `mail.catchall` configured
- [ ] Verify staging has `--max-cron-threads=0` or equivalent
- [ ] Parse `.env.production` and verify production SMTP settings
- [ ] Verify production has required integration keys (non-empty)
- [ ] Add to `.github/workflows/staging-deploy.yml`
- [ ] Document neutralization checklist in error output

**Acceptance:** CI guard validates staging neutralization, fails on misconfiguration.

---

## P1: Runbot-lite + Staging Neutralization (Core Features)

These tasks deliver the primary value: PR environments and safe staging deployments.

### P1.1: GitHub Actions - PR Environment Deploy
**Owner:** DevOps
**Deliverable:** `.github/workflows/pr-environment.yml`

**Tasks:**
- [ ] Trigger workflow on PR open/synchronize (push to PR branch)
- [ ] Build Docker image for PR branch (`docker build -t pr-<number>:latest .`)
- [ ] Tag image with PR number and git SHA
- [ ] Push image to registry (GitHub Container Registry or Docker Hub)
- [ ] Invoke database provisioning script (`scripts/pr_environment/provision_db.sh`)
- [ ] Start Odoo container with unique subdomain (`pr-<number>-<slug>.dev.insightpulseai.com`)
- [ ] Run health check (wait for HTTP 200 on `/web/database/selector`)
- [ ] Post PR comment with access link, credentials, database info
- [ ] Handle errors gracefully (post failure comment to PR)

**Acceptance:** PR environments deploy in <15 minutes, access link posted to PR.

---

### P1.2: DNS Wildcard Configuration
**Owner:** DevOps
**Deliverable:** Cloudflare wildcard DNS record

**Tasks:**
- [ ] Add wildcard DNS record: `*.dev.insightpulseai.com` → Cloudflare proxy
- [ ] Configure Traefik or nginx to route subdomains to Docker containers
- [ ] Test manual subdomain creation (`pr-test.dev.insightpulseai.com`)
- [ ] Document DNS configuration in `docs/deployment/DNS.md`

**Acceptance:** Wildcard DNS resolves, traffic routes to containers.

---

### P1.3: Database Provisioning Script
**Owner:** Backend
**Deliverable:** `scripts/pr_environment/provision_db.sh`

**Tasks:**
- [ ] Accept PR number as argument
- [ ] Create PostgreSQL database: `odoo_pr_<number>`
- [ ] Option 1: Copy staging DB (sanitized snapshot)
- [ ] Option 2: Initialize with demo data (`--without-demo=False`)
- [ ] Set connection string in `.env.pr-<number>` file
- [ ] Return database credentials (user, password, host, port)
- [ ] Add cleanup on failure (drop database if creation fails)

**Acceptance:** Database provisioned in <5 minutes, connection string valid.

---

### P1.4: PR Environment Cleanup Workflow
**Owner:** DevOps
**Deliverable:** `.github/workflows/pr-environment-cleanup.yml`

**Tasks:**
- [ ] Trigger workflow on PR close or merge
- [ ] Stop Docker container for PR (`docker stop pr-<number>`)
- [ ] Remove Docker container (`docker rm pr-<number>`)
- [ ] Drop PostgreSQL database (`dropdb odoo_pr_<number>`)
- [ ] Delete `.env.pr-<number>` file
- [ ] Remove DNS entry (if dynamic, otherwise no-op)
- [ ] Log cleanup actions to GitHub Actions output

**Acceptance:** Environments tear down within 1 hour of PR close, no orphaned resources.

---

### P1.5: Production Snapshot Script
**Owner:** Backend
**Deliverable:** `scripts/staging/snapshot_production_db.sh`

**Tasks:**
- [ ] Create PostgreSQL dump of production database (`pg_dump`)
- [ ] Sanitize PII: `UPDATE res_partner SET email = 'test+' || id || '@example.com'`
- [ ] Sanitize PII: `UPDATE res_partner SET phone = '+1234567890'`
- [ ] Anonymize financial data: `UPDATE account_move_line SET debit = debit * random(), credit = credit * random()`
- [ ] Compress dump (`gzip`)
- [ ] Upload to Supabase Storage or S3
- [ ] Return snapshot URL and metadata (timestamp, size)

**Acceptance:** Snapshot created in <30 minutes, PII sanitized, uploaded to storage.

---

### P1.6: Staging Restore Script
**Owner:** Backend
**Deliverable:** `scripts/staging/restore_snapshot.sh`

**Tasks:**
- [ ] Download latest production snapshot from storage
- [ ] Drop existing staging database (`dropdb odoo_staging`)
- [ ] Create new staging database (`createdb odoo_staging`)
- [ ] Restore snapshot (`psql odoo_staging < snapshot.sql`)
- [ ] Run post-restore cleanup script (`scripts/staging/post_restore_cleanup.sql`)
- [ ] Delete production API keys: `UPDATE ir_config_parameter SET value = 'TEST_KEY' WHERE key LIKE '%api_key%'`
- [ ] Reset admin password to known staging password
- [ ] Verify restore success (check record counts)

**Acceptance:** Staging restores in <30 minutes, data sanitized, admin access works.

---

### P1.7: Staging Neutralization Configuration
**Owner:** Backend
**Deliverable:** `.env.staging`, `odoo.conf.staging`

**Tasks:**
- [ ] Set `ODOO_STAGE=staging` in `.env.staging`
- [ ] Configure email catchall: `mail.catchall = catchall@localhost`
- [ ] Disable crons: `--max-cron-threads=0` in `odoo.conf.staging`
- [ ] Override Slack webhook: `SLACK_WEBHOOK_URL=https://webhook.test/slack`
- [ ] Use test payment gateway keys: `STRIPE_API_KEY=sk_test_...`
- [ ] Document neutralization in `docs/deployment/STAGING_ENVIRONMENT.md`

**Acceptance:** Staging configuration files created, neutralization verified.

---

### P1.8: CI Neutralization Validator
**Owner:** DevOps
**Deliverable:** `scripts/ci/validate_staging_neutralization.sh`

**Tasks:**
- [ ] Parse `.env.staging` and check `ODOO_STAGE=staging`
- [ ] Parse `odoo.conf.staging` and check `mail.catchall` is set
- [ ] Parse `odoo.conf.staging` and check `--max-cron-threads=0`
- [ ] Verify production secrets NOT in `.env.staging` (pattern match `prod`, `live`)
- [ ] Exit with error code 1 if validation fails
- [ ] Print clear error message with remediation steps

**Acceptance:** CI validator passes for valid staging config, fails for invalid.

---

### P1.9: Staging Deployment Workflow
**Owner:** DevOps
**Deliverable:** `.github/workflows/staging-deploy.yml`

**Tasks:**
- [ ] Trigger on merge to `main` branch
- [ ] Run tests (`pytest`, `npm test`)
- [ ] Run security scan (`bandit`, `npm audit`)
- [ ] Run neutralization validator (`scripts/ci/validate_staging_neutralization.sh`)
- [ ] Build Docker image and push to registry
- [ ] Deploy to staging server (Docker Compose or managed service)
- [ ] Run health check (wait for HTTP 200)
- [ ] Post deployment evidence to Supabase `ops.deployments` (if available)
- [ ] Notify Slack on success/failure

**Acceptance:** Staging deploys on merge to `main`, neutralization validated before deploy.

---

## P2: Snapshot Restore + Promotion + Evidence (Advanced Features)

These tasks complete the platform with production promotion workflow and full observability.

### P2.1: Supabase Schema - `ops.*` Tables
**Owner:** Backend
**Deliverable:** `supabase/migrations/<timestamp>_ops_schema.sql`

**Tasks:**
- [ ] Create `ops.builds` table: columns for git SHA, branch, commit message, author, timestamp, dependencies hash, docker image SHA256
- [ ] Create `ops.deployments` table: environment, deployed SHA, migration scripts, health check results, rollback SHA
- [ ] Create `ops.migrations` table: module name, version before/after, migration script, execution time
- [ ] Add indexes on frequently queried columns (environment, deployed SHA, timestamp)
- [ ] Add RLS policies if needed (client isolation)
- [ ] Run migration in Supabase project

**Acceptance:** Tables created, indexes present, RLS configured.

---

### P2.2: CI Build Evidence Emitter
**Owner:** DevOps
**Deliverable:** GitHub Actions step in build workflow

**Tasks:**
- [ ] Capture build metadata (git SHA, branch, commit message, author)
- [ ] Compute Docker image SHA256 (`docker inspect --format='{{.Id}}' <image>`)
- [ ] Compute dependencies lock hash (`sha256sum requirements.txt package-lock.json`)
- [ ] Insert record into Supabase `ops.builds` table via API
- [ ] Save full build logs to `web/docs/evidence/<YYYYMMDD-HHMM+0800>/build/logs/build.log`
- [ ] Handle Supabase API errors gracefully (log warning, don't fail build)

**Acceptance:** Build evidence inserted into Supabase for every build.

---

### P2.3: CI Deployment Evidence Emitter
**Owner:** DevOps
**Deliverable:** GitHub Actions step in deploy workflow

**Tasks:**
- [ ] Capture deployment metadata (environment, deployed SHA, timestamp)
- [ ] Run health checks (HTTP 200 on `/web`, database connectivity)
- [ ] Execute migration dry-run (`odoo -u <modules> --stop-after-init --test-enable`)
- [ ] Insert record into Supabase `ops.deployments` table via API
- [ ] Save deployment logs to `web/docs/evidence/<YYYYMMDD-HHMM+0800>/deploy/logs/deploy.log`
- [ ] Include rollback SHA (previous deployment SHA from Supabase query)

**Acceptance:** Deployment evidence inserted into Supabase for every deployment.

---

### P2.4: Production Promotion Workflow
**Owner:** DevOps
**Deliverable:** `.github/workflows/production-promote.yml`

**Tasks:**
- [ ] Trigger: manual approval on GitHub Actions (workflow_dispatch)
- [ ] Prerequisite check: CI gates pass (tests, security scan, migration dry-run)
- [ ] Execute merge: `main` → `production` branch
- [ ] Build production Docker image (if not built already)
- [ ] Deploy to production server
- [ ] Run health checks (HTTP 200, database connectivity)
- [ ] Emit evidence to Supabase `ops.deployments`
- [ ] Post success/failure notification to Slack
- [ ] On failure: auto-rollback to previous SHA (if health check fails)

**Acceptance:** Production promotions require manual approval, CI gates block bad promotions.

---

### P2.5: Rollback Procedure Documentation
**Owner:** Architect
**Deliverable:** `docs/deployment/ROLLBACK_PROCEDURE.md`

**Tasks:**
- [ ] Document how to identify previous deployment SHA from Supabase `ops.deployments`
- [ ] Document how to revert `production` branch to previous SHA (`git reset --hard <SHA>`)
- [ ] Document how to trigger redeployment (re-run production workflow)
- [ ] Document how to verify rollback success (health checks, smoke tests)
- [ ] Add rollback playbook for common failure scenarios
- [ ] Test rollback procedure in staging environment

**Acceptance:** Rollback procedure documented, tested in staging, <10 minute execution time.

---

### P2.6: Evidence Artifact Retention Policy
**Owner:** DevOps
**Deliverable:** `scripts/evidence/cleanup_old_artifacts.sh`

**Tasks:**
- [ ] Find evidence artifacts older than 30 days (`find web/docs/evidence/ -mtime +30`)
- [ ] Compress with gzip (`gzip -9 <file>`)
- [ ] Move to long-term storage (Supabase Storage or S3)
- [ ] Delete local compressed files after successful upload
- [ ] Delete artifacts older than 90 days from long-term storage
- [ ] Document retention policy in `docs/deployment/EVIDENCE_RETENTION.md`
- [ ] Add to cron job (weekly execution)

**Acceptance:** Evidence artifacts compressed, moved to storage, deleted per policy.

---

### P2.7: PR Environment Documentation
**Owner:** Scribe
**Deliverable:** `docs/development/PR_ENVIRONMENTS.md`

**Tasks:**
- [ ] Document how to access PR environments (URL format, credentials)
- [ ] Document how to view PR database (connection string, admin access)
- [ ] Document how to manually trigger rebuild (re-run workflow)
- [ ] Add troubleshooting section (common errors, restart procedures)
- [ ] Document how to test staging neutralization in PR environment
- [ ] Add screenshots of PR comment with access link

**Acceptance:** PR environment usage documented, screenshots included, no ambiguities.

---

## Notes

- **P0 tasks** are blocking for all other work. Complete these first.
- **P1 tasks** can be parallelized across team members (PR environments and staging neutralization are independent).
- **P2 tasks** depend on P1 completion (promotion workflow requires staging to work).
- **Estimated Total Effort:**
  - P0: 1 week (contracts + guards)
  - P1: 2-3 weeks (PR environments + staging neutralization)
  - P2: 1-2 weeks (promotion + evidence + observability)
  - **Total: 4-6 weeks for full implementation**

---

## Task Ownership

| Priority | Task Count | Owner | Est. Effort |
|----------|------------|-------|-------------|
| P0 | 6 tasks | Architect (3), DevOps (3) | 1 week |
| P1 | 9 tasks | DevOps (5), Backend (4) | 2-3 weeks |
| P2 | 7 tasks | DevOps (4), Backend (1), Architect (1), Scribe (1) | 1-2 weeks |

**Total:** 22 tasks across 3 priorities.
