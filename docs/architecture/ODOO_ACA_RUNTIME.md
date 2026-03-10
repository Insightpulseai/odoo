# Odoo ACA Runtime Architecture

## Role Split

Odoo CE 19 runs as 3 long-running Container Apps + 1 init job on Azure Container Apps.

| Service | Role | Ingress | Replicas | Notes |
|---------|------|---------|----------|-------|
| `odoo-web` | HTTP server | Internal (Front Door routes) | 1–3 | Only service reachable externally |
| `odoo-worker` | Background queue | None | 1–2 | Processes async jobs |
| `odoo-cron` | Scheduled tasks | None | 1 (fixed) | Runs `ir.cron` actions |
| `odoo-init` | Schema init/migrate | None (job) | 0 (on-demand) | One-shot for deploy/migration |

### Why Separate Services?

- **Isolation**: HTTP latency is not affected by heavy background jobs
- **Scaling**: Web scales on HTTP concurrency; workers scale on queue depth; cron is fixed at 1
- **Cron safety**: Single replica prevents duplicate scheduled action execution
- **Init safety**: Database migrations run as a job, not inside a live container

## Ingress Policy

```
Internet → Front Door → odoo-web (internal FQDN)
                          ↓ shared DB
           odoo-worker ← (no ingress, same DB)
           odoo-cron   ← (no ingress, same DB)
```

Only `odoo-web` has an ingress block. Worker and cron have no ingress configuration — they are not routable from any source.

## Secret Flow

```
Azure Key Vault
  ├── pg-odoo-user       → DB_USER env var (all 3 services)
  ├── pg-odoo-password   → DB_PASSWORD env var (all 3 services)
  └── (other secrets)    → referenced via managed identity
```

Secrets are injected via Container Apps Key Vault references using a user-assigned managed identity. No secrets in Bicep parameters or environment variables.

## Scaling

| Service | Strategy | Trigger | Min | Max |
|---------|----------|---------|-----|-----|
| odoo-web | HTTP auto-scale | 50 concurrent requests | 1 | 3 |
| odoo-worker | Manual | N/A | 1 | 2 |
| odoo-cron | Fixed | N/A | 1 | 1 |

## Health Probes

| Service | Liveness | Readiness | Startup |
|---------|----------|-----------|---------|
| odoo-web | HTTP GET /web/health (30s) | HTTP GET /web/health (10s) | HTTP GET /web/health (5s, 30 retries) |
| odoo-worker | TCP 8069 (60s) | — | — |
| odoo-cron | TCP 8069 (60s) | — | — |

Workers and cron use TCP probes because they don't serve HTTP (started with `--no-http`).

## Init Job Strategy

`odoo-init` is a Container App Job (not a long-running app):
- Triggered manually or by CI/CD pipeline on deploy
- Runs `odoo --stop-after-init -d odoo -i base` (or module install/upgrade)
- Exits when complete — no ongoing resource cost
- Must complete successfully before web/worker/cron start serving new code

## Rollback

| Layer | Rollback Method |
|-------|----------------|
| Container revision | `az containerapp revision activate --revision <previous>` |
| Database | PG Flexible Server point-in-time restore (up to 35 days) |
| DNS | Revert Cloudflare CNAME to A 178.128.112.214 (DigitalOcean) |
| Full stack | All three above in sequence |

## Files

| File | Purpose |
|------|---------|
| `infra/azure/modules/aca-odoo-services.bicep` | Bicep module (web + worker + cron) |
| `infra/azure/modules/container-apps.bicep` | Generic ACA module (all 9 services) |
| `ssot/azure/odoo-runtime.yaml` | Canonical role SSOT |
| `scripts/azure/validate-odoo-aca.sh` | Runtime validator |
| `infra/azure/parameters/odoo-runtime-prod.parameters.json` | Production sizing |
