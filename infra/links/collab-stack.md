# Collaboration Stack Links

> This file contains pointers to the external operations stack.
> No secrets should be stored here.

## Repository

**GitHub:** https://github.com/jgtolentino/ipai-ops-stack

## Production URLs

| Service | URL | Status Page |
|---------|-----|-------------|
| Mattermost | https://chat.insightpulseai.net | /api/v4/system/ping |
| Focalboard | https://boards.insightpulseai.net | /api/v2/ping |
| n8n | https://n8n.insightpulseai.net | /healthz |
| Superset | https://superset.insightpulseai.net | /health |

## Infrastructure

- **Cloud Provider:** DigitalOcean
- **Region:** SGP1 (Singapore)
- **Reverse Proxy:** Caddy (automatic TLS)
- **Database:** PostgreSQL 16 (shared instance)

## Deployment

The ops stack is deployed via Docker Compose on a DigitalOcean droplet.

See the `ipai-ops-stack` repository for:
- `docker/docker-compose.yml` - Service definitions
- `scripts/up.sh` - Start stack
- `scripts/down.sh` - Stop stack
- `scripts/healthcheck.sh` - Verify all services
- `scripts/backup.sh` - Database backups

## Odoo Integration

Integration modules in this repository:

| Module | Location |
|--------|----------|
| `ipai_integrations` | `addons/ipai/ipai_integrations/` |
| `ipai_mattermost_connector` | `addons/ipai/ipai_mattermost_connector/` |
| `ipai_focalboard_connector` | `addons/ipai/ipai_focalboard_connector/` |
| `ipai_n8n_connector` | `addons/ipai/ipai_n8n_connector/` |
| `ipai_superset_connector` | `addons/ipai/ipai_superset_connector/` |

## Configuration

System parameters to configure in Odoo:

```
ipai_integrations.mattermost_url = https://chat.insightpulseai.net
ipai_integrations.focalboard_url = https://boards.insightpulseai.net
ipai_integrations.n8n_url = https://n8n.insightpulseai.net
```

Authentication tokens should be stored in secure system parameters
(not committed to any repository).

## Contacts

- **Ops Channel:** #infrastructure on chat.insightpulseai.net
- **Integration Channel:** #odoo-integrations on chat.insightpulseai.net
