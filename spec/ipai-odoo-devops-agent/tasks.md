# Tasks – IPAI Odoo DevOps Agent

**Version**: 1.0.0
**Status**: Spec Phase → Implementation
**Tracking**: This file tracks concrete, actionable tasks mapped to PRs

---

## Task Status Legend

- `⏳ Spec` - Task defined in spec, not started
- `🚧 In Progress` - Currently being implemented
- `✅ Complete` - Implemented, tested, merged
- `❌ Blocked` - Cannot proceed (dependency or external blocker)
- `⚠️ On Hold` - Deprioritized or waiting for decision

---

## Phase 0: Bootstrapping

**Goal**: Establish spec and policy foundations

### T0.1 - Create Spec Kit Directory
**Status**: ✅ Complete
**Owner**: Claude
**Description**: Create `spec/ipai-odoo-devops-agent/` with all four files

**Files**:
- [x] constitution.md
- [x] prd.md
- [x] plan.md
- [x] tasks.md (this file)

**Acceptance**:
- All spec files present and valid markdown
- Spec Kit listed in root `spec/` directory

### T0.2 - Ensure CLAUDE.md Present
**Status**: ✅ Complete
**Owner**: Claude
**Description**: Verify `CLAUDE.md` exists at repo root with section 2 (Secrets & Tokens Policy)

**Verification**:
```bash
grep -A 5 "Secrets & Tokens Policy" CLAUDE.md
```

**Acceptance**:
- CLAUDE.md section 2 exists
- References no-token-chatter rule
- Documents env-driven configuration

### T0.3 - Add CI Validation for Spec Kit
**Status**: ⏳ Spec
**Owner**: TBD
**PR**: #TBD
**Description**: Create GitHub Actions workflow to validate spec bundle integrity

**Workflow**: `.github/workflows/spec-kit-validate.yml`
```yaml
name: Spec Kit Validation
on: [push, pull_request]
jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Validate Spec Kit
        run: |
          ./scripts/validate_spec_kits.sh
```

**Acceptance**:
- CI fails if any spec file missing
- CI passes for valid spec bundles

---

## Phase 1: Manifest & Layout Enforcement

**Goal**: Automated OCA/ipai manifest verification

### T1.1 - Validate Manifest JSON Files
**Status**: ✅ Complete
**Owner**: Claude
**Description**: Confirm manifests are valid JSON

**Files**:
- [x] config/addons_manifest.oca_ipai.json (19 repos, 80+ modules)
- [x] addons.manifest.json (active mounts)

**Verification**:
```bash
jq '.' config/addons_manifest.oca_ipai.json > /dev/null
jq '.' addons.manifest.json > /dev/null
```

### T1.2 - Verify Verification Scripts Exist
**Status**: ✅ Complete
**Owner**: Claude
**Description**: Confirm executable scripts present

**Scripts**:
- [x] scripts/clone_missing_oca_repos.sh
- [x] scripts/verify_oca_ipai_layout.sh
- [x] scripts/verify-addons-mounts.sh

**Verification**:
```bash
test -x scripts/clone_missing_oca_repos.sh
test -x scripts/verify_oca_ipai_layout.sh
test -x scripts/verify-addons-mounts.sh
```

### T1.3 - Create Manifest Verification Workflow
**Status**: ⏳ Spec
**Owner**: TBD
**PR**: #TBD
**Description**: GitHub Actions workflow for manifest verification

**Workflow**: `.github/workflows/verify-oca-ipai-manifest.yml`
**Steps**:
1. Run `./scripts/verify_oca_ipai_layout.sh`
2. Run `./scripts/verify-addons-mounts.sh --verbose`
3. Fail CI if verification fails

**Acceptance**:
- Workflow runs on push/PR
- Blocks merge if manifest broken
- Outputs clear error messages

### T1.4 - Add Evidence Generation
**Status**: ⏳ Spec
**Owner**: TBD
**PR**: #TBD
**Description**: Auto-generate evidence docs for manifest state

**Implementation**:
```python
# scripts/generate_manifest_evidence.py
def generate_evidence():
    timestamp = datetime.now().strftime('%Y%m%d-%H%M')
    evidence_dir = f"docs/evidence/{timestamp}/oca-ipai-manifest/"
    os.makedirs(evidence_dir, exist_ok=True)

    # Run verification
    result = subprocess.run(['./scripts/verify_oca_ipai_layout.sh'])

    # Write evidence
    with open(f"{evidence_dir}/VERIFICATION.md", 'w') as f:
        f.write(f"# Manifest Verification\n\n")
        f.write(f"**Timestamp**: {timestamp}\n")
        f.write(f"**Status**: {'✅ PASS' if result.returncode == 0 else '❌ FAIL'}\n")
```

**Acceptance**:
- Evidence generated after each verification
- Evidence committed to repo
- Evidence readable and traceable

---

## Phase 2: CI Guard (GitHub Checks)

**Goal**: Odoo.sh-like CI for PRs and pushes

### T2.1 - Create odoo-ce CI Workflow
**Status**: ⏳ Spec
**Owner**: TBD
**PR**: #TBD
**Description**: GitHub Actions for Odoo CE testing

**Workflow**: `.github/workflows/odoo-ce-ci.yml`
**Steps**:
1. Checkout code
2. Run manifest verification
3. Build Odoo docker image
4. Run tests: `odoo --test-enable --stop-after-init`
5. Upload logs as artifacts

**Test Scope**:
- Core Odoo modules
- ipai_* custom modules
- High-priority OCA modules (server-tools, web, reporting-engine)

**Acceptance**:
- Tests complete in <15 minutes
- Failed tests show clear error messages
- Logs uploaded for debugging

### T2.2 - Create Prismaconsulting CI Workflow
**Status**: ⏳ Spec
**Owner**: TBD
**PR**: #TBD
**Description**: GitHub Actions for Prismaconsulting stack

**Workflow**: `.github/workflows/prismaconsulting-ci.yml`
**Steps**:
1. Checkout code
2. Build Odoo 19 + website + n8n containers
3. Run health checks (HTTP 200 endpoints)
4. Run smoke tests (basic Odoo operations)

**Acceptance**:
- All containers build successfully
- Health endpoints return 200
- Smoke tests pass

### T2.3 - Configure PR Required Checks
**Status**: ⏳ Spec
**Owner**: TBD
**PR**: #TBD
**Description**: GitHub branch protection requiring CI green

**Settings**:
- odoo-ce main branch: require `Odoo CE CI` check
- Prismaconsulting main branch: require `Prismaconsulting CI` check

**Acceptance**:
- Cannot merge PR with failing CI
- Clear UI indication of required checks

---

## Phase 3: Deploy & Rollback Flows

**Goal**: Scripted, reproducible production deployments

### T3.1 - Standardize deploy_do_prod.sh
**Status**: ⏳ Spec
**Owner**: TBD
**PR**: #TBD
**Location**: `scripts/deploy_do_prod.sh`

**Implementation**:
```bash
#!/bin/bash
set -euo pipefail

# 1. Pre-flight checks
echo "🔍 Pre-flight checks..."
test -f .env.prod || { echo "❌ .env.prod not found"; exit 1; }
ssh root@178.128.112.214 "docker --version" || { echo "❌ Cannot SSH to droplet"; exit 1; }

# 2. Pull latest code
echo "📥 Pulling latest code..."
git pull origin main

# 3. Build containers
echo "🔨 Building containers..."
docker-compose -f deploy/docker-compose.yml build

# 4. Deploy
echo "🚀 Deploying..."
docker-compose -f deploy/docker-compose.yml up -d

# 5. Health checks
echo "🏥 Running health checks..."
./scripts/verify_production.sh

echo "✅ Deployment complete"
```

**Acceptance**:
- Single-command deploy: `./scripts/deploy_do_prod.sh`
- Fails fast on errors
- Runs health checks before declaring success

### T3.2 - Implement setup_ssl.sh
**Status**: ⏳ Spec
**Owner**: TBD
**PR**: #TBD
**Location**: `scripts/setup_ssl.sh`

**Implementation**:
```bash
#!/bin/bash
set -euo pipefail

DOMAIN=${1:-erp.insightpulseai.net}

echo "🔒 Setting up SSL for $DOMAIN..."

# Install certbot
ssh root@178.128.112.214 "apt-get update && apt-get install -y certbot python3-certbot-nginx"

# Generate certificate
ssh root@178.128.112.214 "certbot --nginx -d $DOMAIN --non-interactive --agree-tos -m business@insightpulseai.com"

# Verify renewal
ssh root@178.128.112.214 "certbot renew --dry-run"

echo "✅ SSL setup complete for $DOMAIN"
```

**Acceptance**:
- SSL certificate generated
- Auto-renewal configured
- nginx configured with SSL

### T3.3 - Implement verify_production.sh
**Status**: ⏳ Spec
**Owner**: TBD
**PR**: #TBD
**Location**: `scripts/verify_production.sh`

**Implementation**:
```bash
#!/bin/bash
set -euo pipefail

PROD_URL="http://178.128.112.214:8069"
N8N_URL="https://n8n.insightpulseai.net"

echo "🏥 Running production health checks..."

# Odoo health
curl -sf "$PROD_URL/web/health" | grep -q "pass" || { echo "❌ Odoo health check failed"; exit 1; }
echo "✅ Odoo: healthy"

# n8n health
curl -sf "$N8N_URL" > /dev/null || { echo "❌ n8n unreachable"; exit 1; }
echo "✅ n8n: reachable"

# Database connectivity
ssh root@178.128.112.214 "docker exec postgres-prod psql -U odoo -c 'SELECT 1'" > /dev/null || { echo "❌ DB connection failed"; exit 1; }
echo "✅ Database: connected"

# nginx status
ssh root@178.128.112.214 "systemctl is-active nginx" | grep -q "active" || { echo "❌ nginx not running"; exit 1; }
echo "✅ nginx: running"

echo "✅ All health checks passed"
```

**Acceptance**:
- Checks Odoo, n8n, DB, nginx
- Clear pass/fail output
- Exit code 0 for success, non-zero for failure

### T3.4 - Implement rollback_to_sha.sh
**Status**: ⏳ Spec
**Owner**: TBD
**PR**: #TBD
**Location**: `scripts/rollback_to_sha.sh`

**Implementation**:
```bash
#!/bin/bash
set -euo pipefail

TARGET_SHA=${1:?Usage: rollback_to_sha.sh <sha>}

echo "⏪ Rolling back to $TARGET_SHA..."

# Verify SHA exists
git rev-parse --verify "$TARGET_SHA" > /dev/null || { echo "❌ Invalid SHA"; exit 1; }

# Checkout target
git checkout "$TARGET_SHA"

# Rebuild and deploy
./scripts/deploy_do_prod.sh

echo "✅ Rollback complete to $TARGET_SHA"
```

**Acceptance**:
- Can rollback to any valid commit SHA
- Runs full deploy after checkout
- Logs rollback in evidence pack

### T3.5 - Document Deployment Runbook
**Status**: ⏳ Spec
**Owner**: TBD
**PR**: #TBD
**Location**: `docs/DEPLOYMENT_RUNBOOK.md`

**Sections**:
1. Pre-deployment checklist
2. Production deploy steps
3. Rollback procedure
4. Common issues and fixes
5. Emergency contacts

**Acceptance**:
- Runbook covers all scenarios
- Clear step-by-step instructions
- Tested by non-expert following docs

---

## Phase 4: Monitoring, Backups, Mail

**Goal**: Operational visibility and recovery

### T4.1 - Implement check_all_services.sh
**Status**: ⏳ Spec
**Owner**: TBD
**PR**: #TBD
**Location**: `scripts/health/check_all_services.sh`

**Implementation**:
```bash
#!/bin/bash
# Wrapper that calls verify_production.sh + additional checks

./scripts/verify_production.sh

# Additional checks
echo "📊 Checking metrics..."

# Queue backlog
QUEUE_COUNT=$(curl -s "$N8N_URL/api/v1/executions" | jq '.data | length')
echo "n8n queue: $QUEUE_COUNT executions"

# Disk space
ssh root@178.128.112.214 "df -h / | tail -1" | awk '{print "Disk usage: " $5}'

# Docker containers
ssh root@178.128.112.214 "docker ps --format 'table {{.Names}}\t{{.Status}}'"
```

**Acceptance**:
- Comprehensive service status
- Metrics included (queue, disk, containers)
- Output parseable for dashboards

### T4.2 - Implement Backup Scripts
**Status**: ⏳ Spec
**Owner**: TBD
**PR**: #TBD
**Locations**:
- `scripts/backup/backup_db.sh`
- `scripts/backup/restore_db.sh`

**backup_db.sh**:
```bash
#!/bin/bash
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
BACKUP_FILE="odoo_backup_$TIMESTAMP.sql.gz"

ssh root@178.128.112.214 "docker exec postgres-prod pg_dump -U odoo odoo | gzip > /backups/$BACKUP_FILE"

echo "✅ Backup created: $BACKUP_FILE"
```

**restore_db.sh**:
```bash
#!/bin/bash
BACKUP_FILE=${1:?Usage: restore_db.sh <backup_file> <target_db>}
TARGET_DB=${2:-odoo_staging}

ssh root@178.128.112.214 "gunzip < /backups/$BACKUP_FILE | docker exec -i postgres-prod psql -U odoo -d $TARGET_DB"

echo "✅ Restored $BACKUP_FILE to $TARGET_DB"
```

**Acceptance**:
- Daily cron backups (2 AM SGT)
- 30-day retention policy
- Restore tested monthly

### T4.3 - Configure Mail Catcher
**Status**: ⏳ Spec
**Owner**: TBD
**PR**: #TBD
**Description**: Ensure dev/staging mail goes to catch-all

**Odoo Config** (dev/staging):
```ini
[options]
smtp_server = smtp.mailgun.org
smtp_port = 587
smtp_user = postmaster@mg.insightpulseai.net
smtp_password = ${MAILGUN_SMTP_PASSWORD}
email_from = devtest@mg.insightpulseai.net
```

**Inspection Script**: `scripts/mail/inspect_caught_mail.sh`
```bash
#!/bin/bash
# Query Mailgun API for recent caught emails
curl -s --user "api:$MAILGUN_API_KEY" \
  "https://api.mailgun.net/v3/mg.insightpulseai.net/events" \
  | jq '.items[] | {to, subject, timestamp}'
```

**Acceptance**:
- Dev/staging emails never reach real users
- Can view last 100 caught emails
- Email content accessible via Mailgun API

---

## Phase 5: MCP / Control Room Integration

**Goal**: Agent callable by higher-level orchestrators

### T5.1 - Define MCP Tool Spec
**Status**: ⏳ Spec
**Owner**: TBD
**PR**: #TBD
**Location**: `mcp/servers/devops-agent/spec.json`

**Tools**:
```json
{
  "tools": [
    {
      "name": "ciGuard",
      "description": "Run CI checks (manifest + tests)",
      "inputSchema": {
        "repo": "string",
        "branch": "string"
      }
    },
    {
      "name": "manifestSteward",
      "description": "Verify and fix OCA/ipai layout",
      "inputSchema": {}
    },
    {
      "name": "deployProd",
      "description": "Deploy to production",
      "inputSchema": {
        "sha": "string (optional)"
      }
    },
    {
      "name": "rollbackProd",
      "description": "Rollback production to SHA",
      "inputSchema": {
        "sha": "string (required)"
      }
    },
    {
      "name": "checkHealth",
      "description": "Run all health checks",
      "inputSchema": {
        "env": "string (dev|staging|prod)"
      }
    }
  ]
}
```

**Acceptance**:
- MCP spec valid JSON
- All tools documented
- Input schemas complete

### T5.2 - Implement MCP Handlers
**Status**: ⏳ Spec
**Owner**: TBD
**PR**: #TBD
**Location**: `mcp/servers/devops-agent/server.py`

**Implementation**:
```python
from mcp import MCPServer

server = MCPServer("devops-agent")

@server.tool()
def ciGuard(repo: str, branch: str):
    """Run CI checks"""
    result = subprocess.run([
        './scripts/ci/run_checks.sh',
        '--repo', repo,
        '--branch', branch
    ], capture_output=True, text=True)

    return {
        'status': 'success' if result.returncode == 0 else 'failure',
        'output': result.stdout,
        'errors': result.stderr
    }

@server.tool()
def manifestSteward():
    """Verify OCA/ipai layout"""
    subprocess.run(['./scripts/verify_oca_ipai_layout.sh'], check=True)
    return {'status': 'verified'}

# ... other tool implementations
```

**Acceptance**:
- All MCP tools implemented
- Error handling for all failure modes
- Logs captured and returned

### T5.3 - Wire BuildOpsControlRoom UI
**Status**: ⏳ Spec
**Owner**: TBD
**PR**: #TBD
**Description**: Control room dashboard shows DevOps agent status

**UI Components**:
- CI status widget (last 10 runs)
- Last deployment info (SHA, timestamp, deployer)
- Health summary (all services green/red)
- Quick actions (deploy, rollback, health check)

**Acceptance**:
- Dashboard updates in real-time
- Quick actions invoke MCP tools
- Error states clearly displayed

### T5.4 - Add Agent Documentation
**Status**: ⏳ Spec
**Owner**: TBD
**PR**: #TBD
**Location**: `docs/agents/ipai-odoo-devops-agent.md`

**Sections**:
1. Overview and capabilities
2. MCP tool reference
3. Common workflows
4. Troubleshooting
5. Development guide

**Acceptance**:
- Complete tool reference
- Examples for all use cases
- Troubleshooting guide tested

---

## Phase 6: Hardening

**Goal**: Production-ready robustness

### T6.1 - Add Timeouts and Retries
**Status**: ⏳ Spec
**Owner**: TBD
**PR**: #TBD
**Description**: All long-running scripts have timeouts

**Implementation**:
```bash
# Add to all scripts
TIMEOUT=${TIMEOUT:-300}  # 5 minute default

timeout $TIMEOUT <command> || {
    echo "❌ Command timed out after ${TIMEOUT}s"
    exit 1
}
```

**Acceptance**:
- All scripts respect $TIMEOUT env var
- Clear timeout error messages
- Graceful cleanup on timeout

### T6.2 - Enforce CLAUDE.md Compliance
**Status**: ⏳ Spec
**Owner**: TBD
**PR**: #TBD
**Description**: Automated checks for secret policy compliance

**Checks**:
```bash
# No secrets in logs
grep -r "sk-" scripts/ && exit 1
grep -r "ghp_" scripts/ && exit 1

# No hardcoded secrets
grep -r "OPENAI_API_KEY=" scripts/ | grep -v '\$' && exit 1

# No token prompts
grep -ri "enter your token" scripts/ && exit 1
```

**Acceptance**:
- CI fails if secrets found in code
- CI fails if token prompts found
- Documentation references only env var names

### T6.3 - Add Manifest Drift Alerts
**Status**: ⏳ Spec
**Owner**: TBD
**PR**: #TBD
**Description**: Alert if manifest broken for >24 hours

**Implementation**: Cron job + n8n workflow
```yaml
# n8n workflow: manifest-drift-alert
triggers:
  - cron: "0 8 * * *"  # Daily at 8 AM SGT
steps:
  - run: ./scripts/verify_oca_ipai_layout.sh
  - if: failed
    query: SELECT last_success FROM manifest_checks WHERE id = 1
    if: (NOW() - last_success) > INTERVAL '24 hours'
    then: send_mattermost_alert("⚠️ Manifest broken for >24h")
```

**Acceptance**:
- Alert sent after 24h of drift
- Alert includes fix instructions
- Alert escalates after 48h

### T6.4 - Schedule Periodic Review
**Status**: ⏳ Spec
**Owner**: TBD
**Frequency**: Monthly
**Description**: Review tasks.md and update status

**Checklist**:
- [ ] Close completed tasks
- [ ] Update blocked tasks
- [ ] Add new tasks from feedback
- [ ] Update priorities

**Acceptance**:
- tasks.md current and accurate
- Stale tasks removed
- New work captured

---

## Summary Metrics

**Total Tasks**: 32
**Status Breakdown**:
- ✅ Complete: 5 (16%)
- 🚧 In Progress: 0 (0%)
- ⏳ Spec: 27 (84%)
- ❌ Blocked: 0 (0%)
- ⚠️ On Hold: 0 (0%)

**Phase Completion**:
- Phase 0 (Bootstrapping): 100% (3/3 complete)
- Phase 1 (Manifest): 50% (2/4 complete)
- Phase 2 (CI Guard): 0% (0/3 complete)
- Phase 3 (Deploy): 0% (0/5 complete)
- Phase 4 (Monitoring): 0% (0/3 complete)
- Phase 5 (MCP): 0% (0/4 complete)
- Phase 6 (Hardening): 0% (0/4 complete)

---

**Last Updated**: 2026-01-29
**Next Review**: 2026-02-29
