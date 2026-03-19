# DNS Target State Matrix

> Version: 1.1.0
> Canonical repo: `infra`

## Purpose

This document defines the exact record-by-record target state and migration plan for the `insightpulseai.com` DNS zone. The goal is to consolidate all canonical public endpoints onto Azure Front Door, maintain strict separation for mail/security records, eliminate legacy providers (DigitalOcean, Vercel), and resolve dev-vs-prod naming disparities.

Cloudflare remains the authoritative DNS control plane.

## Complete Record-by-Record Classification Matrix

| Record Name | Type | Current Target | Classification | Action / Destination |
| :--- | :--- | :--- | :--- | :--- |
| **`insightpulseai.com`** | CNAME | `ipai-fd-dev-ep-*.azurefd.net` | **Rename/Promote** | Point to Prod Azure Front Door endpoint |
| **`www`** | CNAME | `ipai-fd-dev-ep-*.azurefd.net` | **Rename/Promote** | Point to Prod Azure Front Door endpoint |
| **`auth`** | CNAME | `ipai-fd-dev-ep-*.azurefd.net` | **Rename/Promote** | Point to Prod Azure Front Door endpoint |
| **`crm`** | CNAME | `ipai-fd-dev-ep-*.azurefd.net` | **Rename/Promote** | Point to Prod Azure Front Door endpoint |
| **`erp`** | CNAME | `ipai-fd-dev-ep-*.azurefd.net` | **Rename/Promote** | Point to Prod Azure Front Door endpoint |
| **`mcp`** | CNAME | `ipai-fd-dev-ep-*.azurefd.net` | **Rename/Promote** | Point to Prod Azure Front Door endpoint |
| **`n8n`** | CNAME | `ipai-fd-dev-ep-*.azurefd.net` | **Rename/Promote** | Point to Prod Azure Front Door endpoint |
| **`ocr`** | CNAME | `ipai-fd-dev-ep-*.azurefd.net` | **Rename/Promote** | Point to Prod Azure Front Door endpoint |
| **`plane`** | CNAME | `ipai-fd-dev-ep-*.azurefd.net` | **Rename/Promote** | Point to Prod Azure Front Door endpoint |
| **`shelf`** | CNAME | `ipai-fd-dev-ep-*.azurefd.net` | **Rename/Promote** | Point to Prod Azure Front Door endpoint |
| **`superset`** | CNAME | `ipai-fd-dev-ep-*.azurefd.net` | **Rename/Promote** | Point to Prod Azure Front Door endpoint |
| **`agent`** | CNAME | `*.agents.do-ai.run` | **Retire** | Remove DigitalOcean residue |
| **`ops`** | CNAME | `cname.vercel-dns.com` | **Retire** | Remove Vercel residue (migrate to prod AFD if keeping) |
| **`erp-azure`** | CNAME | `ipai-fd-dev-ep-*.azurefd.net` | **Retire** | Transitional alias; rely on canonical `erp` |
| **`n8n-azure`** | A | `4.193.100.31` | **Temporary Exception** | Direct-IP bypass. Migrate to Front Door -> ACA |
| **`supabase`** | A | `4.193.100.31` | **Temporary Exception** | Direct-IP bypass. Migrate to Front Door -> ACA |
| **`email.mg`** | CNAME | `mailgun.org` | **Keep** | Mail service record |
| **`insightpulseai.com`** | MX | `mx.zoho.com` (10, 20, 50) | **Keep** | Canonical Mail routing |
| **`_dmarc`** | TXT | `"v=DMARC1; p=quarantine..."` | **Keep** | Mail security |
| **`_dmarc.mg`** | TXT | `"v=DMARC1; p=none..."` | **Keep** | Mail security |
| **`insightpulseai.com`** | TXT | `"v=spf1 include:zohomail.com ~all"` | **Keep** | Mail security |
| **`mg`** | TXT | `"v=spf1 include:mailgun.org ~all"` | **Keep** | Mail security |
| **`mx._domainkey.mg`** | TXT | DKIM Public Key | **Keep** | Mail security |
| **`zoho._domainkey`** | TXT | DKIM Public Key | **Keep** | Mail security |
| **`_dnsauth.*`** | TXT | `_bdiz2p50qoi...` | **Keep** | Azure Front Door validation links |

## Architecture Decisions

1. **Stop Direct-IP Bypasses**: `n8n-azure` and `supabase` pointing raw A records at `4.193.100.31` bypasses the Front Door WAF/edge posture. They should be integrated dynamically via Front Door acting as ingress to Azure Container Apps or equivalent endpoints.
2. **Promote the Edge Configuration**: The primary public-facing hostnames currently route to an explicitly named "dev" Azure Front Door endpoint (`ipai-fd-dev-ep-...`). A production AFD endpoint must be correctly provisioned, and CNAMEs repointed, removing the naming drift.
3. **Purge Third-Party Residue**: Vercel (`ops`) and DigitalOcean (`agent`) must be retired entirely to adhere properly to the target Azure platform.
4. **Proxy State Integrity**: Records routed through Front Door only need Cloudflare acting as **DNS only** (Gray Cloud). Proxied (Orange Cloud) on top of Front Door creates double-proxy overhead unless explicit Cloudflare WAF capabilities are needed on top of AFD's edge processing.
