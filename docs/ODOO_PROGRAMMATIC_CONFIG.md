# Odoo 18 Programmatic Settings Configuration Guide

## Complete CLI & Automation Reference for InsightPulse AI

**Version:** 1.0
**Target:** Odoo 18 CE + Docker
**Scope:** All settings configuration methods via CLI

---

## Table of Contents

1. [Configuration Methods Overview](#1-configuration-methods-overview)
2. [odoo.conf - Server Configuration File](#2-odooconf---server-configuration-file)
3. [Odoo Shell - Interactive ORM Access](#3-odoo-shell---interactive-orm-access)
4. [Python Scripts with Odoo Environment](#4-python-scripts-with-odoo-environment)
5. [XML-RPC External API](#5-xml-rpc-external-api)
6. [Direct PostgreSQL SQL](#6-direct-postgresql-sql)
7. [XML Data Files (Module-based)](#7-xml-data-files-module-based)
8. [Docker Integration Patterns](#8-docker-integration-patterns)
9. [Specific Configuration Examples](#9-specific-configuration-examples)
10. [Automation Scripts](#10-automation-scripts)

---

## 1. Configuration Methods Overview

| Method | Best For | Persistence | Requires Restart |
|--------|----------|-------------|------------------|
| `odoo.conf` | Server/infra settings | Yes | Yes |
| Odoo Shell | Interactive testing, one-off changes | Yes (with commit) | No |
| Python Scripts | Batch operations, CI/CD | Yes | No |
| XML-RPC API | External integrations | Yes | No |
| Direct SQL | Emergency fixes, migrations | Yes | No |
| XML Data Files | Module defaults, deployment | Yes | Module update |

---

## 2. odoo.conf - Server Configuration File

### Location in Docker
```bash
# Standard location
/etc/odoo/odoo.conf

# View current config in container
docker exec odoo cat /etc/odoo/odoo.conf
```

### Key Configuration Parameters

```ini
[options]
# Database
db_host = db
db_port = 5432
db_user = odoo
db_password = odoo
db_name = odoo
db_maxconn = 64
db_template = template1

# Server
http_port = 8069
longpolling_port = 8072
proxy_mode = True
workers = 4
max_cron_threads = 2

# Paths
addons_path = /mnt/extra-addons,/usr/lib/python3/dist-packages/odoo/addons
data_dir = /var/lib/odoo

# Logging
logfile = /var/log/odoo/odoo.log
log_level = info
log_handler = :INFO

# Email (SMTP via CLI)
smtp_server = smtp.gmail.com
smtp_port = 587
smtp_ssl = True
smtp_user = your-email@gmail.com
smtp_password = your-app-password
email_from = noreply@yourdomain.com

# Security
admin_passwd = your-master-password
list_db = False
dbfilter = ^odoo$

# Performance
limit_memory_hard = 2684354560
limit_memory_soft = 2147483648
limit_request = 8192
limit_time_cpu = 600
limit_time_real = 1200
limit_time_real_cron = 3600

# Development (disable in production)
dev_mode = False
```

### Generate Config from CLI
```bash
# Generate default config file
docker exec odoo odoo --save --stop-after-init -c /etc/odoo/odoo.conf

# Generate with specific options
docker exec odoo odoo \
  --db_host=db \
  --db_user=odoo \
  --addons-path=/mnt/extra-addons \
  --save --stop-after-init
```

---

## 3. Odoo Shell - Interactive ORM Access

### Launching Shell

```bash
# Docker exec into Odoo shell
docker exec -it odoo odoo shell -d odoo -c /etc/odoo/odoo.conf

# Or with full path
docker exec -it odoo /usr/bin/odoo shell -d odoo
```

### Shell Commands for Settings

```python
# ============================================
# SYSTEM PARAMETERS (ir.config_parameter)
# ============================================

# Get parameter
env['ir.config_parameter'].sudo().get_param('web.base.url')

# Set parameter
env['ir.config_parameter'].sudo().set_param('web.base.url', 'https://erp.insightpulseai.net')

# Common system parameters
env['ir.config_parameter'].sudo().set_param('mail.catchall.domain', 'insightpulseai.net')
env['ir.config_parameter'].sudo().set_param('mail.default.from', 'notifications')
env['ir.config_parameter'].sudo().set_param('mail.catchall.alias', 'catchall')
env['ir.config_parameter'].sudo().set_param('mail.bounce.alias', 'bounce')

# Commit changes (REQUIRED!)
env.cr.commit()


# ============================================
# OUTGOING MAIL SERVER (ir.mail_server)
# ============================================

# Create SMTP server
mail_server = env['ir.mail_server'].sudo().create({
    'name': 'Gmail SMTP',
    'smtp_host': 'smtp.gmail.com',
    'smtp_port': 587,
    'smtp_encryption': 'starttls',
    'smtp_user': 'your-email@gmail.com',
    'smtp_pass': 'vzabhqzhwvhmzsgz',  # Gmail App Password
    'sequence': 10,
})
env.cr.commit()

# List existing mail servers
for server in env['ir.mail_server'].sudo().search([]):
    print(f"{server.name}: {server.smtp_host}:{server.smtp_port}")


# ============================================
# INCOMING MAIL SERVER (fetchmail.server)
# ============================================

# Create IMAP server
env['fetchmail.server'].sudo().create({
    'name': 'Gmail IMAP',
    'server_type': 'imap',
    'server': 'imap.gmail.com',
    'port': 993,
    'is_ssl': True,
    'user': 'your-email@gmail.com',
    'password': 'vzabhqzhwvhmzsgz',
    'state': 'done',
    'active': True,
})
env.cr.commit()


# ============================================
# COMPANY SETTINGS (res.company)
# ============================================

# Get main company
company = env['res.company'].sudo().browse(1)

# Update company details
company.write({
    'name': 'TBWA Philippines',
    'email': 'finance@tbwa.com.ph',
    'phone': '+63 2 1234 5678',
    'website': 'https://tbwa.com.ph',
    'currency_id': env.ref('base.PHP').id,
    'country_id': env.ref('base.ph').id,
})
env.cr.commit()


# ============================================
# RES.CONFIG.SETTINGS (Application Settings)
# ============================================

# Create and execute settings (transient model pattern)
settings = env['res.config.settings'].sudo().create({
    'group_multi_company': True,
    'module_project_timesheet': True,
    'group_project_stages': True,
    'external_email_server_default': True,
})
settings.execute()
env.cr.commit()


# ============================================
# USER MANAGEMENT
# ============================================

# Create user
env['res.users'].sudo().create({
    'name': 'Jake Tolentino',
    'login': 'jt@insightpulseai.net',
    'email': 'jt@insightpulseai.net',
    'groups_id': [(6, 0, [
        env.ref('base.group_user').id,
        env.ref('project.group_project_manager').id,
    ])],
})
env.cr.commit()

# Update existing user
user = env['res.users'].sudo().search([('login', '=', 'admin')], limit=1)
user.write({'x_employee_code': 'ADMIN'})
env.cr.commit()


# ============================================
# MODULE INSTALLATION
# ============================================

# Install modules
modules_to_install = ['project', 'hr', 'account', 'mail']
for module_name in modules_to_install:
    module = env['ir.module.module'].sudo().search([('name', '=', module_name)], limit=1)
    if module and module.state != 'installed':
        module.button_immediate_install()

env.cr.commit()
```

### Shell Script Automation
```bash
# Execute Python code via shell
docker exec -i odoo odoo shell -d odoo --no-http << 'EOF'
env['ir.config_parameter'].sudo().set_param('web.base.url', 'https://erp.insightpulseai.net')
env.cr.commit()
print("Done!")
EOF
```

---

## Gmail App Password Setup

**Generate App Password:**
1. Go to Google Account → Security → 2-Step Verification
2. Scroll to "App passwords" → Select app: Mail → Select device: Other
3. Name it "Odoo SMTP"
4. **Copy the 16-character password** (format: `xxxx xxxx xxxx xxxx`)
5. **Remove spaces** when pasting: `vzabhqzhwvhmzsgz`

**Configure in Odoo Shell:**
```python
docker exec -it odoo odoo shell -d odoo << 'EOF'
MailServer = env['ir.mail_server'].sudo()

# Delete old Gmail servers
MailServer.search([('smtp_host', '=', 'smtp.gmail.com')]).unlink()

# Create new server with App Password
MailServer.create({
    'name': 'Gmail SMTP',
    'smtp_host': 'smtp.gmail.com',
    'smtp_port': 587,
    'smtp_encryption': 'starttls',
    'smtp_user': 'your-email@gmail.com',
    'smtp_pass': 'vzabhqzhwvhmzsgz',  # 16-char App Password (no spaces)
    'sequence': 10,
})
env.cr.commit()
print("✅ Gmail SMTP configured")
EOF
```

**Or via Settings UI:**
1. Settings → Technical → Outgoing Mail Servers → Create
2. Description: `Gmail SMTP`
3. SMTP Server: `smtp.gmail.com`
4. SMTP Port: `587`
5. Connection Security: **TLS (STARTTLS)**
6. Username: Your Gmail address
7. Password: `vzabhqzhwvhmzsgz` (App Password, no spaces)
8. Click **Test Connection** → **Save**

---

## Quick Reference: One-Liners

```bash
# Set system parameter
docker exec odoo odoo shell -d odoo --no-http << 'EOF'
env['ir.config_parameter'].sudo().set_param('web.base.url', 'https://erp.insightpulseai.net')
env.cr.commit()
EOF

# Configure Gmail SMTP
docker exec odoo odoo shell -d odoo --no-http << 'EOF'
env['ir.mail_server'].sudo().create({
    'name': 'Gmail SMTP',
    'smtp_host': 'smtp.gmail.com',
    'smtp_port': 587,
    'smtp_encryption': 'starttls',
    'smtp_user': 'your-email@gmail.com',
    'smtp_pass': 'vzabhqzhwvhmzsgz',
    'sequence': 10,
})
env.cr.commit()
EOF

# Update module
docker exec odoo odoo -d odoo -u module_name --stop-after-init

# Install module
docker exec odoo odoo -d odoo -i module_name --stop-after-init

# Direct SQL
docker exec odoo-db psql -U odoo -d odoo -c "UPDATE ir_config_parameter SET value='https://erp.insightpulseai.net' WHERE key='web.base.url';"
```

---

**Document Version:** 1.0
**Last Updated:** December 30, 2025
**Author:** InsightPulse AI / Jake Tolentino
