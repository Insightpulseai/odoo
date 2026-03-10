---
name: expense-processing
description: Automates expense receipt capture, validation, and Odoo posting
version: 1.0.0
author: InsightPulse AI
tags: [expense, receipt, ocr, reimbursement, hr]
---

# Expense Processing Skill

## Overview

This skill handles the complete expense management workflow from receipt capture through reimbursement, including OCR extraction, policy validation, and Odoo integration.

## Capabilities

- Receipt image OCR via PaddleOCR
- AI-powered data extraction
- Policy compliance validation
- Automatic expense categorization
- Odoo hr.expense creation
- Approval workflow routing
- Reimbursement tracking

## Workflow

### Step 1: Receipt Capture

**Input Methods**:
- Mobile app upload
- Email forwarding (receipts@insightpulseai.com)
- Telegram bot
- Manual upload via Odoo

**Supported Formats**:
- Images: JPG, PNG, HEIC
- Documents: PDF (first page)
- Max size: 10MB

### Step 2: OCR Extraction

**PaddleOCR Endpoint**: `https://ocr.insightpulseai.com/api/ocr/receipt`

**Request**:
```json
{
  "image": "<base64_encoded_image>",
  "language": "en"
}
```

**Response**:
```json
{
  "text": "JOLLIBEE STORE 1234\n...",
  "confidence": 0.95,
  "regions": [...]
}
```

### Step 3: AI Data Structuring

**Claude Prompt**:
```
Extract receipt data and return JSON:
- merchant_name: string
- merchant_tin: string (if visible)
- receipt_date: YYYY-MM-DD
- receipt_number: string
- subtotal: number
- vat_amount: number
- total_amount: number
- payment_method: cash|credit_card|gcash|paymaya|other
- expense_category: meals|transportation|supplies|communication|accommodation|other
- description: brief description
```

### Step 4: Policy Validation

**Approval Thresholds (PHP)**:
| Amount | Approval | Route |
|--------|----------|-------|
| < 5,000 | Self | Auto-approve |
| 5,000 - 25,000 | Manager | Notify manager |
| 25,000 - 100,000 | Dept Head + Finance | Escalate |
| > 100,000 | CFO | Escalate + alert |

**Policy Rules**:
```python
rules = [
    Rule("amount_limit", lambda e: e.amount <= 100000, "Amount exceeds maximum"),
    Rule("valid_category", lambda e: e.category in ALLOWED_CATEGORIES, "Invalid category"),
    Rule("has_receipt", lambda e: e.receipt_image is not None, "Receipt required"),
    Rule("or_required", lambda e: e.amount < 1000 or e.has_official_receipt, "OR required > 1000"),
    Rule("not_weekend", lambda e: not e.is_personal, "Personal expenses not allowed"),
]
```

### Step 5: Odoo Integration

**hr.expense Creation**:
```json
{
  "name": "Jollibee - Client Meeting Lunch",
  "product_id": 1,  // Meals category
  "unit_amount": 1250.00,
  "quantity": 1,
  "date": "2026-01-06",
  "employee_id": 77,  // RIM
  "payment_mode": "own_account",
  "reference": "OR-12345678",
  "description": "Client meeting with ACME Foods project team"
}
```

**Category Mapping**:
| Category | Odoo Product ID | Account |
|----------|----------------|---------|
| meals | 1 | 6210 - Meals & Entertainment |
| transportation | 2 | 6220 - Transportation |
| supplies | 3 | 6230 - Office Supplies |
| communication | 4 | 6240 - Communication |
| accommodation | 5 | 6250 - Travel & Lodging |
| other | 6 | 6290 - Miscellaneous |

### Step 6: Approval Workflow

**Odoo States**:
```
draft → reported → submitted → approved → posted → done
                 ↘ refused ↙
```

**Notifications**:
- On submit: Notify approver via Mattermost
- On approve/refuse: Notify employee
- On post: Update reimbursement queue

## n8n Workflow Integration

The `expense_receipt_capture.json` workflow:

1. **Webhook receives image**
2. **PaddleOCR extracts text**
3. **Claude structures data**
4. **Policy check (IF node)**
   - Pass: Create expense in Odoo
   - Fail: Alert to #finance-general
5. **Respond with result**

## Mattermost Notifications

**Policy Violation Alert**:
```markdown
#### :warning: Policy Violation Alert
| Field | Value |
|:--|:--|
| **Amount** | PHP 7,500 |
| **Threshold** | PHP 5,000 |
| **Merchant** | Restaurant ABC |
| **Category** | meals |

**Action Required:** Manager approval needed
```

**Expense Created**:
```markdown
#### :receipt: Expense Submitted
| Field | Value |
|:--|:--|
| **Employee** | Rey Meran (RIM) |
| **Amount** | PHP 1,250 |
| **Category** | Meals |
| **Status** | Pending Approval |
```

## Receipt Requirements

### Valid Receipt Elements

- [x] Date of purchase
- [x] Merchant/vendor name
- [x] Itemized list
- [x] Total amount
- [x] OR number (for amounts > ₱1,000)
- [x] VAT details (if applicable)

### Common Issues

| Issue | Resolution |
|-------|------------|
| Faded receipt | Re-scan or request duplicate |
| Missing OR | Request from vendor |
| Foreign currency | Include exchange rate |
| Handwritten | Attach explanation |

## Reimbursement Schedule

- **Cutoff 1**: Submit by 10th → Reimbursed on 15th
- **Cutoff 2**: Submit by 25th → Reimbursed on 30th

## Error Handling

```python
errors = {
    "OCR_FAILED": "Could not extract text. Please re-upload clearer image.",
    "INVALID_DATE": "Receipt date could not be parsed. Please enter manually.",
    "CATEGORY_UNKNOWN": "Could not determine expense category. Please select.",
    "EMPLOYEE_NOT_FOUND": "Employee not found in system. Contact HR.",
    "DUPLICATE_RECEIPT": "This receipt may already exist. Please verify.",
}
```

## Commands

| Command | Action |
|---------|--------|
| `/expense submit` | Start expense submission |
| `/expense status [id]` | Check expense status |
| `/expense history` | View recent expenses |
| `/expense policy` | Show expense policy |

## Related Skills

- [Finance Month-End](../finance-month-end/SKILL.md)
- [BIR Tax Filing](../bir-tax-filing/SKILL.md)

## Changelog

- **v1.0.0** (2026-01-06): Initial release
