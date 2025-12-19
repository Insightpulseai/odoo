# IPAI Expense OCR (CE)

**Version**: 18.0.1.0.0
**Category**: Human Resources/Expenses
**License**: AGPL-3
**Author**: InsightPulseAI

Use InsightPulse OCR service for expense digitization on Odoo CE (no Enterprise/IAP required).

---

## Overview

The **IPAI Expense OCR** module integrates InsightPulse's OCR service with Odoo CE expense management. It enables automatic extraction of expense data from receipt images, eliminating manual data entry and reducing errors. Unlike Odoo Enterprise's IAP-based OCR, this module uses a self-hosted OCR service, making it ideal for organizations requiring data sovereignty or cost control.

## Features

### Core Capabilities

- **Receipt Scanning**: Extract expense data from receipt images
- **Auto-Population**: Automatically fill expense fields from OCR results
- **Observability**: Complete logging of all OCR calls for quality monitoring
- **Multi-Source**: Support for Web UI, Mobile App, and API sources
- **Confidence Scoring**: Track extraction accuracy and confidence levels

### Extracted Data

| Field | Description |
|-------|-------------|
| **Merchant Name** | Vendor/merchant from receipt header |
| **Total Amount** | Receipt total amount |
| **Date** | Invoice/receipt date |
| **Currency** | Currency code (if detected) |

### OCR Status Tracking

```
Not Scanned → Pending → Done
                 ↓
              Error
```

- **Not Scanned**: No OCR attempted
- **Pending**: OCR in progress
- **Done**: Successfully extracted data
- **Error**: OCR failed (check logs)

---

## Installation

### Prerequisites

This module depends on:
- `hr_expense` (Odoo Expenses)

### Python Dependencies

```bash
pip install requests
```

### Install

1. Place the module in your Odoo addons directory
2. Update the apps list: `Settings → Apps → Update Apps List`
3. Search for "IPAI Expense OCR (CE)"
4. Click **Install**

---

## Configuration

### Enable OCR Service

1. Navigate to: **Settings → Expenses → IPAI OCR Settings**
2. Enable **Enable InsightPulse OCR**
3. Configure API settings:
   - **API URL**: Your InsightPulse OCR endpoint
   - **API Key**: Authentication key (optional)
4. Click **Save**

### API Settings

| Setting | Example | Description |
|---------|---------|-------------|
| API URL | `https://ocr.insightpulseai.net/api/expense/ocr` | OCR service endpoint |
| API Key | `sk-xxxx...` | X-API-Key header value |

### InsightPulse OCR Service

The OCR endpoint expects:
- **Method**: POST
- **Content**: multipart/form-data with `file` field
- **Headers**: `X-API-Key` (if configured)

Expected response JSON:
```json
{
  "merchant_name": "SM Supermarket",
  "total_amount": 1250.00,
  "invoice_date": "2025-11-30",
  "currency": "PHP",
  "confidence": 0.95
}
```

---

## Usage

### Scanning Receipts

1. Navigate to: **Expenses → My Expenses**
2. Open an expense record or create new
3. Attach a receipt image (JPG, PNG)
4. Click **Scan with OCR** button
5. Fields are automatically populated from OCR results
6. Review and adjust if needed
7. Submit expense

### Viewing OCR Logs

1. Navigate to: **Expenses → OCR Logs**
2. View all OCR scan attempts with:
   - Timestamp and duration
   - Source (Web/Mobile/API)
   - Status (Success/Partial/Failed)
   - Extracted data
   - Error messages (if failed)

### Troubleshooting OCR Failures

Common issues and solutions:

| Error | Solution |
|-------|----------|
| OCR not enabled | Enable in Settings → Expenses → IPAI OCR |
| API URL not configured | Set API URL in settings |
| No image attached | Attach receipt image before scanning |
| OCR service timeout | Check service availability, increase timeout |
| Low confidence score | Use clearer receipt image |

---

## Data Model

### HR Expense Extension (`hr.expense`)

Additional field on standard expense model:

```python
Fields:
- ocr_status: Selection (none / pending / done / error)
  Status tracking for OCR processing
```

### OCR Expense Log (`ocr.expense.log`)

```python
Fields:
# Core identifiers
- expense_id: Linked expense record
- user_id: User who initiated scan
- employee_id: Employee context

# Request metadata
- created_at: Timestamp
- source: web / mobile / api
- duration_ms: Processing time in milliseconds

# OCR results
- status: success / partial / failed
- vendor_name_extracted: Merchant name
- total_extracted: Amount
- currency_extracted: Currency code
- date_extracted: Receipt date
- confidence: Confidence score (0.0-1.0)

# Error handling
- error_message: Error details
- raw_payload_path: Path to raw response
- request_id: Trace identifier

# Computed
- is_successful: Boolean flag for analytics
```

---

## API Integration

### Programmatic OCR Scan

```python
# Get expense record
expense = env['hr.expense'].browse(expense_id)

# Attach receipt image
attachment = env['ir.attachment'].create({
    'name': 'receipt.jpg',
    'datas': base64_image_data,
    'res_model': 'hr.expense',
    'res_id': expense.id,
})

# Trigger OCR scan
expense.action_ipai_ocr_scan()

# Check results
print(f"Status: {expense.ocr_status}")
print(f"Name: {expense.name}")
print(f"Amount: {expense.total_amount}")
```

### OCR Log Analytics

```python
# Get success rate for last 30 days
from datetime import datetime, timedelta

date_from = datetime.now() - timedelta(days=30)
logs = env['ocr.expense.log'].search([
    ('created_at', '>=', date_from)
])

total = len(logs)
successful = len(logs.filtered(lambda l: l.is_successful))
success_rate = (successful / total * 100) if total else 0

print(f"OCR Success Rate: {success_rate:.1f}%")
```

---

## Technical Details

### File Structure

```
ipai_ocr_expense/
├── __init__.py
├── __manifest__.py
├── README.md
├── models/
│   ├── __init__.py
│   ├── hr_expense_ocr.py
│   ├── ocr_expense_log.py
│   └── res_config_settings.py
├── views/
│   ├── ipai_ocr_settings_views.xml
│   ├── ipai_ocr_expense_views.xml
│   └── ocr_expense_log_views.xml
└── security/
    └── ir.model.access.csv
```

### Dependencies

- Python: `requests` library
- Odoo modules: `hr_expense`
- External: InsightPulse OCR service

### Security Considerations

- API keys stored in `ir.config_parameter`
- Consider encrypting sensitive values
- Logs exclude raw receipt images by default
- User-level access control on log records

---

## Advantages Over Enterprise IAP

| Feature | IPAI OCR | Enterprise IAP |
|---------|----------|----------------|
| Self-hosted option | Yes | No |
| Data sovereignty | Full control | Cloud-based |
| Cost model | Fixed/unlimited | Per-scan credits |
| Customization | Full API control | Limited |
| CE compatibility | Yes | Enterprise only |

---

## Support

- **Author**: InsightPulseAI
- **Website**: https://insightpulseai.net
- **License**: AGPL-3

---

## Changelog

### Version 18.0.1.0.0

- Initial release
- InsightPulse OCR integration
- Automatic expense field population
- OCR call logging for observability
- Settings UI for API configuration
- Multi-source support (Web/Mobile/API)
- Confidence score tracking
