# PRD: Cloudflare DNS IaC (insightpulseai.com)

## Objective
Codify A/MX/TXT records as Terraform to enable auditable changes and safe automation.

## Scope
- A: @, www, erp -> 178.128.112.214 (proxied)
- MX: Zoho (mx/mx2/mx3) DNS-only
- TXT: SPF, DMARC, DKIM

## Out of Scope
- Cloudflare Workers / Rules / SSL modes (separate spec)
