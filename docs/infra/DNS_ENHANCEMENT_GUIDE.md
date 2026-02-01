# DNS Enhancement Guide - insightpulseai.com

**Purpose**: Enhance DNS configuration for improved email authentication and staging environment support

**Date**: 2026-01-28
**Status**: Recommended Changes

---

## Current DNS Status (Verified)

### ✅ Already Configured (DO NOT CHANGE)

**Root & Web**:
- `@` A → `178.128.112.214`
- `www` CNAME → `insightpulseai.com`

**App Hosts**:
- `erp` A → `178.128.112.214`
- `n8n` A → `178.128.112.214`
- `mcp` A → `178.128.112.214`
- `auth` A → `178.128.112.214`
- `superset` A → `178.128.112.214`

**Mailgun (mg subdomain)** - ✅ PROPERLY CONFIGURED:
- `mg` MX → `10 mxa.mailgun.org`
- `mg` MX → `10 mxb.mailgun.org`
- `mg` TXT → `v=spf1 include:mailgun.org ~all`
- `email.mg` CNAME → `mailgun.org`
- `pic._domainkey.mg` TXT → DKIM key (k=rsa; p=...)
- `_dmarc.mg` TXT → `v=DMARC1; p=none; pct=100; fo=1; ri=3600; rua=mailto:3651085@dmarc.mailgun.org,mailto:682ce2a3@inbox.ondmarc.com; ruf=mailto:3651085@dmarc.mailgun.org,mailto:682ce2a3@inbox.ondmarc.com;`

**CAA**:
- `@` CAA → `0 issue "letsencrypt.org"`

### ❌ Missing (Recommended Additions)

1. **Staging ERP DNS** - Not configured
2. **Root SPF** - Not configured
3. **Root DMARC** - Not configured

---

## Recommended DNS Changes

### 1. Staging ERP A Record

**Purpose**: Enable `erp.staging.insightpulseai.com` for staging environment testing

| Host | Type | TTL | Data | Priority |
|------|------|-----|------|----------|
| `erp.staging` | A | 3600 | `178.128.112.214` | Optional |

**Why**: Matches nginx configuration for staging environment. Safe to add even if not immediately used.

### 2. Root SPF Record

**Purpose**: Authorize Mailgun to send email from `*@insightpulseai.com` (not just `*@mg.insightpulseai.com`)

| Host | Type | TTL | Data | Priority |
|------|------|-----|------|----------|
| `@` | TXT | 3600 | `v=spf1 include:mailgun.org ~all` | Recommended |

**Why**:
- Currently SPF only covers `mg.insightpulseai.com`
- If sending email as `business@insightpulseai.com` or `*@insightpulseai.com`, root SPF prevents spam classification
- Without this, emails from root domain may fail SPF checks

### 3. Root DMARC Record

**Purpose**: Provide DMARC policy and reporting for `*@insightpulseai.com` root domain

| Host | Type | TTL | Data | Priority |
|------|------|-----|------|----------|
| `_dmarc` | TXT | 3600 | `v=DMARC1; p=none; rua=mailto:3651085@dmarc.mailgun.org` | Recommended |

**Alternative (Mirror mg DMARC)**:
```txt
v=DMARC1; p=none; pct=100; fo=1; ri=3600; rua=mailto:3651085@dmarc.mailgun.org,mailto:682ce2a3@inbox.ondmarc.com; ruf=mailto:3651085@dmarc.mailgun.org,mailto:682ce2a3@inbox.ondmarc.com;
```

**Why**:
- Provides email authentication reporting for root domain
- Helps detect email spoofing/phishing attempts
- Improves email deliverability for root domain sends

---

## DNS Panel Input Specification

### Step-by-Step Instructions

**Access**: DigitalOcean DNS Panel → `insightpulseai.com` → Manage Domain

#### Record 1: Staging ERP (Optional)

```
Type: A
Hostname: erp.staging
Value: 178.128.112.214
TTL: 1 hour
```

#### Record 2: Root SPF (Recommended)

```
Type: TXT
Hostname: @
Value: v=spf1 include:mailgun.org ~all
TTL: 1 hour
```

**⚠️ Important**: If existing TXT record exists at `@`, merge values or replace obsolete record.

#### Record 3: Root DMARC (Recommended)

```
Type: TXT
Hostname: _dmarc
Value: v=DMARC1; p=none; rua=mailto:3651085@dmarc.mailgun.org
TTL: 1 hour
```

**Alternative (Full Reporting)**:
```
Value: v=DMARC1; p=none; pct=100; fo=1; ri=3600; rua=mailto:3651085@dmarc.mailgun.org,mailto:682ce2a3@inbox.ondmarc.com; ruf=mailto:3651085@dmarc.mailgun.org,mailto:682ce2a3@inbox.ondmarc.com;
```

---

## Verification Commands

### After DNS Changes (Wait 5-15 minutes for propagation)

```bash
# 1. Verify Staging ERP DNS
dig erp.staging.insightpulseai.com A +short
# Expected: 178.128.112.214

# 2. Verify Root SPF
dig insightpulseai.com TXT +short | grep spf
# Expected: v=spf1 include:mailgun.org ~all

# 3. Verify Root DMARC
dig _dmarc.insightpulseai.com TXT +short
# Expected: v=DMARC1; p=none; rua=mailto:3651085@dmarc.mailgun.org

# 4. Sanity Check: Existing Mailgun mg Records
dig mg.insightpulseai.com MX +short
# Expected: 10 mxa.mailgun.org, 10 mxb.mailgun.org

dig mg.insightpulseai.com TXT +short | grep spf
# Expected: v=spf1 include:mailgun.org ~all

dig _dmarc.mg.insightpulseai.com TXT +short
# Expected: v=DMARC1; p=none; pct=100; fo=1; ri=3600; ...
```

### Complete Verification Script

Save as `scripts/verify-dns-enhancements.sh`:

```bash
#!/usr/bin/env bash
set -euo pipefail

echo "=== DNS Enhancement Verification ==="
echo

echo "1. Staging ERP DNS:"
dig erp.staging.insightpulseai.com A +short || echo "❌ Not configured"
echo

echo "2. Root SPF:"
dig insightpulseai.com TXT +short | grep spf || echo "❌ Not configured"
echo

echo "3. Root DMARC:"
dig _dmarc.insightpulseai.com TXT +short || echo "❌ Not configured"
echo

echo "4. Existing Mailgun mg SPF (sanity check):"
dig mg.insightpulseai.com TXT +short | grep spf
echo

echo "5. Existing Mailgun mg DMARC (sanity check):"
dig _dmarc.mg.insightpulseai.com TXT +short
echo

echo "=== Verification Complete ==="
```

---

## Risk Assessment

### Low Risk Changes

✅ **Adding these records is SAFE**:
- Does NOT modify existing Mailgun configuration
- Does NOT break current email flow
- Staging DNS is harmless if unused (just points to existing droplet)

### What NOT to Change

❌ **DO NOT modify**:
- Existing `mg.insightpulseai.com` MX/TXT/CNAME records
- Existing `pic._domainkey.mg` DKIM key
- Existing `_dmarc.mg` DMARC policy
- Any existing A records for production apps

### Rollback Plan

If issues occur, simply **delete** the new TXT records:
```bash
# In DNS panel, delete:
# - TXT record at @ (SPF)
# - TXT record at _dmarc (DMARC)
# - A record at erp.staging (if added)
```

---

## Email Sending Patterns

### Current State
- ✅ `*@mg.insightpulseai.com` - Fully authenticated (SPF + DKIM + DMARC)
- ⚠️ `*@insightpulseai.com` - No SPF/DMARC (may trigger spam filters)

### After Enhancement
- ✅ `*@mg.insightpulseai.com` - Fully authenticated (unchanged)
- ✅ `*@insightpulseai.com` - Fully authenticated (SPF + DMARC added)

### Recommendation
- **If sending ONLY from** `*@mg.insightpulseai.com`: Root SPF/DMARC are "nice to have"
- **If sending from** `business@insightpulseai.com` or other root domain addresses: Root SPF/DMARC are **required** for deliverability

---

## References

- **Mailgun SPF Documentation**: https://documentation.mailgun.com/docs/mailgun/user-manual/get-started/sending-email-best-practices/#spf-dkim-dmarc
- **DMARC Policy Guide**: https://dmarc.org/overview/
- **DigitalOcean DNS Management**: https://docs.digitalocean.com/products/networking/dns/

---

**Status**: Ready for implementation
**Approval Required**: Yes (manual DNS changes)
**Estimated Time**: 5 minutes (changes) + 15 minutes (propagation)
