# Expenses OCR Runbook

## Overview

Operational runbook for the `ipai_expense_ocr` module - covers queue management, cron operations, retry logic, and failure handling.

---

## 1. Module Overview

### 1.1 Features

- Automatic OCR on expense attachment upload
- Extracts: vendor, date, total, tax, currency, line items
- Duplicate detection via file hash
- Confidence-based routing (review queue for < 0.70)
- Cron-based queue processor

### 1.2 States

| State | Description |
|-------|-------------|
| `pending` | Queued for OCR processing |
| `processing` | Currently being processed |
| `done` | Successfully extracted |
| `review` | Low confidence, needs manual review |
| `failed` | OCR failed (after retries) |
| `duplicate` | Duplicate receipt detected |

---

## 2. Queue Management

### 2.1 View Queue Status

```sql
-- Pending queue
SELECT id, name, ocr_state, create_date
FROM hr_expense
WHERE ocr_state = 'pending'
ORDER BY create_date ASC;

-- Processing (stuck?)
SELECT id, name, ocr_state, write_date
FROM hr_expense
WHERE ocr_state = 'processing'
AND write_date < NOW() - INTERVAL '30 minutes';
```

### 2.2 Force Requeue

```python
# Via Odoo shell
expenses = env['hr.expense'].search([('ocr_state', '=', 'failed')])
expenses.write({'ocr_state': 'pending', 'ocr_retry_count': 0})
env.cr.commit()
```

### 2.3 Clear Stuck Processing

```sql
UPDATE hr_expense
SET ocr_state = 'pending', ocr_retry_count = 0
WHERE ocr_state = 'processing'
AND write_date < NOW() - INTERVAL '1 hour';
```

---

## 3. Cron Operations

### 3.1 Cron Configuration

| Field | Value |
|-------|-------|
| Name | OCR: Process Pending Receipts |
| Model | `hr.expense` |
| Method | `_process_ocr_queue` |
| Interval | 5 minutes |
| Batch Size | 20 |

### 3.2 Check Cron Status

```bash
docker compose exec -T odoo odoo shell -d odoo <<'EOF'
cron = env['ir.cron'].search([('name', 'ilike', 'ocr')])
for c in cron:
    print(f"Name: {c.name}")
    print(f"Active: {c.active}")
    print(f"Last call: {c.lastcall}")
    print(f"Next call: {c.nextcall}")
    print("---")
EOF
```

### 3.3 Manually Trigger Cron

```bash
docker compose exec -T odoo odoo shell -d odoo <<'EOF'
env['hr.expense']._process_ocr_queue()
env.cr.commit()
print("OCR queue processed")
EOF
```

### 3.4 Enable/Disable Cron

```python
# Disable
cron = env['ir.cron'].search([('name', 'ilike', 'ocr expense')])
cron.write({'active': False})
env.cr.commit()

# Enable
cron.write({'active': True})
env.cr.commit()
```

---

## 4. Retry Logic

### 4.1 Default Configuration

| Setting | Value |
|---------|-------|
| Max retries | 3 |
| Retry delay | Exponential (1m, 5m, 15m) |
| Final state on max retry | `failed` |

### 4.2 Retry Flow

```
Attempt 1 → Fail → Wait 1 min → Attempt 2 → Fail → Wait 5 min → Attempt 3 → Fail → State: failed
```

### 4.3 Monitor Retry Counts

```sql
SELECT
  ocr_retry_count,
  COUNT(*) as count
FROM hr_expense
WHERE ocr_state IN ('pending', 'failed')
GROUP BY ocr_retry_count
ORDER BY ocr_retry_count;
```

---

## 5. Failure Handling

### 5.1 Common Failure Reasons

| Reason | Detection | Resolution |
|--------|-----------|------------|
| OCR service down | Connection error | Wait/retry or check service |
| Invalid image format | `UnsupportedFileType` | Convert to PNG/JPG |
| Image too large | Timeout | Resize before upload |
| API rate limit | 429 response | Implement backoff |
| Corrupted file | Parse error | Re-upload original |

### 5.2 View Failures

```sql
SELECT
  id, name, ocr_state, ocr_error_message,
  ocr_retry_count, write_date
FROM hr_expense
WHERE ocr_state = 'failed'
ORDER BY write_date DESC
LIMIT 20;
```

### 5.3 Bulk Reset Failures

```python
# Reset all failures from last 24 hours
from datetime import datetime, timedelta

cutoff = datetime.now() - timedelta(hours=24)
failures = env['hr.expense'].search([
    ('ocr_state', '=', 'failed'),
    ('write_date', '>=', cutoff.strftime('%Y-%m-%d %H:%M:%S'))
])
failures.write({
    'ocr_state': 'pending',
    'ocr_retry_count': 0,
    'ocr_error_message': False
})
env.cr.commit()
print(f"Reset {len(failures)} expenses")
```

---

## 6. Duplicate Detection

### 6.1 How It Works

1. File hash computed on upload (SHA256)
2. Hash compared against existing expenses
3. If match found → state = `duplicate`
4. Linked to original expense for reference

### 6.2 Check Duplicates

```sql
SELECT
  e1.id as duplicate_id,
  e1.name as duplicate_name,
  e2.id as original_id,
  e2.name as original_name,
  e1.attachment_hash
FROM hr_expense e1
JOIN hr_expense e2 ON e1.attachment_hash = e2.attachment_hash
WHERE e1.id > e2.id
AND e1.ocr_state = 'duplicate';
```

### 6.3 Override Duplicate

```python
# Force process despite duplicate
expense = env['hr.expense'].browse(EXPENSE_ID)
expense.write({
    'ocr_state': 'pending',
    'ocr_duplicate_of_id': False
})
expense._process_ocr(force=True)
env.cr.commit()
```

---

## 7. Review Queue

### 7.1 Low Confidence Processing

Expenses with confidence < 0.70 go to review queue.

### 7.2 View Review Queue

```sql
SELECT
  id, name, ocr_confidence, ocr_extracted_data,
  create_date
FROM hr_expense
WHERE ocr_state = 'review'
ORDER BY create_date ASC;
```

### 7.3 Approve from Review

```python
# Via UI: Expense > Action > Approve OCR
# Via code:
expense = env['hr.expense'].browse(EXPENSE_ID)
expense.action_approve_ocr()
env.cr.commit()
```

### 7.4 Bulk Approve High Confidence

```python
# Approve all review items with confidence >= 0.65
reviews = env['hr.expense'].search([
    ('ocr_state', '=', 'review'),
    ('ocr_confidence', '>=', 0.65)
])
for expense in reviews:
    expense.action_approve_ocr()
env.cr.commit()
print(f"Approved {len(reviews)} expenses")
```

---

## 8. Monitoring Dashboard

### 8.1 Daily Stats Query

```sql
SELECT
  DATE(create_date) as date,
  COUNT(*) FILTER (WHERE ocr_state = 'done') as successful,
  COUNT(*) FILTER (WHERE ocr_state = 'review') as review,
  COUNT(*) FILTER (WHERE ocr_state = 'failed') as failed,
  COUNT(*) FILTER (WHERE ocr_state = 'duplicate') as duplicates,
  ROUND(AVG(ocr_confidence)::numeric, 2) as avg_confidence
FROM hr_expense
WHERE ocr_state IS NOT NULL
AND create_date >= CURRENT_DATE - INTERVAL '7 days'
GROUP BY DATE(create_date)
ORDER BY date DESC;
```

### 8.2 Processing Time

```sql
SELECT
  DATE(create_date) as date,
  AVG(EXTRACT(EPOCH FROM (ocr_processed_at - create_date))) as avg_seconds
FROM hr_expense
WHERE ocr_state = 'done'
AND ocr_processed_at IS NOT NULL
AND create_date >= CURRENT_DATE - INTERVAL '7 days'
GROUP BY DATE(create_date)
ORDER BY date DESC;
```

---

## 9. Emergency Procedures

### 9.1 Disable All OCR Processing

```bash
# Disable cron
docker compose exec -T odoo odoo shell -d odoo <<'EOF'
env['ir.cron'].search([('name', 'ilike', 'ocr')]).write({'active': False})
env.cr.commit()
print("OCR cron disabled")
EOF
```

### 9.2 Drain Queue (Mark All Pending as Failed)

```sql
UPDATE hr_expense
SET ocr_state = 'failed', ocr_error_message = 'Emergency drain'
WHERE ocr_state IN ('pending', 'processing');
```

### 9.3 Full Reset

```sql
-- WARNING: Clears all OCR state
UPDATE hr_expense
SET
  ocr_state = NULL,
  ocr_confidence = NULL,
  ocr_extracted_data = NULL,
  ocr_retry_count = 0,
  ocr_error_message = NULL
WHERE ocr_state IS NOT NULL;
```

---

## 10. Verification Checklist

- [ ] Cron job active and running
- [ ] Pending queue is being processed
- [ ] No stuck "processing" items
- [ ] Failed items have error messages
- [ ] Review queue is manageable size
- [ ] Duplicate detection working
- [ ] Confidence threshold appropriate

---

*Last updated: 2026-01-08*
