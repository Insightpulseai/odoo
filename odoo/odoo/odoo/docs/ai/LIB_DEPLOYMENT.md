# LIB v1.1 Hybrid Brain - Deployment Guide

Complete deployment guide for LIB Hybrid Brain Sync infrastructure.

## Architecture Overview

```
┌────────────────────────────────────────────────────────────┐
│  LIB Hybrid Brain Sync - Production Architecture          │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  GitHub Actions CI/CD                                      │
│  ├─ Validate: Migration files, Edge Function syntax       │
│  ├─ Deploy Migrations: Push to Supabase PostgreSQL        │
│  ├─ Deploy Function: lib-brain-sync Edge Function         │
│  └─ Verify: Schema, tables, health endpoints              │
│                                                            │
│  Supabase Infrastructure                                   │
│  ├─ PostgreSQL 15: lib_shared schema (events, entities)   │
│  ├─ Edge Function: lib-brain-sync (4 endpoints)           │
│  ├─ pg_cron: Automated event pruning (365 days)           │
│  └─ Webhooks: Real-time device notifications              │
│                                                            │
│  Client Devices (macOS/Linux)                             │
│  ├─ SQLite Database: Local brain (.lib/lib.db)            │
│  ├─ Webhook Listener: Real-time sync (port 8001)          │
│  ├─ Periodic Daemon: Fallback sync (every 10 min)         │
│  └─ Sync Client: Push/pull operations                     │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

---

## Prerequisites

### Required Tools

| Tool | Version | Purpose | Installation |
|------|---------|---------|--------------|
| Supabase CLI | Latest | Deployment | `npm install -g supabase` |
| GitHub CLI | Latest | Secret management | `brew install gh` |
| Python | 3.12+ | Sync client | System default |
| Git | Latest | Version control | System default |

### Required Accounts

- **Supabase Account**: Free or Pro tier
- **GitHub Account**: Repository access with Actions enabled

---

## Phase 1: Supabase Project Setup

### 1.1 Create Supabase Project

```bash
# Login to Supabase
supabase login

# Create new project (or use existing)
# Project Ref: spdtwktxdalcfigzeqrz (InsightPulse AI)

# Get project details
supabase projects list
```

### 1.2 Retrieve Required Credentials

```bash
# Get project reference ID
SUPABASE_PROJECT_REF="spdtwktxdalcfigzeqrz"

# Get Supabase URL
SUPABASE_URL="https://${SUPABASE_PROJECT_REF}.supabase.co"

# Get database password (from Supabase Dashboard → Settings → Database)
SUPABASE_DB_PASSWORD="your-database-password"

# Get service role key (from Supabase Dashboard → Settings → API)
SUPABASE_SERVICE_ROLE_KEY="eyJhbGci..."

# Get access token (from Supabase Dashboard → Settings → Access Tokens)
SUPABASE_ACCESS_TOKEN="sbp_..."
```

### 1.3 Generate Sync Secret

```bash
# Generate random secret for sync authentication
LIB_SYNC_SECRET=$(openssl rand -base64 32)
echo "LIB_SYNC_SECRET: $LIB_SYNC_SECRET"

# Save this value - you'll need it for GitHub secrets and client configuration
```

---

## Phase 2: GitHub Repository Configuration

### 2.1 Configure GitHub Secrets

```bash
# Authenticate with GitHub
gh auth login

# Navigate to repository
cd /path/to/odoo

# Set repository secrets
gh secret set SUPABASE_ACCESS_TOKEN --body "$SUPABASE_ACCESS_TOKEN"
gh secret set SUPABASE_PROJECT_REF --body "$SUPABASE_PROJECT_REF"
gh secret set SUPABASE_DB_PASSWORD --body "$SUPABASE_DB_PASSWORD"
gh secret set SUPABASE_SERVICE_ROLE_KEY --body "$SUPABASE_SERVICE_ROLE_KEY"
gh secret set SUPABASE_URL --body "$SUPABASE_URL"
gh secret set LIB_SYNC_SECRET --body "$LIB_SYNC_SECRET"

# Verify secrets are set
gh secret list
```

**Expected Output:**
```
SUPABASE_ACCESS_TOKEN       Updated 2026-02-10
SUPABASE_PROJECT_REF        Updated 2026-02-10
SUPABASE_DB_PASSWORD        Updated 2026-02-10
SUPABASE_SERVICE_ROLE_KEY   Updated 2026-02-10
SUPABASE_URL                Updated 2026-02-10
LIB_SYNC_SECRET             Updated 2026-02-10
```

### 2.2 Configure GitHub Environment

```bash
# Create production environment with protection rules
gh api repos/:owner/:repo/environments/production --method PUT --field wait_timer=0

# Add environment secrets (same as repository secrets)
# This enables deployment URL in workflow
```

---

## Phase 3: Initial Deployment

### 3.1 Manual Local Deployment (First Time)

```bash
# Navigate to project root
cd /path/to/odoo

# Link to Supabase project
supabase link --project-ref $SUPABASE_PROJECT_REF

# Push database migrations
supabase db push --password "$SUPABASE_DB_PASSWORD"

# Verify schema
supabase db query "SELECT schema_name FROM information_schema.schemata WHERE schema_name = 'lib_shared';"
# Expected: lib_shared

# Set Edge Function secrets
supabase secrets set LIB_SYNC_SECRET="$LIB_SYNC_SECRET"
supabase secrets set SUPABASE_SERVICE_ROLE_KEY="$SUPABASE_SERVICE_ROLE_KEY"
supabase secrets set SUPABASE_URL="$SUPABASE_URL"

# Deploy Edge Function
supabase functions deploy lib-brain-sync --no-verify-jwt

# Test health endpoint
curl https://${SUPABASE_PROJECT_REF}.supabase.co/functions/v1/lib-brain-sync/health
# Expected: {"status":"healthy","version":"1.1.0"}
```

### 3.2 Verify Deployment

```bash
# Check database schema
supabase db query "
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'lib_shared'
ORDER BY table_name;
"
# Expected: device_webhooks, entities, events

# Check RPC functions
supabase db query "
SELECT routine_name
FROM information_schema.routines
WHERE routine_schema = 'public'
AND routine_name LIKE 'lib_shared%'
ORDER BY routine_name;
"
# Expected: lib_shared_get_active_webhooks, lib_shared_ingest_events,
#           lib_shared_mark_webhook_notified, lib_shared_pull_events,
#           lib_shared_register_webhook, etc.

# Check pg_cron job
supabase db query "SELECT * FROM cron.job WHERE jobname = 'lib-events-cleanup';"
# Expected: 1 row with schedule '0 3 * * 0'
```

---

## Phase 4: Automated CI/CD Deployment

### 4.1 Trigger Workflow

```bash
# Push to main branch triggers automatic deployment
git add .github/workflows/lib-brain-sync-deploy.yml
git commit -m "feat(lib): add CI/CD deployment workflow"
git push origin main

# Or trigger manually
gh workflow run lib-brain-sync-deploy.yml
```

### 4.2 Monitor Deployment

```bash
# Watch workflow runs
gh run watch

# View workflow logs
gh run view --log

# Check workflow status
gh run list --workflow=lib-brain-sync-deploy.yml
```

### 4.3 Deployment Verification

```bash
# Check GitHub Actions summary
gh run view

# Verify Edge Function
curl https://${SUPABASE_PROJECT_REF}.supabase.co/functions/v1/lib-brain-sync/health

# Verify migrations
supabase db query "SELECT COUNT(*) FROM lib_shared.events;"
# Expected: 0 (empty table after fresh deployment)
```

---

## Phase 5: Client Configuration

### 5.1 Environment Configuration

Create `.env.lib` in project root:

```bash
# LIB Hybrid Sync Configuration
LIB_SQLITE_PATH="./.lib/lib.db"
LIB_SUPABASE_FN_URL="https://spdtwktxdalcfigzeqrz.supabase.co/functions/v1/lib-brain-sync"
LIB_SYNC_SECRET="YOUR_LIB_SYNC_SECRET"
LIB_SYNC_BATCH_SIZE="200"
LIB_SYNC_LOG_DIR="./.lib/logs"

# Webhook Configuration (optional)
LIB_WEBHOOK_PORT="8001"
LIB_WEBHOOK_SECRET="YOUR_WEBHOOK_SECRET"
```

**⚠️ Security:** Add `.env.lib` to `.gitignore`

### 5.2 Initialize Local Database

```bash
# Create database
python3 scripts/lib/lib_db.py init --db-path .lib/lib.db

# Verify tables
sqlite3 .lib/lib.db "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;"
# Expected: lib_device, lib_files, lib_files_fts, lib_inbox, lib_kv, lib_outbox, lib_runs
```

### 5.3 Test Manual Sync

```bash
# Load environment
source .env.lib

# Test sync client
python3 lib/bin/lib_sync_hybrid.py --verbose

# Expected output:
# {
#   "ok": true,
#   "push": {"pushed": 0, "result": {"inserted_events": 0, "upserted_entities": 0}},
#   "pull": {"pulled": 0, "applied": 0, "new_after_id": 0}
# }
```

---

## Phase 6: Production Daemon Setup

### 6.1 Install macOS Daemons

```bash
# Edit launchd plists with your secrets
nano lib/config/launchd/com.insightpulseai.lib-sync.plist
nano lib/config/launchd/com.insightpulseai.lib-webhook-listener.plist

# Copy to LaunchAgents
cp lib/config/launchd/*.plist ~/Library/LaunchAgents/

# Load daemons
launchctl load ~/Library/LaunchAgents/com.insightpulseai.lib-sync.plist
launchctl load ~/Library/LaunchAgents/com.insightpulseai.lib-webhook-listener.plist

# Verify running
launchctl list | grep insightpulseai
```

### 6.2 Register Webhook URL

```bash
# Get device ID
DEVICE_ID=$(python3 -c "
import asyncio, aiosqlite, sys
from pathlib import Path
sys.path.insert(0, 'scripts/lib')
from lib_db import ensure_device_id
async def get_id():
    async with aiosqlite.connect('.lib/lib.db') as db:
        print(await ensure_device_id(db))
asyncio.run(get_id())
")

echo "Device ID: $DEVICE_ID"

# Register webhook (replace YOUR_PUBLIC_IP)
curl -X POST "https://spdtwktxdalcfigzeqrz.supabase.co/functions/v1/lib-brain-sync/webhook" \
  -H "x-lib-sync-secret: $LIB_SYNC_SECRET" \
  -H "Content-Type: application/json" \
  -d "{
    \"device_id\": \"$DEVICE_ID\",
    \"webhook_url\": \"http://YOUR_PUBLIC_IP:8001/webhook\",
    \"secret\": \"$LIB_WEBHOOK_SECRET\"
  }"

# Expected: {"ok": true, "webhook_id": 1}
```

---

## Monitoring & Maintenance

### Log Locations

| Log Type | Location | Purpose |
|----------|----------|---------|
| Sync Daemon | `.lib/logs/lib-sync-YYYYMMDD.log` | Daily sync operations |
| Webhook Listener | `.lib/logs/lib-webhook-listener.log` | Real-time sync events |
| Launchd (Sync) | `.lib/logs/lib-sync-launchd.log` | Daemon stdout |
| Launchd (Webhook) | `.lib/logs/lib-webhook-listener.log` | Listener stdout |
| Launchd Errors | `.lib/logs/*-error.log` | Daemon stderr |

### Health Checks

```bash
# Edge Function health
curl https://spdtwktxdalcfigzeqrz.supabase.co/functions/v1/lib-brain-sync/health

# Webhook listener health
curl http://localhost:8001/health

# Database event count
supabase db query "SELECT COUNT(*) as total_events FROM lib_shared.events;"

# Webhook registration status
supabase db query "SELECT device_id, webhook_url, active, last_notified_at FROM lib_shared.device_webhooks;"

# pg_cron job status
supabase db query "SELECT public.lib_shared_pruning_status();"
```

### Troubleshooting

#### Deployment Failures

```bash
# Check GitHub Actions logs
gh run view --log

# Check Supabase function logs
supabase functions logs lib-brain-sync --tail

# Verify secrets are set
supabase secrets list

# Re-deploy manually
supabase functions deploy lib-brain-sync --no-verify-jwt
```

#### Sync Failures

```bash
# Check sync logs
tail -f .lib/logs/lib-sync-$(date +%Y%m%d).log

# Test Edge Function directly
curl -X POST "https://spdtwktxdalcfigzeqrz.supabase.co/functions/v1/lib-brain-sync/ingest" \
  -H "x-lib-sync-secret: $LIB_SYNC_SECRET" \
  -H "Content-Type: application/json" \
  -d '{"batch": []}'
# Expected: {"ok": true, "result": {"inserted_events": 0, "upserted_entities": 0}}

# Verify database connectivity
sqlite3 .lib/lib.db "SELECT COUNT(*) FROM lib_outbox;"
```

#### Webhook Failures

```bash
# Check webhook listener is running
launchctl list | grep lib-webhook

# Test webhook endpoint
curl -X POST http://localhost:8001/webhook \
  -H "Content-Type: application/json" \
  -H "x-webhook-secret: $LIB_WEBHOOK_SECRET" \
  -d '{"event": "new_events", "after_id": 0, "timestamp": "2026-02-10T10:00:00Z"}'

# Check webhook registration
supabase db query "SELECT * FROM lib_shared.device_webhooks WHERE device_id = '$DEVICE_ID';"
```

---

## Security Best Practices

### Secret Management

1. **Never commit secrets** to git (.env.lib in .gitignore)
2. **Rotate secrets regularly** (quarterly minimum)
3. **Use unique secrets** per environment (dev/staging/prod)
4. **Audit secret access** (GitHub Actions logs, Supabase logs)

### Network Security

1. **Webhook Listener**: Use reverse proxy with SSL/TLS for public exposure
2. **Firewall Rules**: Restrict port 8001 to known IPs
3. **Secret Validation**: Always configure LIB_WEBHOOK_SECRET

### Database Security

1. **Service Role Key**: Keep secure, never expose in client code
2. **RLS Policies**: Validated (public schema access revoked)
3. **Event Pruning**: Automated cleanup (365-day retention)

---

## Performance Optimization

### Recommended Settings

| Setting | Development | Production |
|---------|-------------|------------|
| Sync Interval | 30 min | 10 min |
| Batch Size | 100 | 200 |
| Webhook Timeout | 10s | 5s |
| Log Retention | 7 days | 30 days |

### Scaling Considerations

- **Event Volume**: <10K events/day per device (current limits)
- **Device Count**: Unlimited (horizontal scaling)
- **Database Size**: Monitor lib_shared.events growth (pruning active)
- **Network Bandwidth**: ~100KB/sync with 200 events

---

## Rollback Procedures

### Revert Edge Function

```bash
# List function versions
supabase functions list

# Deploy previous version
supabase functions deploy lib-brain-sync --version <previous-version>
```

### Revert Database Migrations

```bash
# Not supported - create new migration to reverse changes
# Example: Create 20260210170000_rollback_lib_shared.sql
```

### Emergency Disable

```bash
# Stop all client daemons
launchctl stop com.insightpulseai.lib-sync
launchctl stop com.insightpulseai.lib-webhook-listener

# Deactivate all webhooks in database
supabase db query "UPDATE lib_shared.device_webhooks SET active = false;"
```

---

## Appendix

### Required GitHub Secrets

| Secret Name | Source | Purpose |
|-------------|--------|---------|
| `SUPABASE_ACCESS_TOKEN` | Supabase Dashboard | CLI authentication |
| `SUPABASE_PROJECT_REF` | Supabase Project | Project identifier |
| `SUPABASE_DB_PASSWORD` | Supabase Dashboard | Database access |
| `SUPABASE_SERVICE_ROLE_KEY` | Supabase Dashboard | Edge Function auth |
| `SUPABASE_URL` | Supabase Project | API endpoint |
| `LIB_SYNC_SECRET` | Generated | Sync authentication |

### Useful Commands

```bash
# Quick sync test
python3 lib/bin/lib_sync_hybrid.py --push --pull --verbose

# Quick health check
curl https://spdtwktxdalcfigzeqrz.supabase.co/functions/v1/lib-brain-sync/health && \
curl http://localhost:8001/health

# Monitor sync activity
tail -f .lib/logs/lib-sync-$(date +%Y%m%d).log .lib/logs/lib-webhook-listener.log

# Event statistics
supabase db query "
SELECT
  DATE(created_at) as date,
  COUNT(*) as events,
  COUNT(DISTINCT device_id) as devices
FROM lib_shared.events
WHERE created_at > NOW() - INTERVAL '7 days'
GROUP BY DATE(created_at)
ORDER BY date DESC;
"
```

---

**Version:** 1.1.0
**Last Updated:** 2026-02-10
**Support:** See `lib/config/launchd/README.md` for daemon management
