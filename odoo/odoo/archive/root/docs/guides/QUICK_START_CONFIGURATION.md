# Odoo Quick Start Configuration Guide

Complete setup guide for Mail, AI Agents, and OCR in Odoo 19.

---

## 📧 1. Mail Configuration (Zoho Mail)

### Prerequisites
- Zoho Mail PRO account
- SMTP credentials
- `.env.platform.local` file

### Environment Variables

Add to `.env.platform.local`:

```bash
# Zoho Mail SMTP Configuration
ZOHO_SMTP_HOST=smtppro.zoho.com
ZOHO_SMTP_PORT=587
ZOHO_SMTP_USER=your-email@insightpulseai.com
ZOHO_SMTP_PASS=your_zoho_app_password
ZOHO_SMTP_TLS=true
ZOHO_SMTP_SSL=false

# Mail System Settings
MAIL_DEFAULT_FROM=noreply@insightpulseai.com
MAIL_REPLY_TO=business@insightpulseai.com
MAIL_CATCHALL_DOMAIN=insightpulseai.com
```

### Apply Configuration

```bash
# Apply Zoho Mail configuration
./scripts/odoo_configure_mail.sh

# Verify configuration
./scripts/odoo_configure_mail.sh --verify-only
```

### Manual Configuration (via Odoo UI)

1. Navigate to **Settings → Technical → Email → Outgoing Mail Servers**
2. Click **Create**
3. Fill in:
   - **Name**: Zoho Mail PRO
   - **SMTP Server**: smtppro.zoho.com
   - **SMTP Port**: 587
   - **Connection Security**: STARTTLS
   - **Username**: your-email@insightpulseai.com
   - **Password**: your_zoho_app_password
4. Click **Test Connection**
5. Save

### Verify Mail Setup

```bash
# Send test email via Odoo shell
./scripts/odoo_shell.sh "
env['mail.mail'].create({
    'subject': 'Test Email',
    'email_to': 'test@example.com',
    'body_html': '<p>This is a test email from Odoo</p>'
}).send()
"
```

### Troubleshooting

**Authentication Failed:**
- Generate Zoho App Password: https://accounts.zoho.com/home#security/apppasswords
- Use App Password instead of regular password

**Connection Timeout:**
- Check firewall allows outbound port 587
- Verify SMTP host is `smtppro.zoho.com` (not `smtp.zoho.com`)

---

## 🤖 2. AI Agents Configuration

### Prerequisites
- Supabase project: `spdtwktxdalcfigzeqrz`
- OpenAI API key (for fallback)
- Organization UUID

### Install AI Platform Module

```bash
# Method 1: Via script
./scripts/odoo_install_modules.sh ipai_ai_platform

# Method 2: Via Odoo CLI
./odoo-bin -d odoo_dev -i ipai_ai_platform --stop-after-init

# Method 3: Via UI
# Navigate to Apps → Search "AI Platform" → Install
```

### Configure System Parameters

Navigate to **Settings → Technical → System Parameters** and create these entries:

| Key | Value | Purpose |
|-----|-------|---------|
| `ipai.supabase.url` | `https://spdtwktxdalcfigzeqrz.supabase.co` | Supabase project URL |
| `ipai.supabase.service_role_key` | `sbp_xxx...` (from `~/.zshrc`) | Backend authentication |
| `ipai.org.id` | Your organization UUID | Default org context |
| `ipai.openai.api_key` | `sk-xxx...` | OpenAI fallback key |

### Get Configuration Values

```bash
# Supabase URL (always same for project)
echo "https://spdtwktxdalcfigzeqrz.supabase.co"

# Service role key (from environment)
echo $SUPABASE_SERVICE_ROLE_KEY

# Get Organization UUID (query Supabase)
psql "$POSTGRES_URL" -c "SELECT id, name FROM organizations LIMIT 5;"
```

### Verify AI Configuration

```bash
# Test AI client via Odoo shell
./scripts/odoo_shell.sh "
result = env['ai.client'].ask_question('What is Odoo?')
print('Answer:', result['answer'])
print('Confidence:', result['confidence'])
"

# Health check
./scripts/odoo_shell.sh "
health = env['ai.client'].health_check()
import json
print(json.dumps(health, indent=2))
"
```

### Expected Health Check Output

```json
{
  "configured": true,
  "edge_function": false,
  "openai_fallback": true,
  "org_id": "your-uuid-here",
  "test_result": "Using OpenAI fallback"
}
```

### AI Usage Examples

#### Ask Question from Python Code

```python
# In Odoo Python model
result = self.env['ai.client'].ask_question(
    "How do I configure expense automation?",
    context_filters={'category': 'finance'},
    max_chunks=10
)

# Use result
self.description = result['answer']
```

#### Button Action with AI

```python
# In model method
def action_generate_description(self):
    """Generate description using AI"""
    for record in self:
        prompt = f"Generate a professional description for: {record.name}"
        result = self.env['ai.client'].ask_question(prompt)
        record.write({
            'description': result['answer'],
            'ai_generated': True
        })
    return True
```

### Limits & Billing

**Free Tier:**
- 100 AI questions/month per organization
- 5 context chunks per question
- 30 second timeout

**Pro Tier ($49/month):**
- 5,000 AI questions/month
- 10 context chunks per question
- 60 second timeout

### Troubleshooting

**"AI service unavailable":**
- Check OpenAI API key is valid
- Verify internet connectivity to api.openai.com
- Check OpenAI quota not exceeded

**"No organization configured":**
- Set `ipai.org.id` system parameter
- Verify organization UUID exists in database

**Rate limit errors:**
- Upgrade plan or implement caching
- Batch similar questions together

---

## 📄 3. OCR Configuration

### Available OCR Services

The Odoo setup supports multiple OCR backends:

1. **PaddleOCR-VL** (Default) - Self-hosted, free, multilingual
2. **Azure Document Intelligence** - Cloud service, high accuracy
3. **Google Vision API** - Cloud service, best for photos

### Install OCR Module

```bash
# Install OCR gateway module
./scripts/odoo_install_modules.sh ipai_doc_ocr_bridge

# Or via CLI
./odoo-bin -d odoo_dev -i ipai_doc_ocr_bridge --stop-after-init
```

### Configure PaddleOCR-VL (Recommended)

**Prerequisites:**
- Docker running
- Port 8000 available

**Start PaddleOCR Service:**

```bash
# Pull PaddleOCR-VL Docker image
docker pull paddleocr/paddleocr-vl:900m

# Run OCR service
docker run -d \
  --name paddleocr-vl \
  -p 8000:8000 \
  paddleocr/paddleocr-vl:900m

# Verify service
curl http://localhost:8000/health
```

**Configure in Odoo:**

Navigate to **Settings → Technical → System Parameters**:

| Key | Value |
|-----|-------|
| `ipai.ocr.provider` | `paddleocr` |
| `ipai.ocr.paddleocr.url` | `http://localhost:8000` |
| `ipai.ocr.paddleocr.timeout` | `30` |

### Configure Azure Document Intelligence (Optional)

**Prerequisites:**
- Azure account
- Document Intelligence resource created

**Environment Variables:**

```bash
# Add to .env.platform.local
AZURE_DOCUMENT_INTELLIGENCE_KEY=your_azure_key
AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT=https://your-resource.cognitiveservices.azure.com/
```

**Configure in Odoo:**

| Key | Value |
|-----|-------|
| `ipai.ocr.provider` | `azure` |
| `ipai.ocr.azure.endpoint` | `https://your-resource.cognitiveservices.azure.com/` |
| `ipai.ocr.azure.key` | `your_azure_key` |

### Configure Google Vision API (Optional)

**Prerequisites:**
- Google Cloud account
- Vision API enabled
- Service account JSON key

**Configure in Odoo:**

| Key | Value |
|-----|-------|
| `ipai.ocr.provider` | `google` |
| `ipai.ocr.google.credentials_path` | `/path/to/service-account.json` |

### Test OCR Configuration

```bash
# Test OCR via Odoo shell
./scripts/odoo_shell.sh "
# Create test attachment
import base64
with open('/path/to/test-receipt.jpg', 'rb') as f:
    image_data = base64.b64encode(f.read()).decode()

# Process with OCR
attachment = env['ir.attachment'].create({
    'name': 'test-receipt.jpg',
    'datas': image_data
})

# Trigger OCR processing
result = env['ocr.service'].process_document(attachment)
print('Extracted text:', result.get('text', 'No text found'))
"
```

### OCR Usage in Expense Automation

```python
# In expense model
def action_process_with_ocr(self):
    """Extract data from receipt using OCR"""
    for expense in self:
        if not expense.receipt_attachment_id:
            continue

        # Process with OCR
        ocr_result = self.env['ocr.service'].process_document(
            expense.receipt_attachment_id
        )

        # Extract structured data
        expense.write({
            'total_amount': ocr_result.get('amount'),
            'vendor_name': ocr_result.get('vendor'),
            'expense_date': ocr_result.get('date'),
            'description': ocr_result.get('description')
        })
    return True
```

### Troubleshooting

**PaddleOCR container not starting:**
```bash
# Check Docker logs
docker logs paddleocr-vl

# Restart container
docker restart paddleocr-vl

# Check port availability
lsof -i:8000
```

**OCR service timeout:**
- Increase timeout in system parameter
- Check network connectivity
- Verify service is running: `curl http://localhost:8000/health`

**Poor OCR accuracy:**
- Use higher resolution images (min 300 DPI)
- Ensure good lighting and contrast
- Try different OCR provider (Azure > PaddleOCR for complex layouts)

**Azure quota exceeded:**
- Check Azure portal usage metrics
- Upgrade tier or request quota increase

---

## 🔐 Security Best Practices

### Environment Variables

```bash
# NEVER commit secrets to git
# Add to .gitignore:
.env
.env.local
.env.*.local
*.key
credentials.json
```

### Store Secrets Securely

```bash
# Use environment variables for development
export ODOO_ADMIN_PASSWORD="your-secure-password"
export SUPABASE_SERVICE_ROLE_KEY="sbp_xxx..."
export OPENAI_API_KEY="sk-xxx..."

# Or use .env.platform.local (gitignored)
```

### Rotate Keys Regularly

```bash
# Rotate Zoho app password every 90 days
# Rotate API keys every 180 days
# Update system parameters after rotation
```

---

## 📊 Monitoring & Logs

### Check Mail Logs

```bash
# View sent emails
psql "$POSTGRES_URL" -c "
SELECT id, subject, email_to, state, failure_reason
FROM mail_mail
WHERE create_date > NOW() - INTERVAL '24 hours'
ORDER BY create_date DESC
LIMIT 20;
"
```

### Check AI Usage

```bash
# View AI operations (if cms_artifacts exists)
psql "$POSTGRES_URL" -c "
SELECT
  COUNT(*) AS total_questions,
  DATE(created_at) AS date
FROM cms_artifacts
WHERE artifact_type = 'ai_operation'
GROUP BY DATE(created_at)
ORDER BY date DESC
LIMIT 7;
"
```

### Check OCR Processing

```bash
# View OCR jobs
psql "$POSTGRES_URL" -c "
SELECT
  COUNT(*) AS total_ocr_jobs,
  state,
  AVG(processing_time) AS avg_time_seconds
FROM ocr_job
WHERE create_date > NOW() - INTERVAL '7 days'
GROUP BY state;
"
```

---

## 🚀 Next Steps

After completing configuration:

1. **Test Mail**: Send test emails to verify SMTP works
2. **Test AI**: Ask questions via Odoo shell
3. **Test OCR**: Process sample receipts/invoices
4. **Enable Modules**: Install expense automation, finance modules
5. **Configure Workflows**: Set up approval flows, automations
6. **Monitor Usage**: Check logs daily for errors

---

## 📚 Additional Resources

- **Mail Configuration**: `scripts/odoo_configure_mail.sh`
- **AI Platform Docs**: `docs/platform/ai.md`
- **OCR Gateway**: `docs/modules/ipai_ocr_gateway.md`
- **Environment Template**: `.env.example`
- **Module List**: `docs/modules/*.md`

---

**Last Updated**: 2026-02-11
**Odoo Version**: 19.0
**Status**: Production Ready
