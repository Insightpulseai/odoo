# Tasks: Odoo.sh-Equivalent Platform

## P0: Contracts + Guardrails (Critical Path)

Critical path. Must be completed before automation.

### P0.1: Dev Runtime Contract
**Owner:** Architect
**Deliverable:** `docs/architecture/DEV_RUNTIME_CONTRACT.md`

**DoD:**
- Defines required dev flags (`--dev=all`) and expected hot-reload behavior (<3s Python, <5s JS/CSS)
- Documents `ODOO_STAGE` semantics (development/staging/production)
- Lists required environment variables and addons path order
- References existing Docker Compose and DevContainer configurations
- Includes troubleshooting section for common dev environment issues

---

### P0.2: Staging Runtime Contract
**Owner:** Architect
**Deliverable:** `docs/architecture/STAGING_RUNTIME_CONTRACT.md`

**DoD:**
- Defines neutralization requirements (email catchall, cron disabling, test integrations)
- Specifies staging-specific configuration templates
- Documents staging data source (production snapshot workflow)
- Defines manual cron trigger procedure for testing
- Includes configuration validation checklist

---

### P0.3: Production Runtime Contract
**Owner:** Architect
**Deliverable:** `docs/architecture/PRODUCTION_RUNTIME_CONTRACT.md`

**DoD:**
- Documents current production deployment process and configuration templates
- Defines rollback procedure (manual in v1, <10 minute target)
- Specifies health check endpoints (HTTP, database connectivity)
- Documents resource limits (workers, connection pool, memory constraints)
- Includes disaster recovery procedure

---

### P0.4: Environment Variable Inventory
**Owner:** DevOps
**Deliverable:** `docs/architecture/ENVIRONMENT_VARIABLES.md`

**DoD:**
- Catalogs all env vars across dev/staging/production with required/optional marking
- Documents source for each variable (.env file, CI secrets, runtime injection)
- Specifies default values and security notes (secret identification)
- Includes `.env.template` files for each environment
- References neutralization requirements from staging contract

---

### P0.5: CI Guard - Addons Path Invariants
**Owner:** DevOps
**Deliverable:** Extend `scripts/ci/check_addons_path.sh`

**DoD:**
- Extracts and compares addons paths from docker-compose.yml, devcontainer.json, deployment manifests
- Fails CI with clear error message if paths diverge
- Integrated into `.github/workflows/ci.yml` (runs on all PRs)
- Error output documents expected canonical order
- Prevents configuration drift between environments

---

### P0.6: CI Guard - Environment Consistency
**Owner:** DevOps
**Deliverable:** `scripts/ci/check_environment_consistency.sh`

**DoD:**
- Validates staging config: `ODOO_STAGE=staging`, `mail.catchall` set, crons disabled
- Validates production config: SMTP settings, integration keys present
- Fails CI with remediation steps if validation fails
- Integrated into `.github/workflows/staging-deploy.yml`
- Prevents production secrets leakage to staging

---

## P1: Runbot-lite + Staging Neutralization (Core Features)

Core value delivery: PR environments and safe staging deployments.

### P1.1: GitHub Actions - PR Environment Deploy
**Owner:** DevOps
**Deliverable:** `.github/workflows/pr-environment.yml`

**DoD:**
- Triggers on PR open/synchronize, builds Docker image tagged with PR number and SHA
- Invokes database provisioning script, starts Odoo with unique subdomain pattern
- Runs health check (HTTP 200), posts PR comment with access link and credentials
- Handles errors gracefully (failure comment to PR)
- Completes deployment in <15 minutes

---

### P1.2: DNS Wildcard Configuration
**Owner:** DevOps
**Deliverable:** Cloudflare wildcard DNS + routing configuration

**DoD:**
- Wildcard DNS record configured: `*.dev.insightpulseai.com`
- Traefik/nginx routes subdomains to Docker containers
- Manual subdomain test passing (pr-test.dev.insightpulseai.com resolves)
- Configuration documented in `docs/deployment/DNS.md`

---

### P1.3: Database Provisioning Script
**Owner:** Backend
**Deliverable:** `scripts/pr_environment/provision_db.sh`

**DoD:**
- Accepts PR number argument, creates PostgreSQL database `odoo_pr_<number>`
- Supports staging DB copy (sanitized) OR demo data initialization
- Returns connection string in `.env.pr-<number>` file
- Includes cleanup on failure (drops database if creation fails)
- Provisions database in <5 minutes

---

### P1.4: PR Environment Cleanup Workflow
**Owner:** DevOps
**Deliverable:** `.github/workflows/pr-environment-cleanup.yml`

**DoD:**
- Triggers on PR close/merge, stops and removes Docker container
- Drops PostgreSQL database, deletes `.env.pr-<number>` file
- Removes DNS entry if dynamic (otherwise no-op)
- Logs all cleanup actions to GitHub Actions output
- Completes teardown within 1 hour, no orphaned resources

---

### P1.5: Production Snapshot Script
**Owner:** Backend
**Deliverable:** `scripts/staging/snapshot_production_db.sh`

**DoD:**
- Creates PostgreSQL dump with PII sanitization (emails, phone numbers)
- Anonymizes financial data (randomized multipliers for amounts)
- Compresses dump (gzip), uploads to Supabase Storage or S3
- Returns snapshot URL and metadata (timestamp, size)
- Completes in <30 minutes

---

### P1.6: Staging Restore Script
**Owner:** Backend
**Deliverable:** `scripts/staging/restore_snapshot.sh`

**DoD:**
- Downloads latest snapshot, drops/recreates staging database
- Restores snapshot, runs post-restore cleanup (delete prod API keys, reset admin password)
- Verifies restore success (record count checks)
- Completes in <30 minutes
- Admin access functional after restore

---

### P1.7: Staging Neutralization Configuration
**Owner:** Backend
**Deliverable:** `.env.staging`, `odoo.conf.staging`

**DoD:**
- Sets `ODOO_STAGE=staging`, configures email catchall and cron disabling
- Overrides external integration endpoints with test URLs/keys
- Configuration validated by P0.6 CI guard
- Documented in staging runtime contract
- Zero production emails possible from staging

---

### P1.8: CI Neutralization Validator
**Owner:** DevOps
**Deliverable:** `scripts/ci/validate_staging_neutralization.sh`

**DoD:**
- Parses staging config, checks ODOO_STAGE, mail.catchall, cron threads
- Verifies production secrets NOT present in staging configuration
- Exits with error code 1 and clear remediation message on failure
- Passes for valid staging config, fails for invalid
- Prevents staging misconfigurations

---

### P1.9: Staging Deployment Workflow
**Owner:** DevOps
**Deliverable:** `.github/workflows/staging-deploy.yml`

**DoD:**
- Triggers on merge to main, runs tests and security scans
- Executes neutralization validator before deployment
- Builds/deploys Docker image, runs health checks
- Emits deployment evidence to Supabase ops.deployments (if available)
- Notifies Slack on success/failure

---

## P2: Promotion + Evidence (Advanced Features)

Production promotion workflow and full observability.

### P2.1: Supabase Schema - `ops.*` Tables
**Owner:** Backend
**Deliverable:** `supabase/migrations/<timestamp>_ops_schema.sql`

**DoD:**
- Creates ops.builds (git SHA, dependencies hash, Docker image SHA256)
- Creates ops.deployments (environment, deployed SHA, health checks, rollback SHA)
- Creates ops.migrations (module versions, migration scripts, execution time)
- Adds indexes on frequently queried columns
- Configures RLS policies if needed for client isolation

---

### P2.2: CI Build Evidence Emitter
**Owner:** DevOps
**Deliverable:** GitHub Actions step in build workflow

**DoD:**
- Captures build metadata (SHA, branch, commit message, author)
- Computes Docker image SHA256 and dependencies lock hash
- Inserts record into Supabase ops.builds table via API
- Saves full build logs to canonical evidence path
- Handles Supabase API errors gracefully (warns, doesn't fail build)

---

### P2.3: CI Deployment Evidence Emitter
**Owner:** DevOps
**Deliverable:** GitHub Actions step in deploy workflow

**DoD:**
- Captures deployment metadata (environment, SHA, timestamp)
- Runs health checks (HTTP 200, database connectivity)
- Executes migration dry-run for validation
- Inserts record into Supabase ops.deployments with rollback SHA
- Saves deployment logs to canonical evidence path

---

### P2.4: Production Promotion Workflow
**Owner:** DevOps
**Deliverable:** `.github/workflows/production-promote.yml`

**DoD:**
- Requires manual approval (workflow_dispatch)
- Validates CI gates pass (tests, security, migration dry-run)
- Executes main→production branch merge and deployment
- Runs health checks, emits evidence to Supabase
- Auto-rollback on health check failure, Slack notification on completion

---

### P2.5: Rollback Procedure Documentation
**Owner:** Architect
**Deliverable:** `docs/deployment/ROLLBACK_PROCEDURE.md`

**DoD:**
- Documents SHA identification from Supabase ops.deployments
- Documents branch revert and redeployment trigger procedures
- Includes rollback playbook for common failure scenarios
- Tested in staging environment
- Target execution time <10 minutes

---

### P2.6: Evidence Artifact Retention Policy
**Owner:** DevOps
**Deliverable:** `scripts/evidence/cleanup_old_artifacts.sh`

**DoD:**
- Compresses evidence artifacts older than 30 days (gzip)
- Moves to long-term storage (Supabase Storage or S3)
- Deletes local compressed files after upload, removes 90+ day artifacts
- Documented in `docs/deployment/EVIDENCE_RETENTION.md`
- Runs weekly via cron job

---

### P2.7: PR Environment Runtime Contract
**Owner:** Architect
**Deliverable:** `docs/architecture/PR_RUNTIME_CONTRACT.md`

**DoD:**
- Documents PR environment access (URL format, credentials, database connection)
- Documents manual rebuild trigger procedure (re-run workflow)
- Includes troubleshooting section for common errors and restart procedures
- Documents staging neutralization testing in PR environment
- No ambiguities in usage instructions

---

## Task Inventory (Authoritative)

**P0: Contracts + Guardrails** (6 tasks)
- P0.1 Dev Runtime Contract
- P0.2 Staging Runtime Contract
- P0.3 Production Runtime Contract
- P0.4 Environment Variable Inventory
- P0.5 CI Guard: Addons Path Invariants
- P0.6 CI Guard: Environment Consistency

**P1: Runbot-lite + Staging Neutralization** (9 tasks)
- P1.1 GitHub Actions: PR Environment Deploy
- P1.2 DNS Wildcard Configuration
- P1.3 Database Provisioning Script
- P1.4 PR Environment Cleanup Workflow
- P1.5 Production Snapshot Script
- P1.6 Staging Restore Script
- P1.7 Staging Neutralization Configuration
- P1.8 CI Neutralization Validator
- P1.9 Staging Deployment Workflow

**P2: Promotion + Evidence** (7 tasks)
- P2.1 Supabase Schema: ops.* Tables
- P2.2 CI Build Evidence Emitter
- P2.3 CI Deployment Evidence Emitter
- P2.4 Production Promotion Workflow
- P2.5 Rollback Procedure Documentation
- P2.6 Evidence Artifact Retention Policy
- P2.7 PR Environment Runtime Contract

**Total: 22 tasks across 3 priorities**

---

## Effort Estimates

| Priority | Tasks | Owner Distribution | Est. Effort |
|----------|-------|-------------------|-------------|
| P0 | 6 | Architect (4), DevOps (2) | 1 week |
| P1 | 9 | DevOps (5), Backend (4) | 2-3 weeks |
| P2 | 7 | DevOps (4), Backend (1), Architect (2) | 1-2 weeks |

**Total: 4-6 weeks for full implementation**

**Dependencies:**
- P0 blocks all automation (contracts define what to automate)
- P1 tasks parallelizable (PR environments independent from staging neutralization)
- P2 requires P1 completion (promotion workflow requires working staging)
