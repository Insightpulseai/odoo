# Canonical URLs & Subdomains — InsightPulse AI

> **SSOT**: This document is generated from `infra/dns/subdomain-registry.yaml`.
> Edit the YAML, run the generator, commit all artifacts together.
> CI validates sync via `.github/workflows/dns-sync-check.yml`.

Last updated: 2026-02-17

---

## Production Services

| URL | Service | Owner | Health Check | Success Criteria | SSOT Pointer |
|-----|---------|-------|--------------|------------------|--------------|
| `https://erp.insightpulseai.com` | Odoo ERP (CE 19.0) | Odoo CE 19.0 | `/web/login` | HTTP 200-399; login form renders; `/web` redirects correctly; core CSS/JS assets load | `subdomain-registry.yaml#erp` |
| `https://n8n.insightpulseai.com` | n8n Workflow Automation | n8n automation | `/healthz` | HTTP 200-399; UI loads; `/healthz` returns OK; workflows executable via API key | `subdomain-registry.yaml#n8n` |
| `https://mcp.insightpulseai.com` | MCP Gateway (11 servers) | MCP coordination | `/healthz` | HTTP 200-399; `/healthz` returns JSON OK; MCP routes to configured servers | `subdomain-registry.yaml#mcp` |
| `https://superset.insightpulseai.com` | Apache Superset BI | Apache Superset BI | `/health` | HTTP 200-399; `/health` returns OK; `/login` loads; dashboards reachable behind auth | `subdomain-registry.yaml#superset` |
| `https://ocr.insightpulseai.com` | PaddleOCR Microservice | PaddleOCR microservice | `/health` | HTTP 200-399; `/health` returns JSON OK; OCR endpoint accepts image payloads | `subdomain-registry.yaml#ocr` |
| `https://auth.insightpulseai.com` | Authentication Service | Authentication service | `/.well-known/openid-configuration` | HTTP 200-399; OIDC discovery document returns valid JSON; token endpoint reachable | `subdomain-registry.yaml#auth` |
| `https://www.insightpulseai.com` | WWW Redirect | Redirect to apex | `/` | Redirects to `https://insightpulseai.com` or serves same content; no mixed canonical | `subdomain-registry.yaml#www` |
| `https://insightpulseai.com` | Root / Marketing Site | Apex domain | `/` | HTTP 200-399; correct TLS; fast load; no dead links; canonical domain (not `.net`) | Cloudflare apex config |

### Planned (Not Yet Active)

| URL | Service | Owner | Health Check | Success Criteria | SSOT Pointer |
|-----|---------|-------|--------------|------------------|--------------|
| `https://api.insightpulseai.com` | API Gateway | API Gateway | `/api/health` | HTTP 200-399; `/api/health` returns JSON OK; API routes resolve | `subdomain-registry.yaml#api` (status: planned) |

---

## Staging Services

| URL | Service | Owner | Health Check | Success Criteria | SSOT Pointer |
|-----|---------|-------|--------------|------------------|--------------|
| `https://stage-erp.insightpulseai.com` | Odoo CE 19.0 (staging) | Odoo CE 19.0 (staging) | `/web/login` | HTTP 200-399; uses `odoo_stage` DB; no prod secrets; login form renders | `subdomain-registry.yaml#stage-erp` |
| `https://stage-n8n.insightpulseai.com` | n8n (staging) | n8n automation (staging) | `/healthz` | HTTP 200-399; isolated credentials; staging workflows only | `subdomain-registry.yaml#stage-n8n` |
| `https://stage-mcp.insightpulseai.com` | MCP Gateway (staging) | MCP coordination (staging) | `/healthz` | HTTP 200-399; `/healthz` OK; routes point to staging MCP servers | `subdomain-registry.yaml#stage-mcp` |
| `https://stage-superset.insightpulseai.com` | Superset BI (staging) | Apache Superset BI (staging) | `/health` | HTTP 200-399; `/health` OK; staging dashboards | `subdomain-registry.yaml#stage-superset` |
| `https://stage-api.insightpulseai.com` | API Gateway (staging) | API Gateway (staging) | `/api/health` | HTTP 200-399; `/api/health` OK; staging API routes | `subdomain-registry.yaml#stage-api` |
| `https://stage-auth.insightpulseai.com` | Auth (staging) | Authentication service (staging) | `/.well-known/openid-configuration` | HTTP 200-399; OIDC discovery valid; staging credentials | `subdomain-registry.yaml#stage-auth` |
| `https://stage-ocr.insightpulseai.com` | PaddleOCR (staging) | PaddleOCR microservice (staging) | `/health` | HTTP 200-399; `/health` OK; staging OCR endpoint | `subdomain-registry.yaml#stage-ocr` |

---

## Local Development

| URL | Service | Success Criteria |
|-----|---------|------------------|
| `http://localhost:8069` | Odoo dev local | `/web/login` OK; uses `odoo_dev` DB; dev services reachable |
| `http://localhost:5678` | n8n dev local | UI loads; workflows editable |
| `http://localhost:8088` | Superset dev local | `/health` OK; login page loads |
| `http://localhost:3000` | Auth / Next.js dev | Service responds |
| `http://localhost:5432` | PostgreSQL | Connection accepted |

---

## Drift Analysis (Found in Code but NOT in SSOT)

These subdomains are referenced in active (non-archive) code but are **not defined** in `infra/dns/subdomain-registry.yaml`. Each needs resolution: add to SSOT, or remove references.

| Subdomain | Refs | Status | Assessment | Recommended Action |
|-----------|------|--------|------------|-------------------|
| `ipa.insightpulseai.com` | 148 | MIGRATED | Old n8n hostname; migrated to `n8n.insightpulseai.com` | Remove all refs from code |
| `ops.insightpulseai.com` | 63 | UNDOCUMENTED | Operations console; actively referenced in deployment docs | Add to SSOT if prod, else remove |
| `chat.insightpulseai.com` | 57 | DEPRECATED | Mattermost (deprecated 2026-01-28, replaced by Slack) | Remove all refs from code |
| `odoo.insightpulseai.com` | 40 | LEGACY | Old hostname; canonical is `erp.insightpulseai.com` | Remove all refs, use `erp` |
| `staging.insightpulseai.com` | 32 | UNCLEAR | Generic staging ref; SSOT uses `stage-*` pattern | Clarify or remove |
| `plane.insightpulseai.com` | 18 | UNDOCUMENTED | Project management (Plane.so); has CI workflow | Add to SSOT if prod |
| `boards.insightpulseai.com` | 12 | UNDOCUMENTED | Focalboard/kanban boards | Add to SSOT or remove |
| `docs.insightpulseai.com` | 5 | UNDOCUMENTED | Documentation portal | Clarify purpose or remove |
| `app.insightpulseai.com` | 2 | UNDOCUMENTED | SaaS app frontend (Supabase OAuth ref) | Clarify or remove |
| `storybook.insightpulseai.com` | 2 | SANDBOX | UI component library | Archive or add if needed |
| `gpu.insightpulseai.com` | 1 | ACTIVE CONFIG | GPU/LLM inference endpoint in agent config | Add to SSOT |
| `mlflow.insightpulseai.com` | 1 | CONFIG | ML experiment tracking | Add if production |
| `keycloak.insightpulseai.com` | 1 | RESEARCH | Identity provider reference in sandbox doc | No action (sandbox artifact) |

---

## Deprecated Services

| Subdomain | Deprecated Date | Replacement | DNS Removed | Container Removed |
|-----------|----------------|-------------|-------------|-------------------|
| `affine.insightpulseai.com` | 2026-02-09 | None | Yes | Yes |
| `*.insightpulseai.net` (all) | 2026-02 | `*.insightpulseai.com` | Yes | N/A |
| `mattermost.insightpulseai.com` | 2026-01-28 | Slack | Pending cleanup | Yes |
| `mg.insightpulseai.com` | 2026-02 | Zoho Mail SMTP | Pending cleanup | Yes |
| `ipa.insightpulseai.com` | 2026-02 | `n8n.insightpulseai.com` | Pending cleanup | N/A (alias) |

---

## Stale Reference Summary

### `.net` Domain References (60+ occurrences in active files)

Critical files requiring update:

| File | Issue | Fix |
|------|-------|-----|
| `ipai-platform/nginx/conf.d/sites/odoo-prod.conf` | `erp.insightpulseai.net` | Update to `.com` |
| `ipai-platform/.env.example` | DOMAIN/ODOO_DOMAIN vars | Update to `.com` |
| `ipai-platform/odoo/odoo.conf` | SMTP user | Update to `.com` |
| `supabase/migrations/20251227_database_webhooks.sql` | Webhook URLs | Update to `n8n.insightpulseai.com` |
| `docs/templates/ipai-ops-stack/caddy/Caddyfile` | All subdomain refs | Update to `.com` |

### Old `ipa.insightpulseai.com` References (6 critical files)

| File | Fix |
|------|-----|
| `agents/odoo_reverse_mapper.yaml` | Update to `n8n.insightpulseai.com` |
| `agents/loops/clarity_ppm_reverse.yaml` | Update to `n8n.insightpulseai.com` |
| `workflows/n8n_ocr_expense_webhook.json` | Update instanceId |
| `workflows/n8n_bir_deadline_webhook.json` | Update instanceId |
| `workflows/n8n_scout_sync_webhook.json` | Update instanceId |
| `specs/003-ai-enrichment/odoo_automation_action.py` | Update webhook URL |

---

## n8n Workflow Locations

| Path | Count | Status | Notes |
|------|-------|--------|-------|
| `automations/n8n/workflows/` | 31 | **Canonical** | Single source of truth for n8n workflows |
| `workflows/n8n/` | 7 | **Legacy** | Audit for duplicates; migrate unique ones to `automations/n8n/` |
| `workflows/*.json` | 4 | **Stale** | Webhook definitions with old `ipa.` domain |
| `notion-n8n-monthly-close/workflows/` | 10 | **Archived** | Historical deployment artifacts |

---

## Verification

```bash
# DNS baseline check
./scripts/verify-dns-baseline.sh

# Service health checks
./scripts/verify-service-health.sh

# DNS sync CI validation
# Triggered by: .github/workflows/dns-sync-check.yml

# JSON schema validation
jq . docs/arch/runtime_identifiers.json
```

---

## Related Files

| File | Purpose |
|------|---------|
| `infra/dns/subdomain-registry.yaml` | **DNS SSOT** (edit this) |
| `docs/arch/runtime_identifiers.json` | Generated runtime config |
| `docs/arch/PROD_RUNTIME_SNAPSHOT.md` | Production runtime state |
| `docs/arch/RUNTIME_IDENTIFIERS.md` | Runtime identifiers reference |
| `scripts/generate-dns-artifacts.sh` | Generates Terraform + JSON from YAML |
| `scripts/verify-dns-baseline.sh` | DNS verification script |
| `scripts/verify-service-health.sh` | Service health check script |
| `.github/workflows/dns-sync-check.yml` | CI enforcement |
| `reports/url_inventory.json` | Machine-readable inventory + drift |
