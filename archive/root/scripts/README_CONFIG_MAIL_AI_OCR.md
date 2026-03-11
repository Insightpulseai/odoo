# Odoo Configuration: Mail + AI + OCR (CLI-Only)

**Idempotent, scriptable configuration** for Mail (Zoho SMTP/IMAP), AI agents, and OCR microservices - **no UI required**.

---

## Quick Start

### 1. Export Environment Variables

```bash
# Mail (Zoho)
export ODOO_SMTP_HOST="smtp.zoho.com"
export ODOO_SMTP_PORT="587"
export ODOO_SMTP_USER="business@insightpulseai.com"
export ODOO_SMTP_PASS="your_zoho_app_password"      # ← REQUIRED
export ODOO_SMTP_TLS="true"

export ODOO_IMAP_HOST="imap.zoho.com"
export ODOO_IMAP_PORT="993"
export ODOO_IMAP_USER="$ODOO_SMTP_USER"
export ODOO_IMAP_PASS="$ODOO_SMTP_PASS"
export ODOO_IMAP_SSL="true"

# AI Agents (Supabase Edge Function or direct OpenAI)
export IPAI_AI_ENDPOINT_URL="https://spdtwktxdalcfigzeqrz.supabase.co/functions/v1/docs-ai-ask"
export IPAI_AI_API_KEY="your_supabase_service_role_key"  # ← REQUIRED

# OCR (PaddleOCR or Azure/Google)
export IPAI_OCR_ENDPOINT_URL="http://localhost:8000/ocr"
export IPAI_OCR_API_KEY=""  # Optional for self-hosted
```

### 2. Apply Configuration

```bash
# Run configuration script
./odoo-bin shell -d odoo_dev --addons-path=addons,addons/ipai,oca-parity < scripts/odoo_config_mail_ai_ocr.py
```

### 3. Verify Configuration

```bash
# Check mail servers
./odoo-bin shell -d odoo_dev --addons-path=addons,addons/ipai,oca-parity < scripts/odoo_check_mail.py

# Check AI/OCR parameters
./odoo-bin shell -d odoo_dev --addons-path=addons,addons/ipai,oca-parity < scripts/odoo_check_ai_ocr_params.py
```

### 4. (Optional) Enable IMAP Polling

```bash
./odoo-bin shell -d odoo_dev --addons-path=addons,addons/ipai,oca-parity < scripts/odoo_start_fetchmail.py
```

---

## Configuration Files

| File | Purpose |
|------|---------|
| `odoo_config_mail_ai_ocr.py` | Main configuration script (idempotent) |
| `odoo_check_mail.py` | Verify mail server configuration |
| `odoo_check_ai_ocr_params.py` | Verify AI/OCR parameters |
| `odoo_start_fetchmail.py` | Enable IMAP polling |
| `odoo_rollback_mail_ai_ocr.py` | Rollback configuration |

---

## Environment Variable Reference

### Mail Configuration (Zoho)

| Variable | Default | Required | Notes |
|----------|---------|----------|-------|
| `ODOO_SMTP_HOST` | - | ✅ | smtp.zoho.com or smtppro.zoho.com |
| `ODOO_SMTP_PORT` | 587 | ✅ | Use 587 for STARTTLS |
| `ODOO_SMTP_USER` | - | ✅ | Your email address |
| `ODOO_SMTP_PASS` | - | ✅ | Zoho App Password (not regular password) |
| `ODOO_SMTP_TLS` | true | ⚠️ | Use STARTTLS (true/false) |
| `ODOO_IMAP_HOST` | - | ✅ | imap.zoho.com |
| `ODOO_IMAP_PORT` | 993 | ✅ | Use 993 for SSL |
| `ODOO_IMAP_USER` | - | ✅ | Your email address |
| `ODOO_IMAP_PASS` | - | ✅ | Zoho App Password |
| `ODOO_IMAP_SSL` | true | ⚠️ | Use SSL (true/false) |

### AI Agent Configuration

| Variable | Default | Required | Notes |
|----------|---------|----------|-------|
| `IPAI_AI_ENDPOINT_URL` | - | ✅ | Supabase Edge Function or OpenAI proxy |
| `IPAI_AI_API_KEY` | - | ✅ | Service role key or OpenAI key |

### OCR Configuration

| Variable | Default | Required | Notes |
|----------|---------|----------|-------|
| `IPAI_OCR_ENDPOINT_URL` | - | ✅ | PaddleOCR, Azure, or Google endpoint |
| `IPAI_OCR_API_KEY` | "" | ⚠️ | Optional for self-hosted PaddleOCR |

---

## How It Works

### Configuration Script Logic

```python
# 1. Ensure required modules installed
ensure_modules()  # mail, fetchmail

# 2. Upsert SMTP server
upsert_ir_mail_server()  # Creates or updates ir.mail_server record

# 3. Upsert IMAP fetchmail server
upsert_fetchmail_imap()  # Creates or updates fetchmail.server record

# 4. Apply AI/OCR parameters
apply_agent_params()  # Sets ir.config_parameter values

# 5. Commit transaction
env.cr.commit()
```

### Idempotency

- **SMTP**: Search by `(smtp_host, smtp_user)` → update if exists, create if not
- **IMAP**: Search by `(server, user)` → update if exists, create if not
- **Parameters**: Always set/update values (idempotent by design)

### Database Records Created

**ir.mail_server:**
```python
{
  "name": "Zoho SMTP (business@insightpulseai.com)",
  "smtp_host": "smtp.zoho.com",
  "smtp_port": 587,
  "smtp_user": "business@insightpulseai.com",
  "smtp_pass": "***",
  "smtp_encryption": "starttls",
  "sequence": 10,
  "active": True
}
```

**fetchmail.server:**
```python
{
  "name": "Zoho IMAP (business@insightpulseai.com)",
  "server": "imap.zoho.com",
  "port": 993,
  "type": "imap",
  "is_ssl": True,
  "user": "business@insightpulseai.com",
  "password": "***",
  "state": "draft",
  "active": True
}
```

**ir.config_parameter:**
```
ipai.ai.endpoint_url = https://...
ipai.ai.api_key = ***
ipai.ocr.endpoint_url = http://...
ipai.ocr.api_key = ***
```

---

## Production Deployment

### Deploy to Production Database

```bash
# Set production environment variables
export ODOO_SMTP_HOST="smtppro.zoho.com"  # PRO tier for production
export ODOO_SMTP_USER="noreply@insightpulseai.com"
export ODOO_SMTP_PASS="$ZOHO_PROD_APP_PASSWORD"

export IPAI_AI_ENDPOINT_URL="https://spdtwktxdalcfigzeqrz.supabase.co/functions/v1/docs-ai-ask"
export IPAI_AI_API_KEY="$SUPABASE_SERVICE_ROLE_KEY"

export IPAI_OCR_ENDPOINT_URL="https://ocr.insightpulseai.com/ocr"
export IPAI_OCR_API_KEY="$OCR_PROD_API_KEY"

# Apply to production database
./odoo-bin shell -d odoo --addons-path=addons,addons/ipai,oca-parity < scripts/odoo_config_mail_ai_ocr.py
```

### Verify Production Configuration

```bash
# Check all configurations
./odoo-bin shell -d odoo --addons-path=addons,addons/ipai,oca-parity < scripts/odoo_check_mail.py
./odoo-bin shell -d odoo --addons-path=addons,addons/ipai,oca-parity < scripts/odoo_check_ai_ocr_params.py
```

### Enable Production IMAP Polling

```bash
./odoo-bin shell -d odoo --addons-path=addons,addons/ipai,oca-parity < scripts/odoo_start_fetchmail.py
```

---

## Rollback

### Disable All Services

```bash
./odoo-bin shell -d odoo_dev --addons-path=addons,addons/ipai,oca-parity < scripts/odoo_rollback_mail_ai_ocr.py
```

**What Rollback Does:**
- Sets `active=False` on all `ir.mail_server` records
- Sets `active=False` on all `fetchmail.server` records
- Clears all `ipai.ai.*` and `ipai.ocr.*` parameters

---

## Testing

### Test SMTP (Send Email)

```bash
cat > scripts/test_smtp.py <<'EOF'
env['mail.mail'].create({
    'subject': 'Test Email from Odoo',
    'email_to': 'test@example.com',
    'body_html': '<p>This is a test email sent via configured SMTP</p>'
}).send()
env.cr.commit()
print("OK: Test email queued for sending")
EOF

./odoo-bin shell -d odoo_dev --addons-path=addons,addons/ipai,oca-parity < scripts/test_smtp.py
```

### Test IMAP (Check for New Mail)

```bash
cat > scripts/test_imap.py <<'EOF'
Fetch = env["fetchmail.server"].sudo()
servers = Fetch.search([("active","=",True)])
for s in servers:
    s.fetch_mail()
    print(f"OK: Fetched mail from {s.name}")
env.cr.commit()
EOF

./odoo-bin shell -d odoo_dev --addons-path=addons,addons/ipai,oca-parity < scripts/test_imap.py
```

### Test AI Endpoint

```bash
cat > scripts/test_ai.py <<'EOF'
# Requires ipai_ai_platform module installed
if 'ai.client' in env:
    result = env['ai.client'].ask_question("What is Odoo?")
    print(f"AI Answer: {result.get('answer', 'No answer')[:200]}...")
    print(f"Confidence: {result.get('confidence', 0)}")
else:
    print("WARNING: ipai_ai_platform module not installed")
EOF

./odoo-bin shell -d odoo_dev --addons-path=addons,addons/ipai,oca-parity < scripts/test_ai.py
```

---

## Troubleshooting

### "Missing required env var"

**Problem:** Script exits with environment variable error

**Solution:**
```bash
# Check what's missing
echo "SMTP_USER: ${ODOO_SMTP_USER:-NOT SET}"
echo "SMTP_PASS: ${ODOO_SMTP_PASS:-NOT SET}"
echo "AI_KEY: ${IPAI_AI_API_KEY:-NOT SET}"

# Set missing variables
export ODOO_SMTP_PASS="your_password"
```

### "Module not found: fetchmail"

**Problem:** fetchmail module not installed

**Solution:**
```bash
# Install fetchmail module first
./odoo-bin -d odoo_dev -i fetchmail --stop-after-init

# Then re-run configuration
./odoo-bin shell -d odoo_dev < scripts/odoo_config_mail_ai_ocr.py
```

### SMTP Authentication Failed

**Problem:** Cannot send emails

**Solution:**
```bash
# 1. Generate Zoho App Password (not regular password)
# Go to: https://accounts.zoho.com/home#security/apppasswords

# 2. Use correct SMTP host
export ODOO_SMTP_HOST="smtppro.zoho.com"  # For paid accounts
# or
export ODOO_SMTP_HOST="smtp.zoho.com"  # For free accounts

# 3. Verify credentials
curl -v --url 'smtp://smtp.zoho.com:587' --ssl-reqd \
  --mail-from 'business@insightpulseai.com' \
  --mail-rcpt 'test@example.com' \
  --user 'business@insightpulseai.com:your_app_password'
```

### IMAP Connection Failed

**Problem:** Cannot fetch emails

**Solution:**
```bash
# 1. Verify IMAP settings
export ODOO_IMAP_HOST="imap.zoho.com"
export ODOO_IMAP_PORT="993"
export ODOO_IMAP_SSL="true"

# 2. Test IMAP connection
openssl s_client -connect imap.zoho.com:993 -crlf
# Enter: a LOGIN business@insightpulseai.com your_app_password
```

### AI Endpoint Not Responding

**Problem:** AI queries fail

**Solution:**
```bash
# Test endpoint directly
curl -X POST "$IPAI_AI_ENDPOINT_URL" \
  -H "Authorization: Bearer $IPAI_AI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"question": "Test question"}'

# Check parameter in Odoo
./odoo-bin shell -d odoo_dev < scripts/odoo_check_ai_ocr_params.py
```

---

## Advanced Configuration

### Multiple SMTP Servers

```bash
# Configure fallback SMTP server
export ODOO_SMTP_HOST="smtp.gmail.com"
export ODOO_SMTP_PORT="587"
export ODOO_SMTP_USER="backup@insightpulseai.com"
export ODOO_SMTP_PASS="backup_password"

# Run configuration again (creates second server)
./odoo-bin shell -d odoo_dev < scripts/odoo_config_mail_ai_ocr.py
```

### Custom AI/OCR Parameters

```python
# Modify odoo_config_mail_ai_ocr.py to add custom parameters:

def apply_agent_params():
  upsert_param("ipai.ai.endpoint_url", AI_ENDPOINT)
  upsert_param("ipai.ai.api_key", AI_API_KEY)
  upsert_param("ipai.ai.model", "gpt-4")  # Custom parameter
  upsert_param("ipai.ai.temperature", "0.7")  # Custom parameter

  upsert_param("ipai.ocr.endpoint_url", OCR_ENDPOINT)
  upsert_param("ipai.ocr.api_key", OCR_API_KEY or "")
  upsert_param("ipai.ocr.language", "eng+spa")  # Custom parameter
```

---

## Security Best Practices

### 1. Never Commit Secrets

```bash
# Add to .gitignore
echo "scripts/.env.local" >> .gitignore
echo "**/*_secrets.sh" >> .gitignore
```

### 2. Use Environment Files

```bash
# Create .env.local (gitignored)
cat > scripts/.env.local <<'EOF'
export ODOO_SMTP_PASS="your_secure_password"
export IPAI_AI_API_KEY="your_api_key"
export IPAI_OCR_API_KEY="your_ocr_key"
EOF

# Source before running
source scripts/.env.local
./odoo-bin shell -d odoo_dev < scripts/odoo_config_mail_ai_ocr.py
```

### 3. Use Secret Managers (Production)

```bash
# Example: AWS Secrets Manager
export ODOO_SMTP_PASS=$(aws secretsmanager get-secret-value --secret-id odoo/smtp/pass --query SecretString --output text)
export IPAI_AI_API_KEY=$(aws secretsmanager get-secret-value --secret-id odoo/ai/key --query SecretString --output text)
```

---

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Configure Odoo Production

on:
  workflow_dispatch:

jobs:
  configure:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Configure Odoo
        env:
          ODOO_SMTP_HOST: smtp.zoho.com
          ODOO_SMTP_USER: ${{ secrets.SMTP_USER }}
          ODOO_SMTP_PASS: ${{ secrets.SMTP_PASS }}
          IPAI_AI_ENDPOINT_URL: ${{ secrets.AI_ENDPOINT }}
          IPAI_AI_API_KEY: ${{ secrets.AI_KEY }}
          IPAI_OCR_ENDPOINT_URL: ${{ secrets.OCR_ENDPOINT }}
        run: |
          ssh production "cd /opt/odoo && \
            export ODOO_SMTP_HOST=$ODOO_SMTP_HOST && \
            export ODOO_SMTP_USER=$ODOO_SMTP_USER && \
            export ODOO_SMTP_PASS=$ODOO_SMTP_PASS && \
            ./odoo-bin shell -d odoo < scripts/odoo_config_mail_ai_ocr.py"
```

---

## References

- **Zoho Mail Setup**: https://www.zoho.com/mail/help/adminconsole/app-passwords.html
- **Supabase Edge Functions**: https://supabase.com/docs/guides/functions
- **PaddleOCR**: https://github.com/PaddlePaddle/PaddleOCR
- **Odoo Shell**: https://www.odoo.com/documentation/19.0/developer/reference/cli.html#shell

---

**Last Updated**: 2026-02-11
**Odoo Version**: 19.0
**Status**: Production Ready ✓
