# Runbook: Docker Staging Cleanup & SSOT Alignment

**Owner:** Basher-Docker-Staging (Docker Steward Agent for Staging)
**Host:** 178.128.112.214 (DigitalOcean Droplet)
**Purpose:** Keep staging Docker environment aligned to Odoo staging SSOT.

---

## 1. Context

- **Canonical Odoo staging environment:**
  - Host: `178.128.112.214`
  - Repo: `/opt/odoo-ce`
  - Stack definition: `sandbox/staging/docker-compose.yml`
  - Public URL: `https://staging.insightpulseai.com`

- **Staging Docker is for:**
  - Odoo 18 CE staging app + PostgreSQL
  - Future: Apache Superset, n8n workflow automation

- **Protection boundaries:**
  - **NEVER** touch containers/images with prefixes: `prod-`, `stable-`, `ipai-`, `odoo-erp-prod`
  - Only clean `*-staging` resources and explicitly marked safe-to-delete patterns

**SSOT is defined in:**

```text
infra/docker/DOCKER_STAGING_SSOT.yaml
```

---

## 2. Objectives

1. Audit current Docker state on staging droplet.
2. Compare against SSOT and classify resources:
   - `expected` - Part of staging stack
   - `extra_safe_delete` - Old experiments, safe to remove
   - `protected` - Production resources (NEVER touch)
   - `unknown` - Unclear purpose, manual review required
3. Propose a safe cleanup plan.
4. Apply cleanup (when explicitly requested).
5. Verify staging stack is healthy.

---

## 3. Quick Start (SSH Access)

**Connect to staging:**

```bash
ssh root@178.128.112.214
cd /opt/odoo-ce
```

**Run audit:**

```bash
./scripts/docker-staging-audit.sh
```

This script:

- Lists containers, images, volumes on the staging droplet.
- Highlights anything **not** matching the SSOT allow-lists.
- Writes a JSONL audit log to `logs/docker_staging_audit_log.jsonl`.
- **NEVER** performs destructive operations (read-only).

Use this as the baseline for the Basher-Docker-Staging agent.

---

## 4. Manual Cleanup Commands (to be run by Agent)

> ⚠️ **CRITICAL:** These commands must NEVER touch `prod-*`, `stable-*`, or `ipai-*` resources.

### 4.1 Stop and Remove Safe Staging Containers

```bash
# Identify staging containers not in SSOT
docker ps -a --format '{{.ID}} {{.Names}}' \
  | grep -E 'test-|tmp-|experiment-' \
  | grep -v -E 'prod|stable|ipai' \
  | awk '{print $1}' \
  | xargs -r docker stop

# Remove them
docker ps -a --format '{{.ID}} {{.Names}}' \
  | grep -E 'test-|tmp-|experiment-' \
  | grep -v -E 'prod|stable|ipai' \
  | awk '{print $1}' \
  | xargs -r docker rm
```

### 4.2 Remove Old Staging Images

```bash
# Remove old staging-specific images (not prod/stable/ipai)
docker images --format '{{.Repository}}:{{.Tag}} {{.ID}}' \
  | grep -E 'staging|test|tmp|experiment' \
  | grep -v -E 'prod|stable|ipai' \
  | awk '{print $2}' \
  | xargs -r docker rmi
```

### 4.3 Remove Dangling Images & Volumes

```bash
# Dangling images (no tags)
docker image prune -f

# Unused volumes (CAREFUL: preserve SSOT volumes)
docker volume ls --format '{{.Name}}' \
  | grep -v -E '^(odoo-staging-db-data|odoo-staging-filestore)$' \
  | grep -v -E 'prod|stable|ipai' \
  | xargs -r docker volume rm
```

---

## 5. Re-start & Verify Staging Stack

From the staging host:

```bash
cd /opt/odoo-ce

# Start staging stack
docker compose -f sandbox/staging/docker-compose.yml up -d

# Check status
docker compose -f sandbox/staging/docker-compose.yml ps

# Verify Odoo is accessible
curl -sf https://staging.insightpulseai.com/web/health || echo "Health check failed"
```

**Expected state:**

- Containers: `odoo-staging`, `odoo-staging-db` (running)
- Volumes: `odoo-staging-db-data`, `odoo-staging-filestore`
- Health check: `https://staging.insightpulseai.com/web/health` returns 200

---

## 6. Audit Log (For Future RL / Analytics)

Each audit run appends to:

```text
logs/docker_staging_audit_log.jsonl
```

Fields:

- `timestamp`
- `host`
- `env` ("staging")
- `containers_expected`
- `containers_extra`
- `containers_protected`
- `images_expected`
- `images_extra`
- `volumes_expected`
- `volumes_extra`

This log feeds:
- Mattermost/Slack alerts for drift detection
- Future policy learner / heuristic tuner
- Compliance audit trail

---

## 7. Acceptance Criteria

This runbook is **complete** when:

1. **Staging Docker shows only:**
   - Odoo staging containers (`odoo-staging`, `odoo-staging-db`)
   - Future approved services (Superset, n8n when added to SSOT)

2. **Protection verified:**
   - Zero production containers/images removed
   - All `prod-*`, `stable-*`, `ipai-*` resources untouched

3. **Audit passes:**
   - `docker-staging-audit.sh` runs cleanly
   - Classifies all resources correctly
   - Writes audit log entry

4. **Stack health confirmed:**
   - `https://staging.insightpulseai.com/web/health` returns 200
   - PostgreSQL `pg_isready` returns exit code 0
   - No unexpected containers running

5. **SSOT versioned:**
   - `infra/docker/DOCKER_STAGING_SSOT.yaml` committed to git

---

## 8. Agent Prompt (Gordon-Staging)

When using Claude Code / Codex for automated staging cleanup:

> **Basher-Docker-Staging Prompt:**
>
> You are Gordon-Staging, the Docker steward for the InsightPulseAI staging environment on droplet 178.128.112.214.
>
> Your job: audit Docker state against `infra/docker/DOCKER_STAGING_SSOT.yaml`, classify resources (expected/extra/protected), and propose safe cleanup for `extra_safe_delete` only.
>
> **Critical rules:**
> - NEVER touch containers/images with prefixes: `prod-`, `stable-`, `ipai-`, `odoo-erp-prod`
> - ONLY clean `*-staging` resources and explicitly safe patterns (test-, tmp-, experiment-)
> - ALWAYS verify health checks after any changes
>
> **Commands:**
> 1. SSH to staging: `ssh root@178.128.112.214`
> 2. Run audit: `cd /opt/odoo-ce && ./scripts/docker-staging-audit.sh`
> 3. Show me the drift report with classifications
> 4. Propose cleanup commands (DO NOT execute until I say APPLY CLEANUP)
> 5. After cleanup, verify staging stack health

---

## 9. Integration with n8n & Ops Control Room

**Scheduled n8n workflow (future):**

```javascript
{
  "nodes": [
    {
      "name": "Schedule: Daily 2AM SGT",
      "type": "n8n-nodes-base.cron",
      "parameters": {
        "cronExpression": "0 2 * * *"
      }
    },
    {
      "name": "SSH: Run Staging Audit",
      "type": "n8n-nodes-base.ssh",
      "parameters": {
        "host": "178.128.112.214",
        "command": "cd /opt/odoo-ce && ./scripts/docker-staging-audit.sh"
      }
    },
    {
      "name": "Parse Audit Results",
      "type": "n8n-nodes-base.code",
      "parameters": {
        "jsCode": "// Parse JSONL, extract drift count"
      }
    },
    {
      "name": "Mattermost: Alert if Drift",
      "type": "n8n-nodes-base.mattermost",
      "parameters": {
        "message": "🚨 Staging Docker drift detected: {{$json.extra_containers}} extra containers, {{$json.extra_images}} extra images"
      }
    }
  ]
}
```

**Ops Control Room action:**

- Button: "Clean Staging Docker"
- Action: SSH → `cd /opt/odoo-ce && ./scripts/docker-staging-audit.sh && ./scripts/docker-staging-cleanup.sh`
- Result: Post summary to control room dashboard

---

## 10. Troubleshooting

**Issue: Audit script fails with permission denied**

```bash
# Fix script permissions
chmod +x /opt/odoo-ce/scripts/docker-staging-audit.sh
```

**Issue: Cannot connect to Docker daemon**

```bash
# Verify Docker is running
systemctl status docker

# Restart if needed
systemctl restart docker
```

**Issue: Staging stack won't start**

```bash
# Check logs
docker compose -f sandbox/staging/docker-compose.yml logs

# Verify volumes exist
docker volume ls | grep staging
```

**Issue: Protected resource accidentally removed**

```bash
# IMMEDIATELY notify team via Mattermost
# Restore from latest backup
# Review audit log to identify root cause
# Update SSOT protection rules to prevent recurrence
```

---

## 11. Related Documentation

- Desktop cleanup: `docs/runbooks/DOCKER_DESKTOP_CLEANUP.md`
- Staging SSOT: `infra/docker/DOCKER_STAGING_SSOT.yaml`
- Production SSOT: `infra/docker/DOCKER_PROD_SSOT.yaml` (future)
- Audit scripts: `scripts/docker-*-audit.sh`
