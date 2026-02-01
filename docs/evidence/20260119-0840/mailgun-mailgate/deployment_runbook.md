# Mailgun Mailgate Deployment Runbook

## Overview

This document provides deployment instructions for the Mailgun Mailgate controller
added to `ipai_enterprise_bridge` module.

## Prerequisites

- Mailgun domain: `mg.insightpulseai.com` (configured with SPF, DKIM, DMARC, MX, CNAME)
- Production host: `erp.insightpulseai.com`
- SSH/CICD access to production server

## Deployment Steps

### 1. Pull Latest Code

```bash
cd /opt/odoo-ce/repo  # or appropriate path
git fetch origin claude/deploy-odoo-enterprise-bridge-RbvGm
git checkout claude/deploy-odoo-enterprise-bridge-RbvGm
git pull origin claude/deploy-odoo-enterprise-bridge-RbvGm
```

### 2. Upgrade Module

```bash
# Docker deployment
docker compose exec odoo-core odoo -d odoo_core -u ipai_enterprise_bridge --stop-after-init

# Or systemd deployment
odoo -c /etc/odoo/odoo.conf -d odoo_core -u ipai_enterprise_bridge --stop-after-init
```

### 3. Restart Service

```bash
# Docker
docker compose restart odoo-core

# Or systemd
systemctl restart odoo.service
```

### 4. Validate Endpoint

```bash
# Health check (GET)
curl -I https://erp.insightpulseai.com/mailgate/mailgun

# Expected: HTTP/2 200
```

### 5. Test Webhook

```bash
curl -X POST https://erp.insightpulseai.com/mailgate/mailgun \
  -H "Content-Type: application/x-www-form-urlencoded" \
  --data "sender=test@mg.insightpulseai.com" \
  --data "recipient=invoices@insightpulseai.com" \
  --data "subject=Mailgate Test $(date -Iseconds)" \
  --data "body-plain=Test message from deployment validation"

# Expected: {"status": "ok", "message_id": <int>, "message": "Email processed successfully"}
```

### 6. Verify Database

```bash
psql -d odoo_core -c \
"SELECT id, message_id, email_from, subject, date FROM mail_message ORDER BY id DESC LIMIT 5;"
```

## Mailgun Route Configuration

Configure this route in Mailgun dashboard for mg.insightpulseai.com:

- **Expression**: `match_recipient(".*@insightpulseai.com")`
- **Action**: `forward("https://erp.insightpulseai.com/mailgate/mailgun")`
- **Priority**: 0

## Rollback

```bash
git reset --hard HEAD~1
odoo -d odoo_core -u ipai_enterprise_bridge --stop-after-init
systemctl restart odoo.service
```

## Security Notes

- CSRF is disabled for webhook endpoint (required for external webhooks)
- Mailgun signature verification is implemented but disabled by default
- To enable signature verification:
  1. Set `ipai_enterprise_bridge.mailgun_api_key` system parameter
  2. Uncomment verification block in mailgun_mailgate.py

## Success Criteria

- [ ] HTTP 200 on GET /mailgate/mailgun
- [ ] HTTP 200 on POST /mailgate/mailgun with valid payload
- [ ] mail.message records created in database
- [ ] No errors in Odoo logs after deployment
