# Document Intelligence Processing Architecture

> Architecture for automated document processing using Azure Document Intelligence,
> following the Microsoft PDF forms processing reference architecture.
>
> Ref: https://learn.microsoft.com/en-us/azure/architecture/ai-ml/architecture/automate-pdf-forms-processing
> Cross-references:
>   - `ssot/governance/azdo-execution-hierarchy.yaml` (OBJ-002/FEAT-002-04, FEAT-002-05)
>   - `docs/architecture/AI_CONSOLIDATION_FOUNDRY.md` (agent integration)
>   - `infra/ssot/azure/resources.yaml` (`docai-ipai-dev`)

---

## 1. Intake Source

### Document Sources

| Source | Trigger | Format | Volume |
|--------|---------|--------|--------|
| Email attachments (Zoho) | Incoming mail → n8n webhook | PDF, JPEG, PNG | Low (~50/month) |
| Manual upload (Odoo) | User action in AP module | PDF, JPEG | Low |
| Scanned documents | File drop to ADLS bronze | PDF (scanned) | Low |
| API submission | REST endpoint | PDF, JPEG, PNG | Planned |

### Intake Flow

```
Source → n8n webhook / Odoo upload / ADLS file event
  → Validate (file type, size, virus scan)
  → Store raw document in ADLS bronze/documents/{source}/{date}/
  → Trigger extraction pipeline
```

**Constraints**:
- Max file size: 50MB (Azure Document Intelligence limit)
- Supported formats: PDF, JPEG, PNG, TIFF, BMP
- No executable files accepted

---

## 2. Extraction Service

### Azure Document Intelligence

**Resource**: `docai-ipai-dev` (Southeast Asia, `rg-ipai-ai-dev`)

| Model | Use Case | Fields Extracted |
|-------|----------|-----------------|
| Prebuilt Invoice | Supplier invoices | Vendor, invoice number, date, line items, amounts, tax |
| Prebuilt Receipt | Expense receipts | Merchant, date, total, items, tax |
| Custom model (future) | BIR forms (2551Q, 2550M) | Form-specific fields |

### Extraction Pipeline

```
Raw document (ADLS bronze)
  → Azure Document Intelligence (prebuilt model)
  → Structured JSON result
  → Confidence scoring per field
  → Store result in ADLS silver/documents/{source}/{doc_id}.json
```

### Confidence Thresholds

| Threshold | Action |
|-----------|--------|
| ≥ 0.90 | Auto-accept: proceed to posting |
| 0.70 – 0.89 | Review queue: flag for human validation |
| < 0.70 | Reject: route to manual entry |

---

## 3. Orchestration

### Workflow Engine: n8n

```
┌─────────────┐     ┌──────────────────┐     ┌────────────────┐
│ Intake       │────→│ Document         │────→│ Confidence      │
│ (webhook/    │     │ Intelligence API │     │ Router          │
│  file event) │     │ (extraction)     │     │                │
└─────────────┘     └──────────────────┘     └───────┬────────┘
                                                      │
                              ┌────────────────────────┼────────────────┐
                              ▼                        ▼                ▼
                     ┌────────────────┐     ┌──────────────┐   ┌───────────┐
                     │ Auto-accept    │     │ Review Queue │   │ Reject    │
                     │ (≥0.90)        │     │ (0.70-0.89)  │   │ (<0.70)  │
                     │                │     │              │   │           │
                     │ → Processing   │     │ → Slack      │   │ → Slack  │
                     │   Function     │     │   notification│   │   alert  │
                     └────────────────┘     │ → Odoo activity│  │ → Manual │
                                            └──────────────┘   │   entry  │
                                                               └───────────┘
```

### n8n Workflow: `document-intelligence-pipeline`

Location: `automations/n8n/workflows/document-intelligence-pipeline.json`
Credentials: `{{ $credentials.azure_document_intelligence.endpoint }}` + Key Vault

---

## 4. Processing Function

### Odoo Integration (`ipai_document_intelligence_bridge`)

The processing function maps extracted fields to Odoo records:

#### Invoice Processing

```
Extracted JSON → Field Mapping → Odoo Record Creation
  vendor_name    → res.partner (fuzzy match)
  invoice_number → account.move.ref
  invoice_date   → account.move.invoice_date
  line_items[]   → account.move.line (products matched by description)
  total_amount   → account.move.amount_total (validation)
  tax_amount     → account.move.tax_line_ids
```

#### Expense Processing

```
Extracted JSON → Field Mapping → Odoo Record Creation
  merchant      → expense.sheet vendor
  date          → hr.expense.date
  total         → hr.expense.total_amount
  category      → hr.expense.product_id (ML categorization, future)
```

### Posting Rules

| Rule | Enforcement |
|------|------------|
| Draft only | Documents created as draft — never auto-posted |
| Duplicate detection | Invoice number + vendor + date uniqueness check |
| Amount validation | Extracted total must match sum of line items (±0.01) |
| Currency | Default PHP; multi-currency via Odoo core |
| Audit trail | `ipai.document.audit.log` records extraction + mapping + confidence |

---

## 5. Review / Exception Handling

### Review Queue

When confidence is between 0.70 and 0.89:

1. Odoo activity created on draft document (`mail.activity`)
2. Slack notification to finance channel
3. User reviews extracted fields vs original document (side-by-side in Odoo)
4. User confirms, corrects, or rejects
5. Corrections fed back as training data (future custom model improvement)

### Exception Types

| Exception | Handling |
|-----------|---------|
| Unknown vendor | Create partner draft + flag for review |
| Missing fields | Route to manual entry with partial pre-fill |
| Duplicate invoice | Block creation, alert user |
| Amount mismatch | Flag for review, show extracted vs calculated |
| Unsupported format | Reject with reason, alert user |

---

## 6. Production Hardening

### Starter → Production Path

| Phase | Capability | Status |
|-------|-----------|--------|
| **Starter** | Manual upload → extraction → draft invoice | In development |
| **Intermediate** | Email intake → auto-extraction → confidence routing | Planned |
| **Production** | Full pipeline + exception handling + audit trail | Planned |
| **Advanced** | Custom BIR form models + ML categorization | Future |

### Reliability Requirements

| Requirement | Target |
|------------|--------|
| Extraction latency | < 30s per document |
| Availability | 99.5% (Document Intelligence SLA) |
| Data retention | Raw documents: 7 years (BIR requirement) |
| Error rate | < 5% rejection rate after model tuning |
| Audit trail | 100% of processed documents logged |

### Monitoring

| Metric | Alert Threshold |
|--------|----------------|
| Extraction failures | > 3 in 1 hour |
| Confidence < 0.70 rate | > 20% of batch |
| Processing latency | > 60s per document |
| Queue depth | > 50 unreviewed items |

### Evidence Trail

Every processed document produces:
1. Raw document (ADLS bronze)
2. Extraction result JSON (ADLS silver)
3. Odoo audit log entry (`ipai.document.audit.log`)
4. Confidence score and routing decision
5. Human review decision (if applicable)

---

*Last updated: 2026-03-17*
