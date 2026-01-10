# Odoo 18 CE Fresh Redeploy PRD

## Version

| Field | Value |
|-------|-------|
| PRD ID | `ODOO18_DO_FRESH_REDEPLOY` |
| PRD Version | v0.1.0 |
| Ship Bundle Ref | `IPAI_SHIP_PRD_ODOO18_AIUX` v1.1.0 |
| Repo | `jgtolentino/odoo-ce` |
| Target Platform | DigitalOcean |

---

## 1. Goal

Establish a **deterministic, one-click bootstrap** deployment system for Odoo 18 CE on DigitalOcean that:

1. Provisions from repo with zero manual steps after secrets are configured
2. **Prevents recurring nginx 502** by enforcing health/readiness + correct longpolling route
3. Includes rollback on failed health gates
4. Produces proof artifacts for every deploy

---

## 2. Why 502 Bad Gateway Happens (Root Causes)

A 502 from nginx means nginx is up but the upstream (Odoo) isn't responding. Common causes:

| Cause | Symptom | Fix |
|-------|---------|-----|
| Odoo container down/crash-looping | Logs show OOM, bad module upgrade, missing deps | Health gate + readiness probe |
| Wrong upstream routing | nginx points to wrong container/port | Correct compose network config |
| Longpolling misrouted | `/longpolling` not proxied correctly | Explicit longpoll route in nginx |
| Timeouts | Workers blocked, DB slow | Increase `proxy_read_timeout` to 720s |
| Proxy mode mismatch | Redirect loops | Set `proxy_mode = True` in odoo.conf |
| No health gate | Deploy "succeeds" but app never ready | Mandatory health verification |

---

## 3. Architecture

### 3.1 Component Stack

```
┌─────────────────────────────────────────────────────────────────┐
│                     DigitalOcean Droplet                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   nginx (Edge)                                                  │
│   ├── :443 → odoo:8069 (main)                                  │
│   ├── :443/longpolling → odoo:8072 (websocket)                 │
│   └── SSL termination + timeouts                               │
│                                                                 │
│   ┌─────────────────────────────────────────────────────────┐  │
│   │  Docker Compose Stack                                    │  │
│   │  ├── odoo (ghcr.io/jgtolentino/odoo-ce:TAG)            │  │
│   │  ├── db (postgres:16-alpine)                            │  │
│   │  └── redis (optional, for sessions/queue)               │  │
│   └─────────────────────────────────────────────────────────┘  │
│                                                                 │
│   Object Storage (Spaces)                                       │
│   └── backups, filestore, artifacts                            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 3.2 Component Configuration

#### Edge (nginx/traefik)

```yaml
reverse_proxy: nginx
requires_longpoll_route: true
timeouts:
  proxy_read_timeout_seconds: 720
  proxy_connect_timeout_seconds: 60
  proxy_send_timeout_seconds: 600
```

#### Odoo

```yaml
version: 18.0-ce
workers: auto
proxy_mode: true
health_endpoint: /web/health
readiness_contract:
  - db_connect_ok
  - registry_loaded
  - module_state_ok
```

#### PostgreSQL

```yaml
mode: selfhost (postgres:16-alpine)
backups: scheduled
pitr: optional
```

#### Redis (Optional)

```yaml
enabled: true
use_for:
  - sessions
  - queue
```

---

## 4. Deployment Contract

### 4.1 Deploy Sequence

```
preflight → build → deploy → install → verify → publish proofs
                                          │
                                          ├── PASS → traffic cutover
                                          └── FAIL → rollback + alert
```

### 4.2 Build Artifact

```yaml
type: ghcr-image-tagged
registry: ghcr.io/jgtolentino/odoo-ce
tag_format: "{version}-{sha}"
strategy: rolling
```

### 4.3 Verify Steps (ALL must pass)

| Step | Check | Command | Expected |
|------|-------|---------|----------|
| 1 | Container up | `docker compose ps` | odoo running |
| 2 | Health internal | `curl -sS http://localhost:8069/web/health` | 200 |
| 3 | Health edge | `curl -sS https://erp.domain.com/web/health` | 200 |
| 4 | Login page | `curl -sS https://erp.domain.com/web/login` | 200 |
| 5 | Longpoll route | `curl -sS https://erp.domain.com/longpolling/poll` | 200/400 |
| 6 | DB reachable | `docker compose exec db pg_isready` | OK |

### 4.4 Rollback Rules

- If ANY verify step fails → rollback to previous image tag
- Rollback is automatic in CI workflow
- Manual rollback: `docker compose pull && docker compose up -d`

---

## 5. nginx Configuration (Critical for 502 Prevention)

### 5.1 Required Configuration

```nginx
upstream odoo {
    server 127.0.0.1:8069;
}

upstream odoo-longpolling {
    server 127.0.0.1:8072;
}

server {
    listen 443 ssl http2;
    server_name erp.insightpulseai.net;

    # SSL configuration
    ssl_certificate     /etc/letsencrypt/live/erp.insightpulseai.net/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/erp.insightpulseai.net/privkey.pem;
    ssl_protocols       TLSv1.2 TLSv1.3;

    # Proxy settings (CRITICAL for 502 prevention)
    proxy_read_timeout 720s;
    proxy_connect_timeout 60s;
    proxy_send_timeout 600s;

    # Headers
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto https;

    # Main Odoo routes
    location / {
        proxy_pass http://odoo;
        proxy_redirect off;
    }

    # Longpolling (CRITICAL - prevents websocket 502)
    location /longpolling {
        proxy_pass http://odoo-longpolling;
        proxy_redirect off;
    }

    # Websocket support
    location /websocket {
        proxy_pass http://odoo-longpolling;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # File uploads
    client_max_body_size 64m;
}
```

### 5.2 Common Misconfigurations to Avoid

| Mistake | Result | Fix |
|---------|--------|-----|
| No `/longpolling` route | Chat/notify 502 | Add explicit upstream |
| `proxy_read_timeout` < 120s | Long operations 504 | Set to 720s |
| Missing `X-Forwarded-Proto` | OAuth redirect fails | Add header |
| No healthcheck in compose | False "healthy" status | Add curl healthcheck |

---

## 6. Proof Artifacts

### 6.1 Required Artifacts per Deploy

```json
{
  "deploy_id": "deploy-{timestamp}",
  "artifacts": [
    {
      "name": "module_install_log",
      "path": "proofs/module_install.log",
      "required": true
    },
    {
      "name": "healthcheck_log",
      "path": "proofs/healthcheck.log",
      "required": true
    },
    {
      "name": "manifest_version",
      "value": "1.1.0",
      "required": true
    },
    {
      "name": "git_sha",
      "value": "{commit_sha}",
      "required": true
    },
    {
      "name": "status_summary",
      "path": "proofs/deploy_status.json",
      "required": true
    }
  ]
}
```

### 6.2 Proof Schema

See: `docs/proofs/PROD_DEPLOY_PROOF_SCHEMA.json`

---

## 7. Fresh Bootstrap Runbook

### 7.1 Prerequisites

1. DigitalOcean droplet provisioned (Ubuntu 22.04+)
2. Domain DNS pointing to droplet IP
3. GitHub Secrets configured:
   - `GHCR_TOKEN` - GitHub Container Registry token
   - `DO_SSH_KEY` - SSH private key for droplet
   - `DB_PASSWORD` - PostgreSQL password
   - `ADMIN_PASSWD` - Odoo admin password

### 7.2 Bootstrap Steps

```bash
# 1. Clone repo
git clone https://github.com/jgtolentino/odoo-ce.git /opt/odoo-ce
cd /opt/odoo-ce

# 2. Copy environment template
cp deploy/.env.production.template .env
# Edit .env with your secrets (DO NOT commit)

# 3. Login to GHCR
echo $GHCR_TOKEN | docker login ghcr.io -u USERNAME --password-stdin

# 4. Pull and start
docker compose -f deploy/docker-compose.prod.yml pull
docker compose -f deploy/docker-compose.prod.yml up -d

# 5. Wait for DB ready
sleep 30

# 6. Install ship modules
docker compose -f deploy/docker-compose.prod.yml exec odoo \
  odoo -d odoo -i ipai_theme_aiux,ipai_aiux_chat,ipai_ask_ai,ipai_document_ai,ipai_expense_ocr \
  --stop-after-init

# 7. Restart
docker compose -f deploy/docker-compose.prod.yml restart odoo

# 8. Verify
./scripts/deploy/verify_prod.sh
```

### 7.3 Rollback Procedure

```bash
# If current deploy fails, rollback to previous tag
export PREVIOUS_TAG="v1.0.0-abc123"
docker compose -f deploy/docker-compose.prod.yml pull odoo:$PREVIOUS_TAG
docker compose -f deploy/docker-compose.prod.yml up -d odoo
./scripts/deploy/verify_prod.sh
```

---

## 8. Debugging 502 Errors

### 8.1 Diagnostic Checklist

```bash
# 1. Check container status
docker compose -f deploy/docker-compose.prod.yml ps
docker compose -f deploy/docker-compose.prod.yml logs --tail=200 odoo

# 2. Check internal health
docker compose -f deploy/docker-compose.prod.yml exec odoo \
  curl -sS http://localhost:8069/web/health

# 3. Check nginx config
nginx -t
cat /etc/nginx/sites-enabled/odoo.conf

# 4. Check upstream connectivity
curl -sS http://127.0.0.1:8069/web/login
curl -sS http://127.0.0.1:8072/longpolling/poll

# 5. Check nginx logs
tail -100 /var/log/nginx/error.log
```

### 8.2 Common Fixes

| Symptom | Cause | Fix |
|---------|-------|-----|
| 502 on all routes | Odoo container down | `docker compose restart odoo` |
| 502 on /longpolling | No longpoll upstream | Add nginx longpoll config |
| 502 after module upgrade | Bad module state | `odoo -u web,base --stop-after-init` |
| Intermittent 502 | Worker timeout | Increase `proxy_read_timeout` |
| 502 after SSL change | nginx not reloaded | `nginx -s reload` |

---

## 9. End State JSON

```json
{
  "spec_version": "2026-01-08",
  "project": "odoo-ce",
  "prd": {
    "ship_prd_id": "IPAI_SHIP_PRD_ODOO18_AIUX",
    "ship_prd_version": "1.1.0",
    "redeploy_prd_id": "ODOO18_DO_FRESH_REDEPLOY",
    "redeploy_prd_version": "0.1.0"
  },
  "fresh_redeploy_on_digitalocean": {
    "goals": [
      "one-click bootstrap from repo",
      "zero manual steps after secrets are configured",
      "deterministic health verification before traffic cutover",
      "rollback on failed health"
    ],
    "components": {
      "edge": {
        "reverse_proxy": "nginx",
        "requires_longpoll_route": true,
        "timeouts": {
          "proxy_read_timeout_seconds": 720,
          "proxy_connect_timeout_seconds": 60
        }
      },
      "odoo": {
        "version": "18.0-ce",
        "workers": "auto",
        "proxy_mode": true,
        "health_endpoint": "/web/health",
        "readiness_contract": [
          "db_connect_ok",
          "registry_loaded",
          "module_state_ok"
        ]
      },
      "postgres": {
        "mode": "selfhost",
        "image": "postgres:16-alpine",
        "backups": "scheduled"
      },
      "redis": {
        "enabled": true,
        "use_for": ["sessions", "queue"]
      }
    },
    "deployment_contract": {
      "build_artifact": "ghcr-image-tagged",
      "deploy_strategy": "rolling",
      "verify_steps": [
        "container_up",
        "health_internal_200",
        "health_edge_200",
        "login_page_200",
        "longpoll_route_ok"
      ],
      "rollback_on_failure": true
    }
  }
}
```

---

## 10. References

- [Ship PRD v1.1.0](./IPAI_SHIP_PRD_ODOO18_AIUX.md)
- [Ship Verification Runbook](../ops/SHIP_VERIFICATION.md)
- [Production Redeploy Runbook](../ops/production_redeploy_runbook.md)
- [Cloudpepper Ops Patterns](https://cloudpepper.io/docs)

---

*Last updated: 2026-01-08*
