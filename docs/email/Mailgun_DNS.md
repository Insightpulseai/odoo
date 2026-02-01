# DNS Configuration and Mailgun Setup

**Domain**: `insightpulseai.com`
**Droplet IP**: `178.128.112.214`
**Last Updated**: 2026-01-08

---

## DNS A Records (DigitalOcean)

All subdomains point to the single production droplet for host-based nginx routing.

| Subdomain | Type | Value | Status | Purpose |
|-----------|------|-------|--------|---------|
| `erp.insightpulseai.com` | A | `178.128.112.214` | ✅ Active | Odoo CE 18.0 ERP |
| `n8n.insightpulseai.com` | A | `178.128.112.214` | ✅ Active | n8n Workflow Automation |
| `superset.insightpulseai.com` | A | `178.128.112.214` | ✅ Active | Apache Superset BI |
| `mcp.insightpulseai.com` | A | `178.128.112.214` | 🟡 Placeholder | MCP Coordinator |
| `ocr.insightpulseai.com` | A | `178.128.112.214` | 🟡 Placeholder | OCR Service (PaddleOCR-VL) |
| `auth.insightpulseai.com` | A | `178.128.112.214` | 🟡 Placeholder | Authentication Service |
| `chat.insightpulseai.com` | A | `178.128.112.214` | 🟡 Placeholder | Mattermost Chat |
| `affine.insightpulseai.com` | A | `178.128.112.214` | 🟡 Placeholder | Affine Knowledge Base |

**Status Legend**:
- ✅ Active: Service deployed and accessible
- 🟡 Placeholder: Nginx returns 503, service not yet deployed

---

## Nginx Host-Based Routing

**File**: `/opt/odoo-ce/repo/deploy/nginx-complete.conf`

Nginx routes requests based on the `Host` header:

```nginx
# Example upstream blocks
upstream odoo { server odoo:8069; }
upstream n8n { server n8n:5678; }
upstream superset { server superset:8088; }

# HTTP → HTTPS redirect
server {
    listen 80;
    server_name insightpulseai.com *.insightpulseai.com;
    location /.well-known/acme-challenge/ { root /var/www/html; }
    location / { return 301 https://$host$request_uri; }
}

# Active service routing (example: Odoo)
server {
    listen 443 ssl http2;
    server_name erp.insightpulseai.com;
    ssl_certificate /etc/letsencrypt/live/erp.insightpulseai.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/erp.insightpulseai.com/privkey.pem;

    location / {
        proxy_pass http://odoo;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# Placeholder service routing (example: MCP)
server {
    listen 443 ssl http2;
    server_name mcp.insightpulseai.com;
    ssl_certificate /etc/letsencrypt/live/mcp.insightpulseai.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/mcp.insightpulseai.com/privkey.pem;

    location / {
        return 503 "MCP service not yet deployed";
        add_header Content-Type text/plain;
    }
}
```

---

## SSL/TLS Certificates

**Provider**: Let's Encrypt
**Method**: Certbot standalone mode
**Auto-Renewal**: Enabled via systemd timer

### Certificate Installation

```bash
# Install certbot
apt-get update && apt-get install -y certbot

# Obtain certificates (standalone mode, nginx stopped)
systemctl stop nginx
certbot certonly --standalone \
    -d erp.insightpulseai.com \
    -d n8n.insightpulseai.com \
    -d superset.insightpulseai.com \
    -d mcp.insightpulseai.com \
    -d ocr.insightpulseai.com \
    -d auth.insightpulseai.com \
    -d chat.insightpulseai.com \
    -d affine.insightpulseai.com \
    --non-interactive --agree-tos --email business@insightpulseai.com

# Restart nginx
systemctl start nginx
```

### Certificate Renewal

```bash
# Test renewal
certbot renew --dry-run

# Force renewal
certbot renew --force-renewal

# Auto-renewal is enabled via systemd timer
systemctl status certbot.timer
```

---

## Mailgun Email Configuration

**Domain**: `email.insightpulseai.com`
**Region**: US
**Purpose**: Transactional emails from Odoo, n8n, Mattermost

### DNS Records for Mailgun

Add these records in DigitalOcean DNS:

| Type | Name | Value | TTL | Purpose |
|------|------|-------|-----|---------|
| CNAME | `email.insightpulseai.com` | `mailgun.org` | 3600 | Mailgun routing |
| TXT | `insightpulseai.com` | `v=spf1 include:mailgun.org ~all` | 3600 | SPF (Sender Policy Framework) |
| TXT | `k1._domainkey.insightpulseai.com` | `k=rsa; p=MIGfMA0...` | 3600 | DKIM public key |
| TXT | `_dmarc.insightpulseai.com` | `v=DMARC1; p=none; rua=mailto:postmaster@insightpulseai.com` | 3600 | DMARC policy |
| MX | `insightpulseai.com` | `mxa.mailgun.org` (priority 10) | 3600 | Inbound mail |
| MX | `insightpulseai.com` | `mxb.mailgun.org` (priority 10) | 3600 | Inbound mail backup |

**Note**: The actual DKIM public key (`p=MIGfMA0...`) is provided by Mailgun after domain verification. Retrieve from Mailgun dashboard under Domain Settings → DNS Records.

### Mailgun API Configuration

**Environment Variables** (already set in `.env` files):

```bash
# Mailgun API credentials
MAILGUN_API_KEY="key-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
MAILGUN_DOMAIN="email.insightpulseai.com"
MAILGUN_API_BASE_URL="https://api.mailgun.net/v3"

# Odoo email configuration
EMAIL_HOST="smtp.mailgun.org"
EMAIL_PORT="587"
EMAIL_USE_TLS="True"
EMAIL_HOST_USER="postmaster@email.insightpulseai.com"
EMAIL_HOST_PASSWORD="$MAILGUN_SMTP_PASSWORD"
```

### Odoo Email Configuration

**File**: `deploy/odoo.conf`

```ini
[options]
# Outgoing mail server (Mailgun SMTP)
smtp_server = smtp.mailgun.org
smtp_port = 587
smtp_user = postmaster@email.insightpulseai.com
smtp_password = <MAILGUN_SMTP_PASSWORD>
smtp_ssl = False
smtp_ssl_starttls = True

# Email settings
email_from = InsightPulse AI <noreply@insightpulseai.com>
bounce_email = bounce@insightpulseai.com
```

---

## Verification Steps

### 1. DNS Resolution Verification

```bash
# Verify A records resolve to droplet IP
for subdomain in erp n8n superset mcp ocr auth chat affine; do
  echo "$subdomain.insightpulseai.com:"
  dig +short $subdomain.insightpulseai.com
  echo ""
done

# Expected output: 178.128.112.214 for all subdomains
```

### 2. HTTPS Verification

```bash
# Verify SSL certificates and HTTP → HTTPS redirect
for subdomain in erp n8n superset mcp ocr auth chat affine; do
  echo "$subdomain.insightpulseai.com:"
  curl -I https://$subdomain.insightpulseai.com 2>&1 | head -1
  echo ""
done

# Expected: HTTP/2 200 (active) or HTTP/2 503 (placeholder)
```

### 3. Mailgun DNS Verification

```bash
# Verify SPF record
dig +short TXT insightpulseai.com | grep "v=spf1"

# Verify DKIM record
dig +short TXT k1._domainkey.insightpulseai.com

# Verify DMARC record
dig +short TXT _dmarc.insightpulseai.com

# Verify MX records
dig +short MX insightpulseai.com
```

### 4. Email Send Test

```bash
# Test with Mailgun API
curl -s --user "api:$MAILGUN_API_KEY" \
    https://api.mailgun.net/v3/email.insightpulseai.com/messages \
    -F from="test@insightpulseai.com" \
    -F to="your-email@example.com" \
    -F subject="Mailgun DNS Test" \
    -F text="This is a test email to verify Mailgun configuration."

# Test with Odoo (from Odoo shell)
docker exec -it odoo-core odoo shell -d odoo_core <<EOF
env['mail.mail'].create({
    'email_from': 'noreply@insightpulseai.com',
    'email_to': 'your-email@example.com',
    'subject': 'Odoo Email Test',
    'body_html': '<p>Test email from Odoo</p>'
}).send()
EOF
```

---

## Troubleshooting

### Issue: DNS not resolving

**Symptoms**: `dig` returns no results or wrong IP

**Diagnosis**:
```bash
# Check DigitalOcean DNS settings
doctl compute domain records list insightpulseai.com

# Verify DNS propagation
nslookup erp.insightpulseai.com 8.8.8.8
```

**Resolution**:
1. Log into DigitalOcean dashboard
2. Navigate to Networking → Domains → insightpulseai.com
3. Verify A records point to correct droplet IP
4. Wait 5-10 minutes for DNS propagation

### Issue: ERR_CONNECTION_REFUSED

**Symptoms**: Browser shows "This site can't be reached"

**Diagnosis**:
```bash
# Check if nginx is running
ssh root@178.128.112.214 "systemctl status nginx"

# Check if port 443 is listening
ssh root@178.128.112.214 "netstat -tlnp | grep :443"

# Check SSL certificate files exist
ssh root@178.128.112.214 "ls -la /etc/letsencrypt/live/*/fullchain.pem"
```

**Resolution**:
1. Restart nginx: `systemctl restart nginx`
2. Check nginx error logs: `tail -f /var/log/nginx/error.log`
3. Verify SSL certificates installed correctly
4. Ensure Docker nginx container has `/etc/letsencrypt` mounted

### Issue: Nginx returns 503 Service Unavailable

**Symptoms**: HTTPS works but service unavailable

**Diagnosis**:
```bash
# Check if backend service is running (example: Odoo)
ssh root@178.128.112.214 "docker ps | grep odoo"

# Check nginx upstream configuration
ssh root@178.128.112.214 "docker exec nginx-prod cat /etc/nginx/nginx.conf | grep -A 5 'upstream odoo'"

# Test backend directly
ssh root@178.128.112.214 "curl -I http://localhost:8069"
```

**Resolution**:
1. Start backend service: `docker-compose up -d odoo`
2. Verify service health: `docker logs odoo-core --tail 50`
3. Check nginx upstream configuration matches service port

### Issue: Mailgun emails not sending

**Symptoms**: Emails not delivered, Mailgun dashboard shows errors

**Diagnosis**:
```bash
# Check Mailgun DNS records
dig +short TXT insightpulseai.com | grep spf
dig +short TXT k1._domainkey.insightpulseai.com
dig +short MX insightpulseai.com

# Check Mailgun domain status
curl -s --user "api:$MAILGUN_API_KEY" \
    https://api.mailgun.net/v3/domains/email.insightpulseai.com | jq .

# Check Odoo mail queue
docker exec -it odoo-core odoo shell -d odoo_core <<EOF
failed_mails = env['mail.mail'].search([('state', '=', 'exception')])
print(f"Failed mails: {len(failed_mails)}")
for mail in failed_mails[:5]:
    print(f"  {mail.subject}: {mail.failure_reason}")
EOF
```

**Resolution**:
1. Verify all Mailgun DNS records are correct in DigitalOcean
2. Wait 24-48 hours for full DNS propagation
3. Check Mailgun dashboard for domain verification status
4. Verify SMTP credentials in Odoo configuration
5. Test with Mailgun API directly to isolate issue

---

## Maintenance

### Certificate Renewal Monitoring

```bash
# Check certificate expiry dates
ssh root@178.128.112.214 "certbot certificates"

# Verify auto-renewal timer is active
ssh root@178.128.112.214 "systemctl status certbot.timer"

# Manually trigger renewal check
ssh root@178.128.112.214 "certbot renew --dry-run"
```

### DNS Record Updates

When adding new subdomains:

1. Add A record in DigitalOcean DNS → `insightpulseai.com`
2. Obtain SSL certificate: `certbot certonly --standalone -d newservice.insightpulseai.com`
3. Add nginx server block in `/opt/odoo-ce/repo/deploy/nginx-complete.conf`
4. Restart nginx: `systemctl restart nginx` or `docker-compose restart nginx`

### Mailgun Domain Health

```bash
# Check Mailgun domain health monthly
curl -s --user "api:$MAILGUN_API_KEY" \
    https://api.mailgun.net/v3/domains/email.insightpulseai.com/verify \
    | jq .
```

---

## References

- **Let's Encrypt**: https://letsencrypt.org/
- **Certbot Documentation**: https://eff-certbot.readthedocs.io/
- **Mailgun Documentation**: https://documentation.mailgun.com/
- **DigitalOcean DNS**: https://docs.digitalocean.com/products/networking/dns/
- **Nginx Host-Based Routing**: https://nginx.org/en/docs/http/ngx_http_core_module.html#server_name
- **SPF Records**: https://www.rfc-editor.org/rfc/rfc7208
- **DKIM**: https://www.rfc-editor.org/rfc/rfc6376
- **DMARC**: https://www.rfc-editor.org/rfc/rfc7489

---

**Last Updated**: 2026-01-08
**Maintainer**: Jake Tolentino <business@insightpulseai.com>
