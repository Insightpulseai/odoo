---
name: azure-document-intelligence
description: "Azure Document Intelligence (formerly Form Recognizer) specialist. Extract structured data from PDFs, invoices, receipts, ID documents, tax forms, and custom documents using prebuilt and custom models. Actions: analyze, extract, classify, train, batch. Triggers: 'extract PDF', 'analyze document', 'OCR invoice', 'read receipt', 'process tax form', 'document intelligence', 'form recognizer', 'PDF extraction', 'batch document analysis'."
version: "1.0.0"
tags: [azure, document-intelligence, pdf, ocr, form-recognizer, invoices, receipts, tax-forms, custom-models]
allowed-tools: [Bash, Read, Write, Edit, Glob, Grep]
---

# Azure Document Intelligence

Specialist skill for extracting structured data from documents using Azure Document Intelligence (formerly Azure Form Recognizer). Covers prebuilt models, custom models, layout analysis, and batch processing.

## When to Use This Skill

- Extracting structured data from PDFs, images, or scanned documents
- Processing invoices, receipts, ID documents, or tax forms
- Building custom document extraction models (template or neural)
- Classifying documents by type before extraction
- Running batch analysis on large document sets
- Implementing RAG pipelines with document chunking
- Generating searchable PDFs from scanned images

## How to Use (Prompt Patterns)

- "Extract invoice fields from this PDF using Document Intelligence"
- "Set up a custom neural model for contract extraction"
- "Classify incoming documents by type (invoice, receipt, contract)"
- "Process a batch of W-2 tax forms and extract employee data"
- "Analyze document layout and extract tables"
- "Build a RAG pipeline with Document Intelligence for PDF chunking"

---

## Service Overview

**Azure Document Intelligence** is a cloud-based AI service that uses ML to extract text, key-value pairs, tables, and structures from documents.

- **API versions**: v4.0 (2024-11-30 GA), v3.1 (2023-07-31 GA)
- **Endpoint pattern**: `https://{endpoint}/documentintelligence/documentModels/{modelId}:analyze?api-version=2024-11-30`
- **SDKs**: Python, .NET/C#, Java, JavaScript/TypeScript
- **Studio**: https://documentintelligence.ai.azure.com/studio

---

## Prebuilt Models Reference

### Document Analysis Models

| Model ID | Purpose | Key Fields |
|----------|---------|------------|
| `prebuilt-read` | OCR — text extraction, language detection | pages, words, lines, languages |
| `prebuilt-layout` | Tables, figures, sections, structure | tables, paragraphs, figures, sections |
| `prebuilt-document` | General key-value pairs + structure | key_value_pairs, entities, tables |

### Financial Models

| Model ID | Purpose | Key Fields |
|----------|---------|------------|
| `prebuilt-invoice` | Invoices (AR/AP) | vendor_name, invoice_total, line_items, due_date, purchase_order |
| `prebuilt-receipt` | Receipts (retail, meal, etc.) | merchant_name, total, items, transaction_date, tip |
| `prebuilt-bankStatement` | Bank statements | account_number, transactions, beginning_balance, ending_balance |
| `prebuilt-check` | Checks | payee, amount, date, memo, routing_number |
| `prebuilt-payStub` | Pay stubs | employee_name, gross_pay, net_pay, deductions, pay_period |
| `prebuilt-creditCard` | Credit card statements | card_holder, transactions, statement_balance |

### Tax Form Models

| Model ID | Purpose | Key Fields |
|----------|---------|------------|
| `prebuilt-tax.us.w2` | W-2 Wage and Tax | employee, employer, wages_tips, federal_tax_withheld |
| `prebuilt-tax.us.1040` | Form 1040 | filing_status, adjusted_gross_income, total_tax |
| `prebuilt-tax.us.1098` | Mortgage Interest | lender, borrower, mortgage_interest_received |
| `prebuilt-tax.us.1099` | 1099 variants (NEC, MISC, etc.) | payer, recipient, nonemployee_compensation |
| `prebuilt-tax.us.1095` | Health coverage | covered_individuals, months_covered |

### Identity Models

| Model ID | Purpose | Key Fields |
|----------|---------|------------|
| `prebuilt-idDocument` | ID cards, passports, driver licenses | first_name, last_name, date_of_birth, document_number, expiration_date |
| `prebuilt-healthInsuranceCard.us` | US health insurance cards | member_id, group_number, plan_name, copays |
| `prebuilt-marriageCertificate.us` | Marriage certificates | spouse_names, date_of_marriage, county |

### Contract Model

| Model ID | Purpose | Key Fields |
|----------|---------|------------|
| `prebuilt-contract` | Contracts and agreements | parties, execution_date, renewal_date, jurisdiction, terms |

---

## Custom Models

### Model Types

| Type | Best For | Training Data | Accuracy |
|------|----------|---------------|----------|
| **Template** | Fixed-layout forms (government, standardized) | 5+ labeled samples | High for fixed layouts |
| **Neural** | Variable-layout documents (invoices from different vendors) | 5+ labeled samples | High across layouts |
| **Composed** | Multi-form routing (auto-selects sub-model) | Component models | Depends on components |
| **Classification** | Document type routing before extraction | 5+ samples per class | High |

### Training Workflow

```bash
# 1. Upload training data to Azure Blob Storage
az storage blob upload-batch \
  --destination training-data \
  --source ./training-documents/ \
  --account-name $STORAGE_ACCOUNT

# 2. Label documents in Document Intelligence Studio
#    https://documentintelligence.ai.azure.com/studio

# 3. Train model via API
curl -X POST "${ENDPOINT}/documentintelligence/documentModels:build?api-version=2024-11-30" \
  -H "Ocp-Apim-Subscription-Key: ${DI_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "modelId": "custom-contract-v1",
    "buildMode": "neural",
    "azureBlobSource": {
      "containerUrl": "https://${STORAGE_ACCOUNT}.blob.core.windows.net/training-data?${SAS_TOKEN}"
    }
  }'
```

---

## API Integration Patterns

### Python SDK (Recommended)

```python
import os
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.core.credentials import AzureKeyCredential

endpoint = os.getenv("AZURE_DI_ENDPOINT")
key = os.getenv("AZURE_DI_KEY")

client = DocumentIntelligenceClient(endpoint, AzureKeyCredential(key))

# Analyze invoice
with open("invoice.pdf", "rb") as f:
    poller = client.begin_analyze_document("prebuilt-invoice", body=f)
    result = poller.result()

for doc in result.documents:
    vendor = doc.fields.get("VendorName")
    total = doc.fields.get("InvoiceTotal")
    print(f"Vendor: {vendor.content}, Total: {total.content}")
```

### REST API

```bash
# Submit document for analysis
curl -X POST "${ENDPOINT}/documentintelligence/documentModels/prebuilt-invoice:analyze?api-version=2024-11-30" \
  -H "Ocp-Apim-Subscription-Key: ${DI_KEY}" \
  -H "Content-Type: application/pdf" \
  --data-binary @invoice.pdf

# Poll for results (use Operation-Location header from response)
curl -X GET "${OPERATION_LOCATION}" \
  -H "Ocp-Apim-Subscription-Key: ${DI_KEY}"
```

### Batch Analysis

```bash
# Submit batch job
curl -X POST "${ENDPOINT}/documentintelligence/documentModels/prebuilt-invoice:analyzeBatch?api-version=2024-11-30" \
  -H "Ocp-Apim-Subscription-Key: ${DI_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "azureBlobSource": {
      "containerUrl": "https://${STORAGE}.blob.core.windows.net/invoices?${SAS}"
    },
    "resultContainerUrl": "https://${STORAGE}.blob.core.windows.net/results?${SAS}",
    "resultPrefix": "batch-output/"
  }'
```

---

## Add-On Capabilities

| Capability | Feature Flag | Description |
|------------|-------------|-------------|
| High resolution | `analyzeResult.pages[].highResolution` | 300 DPI processing for small text |
| Formulas | `features: ["formulas"]` | LaTeX extraction from math content |
| Font/style | `features: ["styleFont"]` | Font name, size, weight, color |
| Barcodes | `features: ["barcodes"]` | 1D/2D barcode extraction |
| Language detection | `features: ["languages"]` | Per-span language identification |
| Query fields | `features: ["queryFields"]` | LLM-powered custom field extraction |
| Searchable PDF | `outputContentFormat: "pdf"` | Generate searchable PDF from scan |
| Markdown output | `outputContentFormat: "markdown"` | Markdown-formatted extraction |

### Query Fields Example

```python
poller = client.begin_analyze_document(
    "prebuilt-layout",
    body=document,
    features=["queryFields"],
    query_fields=["PurchaseOrderNumber", "ShipToAddress", "PaymentTerms"]
)
```

---

## Odoo Integration Pattern

For Odoo CE expense/invoice automation using Document Intelligence:

```python
# ipai_document_intelligence/models/document_processor.py
class DocumentProcessor(models.Model):
    _name = "ipai.document.processor"
    _description = "Azure Document Intelligence Processor"

    name = fields.Char(required=True)
    model_id = fields.Selection([
        ('prebuilt-invoice', 'Invoice'),
        ('prebuilt-receipt', 'Receipt'),
        ('prebuilt-idDocument', 'ID Document'),
        ('prebuilt-tax.us.w2', 'W-2 Form'),
        ('custom', 'Custom Model'),
    ], required=True)
    custom_model_id = fields.Char()

    def process_attachment(self, attachment):
        """Extract structured data from Odoo ir.attachment."""
        endpoint = os.getenv("AZURE_DI_ENDPOINT")
        key = os.getenv("AZURE_DI_KEY")
        if not endpoint or not key:
            raise ValueError("AZURE_DI_ENDPOINT and AZURE_DI_KEY not set in environment")

        client = DocumentIntelligenceClient(endpoint, AzureKeyCredential(key))
        model = self.custom_model_id if self.model_id == 'custom' else self.model_id

        poller = client.begin_analyze_document(model, body=attachment.raw)
        return poller.result()
```

---

## Container Deployment (Disconnected)

For air-gapped or on-premise deployments:

```yaml
# docker-compose.document-intelligence.yml
services:
  document-intelligence-read:
    image: mcr.microsoft.com/azure-cognitive-services/form-recognizer/read:latest
    ports:
      - "5000:5000"
    environment:
      - Eula=accept
      - Billing=${AZURE_DI_ENDPOINT}
      - ApiKey=${AZURE_DI_KEY}
    deploy:
      resources:
        limits:
          cpus: '8'
          memory: 8G

  document-intelligence-layout:
    image: mcr.microsoft.com/azure-cognitive-services/form-recognizer/layout:latest
    ports:
      - "5001:5000"
    environment:
      - Eula=accept
      - Billing=${AZURE_DI_ENDPOINT}
      - ApiKey=${AZURE_DI_KEY}
    deploy:
      resources:
        limits:
          cpus: '8'
          memory: 8G
```

---

## RAG Integration (Document Chunking)

Use Document Intelligence Layout model for intelligent document chunking in RAG pipelines:

```python
def chunk_document_for_rag(document_path, chunk_strategy="page"):
    """Chunk document using DI Layout for RAG ingestion."""
    client = DocumentIntelligenceClient(
        os.getenv("AZURE_DI_ENDPOINT"),
        AzureKeyCredential(os.getenv("AZURE_DI_KEY"))
    )

    with open(document_path, "rb") as f:
        poller = client.begin_analyze_document(
            "prebuilt-layout",
            body=f,
            output_content_format="markdown"
        )
        result = poller.result()

    chunks = []
    if chunk_strategy == "page":
        for page in result.pages:
            chunks.append({
                "page": page.page_number,
                "content": page.content,
                "tables": [t for t in (result.tables or []) if any(
                    r.bounding_regions[0].page_number == page.page_number
                    for r in t.cells if r.bounding_regions
                )]
            })
    elif chunk_strategy == "section":
        for section in (result.sections or []):
            chunks.append({
                "content": section.content,
                "elements": section.elements
            })

    return chunks
```

---

## Security & Compliance

- **Authentication**: Azure Key Credential or Azure AD (managed identity preferred)
- **Data residency**: Documents processed in the selected Azure region; no cross-region transfer
- **Encryption**: TLS 1.2+ in transit; AES-256 at rest; customer-managed keys (CMK) supported
- **Network**: Private endpoints and VNET integration available
- **Data retention**: Documents deleted after processing unless explicitly stored
- **Compliance**: SOC 2, ISO 27001, HIPAA BAA, FedRAMP High

### Managed Identity Pattern (Recommended)

```python
from azure.identity import DefaultAzureCredential

credential = DefaultAzureCredential()
client = DocumentIntelligenceClient(
    os.getenv("AZURE_DI_ENDPOINT"),
    credential
)
```

---

## Pricing Tiers

| Tier | Read | Prebuilt | Custom | Add-ons |
|------|------|----------|--------|---------|
| Free (F0) | 500 pages/mo | 500 pages/mo | 500 pages/mo | Not available |
| Standard (S0) | $0.001/page | $0.01/page | $0.05/page (neural) | $0.005/feature/page |

---

## Verification Commands

```bash
# Test endpoint connectivity
curl -s -o /dev/null -w "%{http_code}" \
  "${AZURE_DI_ENDPOINT}/documentintelligence/info?api-version=2024-11-30" \
  -H "Ocp-Apim-Subscription-Key: ${AZURE_DI_KEY}"

# List available models
curl -s "${AZURE_DI_ENDPOINT}/documentintelligence/documentModels?api-version=2024-11-30" \
  -H "Ocp-Apim-Subscription-Key: ${AZURE_DI_KEY}" | python3 -m json.tool

# Analyze test document
python3 -c "
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.core.credentials import AzureKeyCredential
import os
client = DocumentIntelligenceClient(os.getenv('AZURE_DI_ENDPOINT'), AzureKeyCredential(os.getenv('AZURE_DI_KEY')))
result = client.begin_analyze_document('prebuilt-read', body=open('test.pdf','rb')).result()
print(f'Pages: {len(result.pages)}, Words: {sum(len(p.words or []) for p in result.pages)}')
"
```
