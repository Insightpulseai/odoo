# Constitution: Azure Reference Architecture Parity

## Non-Negotiable Rules

1. **Self-hosted only**: All components must run on DigitalOcean droplets, Docker containers, or OSS SaaS (Cloudflare free/pro). No Azure/AWS/GCP managed services.
2. **Cost ceiling**: Total monitoring overhead must stay under $20/month additional infrastructure cost (CPU/RAM on existing droplet).
3. **No EE dependencies**: Auth module must use OCA `auth_oidc` + `auth_totp`, never Odoo Enterprise modules.
4. **Workspace-scoped**: All configuration must respect the workspace boundary (`insightpulseai-prod`, `insightpulseai-dev`, `tbwa-smp-prod`). Monitoring dashboards and auth providers are per-workspace.
5. **Additive only**: No destructive changes to existing compose files, Odoo config, or running services. All new services use Docker Compose profiles or overlay files.
6. **Evidence-driven**: Every score change must have a verification script that produces machine-readable pass/fail output.
7. **Secrets via env**: No secrets in YAML, JSON, or Python. All credentials via `.env` or Docker secrets.

## Architectural Constraints

- Prometheus retention: 15 days max (disk budget).
- Grafana: anonymous read access disabled; admin via env-injected credentials.
- CDN: Cloudflare proxy mode; never cache `/web/*`, `/longpolling/*`, `/xmlrpc/*`.
- Auth: OAuth provider config is data XML, not hardcoded. Provider credentials from env.
- Backup verification: must complete in < 60 seconds, idempotent, safe for cron.

## Quality Gates

- All verification scripts must exit 0 before merge.
- WAF aggregate score must be >= 83 after implementation (projected: 83-85).
- No new `fail` status items in scorecard.json.
