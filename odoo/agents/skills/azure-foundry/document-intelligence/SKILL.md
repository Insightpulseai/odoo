# Skill: Azure Document Intelligence

## Metadata

| Field | Value |
|-------|-------|
| **id** | `azure-document-intelligence` |
| **domain** | `azure_foundry` |
| **source** | https://learn.microsoft.com/en-us/azure/ai-services/document-intelligence/?view=doc-intel-4.0.0 |
| **extracted** | 2026-03-15 |
| **applies_to** | agents, infra, odoo |
| **tags** | ocr, document-intelligence, invoice, receipt, layout, containers, form-recognizer |

---

## What It Is

Cloud-based AI service (Foundry Tool) that uses ML models to extract text, key-value pairs, tables, and structure from documents. API version 4.0.0 (latest). Previously called "Azure Form Recognizer".

## IPAI Resource

| Field | Value |
|-------|-------|
| Resource name | `docai-ipai-dev` |
| Resource group | `rg-ipai-ai-dev` |
| Region | Southeast Asia |
| Endpoint | Via Azure Key Vault reference |

## Prebuilt Models

| Model | What It Extracts | IPAI Use Case |
|-------|-----------------|---------------|
| **Read** | Text, language, handwriting | General document text extraction |
| **Layout** | Text, tables, figures, structure, selection marks | Document structure for RAG indexing |
| **Invoice** | Vendor, dates, line items, amounts, tax | **Expense processing → Odoo** |
| **Receipt** | Merchant, date, items, totals, tax | **Receipt capture → Odoo expense** |
| **ID Document** | Name, DOB, address, ID number | Employee onboarding |
| **Business Card** | Name, company, phone, email | Contact import to Odoo |
| **W-2 / 1099** | US tax forms | Not applicable (Philippines) |
| **Health Insurance** | Insurance card fields | Not applicable |

### Philippines-Relevant Models

| Model | Use Case |
|-------|----------|
| **Invoice** | BIR tax compliance — extract vendor TIN, amounts, VAT |
| **Receipt** | Expense liquidation — extract amounts for reimbursement |
| **Layout** | BIR form processing — extract table structures |
| **Custom** | BIR 2307 / 2316 / 1601-C form extraction |

## Custom Models

| Type | Description | Use Case |
|------|-------------|----------|
| **Custom extraction** | Train on your document types with labeled data | BIR tax forms |
| **Custom classification** | Classify document types before extraction | Route invoices vs receipts vs BIR forms |
| **Composed models** | Combine multiple custom models | Full document processing pipeline |

## Container Deployment

Document Intelligence containers run on-premises or in your own cloud. **Relevant for IPAI** — can deploy alongside Odoo in ACA.

### Supported Container Models (v4.0)

| Container | Docker Image | Use Case |
|-----------|-------------|----------|
| **Layout** | `mcr.microsoft.com/azure-cognitive-services/form-recognizer/layout-4.0` | Document structure extraction |
| **Invoice** | `mcr.microsoft.com/azure-cognitive-services/form-recognizer/invoice-4.0` | Invoice data extraction |
| **Receipt** | `mcr.microsoft.com/azure-cognitive-services/form-recognizer/receipt-4.0` | Receipt data extraction |
| **ID Document** | `mcr.microsoft.com/azure-cognitive-services/form-recognizer/id-document-4.0` | ID extraction |
| **Read** | `mcr.microsoft.com/azure-cognitive-services/form-recognizer/read-4.0` | Text extraction |
| **Custom** | `mcr.microsoft.com/azure-cognitive-services/form-recognizer/custom-4.0` | Custom trained models |

### Docker Run Example

```bash
docker run --rm -it -p 5000:5000 \
  --memory 8g --cpus 4 \
  -e Eula=accept \
  -e Billing={ENDPOINT_URI} \
  -e ApiKey={API_KEY} \
  -v /path/to/output:/output \
  -v /path/to/input:/input \
  mcr.microsoft.com/azure-cognitive-services/form-recognizer/layout-4.0
```

### Container Requirements

| Resource | Minimum | Recommended |
|----------|---------|-------------|
| CPU | 4 cores | 8 cores |
| Memory | 8 GB | 16 GB |
| Storage | 10 GB | Depends on volume |

### Key Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `Eula` | Yes | Must be `accept` |
| `Billing` | Yes | Endpoint URI from Azure portal |
| `ApiKey` | Yes | API key from Azure portal |

**Note**: Containers require internet for billing. They do NOT work fully offline — billing telemetry must reach Azure.

## RAG Integration

Document Intelligence supports **Retrieval-Augmented Generation** — extract structured content from documents and feed into vector stores for RAG pipelines.

```
Source Documents (PDF, DOCX, images)
    ↓
Document Intelligence (Layout model)
    ↓ structured markdown/JSON
Chunking + Embedding
    ↓
Azure AI Search (vector index)
    ↓
Foundry Agent (RAG retrieval)
```

## IPAI Integration Map

| Current | Target | Action |
|---------|--------|--------|
| PaddleOCR (`ipai-ocr-dev` ACA) | Document Intelligence (`docai-ipai-dev`) | Migrate OCR workload |
| Manual invoice entry | Invoice model → Odoo `account.move` | Automate via n8n |
| Manual receipt entry | Receipt model → Odoo `hr.expense` | Automate via n8n |
| No BIR form extraction | Custom model trained on BIR 2307/2316 | Build custom model |
| Cloud-only OCR | Container in ACA (alongside Odoo) | Deploy for latency + cost |

### Migration Path (PaddleOCR → Document Intelligence)

1. **Keep PaddleOCR** for general text extraction (free, no billing)
2. **Add Document Intelligence** for structured extraction (invoices, receipts, BIR forms)
3. **Route by document type**: Classification model → route to correct extractor
4. **Deploy container** in ACA for predictable latency (same VNet as Odoo)
5. **Wire to n8n**: OCR webhook → DI container → structured JSON → Odoo create

### Pricing Consideration

| Tier | Price | Notes |
|------|-------|-------|
| Free | 500 pages/month | Sufficient for dev/testing |
| S0 | $1.50 per 1000 pages | Production volume |
| Container | Same as S0 (billing required) | Self-hosted, lower latency |

For IPAI's volume (~1000 invoices/month), S0 tier = ~$1.50/month. Container deployment justified by latency and VNet isolation, not cost.
