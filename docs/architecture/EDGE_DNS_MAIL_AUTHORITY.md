# Edge, DNS & Mail Authority

> Defines authoritative DNS, edge routing, and mail infrastructure.
> Cross-referenced by: `INSIGHTPULSEAI_TARGET_STATE_ARCHITECTURE.md` §2, §8
> Updated: 2026-03-25

---

## DNS Authority

| Concern | Owner | Notes |
|---------|-------|-------|
| Domain registration | Squarespace | `insightpulseai.com` — registrar only |
| NS delegation | Squarespace → Cloudflare | NS records point to Cloudflare nameservers |
| Authoritative DNS | **Cloudflare** (DNS-only mode) | All records managed here. Proxy mode disabled. |
| DNS-as-code | `infra/dns/subdomain-registry.yaml` | Human-readable record index |
| SSOT registry | `infra/dns/subdomain-registry.yaml` | Record truth for CI validation |

### Azure DNS Migration (Zone Provisioned, NS Not Delegated)

Azure DNS zone `insightpulseai.com` **exists** in `rg-ipai-dev-odoo-runtime` (confirmed via Resource Graph).
However, Squarespace NS records still point to Cloudflare — **NS delegation has not been switched**.
Cloudflare remains the live DNS authority until NS delegation is updated.

**Migration steps (when ready):**
1. Create Azure DNS zone for `insightpulseai.com`
2. Import all records from Cloudflare export
3. Verify record parity (A, CNAME, MX, TXT, CAA)
4. Update Squarespace NS records to Azure DNS nameservers
5. Wait for propagation (48h with lowered TTLs)
6. Deactivate Cloudflare zone
7. Update `infra/dns/subdomain-registry.yaml` to reference Azure DNS
8. Update IaC in `infra/azure/dns/` for ongoing management

**Prerequisite**: Azure DNS zone must be provisioned and validated before NS delegation.

### Cloudflare Proxy Retirement (Completed)

Cloudflare **proxy mode** (orange cloud) is retired as of 2026-03-25.
All edge routing, TLS termination, and WAF are handled by Azure Front Door.
Cloudflare operates in **DNS-only mode** (grey cloud) for all records.

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
| Inbound mail | Zoho Mail | MX records in Cloudflare DNS |
| Outbound SMTP | Zoho SMTP | `smtp.zoho.com:587` (STARTTLS) |
| SPF | Cloudflare DNS TXT | `v=spf1 include:zoho.com ~all` |
| DKIM | Cloudflare DNS TXT | `zoho._domainkey` |
| DMARC | Cloudflare DNS TXT | `_dmarc` |
| Credentials | Azure Key Vault | `zoho-smtp-user`, `zoho-smtp-password` |

Odoo sends mail via `ir.mail_server` configured with Zoho SMTP. Credentials resolved at runtime via managed identity → Key Vault → env vars.

## Retired

| Service | Was | Replaced By | Date |
|---------|-----|-------------|------|
| Cloudflare proxy | Edge routing + WAF | Azure Front Door | 2026-03-25 |
| Mailgun | SMTP | Zoho SMTP | 2026-03-11 |
| `insightpulseai.net` | Domain | `insightpulseai.com` | 2026-02 |

---

*Cloudflare is the current DNS authority (DNS-only mode). Front Door is the sole edge authority. Zoho is the sole mail authority.*
*Azure DNS is the target DNS authority — migration not yet executed.*
