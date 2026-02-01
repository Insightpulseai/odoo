# Implementation Plan – IPAI Odoo DevOps Agent

**Version**: 1.0.0
**Target**: 8-week rollout to production
**Parity Goal**: 90% Odoo.sh feature coverage

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                  IPAI Odoo DevOps Agent                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │  CI Guard    │  │ Ops Surgeon  │  │   Manifest   │          │
│  │    Mode      │  │    Mode      │  │   Steward    │          │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘          │
│         │                  │                  │                  │
│         └──────────────────┴──────────────────┘                  │
│                            │                                     │
│                   ┌────────▼────────┐                            │
│                   │  Skill Router   │                            │
│                   └────────┬────────┘                            │
│                            │                                     │
│     ┌──────────────────────┼──────────────────────┐             │
│     │                      │                      │             │
│  ┌──▼───┐  ┌────▼─────┐  ┌▼─────┐  ┌──────▼────┐  ┌─▼──────┐  │
│  │ CI   │  │  Logs    │  │Shell │  │   Deps    │  │Backup  │  │
│  │Runner│  │ Explorer │  │Proxy │  │ Resolver  │  │Manager │  │
│  └──┬───┘  └────┬─────┘  └┬─────┘  └──────┬────┘  └─┬──────┘  │
│     │           │          │               │          │         │
│     └───────────┴──────────┴───────────────┴──────────┘         │
│                            │                                     │
│                   ┌────────▼────────┐                            │
│                   │   Tool Layer    │                            │
│                   └────────┬────────┘                            │
│                            │                                     │
│  ┌─────────────────────────┼─────────────────────────┐          │
│  │                         │                         │          │
│  ▼                         ▼                         ▼          │
│ Git/GitHub        Docker/Postgres          Mailgun/n8n         │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Phase 1: Foundation (Weeks 1-2)

### Milestone: "Can run CI on every PR"

#### 1.1 Project Setup
**Duration**: 2 days

**Tasks**:
- [ ] Create agent directory: `apps/devops-agent/`
- [ ] Setup Python project structure:
  ```
  apps/devops-agent/
  ├── src/
  │   ├── skills/          # 10 skill implementations
  │   ├── tools/           # Tool wrappers
  │   ├── modes/           # 3 operating modes
  │   └── core/            # Router, config, utils
  ├── tests/
  ├── pyproject.toml
  └── README.md
  ```
- [ ] Install dependencies: `click`, `pyyaml`, `requests`, `docker`, `psycopg2`
- [ ] Setup MCP server integration (coordinate with `mcp-coordinator`)

**Acceptance Criteria**:
- Python package installable via `pip install -e .`
- Can import `from devops_agent import skills, tools, modes`
- Basic CLI works: `devops-agent --help`

#### 1.2 Tool Layer Implementation
**Duration**: 3 days

**Tools to Implement**:
1. **git_cli**:
   ```python
   # src/tools/git.py
   class GitTool:
       def clone(repo_url, target_dir, branch=None):
           # Safety: validate repo_url against whitelist
       def checkout(branch):
           # Safety: no force checkout on protected branches
   ```

2. **github_api**:
   ```python
   # src/tools/github.py
   class GitHubTool:
       def get_pr(repo, pr_number):
       def post_status(commit_sha, state, description):
       def create_comment(pr_number, body):
   ```

3. **docker_compose**:
   ```python
   # src/tools/docker.py
   class DockerComposeTool:
       def up(compose_file, services=None):
       def down(compose_file):
       def logs(service_name, tail=50):
   ```

**Acceptance Criteria**:
- All tools have safety checks (whitelist validation)
- All tools return structured results (not raw shell output)
- Unit tests cover error cases (missing repos, auth failures)

#### 1.3 GitHub CI Runner (Skill #1)
**Duration**: 4 days

**Implementation**:
```python
# src/skills/github_ci_runner.py
class GitHubCIRunner:
    def run(repo_slug, branch_or_pr):
        # 1. Clone repo + checkout branch
        # 2. Detect project type (Odoo module, Python package)
        # 3. Spin up test environment (docker-compose)
        # 4. Run tests (pytest or odoo --test-enable)
        # 5. Collect results
        # 6. Post status to GitHub
        # 7. Teardown environment
        return {
            'status': 'success|failure',
            'summary': 'X tests passed, Y failed',
            'log_links': [...]
        }
```

**GitHub Actions Workflow**:
```yaml
# .github/workflows/devops-agent-ci.yml
name: IPAI DevOps Agent CI
on: [push, pull_request]
jobs:
  test:
    runs-on: self-hosted  # DO droplet
    steps:
      - uses: actions/checkout@v4
      - name: Run DevOps Agent CI
        run: |
          devops-agent skill run github_ci_runner \
            --repo ${{ github.repository }} \
            --pr ${{ github.event.pull_request.number }}
```

**Acceptance Criteria**:
- [ ] CI runs on every push/PR
- [ ] Results posted to GitHub (green check or red X)
- [ ] Failed tests show log excerpts in PR comments
- [ ] Execution time <10 minutes for typical PR

#### 1.4 Evidence Pack Automation
**Duration**: 2 days

**Implementation**:
```python
# src/core/evidence.py
class EvidencePack:
    def __init__(scope):
        timestamp = datetime.now().strftime('%Y%m%d-%H%M')
        self.path = f"docs/evidence/{timestamp}/{scope}/"
        os.makedirs(self.path, exist_ok=True)

    def add_git_state():
        # Capture: branch, SHA, diffstat

    def add_runtime_proof():
        # Capture: health checks, container status, logs

    def add_verification_results():
        # Capture: test results, gate pass/fail

    def finalize():
        # Create SUMMARY.md with all evidence
```

**Acceptance Criteria**:
- All skills automatically create evidence packs
- Evidence includes git state, runtime proof, verification
- Evidence committed alongside code changes

---

## Phase 2: Core Features (Weeks 3-4)

### Milestone: "Can deploy to staging and debug issues"

#### 2.1 Log Explorer (Skill #2)
**Duration**: 3 days

**Implementation**:
```python
# src/skills/log_explorer.py
class LogExplorer:
    def explore(service_name, filter_pattern=None, timeframe='1h'):
        # 1. Identify log source (docker logs, journalctl, n8n API)
        # 2. Fetch logs with filtering
        # 3. Parse and structure (timestamp, level, message)
        # 4. Return top N errors or matching lines
        return {
            'log_excerpt': [...],
            'error_summary': '5 errors in last hour'
        }
```

**CLI Interface**:
```bash
# Fetch last 50 errors from odoo-prod
devops-agent logs odoo-prod --errors --tail 50

# Search for "timeout" in last 1 hour
devops-agent logs nginx --grep "timeout" --since 1h
```

**Acceptance Criteria**:
- Can fetch logs from Docker containers, journalctl, n8n
- Supports filtering by pattern, time, log level
- Returns structured output (JSON or human-readable)

#### 2.2 Shell Proxy (Skill #3)
**Duration**: 2 days

**Template System**:
```yaml
# config/shell_templates.yml
templates:
  restart_service:
    command: "docker restart {service_name}"
    params: [service_name]
    allowed_values:
      service_name: [odoo-prod, nginx, postgres-prod, n8n]

  check_db_size:
    command: "docker exec postgres-prod psql -U odoo -c 'SELECT pg_database_size(\\'{db_name}\\');'"
    params: [db_name]
    allowed_values:
      db_name: [odoo, odoo_staging, oca_test]
```

**Implementation**:
```python
# src/skills/shell_proxy.py
class ShellProxy:
    def execute(template_id, params, target_env):
        # 1. Load template from config
        # 2. Validate params against allowed values
        # 3. Render command (no arbitrary strings!)
        # 4. Execute via SSH or docker exec
        # 5. Capture output with timeout
        return {
            'stdout': ...,
            'stderr': ...,
            'exit_code': ...
        }
```

**Acceptance Criteria**:
- [ ] 10 pre-approved templates defined
- [ ] Cannot execute arbitrary shell commands
- [ ] All executions logged to evidence packs
- [ ] Timeout enforced (max 5 minutes)

#### 2.3 Module Dependency Resolver (Skill #4)
**Duration**: 3 days

**Algorithm**:
```python
# src/skills/module_dependency_resolver.py
class ModuleDependencyResolver:
    def resolve(feature_slug_or_module):
        # 1. Read config/addons_manifest.oca_ipai.json
        # 2. Find target module in manifest
        # 3. Parse 'depends' field
        # 4. Recursively resolve dependencies
        # 5. Topological sort for installation order
        # 6. Check which repos are missing
        # 7. Generate clone + install commands
        return {
            'ordered_module_list': [...],
            'missing_repos': [...],
            'commands_to_install': [...]
        }
```

**CLI Interface**:
```bash
# Resolve dependencies for ipai_finance_ppm
devops-agent deps resolve ipai_finance_ppm

# Output:
# Missing repos: server-env, account-reconcile
# Run: ./scripts/clone_missing_oca_repos.sh
# Install order:
#   1. base_tier_validation
#   2. date_range
#   3. ipai_finance_ppm
# Command: odoo -d odoo -i base_tier_validation,date_range,ipai_finance_ppm
```

**Acceptance Criteria**:
- Handles circular dependencies gracefully
- Detects missing OCA repos
- Generates idempotent install commands

#### 2.4 Staging Promoter (Skill #6)
**Duration**: 4 days

**Deployment Workflow**:
```python
# src/skills/staging_promoter.py
class StagingPromoter:
    def promote(source_branch, staging_env_id='staging'):
        # 1. Verify source branch tests passed
        # 2. Build Docker image with branch code
        # 3. SSH to staging droplet
        # 4. Pull new image
        # 5. docker-compose up -d (recreate containers)
        # 6. Run health checks (HTTP 200, DB connectivity)
        # 7. Report deployment status
        return {
            'deploy_status': 'success|failure',
            'health_checks': {...}
        }
```

**Health Checks**:
```python
def run_health_checks():
    checks = {
        'http': requests.get('http://staging.insightpulseai.com:8070/web/health'),
        'db': psycopg2.connect(STAGING_DB_URL),
        'workers': docker_ps('odoo-staging-worker'),
    }
    return all(c.status == 'ok' for c in checks)
```

**Acceptance Criteria**:
- Deployment completes in <10 minutes
- Health checks pass before declaring success
- Rollback triggered if health checks fail

---

## Phase 3: Polish (Weeks 5-6)

### Milestone: "Production-ready with monitoring"

#### 3.1 Backup Manager (Skill #7)
**Duration**: 4 days

**Backup Implementation**:
```python
# src/skills/backup_manager.py
class BackupManager:
    def backup(db_name, backup_type='full'):
        # 1. pg_dump with compression
        # 2. Tar filestore if full backup
        # 3. Upload to DO Spaces
        # 4. Verify backup integrity
        # 5. Update backup metadata table
        return {
            'backup_snapshot_id': ...,
            'size': ...,
            'location': ...
        }

    def restore(backup_id, target_env):
        # 1. Fetch backup from DO Spaces
        # 2. Create target database
        # 3. pg_restore
        # 4. Restore filestore
        # 5. Run health checks
        return {
            'restore_status': 'success|failure'
        }
```

**Cron Schedule**:
```yaml
# cron: 0 2 * * * (daily at 2 AM SGT)
backups:
  production:
    type: full
    retention: 30 days
  staging:
    type: full
    retention: 7 days
```

**Acceptance Criteria**:
- Daily backups complete successfully
- Restore tested monthly
- Restore to dev/staging <15 minutes

#### 3.2 Mail Catcher (Skill #8)
**Duration**: 2 days

**Implementation**:
```python
# src/skills/mail_catcher.py
class MailCatcher:
    def list_mails(env, filter=None):
        # 1. Query Mailgun API for devtest@mg.insightpulseai.com
        # 2. Filter by recipient or subject
        # 3. Return recent mails (last 100)
        return {
            'mail_list': [
                {'from': ..., 'to': ..., 'subject': ..., 'timestamp': ...}
            ]
        }

    def get_mail(mail_id):
        # Fetch full email content (HTML + plaintext)
        return {
            'html': ...,
            'plaintext': ...,
            'attachments': [...]
        }
```

**Odoo Configuration**:
```ini
# Development/Staging odoo.conf
[options]
smtp_server = smtp.mailgun.org
smtp_port = 587
smtp_user = postmaster@mg.insightpulseai.com
smtp_password = ${MAILGUN_SMTP_PASSWORD}
email_from = devtest@mg.insightpulseai.com
```

**Acceptance Criteria**:
- Zero emails reach real users from dev/staging
- Can view last 100 caught emails via CLI
- Email content rendered properly

#### 3.3 Monitoring Analyst (Skill #9)
**Duration**: 4 days

**Metrics Collection**:
```python
# src/skills/monitoring_analyst.py
class MonitoringAnalyst:
    def collect_metrics(env, timeframe='1h'):
        metrics = {
            'availability': self._check_uptime(),
            'performance': self._get_latency_percentiles(),
            'errors': self._count_errors(),
            'queue': self._check_n8n_backlog()
        }
        return metrics

    def _check_uptime():
        # Query DO monitoring API
        # Check nginx access logs
        return uptime_percentage

    def _get_latency_percentiles():
        # Parse nginx logs
        # Calculate P95, P99 request times
        return {'p95': ..., 'p99': ...}
```

**Dashboard** (MCP-exposed):
```python
@mcp_tool
def get_kpi_summary():
    return {
        'production': {
            'uptime': '99.8%',
            'error_rate': '0.3%',
            'latency_p95': '180ms',
            'queue_backlog': 3
        }
    }
```

**Acceptance Criteria**:
- Metrics updated every 5 minutes
- Alerts triggered on thresholds
- Dashboard accessible via MCP

#### 3.4 Full MCP Integration
**Duration**: 3 days

**MCP Server**:
```python
# mcp/servers/devops-agent/server.py
from mcp import MCPServer

server = MCPServer("devops-agent")

@server.tool()
def run_skill(skill_id: str, params: dict):
    """Execute a DevOps agent skill"""
    from devops_agent.core import SkillRouter
    router = SkillRouter()
    return router.execute(skill_id, params)

@server.tool()
def get_logs(service: str, filter: str = None):
    """Get logs from a service"""
    from devops_agent.skills import LogExplorer
    explorer = LogExplorer()
    return explorer.explore(service, filter)
```

**Acceptance Criteria**:
- All skills exposed via MCP
- Control Room can invoke agent via MCP
- Agent reports status updates to Control Room

---

## Phase 4: Production (Weeks 7-8)

### Milestone: "Live in production with 30-day monitoring"

#### 4.1 Production Deployment
**Duration**: 2 days

**Deployment Checklist**:
- [ ] All skills passing tests (100% coverage)
- [ ] MCP server deployed and accessible
- [ ] GitHub Actions workflows configured
- [ ] Cron jobs scheduled (backups, manifest steward)
- [ ] Monitoring dashboards live
- [ ] Runbooks updated

**Deployment Steps**:
1. Deploy MCP server to DO droplet
2. Configure GitHub webhook to agent endpoint
3. Enable cron jobs for manifest steward
4. Update Control Room integration
5. Monitor first 24 hours continuously

#### 4.2 30-Day Monitoring Period
**Duration**: 30 days

**Success Metrics**:
- CI reliability: 99% test runs complete
- Deployment speed: <15 minutes average
- Backup success rate: 100%
- Production uptime: ≥99.5%

**Weekly Reviews**:
- Review error logs and failures
- Tune alert thresholds
- Optimize slow operations
- Document common issues

#### 4.3 Documentation Finalization
**Duration**: 3 days

**Deliverables**:
- [ ] README.md with quick start guide
- [ ] SKILLS.md with complete skill reference
- [ ] TOOLS.md with tool API documentation
- [ ] RUNBOOKS.md for common operations
- [ ] TROUBLESHOOTING.md for known issues

---

## File Structure

```
apps/devops-agent/
├── src/
│   ├── skills/
│   │   ├── __init__.py
│   │   ├── github_ci_runner.py
│   │   ├── log_explorer.py
│   │   ├── shell_proxy.py
│   │   ├── module_dependency_resolver.py
│   │   ├── odoo_runbot_clone.py
│   │   ├── staging_promoter.py
│   │   ├── backup_manager.py
│   │   ├── mail_catcher.py
│   │   ├── monitoring_analyst.py
│   │   └── oca_ipai_layout_enforcer.py
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── git.py
│   │   ├── github.py
│   │   ├── docker.py
│   │   ├── postgres.py
│   │   ├── ssh.py
│   │   ├── mailgun.py
│   │   ├── n8n.py
│   │   └── filesystem.py
│   ├── modes/
│   │   ├── __init__.py
│   │   ├── ci_guard.py
│   │   ├── ops_surgeon.py
│   │   └── manifest_steward.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── router.py
│   │   ├── config.py
│   │   ├── evidence.py
│   │   └── utils.py
│   └── cli.py
├── tests/
│   ├── test_skills/
│   ├── test_tools/
│   └── test_modes/
├── config/
│   ├── shell_templates.yml
│   └── agent.yml
├── pyproject.toml
├── README.md
└── SKILLS.md
```

---

## Risk Mitigation

### Technical Risks

**Risk**: Docker container resource exhaustion
**Mitigation**:
- Set memory limits in compose files
- Monitor resource usage via DO API
- Auto-scale workers if needed

**Risk**: GitHub Actions runner downtime
**Mitigation**:
- Deploy 2 self-hosted runners (primary + backup)
- Fallback to GitHub cloud runners if self-hosted fails

**Risk**: Backup failures
**Mitigation**:
- Daily verification of backup integrity
- Test restore monthly
- Alert on backup failure

### Operational Risks

**Risk**: Production deployment breaks site
**Mitigation**:
- Require staging deploy + 24h soak before prod
- Auto-rollback on health check failures
- Keep last 3 production images for rollback

**Risk**: Agent makes destructive changes
**Mitigation**:
- All destructive ops require backup verification
- Shell proxy only uses pre-approved templates
- Evidence packs track all changes

---

## Dependencies

**Required Before Start**:
- [ ] Self-hosted GitHub Actions runner on DO droplet
- [ ] MCP coordinator deployed and accessible
- [ ] Mailgun API access configured
- [ ] DO API token with full permissions
- [ ] PostgreSQL access configured

**Nice to Have**:
- Grafana/Prometheus for metrics visualization
- Slack integration for alerts
- Monthly backup restore tests

---

**Last Updated**: 2026-01-29
**Next**: Task breakdown with assignments
