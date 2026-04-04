# Front Door Hostname Preservation

## Why this matters

Azure Front Door rewrites the `Host` header to the origin's internal FQDN by default.
For Odoo behind Front Door, this breaks:

- **Session cookies** — Odoo sets cookies on the `Host` header domain; if it sees `*.azurecontainerapps.io` instead of `erp.insightpulseai.com`, cookies scope to the wrong domain
- **OIDC redirect URIs** — `ipai_auth_oidc` generates callback URLs from the request host; wrong host = redirect_uri mismatch with Entra app `07bd9669`
- **CSRF validation** — Odoo validates `Referer`/`Origin` headers against the base URL
- **Canonical URL generation** — links in emails, reports, and API responses use wrong hostname

## Current state

### What is configured

`infra/azure/front-door-routes.yaml` defines 10 origin groups with health probes and routing rules.
`config/azure/odoo.conf` sets `web.base.url = https://erp.insightpulseai.com` as a hardcoded workaround.

### What is missing

No origin group in `front-door-routes.yaml` specifies `originHostHeader` or `preserveHostHeader`.
This means Front Door may use default behavior: forwarding the ACA internal FQDN as the Host header.

The `web.base.url` workaround in `odoo.conf` fixes URL generation but does **not** fix:
- Cookie domain mismatch (browser-visible)
- OIDC callback host detection (request-visible)
- `Referer` / `Origin` validation (request-visible)

## Required configuration

### Origin group level

Each origin in `front-door-routes.yaml` must explicitly preserve the incoming hostname:

```yaml
origin_groups:
  - name: odoo-web
    origins:
      - container_app: odoo-web
        http_port: 80
        https_port: 443
        priority: 1
        weight: 1000
        origin_host_header: erp.insightpulseai.com  # <-- required
```

For all origin groups, `origin_host_header` must match the public custom domain:

| Origin group | `origin_host_header` |
|-------------|---------------------|
| `odoo-web` | `erp.insightpulseai.com` |
| `n8n` | `n8n.insightpulseai.com` |
| `mcp-gateway` | `mcp.insightpulseai.com` |
| `plane` | `plane.insightpulseai.com` |
| `shelf` | `shelf.insightpulseai.com` |
| `crm` | `crm.insightpulseai.com` |
| `superset` | `superset.insightpulseai.com` |
| `ocr` | `ocr.insightpulseai.com` |
| `auth` | `auth.insightpulseai.com` |
| `redirect` | `insightpulseai.com` |

### Bicep level

In `infra/azure/modules/front-door.bicep`, origin definitions must include:

```bicep
properties: {
  hostName: origin.hostName
  originHostHeader: origin.originHostHeader  // preserve public hostname
  httpPort: origin.httpPort
  httpsPort: origin.httpsPort
  priority: origin.priority
  weight: origin.weight
}
```

### ACA custom domain requirement

Each ACA app must have its public hostname registered as a custom domain with a managed certificate.
Without this, ACA rejects requests where the `Host` header doesn't match any configured hostname.

## Verification

### Pipeline check

The `prod-verify` Playwright specs include a hostname redirect check:
- Request to the public URL must not expose `*.azurecontainerapps.io` in any response header or redirect
- `Location` headers on redirects must use the public hostname

### CLI audit

```bash
# Check origin host header configuration for all origins
az afd origin list \
  --profile-name ipai-fd-dev \
  --resource-group rg-ipai-dev-odoo-runtime \
  --origin-group-name odoo-web \
  --query "[].{name:name, hostName:hostName, originHostHeader:originHostHeader}" \
  -o table
```

Expected: `originHostHeader` = `erp.insightpulseai.com` (not null, not the ACA FQDN).

### Manual smoke test

```bash
# Verify the response doesn't leak internal FQDN
curl -sI https://erp.insightpulseai.com/web/login | grep -iE 'location|set-cookie|x-'
```

Expected:
- No `*.azurecontainerapps.io` in any header value
- `Set-Cookie` domain matches `insightpulseai.com` (or is unset, defaulting to request host)

## Reference

- [Azure Architecture Center: Host name preservation](https://learn.microsoft.com/en-us/azure/architecture/best-practices/host-name-preservation)
- `infra/azure/front-door-routes.yaml` — SSOT for routing rules
- `infra/azure/modules/front-door.bicep` — IaC deployment
- `config/azure/odoo.conf` — Odoo runtime config (contains `web.base.url` workaround)
