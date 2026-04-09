# CP-3 WAF / Front Door Validation

**Date**: 2026-03-20
**Method**: Azure CLI + curl

## Front Door Profile
- Name: ipai-fd-dev
- SKU: Premium_AzureFrontDoor
- Resource Group: rg-ipai-shared-dev
- Endpoint: afd-ipai-dev-ep-h6gcfyafbug5dcdb.z03.azurefd.net

## WAF Policy
- Name: ipaiDevWafPolicy
- Mode: Prevention
- Enabled: Yes

### Managed Rules
| Rule Set | Version | Action |
|----------|---------|--------|
| Microsoft_DefaultRuleSet | 2.1 | Block |
| Microsoft_BotManagerRuleSet | 1.0 | Block |

### Custom Rules
| Name | Priority | Action |
|------|----------|--------|
| AllowHealthChecks | 50 | Allow |
| RateLimitRpcEndpoints | 100 | Block (60/min) |
| BlockAiCrawlers | 200 | Block |

## Security Policy Binding
- Name: ipai-fd-dev-waf
- Bound to: ipai-fd-dev-ep endpoint

## Custom Domains (13 total, all Managed Certificate TLS)
erp.insightpulseai.com, erp-azure.insightpulseai.com, n8n.insightpulseai.com, 
auth.insightpulseai.com, ocr.insightpulseai.com, superset.insightpulseai.com, 
mcp.insightpulseai.com, plane.insightpulseai.com, shelf.insightpulseai.com, 
crm.insightpulseai.com, insightpulseai.com, www.insightpulseai.com, n8n-azure.insightpulseai.com

## Routing (erp.insightpulseai.com)
- 5 routes: erp-default, erp-static, erp-content, erp-websocket, erp-rpc
- All → origin group: odoo-web
- HTTPS redirect: Enabled
- Forwarding: HttpsOnly

## Live Edge Validation
- x-azure-ref: present (confirms AFD routing)
- x-frame-options: SAMEORIGIN
- content-security-policy: frame-ancestors 'self'
- Set-Cookie: HttpOnly flag present
- HTTP redirect: 307 from HTTP to HTTPS

## Verdict
- CP-3: **DONE** — WAF in Prevention mode, managed + custom rules active, all domains routed through AFD
