# Docker SSOT Architecture

**Single Source of Truth for all Docker environments across InsightPulseAI infrastructure**

---

## Overview

Three-tier Docker management with automated auditing and Gordon-style cleanup agents:

1. **Desktop (Local Dev)** - Your MacBook Pro
2. **Staging (DigitalOcean Droplet)** - 178.128.112.214
3. **Production (DigitalOcean Droplet)** - 178.128.112.214 (same host, different containers)

Each environment has:
- **SSOT YAML** - Canonical definition of allowed resources
- **Audit Script** - Non-destructive classification (expected/extra/protected/safe-to-delete)
- **Cleanup Runbook** - Safe manual/automated cleanup procedures
- **Gordon Agent** - AI steward for automated maintenance

---

## 1. Desktop Environment

**Host:** MacBook Pro (local development)
**Purpose:** Odoo 18 CE dev sandbox only

### Files

| File | Purpose |
|------|---------|
| `infra/docker/DOCKER_DESKTOP_SSOT.yaml` | Canonical desktop Docker state |
| `scripts/docker-desktop-audit.sh` | Non-destructive audit script |
| `docs/runbooks/DOCKER_DESKTOP_CLEANUP.md` | Cleanup procedures |

### Allowed Resources

**Containers:**
- `odoo-dev` - Odoo app
- `odoo-dev-db` - PostgreSQL
- `odoo-mailpit` - Email testing (optional)
- `odoo-pgadmin` - DB admin (optional)

**Images:**
- `odoo:*`
- `postgres:16*`
- `axllent/mailpit:*`
- `dpage/pgadmin4:*`

**Volumes:**
- `odoo-dev-db-data`
- `odoo-dev-filestore`

### Cleanup Policy

- Max unused image age: 14 days
- Max unused volume age: 30 days
- Auto-delete patterns: `*/docker-extension*`, `mcp/*`, `artifision/*`
- Protected tags: `prod-*`, `stable-*`, `ipai-*`

### Usage

```bash
cd ~/Documents/GitHub/odoo-ce
./scripts/docker-desktop-audit.sh
```

---

## 2. Staging Environment

**Host:** 178.128.112.214 (DigitalOcean Droplet)
**Purpose:** Pre-production validation for Odoo 18 CE
**URL:** https://staging.insightpulseai.com

### Files

| File | Purpose |
|------|---------|
| `infra/docker/DOCKER_STAGING_SSOT.yaml` | Canonical staging Docker state |
| `scripts/docker-staging-audit.sh` | Non-destructive audit with production protection |
| `docs/runbooks/DOCKER_STAGING_CLEANUP.md` | Cleanup procedures for staging |

### Allowed Resources

**Containers:**
- `odoo-staging` - Odoo app (staging)
- `odoo-staging-db` - PostgreSQL (staging)
- Future: `superset-staging`, `n8n-staging`

**Images:**
- `odoo:18.0-*`
- `postgres:16-alpine`
- Future: `apache/superset`, `n8nio/n8n`

**Volumes:**
- `odoo-staging-db-data`
- `odoo-staging-filestore`

### Protection Rules (CRITICAL)

**NEVER touch these prefixes:**
- `prod-*`
- `stable-*`
- `ipai-*`
- `odoo-erp-prod`
- `odoo-db-sgp1`

**Safe to delete patterns:**
- `test-*`
- `tmp-*`
- `experiment-*`
- `docker-extension*`
- `mcp/*`

### Usage

```bash
# SSH to staging
ssh root@178.128.112.214

# Run audit
cd /opt/odoo-ce
./scripts/docker-staging-audit.sh

# Review output before any cleanup
# See docs/runbooks/DOCKER_STAGING_CLEANUP.md for cleanup commands
```

---

## 3. Production Environment

**Host:** 178.128.112.214 (same droplet as staging)
**Purpose:** Production Odoo ERP, Superset, n8n, MCP
**URL:** https://erp.insightpulseai.com

### Files (Future)

| File | Purpose |
|------|---------|
| `infra/docker/DOCKER_PROD_SSOT.yaml` | Canonical production Docker state (TBD) |
| `scripts/docker-prod-audit.sh` | Read-only audit (no cleanup allowed) |
| `docs/runbooks/DOCKER_PROD_AUDIT.md` | Production audit procedures |

### Current Production Resources (Protected)

**Containers:**
- `odoo-erp-prod` - Production Odoo
- `odoo-db-sgp1` - Managed PostgreSQL cluster
- `ipai-superset` - Apache Superset BI
- `n8n` - Workflow automation
- `mcp-coordinator` - MCP services

**All production resources are OFF-LIMITS to automated cleanup.**

---

## Gordon Agent Architecture

### Gordon-Desktop (Local)

**Role:** Keep MacBook Docker clean (Odoo dev sandbox only)

**Responsibilities:**
- Daily audit of Docker Desktop
- Auto-delete old extensions/MCP helpers (>14 days)
- Preserve Odoo dev stack always
- Log to `logs/docker_audit_log.jsonl`

**Safety:**
- No remote operations
- User confirmation required for cleanup
- Can run autonomously for whitelisted patterns

### Gordon-Staging (Droplet)

**Role:** Keep staging Docker aligned to SSOT, never touch production

**Responsibilities:**
- Daily audit of staging droplet
- Classify resources: expected/extra/protected/safe-to-delete
- Auto-delete `safe-to-delete` only (with confirmation)
- Alert on drift via Mattermost/Slack
- Log to `/var/log/ipai/docker-staging-audit.jsonl`

**Critical Protection:**
- **NEVER** touch `prod-*`, `stable-*`, `ipai-*` prefixes
- **NEVER** touch `odoo-erp-prod` or `odoo-db-sgp1`
- Manual approval required for unknown resources
- Health checks before and after cleanup

**n8n Integration (Future):**
```yaml
Schedule: Daily 2AM SGT
Actions:
  1. SSH to staging
  2. Run docker-staging-audit.sh
  3. Parse drift count
  4. If drift > 0: Alert Mattermost
  5. If auto_cleanup=true AND safe_to_delete > 0: Run cleanup
  6. Post summary to Ops Control Room
```

### Gordon-Prod (Future)

**Role:** Read-only audit, zero automated cleanup

**Responsibilities:**
- Weekly audit of production droplet
- Classify resources (informational only)
- Alert on unexpected containers/images
- **NEVER** perform any cleanup operations

**Safety:**
- Read-only mode enforced
- No docker rm/rmi commands ever
- Alert-only for drift
- Manual intervention required for all changes

---

## Audit Log Schema

All audit scripts write JSONL logs with this schema:

```json
{
  "timestamp": "2026-01-16T05:53:32Z",
  "host": "hostname",
  "ip": "178.128.112.214",
  "env": "staging|desktop|prod",
  "containers_expected": ["odoo-staging", "odoo-staging-db"],
  "containers_extra": ["test-experiment-1"],
  "containers_protected": ["odoo-erp-prod"],
  "containers_safe_delete": ["tmp-debug-container"],
  "images_expected": ["odoo:18.0", "postgres:16-alpine"],
  "images_extra": ["old-experiment:v1"],
  "images_protected": ["ipai-superset:stable-2.1"],
  "images_safe_delete": ["docker-extension:latest"],
  "volumes_expected": ["odoo-staging-db-data"],
  "volumes_extra": ["old-volume-xyz"]
}
```

---

## File Structure

```
odoo-ce/
├── infra/docker/
│   ├── DOCKER_DESKTOP_SSOT.yaml     ✅ Desktop canonical state
│   ├── DOCKER_STAGING_SSOT.yaml     ✅ Staging canonical state
│   └── DOCKER_PROD_SSOT.yaml        🚧 Future: Production state
│
├── scripts/
│   ├── docker-desktop-audit.sh      ✅ Desktop audit (executable)
│   ├── docker-staging-audit.sh      ✅ Staging audit (executable)
│   └── docker-prod-audit.sh         🚧 Future: Production audit
│
└── docs/runbooks/
    ├── DOCKER_DESKTOP_CLEANUP.md    ✅ Desktop cleanup procedures
    ├── DOCKER_STAGING_CLEANUP.md    ✅ Staging cleanup procedures
    └── DOCKER_PROD_AUDIT.md         🚧 Future: Production audit only
```

---

## Testing Locally

### Desktop Audit (Local)

```bash
cd ~/Documents/GitHub/odoo-ce
./scripts/docker-desktop-audit.sh
```

Expected output:
- Lists containers, images, volumes
- Classifies each as expected/extra
- Writes to `logs/docker_audit_log.jsonl`
- Zero destructive operations

### Staging Audit (Remote - After Repo Sync)

```bash
# 1. SSH to staging
ssh root@178.128.112.214

# 2. Clone/pull repo
cd /opt
git clone https://github.com/jgtolentino/odoo-ce.git  # if first time
# OR
cd /opt/odoo-ce && git pull origin main

# 3. Run audit
./scripts/docker-staging-audit.sh
```

Expected output:
- Shows expected staging containers
- Highlights protected production resources (never touch)
- Shows safe-to-delete candidates
- Writes to `logs/docker_staging_audit_log.jsonl`
- Zero destructive operations

---

## Acceptance Criteria

### Desktop

✅ SSOT file committed and versioned
✅ Audit script executable and runs cleanly
✅ Only Odoo dev containers allowed
✅ Extensions/MCP helpers flagged for cleanup
✅ Zero false positives on Odoo stack

### Staging

✅ SSOT file committed and versioned
✅ Audit script executable with production protection
✅ Protected prefixes never touched
✅ Safe-to-delete patterns correctly classified
✅ Health checks pass after cleanup
✅ n8n integration ready (workflow defined)

### Production (Future)

🚧 SSOT file created (read-only reference)
🚧 Audit script (read-only, no cleanup mode)
🚧 Alert-only workflow
🚧 Manual change approval process

---

## Next Steps

1. **Test staging audit on droplet:**
   ```bash
   ssh root@178.128.112.214
   cd /opt && git clone https://github.com/jgtolentino/odoo-ce.git
   cd odoo-ce && ./scripts/docker-staging-audit.sh
   ```

2. **Wire up n8n staging audit workflow:**
   - Schedule: Daily 2AM SGT
   - Action: SSH → audit → alert if drift
   - Optional: Auto-cleanup safe-to-delete with flag

3. **Create Ops Control Room action:**
   - Button: "Audit Staging Docker"
   - Action: Trigger n8n workflow
   - Display: Drift summary on dashboard

4. **Formalize production SSOT (later):**
   - After staging pattern proven stable
   - Read-only audit mode only
   - No automated cleanup ever

---

## Related Documentation

- Desktop cleanup: `docs/runbooks/DOCKER_DESKTOP_CLEANUP.md`
- Staging cleanup: `docs/runbooks/DOCKER_STAGING_CLEANUP.md`
- Odoo sandbox setup: `sandbox/dev/README.md`
- Infrastructure SSOT: `INFRASTRUCTURE_SSOT.yaml`
