# Wix DNS Configuration for Mailgun

## Domain: mg.insightpulseai.com
## DNS Provider: Wix (ns6.wixdns.net, ns7.wixdns.net)

### Access Wix DNS Dashboard

1. Go to https://manage.wix.com
2. Click "Domains" in left sidebar
3. Select `insightpulseai.com`
4. Click "Manage DNS Records" or "DNS Records"

---

## DNS Records to Add

### 1. SPF Record (TXT)
| Field | Value |
|-------|-------|
| Type | TXT |
| Host | `mg` |
| Value | `v=spf1 include:mailgun.org ~all` |

### 2. DKIM Record (TXT)
| Field | Value |
|-------|-------|
| Type | TXT |
| Host | `mx._domainkey.mg` |
| Value | `k=rsa; p=MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQC59AXS0WKSDfH3HaKlpa1a3dusQWC7PECyywHd2mntae8jiwJ9++tHgu+YFNRVwXTmCFfUIsUdQpmxhYyVsYVLis/xagryklQ/wU3SF0E3Qso796fV9x1ShYb/W9rqpiW8jVD78LSppRquyYwTNLuP2+5hWFLxxVqPJYWZBHE2CQIDAQAB` |

### 3. MX Record (Primary)
| Field | Value |
|-------|-------|
| Type | MX |
| Host | `mg` |
| Points to | `mxa.mailgun.org` |
| Priority | `10` |

### 4. MX Record (Secondary)
| Field | Value |
|-------|-------|
| Type | MX |
| Host | `mg` |
| Points to | `mxb.mailgun.org` |
| Priority | `10` |

### 5. CNAME Record (Tracking - Optional)
| Field | Value |
|-------|-------|
| Type | CNAME |
| Host | `email.mg` |
| Points to | `mailgun.org` |

---

## Root Domain Records (if not already set)

### Combined SPF for Root Domain
| Field | Value |
|-------|-------|
| Type | TXT |
| Host | `@` |
| Value | `v=spf1 include:zohomail.com include:mailgun.org ~all` |

### DMARC Record
| Field | Value |
|-------|-------|
| Type | TXT |
| Host | `_dmarc` |
| Value | `v=DMARC1; p=quarantine; rua=mailto:dmarc@insightpulseai.com` |

---

## Verification

After adding records, wait 5-60 minutes for DNS propagation, then:

1. **In Mailgun Dashboard**: Click "Verify DNS Settings"
2. **CLI verification**:
   ```bash
   # Check SPF
   dig TXT mg.insightpulseai.com +short

   # Check DKIM
   dig TXT mx._domainkey.mg.insightpulseai.com +short

   # Check MX
   dig MX mg.insightpulseai.com +short
   ```

---

## Expected Verification Output

```
✓ SPF Record: v=spf1 include:mailgun.org ~all
✓ DKIM Record: k=rsa; p=MIGfMA0GCSqGSIb3DQEBAQUAA4...
✓ MX Records: mxa.mailgun.org, mxb.mailgun.org
```

---

## SMTP Credentials

| User | Login | Purpose |
|------|-------|---------|
| No-Reply | `no-reply@mg.insightpulseai.com` | System notifications, invoices |
| Support | `support@mg.insightpulseai.com` | Helpdesk, customer support |

**SMTP Server**: `smtp.mailgun.org`
**Port**: `587` (TLS/STARTTLS)
