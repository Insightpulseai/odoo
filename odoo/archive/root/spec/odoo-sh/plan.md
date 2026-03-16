# Implementation Plan: Odoo.sh-Equivalent Platform

## Overview

This plan delivers an Odoo.sh-like platform for the InsightPulse AI monorepo through 5 phases:
- **Phase 0:** Inventory + Contracts (docs, guards)
- **Phase 1:** Runbot-lite (PR environments)
- **Phase 2:** Staging Snapshot + Neutralization
- **Phase 3:** Promotion + Evidence
- **Phase 4:** Observability Parity

**Total Estimated Effort:** 3-4 weeks for P0 functionality, 6-8 weeks for complete implementation.

---

## Phase 0: Inventory + Contracts (Foundation)

**Goal:** Document existing environment setup, create runtime contracts, establish CI guards.

### Deliverables

1. **Dev Runtime Contract** (`docs/architecture/DEV_RUNTIME_CONTRACT.md`)
   - Document current `docker-compose.yml` and `.devcontainer/devcontainer.json` setup
   - Specify `--dev=all` flags and asset build toolchain
   - Define hot reload expectations (<3s Python, <5s JS/CSS)
   - List required environment variables (`ODOO_STAGE=development`)

2. **Staging Runtime Contract** (`docs/architecture/STAGING_RUNTIME_CONTRACT.md`)
   - Document neutralization requirements (email, crons, integrations)
   - Specify staging-specific configuration (`.env.staging`, `odoo.conf.staging`)
   - Define staging data source (production snapshot workflow)

3. **Production Runtime Contract** (`docs/architecture/PRODUCTION_RUNTIME_CONTRACT.md`)
   - Document production deployment process (current manual steps)
   - Specify production configuration (`.env.production`, `odoo.conf.production`)
   - Define rollback procedure (manual in v1)

4. **Environment Variable Inventory** (`docs/architecture/ENVIRONMENT_VARIABLES.md`)
   - Catalog all env vars across dev/staging/production
   - Mark which are required vs. optional
   - Document source (`.env` file, CI secrets, runtime)

5. **CI Guard: Addons Path Invariants** (extend existing `scripts/ci/check_addons_path.sh`)
   - Verify addons path matches across `docker-compose.yml`, `.devcontainer/devcontainer.json`, deployment manifests
   - Fail CI if paths diverge (prevents runtime configuration drift)

6. **CI Guard: Environment Consistency** (`scripts/ci/check_environment_consistency.sh`)
   - Verify staging has neutralization config (`ODOO_STAGE=staging`, `mail.catchall`, crons disabled)
   - Verify production has correct SMTP settings and integration keys
   - Fail CI if required env vars missing

### Dependencies
- Existing Docker setup (`docker-compose.yml`, `.devcontainer/devcontainer.json`)
- CI infrastructure (`.github/workflows/`)

### Success Criteria
- [ ] 3 runtime contract docs published
- [ ] 1 environment variable inventory
- [ ] 2 CI guard scripts passing
- [ ] Zero ambiguity in environment setup process

---

## Phase 1: Runbot-lite (PR Environments)

**Goal:** Auto-deploy ephemeral environments for pull requests with unique URLs and auto-teardown.

### Deliverables

1. **GitHub Actions Workflow** (`.github/workflows/pr-environment.yml`)
   - Trigger on PR open/push to PR branch
   - Build Docker image for PR branch (`docker build -t pr-<number>:latest .`)
   - Provision ephemeral database (PostgreSQL container or Supabase branch)
   - Start Odoo container with unique subdomain (`pr-<number>-<slug>.dev.insightpulseai.com`)
   - Post PR comment with access link and credentials
   - Trigger teardown on PR close/merge

2. **DNS Wildcard Configuration**
   - Add wildcard DNS record: `*.dev.insightpulseai.com` → Cloudflare proxy
   - Configure Traefik or nginx to route subdomains to Docker containers

3. **Database Provisioning Script** (`scripts/pr_environment/provision_db.sh`)
   - Create PostgreSQL database for PR (name: `odoo_pr_<number>`)
   - Initialize with staging DB copy (sanitized) OR demo data
   - Set connection string in `.env.pr-<number>`

4. **PR Environment Cleanup Workflow** (`.github/workflows/pr-environment-cleanup.yml`)
   - Trigger on PR close/merge
   - Stop Docker container
   - Drop PostgreSQL database
   - Remove DNS entry (if dynamic)
   - Delete `.env.pr-<number>` file

5. **PR Environment Runtime Contract** (`docs/architecture/PR_RUNTIME_CONTRACT.md`)
   - How to access PR environments
   - Credentials and database access
   - How to manually trigger rebuild
   - Troubleshooting common issues

### Dependencies
- Docker infrastructure
- DNS wildcard record (`*.dev.insightpulseai.com`)
- Cloudflare API access (for dynamic DNS if needed)
- GitHub Actions runner with Docker support

### Success Criteria
- [ ] PR environments deploy in <15 minutes
- [ ] Unique URL posted to PR comment
- [ ] Environments tear down within 1 hour of PR close
- [ ] Zero manual steps required for deployment

---

## Phase 2: Staging Snapshot + Neutralization

**Goal:** Establish staging environment with production data snapshot (sanitized) and verified neutralization.

### Deliverables

1. **Production Snapshot Script** (`scripts/staging/snapshot_production_db.sh`)
   - Create PostgreSQL dump of production database
   - Sanitize PII (emails → `test+<id>@example.com`, phone numbers → random)
   - Anonymize financial data (amounts multiplied by random factor 0.8-1.2)
   - Upload to secure storage (S3 or Supabase Storage)

2. **Staging Restore Script** (`scripts/staging/restore_snapshot.sh`)
   - Download latest production snapshot
   - Restore to staging database (`odoo_staging`)
   - Run post-restore cleanup (delete production API keys, reset passwords)

3. **Staging Neutralization Configuration** (`.env.staging`, `odoo.conf.staging`)
   - Set `ODOO_STAGE=staging`
   - Configure email catchall: `mail.catchall = catchall@localhost`
   - Disable crons: `--max-cron-threads=0` or database flag
   - Override integration endpoints (Slack webhook → test URL)
   - Use test API keys for external services

4. **CI Neutralization Validator** (`scripts/ci/validate_staging_neutralization.sh`)
   - Parse staging configuration files
   - Verify `ODOO_STAGE=staging`
   - Verify `mail.catchall` set
   - Verify no production secrets in staging env vars
   - Fail CI if neutralization not configured

5. **Staging Deployment Workflow** (`.github/workflows/staging-deploy.yml`)
   - Trigger on merge to `main` branch
   - Run tests and security scans
   - Run neutralization validator
   - Deploy to staging server (Docker Compose or managed service)
   - Post deployment evidence to Supabase `ops.deployments`

### Dependencies
- Production database access (read-only credentials)
- Staging server infrastructure
- S3 or Supabase Storage for snapshot hosting
- CI infrastructure

### Success Criteria
- [ ] Staging restores production snapshot in <30 minutes
- [ ] Zero production emails sent from staging
- [ ] CI validates neutralization before deployment
- [ ] Staging data refreshed weekly (automated)

---

## Phase 3: Promotion + Evidence

**Goal:** Formalize promotion workflow with CI gates and evidence emission to Supabase.

### Deliverables

1. **Supabase Schema: `ops.*` Tables** (`supabase/migrations/<timestamp>_ops_schema.sql`)
   - `ops.builds`: git SHA, branch, commit message, author, timestamp, dependencies hash, docker image SHA256
   - `ops.deployments`: environment, deployed SHA, migration scripts executed, health check results, rollback SHA
   - `ops.migrations`: module name, version before/after, migration script, execution time

2. **CI Build Evidence Emitter** (GitHub Actions step in build workflow)
   - Capture build metadata (git SHA, branch, dependencies lock hash)
   - Compute Docker image SHA256
   - Insert record into Supabase `ops.builds` table
   - Save full build logs to `web/docs/evidence/<timestamp>/build/logs/build.log`

3. **CI Deployment Evidence Emitter** (GitHub Actions step in deploy workflow)
   - Capture deployment metadata (environment, deployed SHA, timestamp)
   - Run health checks (HTTP 200, database connectivity)
   - Execute migration dry-run (Odoo `--stop-after-init --test-enable`)
   - Insert record into Supabase `ops.deployments` table
   - Save deployment logs to `web/docs/evidence/<timestamp>/deploy/logs/deploy.log`

4. **Production Promotion Workflow** (`.github/workflows/production-promote.yml`)
   - Trigger: manual approval on GitHub Actions
   - Prerequisite: CI gates pass (tests, security scan, migration dry-run)
   - Execute: merge `main` → `production` branch
   - Deploy to production server
   - Emit evidence to Supabase
   - Post success/failure notification to Slack

5. **Rollback Procedure Documentation** (`docs/deployment/ROLLBACK_PROCEDURE.md`)
   - How to identify previous deployment SHA from Supabase `ops.deployments`
   - How to revert `production` branch to previous SHA
   - How to trigger redeployment
   - How to verify rollback success

### Dependencies
- Supabase project with `ops.*` schema
- GitHub Actions workflows for build/deploy
- Slack webhook for notifications (optional)

### Success Criteria
- [ ] 100% of deployments have evidence in Supabase
- [ ] Production promotions require manual approval
- [ ] CI gates block promotion on test/security failures
- [ ] Rollback completes in <10 minutes

---

## Phase 4: Observability Parity

**Goal:** Achieve full observability parity with Odoo.sh (logs, metrics, traces, evidence artifacts).

### Deliverables

1. **Log Aggregation** (Supabase Edge Function or external service)
   - Collect Odoo application logs (Python `logging` module)
   - Collect nginx/Traefik access logs
   - Collect PostgreSQL slow query logs
   - Store in Supabase or external log service (Loki, CloudWatch)

2. **Metrics Collection** (Prometheus + Grafana or Supabase dashboard)
   - Odoo worker count, request rate, response time
   - PostgreSQL connection pool usage, query execution time
   - Docker container resource usage (CPU, memory, disk)
   - Deployment frequency, success rate, rollback count

3. **Evidence Artifact Retention Policy** (`scripts/evidence/cleanup_old_artifacts.sh`)
   - Compress evidence logs older than 30 days (gzip)
   - Move to long-term storage (S3 or Supabase Storage)
   - Delete artifacts older than 90 days
   - Document retention policy in `docs/deployment/EVIDENCE_RETENTION.md`

4. **Incident Postmortem Generator** (`scripts/observability/generate_postmortem.sh`)
   - Query Supabase `ops.deployments` for failed deployments
   - Fetch evidence artifacts (build logs, deploy logs, error traces)
   - Generate markdown postmortem template with timeline
   - Save to `docs/postmortems/<YYYYMMDD>-<incident-slug>.md`

5. **Observability Documentation** (`docs/deployment/OBSERVABILITY.md`)
   - How to access logs (Supabase queries, log service UI)
   - How to view metrics (Grafana dashboards)
   - How to retrieve evidence artifacts
   - How to generate postmortems

### Dependencies
- Supabase Edge Functions (for log aggregation)
- Prometheus + Grafana (or equivalent metrics stack)
- S3 or Supabase Storage (for long-term evidence retention)

### Success Criteria
- [ ] Logs accessible within <1 minute of event
- [ ] Metrics updated in real-time (<10 second lag)
- [ ] Evidence artifacts compressed and retained per policy
- [ ] Postmortems auto-generated for failed deployments

---

## Risks and Mitigations

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| Docker image build failures in CI | High | Medium | Implement build caching, retry logic |
| Database snapshot too large (>10GB) | Medium | High | Incremental snapshots, anonymization |
| PR environment resource exhaustion | Medium | Medium | Limit concurrent PR environments to 5 |
| Supabase `ops.*` table schema changes break queries | Low | Medium | Version schema, add migration scripts |
| Evidence artifacts exceed storage quota | Medium | Low | Implement retention policy early (Phase 4) |

---

## Dependencies and Sequencing

### Phase Dependencies
- **Phase 0 → Phase 1:** Contracts must exist before PR environments (environment variable inventory)
- **Phase 0 → Phase 2:** Contracts must exist before staging neutralization (neutralization requirements)
- **Phase 2 → Phase 3:** Staging must work before production promotion (promotion requires staging validation)
- **Phase 3 → Phase 4:** Evidence emission must work before observability parity (metrics depend on evidence tables)

### External Dependencies
- DNS wildcard record configuration (Phase 1)
- Supabase project access (Phase 3, Phase 4)
- GitHub Actions runner with Docker support (Phase 1, Phase 2, Phase 3)
- Production database read access (Phase 2)

---

## Success Metrics

**Overall Platform Health:**
- Developer onboarding time: <4 hours (from 2-3 days)
- Deployment frequency: >5 per week (from <2 per week)
- Staging incident rate: <1 per month (email/cron/integration escapes)
- Production rollback rate: <10% (with <10 minute rollback time)
- Evidence completeness: 100% of deployments have artifacts

**Phase-Specific Metrics:**
- **Phase 0:** All environment contracts published, CI guards passing
- **Phase 1:** PR environments deploy in <15 minutes, teardown in <1 hour
- **Phase 2:** Staging neutralization validated in CI, zero production emails
- **Phase 3:** 100% deployments tracked in Supabase, CI gates block bad promotions
- **Phase 4:** Logs accessible in <1 minute, metrics updated in <10 seconds
