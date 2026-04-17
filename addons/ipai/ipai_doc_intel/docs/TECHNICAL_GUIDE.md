# TECHNICAL_GUIDE — ipai_doc_intel

## Architecture

```
User uploads PDF to vendor bill attachment
  → clicks "Extract with DocAI" button
    → doc_intel_service.analyze_invoice(file_bytes)
      → POST to DocAI prebuilt-invoice API
      → poll for result (max 60s)
      → parse fields + confidence
    → account_move._apply_docai_fields(parsed)
      → set partner_id, ref, dates, lines
      → post chatter message with confidence
    → set x_docai_status (extracted / review / failed)
```

## Models extended

| Model | Type | Changes |
|-------|------|---------|
| `account.move` | _inherit | +3 fields, +2 methods |
| `ipai.doc.intel.service` | AbstractModel | Service layer (no DB table) |

## Fields added

On `account.move`:
- `x_docai_status` — Selection (none/extracting/extracted/review/failed)
- `x_docai_confidence` — Float (average extraction confidence)
- `x_docai_raw_result` — Text (JSON dump of full DocAI response)

## Methods

| Method | Model | Purpose |
|--------|-------|---------|
| `action_extract_with_docai` | account.move | Button action — orchestrates extraction |
| `_apply_docai_fields` | account.move | Maps DocAI fields → move fields |
| `_apply_docai_lines` | account.move | Creates invoice lines from extracted items |
| `analyze_invoice` | doc.intel.service | Calls DocAI API + polls + parses |
| `_parse_invoice_result` | doc.intel.service | Transforms DocAI response to clean dict |
| `_extract_field_value` | doc.intel.service | Type-aware field value extraction |

## View inheritance

- `account.view_move_form` — adds "Extract with DocAI" button + status badge
- `account.view_in_invoice_bill_tree` — adds DocAI status column

## Security model

- `ipai.doc.intel.service` — read-only for `account.group_account_invoice`
- Extraction action available to any user who can edit vendor bills

## Data files

- `ir_config_parameter.xml` — seeds endpoint + API key placeholder

## External integrations

- Azure Document Intelligence REST API (v2024-11-30)
- `prebuilt-invoice` model (GA)

## Test strategy

1. Unit: mock DocAI response → verify field mapping
2. Integration: real DocAI call with sample PDF → verify end-to-end
3. UI: verify button visibility on vendor bills only (not customer invoices)

## Known limitations

- Polling blocks the UI for up to 60 seconds (use async job for production)
- API key stored in ir.config_parameter (should use KV SecretClient for production)
- No batch processing (one invoice at a time)
- Custom TBWA forms need separate custom model training
