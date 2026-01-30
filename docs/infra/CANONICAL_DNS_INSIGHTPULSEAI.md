# Canonical DNS - insightpulseai.net

**Status**: PRODUCTION  
**Stack**: Odoo CE, n8n, MCP Hub, Superset, Mailgun  
**Provider**: DigitalOcean DNS  
**Last Updated**: 2026-01-28

---

## 1. A / CNAME Records (Apps & Core)

| Host          | Type  | Value              | Purpose                  |
|---------------|-------|--------------------|--------------------------|
| @             | A     | 178.128.112.214    | Root site / default vhost|
| www           | CNAME | insightpulseai.net | Canonical WWW alias      |
| erp           | A     | 178.128.112.214    | Odoo production          |
| erp.staging   | A     | 178.128.112.214    | Odoo staging             |
| n8n           | A     | 178.128.112.214    | n8n automation           |
| mcp           | A     | 178.128.112.214    | MCP / tools hub          |
| auth          | A     | 178.128.112.214    | Auth / IdP / SSO         |
| superset      | A     | 178.128.112.214    | Superset BI              |

**Notes**:
- All app subdomains terminate on the **same DO droplet** (178.128.112.214)
- Traffic demultiplexed by nginx virtual hosts
- If splitting infrastructure, move individual A records to new IPs (not `@`)

---

## 2. Mailgun - mg.insightpulseai.net

Mailgun is the canonical mail sending domain for transactional emails.

### 2.1. MX Records

| Host | Type | Priority | Value          | Purpose                |
|------|------|----------|----------------|------------------------|
| mg   | MX   | 10       | mxa.mailgun.org| Primary Mailgun MX     |
| mg   | MX   | 10       | mxb.mailgun.org| Secondary Mailgun MX   |

### 2.2. SPF (Subdomain)

| Host | Type | Value                             | Purpose                         |
|------|------|-----------------------------------|---------------------------------|
| mg   | TXT  | v=spf1 include:mailgun.org ~all   | SPF for *@mg.insightpulseai.net |

### 2.3. DKIM

From Mailgun (selector `pic` already present):

| Host                | Type | Value (truncated) | Purpose    |
|---------------------|------|-------------------|------------|
| email.mg            | CNAME| mailgun.org       | Mailgun CNAME helper |
| pic._domainkey.mg   | TXT  | k=rsa; p=...      | DKIM key   |

*Additional `_domainkey.mg` selectors issued by Mailgun should be added here*

### 2.4. DMARC (Subdomain)

| Host       | Type | Value                                                                     | Purpose                         |
|------------|------|---------------------------------------------------------------------------|---------------------------------|
| _dmarc.mg  | TXT  | v=DMARC1; p=none; pct=100; fo=1; ri=3600; rua=...; ruf=...               | DMARC for mg.insightpulseai.net |

---

## 3. Root Domain Email (insightpulseai.net)

Root domain also authorized to send via Mailgun.

### 3.1. SPF (Root)

| Host | Type | Value                             | Purpose                             |
|------|------|-----------------------------------|-------------------------------------|
| @    | TXT  | v=spf1 include:mailgun.org ~all   | SPF for *@insightpulseai.net        |

### 3.2. DMARC (Root)

| Host    | Type | Value                                      | Purpose               |
|---------|------|--------------------------------------------|-----------------------|
| _dmarc  | TXT  | v=DMARC1; p=none; rua=mailto:3651085@dmarc.mailgun.org | DMARC for root domain |

**Future Hardening** (optional, not required today):
- Move `p=none` → `p=quarantine` then `p=reject` once traffic stable
- Add ruf (forensic reporting) if desired

---

## 4. CAA (Certificate Authority Authorization)

Restricts certificate issuance to Let's Encrypt only:

| Host | Type | Value                  | Purpose             |
|------|------|------------------------|---------------------|
| @    | CAA  | 0 issue "letsencrypt.org" | Restrict CA to LE |

---

## 5. Canonical Summary

A canonical configuration for `insightpulseai.net` includes:

**Core Records**:
- A records: @, erp, erp.staging, n8n, mcp, auth, superset
- CNAME: www → insightpulseai.net

**Mailgun (mg.insightpulseai.net)**:
- MX: mxa/mxb.mailgun.org
- DKIM TXT
- SPF TXT  
- DMARC TXT

**Root Domain Email**:
- SPF + DMARC for *@insightpulseai.net

**Security**:
- CAA allowing only Let's Encrypt

**Current Status**: Live DNS matches this canonical layout. Future changes must be reflected here as SSOT.

---

## 6. Verification Commands

```bash
# A records
dig +short insightpulseai.net A
dig +short erp.insightpulseai.net A
dig +short erp.staging.insightpulseai.net A
dig +short n8n.insightpulseai.net A
dig +short mcp.insightpulseai.net A
dig +short superset.insightpulseai.net A
dig +short auth.insightpulseai.net A

# Mailgun records
dig +short mg.insightpulseai.net MX
dig +short mg.insightpulseai.net TXT
dig +short _dmarc.mg.insightpulseai.net TXT

# Root domain email
dig +short insightpulseai.net TXT
dig +short _dmarc.insightpulseai.net TXT

# CAA
dig +short insightpulseai.net CAA
```

All results should match values documented above.
