# Expenses OCR Operational Runbook

**Purpose:** Operate and maintain the expense receipt OCR integration.

**Module:** `ipai_expense_ocr`
**OCR Service:** `188.166.237.231:8000` (or internal network)

---

## 1. Overview

The Expense OCR integration provides:
- Receipt scanning from expense forms
- Auto-extraction of merchant, date, amount, tax
- Duplicate receipt detection (SHA256 hash)
- Queue-based async processing
- Confidence-based review workflow

### Extracted Fields

| Field | Description | Confidence Threshold |
|-------|-------------|---------------------|
| `merchant_name` | Store/vendor name | 0.70 |
| `receipt_date` | Transaction date | 0.85 |
| `total_amount` | Total paid | 0.85 |
| `currency` | Currency code | 0.80 |
| `tax_amount` | Tax/VAT amount | 0.75 |
| `payment_method` | Cash/Card/etc | 0.60 |

---

## 2. Configuration

### Environment Variables

```bash
# OCR Service
OCR_BASE_URL=http://ocr:8000
OCR_TIMEOUT_SECONDS=60
OCR_MAX_MB=25

# Expense OCR specific
EXPENSE_OCR_DUPLICATE_DAYS=90
EXPENSE_OCR_AUTO_APPLY=false
EXPENSE_OCR_REVIEW_THRESHOLD=0.70
```

### System Parameters

Set in Odoo (Settings → Technical → System Parameters):

| Key | Default | Description |
|-----|---------|-------------|
| `ipai_expense_ocr.duplicate_days` | 90 | Days to check for duplicate receipts |
| `ipai_expense_ocr.review_threshold` | 0.70 | Confidence threshold for auto-apply |
| `ipai_expense_ocr.auto_apply` | false | Auto-apply high-confidence results |

---

## 3. Workflow States

```
                    ┌──────────┐
                    │  queued  │
                    └────┬─────┘
                         │
                         ▼
                    ┌──────────┐
                    │processing│
                    └────┬─────┘
                         │
           ┌─────────────┼─────────────┐
           ▼             ▼             ▼
    ┌──────────┐  ┌────────────┐  ┌────────┐
    │extracted │  │needs_review│  │ failed │
    └────┬─────┘  └─────┬──────┘  └────────┘
         │              │
         └──────┬───────┘
                ▼
           ┌─────────┐
           │ applied │
           └─────────┘
```

### State Descriptions

| State | Description | Action Required |
|-------|-------------|-----------------|
| `queued` | Waiting for processing | None (auto-processed) |
| `processing` | Being extracted | None (wait) |
| `extracted` | Extraction complete | Review/Apply |
| `needs_review` | Low confidence | Manual review |
| `applied` | Fields applied | None (complete) |
| `failed` | Extraction failed | Retry or manual entry |

---

## 4. Duplicate Detection

### How It Works

1. When a receipt is uploaded, SHA256 hash is computed
2. Hash is compared against recent expenses (configurable days)
3. If match found, expense is flagged as potential duplicate

### Configuration

```python
# System parameter
EXPENSE_OCR_DUPLICATE_DAYS = 90  # Check last 90 days
```

### Handling Duplicates

- Warning displayed on expense form
- User can override and submit anyway
- Audit trail maintained

---

## 5. Verification Commands

### Check OCR Service

```bash
# Health check
curl -sS http://188.166.237.231:8000/health

# Test extraction
curl -sS -X POST \
  -F "file=@./sample-receipt.jpg" \
  -F "options={\"doc_type_hint\":\"receipt\"}" \
  http://188.166.237.231:8000/v1/ocr/extract | jq .
```

### Check Queue Status

```python
# From Odoo shell
queued = env['ipai.expense.ocr.result'].search([('state', '=', 'queued')])
print(f"Queued: {len(queued)}")

processing = env['ipai.expense.ocr.result'].search([('state', '=', 'processing')])
print(f"Processing: {len(processing)}")

failed = env['ipai.expense.ocr.result'].search([('state', '=', 'failed')])
print(f"Failed: {len(failed)}")
```

### Force Process Queue

```python
# From Odoo shell (emergency)
queued = env['ipai.expense.ocr.result'].search([('state', '=', 'queued')], limit=10)
for result in queued:
    try:
        result.action_extract()
        env.cr.commit()
    except Exception as e:
        print(f"Failed {result.id}: {e}")
        result.state = 'failed'
        result.error_message = str(e)
        env.cr.commit()
```

---

## 6. Common Issues

### Low Confidence Extractions

**Symptoms:** Fields extracted but confidence < 70%

**Causes:**
- Poor image quality
- Unusual receipt format
- Rotated or skewed image
- Multi-language receipts

**Solutions:**
1. Ask user to re-scan with better quality
2. Manual entry with extracted text as reference
3. Train OCR model on common receipt types

### Failed Extractions

**Symptoms:** State = `failed`, error_message populated

**Common Errors:**

| Error | Cause | Solution |
|-------|-------|----------|
| Timeout | Large file / slow service | Increase timeout or reduce file size |
| Connection refused | OCR service down | Restart OCR service |
| Invalid format | Unsupported file type | Convert to PDF/JPG |
| File too large | Exceeds max size | Compress or split |

### Duplicate False Positives

**Symptoms:** Non-duplicate receipts flagged as duplicates

**Causes:**
- Same receipt template from merchant
- Low-quality images producing similar hashes

**Solutions:**
1. User can override duplicate warning
2. Adjust duplicate detection window
3. Consider content-based similarity instead of hash

---

## 7. Monitoring

### Key Metrics

| Metric | Description | Alert Threshold |
|--------|-------------|-----------------|
| Queue depth | Pending OCR jobs | > 50 |
| Failure rate | % failed extractions | > 10% |
| Average confidence | Mean confidence score | < 0.70 |
| Processing time | Avg extraction duration | > 30s |

### Log Queries

```bash
# Recent failures
docker logs odoo-core 2>&1 | grep "OCR extraction failed"

# Successful extractions
docker logs odoo-core 2>&1 | grep "OCR extraction completed"

# Low confidence warnings
docker logs odoo-core 2>&1 | grep "low confidence"
```

---

## 8. Maintenance

### Clear Failed Jobs

```python
# From Odoo shell
failed = env['ipai.expense.ocr.result'].search([
    ('state', '=', 'failed'),
    ('create_date', '<', '2026-01-01'),
])
print(f"Deleting {len(failed)} old failed results")
failed.unlink()
env.cr.commit()
```

### Reset Stuck Jobs

```python
# From Odoo shell
stuck = env['ipai.expense.ocr.result'].search([
    ('state', '=', 'processing'),
    ('write_date', '<', datetime.now() - timedelta(hours=1)),
])
print(f"Resetting {len(stuck)} stuck jobs")
stuck.write({'state': 'queued'})
env.cr.commit()
```

### Rebuild Duplicate Hashes

```python
# From Odoo shell (if hashes missing)
expenses = env['hr.expense'].search([
    ('receipt_hash', '=', False),
])
for expense in expenses:
    attachments = env['ir.attachment'].search([
        ('res_model', '=', 'hr.expense'),
        ('res_id', '=', expense.id),
    ], limit=1)
    if attachments:
        expense.receipt_hash = expense._compute_receipt_hash(attachments[0])
env.cr.commit()
```

---

## 9. Integration Testing

### End-to-End Test

```python
# Create test expense
expense = env['hr.expense'].create({
    'name': 'Test OCR Expense',
    'employee_id': env.user.employee_id.id,
    'product_id': env.ref('hr_expense.product_product_fixed_cost').id,
})

# Create test attachment
import base64
with open('/path/to/test-receipt.jpg', 'rb') as f:
    content = base64.b64encode(f.read()).decode()

attachment = env['ir.attachment'].create({
    'name': 'test-receipt.jpg',
    'datas': content,
    'res_model': 'hr.expense',
    'res_id': expense.id,
})

# Trigger OCR
expense.action_scan_receipt()

# Wait and check result
import time
time.sleep(10)
expense.refresh()
print(f"OCR State: {expense.ocr_state}")
print(f"Confidence: {expense.ocr_confidence}")
print(f"Merchant: {expense.ocr_result_id.merchant_name}")
```

---

## 10. Checklist

### Deployment

- [ ] OCR service running and healthy
- [ ] Module installed (`ipai_expense_ocr`)
- [ ] Environment variables configured
- [ ] Cron job active (check ir.cron)
- [ ] User groups assigned

### Verification

- [ ] Test expense created
- [ ] Receipt uploaded
- [ ] OCR extraction triggered
- [ ] Fields extracted correctly
- [ ] Apply to expense works
- [ ] Duplicate detection works

### Production

- [ ] Queue depth monitored
- [ ] Failure alerts configured
- [ ] Log rotation enabled
- [ ] Backup includes OCR results

---

*Last updated: 2026-01-08*
