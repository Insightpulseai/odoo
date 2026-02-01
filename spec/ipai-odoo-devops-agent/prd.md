# PRD – IPAI Odoo DevOps Agent

**Version**: 1.0.0
**Status**: Spec Phase
**Goal**: Build an agent that mirrors Odoo.sh capabilities using our self-hosted stack

---

## 1. Vision

Replace Odoo.sh dependency with a **self-hosted DevOps agent** that provides:
- Continuous integration for every commit/PR
- Staging environments for branch testing
- Clear logs and debugging tools
- Module dependency management
- Automated backups and recovery
- Mail catching for dev/staging
- Production monitoring and KPIs

**Philosophy**: Build it ourselves → Own the IP → Control the costs (no vendor lock-in)

---

## 2. Odoo.sh Feature Parity Matrix

| Odoo.sh Feature | Agent Skill | Implementation | Status |
|-----------------|-------------|----------------|--------|
| **GitHub Integration** | `github_ci_runner` | GitHub Actions + docker-compose | ⏳ Spec |
| **Clear Logs** | `log_explorer` | docker logs + grep + journalctl | ⏳ Spec |
| **Web Shell** | `shell_proxy` | SSH templates + docker exec | ⏳ Spec |
| **Modules Dependencies** | `module_dependency_resolver` | OCA/ipai manifests + jq | ⏳ Spec |
| **Continuous Integration** | `odoo_runbot_clone` | Ephemeral docker stacks + pytest | ⏳ Spec |
| **Staging Branches** | `staging_promoter` | Branch-based deployments | ⏳ Spec |
| **Backups** | `backup_manager` | pg_dump + DO snapshots | ⏳ Spec |
| **Instant Recovery** | `backup_manager` | pg_restore to staging/dev | ⏳ Spec |
| **Mail Catcher** | `mail_catcher` | Mailgun catch-all + SMTP logs | ⏳ Spec |
| **Monitoring** | `monitoring_analyst` | nginx + DO metrics + n8n | ⏳ Spec |
| **OCA Layout Enforcer** | `oca_ipai_layout_enforcer` | Manifest verification scripts | ✅ Existing |

**Parity Score Target**: ≥90% (10 of 11 features implemented)

---

## 3. Skills (What It Can Do)

### 3.1 GitHub CI Runner
**Purpose**: Run full CI pipeline on every branch/PR

**Workflow**:
1. GitHub webhook triggers on push/PR
2. Spin up ephemeral Odoo stack with branch code
3. Run tests (pytest + odoo --test-enable)
4. Run linting (black, flake8, isort)
5. Verify manifests (OCA compliance)
6. Report pass/fail with logs

**Tools**: `git_cli`, `github_api`, `docker_compose`, `pytest_runner`, `odoo_test_runner`

**Acceptance Criteria**:
- [ ] Every PR shows CI status (green/red)
- [ ] Test failures include log excerpts
- [ ] Manifest errors block merge
- [ ] Execution time <10 minutes

### 3.2 Log Explorer
**Purpose**: Stream and filter logs for debugging

**Capabilities**:
- Docker container logs (odoo-core, nginx, workers)
- Journalctl system logs
- n8n workflow logs
- Grep filtering by pattern/time

**Tools**: `docker_logs`, `journalctl`, `grep`, `n8n_api`

**Acceptance Criteria**:
- [ ] Can fetch last 50 errors for any service
- [ ] Can filter by timestamp and pattern
- [ ] Returns structured log excerpts

### 3.3 Shell Proxy
**Purpose**: Execute controlled shell commands on environments

**Safety Model**:
- Only pre-approved command templates
- No arbitrary shell strings from chat
- Environment-specific whitelists (dev vs prod)

**Tools**: `ssh_client`, `docker_exec`

**Examples**:
```bash
# Template: restart_service
ssh root@178.128.112.214 "docker restart odoo-prod"

# Template: check_db_size
ssh root@178.128.112.214 "docker exec postgres-prod psql -U odoo -c 'SELECT pg_database_size(\'odoo\');'"
```

**Acceptance Criteria**:
- [ ] 10 pre-approved templates defined
- [ ] Commands execute with timeout (max 5 minutes)
- [ ] All output logged to evidence packs

### 3.4 Module Dependency Resolver
**Purpose**: Determine which modules to clone/install for a feature

**Input**: Feature slug or module name
**Output**: Ordered list of dependencies + installation commands

**Algorithm**:
1. Read `config/addons_manifest.oca_ipai.json`
2. Parse `depends` fields for target module
3. Resolve transitive dependencies
4. Check which repos are missing
5. Generate clone + install commands

**Tools**: `filesystem_reader`, `jq`, `python_dep_resolver`

**Acceptance Criteria**:
- [ ] Handles circular dependencies gracefully
- [ ] Detects missing OCA repos
- [ ] Generates idempotent install commands

### 3.5 Odoo Runbot Clone
**Purpose**: Ephemeral branch-based testing stacks

**Workflow**:
1. Receive branch name from GitHub webhook
2. Clone branch into isolated directory
3. Spin up docker-compose stack with test database
4. Run `odoo --test-enable --stop-after-init`
5. Capture results (pass/fail counts)
6. Tear down containers and cleanup

**Tools**: `docker_compose`, `postgres_cli`, `pytest_runner`, `odoo_test_runner`

**Acceptance Criteria**:
- [ ] Each branch gets isolated test DB
- [ ] Containers cleaned up after test
- [ ] Results posted to GitHub PR comments

### 3.6 Staging Promoter
**Purpose**: Deploy feature branches to staging environment

**Environments**:
- **Dev**: `http://localhost:8069` (local developer machines)
- **Staging**: `http://staging.insightpulseai.com` (DO droplet, port 8070)
- **Production**: `http://erp.insightpulseai.com` (DO droplet, port 8069)

**Workflow**:
1. Verify source branch tests passed
2. Build Docker image with branch code
3. Deploy to staging droplet
4. Run health checks (HTTP 200, DB connectivity)
5. Report deployment status

**Tools**: `git_cli`, `docker_compose`, `db_dump_restore`, `nginx_configurator`

**Acceptance Criteria**:
- [ ] Staging uses production-like data (anonymized)
- [ ] Deployment completes in <10 minutes
- [ ] Health checks pass before declaring success

### 3.7 Backup Manager
**Purpose**: Orchestrate database and filestore backups

**Backup Types**:
- **Full**: Complete pg_dump + filestore tar
- **Incremental**: WAL-based continuous archiving
- **On-Demand**: Manual trigger via MCP/CLI

**Schedule**:
- Daily full backups (2 AM SGT)
- Hourly incremental (production only)
- 30-day retention

**Tools**: `postgres_cli`, `do_api`, `cron_configurator`

**Acceptance Criteria**:
- [ ] Backups stored in DO Spaces
- [ ] Restore tested monthly
- [ ] Restore to dev/staging <15 minutes

### 3.8 Mail Catcher
**Purpose**: Intercept outgoing emails in dev/staging

**Implementation**:
- **Dev/Staging**: All emails routed to Mailgun catch-all (`devtest@mg.insightpulseai.com`)
- **Production**: Real delivery to recipients

**API**:
- List recent caught emails
- Fetch email content (HTML + plaintext)
- Search by recipient or subject

**Tools**: `mailgun_api`, `smtp_logs`

**Acceptance Criteria**:
- [ ] Zero emails reach real users from dev/staging
- [ ] Can view last 100 caught emails
- [ ] Email content rendered in readable format

### 3.9 Monitoring Analyst
**Purpose**: Surface KPIs and alerts

**Metrics**:
- **Availability**: Uptime % (production target: 99.5%)
- **Performance**: Request latency P95, P99
- **Errors**: Error rate %, slow query count
- **Queue**: n8n workflow backlog

**Data Sources**:
- nginx access logs
- Odoo health endpoint (`/web/health`)
- DO monitoring API
- n8n API (`/workflows`)

**Tools**: `curl`, `docker_logs`, `do_monitoring_api`, `n8n_api`

**Acceptance Criteria**:
- [ ] Metrics updated every 5 minutes
- [ ] Alerts triggered on thresholds (error rate >5%, uptime <99%)
- [ ] Dashboard accessible via MCP

### 3.10 OCA/ipai Layout Enforcer
**Purpose**: Keep filesystem in sync with manifests

**Checks**:
1. All 19 OCA repos present in `addons/oca/`
2. All repos on correct branch (18.0)
3. No orphaned directories
4. Mount configuration matches `addons.manifest.json`

**Auto-Fix**:
- Run `./scripts/clone_missing_oca_repos.sh` for missing repos
- Run `./scripts/verify_oca_ipai_layout.sh` for verification
- Update `.devcontainer/devcontainer.json` if mounts drift

**Tools**: `bash_scripts`, `filesystem_reader`

**Acceptance Criteria**:
- [ ] Runs daily via cron
- [ ] Auto-fixes common drift issues
- [ ] Reports unresolvable conflicts

---

## 4. Tools (What It's Allowed to Drive)

```yaml
tools:
  - id: git_cli
    commands: [clone, checkout, pull, push, status, diff, log]
    safety: no-force-push-on-protected-branches

  - id: github_api
    endpoints: [repos, pulls, statuses, checks, workflows]
    safety: read-mostly, write-only-on-approved-workflows

  - id: docker_compose
    files: [docker-compose.yml, deploy/docker-compose.yml]
    commands: [up, down, build, logs, ps]
    safety: limit-to-known-compose-files

  - id: docker_logs
    containers: [odoo-core, odoo-prod, nginx, postgres, n8n]

  - id: postgres_cli
    commands: [psql, pg_dump, pg_restore, vacuumdb]
    safety: destructive-commands-via-backup-paths-only

  - id: ssh_client
    hosts: [178.128.112.214]
    safety: templates-only, no-arbitrary-shell

  - id: mailgun_api
    domain: mg.insightpulseai.com
    endpoints: [events, logs, messages]

  - id: n8n_api
    base_url: https://n8n.insightpulseai.com
    endpoints: [workflows, executions, credentials]

  - id: filesystem_reader
    paths: [spec/, config/, addons/, scripts/, docs/]

  - id: bash_scripts
    whitelist:
      - ./scripts/clone_missing_oca_repos.sh
      - ./scripts/verify_oca_ipai_layout.sh
      - ./scripts/verify-addons-mounts.sh
      - ./scripts/deploy_do_prod.sh
      - ./scripts/ci_local.sh
```

---

## 5. Knowledge (What It Knows About Your World)

### 5.1 Static Documentation
- `CLAUDE.md` - Execution contract and secrets policy
- `config/addons_manifest.oca_ipai.json` - OCA repository catalog
- `addons.manifest.json` - Active development mounts
- `QUICK_DEPLOY_DO.md` - Baseline deployment steps
- `PRODUCTION_DEPLOYMENT_DO.md` - Full production runbook
- `DIGITALOCEAN_MCP_INTEGRATION.md` - MCP integration guide
- `N8N_INTEGRATION_GUIDE.md` - Workflow orchestration
- `ODOO_19_AI_INTEGRATION.md` - AI agent architecture

### 5.2 Runtime Facts
```yaml
infrastructure:
  prod_droplet: 178.128.112.214
  prod_db_cluster: odoo-db-sgp1 (PostgreSQL 16, DO)
  mail_domain: mg.insightpulseai.com
  n8n_url: https://n8n.insightpulseai.com/

repositories:
  odoo_dev: ~/Documents/GitHub/odoo-ce
  prismaconsulting: /opt/Prismaconsulting  # on droplet

databases:
  dev: odoo_dev
  test: oca_test
  staging: odoo_staging
  production: odoo
```

### 5.3 Conventions
- OCA repos must be on branch `18.0`
- All custom modules use `ipai_` prefix
- Evidence packs: `docs/evidence/YYYYMMDD-HHMM/<scope>/`
- Commits follow: `feat|fix|chore(scope): description`

---

## 6. Operating Modes

### 6.1 CI Guard Mode
**Trigger**: GitHub push/PR events
**Action**: Validate manifests, run tests, block merge on failure
**Output**: GitHub status check (success/failure)

### 6.2 Ops Surgeon Mode
**Trigger**: Manual MCP call or Control Room orchestration
**Action**: Diagnose/fix production issues on demand
**Output**: Diagnosis report + fix applied + evidence pack

### 6.3 Manifest Steward Mode
**Trigger**: Daily cron (2 AM SGT)
**Action**: Verify OCA/ipai layout, clone missing repos, update mounts
**Output**: Verification report + auto-fix summary

---

## 7. Success Metrics

### 7.1 Feature Parity
- **Target**: 90% Odoo.sh feature coverage
- **Current**: 10% (OCA layout enforcer only)
- **Milestone 1**: 50% (CI + logs + shell + deps)
- **Milestone 2**: 90% (all features except advanced monitoring)

### 7.2 Operational KPIs
- **CI Reliability**: 99% test runs complete successfully
- **Deployment Speed**: <15 minutes for production deploy
- **Backup Success Rate**: 100% daily backups complete
- **Uptime**: 99.5% production availability

### 7.3 Developer Experience
- **PR Feedback Time**: <10 minutes for CI results
- **Log Access Time**: <30 seconds to fetch relevant logs
- **Staging Deploy Time**: <10 minutes from request to ready

---

## 8. Non-Goals (Out of Scope)

- ❌ Direct Odoo module development (use `odoo_developer` agent)
- ❌ Custom n8n workflow creation (use existing templates)
- ❌ Database schema design (use `database-architect` agent)
- ❌ BI dashboard creation (use `bi_architect` agent)
- ❌ User training or documentation writing
- ❌ Business logic implementation

---

## 9. Dependencies

**Required for Implementation**:
- [ ] GitHub Actions runner (self-hosted on DO droplet)
- [ ] MCP server for agent communication
- [ ] Mailgun API access (existing: `mg.insightpulseai.com`)
- [ ] DigitalOcean API token (existing: `DO_ACCESS_TOKEN`)
- [ ] PostgreSQL access (existing: DO managed cluster)
- [ ] n8n API access (existing: `N8N_API_KEY`)

**Existing Assets to Leverage**:
- ✅ OCA/ipai manifest system (19 repos, 80+ modules)
- ✅ Verification scripts (`verify_oca_ipai_layout.sh`, `clone_missing_oca_repos.sh`)
- ✅ Deployment runbooks (`QUICK_DEPLOY_DO.md`, `PRODUCTION_DEPLOYMENT_DO.md`)
- ✅ Docker compose configurations
- ✅ CLAUDE.md secrets policy

---

## 10. Rollout Plan

### Phase 1: Foundation (Week 1-2)
- [ ] CI Guard Mode implementation
- [ ] Log Explorer basic functionality
- [ ] Shell Proxy with 5 templates
- [ ] Evidence pack automation

### Phase 2: Core Features (Week 3-4)
- [ ] Module Dependency Resolver
- [ ] Odoo Runbot Clone
- [ ] Staging Promoter
- [ ] Backup Manager (backup only)

### Phase 3: Polish (Week 5-6)
- [ ] Mail Catcher integration
- [ ] Monitoring Analyst dashboard
- [ ] Backup Manager (restore + testing)
- [ ] Full MCP integration

### Phase 4: Production (Week 7-8)
- [ ] Production deployment
- [ ] 30-day monitoring period
- [ ] Performance tuning
- [ ] Documentation finalization

---

**Last Updated**: 2026-01-29
**Next**: Implementation plan with task breakdown
