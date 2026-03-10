# DNS Email Contract — insightpulseai.com

> **SSOT**: `infra/dns/zoho_mail_dns.yaml`
> **Provider**: Cloudflare (delegated from Spacesquare)
> **Mail Provider**: Zoho Mail (US datacenter)

## Required Records

| Type | Name | Value | Priority | Purpose |
|------|------|-------|----------|---------|
| MX | `@` | `mx.zoho.com` | 10 | Primary mail routing |
| MX | `@` | `mx2.zoho.com` | 20 | Secondary failover |
| MX | `@` | `mx3.zoho.com` | 50 | Tertiary failover |
| TXT | `@` | `v=spf1 include:zoho.com ~all` | — | SPF authorization |
| TXT | `zoho._domainkey` | `<DKIM public key>` | — | DKIM signing |
| TXT | `_dmarc` | `v=DMARC1; p=quarantine; ...` | — | DMARC policy |

## SMTP / IMAP Endpoints

| Protocol | Host | Port | Encryption | Auth |
|----------|------|------|------------|------|
| SMTP | `smtppro.zoho.com` | 587 | STARTTLS | App Password |
| IMAP | `imappro.zoho.com` | 993 | SSL/TLS | App Password |

**Note**: The `smtppro` / `imappro` endpoints are the US datacenter. Do NOT use `smtp.zoho.com` / `imap.zoho.com` (global endpoints) for `@insightpulseai.com` — those cause `535 Authentication Failed`.

## Drift Policy

1. **Never** edit Cloudflare DNS records directly via UI.
2. All DNS changes go through `infra/dns/zoho_mail_dns.yaml` → PR → merge → Terraform apply.
3. CI enforces consistency: `.github/workflows/dns-sync-check.yml`
4. Drift check: `scripts/verify-dns-baseline.sh`

## Applying Changes

```bash
# 1. Edit SSOT
vim infra/dns/zoho_mail_dns.yaml

# 2. Regenerate Terraform artifacts
bash scripts/generate-dns-artifacts.sh

# 3. Commit all (YAML + generated)
git add infra/dns/ infra/cloudflare/
git commit -m "chore(dns): update zoho mail dns records"

# 4. Terraform apply (production)
cd infra/cloudflare/envs/prod
terraform apply
```

## DKIM Setup (Manual)

DKIM requires generating keys in Zoho Admin:

1. Go to: https://mailadmin.zoho.com → Domains → `insightpulseai.com` → Email Authentication
2. Click "Configure DKIM" → copy the TXT value
3. Update `infra/dns/zoho_mail_dns.yaml` — replace `PLACEHOLDER` with actual key
4. Apply via Terraform

## Verification

```bash
# MX records
dig MX insightpulseai.com

# SPF
dig TXT insightpulseai.com | grep spf

# DKIM
dig TXT zoho._domainkey.insightpulseai.com

# DMARC
dig TXT _dmarc.insightpulseai.com

# SMTP auth probe
python3 - <<'PY'
import smtplib, ssl
s = smtplib.SMTP("smtppro.zoho.com", 587, timeout=20)
s.ehlo(); s.starttls(context=ssl.create_default_context()); s.ehlo()
s.login("business@insightpulseai.com", "$ZOHO_SMTP_APP_PASSWORD")
print("AUTH OK"); s.quit()
PY
```
