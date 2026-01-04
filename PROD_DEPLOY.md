# IPAI Odoo CE Production Deployment Guide

Complete production deployment guide for Odoo CE with:
- Gmail/Google Workspace SMTP integration
- OCA "Enterprise replacement" modules
- Ask AI chatter integration
- ChatGPT Apps SDK integration
- IPAI design system theme

## Environment Variables

### Required (Odoo)

```bash
# Database
DB_HOST=db
DB_PORT=5432
DB_USER=odoo
DB_PASSWORD=<strong-password>
DB_NAME=odoo_prod

# Email (Gmail/Workspace SMTP)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=business@yourdomain.com
SMTP_PASSWORD=<google-app-password>
EMAIL_FROM=business@yourdomain.com

# Security
ADMIN_PASSWORD=<master-admin-password>
```

### Required (Ask AI Chatter)

Set via Odoo System Parameters or shell script:

```bash
ipai_ask_ai_chatter.enabled=True
ipai_ask_ai_chatter.api_url=https://your-executor-endpoint/ask-ai
ipai_ask_ai_chatter.api_key=<optional-bearer-token>
ipai_ask_ai_chatter.trigger=@askai
ipai_ask_ai_chatter.context_messages=12
ipai_ask_ai_chatter.timeout_seconds=30
```

### Required (ChatGPT App Server)

```bash
PORT=8787
MCP_PATH=/mcp
```

---

## Deployment Steps

### 1. Bootstrap OCA Addons

```bash
./scripts/oca-bootstrap.sh
```

This clones essential OCA repos:
- queue (queue_job)
- rest-framework (base_rest)
- server-ux (base_tier_validation)
- server-tools (iap_alternative_provider)
- web (web_responsive)

### 2. Sync Design Tokens

```bash
./scripts/sync-tokens.sh
```

Copies shared tokens to Odoo theme.

### 3. Start Odoo Stack

```bash
docker compose up -d
```

Wait for Odoo to be ready:
```bash
docker compose logs -f odoo
# Wait for "HTTP service (werkzeug) running"
```

### 4. Install Modules

In Odoo UI (Settings > Apps > Update Apps List):

1. **Install OCA essentials (in order):**
   - `queue_job`
   - `base_rest`
   - `base_tier_validation`
   - `web_responsive` (optional)

2. **Install IPAI modules:**
   - `ipai_web_theme_chatgpt` (design theme)
   - `ipai_ask_ai_chatter` (AI in chatter)

### 5. Configure Gmail SMTP

Run the configuration script:
```bash
docker exec -i odoo-core odoo shell -d odoo_core < scripts/configure_gmail_smtp.py
```

Or configure in Odoo UI:
1. Settings > Technical > Outgoing Mail Servers
2. Add Gmail SMTP with App Password
3. Test Connection

### 6. Configure Ask AI

```bash
docker exec -i odoo-core odoo shell -d odoo_core <<'PY'
ICP = env["ir.config_parameter"].sudo()
ICP.set_param("ipai_ask_ai_chatter.enabled", "True")
ICP.set_param("ipai_ask_ai_chatter.api_url", "https://your-executor/ask-ai")
ICP.set_param("ipai_ask_ai_chatter.api_key", "your-api-key")
ICP.set_param("ipai_ask_ai_chatter.trigger", "@askai")
env.cr.commit()
PY
```

### 7. Build & Start ChatGPT App

```bash
# Install dependencies
pnpm -C apps/ipai-chatgpt-app/web install
pnpm -C apps/ipai-chatgpt-app/server install

# Build widget
pnpm -C apps/ipai-chatgpt-app/web build

# Start MCP server
PORT=8787 pnpm -C apps/ipai-chatgpt-app/server start
```

---

## Production DNS Records (Gmail/Workspace)

Add these DNS records for `yourdomain.com`:

### MX Records
```
ASPMX.L.GOOGLE.COM         priority 1
ALT1.ASPMX.L.GOOGLE.COM    priority 5
ALT2.ASPMX.L.GOOGLE.COM    priority 5
ALT3.ASPMX.L.GOOGLE.COM    priority 10
ALT4.ASPMX.L.GOOGLE.COM    priority 10
```

### SPF (TXT record for @)
```
v=spf1 include:_spf.google.com ~all
```

### DKIM (TXT record - get from Google Admin)
```
google._domainkey   v=DKIM1; k=rsa; p=...
```

### DMARC (TXT record for _dmarc)
```
v=DMARC1; p=none; rua=mailto:dmarc@yourdomain.com; adkim=s; aspf=s
```

---

## System Parameters (Odoo)

Set these in Settings > Technical > Parameters > System Parameters:

| Key | Value |
|-----|-------|
| `web.base.url` | `https://erp.yourdomain.com` |
| `web.base.url.freeze` | `True` |
| `mail.catchall.domain` | `yourdomain.com` |
| `mail.catchall.alias` | `catchall` |
| `mail.bounce.alias` | `bounce` |

---

## Health Check URLs

| Service | URL |
|---------|-----|
| Odoo | `http://localhost:8069/web/health` |
| MCP Server | `http://localhost:8787/` |

---

## Rollback Instructions

### Odoo Module Rollback
```bash
# Uninstall a module
docker exec -i odoo-core odoo shell -d odoo_core <<'PY'
env['ir.module.module'].search([('name', '=', 'module_name')]).button_immediate_uninstall()
env.cr.commit()
PY
```

### Database Rollback
```bash
# Restore from backup
docker exec -i odoo-postgres pg_restore -U odoo -d odoo_core < backup.dump
```

### Container Rollback
```bash
# Use previous image tag
docker compose down
# Edit docker-compose.yml to use previous image
docker compose up -d
```

---

## Monitoring

### Check Odoo logs
```bash
docker compose logs -f odoo-core
```

### Check mail queue
```bash
docker exec -i odoo-core odoo shell -d odoo_core <<'PY'
mails = env['mail.mail'].search([('state', '!=', 'sent')])
for m in mails[:10]:
    print(f"{m.id}: {m.state} - {m.subject}")
PY
```

### Check Ask AI requests
```bash
docker exec -i odoo-core odoo shell -d odoo_core <<'PY'
reqs = env['ipai.ask_ai_chatter.request'].search([], limit=10, order='create_date desc')
for r in reqs:
    print(f"{r.uuid}: {r.state} - {r.question[:50]}")
PY
```
