# Product Requirements: Odoo.sh-Equivalent Platform

## Problem Statement

The InsightPulse AI Odoo monorepo currently lacks a formalized platform definition for development, staging, and production environments. This creates:

**Pain Points:**
- Inconsistent environment setup across developers (manual configuration drift)
- No clear promotion workflow (ad-hoc deployments to production)
- Lack of staging neutralization (accidental email sends, cron executions)
- Missing observability (no build/deploy evidence trail)
- Unclear hot reload requirements for local development

**Impact:**
- Developer onboarding takes 2-3 days vs. <4 hours target
- Production incidents from untested staging deployments
- Debugging difficulty without deployment evidence
- Feature development blocked by environment inconsistencies

---

## Goals

### 1. Branch-Driven Environment Lifecycle
Formalize dev → staging → production promotion path with git branch mapping and PR-based ephemeral environments.

**Success Metrics:**
- 100% of deployments traceable to git SHA
- <15 minute PR environment creation time
- Zero manual configuration steps in promotion workflow

### 2. Developer Experience Parity with Odoo.sh
Provide hot reload (`--dev=all`), debug assets, and instant feedback for local development.

**Success Metrics:**
- <3 second reload time for Python file changes
- <5 second reload time for JS/CSS changes
- 100% of developers reporting improved DX vs. current state

### 3. Staging Safety and Neutralization
Prevent accidental production interactions (email sends, external API calls) from staging environment.

**Success Metrics:**
- Zero production emails sent from staging in 90-day period
- 100% of external integrations disabled in staging by default
- Automated verification of neutralization configuration in CI

### 4. Promotion Workflow with CI Gates
Require automated validation (tests, security scans, migration dry-runs) before production promotion.

**Success Metrics:**
- 100% of production deployments pass CI gates
- <10 minute gate execution time
- Automated rollback triggered on failed health checks

### 5. Observability and Evidence Emission
Track all builds, deployments, and migrations with structured evidence in Supabase `ops.*` tables.

**Success Metrics:**
- 100% of deployments have evidence artifacts
- <1 minute to retrieve logs for any deployment in past 30 days
- Automated incident postmortem generation from evidence data

---

## Non-Goals

### Will Not Be Implemented

1. **Rebuilding Odoo Enterprise SaaS Features**
   - Multi-tenant infrastructure (single tenant per environment)
   - Automated scaling (manual scaling via configuration)
   - Usage-based billing (not applicable to self-hosted)

2. **Manual UI-Based Operations**
   - Web dashboard for deployments (CLI/CI only)
   - Drag-and-drop configuration builders (YAML/code only)

3. **Environment Parity Beyond Core Constraints**
   - Byte-identical staging/production hardware (acceptable differences in resource limits)
   - Real-time staging synchronization with production data (snapshot-based only)

---

## User Personas

### 1. Full-Stack Developer (Primary)
**Profile:** Develops Odoo modules and integrations, needs fast feedback loops.

**Use Cases:**
- Start dev environment with hot reload in <5 minutes
- Test module changes without restarting Odoo server
- Preview PR changes in ephemeral environment before review

**Needs:**
- Clear documentation on dev environment setup
- Fast reload times (<3 seconds for code changes)
- Confidence that local dev matches staging/production behavior

### 2. QA/Tester
**Profile:** Validates features in staging before production release.

**Use Cases:**
- Access staging environment for manual testing
- Verify email/cron/integration neutralization
- Compare staging behavior against production

**Needs:**
- Staging environment with production-like data (sanitized)
- Ability to trigger crons manually for testing
- Clear diff between staging and production configurations

### 3. Product Manager
**Profile:** Reviews features in PR environments, approves production releases.

**Use Cases:**
- Access PR preview links from GitHub PR comments
- Review feature implementation before merge
- Track deployment history and rollback if needed

**Needs:**
- Self-service PR environment access (no technical setup)
- Evidence of deployment success/failure
- Clear promotion workflow visibility

### 4. SysAdmin/DevOps
**Profile:** Manages infrastructure, deployment automation, and observability.

**Use Cases:**
- Set up CI/CD pipelines for automated deployments
- Monitor deployment health and performance
- Troubleshoot failed deployments with evidence logs

**Needs:**
- Infrastructure-as-code (Dockerfiles, CI workflows)
- Centralized logging (Supabase `ops.*` tables)
- Rollback procedures with <5 minute execution time

---

## Functional Requirements

### FR1: Developer Hot Reload
**Description:** Local dev environment MUST support hot reload for Python, JavaScript, and CSS changes without full Odoo restart.

**Acceptance Criteria:**
- Python file changes reload modules in <3 seconds (via `--dev=all`)
- JS/CSS changes rebuild assets in <5 seconds (via debug mode)
- Database schema changes trigger automatic migration prompts
- Configuration changes (odoo.conf) require manual restart (documented)

**Dependencies:**
- Odoo 19 `--dev=all` flag support
- Watchdog or similar file change detection
- Asset build toolchain (for JS/CSS)

**Priority:** P0 (critical for developer experience)

---

### FR2: Staging Environment Semantics
**Description:** Staging environment MUST neutralize external interactions (email, crons, integrations) by default.

**Acceptance Criteria:**
- Email sending disabled (`mail.catchall = catchall@localhost` or mailhog)
- Scheduled actions (crons) disabled by default, manual trigger only
- External integrations (Slack, n8n, payment gateways) use test endpoints/keys
- Production secrets NOT accessible in staging (separate `.env` files)
- CI gate MUST verify neutralization configuration before staging deployment

**Dependencies:**
- Odoo configuration templates (`.env.staging`, `odoo.conf.staging`)
- CI validation script for neutralization checks
- Mailhog or equivalent local email capture

**Priority:** P0 (critical for safety)

---

### FR3: PR/Branch Build Automation (Runbot-lite)
**Description:** On PR creation, automatically build and deploy ephemeral environment with unique URL.

**Acceptance Criteria:**
- GitHub Actions workflow triggers on PR open/push
- Ephemeral environment created with URL: `pr-<number>-<slug>.dev.insightpulseai.com`
- Database initialized (copy of staging DB or fresh with demo data)
- PR comment posted with access link and credentials
- Environment torn down automatically on PR close/merge (within 1 hour)

**Dependencies:**
- GitHub Actions runner with Docker support
- DNS wildcard record (`*.dev.insightpulseai.com`)
- Ephemeral database provisioning (PostgreSQL container or Supabase branch)
- Cleanup cron job or workflow for stale environments

**Priority:** P1 (high value, not blocking)

---

### FR4: Promotion Workflow with CI Gates
**Description:** Production promotion MUST pass automated validation gates (tests, security, migration dry-run).

**Acceptance Criteria:**
- CI workflow runs on merge to `main` (staging deployment)
- Production promotion requires manual approval + CI gate passage
- Gates include: unit tests (100% of existing), security scan (no critical/high), migration dry-run (no errors)
- Failed gate blocks production merge and posts PR comment with failure details
- Successful promotion creates immutable deployment record in Supabase `ops.deployments`

**Dependencies:**
- CI workflow definitions (`.github/workflows/staging.yml`, `.github/workflows/production.yml`)
- Test suite (Python unittest, pytest)
- Security scanner (Bandit, Safety)
- Migration dry-run script (`odoo -u <modules> --stop-after-init --test-enable`)

**Priority:** P0 (critical for reliability)

---

### FR5: Observability + Evidence Emission
**Description:** All builds and deployments MUST emit structured evidence to Supabase `ops.*` tables.

**Acceptance Criteria:**
- Build metadata: git SHA, branch, commit message, author, timestamp, dependencies hash
- Deployment metadata: environment, deployed SHA, migration scripts executed, health check results
- Evidence artifacts: full stdout/stderr logs saved to `web/docs/evidence/<YYYYMMDD-HHMM+0800>/<topic>/logs/`
- Supabase tables: `ops.builds`, `ops.deployments`, `ops.migrations`
- Retention: 30 days in Supabase, 90 days in evidence artifacts (compressed)

**Dependencies:**
- Supabase project with `ops.*` schema
- CI workflow steps to emit evidence
- Evidence artifact storage (Git LFS or S3-compatible)

**Priority:** P1 (high value for debugging, not blocking launch)

---

## Acceptance Criteria Summary

**Platform is considered production-ready when:**

1. ✅ Local dev environment starts with hot reload in <5 minutes
2. ✅ Staging environment has email/cron/integration neutralization verified by CI
3. ✅ PR environments auto-deploy with unique URLs and tear down on close
4. ✅ Production promotion requires CI gate passage (tests, security, migration dry-run)
5. ✅ All deployments emit evidence to Supabase `ops.*` tables
6. ✅ Documentation exists for: dev setup, promotion workflow, rollback procedure
7. ✅ Zero production incidents from staging misconfigurations in 30-day period

---

## Out of Scope (Future Enhancements)

- Automated rollback on health check failures (manual rollback only in v1)
- Database migration preview UI (CLI-only in v1)
- Multi-region deployments (single region in v1)
- A/B testing infrastructure (not applicable for internal ERP)
- Automated performance regression detection (manual monitoring in v1)
