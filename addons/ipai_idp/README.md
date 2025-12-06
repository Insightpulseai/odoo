# IPAI Intelligent Document Processing (IDP)

Enterprise-grade IDP service that converts messy documents into clean,
validated, analytics-ready structured records using OCR + LLM extraction.

## Features

- **Multi-document type support**: Invoices, receipts, purchase orders, delivery notes
- **LLM-based extraction**: Versioned prompts/models for reproducibility
- **Confidence scoring**: Auto-approval for high-confidence extractions
- **Human-in-the-loop**: Review workflow for low-confidence results
- **Validation rules engine**: Configurable business rule validation
- **Health endpoints**: Kubernetes-ready liveness, readiness, and deep health checks

## Architecture

```
Upload -> OCR -> Classify -> LLM Extract -> Validate -> Auto-approve/Review -> Export
```

See the full architecture diagram: [docs/architecture/ipai_idp_architecture.drawio](../../docs/architecture/ipai_idp_architecture.drawio)

### Processing Pipeline

1. **Document Ingestion**: Sources include manual upload, email inbox, REST API, mobile app, cloud drive
2. **OCR Processing**: Converts images/PDFs to text using configurable OCR provider
3. **Classification**: Identifies document type (invoice, receipt, PO, delivery note)
4. **LLM Extraction**: Uses versioned prompts to extract structured fields
5. **Validation**: Applies configurable business rules
6. **Routing**: Auto-approves high-confidence extractions, routes others to review
7. **Export**: Creates Odoo records (vendor bills, etc.)

### Security Groups

- **IDP User**: Read-only access to documents
- **IDP Reviewer**: Can create and edit reviews
- **IDP Manager**: Full CRUD on documents and reviews
- **IDP Admin**: Configuration access (model versions, validation rules, settings)

## API Endpoints

### Health Checks

- `GET /ipai/idp/livez` - Liveness probe (lightweight)
- `GET /ipai/idp/readyz` - Readiness probe (checks DB)
- `GET /ipai/idp/healthz` - Deep health check (all dependencies)
- `POST /ipai/idp/metrics` - Processing metrics (requires auth)

### Document Processing

- `POST /ipai/idp/api/documents` - Upload new document
- `GET /ipai/idp/api/documents` - List documents
- `GET /ipai/idp/api/documents/<id>` - Get document details
- `POST /ipai/idp/api/documents/<id>/process` - Trigger processing
- `POST /ipai/idp/api/documents/<id>/approve` - Approve document

### Testing Endpoints

- `POST /ipai/idp/api/extract_preview` - Preview extraction without saving
- `POST /ipai/idp/api/validate` - Validate data against rules
- `POST /ipai/idp/api/parse/amount` - Parse amount string
- `POST /ipai/idp/api/parse/date` - Normalize date string

## Configuration

Configure via **Settings → IPAI IDP** or set these system parameters:

### API Keys
- `ipai_idp.ocr_api_url` - OCR service endpoint
- `ipai_idp.ocr_api_key` - OCR service API key
- `ipai_idp.llm_api_url` - LLM API endpoint (Claude/OpenAI compatible)
- `ipai_idp.llm_api_key` - LLM API key

### Processing Options
- `ipai_idp.auto_approve_enabled` - Enable auto-approval (default: True)
- `ipai_idp.auto_approve_confidence` - Minimum confidence for auto-approval (default: 0.90)
- `ipai_idp.async_processing` - Enable async processing via queue_job (default: False)

### Async Processing

When `queue_job` module is installed and `ipai_idp.async_processing` is enabled:
- Documents are processed asynchronously via job queue
- Falls back to synchronous processing if queue_job is unavailable
- Jobs use channel `root.idp` for prioritization

## Model Versions

Model versions allow you to version your extraction prompts and schemas:

1. Create a new model version with updated prompt/schema
2. Set it as default for the document type
3. A/B test by comparing success rates
4. Roll back by deactivating problematic versions

## Validation Rules

Configurable validation rules include:

- **Required fields**: Ensure critical fields are present
- **Format checks**: Regex validation for dates, codes
- **Range checks**: Numeric value bounds
- **Sum checks**: Total = subtotal + tax
- **Date order**: Invoice date before due date
- **Custom expressions**: Python expressions for complex logic

## License

AGPL-3
