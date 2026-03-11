# Constitution: Infrastructure Well-Architected Assessment System

## Core Principles

1. **Docker-First**: Primary source of truth for compute is `infra/docker-compose.prod.yaml`.
2. **Immutable Infrastructure**: Changes must be made via IaC (Terraform) or Compose, never manually on servers.
3. **Secret Zero**: No secrets in code. all secrets must be injected via env vars or secret managers.
4. **Backup-First**: Data persistence layers (PostgreSQL) must have automated, tested backups.

## Non-Negotiables

- **PR Gate Speed**: Must complete in < 5 minutes (Local checks only).
- **Critical Checks**:
  - `restart: always` or `unless-stopped` for all long-running services (Reliability).
  - `healthcheck` defined for all exposed services (Reliability).
  - No hardcoded secrets in `docker-compose.yaml` (Security).
  - No `image: latest` tags in production (Ops/Reliability).
- **Scoring**: Must use 0-4 maturity scale.

## Integration Standards

- Must output standard JSON evidence to `docs/evidence/`.
- Must handle missing API credentials gracefully (SKIP checks).
