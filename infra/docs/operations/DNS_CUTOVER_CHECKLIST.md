# DNS Cutover Checklist

> Version: 1.0.0
> Last updated: 2026-03-14
> Canonical repo: `infra`
> Parent: `infra/docs/architecture/DNS_TARGET_STATE_MATRIX.md`

## Pre-Cutover Validation

- [ ] Production Azure Front Door endpoint provisioned and healthy
- [ ] All origin backends (Odoo, auth, n8n, etc.) responding behind prod AFD
- [ ] TLS certificates issued for all target custom domains
- [ ] Custom domain validation tokens (`_dnsauth*`) in place
- [ ] Current DNS state documented (snapshot of all records)
- [ ] Rollback targets identified for every record change

## Record Changes

### Phase 1 — New product hostnames

| Action | Host | Type | Target |
|--------|------|------|--------|
| ADD | `copilot` | CNAME | `<PROD_AFD_ENDPOINT>` |
| ADD | `analytics` | CNAME | `<PROD_AFD_ENDPOINT>` |
| ADD | `api` | CNAME | `<PROD_AFD_ENDPOINT>` |
| ADD | `status` | CNAME | `<PROD_AFD_ENDPOINT>` or status provider |
| ADD | `docs` | CNAME | `<PROD_AFD_ENDPOINT>` |

### Phase 2 — Replace dev targets with prod

| Action | Host | From | To |
|--------|------|------|----|
| REPLACE | `@` | dev AFD endpoint | `<PROD_AFD_ENDPOINT>` |
| REPLACE | `www` | dev AFD endpoint | `<PROD_AFD_ENDPOINT>` |
| REPLACE | `erp` | dev AFD endpoint | `<PROD_AFD_ENDPOINT>` |
| REPLACE | `auth` | dev AFD endpoint | `<PROD_AFD_ENDPOINT>` |
| REPLACE | `n8n` | dev AFD endpoint | `<PROD_AFD_ENDPOINT>` |
| REPLACE | `mcp` | dev AFD endpoint | `<PROD_AFD_ENDPOINT>` |
| REPLACE | `ocr` | dev AFD endpoint | `<PROD_AFD_ENDPOINT>` |
| REPLACE | `ops` | `cname.vercel-dns.com` | `<PROD_AFD_ENDPOINT>` |

### Phase 3 — Retire transitional aliases

| Action | Host | Condition |
|--------|------|-----------|
| DELETE | `erp-azure` | After `erp` validated on prod |
| DELETE | `n8n-azure` | Retired — canonical subdomain is now `n8n` |
| DELETE | `agent` | After confirming no active dependency |
| DELETE | `mail` | After confirming Zoho handles all inbound |

### Phase 4 — Conditional review

| Action | Host | Decision |
|--------|------|----------|
| KEEP or DELETE | `plane` | Keep if actively used |
| KEEP or DELETE | `shelf` | Keep if actively used |
| KEEP or DELETE | `superset` | Keep if actively used |
| KEEP or DELETE | `supabase` | Keep only if intentionally public |

## Propagation Checks

After each phase, verify propagation:

```bash
# Check CNAME resolution
dig +short copilot.insightpulseai.com CNAME
dig +short erp.insightpulseai.com CNAME
dig +short ops.insightpulseai.com CNAME

# Check A record resolution (through CNAME chain)
dig +short copilot.insightpulseai.com A
dig +short erp.insightpulseai.com A

# Verify TLS
curl -sI https://copilot.insightpulseai.com | head -5
curl -sI https://erp.insightpulseai.com | head -5
curl -sI https://ops.insightpulseai.com | head -5

# Verify mail records unchanged
dig +short insightpulseai.com MX
dig +short insightpulseai.com TXT | grep spf
```

## TLS / Domain Validation

- [ ] Azure Front Door shows all custom domains as "Validated"
- [ ] No certificate errors on any hostname
- [ ] HTTPS redirect working for all product hostnames
- [ ] No mixed-content warnings on any page

## App Routing Validation

- [ ] `erp.insightpulseai.com` → Odoo login page loads
- [ ] `auth.insightpulseai.com` → Auth service responds
- [ ] `n8n.insightpulseai.com` → n8n UI loads (if public)
- [ ] `ops.insightpulseai.com` → Ops console loads
- [ ] `copilot.insightpulseai.com` → Copilot surface loads (when ready)
- [ ] `api.insightpulseai.com` → API health endpoint returns 200

## Rollback Plan

If any hostname fails after cutover:

1. Revert the CNAME to the previous target (dev AFD or Vercel)
2. Verify resolution restored
3. Investigate origin/routing issue
4. Re-attempt after fix

**Rollback targets (document before cutover):**

| Host | Rollback target |
|------|----------------|
| `@` | `ipai-fd-dev-ep-fnh4e8d6gtdhc8ax.z03.azurefd.net` |
| `erp` | same |
| `ops` | `cname.vercel-dns.com` |

## Mail Records — Do Not Touch

The following records must NOT be modified during DNS cutover:

- MX records (Zoho)
- SPF TXT record
- DKIM (`zoho._domainkey`)
- DMARC (`_dmarc`)
- Mailgun subdomain records (`mg.*`)

Mail cutover is a separate phase with its own checklist (see DNS_TARGET_STATE_MATRIX.md §I).
