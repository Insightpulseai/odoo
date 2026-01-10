# OCR Service Operations Runbook

## Overview

This runbook covers the operations of the OCR service used by `ipai_expense_ocr` for receipt/document processing.

---

## Prerequisites

- OCR service endpoint configured
- Environment variables set (NOT in repo):
  - `OCR_SERVICE_URL`
  - `OCR_SERVICE_TOKEN`

---

## 1. Supported OCR Backends

### 1.1 Backend Options

| Backend | Use Case | Configuration |
|---------|----------|---------------|
| Custom OCR Service | Self-hosted PaddleOCR-VL | `OCR_SERVICE_URL` |
| OpenAI GPT-4 Vision | Cloud-based, high accuracy | OpenAI API key |
| Google Gemini Vision | Cloud-based alternative | Gemini API key |
| DigitalOcean Model Endpoints | DO-hosted models | DO API token |

### 1.2 Configuration Priority

Odoo checks backends in order:
1. Custom OCR Service (if `OCR_SERVICE_URL` set)
2. OpenAI Vision (if `OPENAI_API_KEY` set)
3. Gemini Vision (if `GEMINI_API_KEY` set)

---

## 2. Custom OCR Service Setup

### 2.1 Service Requirements

The OCR service endpoint must accept:

**Request:**
```http
POST /extract
Content-Type: multipart/form-data
Authorization: Bearer ${OCR_SERVICE_TOKEN}

file: <binary image/pdf>
```

**Response:**
```json
{
  "vendor": "Starbucks",
  "date": "2026-01-08",
  "total": 45.50,
  "tax": 4.50,
  "currency": "USD",
  "line_items": [
    {"description": "Coffee", "amount": 20.00},
    {"description": "Sandwich", "amount": 21.00}
  ],
  "confidence": 0.92,
  "raw_text": "..."
}
```

### 2.2 Health Check

```bash
curl -X GET "${OCR_SERVICE_URL}/health" \
  -H "Authorization: Bearer ${OCR_SERVICE_TOKEN}"
```

Expected: `{"status": "ok"}`

---

## 3. Odoo Configuration

### 3.1 System Parameters

Set via Settings > Technical > Parameters > System Parameters:

| Key | Value |
|-----|-------|
| `ocr.service_url` | `${OCR_SERVICE_URL}` |
| `ocr.service_token` | `${OCR_SERVICE_TOKEN}` |
| `ocr.confidence_threshold` | `0.70` |
| `ocr.auto_process` | `True` |

### 3.2 Module Settings

Configure via Settings > Expenses > OCR Configuration:

1. Enable OCR auto-processing
2. Set confidence threshold (default: 0.70)
3. Configure review queue routing

---

## 4. Processing Flow

### 4.1 Receipt Upload Flow

```
1. User uploads receipt to expense
   ↓
2. `ipai_expense_ocr` detects attachment
   ↓
3. OCR job queued (cron or async)
   ↓
4. OCR service extracts data
   ↓
5. Confidence check:
   - >= 0.70: Auto-populate fields
   - < 0.70: Route to review queue
   ↓
6. Duplicate check (hash comparison)
   ↓
7. Expense fields updated
```

### 4.2 Cron Job

The OCR processor runs via cron:

```xml
<record id="ir_cron_ocr_processor" model="ir.cron">
    <field name="name">OCR: Process Pending Receipts</field>
    <field name="model_id" ref="model_hr_expense"/>
    <field name="state">code</field>
    <field name="code">model._process_ocr_queue()</field>
    <field name="interval_number">5</field>
    <field name="interval_type">minutes</field>
    <field name="active">True</field>
</record>
```

---

## 5. Monitoring

### 5.1 Queue Status

Check pending OCR jobs:

```sql
SELECT
  id, name, state, ocr_state, ocr_confidence
FROM hr_expense
WHERE ocr_state IN ('pending', 'processing')
ORDER BY create_date DESC;
```

### 5.2 Processing Stats

```sql
SELECT
  ocr_state,
  COUNT(*) as count,
  AVG(ocr_confidence) as avg_confidence
FROM hr_expense
WHERE ocr_state IS NOT NULL
GROUP BY ocr_state;
```

### 5.3 Error Logs

```bash
docker compose logs odoo | grep -E "ocr|OCR|expense" | tail -100
```

---

## 6. Troubleshooting

### OCR Service Unreachable

```bash
# Test connectivity
curl -v "${OCR_SERVICE_URL}/health"

# Check DNS
dig +short $(echo ${OCR_SERVICE_URL} | sed 's|https*://||' | cut -d'/' -f1)
```

### Low Confidence Results

Common causes:
- Poor image quality
- Handwritten receipts
- Non-standard receipt formats
- Multiple receipts in one image

Solutions:
1. Request higher resolution images
2. Train model on specific receipt types
3. Lower threshold for specific vendors

### Duplicate Detection Issues

Check hash collision:

```sql
SELECT
  attachment_hash, COUNT(*)
FROM hr_expense
WHERE attachment_hash IS NOT NULL
GROUP BY attachment_hash
HAVING COUNT(*) > 1;
```

### Cron Not Running

```bash
# Check cron status
docker compose exec odoo odoo shell -d odoo <<EOF
cron = env['ir.cron'].search([('name', 'ilike', 'ocr')])
for c in cron:
    print(f"{c.name}: active={c.active}, lastcall={c.lastcall}")
EOF
```

---

## 7. Performance Tuning

### 7.1 Batch Processing

For high volume:
- Process in batches of 10-20
- Use async job queue (Celery/RQ)
- Implement retry with exponential backoff

### 7.2 Caching

Cache OCR results by file hash to avoid re-processing:

```python
# Check cache before calling OCR
cache_key = f"ocr:{file_hash}"
cached = redis.get(cache_key)
if cached:
    return json.loads(cached)
```

---

## 8. Security Notes

- NEVER commit `OCR_SERVICE_TOKEN` to repo
- Use HTTPS for all OCR service calls
- Implement request signing if available
- Log all OCR requests for audit
- Sanitize extracted text before database storage

---

## 9. Verification Checklist

- [ ] OCR service endpoint reachable
- [ ] Health check returns OK
- [ ] System parameters configured
- [ ] Test upload processed successfully
- [ ] Confidence routing works correctly
- [ ] Duplicate detection works
- [ ] Cron job running on schedule

---

*Last updated: 2026-01-08*
