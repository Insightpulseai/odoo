# Mailgun DNS Configuration for insightpulseai.net

## Current Records (Verified Working)

| Host | Type | Priority | TTL | Data |
|------|------|----------|-----|------|
| `email.mg` | CNAME | - | 1 hr | mailgun.org |
| `pic._domainkey.mg` | TXT | - | 1 hr | `k=rsa; p=MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDcYB3DG10ylI4z6PWaiwyiByMrjwr9kfgJK8ccsZYT4guxi8+Emyf/nUs7IqR/LTZwwymeTZDaS/vQ6pjDhIaF2J9M9XsdgP+nv3wx99BqQ7dA+aa5sNwJKI3WRhr1YMK6IJQJIWSLERPBr74eMBAVa/Zmrfui1BOCgUFvQN9GBQIDAQAB` |
| `mg` | TXT | - | 5 mins | `v=spf1 include:mailgun.org ~all` |

## Missing Records (Add These)

### MX Records for Bounce Handling

```
Host: mg
Type: MX
Priority: 10
Data: mxa.mailgun.org

Host: mg
Type: MX
Priority: 10
Data: mxb.mailgun.org
```

### DMARC Record

```
Host: _dmarc
Type: TXT
Priority: -
Data: v=DMARC1; p=none; rua=mailto:dmarc@insightpulseai.net
```

## DigitalOcean DNS API Commands

```bash
# Set your DO API token
export DO_TOKEN="your_digitalocean_api_token"

# Add MX record for mxa.mailgun.org
curl -X POST \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $DO_TOKEN" \
  -d '{"type":"MX","name":"mg","data":"mxa.mailgun.org.","priority":10,"ttl":3600}' \
  "https://api.digitalocean.com/v2/domains/insightpulseai.net/records"

# Add MX record for mxb.mailgun.org
curl -X POST \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $DO_TOKEN" \
  -d '{"type":"MX","name":"mg","data":"mxb.mailgun.org.","priority":10,"ttl":3600}' \
  "https://api.digitalocean.com/v2/domains/insightpulseai.net/records"

# Add DMARC record
curl -X POST \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $DO_TOKEN" \
  -d '{"type":"TXT","name":"_dmarc","data":"v=DMARC1; p=none; rua=mailto:dmarc@insightpulseai.net","ttl":3600}' \
  "https://api.digitalocean.com/v2/domains/insightpulseai.net/records"
```

## Verification Commands

```bash
# Verify MX records
dig MX mg.insightpulseai.net +short

# Verify DMARC
dig TXT _dmarc.insightpulseai.net +short

# Verify SPF
dig TXT mg.insightpulseai.net +short

# Verify DKIM
dig TXT pic._domainkey.mg.insightpulseai.net +short
```

## Mailgun Verification

After adding DNS records, verify in Mailgun dashboard:
1. Go to https://app.mailgun.com/app/sending/domains/mg.insightpulseai.net
2. Click "Check DNS Records Now"
3. All records should show green checkmarks

## Troubleshooting

### Common Issues

1. **"No MX for yourcompany.example.com"**
   - This is from Odoo's default config
   - Run `fix_odoo_email_config.sh` to update

2. **SPF failures**
   - Ensure SPF record includes `include:mailgun.org`
   - Check for duplicate SPF records

3. **DKIM failures**
   - Verify the full DKIM key is copied (no truncation)
   - Ensure proper quoting in TXT record
