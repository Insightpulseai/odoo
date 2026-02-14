# PRD: Infrastructure Well-Architected Assessment System

## Goal

Implement a systematic assessment framework to validate the DigitalOcean/Docker/Cloudflare infrastructure against Well-Architected 5 pillars.

## Pillars

1. **Reliability (0.25)**: Container restart policies, healthchecks, backups.
2. **Security (0.25)**: Secret management, SSL/TLS (Cloudflare), firewall rules.
3. **Cost Optimization (0.20)**: Rightsizing (Droplets), caching (Cloudflare).
4. **Operational Excellence (0.15)**: Logging drivers, image pinning, state locking.
5. **Performance Efficiency (0.15)**: Volume config, CDN usage.

## Functional Requirements

- **Audit Script**: `check_infra_waf.py` using `lib.py`.
- **Local Mode**: Parse `docker-compose.prod.yaml` and `*.tf` files.
- **API Mode**: Optional `doctl` checks (future).
- **Reporting**: Console summary + JSON evidence.

## Non-Functional Requirements

- **Performance**: Local checks < 5s.
- **Dependency**: `pyyaml`, `python-dotenv`.
