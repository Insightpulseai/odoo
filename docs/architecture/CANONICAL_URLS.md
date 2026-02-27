# Canonical URLs & Subdomains — InsightPulse AI

> **SSOT**: DNS records live in `infra/cloudflare/zones/insightpulseai.com/records.yaml`.
> Edit the YAML, commit + push → CI applies on merge to main.
> CI gates: `cloudflare-authority-gate.yml` (NS check) + `cloudflare-dns-drift.yml` (drift check).
> Spec bundle: `spec/insightpulseai-com/`

Last updated: 2026-02-27

---

## Authoritative DNS Status

| Check | Status | Proof mechanism |
|-------|--------|----------------|
| **Cloudflare is authoritative** | ✅ Confirmed 2026-02-27 | `dig NS insightpulseai.com` → `edna.ns.cloudflare.com` + `keanu.ns.cloudflare.com` (verified by `scripts/cloudflare/verify_authoritative.py`) |
| **CI authority gate** | ✅ Enforced | `.github/workflows/cloudflare-authority-gate.yml` — blocks DNS PRs if not authoritative |
| **DNS records in SSOT** | ✅ Committed | `infra/cloudflare/zones/insightpulseai.com/records.yaml` |
| **Apply on merge** | ✅ Configured | `.github/workflows/cloudflare-dns-apply.yml` (push to main) |

### Authoritative nameservers (confirmed)

Cloudflare is the authoritative resolver for `insightpulseai.com`:
- `edna.ns.cloudflare.com`
- `keanu.ns.cloudflare.com`

DNS record commits in `infra/cloudflare/zones/` **take effect on next apply-on-merge run**.
The CI authority gate will pass — no `cf-ns-pending` label bypass needed.

Verify current status: `python3 scripts/cloudflare/verify_authoritative.py`

### DNS record SSOT location

```
infra/cloudflare/zones/insightpulseai.com/records.yaml   ← SSOT (edit this)
artifacts/cloudflare/zone_state.json                      ← generated output (do not edit)
```

> `artifacts/` is **output-only**. All SSOT inputs live in `infra/`.

---

## Redirect Policy

| From | To | Method | Rationale |
|------|----|--------|-----------|
| `https://www.insightpulseai.com` | `https://insightpulseai.com` | 301 | Apex is canonical; single canonical URL for SEO + caching |
| `http://*.insightpulseai.com` | `https://*.insightpulseai.com` | 301 | HTTPS only; HSTS enabled |
| `*.insightpulseai.net` | N/A | **Deprecated** | `.net` domain fully retired 2026-02 |

---

## Cross-Cutting Rules

1. **`.com` only** — no `.net` anywhere in code, docs, DNS, emails, or redirects
2. **DNS managed via IaC** — `infra/dns/subdomain-registry.yaml` is the single source; Cloudflare IaC under `infra/cloudflare/`
3. **Healthcheck-covered** — every production service has a defined health endpoint
4. **Content signature check** — healthcheck validates correct app is served on correct domain (prevents misrouting)
5. **No secrets in repo** — env-only configuration
6. **SSOT-first** — any new subdomain must be added to `subdomain-registry.yaml` before code references it
7. **CI-enforced** — `.github/workflows/domain-lint.yml` blocks `.net` regressions; `dns-sync-check.yml` validates SSOT sync

---

## Production Services

| URL | Service | Owner | Health Check | Success Criteria | SSOT Pointer |
|-----|---------|-------|--------------|------------------|--------------|
| `https://insightpulseai.com` | Marketing Site (apex) | Apex domain | `/` | HTTP 200-399; correct TLS (Full strict); correct content signature (InsightPulseAI branding); fast load (LCP < 2.5s) | Cloudflare apex config |
| `https://www.insightpulseai.com` | WWW Redirect | Redirect to apex | `/` | HTTP 301 → `https://insightpulseai.com`; no direct content served; no mixed canonical | `subdomain-registry.yaml#www` |
| `https://erp.insightpulseai.com` | Odoo ERP (CE 19.0) | Odoo CE 19.0 | `/web/login` | HTTP 200-399; login form renders; `/web` redirects correctly; core CSS/JS assets load; Odoo branding visible | `subdomain-registry.yaml#erp` |
| `https://n8n.insightpulseai.com` | n8n Workflow Automation | n8n automation | `/healthz` | HTTP 200-399; n8n UI loads (not another app); `/healthz` returns OK; workflows executable via API key | `subdomain-registry.yaml#n8n` |
| `https://mcp.insightpulseai.com` | MCP Gateway (11 servers) | MCP coordination | `/healthz` | HTTP 200-399; `/healthz` returns JSON OK; MCP routes to configured servers; timeouts + headers correct | `subdomain-registry.yaml#mcp` |
| `https://superset.insightpulseai.com` | Apache Superset BI | Apache Superset BI | `/health` | HTTP 200-399; `/health` returns OK; `/login` loads; correct Postgres datasource; no write permissions | `subdomain-registry.yaml#superset` |
| `https://ocr.insightpulseai.com` | PaddleOCR Microservice | PaddleOCR microservice | `/health` | HTTP 200-399; `/health` returns JSON OK; OCR endpoint accepts image payloads | `subdomain-registry.yaml#ocr` |
| `https://auth.insightpulseai.com` | Authentication Service | Authentication service | `/.well-known/openid-configuration` | HTTP 200-399; OIDC discovery document returns valid JSON; token endpoint reachable | `subdomain-registry.yaml#auth` |

### Planned (Not Yet Active)

| URL | Service | Owner | Health Check | Success Criteria | SSOT Pointer |
|-----|---------|-------|--------------|------------------|--------------|
| `https://api.insightpulseai.com` | API Gateway | API Gateway | `/api/health` | HTTP 200-399; `/api/health` returns JSON OK; API routes resolve | `subdomain-registry.yaml#api` (status: planned) |

---

## Staging Services

| URL | Service | Health Check | Success Criteria |
|-----|---------|--------------|------------------|
| `https://stage-erp.insightpulseai.com` | Odoo CE 19.0 (staging) | `/web/login` | HTTP 200-399; uses `odoo_stage` DB; no prod secrets; login form renders |
| `https://stage-n8n.insightpulseai.com` | n8n (staging) | `/healthz` | HTTP 200-399; isolated credentials; staging workflows only |
| `https://stage-mcp.insightpulseai.com` | MCP Gateway (staging) | `/healthz` | HTTP 200-399; `/healthz` OK; routes point to staging MCP servers |
| `https://stage-superset.insightpulseai.com` | Superset BI (staging) | `/health` | HTTP 200-399; `/health` OK; staging dashboards |
| `https://stage-api.insightpulseai.com` | API Gateway (staging) | `/api/health` | HTTP 200-399; `/api/health` OK; staging API routes |
| `https://stage-auth.insightpulseai.com` | Auth (staging) | `/.well-known/openid-configuration` | HTTP 200-399; OIDC discovery valid; staging credentials |
| `https://stage-ocr.insightpulseai.com` | PaddleOCR (staging) | `/health` | HTTP 200-399; `/health` OK; staging OCR endpoint |

---

## Local Development

| URL | Service | Success Criteria |
|-----|---------|------------------|
| `http://localhost:8069` | Odoo dev local | `/web/login` OK; uses `odoo_dev` DB; dev services reachable |
| `http://localhost:5678` | n8n dev local | UI loads; workflows editable |
| `http://localhost:8766` | MCP dev local | MCP client ping responds |
| `http://localhost:54321` | Supabase local | Dashboard loads |
| `http://localhost:8088` | Superset dev local | `/health` OK; login page loads |
| `http://localhost:3000` | Auth / Next.js dev | Service responds |

---

## Drift Analysis (Found in Code but NOT in SSOT)

These subdomains are referenced in active (non-archive) code but are **not defined** in `infra/dns/subdomain-registry.yaml`. Each needs resolution: add to SSOT, or remove references.

| Subdomain | Refs | Status | Assessment | Recommended Action |
|-----------|------|--------|------------|-------------------|
| `ops.insightpulseai.com` | 63 | UNDOCUMENTED | Operations console; actively referenced in deployment docs | Add to SSOT if prod, else remove |
| `plane.insightpulseai.com` | 18 | UNDOCUMENTED | Project management (Plane.so); has CI workflow | Add to SSOT if prod |
| `boards.insightpulseai.com` | 12 | UNDOCUMENTED | Focalboard/kanban boards | Add to SSOT or remove |
| `docs.insightpulseai.com` | 5 | UNDOCUMENTED | Documentation portal | Clarify purpose or remove |
| `app.insightpulseai.com` | 2 | UNDOCUMENTED | SaaS app frontend (Supabase OAuth ref) | Clarify or remove |
| `gpu.insightpulseai.com` | 1 | ACTIVE CONFIG | GPU/LLM inference endpoint in agent config | Add to SSOT |
| `mlflow.insightpulseai.com` | 1 | CONFIG | ML experiment tracking | Add if production |

### Resolved Drift (Fixed 2026-02-17)

| Subdomain | Refs | Resolution |
|-----------|------|------------|
| `ipa.insightpulseai.com` | 148 | Migrated to `n8n.insightpulseai.com` — code refs updated |
| `*.insightpulseai.net` | 60+ | Updated to `.com` in all non-archive active files |

---

## Runtime Classification Audit

> Audited: 2026-02-28 | SSH audit of `178.128.112.214` + `nginx -T` + `docker ps` + DNS SSOT
> Legend: ✅ Healthy | ⚠️ Issues present | ❌ Broken or missing

### Classification Key

| Class | Meaning |
|-------|---------|
| **DEPLOYED SERVICE** | Backing runtime confirmed: container running + nginx vhost wired + DNS active |
| **REDIRECT ONLY** | No content; issues a 301/302 to another URL |
| **DOCS/STATIC OUTPUT** | Generated static content (GitHub Pages, JSON artifacts) |
| **STAGED/BROKEN** | DNS record is live in Cloudflare but backing service absent or non-functional |
| **INVENTORY ONLY** | Code/doc references exist but no DNS record, no container, no nginx vhost |

### Production URLs

| URL | Class | Backing Runtime | Health | Gap / Action |
|-----|-------|-----------------|--------|--------------|
| `https://insightpulseai.com` | DEPLOYED SERVICE | nginx vhost present on droplet | ⚠️ Verify content | Confirm correct marketing content served; not just Odoo default |
| `https://www.insightpulseai.com` | REDIRECT ONLY | nginx 301 → apex | ✅ | None |
| `https://erp.insightpulseai.com` | DEPLOYED SERVICE | `odoo-prod` → port 8069; nginx vhost | ✅ | None |
| `https://n8n.insightpulseai.com` | DEPLOYED SERVICE | `ipai-n8n` → port 5678; nginx vhost | ✅ | None |
| `https://mcp.insightpulseai.com` | DEPLOYED SERVICE | `mcp-coordinator` → port 8766; nginx vhost | ⚠️ DNS drift | SSOT declares CNAME to `pulse-hub-web-an645.ondigitalocean.app`; CF actually has A record → droplet; reconcile |
| `https://superset.insightpulseai.com` | DEPLOYED SERVICE | `superset-prod` → port 8088; nginx vhost | ✅ | Stale `superset.insightpulseai.net` vhost in nginx — remove |
| `https://ocr.insightpulseai.com` | DEPLOYED SERVICE | `ocr-prod` port 8001 (externally bound); CF origin rule inferred | ✅ | No nginx vhost; add vhost or document CF origin port rule |
| `https://auth.insightpulseai.com` | STAGED/BROKEN | `auth-prod` → port 8080 (healthy); **no nginx vhost**; OIDC endpoint returns 404 | ❌ | MISSING: nginx vhost wiring auth → 8080; OIDC discovery handler not implemented in app |
| `https://plane.insightpulseai.com` | DEPLOYED SERVICE | `community-proxy-1` → port 3002; nginx vhost | ⚠️ `community-space-1` unhealthy | Added 2026-02-28; monitor Plane space service |
| `https://api.insightpulseai.com` | INVENTORY ONLY | None | ❌ | SSOT status: planned; no container, no nginx vhost; do not route |

### Staging URLs

All `stage-*` DNS entries carry `lifecycle: active / status: claimed` in `infra/dns/subdomain-registry.yaml`
— records are live in Cloudflare — but **zero staging containers are running on the droplet**.

| URL | Class | Gap / Action |
|-----|-------|--------------|
| `https://stage-erp.insightpulseai.com` | STAGED/BROKEN | DNS live; no staging Odoo container; requests resolve to dead port |
| `https://stage-n8n.insightpulseai.com` | STAGED/BROKEN | DNS live; no staging n8n container |
| `https://stage-mcp.insightpulseai.com` | STAGED/BROKEN | DNS live; no staging MCP container |
| `https://stage-superset.insightpulseai.com` | STAGED/BROKEN | DNS live; no staging Superset container |
| `https://stage-api.insightpulseai.com` | STAGED/BROKEN | DNS live; port 8000 is `paddleocr-service` — **MISMAPPED** (wrong service) |
| `https://stage-auth.insightpulseai.com` | STAGED/BROKEN | DNS live; no staging auth container |
| `https://stage-ocr.insightpulseai.com` | STAGED/BROKEN | DNS live; no staging OCR container |

Recommended: change all `stage-*` SSOT lifecycle to `planned` (removes false confidence that staging exists)
until containers are actually provisioned.

### Drift URLs (Found in Code, Not in DNS SSOT)

| URL | Class | Backing Runtime | Gap / Action |
|-----|-------|-----------------|--------------|
| `https://ops.insightpulseai.com` | STAGED/BROKEN | Vercel project `prj_0pVE25oMd1EHDD1Ks3Xr7RTgqfsX` (ops-console) confirmed | DNS SSOT lifecycle: planned; Vercel domain not claimed; promote to active once Vercel domain assigned |
| `https://boards.insightpulseai.com` | INVENTORY ONLY | None | Not in DNS SSOT; no container running; `docs/integrations/FOCALBOARD.md` incorrectly claims this as prod — fix doc |
| `https://docs.insightpulseai.com` | DOCS/STATIC OUTPUT | GitHub Pages at `insightpulseai.github.io/odoo/` (mkdocs output) | Custom domain DNS never created; GitHub Pages not configured for custom domain |
| `https://app.insightpulseai.com` | INVENTORY ONLY | None | 2 code refs (Supabase OAuth callback); no DNS, no container, no spec |
| `https://gpu.insightpulseai.com` | INVENTORY ONLY | `ollama-service` running on droplet (unhealthy) | No DNS entry; no nginx vhost; do not route until service is healthy and spec exists |
| `https://mlflow.insightpulseai.com` | INVENTORY ONLY | None | 1 config reference; no DNS, no container, no spec bundle |

### Static / Generated Output

| URL | Class | Notes |
|-----|-------|-------|
| `https://insightpulseai.github.io/odoo/` | DOCS/STATIC OUTPUT | mkdocs build output; GitHub Pages; no custom domain pointing here |
| `artifacts/cloudflare/zone_state.json` | DOCS/STATIC OUTPUT | Generated CF zone snapshot; do not edit |
| `infra/cloudflare/envs/prod/subdomains.auto.tfvars` | DOCS/STATIC OUTPUT | Generated from `infra/dns/subdomain-registry.yaml`; do not edit |

### Remediation Backlog

| Priority | URL | Required Action |
|----------|-----|-----------------|
| 🔴 HIGH | `https://auth.insightpulseai.com` | Add nginx vhost routing → port 8080 AND implement OIDC discovery endpoint in `auth-prod` |
| 🔴 HIGH | `https://stage-api.insightpulseai.com` | Unmap port 8000 (PaddleOCR collision) — either provision real API gateway or deprovision DNS record |
| 🟡 MEDIUM | `https://ops.insightpulseai.com` | Claim Vercel custom domain → promote SSOT to `lifecycle: active` |
| 🟡 MEDIUM | `https://mcp.insightpulseai.com` | Reconcile DNS drift: update CF to CNAME → DO App Platform OR accept A record and update SSOT |
| 🟡 MEDIUM | `https://ocr.insightpulseai.com` | Add nginx vhost or document CF origin rule explicitly in registry |
| 🟢 LOW | All `stage-*` (7 entries) | Change SSOT lifecycle to `planned` until staging containers provisioned |
| 🟢 LOW | nginx `superset.insightpulseai.net` | Remove stale `.net` vhost block from nginx conf |
| 🟢 LOW | `docs/integrations/FOCALBOARD.md` | Update to reflect Focalboard deprovisioned state; remove false prod URL claim |

---

## Deprecated Services

| Subdomain | Deprecated Date | Replacement | DNS Removed | Container Removed |
|-----------|----------------|-------------|-------------|-------------------|
| `affine.insightpulseai.com` | 2026-02-09 | None | Yes | Yes |
| `*.insightpulseai.net` (all) | 2026-02 | `*.insightpulseai.com` | Yes | N/A |
| `mattermost.insightpulseai.com` | 2026-01-28 | Slack | Pending cleanup | Yes |
| `mg.insightpulseai.com` | 2026-02 | Zoho Mail SMTP | Pending cleanup | Yes |
| `ipa.insightpulseai.com` | 2026-02 | `n8n.insightpulseai.com` | Pending cleanup | N/A (alias) |
| `chat.insightpulseai.com` | 2026-01-28 | Slack | Pending cleanup | Mattermost |
| `odoo.insightpulseai.com` | 2026-02 | `erp.insightpulseai.com` | Pending cleanup | N/A (alias) |

---

## n8n Workflow Locations

| Path | Count | Status | Notes |
|------|-------|--------|-------|
| `automations/n8n/workflows/` | 31 | **Canonical** | Single source of truth for n8n workflows |
| `workflows/n8n/` | 7 | **Legacy** | Audit for duplicates; migrate unique ones to `automations/n8n/` |
| `workflows/*.json` | 4 | **Stale** | Webhook definitions (instanceId updated to `n8n.insightpulseai.com`) |
| `notion-n8n-monthly-close/workflows/` | 10 | **Archived** | Historical deployment artifacts |

---

## Verification

```bash
# DNS baseline check
./scripts/verify-dns-baseline.sh

# Service health checks (all prod services + marketing surface)
./scripts/verify-service-health.sh

# Marketing surface only (edge mode)
MODE=edge SCOPE=production ./scripts/verify-service-health.sh

# DNS sync CI validation
# Triggered by: .github/workflows/dns-sync-check.yml

# .net regression gate
# Triggered by: .github/workflows/domain-lint.yml

# JSON schema validation
jq . docs/arch/runtime_identifiers.json
```

---

## Related Files

| File | Purpose |
|------|---------|
| `infra/dns/subdomain-registry.yaml` | **DNS SSOT** (edit this) |
| `infra/cloudflare/envs/prod/subdomains.auto.tfvars` | Generated Terraform input |
| `docs/arch/runtime_identifiers.json` | Generated runtime config |
| `docs/arch/PROD_RUNTIME_SNAPSHOT.md` | Production runtime state |
| `docs/arch/RUNTIME_IDENTIFIERS.md` | Runtime identifiers reference |
| `scripts/generate-dns-artifacts.sh` | Generates Terraform + JSON from YAML |
| `scripts/verify-dns-baseline.sh` | DNS verification script |
| `scripts/verify-service-health.sh` | Service health check script |
| `.github/workflows/dns-sync-check.yml` | CI: SSOT sync enforcement |
| `.github/workflows/domain-lint.yml` | CI: `.net` regression gate |
| `reports/url_inventory.json` | Machine-readable inventory + drift |
| `spec/insightpulseai-com/` | Spec Kit bundle for marketing surface |
