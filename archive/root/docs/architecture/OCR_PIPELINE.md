# OCR Pipeline Architecture

**Version:** 1.0.0
**Date:** 2026-01-08

---

## 1. Overview

The OCR Pipeline provides self-hosted document intelligence capabilities for Odoo 18 CE, replacing Enterprise "Documents AI" features without using Odoo SA proprietary modules or IAP billing.

```
┌─────────────────────────────────────────────────────────────────────┐
│                        OCR Pipeline                                  │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│   User                                                               │
│     │                                                                │
│     ▼                                                                │
│   ┌─────────────┐     ┌─────────────┐     ┌─────────────┐           │
│   │   Odoo 18   │────▶│ OCR Service │────▶│   Storage   │           │
│   │    (OWL)    │◀────│  (Docker)   │     │  (Odoo DB)  │           │
│   └─────────────┘     └─────────────┘     └─────────────┘           │
│         │                   │                   │                    │
│         ▼                   ▼                   ▼                    │
│   ┌─────────────┐     ┌─────────────┐     ┌─────────────┐           │
│   │ ipai_       │     │ Text + Field│     │ ipai.       │           │
│   │ document_ai │     │ Extraction  │     │ document    │           │
│   └─────────────┘     └─────────────┘     └─────────────┘           │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 2. Components

### 2.1 Odoo Module: `ipai_document_ai`

**Responsibilities:**
- Document upload UI
- OCR service communication
- Result storage and display
- Field mapping and application

**Key Models:**

```
┌─────────────────────────────────────┐
│          ipai.document              │
├─────────────────────────────────────┤
│ id                    : Integer     │
│ name                  : Char        │
│ attachment_id         : Many2one    │
│ res_model             : Char        │
│ res_id                : Integer     │
│ doc_type              : Selection   │
│ state                 : Selection   │
│ extracted_text        : Text        │
│ extraction_json       : Json        │
│ confidence            : Float       │
│ ocr_job_id            : Char        │
│ error_message         : Text        │
│ create_date           : Datetime    │
│ processing_duration   : Float       │
└─────────────────────────────────────┘
```

**States:**
```
draft ──▶ processing ──▶ ready ──▶ applied
                │
                └──▶ failed
```

### 2.2 OCR Service

**Technology Stack:**
- Python FastAPI (or Flask)
- Tesseract OCR (text extraction)
- LayoutLM / DocTR (document understanding)
- Optional: PaddleOCR for multi-language

**Endpoints:**

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check |
| POST | `/v1/ocr/extract` | Sync extraction |
| POST | `/v1/ocr/extract-async` | Async extraction |
| GET | `/v1/ocr/jobs/{id}` | Job status |

### 2.3 Storage

**Option A: Odoo Attachments (Default)**
- Simple, single source of truth
- Suitable for documents < 10MB
- Uses `ir.attachment`

**Option B: Object Storage + Signed URLs**
- Better for large PDFs
- S3-compatible storage
- Signed URLs for secure access

---

## 3. Data Flow

### 3.1 Sync Extraction Flow

```
┌──────────┐    ┌──────────────┐    ┌─────────────┐    ┌──────────────┐
│  User    │    │    Odoo      │    │ OCR Service │    │   Odoo DB    │
│          │    │ ipai_doc_ai  │    │             │    │              │
└────┬─────┘    └──────┬───────┘    └──────┬──────┘    └──────┬───────┘
     │                 │                    │                  │
     │ Upload PDF      │                    │                  │
     │────────────────▶│                    │                  │
     │                 │                    │                  │
     │                 │ Create ipai.doc    │                  │
     │                 │ state=processing   │                  │
     │                 │────────────────────│─────────────────▶│
     │                 │                    │                  │
     │                 │ POST /v1/ocr/extract                  │
     │                 │───────────────────▶│                  │
     │                 │                    │                  │
     │                 │                    │ Extract text     │
     │                 │                    │ + fields         │
     │                 │                    │                  │
     │                 │ JSON result        │                  │
     │                 │◀───────────────────│                  │
     │                 │                    │                  │
     │                 │ Update ipai.doc    │                  │
     │                 │ state=ready        │                  │
     │                 │────────────────────│─────────────────▶│
     │                 │                    │                  │
     │ Show results    │                    │                  │
     │◀────────────────│                    │                  │
     │                 │                    │                  │
```

### 3.2 Field Mapping Flow

```
┌──────────┐    ┌──────────────┐    ┌──────────────┐
│  User    │    │    Odoo      │    │ Target Model │
│          │    │ ipai_doc_ai  │    │ (e.g. Bill)  │
└────┬─────┘    └──────┬───────┘    └──────┬───────┘
     │                 │                    │
     │ Review fields   │                    │
     │◀────────────────│                    │
     │                 │                    │
     │ Approve mapping │                    │
     │────────────────▶│                    │
     │                 │                    │
     │                 │ Write fields       │
     │                 │───────────────────▶│
     │                 │                    │
     │                 │ Update ipai.doc    │
     │                 │ state=applied      │
     │                 │                    │
     │ Success         │                    │
     │◀────────────────│                    │
     │                 │                    │
```

---

## 4. Field Extraction Schema

### 4.1 Invoice / Bill Fields

| Field | Type | Description |
|-------|------|-------------|
| `vendor_name` | string | Supplier/vendor name |
| `invoice_number` | string | Invoice/bill number |
| `invoice_date` | date | Document date |
| `due_date` | date | Payment due date |
| `currency` | string | Currency code (PHP, USD) |
| `subtotal` | float | Amount before tax |
| `tax` | float | Tax amount |
| `total` | float | Total amount |
| `payment_terms` | string | Payment terms text |

### 4.2 Receipt Fields

| Field | Type | Description |
|-------|------|-------------|
| `merchant_name` | string | Store/merchant name |
| `receipt_date` | date | Transaction date |
| `total` | float | Total amount |
| `payment_method` | string | Cash/Card/etc |
| `items` | array | Line items (if extracted) |

### 4.3 Contract Fields

| Field | Type | Description |
|-------|------|-------------|
| `parties` | array | Contract parties |
| `effective_date` | date | Start date |
| `expiry_date` | date | End date |
| `contract_value` | float | Total value |
| `key_terms` | array | Important clauses |

---

## 5. Confidence Thresholds

| Threshold | Action |
|-----------|--------|
| > 0.90 | Auto-apply (optional) |
| 0.70 - 0.90 | Show for review |
| < 0.70 | Flag as uncertain |

**Configuration:**
```python
OCR_CONFIDENCE_AUTO_APPLY = 0.90
OCR_CONFIDENCE_REVIEW = 0.70
OCR_CONFIDENCE_UNCERTAIN = 0.50
```

---

## 6. Error Handling

### 6.1 Service Unavailable

```python
# Retry with exponential backoff
max_retries = 3
delays = [5, 15, 45]  # seconds

for attempt, delay in enumerate(delays):
    try:
        result = ocr_service.extract(document)
        break
    except ServiceUnavailable:
        if attempt < max_retries - 1:
            time.sleep(delay)
        else:
            document.state = 'failed'
            document.error_message = 'OCR service unavailable after retries'
```

### 6.2 Timeout

```python
# Mark for retry
if timeout_error:
    document.state = 'failed'
    document.error_message = 'Processing timeout - retry with smaller file'
```

### 6.3 Low Confidence

```python
# Flag for manual review
if all_fields_low_confidence:
    document.requires_manual_review = True
    document.review_note = 'All fields below confidence threshold'
```

---

## 7. Security

### 7.1 Access Control

**Groups:**
- `ipai_document_ai.group_document_ai_user` - Can upload and review
- `ipai_document_ai.group_document_ai_admin` - Can configure and manage

**Record Rules:**
- Users can only see documents they created or on records they can access

### 7.2 Data Privacy

- Extracted text stored in Odoo (not in OCR service)
- OCR service is stateless (no persistent storage of documents)
- Option to purge extraction data after application

### 7.3 Network Security

- OCR service on internal network only (no public exposure)
- HTTPS between Odoo and OCR if crossing network boundaries
- API key authentication (optional)

---

## 8. Performance

### 8.1 Benchmarks

| Document Type | Size | Expected Time |
|---------------|------|---------------|
| Single page PDF | < 1MB | < 5s |
| Multi-page PDF (5 pages) | < 5MB | < 15s |
| Large PDF (20 pages) | < 20MB | < 60s |
| Image (JPG/PNG) | < 2MB | < 3s |

### 8.2 Scaling

**Horizontal:**
- Run multiple OCR service containers
- Load balance with round-robin

**Vertical:**
- Increase container CPU/memory
- Use GPU acceleration (if available)

---

## 9. Integration Points

### 9.1 Supported Models

| Model | Button Location | Field Mapping |
|-------|-----------------|---------------|
| `account.move` (Bill) | Form view header | Vendor, Date, Amounts |
| `account.move` (Invoice) | Form view header | Partner, Date, Amounts |
| `hr.expense` | Form view header | Vendor, Amount, Date |
| `purchase.order` | Form view header | Vendor, Lines, Total |

### 9.2 Hooks

```python
# Before extraction
def _before_ocr_extract(self):
    """Validate document before sending to OCR."""
    pass

# After extraction
def _after_ocr_extract(self, result):
    """Process extraction result before storing."""
    pass

# Before apply
def _before_field_apply(self, field_mapping):
    """Validate field mapping before writing to target."""
    pass
```

---

## 10. Monitoring

### 10.1 Key Metrics

| Metric | Description | Alert |
|--------|-------------|-------|
| `ocr_extraction_duration_seconds` | Time to extract | > 60s |
| `ocr_extraction_errors_total` | Error count | > 10/hour |
| `ocr_confidence_avg` | Average confidence | < 0.7 |
| `ocr_queue_depth` | Pending documents | > 50 |

### 10.2 Logging

```python
_logger.info(f"OCR extraction started for document {doc.id}")
_logger.info(f"OCR extraction completed: {doc.id}, confidence={doc.confidence:.2f}")
_logger.warning(f"OCR low confidence: {doc.id}, confidence={doc.confidence:.2f}")
_logger.error(f"OCR extraction failed: {doc.id}, error={doc.error_message}")
```

---

## 11. Future Enhancements

- [ ] Table extraction and line item parsing
- [ ] Multi-language support
- [ ] Custom model training for domain-specific documents
- [ ] Batch processing for bulk uploads
- [ ] Integration with document management system
- [ ] Real-time extraction preview

---

*This architecture document is the reference for OCR pipeline implementation.*
