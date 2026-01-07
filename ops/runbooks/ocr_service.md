# OCR Service Operational Runbook

**Purpose:** Operate and maintain the self-hosted OCR service for document intelligence.

**Service Location:** `188.166.237.231:8000` (or `http://ocr:8000` on internal network)

---

## 1. Overview

The OCR service provides document extraction capabilities for:
- Invoices and bills
- Receipts
- Purchase orders
- Contracts
- General documents

### Capabilities

| Feature | Description |
|---------|-------------|
| Text extraction | Full text from PDF/images |
| Layout analysis | Bounding boxes for text blocks |
| Field extraction | Structured fields (vendor, date, amounts) |
| Document classification | Auto-detect document type |
| Confidence scores | Per-field confidence values |

---

## 2. Environment Configuration

### Odoo Environment Variables

Set these in the Odoo container:

```bash
OCR_BASE_URL=http://ocr:8000          # Internal network
# OR
OCR_BASE_URL=http://188.166.237.231:8000  # Direct access

OCR_TIMEOUT_SECONDS=60                # Request timeout
OCR_MAX_MB=25                         # Max file size
OCR_RETRY_ATTEMPTS=3                  # Retry on failure
OCR_RETRY_DELAY_SECONDS=5             # Delay between retries
```

### Docker Compose (if co-located)

```yaml
services:
  ocr:
    image: your-ocr-image:latest
    container_name: ocr
    restart: unless-stopped
    ports:
      - "8000:8000"
    environment:
      - LOG_LEVEL=info
      - MAX_WORKERS=4
      - MAX_FILE_SIZE_MB=25
    volumes:
      - ocr_cache:/app/cache
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    networks:
      - odoo_backend

volumes:
  ocr_cache:
```

---

## 3. API Reference

### Health Check

```bash
GET /health

Response:
{
  "status": "ok",
  "version": "1.0.0",
  "uptime_seconds": 3600
}
```

### Extract (Sync)

```bash
POST /v1/ocr/extract
Content-Type: multipart/form-data

Form fields:
- file: PDF/JPG/PNG document
- options: JSON string (optional)
  {
    "doc_type_hint": "invoice",  # optional hint
    "extract_tables": true,       # extract tables
    "language": "en"              # OCR language
  }

Response:
{
  "doc_type": "invoice",
  "text": "full extracted text...",
  "blocks": [
    { "text": "ACME INC", "bbox": [12, 32, 210, 58], "conf": 0.98 }
  ],
  "fields": {
    "vendor_name": { "value": "ACME INC", "conf": 0.93 },
    "invoice_number": { "value": "INV-10021", "conf": 0.89 },
    "invoice_date": { "value": "2026-01-08", "conf": 0.91 },
    "currency": { "value": "PHP", "conf": 0.85 },
    "subtotal": { "value": 1000.0, "conf": 0.87 },
    "tax": { "value": 120.0, "conf": 0.84 },
    "total": { "value": 1120.0, "conf": 0.92 }
  },
  "tables": [],
  "meta": {
    "pages": 2,
    "engine": "tesseract+layoutlm",
    "duration_ms": 1432
  }
}
```

### Extract (Async) - Optional

```bash
POST /v1/ocr/extract-async
Content-Type: multipart/form-data

Response:
{
  "job_id": "abc123",
  "status": "pending",
  "poll_url": "/v1/ocr/jobs/abc123"
}

---

GET /v1/ocr/jobs/{job_id}

Response (pending):
{
  "job_id": "abc123",
  "status": "processing",
  "progress": 0.5
}

Response (complete):
{
  "job_id": "abc123",
  "status": "complete",
  "result": { ... extraction result ... }
}
```

---

## 4. Verification Commands

### Health Check

```bash
# Basic health
curl -sS http://188.166.237.231:8000/health | jq .

# Expected:
# { "status": "ok", "version": "1.0.0" }
```

### Smoke Test

```bash
# Extract from sample invoice
curl -sS -X POST \
  -F "file=@./sample-invoice.pdf" \
  http://188.166.237.231:8000/v1/ocr/extract | jq .

# Check extracted fields
curl -sS -X POST \
  -F "file=@./sample-invoice.pdf" \
  http://188.166.237.231:8000/v1/ocr/extract | jq '.fields'
```

### From Odoo Container

```bash
# Test connectivity from Odoo
docker exec odoo-core curl -sS http://ocr:8000/health

# Or direct IP
docker exec odoo-core curl -sS http://188.166.237.231:8000/health
```

---

## 5. Monitoring

### Metrics to Track

| Metric | Description | Alert Threshold |
|--------|-------------|-----------------|
| Response time | P95 latency | > 30s |
| Error rate | 5xx responses | > 5% |
| Queue depth | Pending jobs | > 100 |
| Memory usage | Container memory | > 80% |
| CPU usage | Container CPU | > 90% |

### Log Inspection

```bash
# View recent logs
docker logs ocr --tail 100

# Follow logs
docker logs ocr -f

# Filter errors
docker logs ocr 2>&1 | grep -i error
```

### Prometheus Metrics (if enabled)

```bash
curl -sS http://188.166.237.231:8000/metrics
```

---

## 6. Troubleshooting

### Common Issues

| Symptom | Cause | Solution |
|---------|-------|----------|
| Connection refused | Service not running | `docker start ocr` |
| Timeout | Large file / slow processing | Increase `OCR_TIMEOUT_SECONDS` |
| Low confidence | Poor image quality | Improve scan quality |
| Wrong doc type | Ambiguous document | Pass `doc_type_hint` |
| Out of memory | Large PDF | Increase container memory |

### Debug Mode

```bash
# Run with debug logging
docker run -e LOG_LEVEL=debug your-ocr-image:latest

# Test single file with verbose output
curl -v -X POST \
  -F "file=@./test.pdf" \
  http://188.166.237.231:8000/v1/ocr/extract
```

### Restart Service

```bash
# Restart container
docker restart ocr

# Full redeploy
docker-compose up -d --force-recreate ocr
```

---

## 7. Maintenance

### Cache Cleanup

```bash
# Clear OCR cache (if using file cache)
docker exec ocr rm -rf /app/cache/*

# Or volume cleanup
docker volume rm ocr_cache
```

### Update Service

```bash
# Pull new image
docker pull your-ocr-image:latest

# Restart with new image
docker-compose up -d ocr
```

### Backup/Restore

The OCR service is stateless - no backup needed.
Extracted results are stored in Odoo (`ipai.document` model).

---

## 8. Integration with Odoo

### Module: `ipai_document_ai`

The Odoo module handles:
1. File upload from user
2. Send to OCR service
3. Store extraction results
4. Display review UI
5. Apply fields to records

### API Call from Odoo

```python
import requests
import os

OCR_URL = os.getenv('OCR_BASE_URL', 'http://ocr:8000')
OCR_TIMEOUT = int(os.getenv('OCR_TIMEOUT_SECONDS', 60))

def extract_document(file_content, filename):
    """Send document to OCR service and return extraction result."""
    try:
        response = requests.post(
            f"{OCR_URL}/v1/ocr/extract",
            files={'file': (filename, file_content)},
            timeout=OCR_TIMEOUT
        )
        response.raise_for_status()
        return response.json()
    except requests.Timeout:
        raise Exception("OCR service timeout")
    except requests.RequestException as e:
        raise Exception(f"OCR service error: {e}")
```

---

## 9. Checklist

### Deployment

- [ ] OCR container running
- [ ] Health endpoint responding
- [ ] Network connectivity from Odoo
- [ ] Environment variables set
- [ ] Logging configured

### Verification

- [ ] Smoke test with sample document
- [ ] Field extraction working
- [ ] Confidence scores reasonable
- [ ] Error handling graceful

### Production

- [ ] Monitoring alerts configured
- [ ] Log rotation enabled
- [ ] Resource limits set
- [ ] Backup strategy (Odoo data, not OCR)

---

*Last updated: 2026-01-08*
