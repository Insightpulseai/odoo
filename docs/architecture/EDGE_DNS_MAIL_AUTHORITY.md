# Edge, DNS & Mail Authority

> Defines authoritative DNS, edge routing, and mail infrastructure.
> Cross-referenced by: `INSIGHTPULSEAI_TARGET_STATE_ARCHITECTURE.md` §2, §8
> Updated: 2026-03-25

---

## DNS Authority

| Concern | Owner | Notes |
|---------|-------|-------|
| Domain registration | Squarespace | `insightpulseai.com` — registrar only |
| NS delegation | Squarespace → Azure DNS | NS records point to Azure DNS nameservers |
| Authoritative DNS | **Azure DNS** (authoritative) | All records managed here. Cloudflare retired. |
| DNS-as-code | `infra/dns/subdomain-registry.yaml` | Human-readable record index |
| SSOT registry | `infra/dns/subdomain-registry.yaml` | Record truth for CI validation |

### Azure DNS Migration (Complete)

Azure DNS zone `insightpulseai.com` is **active** in `rg-ipai-dev-odoo-runtime`.
Squarespace NS records point to Azure DNS nameservers. Cloudflare DNS authority is **retired**.
All DNS records are managed in Azure DNS. IaC in `infra/azure/dns/`.

### Cloudflare Retirement (Completed)

Cloudflare is fully retired (proxy mode 2026-03-25, DNS authority 2026-03-26).
All edge routing, TLS termination, and WAF are handled by Azure Front Door.
All DNS is managed by Azure DNS.

## Edge / Ingress

| Concern | Owner | Resource |
|---------|-------|----------|
| TLS termination | Azure Front Door | `ipai-fd-dev` |
| WAF | Azure Front Door | Managed rule sets + custom rules |
| DDoS protection | Azure Front Door | Standard tier |
| Routing | Azure Front Door | Route rules → ACA backends |
| Certificates | Azure Front Door | Managed TLS (auto-renewal) |
| CDN / caching | Azure Front Door | Static assets cache at edge |

### Route Table

| Frontend Domain | Backend Pool | Service |
|-----------------|-------------|---------|
| `insightpulseai.com` | `ipai-website-dev` | Landing / marketing |
| `erp.insightpulseai.com` | `ipai-odoo-dev-web` | Odoo ERP |
| `ocr.insightpulseai.com` | `ipai-ocr-dev` | Document OCR |
| `mcp.insightpulseai.com` | `ipai-mcp-dev` | MCP coordination |

All subdomains route through Front Door. No direct ACA public endpoints.

## Mail

| Concern | Owner | Config |
|---------|-------|--------|
| Inbound mail | Zoho Mail | MX records in Azure DNS |
| Outbound SMTP | Zoho SMTP | `smtp.zoho.com:587` (STARTTLS) |
| SPF | Azure DNS TXT | `v=spf1 include:zoho.com ~all` |
| DKIM | Azure DNS TXT | `zoho._domainkey` |
| DMARC | Azure DNS TXT | `_dmarc` |
| Credentials | Azure Key Vault | `zoho-smtp-user`, `zoho-smtp-password` |

Odoo sends mail via `ir.mail_server` configured with Zoho SMTP. Credentials resolved at runtime via managed identity → Key Vault → env vars.

## Retired

| Service | Was | Replaced By | Date |
|---------|-----|-------------|------|
| Cloudflare proxy | Edge routing + WAF | Azure Front Door | 2026-03-25 |
| Mailgun | SMTP | Zoho SMTP | 2026-03-11 |
| `insightpulseai.net` | Domain | `insightpulseai.com` | 2026-02 |

---

*Azure DNS is the authoritative DNS provider. Front Door is the sole edge authority. Zoho is the sole mail authority.*
*Cloudflare is fully retired (2026-03-26).*
