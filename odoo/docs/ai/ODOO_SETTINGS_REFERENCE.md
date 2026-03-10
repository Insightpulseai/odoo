# Odoo Settings Reference

> Comprehensive guide to Odoo 19 CE settings, configuration, and access methods.
> Last updated: 2026-02-09

## Overview

**Settings Page Location:** `/odoo/settings` (requires admin access)
**Debug Mode:** Add `?debug=1` to URL for developer options
**Access Methods:** UI, XML-RPC API, Odoo shell, direct SQL

The Odoo settings page is the central hub for system configuration, covering everything from company information to technical parameters, email servers, and module-specific settings.

---

## Settings Sections (Odoo 19 CE)

### General Settings

#### System Parameters (`ir.config_parameter`)

Core system-wide configuration parameters:

| Parameter Key | Purpose | Example Value |
|---------------|---------|---------------|
| `web.base.url` | Base URL for web access | `https://insightpulseai.com` |
| `database.uuid` | Unique database identifier | `(auto-generated UUID)` |
| `web.session.timeout` | Session timeout in seconds | `7200` (2 hours) |
| `web.session.expire.delay` | Session expiry delay | `86400` (1 day) |
| `mail.catchall.domain` | Email catchall domain | `insightpulseai.com` |
| `mail.default.from` | Default sender email | `noreply@insightpulseai.com` |
| `mail.bounce.alias` | Bounce email alias | `bounce@insightpulseai.com` |
| `auth_signup.allow_uninvited` | Allow public signup | `True`/`False` |
| `portal.enable_signup` | Enable portal signup | `True`/`False` |
| `base.module_update` | Module update setting | `all`/`installed` |

#### Companies (`res.company`)

Multi-company management and configuration:

**Key Fields:**
- `name`: Company name
- `email`: Company email address
- `website`: Company website URL
- `currency_id`: Default currency
- `partner_id`: Related partner record
- `logo`: Company logo (binary)
- `street`, `street2`, `city`, `state_id`, `zip`, `country_id`: Address fields
- `phone`: Company phone number
- `vat`: Tax/VAT identification number

**Settings:**
- Multi-company management (enable/disable)
- Fiscal year configuration
- Currency settings
- Document layouts
- Bank account configuration

#### Users & Access Rights (`res.users`, `res.groups`)

User management and permission system:

**User Model (`res.users`):**
- `name`: User's full name
- `login`: Login username (usually email)
- `email`: Email address
- `password`: Hashed password
- `groups_id`: Permission groups (many2many)
- `company_id`: Default company
- `company_ids`: Allowed companies (multi-company)
- `active`: User active status
- `signature`: Email signature
- `tz`: Timezone
- `lang`: Language preference

**Groups Model (`res.groups`):**
- `name`: Group name
- `category_id`: Group category
- `users`: Users in this group
- `implied_ids`: Implied groups (inherited permissions)
- `model_access`: Access rights on models
- `rule_ids`: Record rules (row-level security)

**Permission Levels:**
1. **User**: Basic access (read own records)
2. **Officer**: Department-level access
3. **Manager**: Full module access
4. **Administrator**: System-wide access

### Technical Settings (Debug Mode Only)

Enable debug mode (`?debug=1`) to access advanced settings:

#### System Parameters (Direct Access)

Direct editing of `ir.config_parameter` records:
- Create new parameters
- Edit existing parameters
- Delete parameters
- Search and filter parameters
- View parameter metadata (create date, create user, etc.)

#### Server Actions (`ir.actions.server`)

Define custom server-side actions:

**Action Types:**
- **Execute Python Code**: Run Python code with `env` context
- **Create Record**: Create a new record in a model
- **Update Record**: Update existing record
- **Execute Multiple Actions**: Chain multiple actions
- **Send Email**: Send email using template
- **Add Followers**: Add followers to record
- **Create Next Activity**: Schedule activity
- **Send SMS**: Send SMS message

**Key Fields:**
- `name`: Action name
- `model_id`: Target model
- `state`: Action type
- `code`: Python code (for code execution type)
- `crud_model_id`: Model for create/update

#### Automated Actions (`base.automation`)

Define triggers and automated responses:

**Trigger Types:**
- **On Creation**: When record is created
- **On Update**: When record is updated
- **On Deletion**: When record is deleted
- **On Creation & Update**: Combined trigger
- **Based on Form Modification**: UI-triggered
- **Based on Timed Condition**: Time-based trigger

**Key Fields:**
- `name`: Automation name
- `model_id`: Target model
- `trigger`: Trigger type
- `filter_domain`: Domain filter for records
- `filter_pre_domain`: Pre-filter domain
- `action_server_id`: Server action to execute

#### Scheduled Actions (`ir.cron`)

Configure recurring tasks:

**Key Fields:**
- `name`: Cron job name
- `model_id`: Model to execute on
- `function`: Method to call
- `interval_number`: Interval quantity
- `interval_type`: Interval unit (minutes, hours, days, weeks, months)
- `numbercall`: Number of calls (-1 = unlimited)
- `doall`: Execute missed runs
- `nextcall`: Next execution time
- `priority`: Execution priority
- `active`: Active status

**Common Cron Jobs:**
- Email queue processor (every 1 minute)
- Session garbage collector (daily)
- Automatic backup (nightly)
- Report generation (scheduled)

#### Database Structure

View and modify database structure:
- Models and fields
- Field properties (type, required, readonly, etc.)
- Relations between models
- Indexes and constraints
- Custom fields

#### Custom Fields

Create custom fields on models:
- **Field Types**: Char, Text, Integer, Float, Boolean, Date, Datetime, Selection, Many2one, One2many, Many2many
- **Properties**: Required, Readonly, Searchable, Stored, Computed
- **Domain**: Filter options for relational fields
- **Dependencies**: Recompute triggers

### Communication Settings

#### Email Servers (`ir.mail_server`)

Configure outgoing and incoming mail servers:

**Outgoing Mail (SMTP):**

**Key Fields:**
- `name`: Server name (e.g., "Zoho Mail")
- `smtp_host`: SMTP server hostname (e.g., `smtp.zoho.com`)
- `smtp_port`: SMTP port (587 for STARTTLS, 465 for SSL)
- `smtp_user`: SMTP username
- `smtp_pass`: SMTP password
- `smtp_encryption`: Encryption type (`starttls`, `ssl`, `none`)
- `smtp_authentication`: Authentication type (`login`, `plain`)
- `sequence`: Priority order
- `active`: Active status

**Supported Providers:**
- **Zoho Mail**: `smtp.zoho.com:587` (STARTTLS)
- **Gmail**: `smtp.gmail.com:587` (STARTTLS, App Password required)
- **SendGrid**: `smtp.sendgrid.net:587` (API key as password)
- **Mailgun**: `smtp.mailgun.org:587` (SMTP credentials)
- **Custom SMTP**: Any standard SMTP server

**Configuration Scripts:**
- `scripts/configure_zoho_smtp.py`: Configure Zoho Mail
- `scripts/configure_gmail_smtp.py`: Configure Gmail
- `scripts/configure_sendgrid_smtp.py`: Configure SendGrid
- `scripts/audit_email_config.py`: Audit email settings
- `scripts/verify_smtp.py`: Test SMTP connection

**Incoming Mail (Fetchmail):**

Configure incoming mail servers for fetching emails into Odoo:
- **Server Type**: IMAP, POP3
- **Server**: Mail server hostname
- **Port**: Server port (993 for IMAP SSL, 995 for POP3 SSL)
- **SSL/TLS**: Encryption settings
- **Username/Password**: Mail account credentials
- **Action**: Create lead, create ticket, create task, etc.

### Integration Settings

#### External API Access

Configure API access for external systems:

**XML-RPC/JSON-RPC:**
- Endpoint: `/xmlrpc/2/` (XML-RPC), `/jsonrpc` (JSON-RPC)
- Authentication: Database, username, password
- Session management
- API keys (Odoo 19+)

**RESTful API (via modules):**
- Third-party modules for REST API
- OAuth authentication
- Rate limiting
- API documentation

#### OAuth Providers

Configure OAuth authentication providers:

**Supported Providers:**
- Google OAuth
- Microsoft OAuth
- Facebook OAuth
- GitHub OAuth
- Custom OAuth2 providers

**Configuration:**
- Client ID
- Client Secret
- Authorization URL
- Token URL
- Scope
- Redirect URI

### Module-Specific Settings

Each installed module adds its own settings section:

**Accounting:**
- Fiscal year and periods
- Taxes configuration
- Currency rates
- Payment terms
- Bank accounts
- Chart of accounts

**Sales:**
- Quotation and order settings
- Product configuration
- Invoicing policies
- Sales teams
- Pricelists

**Inventory:**
- Warehouse configuration
- Locations and routes
- Delivery methods
- Product variants
- Barcode settings

**Website:**
- Domain configuration
- Multilingual settings
- SEO configuration
- Google Analytics
- Social media integration

**HR:**
- Employee settings
- Leave types
- Expense categories
- Timesheets

**Project:**
- Project stages
- Task stages
- Timesheet configuration

---

## Accessing Settings Programmatically

### Method 1: XML-RPC API

Connect to running Odoo instance via XML-RPC:

```python
#!/usr/bin/env python3
"""
Access Odoo settings via XML-RPC
Requires Odoo running on http://localhost:8069
"""
import xmlrpc.client

# Configuration
url = "http://localhost:8069"
db = "odoo_dev"
username = "admin"
password = "admin"

# Authenticate
common = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common")
uid = common.authenticate(db, username, password, {})

if not uid:
    print("Authentication failed")
    exit(1)

# Access models
models = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/object")

# Get system parameter
base_url = models.execute_kw(
    db, uid, password,
    "ir.config_parameter", "get_param",
    ["web.base.url"]
)
print(f"Base URL: {base_url}")

# Set system parameter
models.execute_kw(
    db, uid, password,
    "ir.config_parameter", "set_param",
    ["web.base.url", "https://insightpulseai.com"]
)

# Get all system parameters
params = models.execute_kw(
    db, uid, password,
    "ir.config_parameter", "search_read",
    [[]],
    {"fields": ["key", "value"], "limit": 10}
)
for param in params:
    print(f"{param['key']} = {param['value']}")

# Get email server config
email_servers = models.execute_kw(
    db, uid, password,
    "ir.mail_server", "search_read",
    [[]],
    {"fields": ["name", "smtp_host", "smtp_port", "smtp_user"]}
)
for server in email_servers:
    print(f"{server['name']}: {server['smtp_host']}:{server['smtp_port']}")

# Get installed modules
modules = models.execute_kw(
    db, uid, password,
    "ir.module.module", "search_read",
    [[["state", "=", "installed"]]],
    {"fields": ["name", "latest_version"], "limit": 10}
)
print(f"Installed modules: {len(modules)}")

# Get company info
company = models.execute_kw(
    db, uid, password,
    "res.company", "search_read",
    [[]],
    {"fields": ["name", "email", "website", "currency_id"], "limit": 1}
)
if company:
    print(f"Company: {company[0]['name']}")
```

### Method 2: Odoo Shell

Interactive Python shell with Odoo ORM:

```bash
# Start Odoo shell
./odoo-bin shell -d odoo_dev --config=./infra/odoo.conf

# Or with explicit connection
./odoo-bin shell -d odoo_dev \
  --db_host=localhost --db_port=5433 \
  --db_user=odoo_app --db_password=OdooAppDev2026
```

**Inside Shell:**

```python
# Get system parameter
base_url = env["ir.config_parameter"].get_param("web.base.url")
print(base_url)

# Set system parameter
env["ir.config_parameter"].set_param("web.base.url", "https://insightpulseai.com")

# Get all parameters
params = env["ir.config_parameter"].search([])
for p in params:
    print(f"{p.key} = {p.value}")

# Get email servers
servers = env["ir.mail_server"].search([])
for s in servers:
    print(f"{s.name}: {s.smtp_host}:{s.smtp_port}")

# Get company
company = env["res.company"].search([], limit=1)
print(f"Company: {company.name}")

# Get installed modules
modules = env["ir.module.module"].search([("state", "=", "installed")])
print(f"Installed: {len(modules)} modules")

# Get scheduled actions
crons = env["ir.cron"].search([("active", "=", True)])
for c in crons:
    print(f"{c.name}: every {c.interval_number} {c.interval_type}")
```

### Method 3: Direct Database Query

Query PostgreSQL database directly:

```bash
# Connect to database
psql -h localhost -p 5433 -U odoo_app -d odoo_dev

# Or via tunnel
psql "postgresql://odoo_app:OdooAppDev2026@localhost:5433/odoo_dev?sslmode=require"
```

**SQL Queries:**

```sql
-- Get system parameters
SELECT key, value, create_date, write_date
FROM ir_config_parameter
ORDER BY key;

-- Get specific parameter
SELECT value FROM ir_config_parameter WHERE key = 'web.base.url';

-- Get email servers
SELECT id, name, smtp_host, smtp_port, smtp_user, smtp_encryption
FROM ir_mail_server
WHERE active = true
ORDER BY sequence;

-- Get installed modules
SELECT name, state, latest_version, published_version
FROM ir_module_module
WHERE state = 'installed'
ORDER BY name;

-- Get companies
SELECT id, name, email, website, currency_id
FROM res_company;

-- Get users
SELECT id, login, name, email, active
FROM res_users
WHERE active = true
ORDER BY login;

-- Get scheduled actions
SELECT id, name, model, function, interval_number, interval_type, nextcall, active
FROM ir_cron
WHERE active = true
ORDER BY nextcall;
```

---

## Configuration Scripts in Repository

The repository contains ready-to-use scripts for common settings:

| Script | Purpose | Model | Location |
|--------|---------|-------|----------|
| `configure_base_url.py` | Set web.base.url parameter | `ir.config_parameter` | `scripts/` |
| `configure_zoho_smtp.py` | Configure Zoho Mail SMTP | `ir.mail_server` | `scripts/` |
| `configure_gmail_smtp.py` | Configure Gmail SMTP | `ir.mail_server` | `scripts/` |
| `configure_sendgrid_smtp.py` | Configure SendGrid SMTP | `ir.mail_server` | `scripts/` |
| `audit_email_config.py` | Audit email settings | `ir.mail_server` | `scripts/` |
| `verify_smtp.py` | Test SMTP connection | `ir.mail_server` | `scripts/` |

### Usage Examples

**Via Docker Compose:**

```bash
# Configure Zoho SMTP
docker exec -i ipai-odoo-dev odoo shell -d odoo_dev < scripts/configure_zoho_smtp.py

# Verify SMTP configuration
docker exec -i ipai-odoo-dev odoo shell -d odoo_dev < scripts/verify_smtp.py

# Audit email configuration
docker exec -i ipai-odoo-dev odoo shell -d odoo_dev < scripts/audit_email_config.py
```

**Via odoo-bin:**

```bash
# Configure Gmail SMTP
./odoo-bin shell -d odoo_dev --no-http < scripts/configure_gmail_smtp.py

# Set base URL
./odoo-bin shell -d odoo_dev --no-http < scripts/configure_base_url.py
```

### Script Pattern

All configuration scripts follow this pattern:

```python
#!/usr/bin/env python3
"""
Configure [service] in Odoo
Usage: odoo shell -d DATABASE < configure_[service].py
"""

import sys
import os

# 1. Check if running in Odoo shell
if not env:
    print("Error: Must run via 'odoo shell'")
    sys.exit(1)

# 2. Search for existing configuration
existing = env["ir.mail_server"].search([
    ("name", "=", "Zoho Mail")
])

# 3. Prepare configuration values
config = {
    "name": "Zoho Mail",
    "smtp_host": "smtp.zoho.com",
    "smtp_port": 587,
    "smtp_user": os.getenv("ZOHO_SMTP_USER", "business@insightpulseai.com"),
    "smtp_pass": os.getenv("ZOHO_SMTP_PASSWORD"),
    "smtp_encryption": "starttls",
    "smtp_authentication": "login",
    "sequence": 10,
    "active": True,
}

# 4. Create or update
if existing:
    print(f"Updating existing server: {existing.name}")
    existing.write(config)
else:
    print("Creating new server")
    env["ir.mail_server"].create(config)

# 5. Commit changes
env.cr.commit()

print("Configuration complete")
```

---

## Accessing Settings via UI (Live)

If you want to see the settings page in your browser:

### 1. Start Odoo (Docker Compose)

```bash
cd /Users/tbwa/Documents/GitHub/Insightpulseai/odoo

# Start SSH tunnel to database (Terminal 1)
./scripts/ssh-tunnel-db.sh

# Start Odoo container (Terminal 2)
docker compose -f docker-compose.dev.yml up -d odoo

# Wait for health check
curl http://localhost:8069/web/health

# Check container logs
docker compose -f docker-compose.dev.yml logs -f odoo
```

### 2. Login

- **URL**: `http://localhost:8069`
- **Database**: `odoo_dev`
- **Email**: `admin@example.com`
- **Password**: (set during database initialization, check `.env` or initialization logs)

### 3. Access Settings

- **Standard Settings**: `http://localhost:8069/odoo/settings`
- **Debug Mode**: `http://localhost:8069/odoo/settings?debug=1`
- **Activate Debug**: Click your user avatar → Developer Tools → Activate developer mode

### Debug Mode Features

With `?debug=1` enabled:

**Settings Page:**
- ✅ System Parameters (direct editing)
- ✅ Server Actions (create/edit/delete)
- ✅ Automated Actions (create/edit/delete)
- ✅ Scheduled Actions (cron jobs)
- ✅ Database Structure (view models/fields)
- ✅ Custom Fields (create custom fields)
- ✅ View Architecture (inspect view XML)
- ✅ Menu Editor (customize menus)

**Developer Menu (top-right):**
- View Metadata
- Edit View: Form / List / Kanban / etc.
- Manage Views
- Manage Filters
- Edit Action
- Edit Menu Item
- Technical Translation
- Regenerate Assets
- Become Superuser

**Field-Level Tools:**
- Field metadata
- Edit field properties
- Set default values
- Edit domain/context

---

## Common Use Cases

### Set Base URL

```python
# Via Odoo shell
env["ir.config_parameter"].set_param("web.base.url", "https://insightpulseai.com")
env.cr.commit()
```

```bash
# Via script
./odoo-bin shell -d odoo_dev --no-http < scripts/configure_base_url.py
```

### Configure Email Server

```python
# Via Odoo shell
env["ir.mail_server"].create({
    "name": "Zoho Mail",
    "smtp_host": "smtp.zoho.com",
    "smtp_port": 587,
    "smtp_user": "business@insightpulseai.com",
    "smtp_pass": "YOUR_PASSWORD",
    "smtp_encryption": "starttls",
})
env.cr.commit()
```

```bash
# Via script
./odoo-bin shell -d odoo_dev --no-http < scripts/configure_zoho_smtp.py
```

### Create Scheduled Action

```python
# Via Odoo shell
env["ir.cron"].create({
    "name": "Daily Backup",
    "model_id": env.ref("base.model_ir_config_parameter").id,
    "function": "backup_database",
    "interval_number": 1,
    "interval_type": "days",
    "numbercall": -1,  # Unlimited
    "doall": True,
    "nextcall": "2026-02-10 02:00:00",
    "active": True,
})
env.cr.commit()
```

### Create Automated Action

```python
# Via Odoo shell
action = env["ir.actions.server"].create({
    "name": "Send Welcome Email",
    "model_id": env.ref("base.model_res_users").id,
    "state": "email",
    "template_id": env.ref("mail.mail_template_welcome").id,
})

env["base.automation"].create({
    "name": "Welcome New Users",
    "model_id": env.ref("base.model_res_users").id,
    "trigger": "on_create",
    "action_server_id": action.id,
})
env.cr.commit()
```

---

## Security Considerations

### Best Practices

1. **Never expose system parameters publicly**
2. **Use environment variables for sensitive data** (passwords, API keys)
3. **Enable SSL/TLS for SMTP** (use `starttls` or `ssl`)
4. **Restrict admin access** (use specific permission groups)
5. **Audit configuration changes** (track who changed what)
6. **Use strong passwords** (for users and SMTP)
7. **Enable two-factor authentication** (for admin users)
8. **Regular backups** (of database including ir.config_parameter)

### Secrets Management

**❌ Never hardcode secrets:**

```python
# BAD
smtp_pass = "MyPassword123"
```

**✅ Use environment variables:**

```python
# GOOD
import os
smtp_pass = os.getenv("ZOHO_SMTP_PASSWORD")
```

**✅ Use Odoo's secret storage:**

```python
# GOOD
smtp_pass = env["ir.config_parameter"].get_param("mail.smtp.password")
```

---

## Troubleshooting

### Cannot Access Settings Page

**Symptoms:** Redirect to login, "Access Denied" error

**Solutions:**
1. Verify logged in as admin user
2. Check user has "Settings" access rights
3. Check database is correct
4. Clear browser cache/cookies
5. Check Odoo logs for errors

### Settings Not Saving

**Symptoms:** Changes revert after save

**Solutions:**
1. Check database connection
2. Verify user has write permissions
3. Check for automated actions overriding changes
4. Check Odoo logs for constraint violations
5. Verify no cron jobs reverting changes

### Email Configuration Not Working

**Symptoms:** Emails not sending, SMTP errors

**Solutions:**
1. Test SMTP connection: `scripts/verify_smtp.py`
2. Check SMTP credentials (username/password)
3. Verify SMTP port and encryption settings
4. Check firewall rules (allow outbound port 587/465)
5. Check email server logs
6. Verify email address format
7. Test with external SMTP test tool

### Database Connection Issues

**Symptoms:** Cannot access settings via shell

**Solutions:**
1. Verify SSH tunnel is active: `./scripts/ssh-tunnel-db.sh`
2. Check database credentials in `.env`
3. Test database connection: `psql postgresql://...`
4. Check PostgreSQL logs
5. Verify database exists: `\l` in psql

---

## Related Documentation

- [CLAUDE.md](../CLAUDE.md) - Project operating contract
- [ARCHITECTURE.md](./ARCHITECTURE.md) - System architecture
- [DATABASE_SETUP.md](../DATABASE_SETUP.md) - Database configuration
- [INTEGRATIONS.md](./INTEGRATIONS.md) - Integration points
- [TESTING.md](./TESTING.md) - Testing strategies
- [ODOO_SETTINGS_CHEATSHEET.md](./ODOO_SETTINGS_CHEATSHEET.md) - Quick reference

---

## Quick Links

- [Odoo Documentation](https://www.odoo.com/documentation/19.0/)
- [Odoo ORM API](https://www.odoo.com/documentation/19.0/developer/reference/backend/orm.html)
- [Odoo Models Reference](https://www.odoo.com/documentation/19.0/developer/reference/backend/orm.html)
- [Odoo XML-RPC](https://www.odoo.com/documentation/19.0/developer/reference/external_api.html)
