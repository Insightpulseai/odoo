<!-- DO NOT EDIT MANUALLY — derived from infra/dns/canonical_urls.yaml
     CI gate reads the YAML, not this file.
     To add or modify a URL: edit infra/dns/canonical_urls.yaml first,
     then regenerate this file by running: scripts/ci/check_canonical_urls.py --render-md
-->

# Canonical URLs — InsightPulse AI

**Last updated:** 2026-02-28
**SSOT:** `infra/dns/canonical_urls.yaml`
**Domain:** `insightpulseai.com`

> This document is the human-readable mirror of `infra/dns/canonical_urls.yaml`.
> Do not introduce new URLs here — CI (exit code 5) will fail the PR.
>
> - DNS record SSOT: `infra/dns/subdomain-registry.yaml`
> - URL lifecycle SSOT: `infra/dns/canonical_urls.yaml`
> - CI guard: `.github/workflows/canonical-urls-gate.yml`

---

## DEPLOYED

All five conditions met: DNS provisioned + edge healthy + origin healthy + TLS valid + lifecycle=active.

| URL | Backing | Health Probe | Notes |
|-----|---------|--------------|-------|
| `https://erp.insightpulseai.com` | nginx_vhost → `odoo-prod:8069` | `/web/login` | Odoo CE 19.0 — primary ERP |
| `https://n8n.insightpulseai.com` | nginx_vhost → `ipai-n8n:5678` | `/healthz` | n8n workflow automation |
| `https://plane.insightpulseai.com` | nginx_vhost → `community-web-1:3002` | `/` | Plane CE project management |
| `https://superset.insightpulseai.com` | nginx_vhost → `superset-prod:8088` | `/health` | Apache Superset BI; DO managed PostgreSQL: odoo-db-sgp1/superset |
| `https://mcp.insightpulseai.com` | platform → DO App Platform | `/healthz` | MCP coordination; DNS drift: CF has A record (should be CNAME → `pulse-hub-web-an645.ondigitalocean.app`) — fix on next Terraform apply |
| `https://ocr.insightpulseai.com` | nginx_vhost → `ocr-prod:8001` | `/health` | PaddleOCR microservice; nginx vhost + Let's Encrypt deployed 2026-02-28; `/healthz` remapped to `/health` |

---

## REDIRECT

Healthy but serves redirects only — no application content.

| URL | Backing | Health Probe | Notes |
|-----|---------|--------------|-------|
| `https://www.insightpulseai.com` | nginx_vhost → port 80 | `/` | 301 → `https://insightpulseai.com` (apex canonical) |

---

## BROKEN

DNS exists and origin may be running, but one or more required conditions are failing.

| URL | Backing | Health Probe | Breaking Conditions | Activation Criteria |
|-----|---------|--------------|---------------------|---------------------|
| `https://auth.insightpulseai.com` | none (`auth-prod` runs on :8080, unwired) | `/.well-known/openid-configuration` | No nginx vhost; OIDC discovery returns 404 | Add nginx vhost → `127.0.0.1:8080`; implement `/.well-known/openid-configuration` in auth-prod |

---

## STAGED

DNS claimed or planned; no backing service running.

| URL | Backing | Health Probe | Environment | Notes |
|-----|---------|--------------|-------------|-------|
| `https://stage-erp.insightpulseai.com` | none | `/web/login` | staging | No staging Odoo container; provision compose stack + nginx vhost → :8069 |
| `https://stage-api.insightpulseai.com` | none | `/api/health` | staging | Port 8100 (8000 conflicts with paddleocr-service); provision API gateway + nginx vhost → :8100 |
| `https://stage-auth.insightpulseai.com` | none | `/.well-known/openid-configuration` | staging | No staging auth container; provision + implement OIDC + nginx vhost → :8080 |
| `https://stage-mcp.insightpulseai.com` | none | `/healthz` | staging | No staging MCP container; provision on port 8766 + nginx vhost |
| `https://stage-n8n.insightpulseai.com` | none | `/healthz` | staging | Port 5679 (5678 conflicts with prod n8n); provision + nginx vhost |
| `https://stage-superset.insightpulseai.com` | none | `/health` | staging | Port 8089 (8088 conflicts with prod Superset); provision + nginx vhost |
| `https://stage-ocr.insightpulseai.com` | none | `/health` | staging | Port 8002 (8080 conflicts with auth-prod); provision + nginx vhost |
| `https://ops.insightpulseai.com` | platform → Vercel (unclaimed) | `/api/health` | production | OdooOps Console; Vercel domain not yet claimed — claim in Vercel dashboard to activate |
| `https://api.insightpulseai.com` | none | `/api/health` | production | API gateway — not yet provisioned |
| `https://app.insightpulseai.com` | none | `/` | — | Inventory-only; 2 code refs (Supabase OAuth callback); no DNS, no container, no spec |
| `https://boards.insightpulseai.com` | none | `/` | — | Inventory-only; Focalboard/kanban ref in docs; not in DNS SSOT; no container |
| `https://docs.insightpulseai.com` | none | `/` | — | Documentation portal (mkdocs at `insightpulseai.github.io/odoo/`); custom domain DNS never configured |
| `https://gpu.insightpulseai.com` | none | `/healthz` | — | GPU/LLM inference; ollama-service on droplet is unhealthy; no DNS entry; do not route until healthy + spec exists |
| `https://mlflow.insightpulseai.com` | none | `/health` | — | ML experiment tracking; 1 config ref; no DNS, no container, no spec bundle |

---

## Related Files

| File | Purpose |
|------|---------|
| `infra/dns/canonical_urls.yaml` | **URL lifecycle SSOT** (machine-readable — edit this, not this doc) |
| `infra/dns/subdomain-registry.yaml` | DNS record SSOT (Terraform-managed) |
| `scripts/ci/check_canonical_urls.py` | CI validator that reads the YAML |
| `.github/workflows/canonical-urls-gate.yml` | CI gate enforcing YAML consistency |
