# Operations Stack Overview

## Introduction

The InsightPulse AI operations stack (`ipai-ops-stack`) hosts all runtime collaboration and automation services. These services are deployed separately from Odoo CE to maintain clean separation of concerns.

## Services

| Service | URL | Purpose |
|---------|-----|---------|
| Mattermost | https://chat.insightpulseai.com | Team chat & messaging |
| Focalboard | https://boards.insightpulseai.com | Kanban project boards |
| n8n | https://n8n.insightpulseai.com | Workflow automation |
| Superset | https://superset.insightpulseai.com | Business intelligence |

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     ipai-ops-stack                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐           │
│   │Mattermost│ │Focalboard│ │   n8n   │  │ Superset│           │
│   │  :8065   │ │  :8000   │  │  :5678  │  │  :8088  │           │
│   └────┬─────┘ └────┬─────┘  └────┬────┘  └────┬────┘           │
│        │            │             │            │                 │
│   ┌────┴────────────┴─────────────┴────────────┴────┐           │
│   │              Caddy Reverse Proxy                │           │
│   │              (TLS termination)                  │           │
│   └────────────────────────┬────────────────────────┘           │
│                            │                                     │
│   ┌────────────────────────┴────────────────────────┐           │
│   │              PostgreSQL (shared)                │           │
│   │   - mattermost_db                               │           │
│   │   - focalboard_db                               │           │
│   │   - superset_db                                 │           │
│   └─────────────────────────────────────────────────┘           │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ HTTPS
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                        Internet                                  │
│   chat.insightpulseai.com                                       │
│   boards.insightpulseai.com                                     │
│   n8n.insightpulseai.com                                        │
│   superset.insightpulseai.com                                   │
└─────────────────────────────────────────────────────────────────┘
```

## Repository Structure

```
ipai-ops-stack/
├── docker/
│   ├── docker-compose.yml
│   ├── .env.example
│   └── .gitignore
├── caddy/
│   └── Caddyfile
├── mattermost/
│   ├── config/
│   └── plugins/
├── focalboard/
│   └── config.json
├── n8n/
│   ├── workflows/          # Committed workflow JSONs
│   ├── credentials/        # GITIGNORED
│   └── bootstrap/
│       └── import_workflows.sh
├── superset/
│   └── superset_config.py
├── scripts/
│   ├── up.sh
│   ├── down.sh
│   ├── logs.sh
│   ├── healthcheck.sh
│   ├── backup.sh
│   └── restore.sh
└── docs/
    ├── SETUP.md
    ├── DNS_TLS.md
    ├── UPGRADE.md
    └── BACKUP.md
```

## Odoo Integration

### What Lives in odoo-ce

- Connector configurations (URLs, settings)
- Webhook endpoints (receive from ops services)
- Outbound webhook jobs (send to ops services)
- Audit logs
- Data models for sync tracking

### What Does NOT Live in odoo-ce

- Mattermost source code
- Focalboard source code
- n8n source code
- Superset source code
- Docker images
- Runtime configuration

## Integration Modules

| Module | Purpose |
|--------|---------|
| `ipai_integrations` | Central admin UI |
| `ipai_mattermost_connector` | Mattermost API client |
| `ipai_focalboard_connector` | Focalboard API client |
| `ipai_n8n_connector` | n8n API client |
| `ipai_superset_connector` | Superset embedding |

## Health Checks

### From Odoo

Each connector provides a `Test Connection` button that verifies:
- Service is reachable
- Authentication is valid
- API version is compatible

### From Ops Stack

```bash
# Run all health checks
./scripts/healthcheck.sh

# Individual checks
curl https://chat.insightpulseai.com/api/v4/system/ping
curl https://boards.insightpulseai.com/api/v2/ping
curl https://n8n.insightpulseai.com/healthz
curl https://superset.insightpulseai.com/health
```

## Deployment

### Prerequisites

- Docker & Docker Compose
- Domain with DNS configured
- SSL certificates (Caddy handles automatically)

### Quick Start

```bash
cd ipai-ops-stack
cp docker/.env.example docker/.env
# Edit .env with your secrets

./scripts/up.sh
./scripts/healthcheck.sh
```

### DNS Records

| Subdomain | Type | Value |
|-----------|------|-------|
| chat | A | <droplet IP> |
| boards | A | <droplet IP> |
| n8n | A | <droplet IP> |
| superset | A | <droplet IP> |

## Maintenance

### Backup

```bash
./scripts/backup.sh  # Creates timestamped backup
```

### Restore

```bash
./scripts/restore.sh backup-2024-01-15.tar.gz
```

### Upgrade

```bash
./scripts/down.sh
# Edit docker-compose.yml with new image versions
./scripts/up.sh
./scripts/healthcheck.sh
```

## Related Documentation

- [Mattermost Integration](./MATTERMOST.md)
- [Focalboard Integration](./FOCALBOARD.md)
- [n8n Integration](./N8N.md)
- [Superset Integration](../ipai_superset_connector/README.md)
