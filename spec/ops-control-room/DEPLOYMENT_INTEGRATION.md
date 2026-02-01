# Ops Control Room — Deployment Integration Guide

**Spec Bundle**: `spec/ops-control-room/`
**Status**: Canonical
**Last Updated**: 2026-01-08

---

## Purpose

This document bridges the **Ops Control Room** (parallel runbook executor) with the **Odoo 18 CE DIY Deployment Best Practices** to enable automated production deployments following CloudPepper standards.

---

## 1) Worker Sizing for Ops Executors

The Ops Control Room workers should follow similar sizing principles as Odoo workers but optimized for I/O-bound operations:

### Recommended Worker Topology

| Environment | Droplet Size | Ops Workers | Concurrent Runs | Monthly Cost |
|-------------|--------------|-------------|-----------------|--------------|
| Dev/Testing | s-2vcpu-4gb | 2 | 8 (4 lanes × 2) | $24/mo |
| Small Prod | s-4vcpu-8gb | 3 | 12 (4 lanes × 3) | $48/mo |
| Medium Prod | s-8vcpu-16gb | 5 | 20 (4 lanes × 5) | $96/mo |
| Large Prod | c-8 (dedicated) | 10 | 40 (4 lanes × 10) | $168/mo |

**Formula**:
```
# Ops workers are I/O-bound, not CPU-bound like Odoo
ops_workers = concurrent_deployments / 4  # 4 lanes per worker
cpu_cores = ops_workers / 2  # Lower CPU requirements than Odoo
ram_per_worker = 512 MB  # Lightweight Node.js workers
total_ram = (ops_workers * 0.5 GB) + 2 GB  # +2 for OS overhead
```

**Key Differences from Odoo Workers**:
- Ops workers: I/O-bound (git, docker, network)
- Odoo workers: CPU/memory-bound (Python/PostgreSQL)
- Ops workers can be more densely packed (2× workers per CPU)

---

## 2) Firewall Configuration for Ops Control Room

### Additional Ports Required

```bash
# Standard UFW rules (from deployment guide)
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP (Let's Encrypt + redirect)
sudo ufw allow 443/tcp   # HTTPS (Odoo + Ops UI)

# Ops Control Room specific
sudo ufw allow 5432/tcp from <SUPABASE_IP>  # PostgreSQL (ops schema)
sudo ufw allow 8072/tcp                     # Odoo longpolling (if separate)

# Worker health checks (internal only)
sudo ufw allow from 10.0.0.0/8 to any port 3000 proto tcp

sudo ufw enable
```

**Rationale**:
- Port 5432: Supabase needs direct PostgreSQL access for `ops` schema
- Port 3000: Worker health check endpoint (internal network only)
- No new public ports required (UI on Vercel, workers on DO internal network)

---

## 3) PostgreSQL Configuration for Ops Schema

### Create `ops` Schema with Grants

```sql
-- Connect as postgres
sudo -u postgres psql

-- Create ops schema (separate from public/Odoo)
CREATE SCHEMA IF NOT EXISTS ops;

-- Grant access to Supabase connection pool
GRANT USAGE ON SCHEMA ops TO supabase_admin;
GRANT ALL ON ALL TABLES IN SCHEMA ops TO supabase_admin;
GRANT ALL ON ALL SEQUENCES IN SCHEMA ops TO supabase_admin;
GRANT ALL ON ALL FUNCTIONS IN SCHEMA ops TO supabase_admin;

-- Auto-grant on future tables
ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA ops
GRANT ALL ON TABLES TO supabase_admin;

ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA ops
GRANT ALL ON SEQUENCES TO supabase_admin;

-- Read-only access for monitoring (optional)
CREATE ROLE ops_monitor WITH LOGIN PASSWORD 'STRONG_PASSWORD';
GRANT CONNECT ON DATABASE "odoo_prod" TO ops_monitor;
GRANT USAGE ON SCHEMA ops TO ops_monitor;
GRANT SELECT ON ALL TABLES IN SCHEMA ops TO ops_monitor;

\q
```

### Configure Remote Access (Supabase)

```bash
# /etc/postgresql/16/main/postgresql.conf
listen_addresses = '*'

# /etc/postgresql/16/main/pg_hba.conf
# Add Supabase IP range (after existing rules)
hostssl odoo_prod supabase_admin <SUPABASE_IP_RANGE> scram-sha-256
hostssl odoo_prod ops_monitor <MONITOR_IP>/32 scram-sha-256

# Restart PostgreSQL
sudo systemctl restart postgresql
```

**Security Notes**:
- `ops` schema isolated from `public` schema (Odoo data)
- Supabase uses separate user (`supabase_admin`, not `odoo`)
- Monitor user is read-only for observability
- SSL/TLS required for all remote connections

---

## 4) Nginx Configuration for Ops UI

### /etc/nginx/sites-available/ops-control-room

```nginx
# Ops Control Room UI (Vercel proxy - optional for internal access)
upstream ops-ui {
    server ops-control-room.vercel.app:443;
}

server {
    listen 443 ssl http2;
    server_name ops.insightpulseai.com;

    # SSL (Let's Encrypt - same cert as Odoo)
    ssl_certificate /etc/letsencrypt/live/erp.insightpulseai.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/erp.insightpulseai.com/privkey.pem;
    ssl_session_timeout 30m;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256;
    ssl_prefer_server_ciphers off;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    # Logs
    access_log /var/log/nginx/ops-access.log;
    error_log /var/log/nginx/ops-error.log;

    # Proxy to Vercel (or direct to Supabase Edge Functions)
    location / {
        proxy_pass https://ops-ui;
        proxy_ssl_server_name on;
        proxy_set_header Host ops-control-room.vercel.app;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Direct access to Supabase Edge Functions (bypass Vercel)
    location /functions/ {
        proxy_pass https://<project>.supabase.co/functions/v1/;
        proxy_ssl_server_name on;
        proxy_set_header Host <project>.supabase.co;
        proxy_set_header Authorization "Bearer $http_authorization";
    }
}
```

**Alternative**: If UI is purely on Vercel, no nginx config needed (just DNS CNAME).

---

## 5) Deployment Runbook Templates

### Template 1: Fresh Odoo Deployment (from AIUX Ship PRD)

**Kind**: `odoo_fresh_deploy`

**Steps**:
```json
{
  "kind": "odoo_fresh_deploy",
  "steps": [
    {
      "name": "provision_droplet",
      "command": "doctl compute droplet create odoo-prod --size s-4vcpu-8gb --image ubuntu-22-04-x64 --region sgp1",
      "timeout": 300
    },
    {
      "name": "configure_firewall",
      "command": "bash scripts/setup-firewall.sh",
      "timeout": 60
    },
    {
      "name": "install_postgresql",
      "command": "bash scripts/install-postgresql.sh",
      "timeout": 300
    },
    {
      "name": "clone_repo",
      "command": "git clone https://github.com/jgtolentino/odoo-ce.git /opt/odoo",
      "timeout": 120
    },
    {
      "name": "deploy_odoo",
      "command": "bash scripts/deploy/bootstrap_from_tag.sh",
      "timeout": 600,
      "env": {
        "GIT_REF": "${params.git_ref}",
        "ODOO_DB": "${params.odoo_db}",
        "COMPOSE_FILE": "deploy/docker-compose.prod.yml"
      }
    },
    {
      "name": "configure_nginx",
      "command": "bash scripts/setup-nginx.sh",
      "timeout": 120
    },
    {
      "name": "configure_ssl",
      "command": "certbot --nginx -d ${params.domain} --non-interactive --agree-tos -m ${params.email}",
      "timeout": 120
    },
    {
      "name": "smoke_test",
      "command": "curl -f https://${params.domain}/web/health",
      "timeout": 30
    }
  ]
}
```

### Template 2: Module Upgrade (Hot Swap)

**Kind**: `odoo_module_upgrade`

**Steps**:
```json
{
  "kind": "odoo_module_upgrade",
  "steps": [
    {
      "name": "pull_latest",
      "command": "cd /opt/odoo && git pull origin main",
      "timeout": 60
    },
    {
      "name": "upgrade_modules",
      "command": "docker compose -f ${COMPOSE_FILE} exec -T ${ODOO_SERVICE} odoo -d ${ODOO_DB} -u ${modules} --stop-after-init",
      "timeout": 300,
      "env": {
        "modules": "${params.modules}",
        "ODOO_DB": "${params.odoo_db}"
      }
    },
    {
      "name": "rebuild_assets",
      "command": "docker compose -f ${COMPOSE_FILE} exec -T ${ODOO_SERVICE} odoo -d ${ODOO_DB} -u web,${modules} --stop-after-init",
      "timeout": 300
    },
    {
      "name": "restart_odoo",
      "command": "docker compose -f ${COMPOSE_FILE} restart ${ODOO_SERVICE}",
      "timeout": 60
    },
    {
      "name": "wait_health",
      "command": "sleep 120 && curl -f http://localhost:8069/web/health",
      "timeout": 150
    }
  ]
}
```

### Template 3: Database Backup (Daily Cron)

**Kind**: `odoo_db_backup`

**Steps**:
```json
{
  "kind": "odoo_db_backup",
  "steps": [
    {
      "name": "pg_dump",
      "command": "pg_dump -Fc -h localhost -U odoo ${ODOO_DB} > /var/lib/odoo/backups/${ODOO_DB}_$(date +%Y%m%d_%H%M%S).dump",
      "timeout": 600
    },
    {
      "name": "gzip",
      "command": "gzip /var/lib/odoo/backups/${ODOO_DB}_*.dump",
      "timeout": 300
    },
    {
      "name": "upload_s3",
      "command": "s3cmd put /var/lib/odoo/backups/${ODOO_DB}_*.dump.gz s3://${S3_BUCKET}/db/",
      "timeout": 600
    },
    {
      "name": "cleanup_old",
      "command": "find /var/lib/odoo/backups -type f -mtime +7 -delete",
      "timeout": 60
    }
  ]
}
```

---

## 6) Worker Health Check Integration

### Ops Worker /health Endpoint

```typescript
// workers/ops-executor/health.js
import express from 'express';
import { createClient } from '@supabase/supabase-js';

const app = express();
const supabase = createClient(process.env.SUPABASE_URL, process.env.SUPABASE_ANON_KEY);

app.get('/health', async (req, res) => {
  try {
    // Check Supabase connection
    const { error } = await supabase.from('ops.sessions').select('id').limit(1);
    if (error) throw error;

    // Check system resources
    const memoryUsage = process.memoryUsage();
    const healthy = memoryUsage.heapUsed < 500 * 1024 * 1024; // 500MB threshold

    res.status(healthy ? 200 : 503).json({
      status: healthy ? 'ok' : 'degraded',
      uptime: process.uptime(),
      memory: {
        heapUsed: `${Math.round(memoryUsage.heapUsed / 1024 / 1024)}MB`,
        heapTotal: `${Math.round(memoryUsage.heapTotal / 1024 / 1024)}MB`
      },
      worker_id: process.env.WORKER_ID
    });
  } catch (err) {
    res.status(503).json({ status: 'unhealthy', error: err.message });
  }
});

app.listen(3000);
```

### DigitalOcean App Platform Spec

```yaml
# infra/do/ops-workers.yaml
name: ops-executor-workers
region: sgp
services:
- name: worker
  dockerfile_path: workers/ops-executor/Dockerfile
  github:
    repo: jgtolentino/odoo-ce
    branch: main
    deploy_on_push: true
  instance_count: 3
  instance_size_slug: basic-xs
  health_check:
    http_path: /health
    initial_delay_seconds: 10
    period_seconds: 30
    timeout_seconds: 5
    success_threshold: 1
    failure_threshold: 3
  envs:
  - key: SUPABASE_URL
    value: ${SUPABASE_URL}
  - key: SUPABASE_ANON_KEY
    type: SECRET
    value: ${SUPABASE_ANON_KEY}
  - key: WORKER_ID
    value: worker-${RANDOM_UUID}
```

---

## 7) GitHub Actions Integration

### Deploy Ops Control Room Workers

```yaml
# .github/workflows/deploy-ops-workers.yml
name: Deploy Ops Workers

on:
  push:
    branches: [main]
    paths:
      - 'workers/ops-executor/**'
      - 'infra/do/ops-workers.yaml'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install doctl
        uses: digitalocean/action-doctl@v2
        with:
          token: ${{ secrets.DO_ACCESS_TOKEN }}

      - name: Update app spec
        run: |
          doctl apps update <APP_ID> --spec infra/do/ops-workers.yaml

      - name: Trigger deployment
        run: |
          doctl apps create-deployment <APP_ID> --force-rebuild

      - name: Wait for deployment
        run: |
          sleep 60
          doctl apps list-deployments <APP_ID> --format ID,Phase | grep ACTIVE || exit 1

      - name: Health check
        run: |
          curl -f https://ops-executor-workers-<hash>.ondigitalocean.app/health
```

---

## 8) Backup Integration with Ops Control Room

### Automated Backup Runs (Daily Cron)

**Trigger**: Scheduled Edge Function runs daily at 2 AM UTC

```typescript
// supabase/functions/ops-backup-scheduler/index.ts
Deno.cron('daily-backup', '0 2 * * *', async () => {
  const supabase = createClient(
    Deno.env.get('SUPABASE_URL')!,
    Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!
  );

  // Create backup session
  const { data: session } = await supabase
    .from('ops.sessions')
    .insert({
      name: 'Daily Backup',
      description: `Automated backup ${new Date().toISOString()}`,
      triggered_by: 'schedule'
    })
    .select()
    .single();

  // Enqueue backup runs (one per database)
  const databases = ['odoo_prod', 'odoo_staging'];
  for (const db of databases) {
    await supabase.from('ops.runs').insert({
      session_id: session.id,
      kind: 'odoo_db_backup',
      lane: 'A',
      priority: 10,
      params: {
        odoo_db: db,
        s3_bucket: 'your-do-space/odoo-backups',
        retention_days: 30
      }
    });
  }

  console.log(`Backup session ${session.id} created with ${databases.length} runs`);
});
```

---

## 9) Monitoring & Alerting

### Ops Control Room Metrics Dashboard

**Superset Integration** (using read-only PG user):

```sql
-- Connect Superset to ops schema via superset_ro user
-- Database: postgresql://superset_ro:<PASSWORD>@<HOST>:5432/odoo_prod?options=-c%20search_path=ops,public

-- Query: Run Success Rate (Last 24h)
SELECT
  COUNT(*) FILTER (WHERE status = 'succeeded') * 100.0 / COUNT(*) AS success_rate,
  COUNT(*) AS total_runs,
  COUNT(*) FILTER (WHERE status = 'failed') AS failed_runs
FROM ops.runs
WHERE created_at > NOW() - INTERVAL '24 hours';

-- Query: Average Execution Time by Kind
SELECT
  kind,
  AVG(EXTRACT(EPOCH FROM (finished_at - started_at))) AS avg_duration_seconds,
  COUNT(*) AS run_count
FROM ops.runs
WHERE status = 'succeeded'
  AND created_at > NOW() - INTERVAL '7 days'
GROUP BY kind
ORDER BY avg_duration_seconds DESC;

-- Query: Stuck Runs (Real-time Alert)
SELECT
  id,
  kind,
  claimed_by,
  EXTRACT(EPOCH FROM (NOW() - heartbeat_at)) AS seconds_since_heartbeat
FROM ops.runs
WHERE status IN ('claimed', 'running')
  AND NOW() - heartbeat_at > INTERVAL '30 seconds';
```

### Mattermost Alerts (n8n Workflow)

```javascript
// n8n workflow: Ops Control Room Alerts
{
  "nodes": [
    {
      "name": "Schedule Trigger",
      "type": "n8n-nodes-base.cron",
      "parameters": {
        "triggerTimes": {
          "item": [
            { "mode": "everyMinute" }
          ]
        }
      }
    },
    {
      "name": "Query Stuck Runs",
      "type": "n8n-nodes-base.postgres",
      "parameters": {
        "query": "SELECT id, kind, claimed_by FROM ops.runs WHERE status IN ('claimed', 'running') AND NOW() - heartbeat_at > INTERVAL '30 seconds'"
      }
    },
    {
      "name": "Alert Mattermost",
      "type": "n8n-nodes-base.mattermost",
      "parameters": {
        "channel": "ops-alerts",
        "message": "🚨 **Stuck Run Detected**\n- Run ID: {{$json.id}}\n- Kind: {{$json.kind}}\n- Worker: {{$json.claimed_by}}"
      }
    }
  ]
}
```

---

## 10) Quick Start Integration Checklist

### Day 1: Infrastructure + Ops Schema

- [ ] Create DigitalOcean droplet (4vCPU/8GB, Singapore) - **SHARED with Odoo**
- [ ] Configure UFW firewall (22, 80, 443, 5432 from Supabase IP)
- [ ] Install PostgreSQL 16
- [ ] Create `ops` schema with grants for Supabase
- [ ] Configure remote PostgreSQL access (Supabase IP only)

### Day 2: Ops Workers + Edge Functions

- [ ] Deploy Supabase Edge Function: `ops-executor`
- [ ] Deploy Supabase Edge Function: `ops-recovery`
- [ ] Deploy Supabase Edge Function: `ops-backup-scheduler`
- [ ] Create DigitalOcean App: `ops-executor-workers` (3 instances)
- [ ] Verify worker health checks pass

### Day 3: Ops UI + Nginx

- [ ] Deploy Ops Control Room UI to Vercel
- [ ] Configure nginx reverse proxy (optional, if internal access needed)
- [ ] Configure Let's Encrypt SSL for ops.insightpulseai.com
- [ ] Test end-to-end: Create session → Enqueue run → Execute → Complete

### Day 4: Templates + Runbooks

- [ ] Create runbook template: `odoo_fresh_deploy`
- [ ] Create runbook template: `odoo_module_upgrade`
- [ ] Create runbook template: `odoo_db_backup`
- [ ] Test automated backup workflow
- [ ] Verify backup uploaded to S3/Spaces

### Day 5: Monitoring + Alerts

- [ ] Configure Superset dashboard for Ops metrics
- [ ] Set up n8n workflow for stuck-run alerts
- [ ] Configure Mattermost webhook for notifications
- [ ] Test alert triggers (manual stuck run)
- [ ] Document operational procedures

---

## 11) Cost Analysis

### Combined Odoo + Ops Control Room Stack

| Component | Service | Size | Monthly Cost |
|-----------|---------|------|--------------|
| **Shared Droplet** | DO Droplet | s-4vcpu-8gb | $48 |
| **Ops Workers** | DO App Platform | 3× basic-xs | $15 |
| **Ops UI** | Vercel | Hobby | $0 |
| **Ops Database** | Supabase (free tier) | - | $0 |
| **Backups** | DO Spaces | 100GB | $5 |
| **SSL** | Let's Encrypt | - | $0 |
| **Total** | | | **$68/mo** |

**Comparison**:
- **DIY (Odoo + Ops)**: $68/mo
- **Odoo.com SH (15 users)**: $240/mo
- **Savings**: $172/mo = **72% cost reduction**

---

## 12) References

- [Odoo 18 CE DIY Deployment Best Practices](../docs/ODOO_DEPLOYMENT_BEST_PRACTICES.md)
- [Ops Control Room Constitution](./constitution.md)
- [Ops Control Room PRD](./prd.md)
- [Ops Control Room Implementation Plan](./plan.md)
- [Ops Control Room Task Checklist](./tasks.md)
- [AIUX Ship v1.1.0 Parameterized PRD](../../docs/prd/AIUX_SHIP_PRD_v1.1.0.md)

---

**Version**: 1.0.0
**Status**: Ready for Integration
**Next**: Begin M0 (Fix Schema Access) + Day 1 Infrastructure Setup
