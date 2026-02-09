# OCR & Document Digitization Settings Reference

Complete guide to configuring and managing OCR and document digitization in Odoo 19 CE.

## Overview

The IPAI OCR system provides intelligent document digitization capabilities for receipts, invoices, and vendor bills. The system uses a custom PaddleOCR microservice (hosted at `ocr.insightpulseai.net`) with fallback support for Azure Vision and Google Vision APIs.

**Key Features:**
- **Custom PaddleOCR Microservice**: Self-hosted OCR service optimized for financial documents
- **Multi-Provider Support**: PaddleOCR (primary), Azure Vision, Google Vision (fallback)
- **Email Integration**: Automatic OCR via email attachments
- **Confidence Scoring**: Auto-approval based on confidence thresholds
- **Batch Processing**: Handle multiple documents efficiently
- **Manual Review Queue**: Low-confidence extractions flagged for human review

**Supported Document Types:**
- Receipts (hr.expense)
- Invoices (account.move)
- Vendor Bills (account.move type purchase)

**Access Locations:**
- Expenses: Expenses → Upload Receipt → Auto-OCR
- Documents: Documents → Upload → Auto-OCR
- Email: Send to ocr@insightpulseai.com

---

## Module Status & Dependencies

| Module | Status | Purpose | Dependencies |
|--------|--------|---------|--------------|
| `ipai_expense_ocr` | ✅ **ACTIVE** | Receipt OCR for hr.expense | `hr_expense`, `documents` |
| `ipai_doc_ocr_bridge` | 🆕 **NEW** | Document manager OCR bridge | `documents`, `mail` |
| `ipai_documents_ai` | ❌ **DEPRECATED** | Document classification (old) | - |

**Installation Order:**
1. Base Odoo modules: `documents`, `hr_expense`, `mail`
2. `ipai_expense_ocr` (receipt OCR for expenses)
3. `ipai_doc_ocr_bridge` (document manager integration)

**Install Commands:**

```bash
# Via Odoo Shell
./odoo-bin shell -d odoo_dev <<'EOF'
modules = ['ipai_expense_ocr', 'ipai_doc_ocr_bridge']
for module_name in modules:
    module = env['ir.module.module'].search([('name', '=', module_name)])
    if module and module.state != 'installed':
        module.button_immediate_install()
        print(f"Installed: {module_name}")
EOF

# Via CLI (Docker)
docker exec -it ipai-odoo-dev odoo -d odoo_dev -u ipai_expense_ocr,ipai_doc_ocr_bridge --stop-after-init
```

**Mark Deprecated Module as Not Installable:**

```python
# Mark ipai_documents_ai as deprecated
deprecated = env['ir.module.module'].search([('name', '=', 'ipai_documents_ai')])
if deprecated:
    deprecated.write({'state': 'uninstallable'})
```

---

## Configuration Parameters

### OCR Provider Configuration (ir.config_parameter)

| Parameter Key | Purpose | Example Value | Required |
|---------------|---------|---------------|----------|
| `ocr.provider.default` | Default OCR provider | `paddleocr`\|`azure`\|`google` | Yes |
| `ocr.paddleocr.endpoint` | PaddleOCR microservice URL | `http://ocr.insightpulseai.net/api/v1/ocr` | Yes (primary) |
| `ocr.paddleocr.api_key` | PaddleOCR API key (if auth enabled) | `pk-...` | Optional |
| `ocr.azure.endpoint` | Azure Vision endpoint | `https://<region>.cognitiveservices.azure.com` | If using Azure |
| `ocr.azure.key` | Azure Vision API key | `...` | If using Azure |
| `ocr.google.credentials` | Google Vision credentials JSON | `{...}` | If using Google |
| `ocr.confidence.threshold` | Min confidence for auto-approval | `0.85` (85%) | Yes |
| `ocr.confidence.manual_review` | Confidence threshold for manual review | `0.70` (70%) | Yes |
| `ocr.batch.size` | Max documents per batch | `10` | Yes |
| `ocr.batch.enabled` | Enable batch processing | `True`\|`False` | Yes |
| `ocr.retry.attempts` | Retry attempts on provider failure | `3` | Yes |
| `ocr.retry.backoff` | Backoff multiplier for retries | `2.0` | Yes |
| `ocr.timeout.default` | Request timeout (seconds) | `30` | Yes |
| `ocr.fallback.enabled` | Enable provider fallback | `True`\|`False` | Yes |
| `ocr.fallback.providers` | Fallback provider order | `azure,google` | If fallback enabled |

**Set Configuration:**

```python
# Via Odoo Shell - Configure PaddleOCR (primary)
env['ir.config_parameter'].sudo().set_param('ocr.provider.default', 'paddleocr')
env['ir.config_parameter'].sudo().set_param('ocr.paddleocr.endpoint', 'http://ocr.insightpulseai.net/api/v1/ocr')
env['ir.config_parameter'].sudo().set_param('ocr.confidence.threshold', '0.85')
env['ir.config_parameter'].sudo().set_param('ocr.confidence.manual_review', '0.70')
env['ir.config_parameter'].sudo().set_param('ocr.batch.size', '10')
env['ir.config_parameter'].sudo().set_param('ocr.retry.attempts', '3')
env['ir.config_parameter'].sudo().set_param('ocr.fallback.enabled', 'True')
env['ir.config_parameter'].sudo().set_param('ocr.fallback.providers', 'azure,google')

# Configure Azure Vision (fallback)
env['ir.config_parameter'].sudo().set_param('ocr.azure.endpoint', 'https://eastus.api.cognitive.microsoft.com')
env['ir.config_parameter'].sudo().set_param('ocr.azure.key', 'YOUR_AZURE_KEY')

# Configure Google Vision (fallback)
env['ir.config_parameter'].sudo().set_param('ocr.google.credentials', '{"type": "service_account", ...}')
```

---

## Document Type Configuration

### Receipt OCR (hr.expense)

**Extracted Fields:**

| Field | OCR Key | Validation | Auto-Fill |
|-------|---------|------------|-----------|
| Date | `date` | date <= today | ✅ Yes |
| Vendor | `vendor_name` | - | ✅ Yes |
| Total Amount | `total_amount` | amount > 0 | ✅ Yes |
| Tax Amount | `tax_amount` | tax >= 0 | ✅ Yes |
| Category | `category` | Valid expense category | ⚠️ Suggested |
| Description | `description` | - | ✅ Yes |
| Currency | `currency_code` | Valid ISO code | ✅ Yes |

**Validation Rules:**

```python
# Receipt validation logic (ipai_expense_ocr module)
def validate_receipt_ocr(ocr_result):
    errors = []

    # Required fields
    if not ocr_result.get('total_amount'):
        errors.append('Total amount is required')
    elif float(ocr_result['total_amount']) <= 0:
        errors.append('Total amount must be positive')

    if not ocr_result.get('date'):
        errors.append('Date is required')
    elif ocr_result['date'] > fields.Date.today():
        errors.append('Date cannot be in the future')

    # Confidence check
    if ocr_result.get('confidence', 0) < 0.70:
        errors.append('Confidence too low - manual review required')

    return errors
```

### Invoice OCR (account.move)

**Extracted Fields:**

| Field | OCR Key | Validation | Auto-Fill |
|-------|---------|------------|-----------|
| Invoice Number | `invoice_number` | Unique per vendor | ✅ Yes |
| Invoice Date | `invoice_date` | date <= today | ✅ Yes |
| Due Date | `due_date` | due_date >= invoice_date | ✅ Yes |
| Vendor | `vendor_name` | Vendor must exist | ✅ Yes (match) |
| Total Amount | `amount_total` | amount > 0 | ✅ Yes |
| Tax Amount | `amount_tax` | tax >= 0 | ✅ Yes |
| Untaxed Amount | `amount_untaxed` | untaxed + tax = total | ✅ Yes (calculated) |
| Currency | `currency_code` | Valid ISO code | ✅ Yes |
| Line Items | `invoice_lines[]` | At least 1 line | ⚠️ Suggested |

**Line Item Fields:**

| Field | OCR Key | Validation |
|-------|---------|------------|
| Description | `line.description` | Required |
| Quantity | `line.quantity` | quantity > 0 |
| Unit Price | `line.price_unit` | price_unit > 0 |
| Subtotal | `line.price_subtotal` | qty * unit_price |
| Account | `line.account_id` | Valid GL account |

---

## File Format Support

| Format | Supported | Max Size | Notes |
|--------|-----------|----------|-------|
| **PDF** | ✅ Yes | 20 MB | Multi-page supported, pages extracted individually |
| **PNG** | ✅ Yes | 10 MB | Preferred format for best OCR accuracy |
| **JPEG/JPG** | ✅ Yes | 10 MB | Good quality (300+ DPI) recommended |
| **TIFF** | ✅ Yes | 20 MB | High-res scans, good for invoices |
| **HEIC** | ⚠️ Partial | 10 MB | Auto-converted to JPEG, quality may vary |
| **WebP** | ❌ No | - | Not supported, convert to PNG/JPEG first |
| **GIF** | ❌ No | - | Not supported |
| **BMP** | ⚠️ Partial | 20 MB | Large file size, use PNG instead |

**Resolution Recommendations:**
- **Receipts**: 300+ DPI for best accuracy
- **Invoices**: 400+ DPI for detailed line items
- **Vendor Bills**: 600+ DPI for small text

---

## Access Methods

### Method 1: UI Upload (Expenses App)

**Steps:**
1. Navigate to **Expenses** → **My Expenses**
2. Click **Upload** or **Create** → **Upload Receipt**
3. Select receipt image file (PNG/JPEG/PDF)
4. Wait for OCR processing (2-5 seconds)
5. Review extracted fields:
   - ✅ Green checkmark = High confidence (>85%)
   - ⚠️ Yellow warning = Medium confidence (70-85%) - Review recommended
   - ❌ Red cross = Low confidence (<70%) - Manual entry required
6. Correct any inaccuracies
7. Click **Create Expense**

**UI Indicators:**

```
✅ Date: 2024-02-10           [Confidence: 95%]
✅ Vendor: Starbucks Coffee   [Confidence: 92%]
⚠️ Amount: $15.75             [Confidence: 78%] ← Review suggested
⚠️ Category: Food & Beverage  [Confidence: 72%] ← Review suggested
```

### Method 2: Email Attachment (Automated)

**Setup:**

```python
# Configure email alias for OCR
alias = env['mail.alias'].search([('alias_name', '=', 'ocr')])
if not alias:
    alias = env['mail.alias'].create({
        'alias_name': 'ocr',
        'alias_model_id': env.ref('hr_expense.model_hr_expense').id,
        'alias_user_id': False,  # Auto-assign to sender
        'alias_contact': 'everyone',
        'alias_defaults': "{'ocr_auto_process': True}"
    })

# Configure mail server for incoming mail
fetchmail = env['fetchmail.server'].search([('name', '=', 'OCR Inbox')])
if not fetchmail:
    fetchmail = env['fetchmail.server'].create({
        'name': 'OCR Inbox',
        'type': 'imap',
        'server': 'imap.gmail.com',
        'port': 993,
        'is_ssl': True,
        'user': 'ocr@insightpulseai.com',
        'password': env['ir.config_parameter'].sudo().get_param('mail.ocr.password'),
        'active': True,
        'state': 'draft'
    })
    fetchmail.button_confirm_login()
```

**Usage:**
1. Send email to **ocr@insightpulseai.com**
2. Attach receipt/invoice image
3. Subject line becomes expense description (optional)
4. Email body ignored (optional notes)
5. OCR processes automatically
6. Confirmation email sent to sender with results

**Email Example:**

```
To: ocr@insightpulseai.com
Subject: Lunch meeting with client
Attachment: receipt_20240210.jpg

[Body can be empty or include notes]
```

**Confirmation Email:**

```
Subject: OCR Processing Complete - Expense Created

Your receipt has been processed successfully.

Expense Details:
- Date: 2024-02-10
- Vendor: Restaurant ABC
- Amount: $45.50
- Category: Meals & Entertainment
- Confidence: 89%

Expense ID: EXP/2024/0123
View: http://erp.insightpulseai.net/web#id=123&model=hr.expense

Please review and submit for approval.
```

### Method 3: Programmatic API

**Trigger OCR on Existing Document:**

```python
# Trigger OCR on uploaded document
doc = env['documents.document'].browse(123)
result = doc.extract_ocr_data()

print(f"OCR Result: {result['success']}")
print(f"Confidence: {result['confidence']:.2%}")
print(f"Extracted Data: {result['data']}")

# Create expense from OCR result
if result['success'] and result['confidence'] >= 0.85:
    expense = env['hr.expense'].create({
        'name': result['data']['description'],
        'total_amount': result['data']['total_amount'],
        'date': result['data']['date'],
        'employee_id': env.user.employee_id.id,
        'product_id': env.ref('hr_expense.product_product_no_cost').id,
        'ocr_confidence': result['confidence'],
        'ocr_data': result['data']
    })
    print(f"Expense created: {expense.name}")
else:
    print("Manual review required")
```

**Batch OCR Processing:**

```python
# Find all documents without OCR
pending_docs = env['documents.document'].search([
    ('ocr_processed', '=', False),
    ('mimetype', 'in', ['image/png', 'image/jpeg', 'application/pdf'])
])

print(f"Processing {len(pending_docs)} documents...")

for doc in pending_docs:
    try:
        result = doc.extract_ocr_data()
        if result['success']:
            print(f"✅ {doc.name}: {result['confidence']:.0%} confidence")
        else:
            print(f"❌ {doc.name}: Failed - {result['error']}")
    except Exception as e:
        print(f"❌ {doc.name}: Error - {str(e)}")

    env.cr.commit()  # Commit after each to avoid long transactions
```

### Method 4: Batch Processing (CLI)

**Process Pending OCR Jobs:**

```bash
# Process all pending OCR jobs
./odoo-bin shell -d odoo_dev <<'EOF'
pending = env['ocr.job'].search([('state', '=', 'pending')], limit=50)
print(f"Processing {len(pending)} OCR jobs...")

for job in pending:
    try:
        job.process()
        print(f"✅ Job {job.id}: {job.confidence:.0%} confidence")
    except Exception as e:
        print(f"❌ Job {job.id}: {str(e)}")
        job.write({'state': 'failed', 'error': str(e)})

    env.cr.commit()
EOF

# Schedule via cron (daily at 2 AM)
cron = env['ir.cron'].create({
    'name': 'OCR Batch Processing',
    'model_id': env.ref('base.model_ocr_job').id,
    'state': 'code',
    'code': '''
pending = env['ocr.job'].search([('state', '=', 'pending')], limit=100)
for job in pending:
    job.process()
    env.cr.commit()
''',
    'interval_number': 1,
    'interval_type': 'days',
    'numbercall': -1,
    'active': True
})
```

---

## Common Operations

### Test OCR Provider

**Test PaddleOCR Microservice:**

```bash
# Test health endpoint
curl http://ocr.insightpulseai.net/health

# Test OCR endpoint with sample receipt
curl -X POST http://ocr.insightpulseai.net/api/v1/ocr \
  -H "Content-Type: multipart/form-data" \
  -F "file=@receipt_sample.jpg" \
  -F "document_type=receipt"

# Expected response:
{
  "success": true,
  "confidence": 0.92,
  "data": {
    "date": "2024-02-10",
    "vendor_name": "Starbucks",
    "total_amount": "15.75",
    "tax_amount": "1.26",
    "currency_code": "USD"
  },
  "processing_time_ms": 1250
}
```

**Test from Odoo:**

```python
# Test OCR provider programmatically
ocr_service = env['ocr.service']
result = ocr_service.test_provider(provider='paddleocr')

print(f"Provider: {result['provider']}")
print(f"Status: {result['status']}")
print(f"Response Time: {result['response_time_ms']}ms")
print(f"Sample Accuracy: {result['sample_accuracy']:.2%}")
```

### Adjust Confidence Thresholds

```python
# Lower confidence threshold for manual review (more permissive)
env['ir.config_parameter'].sudo().set_param('ocr.confidence.threshold', '0.75')
env['ir.config_parameter'].sudo().set_param('ocr.confidence.manual_review', '0.60')

# Find and reprocess low-confidence records
low_conf = env['hr.expense'].search([
    ('ocr_confidence', '<', 0.85),
    ('ocr_confidence', '>', 0.70),
    ('state', '=', 'draft')
])

print(f"Found {len(low_conf)} expenses with medium confidence")
for expense in low_conf:
    expense.manual_review_required = True
    print(f"Flagged for review: {expense.name} ({expense.ocr_confidence:.0%})")
```

### Monitor OCR Accuracy

```python
# Get OCR accuracy stats
expenses = env['hr.expense'].search([
    ('create_date', '>=', '2024-01-01'),
    ('ocr_confidence', '>', 0)
])

if expenses:
    # Calculate average confidence
    avg_confidence = sum(e.ocr_confidence for e in expenses) / len(expenses)
    print(f"Average OCR Confidence: {avg_confidence:.2%}")

    # Confidence distribution
    high_conf = expenses.filtered(lambda e: e.ocr_confidence >= 0.85)
    medium_conf = expenses.filtered(lambda e: 0.70 <= e.ocr_confidence < 0.85)
    low_conf = expenses.filtered(lambda e: e.ocr_confidence < 0.70)

    print(f"\nConfidence Distribution:")
    print(f"  High (≥85%):   {len(high_conf)} ({len(high_conf)/len(expenses)*100:.1f}%)")
    print(f"  Medium (70-85%): {len(medium_conf)} ({len(medium_conf)/len(expenses)*100:.1f}%)")
    print(f"  Low (<70%):    {len(low_conf)} ({len(low_conf)/len(expenses)*100:.1f}%)")

    # Manual correction rate
    corrected = expenses.filtered(lambda e: e.ocr_corrected)
    correction_rate = len(corrected) / len(expenses)
    print(f"\nManual Correction Rate: {correction_rate:.1%}")

    # Provider success rate
    provider_stats = {}
    for expense in expenses:
        provider = expense.ocr_provider or 'unknown'
        if provider not in provider_stats:
            provider_stats[provider] = {'total': 0, 'high_conf': 0}
        provider_stats[provider]['total'] += 1
        if expense.ocr_confidence >= 0.85:
            provider_stats[provider]['high_conf'] += 1

    print(f"\nProvider Statistics:")
    for provider, stats in provider_stats.items():
        success_rate = stats['high_conf'] / stats['total'] if stats['total'] > 0 else 0
        print(f"  {provider}: {success_rate:.1%} high confidence ({stats['total']} total)")
```

### Switch OCR Provider

```python
# Switch from PaddleOCR to Azure Vision
env['ir.config_parameter'].sudo().set_param('ocr.provider.default', 'azure')

# Test new provider
ocr_service = env['ocr.service']
result = ocr_service.test_provider(provider='azure')
if result['status'] == 'ok':
    print("✅ Azure Vision provider configured successfully")
else:
    print(f"❌ Azure Vision provider test failed: {result['error']}")
    # Rollback to PaddleOCR
    env['ir.config_parameter'].sudo().set_param('ocr.provider.default', 'paddleocr')
```

---

## Troubleshooting

### OCR Not Triggering

**Symptoms:** Documents uploaded but OCR doesn't process

**Diagnosis:**

```bash
# 1. Check PaddleOCR microservice health
curl http://ocr.insightpulseai.net/health

# 2. Check Odoo module installed
./odoo-bin shell -d odoo_dev <<'EOF'
module = env['ir.module.module'].search([
    ('name', '=', 'ipai_expense_ocr'),
    ('state', '=', 'installed')
])
print(f"Module installed: {bool(module)}")
EOF

# 3. Check configuration
./odoo-bin shell -d odoo_dev <<'EOF'
endpoint = env['ir.config_parameter'].sudo().get_param('ocr.paddleocr.endpoint')
print(f"OCR Endpoint: {endpoint}")
print(f"Provider: {env['ir.config_parameter'].sudo().get_param('ocr.provider.default')}")
EOF

# 4. Check file format
file receipt.jpg
# Should show: JPEG image data, ...

# 5. Check logs
tail -f /var/log/odoo/odoo.log | grep OCR
```

**Solutions:**
1. Verify PaddleOCR microservice is running and accessible
2. Check module installed and up-to-date: `odoo-bin -u ipai_expense_ocr`
3. Verify `ocr.paddleocr.endpoint` configuration parameter
4. Ensure file format is supported (PNG/JPEG/PDF only)
5. Check file size is within limits (10-20 MB)
6. Review Odoo logs for OCR errors

### Low OCR Accuracy

**Symptoms:** Frequent manual corrections needed, low confidence scores

**Diagnosis:**

```python
# 1. Check image quality
doc = env['documents.document'].browse(123)
print(f"File size: {doc.file_size} bytes")
print(f"MIME type: {doc.mimetype}")

# If image, check resolution
import base64
from PIL import Image
from io import BytesIO

image_data = base64.b64decode(doc.datas)
image = Image.open(BytesIO(image_data))
print(f"Resolution: {image.size[0]}x{image.size[1]} pixels")
print(f"DPI: {image.info.get('dpi', 'unknown')}")

# 2. Review recent low-confidence extractions
low_conf = env['hr.expense'].search([
    ('ocr_confidence', '<', 0.70)
], limit=10, order='create_date DESC')

for expense in low_conf:
    print(f"{expense.name}: {expense.ocr_confidence:.0%} - {expense.ocr_error or 'No error'}")
```

**Solutions:**
1. **Improve Image Quality**:
   - Use 300+ DPI for scans
   - Ensure good lighting for photos
   - Avoid blur and shadows
   - Use PNG format for best quality

2. **Switch Provider**:
   ```python
   # Try Azure Vision for better accuracy
   env['ir.config_parameter'].sudo().set_param('ocr.provider.default', 'azure')
   ```

3. **Adjust Preprocessing**:
   ```python
   # Enable image preprocessing (if available)
   env['ir.config_parameter'].sudo().set_param('ocr.preprocessing.enabled', 'True')
   env['ir.config_parameter'].sudo().set_param('ocr.preprocessing.enhance_contrast', 'True')
   env['ir.config_parameter'].sudo().set_param('ocr.preprocessing.denoise', 'True')
   ```

4. **Train Custom Models** (Advanced):
   - Collect sample receipts/invoices
   - Train PaddleOCR custom model for specific vendors/formats
   - Deploy to microservice
   - Update endpoint configuration

### Email Routing Not Working

**Symptoms:** Emails to ocr@insightpulseai.com don't create expenses

**Diagnosis:**

```python
# 1. Check email alias configured
alias = env['mail.alias'].search([('alias_name', '=', 'ocr')])
print(f"Alias found: {bool(alias)}")
if alias:
    print(f"Alias model: {alias.alias_model_id.model}")
    print(f"Alias active: {alias.active}")

# 2. Check mail server settings
mail_servers = env['ir.mail_server'].search([('active', '=', True)])
print(f"Mail servers configured: {len(mail_servers)}")
for server in mail_servers:
    print(f"  - {server.name}: {server.smtp_host}")

# 3. Check fetchmail configuration
fetchmail = env['fetchmail.server'].search([('active', '=', True)])
print(f"Fetchmail servers: {len(fetchmail)}")
for server in fetchmail:
    print(f"  - {server.name}: {server.server} (port {server.port})")
    print(f"    State: {server.state}")

# 4. Test fetchmail
fetchmail = env['fetchmail.server'].search([('name', '=', 'OCR Inbox')], limit=1)
if fetchmail:
    fetchmail.fetch_mail()
    print("Fetchmail test triggered")
```

**Solutions:**
1. **Configure Email Alias**:
   ```python
   env['mail.alias'].create({
       'alias_name': 'ocr',
       'alias_model_id': env.ref('hr_expense.model_hr_expense').id,
       'alias_user_id': False,
       'alias_contact': 'everyone',
       'active': True
   })
   ```

2. **Configure Fetchmail**:
   ```python
   env['fetchmail.server'].create({
       'name': 'OCR Inbox',
       'type': 'imap',
       'server': 'imap.gmail.com',
       'port': 993,
       'is_ssl': True,
       'user': 'ocr@insightpulseai.com',
       'password': 'YOUR_APP_PASSWORD',
       'active': True
   })
   ```

3. **Check DNS/MX Records** (via Cloudflare):
   - MX record points to correct mail server
   - SPF/DKIM/DMARC configured for domain

4. **Test Email Flow**:
   ```bash
   # Send test email
   echo "Test OCR email" | mail -s "Test Receipt" -a receipt.jpg ocr@insightpulseai.com

   # Check Odoo logs
   tail -f /var/log/odoo/odoo.log | grep -E "(fetchmail|mail.alias|OCR)"
   ```

### Provider Timeout/Failure

**Symptoms:** OCR requests timing out or failing

**Diagnosis:**

```bash
# 1. Test PaddleOCR microservice directly
time curl -X POST http://ocr.insightpulseai.net/api/v1/ocr \
  -F "file=@receipt.jpg" \
  -w "\nTime: %{time_total}s\n"

# 2. Check firewall/network
ping ocr.insightpulseai.net
traceroute ocr.insightpulseai.net

# 3. Check Odoo timeout settings
./odoo-bin shell -d odoo_dev <<'EOF'
timeout = env['ir.config_parameter'].sudo().get_param('ocr.timeout.default')
print(f"OCR Timeout: {timeout}s")
EOF

# 4. Check provider fallback
./odoo-bin shell -d odoo_dev <<'EOF'
fallback = env['ir.config_parameter'].sudo().get_param('ocr.fallback.enabled')
providers = env['ir.config_parameter'].sudo().get_param('ocr.fallback.providers')
print(f"Fallback enabled: {fallback}")
print(f"Fallback providers: {providers}")
EOF
```

**Solutions:**
1. **Increase Timeout**:
   ```python
   env['ir.config_parameter'].sudo().set_param('ocr.timeout.default', '60')
   ```

2. **Enable Fallback**:
   ```python
   env['ir.config_parameter'].sudo().set_param('ocr.fallback.enabled', 'True')
   env['ir.config_parameter'].sudo().set_param('ocr.fallback.providers', 'azure,google')
   ```

3. **Check Microservice Logs** (if self-hosted):
   ```bash
   # SSH to OCR microservice server
   ssh root@ocr.insightpulseai.net

   # Check service status
   systemctl status paddleocr-service

   # Check logs
   journalctl -u paddleocr-service -f
   ```

4. **Scale Microservice** (if high load):
   - Increase microservice workers/replicas
   - Add load balancer if needed
   - Implement request queuing

---

## Performance Optimization

### Enable OCR Caching

```python
# Enable OCR result caching for duplicate documents
env['ir.config_parameter'].sudo().set_param('ocr.cache.enabled', 'True')
env['ir.config_parameter'].sudo().set_param('ocr.cache.ttl', '86400')  # 24 hours

# Clear OCR cache
env['ocr.cache'].search([]).unlink()
```

### Batch Processing Configuration

```python
# Optimize batch processing
env['ir.config_parameter'].sudo().set_param('ocr.batch.enabled', 'True')
env['ir.config_parameter'].sudo().set_param('ocr.batch.size', '20')
env['ir.config_parameter'].sudo().set_param('ocr.batch.interval', '300')  # 5 minutes

# Manual batch trigger
env['ocr.service'].process_batch()
```

### Reduce Processing Time

```python
# Skip OCR for high-quality structured invoices
env['ir.config_parameter'].sudo().set_param('ocr.structured.skip', 'True')

# Enable parallel processing (if multiple workers available)
env['ir.config_parameter'].sudo().set_param('ocr.parallel.enabled', 'True')
env['ir.config_parameter'].sudo().set_param('ocr.parallel.workers', '4')
```

---

## Security & Compliance

### Data Privacy

```python
# Enable PII redaction in OCR logs
env['ir.config_parameter'].sudo().set_param('ocr.privacy.redact_pii', 'True')

# Disable external provider (use PaddleOCR microservice only)
env['ir.config_parameter'].sudo().set_param('ocr.provider.default', 'paddleocr')
env['ir.config_parameter'].sudo().set_param('ocr.fallback.enabled', 'False')

# Enable data retention policy
env['ir.config_parameter'].sudo().set_param('ocr.retention.days', '90')
```

### Audit Logging

```python
# Enable comprehensive OCR audit logging
env['ir.config_parameter'].sudo().set_param('ocr.audit.enabled', 'True')
env['ir.config_parameter'].sudo().set_param('ocr.audit.log_images', 'False')  # Don't log actual images
env['ir.config_parameter'].sudo().set_param('ocr.audit.log_results', 'True')

# Query audit logs
audit_logs = env['ocr.audit.log'].search([
    ('create_date', '>=', '2024-01-01')
])
for log in audit_logs:
    print(f"{log.create_date}: {log.document_type} - {log.provider} - {log.confidence:.0%}")
```

---

## Further Reading

**Architecture Documentation:**
- `/docs/architecture/OCR_PIPELINE.md` - OCR pipeline flow
- `/docs/architecture/OCR_ROUTING_MATRIX.md` - OCR routing logic

**Module Documentation:**
- `/addons/ipai/ipai_expense_ocr/README.md` - Expense OCR module
- `/addons/ipai/ipai_doc_ocr_bridge/README.md` - Document OCR bridge

**Related Settings:**
- `/docs/ai/ODOO_SETTINGS_REFERENCE.md` - General settings
- `/docs/ai/ODOO_SETTINGS_CHEATSHEET.md` - Quick commands
- `/docs/ai/ODOO_SETTINGS_AI_AGENTS.md` - AI agents settings

**PaddleOCR Microservice:**
- Service endpoint: `http://ocr.insightpulseai.net`
- Health check: `http://ocr.insightpulseai.net/health`
- API docs: `http://ocr.insightpulseai.net/docs`

---

**Last Updated:** 2024-02-10
**Odoo Version:** 19.0 CE
**IPAI OCR System Version:** 1.0
