# Odoo Settings Quick Reference

> Fast reference for common Odoo settings operations.
> Last updated: 2026-02-09

## Common System Parameters (`ir.config_parameter`)

| Key | Purpose | Example Value |
|-----|---------|---------------|
| `web.base.url` | Base URL for Odoo | `https://insightpulseai.com` |
| `database.uuid` | Unique DB identifier | `(auto-generated)` |
| `web.session.timeout` | Session timeout (seconds) | `7200` |
| `mail.catchall.domain` | Email catchall domain | `insightpulseai.com` |
| `mail.default.from` | Default sender email | `noreply@insightpulseai.com` |
| `mail.bounce.alias` | Bounce email alias | `bounce@insightpulseai.com` |
| `auth_signup.allow_uninvited` | Allow public signup | `True`/`False` |
| `portal.enable_signup` | Enable portal signup | `True`/`False` |
| `base.module_update` | Module update setting | `all`/`installed` |

---

## Common Models

| Model | Purpose | Key Fields |
|-------|---------|------------|
| `ir.config_parameter` | System parameters | `key`, `value` |
| `res.company` | Company settings | `name`, `email`, `website`, `currency_id` |
| `res.users` | User management | `name`, `login`, `email`, `groups_id` |
| `res.groups` | Permission groups | `name`, `category_id`, `users` |
| `ir.mail_server` | Email servers | `name`, `smtp_host`, `smtp_port`, `smtp_user` |
| `ir.module.module` | Installed modules | `name`, `state`, `latest_version` |
| `ir.cron` | Scheduled actions | `name`, `model_id`, `function`, `interval_type` |
| `base.automation` | Automated actions | `name`, `model_id`, `trigger`, `action_server_id` |
| `ir.actions.server` | Server actions | `name`, `model_id`, `state`, `code` |

---

## Quick Commands

### System Parameters

```python
# Get parameter
value = env["ir.config_parameter"].get_param("web.base.url")

# Set parameter
env["ir.config_parameter"].set_param("web.base.url", "https://insightpulseai.com")
env.cr.commit()

# Delete parameter
env["ir.config_parameter"].search([("key", "=", "old.param")]).unlink()
env.cr.commit()

# List all parameters
params = env["ir.config_parameter"].search([])
for p in params:
    print(f"{p.key} = {p.value}")

# List parameters by pattern
params = env["ir.config_parameter"].search([("key", "like", "mail.%")])
```

### Email Servers

```python
# Get all email servers
servers = env["ir.mail_server"].search([])
for s in servers:
    print(f"{s.name}: {s.smtp_host}:{s.smtp_port}")

# Get specific server
server = env["ir.mail_server"].search([("name", "=", "Zoho Mail")], limit=1)

# Create email server
env["ir.mail_server"].create({
    "name": "Zoho Mail",
    "smtp_host": "smtp.zoho.com",
    "smtp_port": 587,
    "smtp_user": "business@insightpulseai.com",
    "smtp_pass": "YOUR_PASSWORD",
    "smtp_encryption": "starttls",
})
env.cr.commit()

# Update email server
server.write({"smtp_port": 465, "smtp_encryption": "ssl"})
env.cr.commit()

# Test email server
server.test_smtp_connection()
```

### Installed Modules

```python
# Get installed modules
modules = env["ir.module.module"].search([("state", "=", "installed")])
print(f"Installed modules: {len(modules)}")

# Get specific module
module = env["ir.module.module"].search([("name", "=", "sale")], limit=1)

# Install module
module = env["ir.module.module"].search([("name", "=", "crm")], limit=1)
module.button_immediate_install()

# Upgrade module
module = env["ir.module.module"].search([("name", "=", "account")], limit=1)
module.button_immediate_upgrade()

# Uninstall module
module = env["ir.module.module"].search([("name", "=", "website_blog")], limit=1)
module.button_immediate_uninstall()
```

### Companies

```python
# Get current company
company = env.company

# Get all companies
companies = env["res.company"].search([])

# Get specific company
company = env["res.company"].search([("name", "=", "InsightPulse AI")], limit=1)

# Update company
company.write({
    "name": "InsightPulse AI",
    "email": "business@insightpulseai.com",
    "website": "https://insightpulseai.com",
})
env.cr.commit()
```

### Users & Groups

```python
# Get all users
users = env["res.users"].search([("active", "=", True)])

# Get specific user
user = env["res.users"].search([("login", "=", "admin")], limit=1)

# Create user
env["res.users"].create({
    "name": "John Doe",
    "login": "john.doe@example.com",
    "email": "john.doe@example.com",
    "password": "SecurePassword123",
    "groups_id": [(6, 0, [env.ref("base.group_user").id])],
})
env.cr.commit()

# Add user to group
user.groups_id = [(4, env.ref("sales_team.group_sale_manager").id)]
env.cr.commit()

# Get all groups
groups = env["res.groups"].search([])

# Get users in group
group = env.ref("base.group_system")
print(f"Admins: {group.users.mapped('name')}")
```

### Scheduled Actions (Cron)

```python
# Get all cron jobs
crons = env["ir.cron"].search([("active", "=", True)])
for c in crons:
    print(f"{c.name}: every {c.interval_number} {c.interval_type}, next: {c.nextcall}")

# Get specific cron
cron = env["ir.cron"].search([("name", "=", "Mail: Fetchmail Service")], limit=1)

# Create cron job
env["ir.cron"].create({
    "name": "Daily Backup",
    "model_id": env.ref("base.model_ir_config_parameter").id,
    "function": "backup_database",
    "interval_number": 1,
    "interval_type": "days",
    "numbercall": -1,
    "doall": True,
    "nextcall": "2026-02-10 02:00:00",
    "active": True,
})
env.cr.commit()

# Disable cron job
cron.write({"active": False})
env.cr.commit()

# Run cron job immediately
cron.method_direct_trigger()
```

### Automated Actions

```python
# Get all automated actions
automations = env["base.automation"].search([])

# Create automated action
action = env["ir.actions.server"].create({
    "name": "Send Welcome Email",
    "model_id": env.ref("base.model_res_users").id,
    "state": "email",
    "template_id": env.ref("mail.mail_template_user_welcome").id,
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

## XML-RPC Quick Commands

### Connect

```python
import xmlrpc.client

url = "http://localhost:8069"
db = "odoo_dev"
username = "admin"
password = "admin"

common = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common")
uid = common.authenticate(db, username, password, {})

models = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/object")
```

### Execute Commands

```python
# Get parameter
value = models.execute_kw(
    db, uid, password,
    "ir.config_parameter", "get_param",
    ["web.base.url"]
)

# Set parameter
models.execute_kw(
    db, uid, password,
    "ir.config_parameter", "set_param",
    ["web.base.url", "https://insightpulseai.com"]
)

# Search and read
records = models.execute_kw(
    db, uid, password,
    "ir.mail_server", "search_read",
    [[]],
    {"fields": ["name", "smtp_host"], "limit": 5}
)

# Create record
id = models.execute_kw(
    db, uid, password,
    "ir.mail_server", "create",
    [{
        "name": "Zoho Mail",
        "smtp_host": "smtp.zoho.com",
        "smtp_port": 587,
    }]
)

# Update record
models.execute_kw(
    db, uid, password,
    "ir.mail_server", "write",
    [[id], {"smtp_port": 465}]
)

# Delete record
models.execute_kw(
    db, uid, password,
    "ir.mail_server", "unlink",
    [[id]]
)
```

---

## SQL Quick Queries

```sql
-- Get all system parameters
SELECT key, value FROM ir_config_parameter ORDER BY key;

-- Get specific parameter
SELECT value FROM ir_config_parameter WHERE key = 'web.base.url';

-- Update parameter
UPDATE ir_config_parameter SET value = 'https://insightpulseai.com' WHERE key = 'web.base.url';

-- Get email servers
SELECT name, smtp_host, smtp_port FROM ir_mail_server WHERE active = true;

-- Get installed modules
SELECT name, latest_version FROM ir_module_module WHERE state = 'installed' ORDER BY name;

-- Get users
SELECT login, name, email FROM res_users WHERE active = true ORDER BY login;

-- Get companies
SELECT name, email, website FROM res_company;

-- Get cron jobs
SELECT name, nextcall, interval_number, interval_type FROM ir_cron WHERE active = true ORDER BY nextcall;

-- Get automated actions
SELECT name, model, trigger FROM base_automation WHERE active = true;
```

---

## Repository Scripts

### Email Configuration

```bash
# Configure Zoho Mail
./odoo-bin shell -d odoo_dev --no-http < scripts/configure_zoho_smtp.py

# Configure Gmail
./odoo-bin shell -d odoo_dev --no-http < scripts/configure_gmail_smtp.py

# Configure SendGrid
./odoo-bin shell -d odoo_dev --no-http < scripts/configure_sendgrid_smtp.py

# Verify SMTP
./odoo-bin shell -d odoo_dev --no-http < scripts/verify_smtp.py

# Audit email config
./odoo-bin shell -d odoo_dev --no-http < scripts/audit_email_config.py
```

### Base Configuration

```bash
# Set base URL
./odoo-bin shell -d odoo_dev --no-http < scripts/configure_base_url.py
```

---

## Docker Compose Commands

### Start Odoo

```bash
# Start with SSH tunnel
./scripts/ssh-tunnel-db.sh  # Terminal 1

# Start Odoo
docker compose -f docker-compose.dev.yml up -d odoo  # Terminal 2

# Check health
curl http://localhost:8069/web/health

# View logs
docker compose -f docker-compose.dev.yml logs -f odoo
```

### Execute Commands in Container

```bash
# Run configuration script
docker exec -i ipai-odoo-dev odoo shell -d odoo_dev < scripts/configure_zoho_smtp.py

# Interactive shell
docker exec -it ipai-odoo-dev odoo shell -d odoo_dev

# Check installed modules
docker exec ipai-odoo-dev odoo -d odoo_dev --list-installed

# Run tests
docker exec ipai-odoo-dev odoo -d odoo_dev --test-enable --stop-after-init
```

---

## Debug Mode Access

### Enable Debug Mode

**Via URL:**
```
http://localhost:8069/odoo/settings?debug=1
```

**Via UI:**
1. Click user avatar (top-right)
2. Developer Tools → Activate developer mode

### Debug Features

- System Parameters (direct edit)
- Server Actions (create/edit)
- Automated Actions (create/edit)
- Scheduled Actions (view/edit cron)
- Database Structure (inspect models)
- Custom Fields (create fields)
- View Architecture (inspect XML)
- Menu Editor (customize menus)

---

## Common SMTP Configurations

### Zoho Mail

```python
{
    "name": "Zoho Mail",
    "smtp_host": "smtp.zoho.com",
    "smtp_port": 587,
    "smtp_user": "business@insightpulseai.com",
    "smtp_pass": "YOUR_PASSWORD",
    "smtp_encryption": "starttls",
}
```

### Gmail

```python
{
    "name": "Gmail",
    "smtp_host": "smtp.gmail.com",
    "smtp_port": 587,
    "smtp_user": "your-email@gmail.com",
    "smtp_pass": "YOUR_APP_PASSWORD",  # Use App Password, not regular password
    "smtp_encryption": "starttls",
}
```

### SendGrid

```python
{
    "name": "SendGrid",
    "smtp_host": "smtp.sendgrid.net",
    "smtp_port": 587,
    "smtp_user": "apikey",  # Always "apikey"
    "smtp_pass": "YOUR_SENDGRID_API_KEY",
    "smtp_encryption": "starttls",
}
```

---

## Troubleshooting Quick Fixes

### Settings Page Not Loading

```bash
# Check Odoo is running
curl http://localhost:8069/web/health

# Check logs
docker compose -f docker-compose.dev.yml logs odoo

# Restart Odoo
docker compose -f docker-compose.dev.yml restart odoo
```

### Cannot Save Settings

```python
# Check user has admin rights
user = env["res.users"].search([("login", "=", "admin")], limit=1)
admin_group = env.ref("base.group_system")
print(f"Is admin: {admin_group in user.groups_id}")

# Add admin rights if needed
user.groups_id = [(4, admin_group.id)]
env.cr.commit()
```

### Email Not Sending

```bash
# Test SMTP connection
./odoo-bin shell -d odoo_dev --no-http < scripts/verify_smtp.py

# Check email queue
# In Odoo shell:
emails = env["mail.mail"].search([("state", "=", "exception")])
for email in emails:
    print(f"Failed: {email.subject} - {email.failure_reason}")

# Retry failed emails
emails.send()
env.cr.commit()
```

### Database Connection Failed

```bash
# Check SSH tunnel
ps aux | grep "ssh.*5433"

# Start tunnel if not running
./scripts/ssh-tunnel-db.sh

# Test database connection
psql "postgresql://odoo_app:OdooAppDev2026@localhost:5433/odoo_dev?sslmode=require"
```

---

## AI Agents Quick Commands

### List AI Agents

```python
# Get all active agents
agents = env["ai.agent"].search([("active", "=", True)])
for agent in agents:
    print(f"{agent.id}: {agent.name} ({agent.technical_name})")
    print(f"  Model: {agent.model_id.model}, Provider: {agent.provider}")

# Get agents for specific Odoo model
invoice_agents = env["ai.agent"].search([
    ("model_id.model", "=", "account.move"),
    ("active", "=", True)
])
```

### Execute Agent

```python
# Simple agent execution
agent = env["ai.agent"].browse(1)
result = agent.execute_agent(
    prompt="Analyze this invoice",
    context={"invoice_id": 123}
)
print(f"Response: {result['response']}")
print(f"Tokens: {result['usage']['total_tokens']}")

# With conversation history
result = agent.execute_agent(
    prompt="What is the total amount?",
    session_id="session-123"
)
```

### Monitor AI Usage & Cost

```python
# Get usage stats
usage = env["ai.usage"].search([
    ("create_date", ">=", "2024-01-01")
])
total_cost = sum(u.cost for u in usage)
total_tokens = sum(u.total_tokens for u in usage)
print(f"Total Cost: ${total_cost:.2f}")
print(f"Total Tokens: {total_tokens:,}")

# Usage by agent
agent = env["ai.agent"].browse(1)
agent_usage = env["ai.usage"].search([("agent_id", "=", agent.id)])
print(f"{agent.name}: ${sum(u.cost for u in agent_usage):.2f}")

# Usage by provider
openai_usage = env["ai.usage"].search([("provider", "=", "openai")])
claude_usage = env["ai.usage"].search([("provider", "=", "claude")])
print(f"OpenAI: ${sum(u.cost for u in openai_usage):.2f}")
print(f"Claude: ${sum(u.cost for u in claude_usage):.2f}")
```

### Configure AI Provider

```python
# Set OpenAI as default
env["ir.config_parameter"].sudo().set_param("ai.provider.default", "openai")
env["ir.config_parameter"].sudo().set_param("ai.openai.api_key", "sk-proj-...")
env["ir.config_parameter"].sudo().set_param("ai.model.default", "gpt-4o")

# Configure rate limits
env["ir.config_parameter"].sudo().set_param("ai.rate_limit.rpm", "60")
env["ir.config_parameter"].sudo().set_param("ai.rate_limit.tpm", "150000")

# Configure token budget
env["ir.config_parameter"].sudo().set_param("ai.token_budget.default", "10000")
```

---

## OCR Quick Commands

### Test OCR Endpoint

```bash
# Test PaddleOCR microservice health
curl http://ocr.insightpulseai.net/health

# Test OCR with sample receipt
curl -X POST http://ocr.insightpulseai.net/api/v1/ocr \
  -F "file=@receipt.jpg" \
  -F "document_type=receipt"
```

```python
# Test from Odoo
ocr_service = env["ocr.service"]
result = ocr_service.test_provider(provider="paddleocr")
print(f"Status: {result['status']}")
print(f"Response Time: {result['response_time_ms']}ms")
```

### Process OCR Documents

```python
# Trigger OCR on existing document
doc = env["documents.document"].browse(123)
result = doc.extract_ocr_data()
print(f"Confidence: {result['confidence']:.2%}")
print(f"Data: {result['data']}")

# Create expense from OCR result
if result["success"]:
    expense = env["hr.expense"].create({
        "name": result["data"]["description"],
        "total_amount": result["data"]["total_amount"],
        "date": result["data"]["date"],
        "employee_id": env.user.employee_id.id,
        "ocr_confidence": result["confidence"]
    })
```

### Batch OCR Processing

```bash
# Process all pending OCR jobs
./odoo-bin shell -d odoo_dev <<'EOF'
pending = env["ocr.job"].search([("state", "=", "pending")], limit=50)
for job in pending:
    job.process()
    env.cr.commit()
EOF
```

```python
# Find documents without OCR
pending_docs = env["documents.document"].search([
    ("ocr_processed", "=", False),
    ("mimetype", "in", ["image/png", "image/jpeg", "application/pdf"])
])

for doc in pending_docs:
    result = doc.extract_ocr_data()
    print(f"{'✅' if result['success'] else '❌'} {doc.name}")
    env.cr.commit()
```

### Monitor OCR Accuracy

```python
# Get accuracy stats
expenses = env["hr.expense"].search([
    ("create_date", ">=", "2024-01-01"),
    ("ocr_confidence", ">", 0)
])

# Average confidence
avg = sum(e.ocr_confidence for e in expenses) / len(expenses)
print(f"Average Confidence: {avg:.2%}")

# Confidence distribution
high = expenses.filtered(lambda e: e.ocr_confidence >= 0.85)
medium = expenses.filtered(lambda e: 0.70 <= e.ocr_confidence < 0.85)
low = expenses.filtered(lambda e: e.ocr_confidence < 0.70)
print(f"High (≥85%): {len(high)} ({len(high)/len(expenses)*100:.1f}%)")
print(f"Medium (70-85%): {len(medium)} ({len(medium)/len(expenses)*100:.1f}%)")
print(f"Low (<70%): {len(low)} ({len(low)/len(expenses)*100:.1f}%)")

# Manual correction rate
corrected = expenses.filtered(lambda e: e.ocr_corrected)
print(f"Correction Rate: {len(corrected)/len(expenses):.1%}")
```

### Configure OCR Settings

```python
# Configure PaddleOCR (primary)
env["ir.config_parameter"].sudo().set_param("ocr.provider.default", "paddleocr")
env["ir.config_parameter"].sudo().set_param("ocr.paddleocr.endpoint", "http://ocr.insightpulseai.net/api/v1/ocr")

# Configure confidence thresholds
env["ir.config_parameter"].sudo().set_param("ocr.confidence.threshold", "0.85")
env["ir.config_parameter"].sudo().set_param("ocr.confidence.manual_review", "0.70")

# Configure fallback providers
env["ir.config_parameter"].sudo().set_param("ocr.fallback.enabled", "True")
env["ir.config_parameter"].sudo().set_param("ocr.fallback.providers", "azure,google")
```

---

## Related Documentation

- [ODOO_SETTINGS_REFERENCE.md](./ODOO_SETTINGS_REFERENCE.md) - General + Mail settings
- [ODOO_SETTINGS_AI_AGENTS.md](./ODOO_SETTINGS_AI_AGENTS.md) - AI agents settings
- [ODOO_SETTINGS_OCR_DIGITIZATION.md](./ODOO_SETTINGS_OCR_DIGITIZATION.md) - OCR settings
- [CLAUDE.md](../CLAUDE.md) - Project operating contract
- [ARCHITECTURE.md](./ARCHITECTURE.md) - System architecture
- [DATABASE_SETUP.md](../DATABASE_SETUP.md) - Database configuration

---

## Quick Navigation

| Section | Link |
|---------|------|
| System Parameters | [Common Parameters](#common-system-parameters-irconfigparameter) |
| Email Setup | [SMTP Configurations](#common-smtp-configurations) |
| Python Commands | [Quick Commands](#quick-commands) |
| SQL Queries | [SQL Quick Queries](#sql-quick-queries) |
| Docker Commands | [Docker Compose](#docker-compose-commands) |
| Troubleshooting | [Quick Fixes](#troubleshooting-quick-fixes) |
