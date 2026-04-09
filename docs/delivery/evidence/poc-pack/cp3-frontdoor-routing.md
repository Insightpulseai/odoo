# CP-3: Azure Front Door Routing Validation

> **Date:** 2026-03-20T00:10:00Z
> **Status:** PARTIAL (routing validated, WAF policy export pending)

## Evidence

### Front Door Profile

```
Name         Sku                     State
-----------  ----------------------  ---------
ipai-fd-dev  Premium_AzureFrontDoor  Succeeded
```

- Resource Group: `rg-ipai-dev`
- SKU: Premium (supports WAF managed rules)

### Routing Validation (Smoke Test)

The smoke test at `erp.insightpulseai.com` confirms AFD routing:

```
PASS: Azure Front Door routing (x-azure-ref header present)
PASS: Security headers present (strict-transport-security)
PASS: Session cookie HttpOnly
PASS: X-Frame-Options set
```

### ACA Ingress Configuration

```json
{
  "allowInsecure": false,
  "external": true,
  "fqdn": "ipai-odoo-dev-web.thankfulbush-191bdcb0.southeastasia.azurecontainerapps.io",
  "targetPort": 8069,
  "transport": "Http"
}
```

### FDID Binding

- `AZURE_FRONTDOOR_ID` env var set on container: `38c7f9ab-c904-4c47-ad53-4b9fb1abea8e`
- `ipai_security_frontdoor` middleware committed but not yet deployed to running image

### Origin Bypass Status

- Direct ACA URL currently returns 200 (middleware not yet in running image)
- Will return 403 after next pipeline deploy includes the frontdoor module

### Remaining

- [ ] WAF managed rules policy export (az afd waf-policy show)
- [ ] Redeploy container image with ipai_security_frontdoor module
