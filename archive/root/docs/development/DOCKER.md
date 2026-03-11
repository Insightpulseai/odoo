# Local Docker (SSOT)

## Source of Truth

- **Canonical**: `docker-compose.yml` (repo root)
- **Overlays**:
  - `docker-compose.dev.yml` — full stack (Superset, n8n, MCP)
  - `.devcontainer/docker-compose.devcontainer.yml` — devcontainer-only overrides
  - `docker-compose.override.yml` — developer local overrides (gitignored)

## Services

| Service | Image | Port | Purpose |
|---------|-------|------|---------|
| `db` | postgres:16-alpine | 5433 | PostgreSQL (tuned for Odoo) |
| `redis` | redis:7-alpine | 6379 | Session store / cache |
| `odoo` | odoo:19 | 8069, 8072 | Odoo CE ERP |
| `pgadmin` | dpage/pgadmin4 | 5050 | DB admin (profile: tools) |
| `mailpit` | axllent/mailpit | 8025, 1025 | Email testing (profile: tools) |

## Rules

- No secrets in git; use `.env.example` patterns.
- Compose defines services; docs describe environment mapping.
- Avoid cloning compose into multiple divergent files.
- Real `.env` files are gitignored; only examples are committed.

## Environment Mapping

| Env | Compose | Config |
|-----|---------|--------|
| dev | `docker-compose.yml` | `config/dev/odoo.conf` |
| staging | CI-triggered remote deploy | `config/staging/odoo.conf` |
| prod | `infra/deploy/docker-compose.prod.yml` | `config/prod/odoo.conf` |
