# Azure Front Door and Ingress

Azure Front Door configuration for public ingress, TLS termination, WAF rules, and routing.

## Architecture

- Front Door: `ipai-fd-dev` (endpoint: `ipai-fd-dev-ep-fnh4e8d6gtdhc8ax.z03.azurefd.net`)
- All public subdomains route through Front Door
- TLS: managed certificates via Front Door
- WAF: Azure-managed ruleset + custom rules

## Convention

- No nginx, no Cloudflare (deprecated)
- Route rules defined per origin group
- Custom domains validated via Azure DNS CNAME

<!-- TODO: Add Bicep/ARM templates for Front Door configuration -->
