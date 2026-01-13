# Mailgun DNS Configuration for mg.insightpulseai.net

## SMTP Server Configuration (Already Applied to Odoo)

- **Host**: smtp.mailgun.org
- **Port**: 587
- **User**: postmaster@mg.insightpulseai.net
- **Encryption**: STARTTLS
- **From Domain**: mg.insightpulseai.net

## Required DNS Records

### 1. Sending Records (SPF + DKIM)

**SPF Record:**
```
Type: TXT
Host: mg.insightpulseai.net
Value: v=spf1 include:mailgun.org ~all
```

**DKIM Record:**
```
Type: TXT
Host: pic._domainkey.mg.insightpulseai.net
Value: k=rsa; p=MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDcYB3DG10ylI4z6PWaiwyiByMrjwr9kfgJK8ccsZYT4guxi8+Emyf/nUs7IqR/LTZwwymeTZDaS/vQ6pjDhIaF2J9M9XsdgP+nv3wx99BqQ7dA+aa5sNwJKI3WRhr1YMK6IJQJIWSLERPBr74eMBAVa/Zmrfui1BOCgUFvQN9GBQIDAQAB
```

### 2. Receiving Records (MX)

```
Type: MX
Host: mg.insightpulseai.net
Value: mxa.mailgun.org
Priority: 10

Type: MX
Host: mg.insightpulseai.net
Value: mxb.mailgun.org
Priority: 10
```

### 3. Tracking Records (CNAME)

```
Type: CNAME
Host: email.mg.insightpulseai.net
Value: mailgun.org
```

### 4. Authentication Records (DMARC)

```
Type: TXT
Host: _dmarc.mg.insightpulseai.net
Value: v=DMARC1; p=none; pct=100; fo=1; ri=3600; rua=mailto:3651085@dmarc.mailgun.org,mailto:682ce2a3@inbox.ondmarc.com; ruf=mailto:3651085@dmarc.mailgun.org,mailto:682ce2a3@inbox.ondmarc.com;
```

## Next Steps

1. **Add DNS Records**: Add all records above to your DNS provider
2. **Get SMTP Password**: From Mailgun dashboard for postmaster@mg.insightpulseai.net
3. **Update Odoo**: Settings → Technical → Outgoing Mail Servers → Add password
4. **Test Email**: Send test email from Odoo

---
*Last updated: 2026-01-13*
