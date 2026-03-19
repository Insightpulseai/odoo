# Skill: LandingAI Agentic Document Extraction (ADE)

## Metadata

| Field | Value |
|-------|-------|
| **id** | `landing-ai-ade` |
| **domain** | `inference` |
| **source** | https://github.com/landing-ai/ade-python |
| **extracted** | 2026-03-15 |
| **applies_to** | agents, odoo, automations |
| **tags** | ocr, document-extraction, agentic, invoice, receipt, schema-extraction, mcp |
| **secrets_required** | `VISION_AGENT_API_KEY` |

---

## What It Is

Agentic Document Extraction (ADE) by LandingAI (Andrew Ng). Python SDK for document parsing, splitting/classification, and schema-based structured data extraction. 2,385+ stars (legacy repo) + 617 stars (current SDK). Production-grade with async support, retries, type safety.

**Key differentiator vs Azure Document Intelligence**: ADE uses an agentic approach — the model reasons about document structure rather than relying on fixed prebuilt templates. More flexible for novel document types without custom training.

## GitHub Repos

| Repo | Stars | Purpose |
|------|-------|---------|
| `landing-ai/ade-python` | 617 | Python SDK (current) |
| `landing-ai/agentic-doc` | 2,385 | Legacy Python library |
| `landing-ai/ade-typescript` | 28 | TypeScript SDK |
| `landing-ai/ade-document-processing-skills` | 1 | Agent skills for ADE |
| `landing-ai/ade-helper-scripts` | 38 | Sample notebooks |
| `landing-ai/ade-fintech` | 1 | Financial services examples |
| `landing-ai/vision-agent-mcp` | 27 | MCP server (deprecated → use ADE) |

## Core Operations

### 1. Parse — Document → Markdown

Converts any document to markdown with semantic chunking. Preserves layout, tables, figures.

```python
from pathlib import Path
from landingai_ade import LandingAIADE

client = LandingAIADE(apikey="your-api-key")

response = client.parse(
    document=Path("invoice.pdf"),
    model="dpt-2-latest",
    save_to="./output"
)
print(response.markdown)  # Structured markdown
print(response.chunks)    # Semantic chunks for RAG
```

### 2. Split — Classify Document Segments

Classifies pages/sections within a multi-document file.

```python
import json

split_classes = [
    {"name": "Invoice", "description": "Vendor billing document with line items"},
    {"name": "Receipt", "description": "Point-of-sale transaction record"},
    {"name": "BIR Form", "description": "Philippine tax compliance form", "identifier": "BIR Form Number"},
]

split_response = client.split(
    split_class=json.dumps(split_classes),
    markdown=parse_response.markdown,
    model="split-latest",
)

for split in split_response.splits:
    print(f"{split.classification}: pages {split.page_range}")
```

### 3. Extract — Schema-Based Structured Extraction

Pull typed data from parsed documents using Pydantic schemas.

```python
from pydantic import BaseModel, Field
from landingai_ade.lib import pydantic_to_json_schema

class InvoiceData(BaseModel):
    vendor_name: str = Field(description="Name of the vendor/supplier")
    vendor_tin: str = Field(description="Tax Identification Number")
    invoice_number: str = Field(description="Invoice reference number")
    date: str = Field(description="Invoice date")
    line_items: list[dict] = Field(description="List of items with description, qty, unit_price, amount")
    subtotal: float = Field(description="Subtotal before tax")
    vat_amount: float = Field(description="VAT/tax amount")
    total: float = Field(description="Total amount due")

schema = pydantic_to_json_schema(InvoiceData)
response = client.extract(
    schema=schema,
    markdown=parse_response.markdown,
    save_to="./extracted"
)
```

### 4. Parse Jobs — Async for Large Documents

Process large files (up to 1 GB / 6,000 pages) asynchronously.

```python
job = client.parse_jobs.create(
    document=Path("large_batch.pdf"),
    model="dpt-2-latest",
)

# Poll for completion
status = client.parse_jobs.get(job.job_id)
print(f"Status: {status.status}")

# List completed jobs
jobs = client.parse_jobs.list(status="completed", page=0, page_size=10)
```

## Agent Skills (from ade-document-processing-skills)

| Skill | Description |
|-------|-------------|
| **document-extraction** | Parse → extract with schema, split/classify batches, visual grounding with bounding boxes |
| **document-workflows** | Batch processing, classify-then-extract pipelines, RAG prep, DataFrame/CSV/Snowflake export, Streamlit UI |

## Supported Formats

20+ file types: PDF, PNG, JPG, TIFF, BMP, HEIF, DOCX, XLSX, PPTX, and more.

## Install

```bash
pip install landingai-ade
# For async aiohttp support:
pip install landingai-ade[aiohttp]
```

## Async Client

```python
from landingai_ade import AsyncLandingAIADE
import asyncio

client = AsyncLandingAIADE()

async def process():
    response = await client.parse(
        document=Path("document.pdf"),
        model="dpt-2-latest",
    )
    return response.chunks

asyncio.run(process())
```

## Error Handling

| Status | Exception |
|--------|-----------|
| 400 | `BadRequestError` |
| 401 | `AuthenticationError` |
| 403 | `PermissionDeniedError` |
| 404 | `NotFoundError` |
| 422 | `UnprocessableEntityError` |
| 429 | `RateLimitError` |
| 500+ | `InternalServerError` |

Built-in retries (default: 2) with exponential backoff. Timeout: 8 minutes default.

## MCP Server

ADE includes an MCP server for AI assistant integration (Cursor, VS Code). Enables document processing directly from coding environments.

## ADE vs Azure Document Intelligence

| Feature | ADE (LandingAI) | Azure Doc Intelligence |
|---------|-----------------|----------------------|
| Approach | Agentic (LLM-driven reasoning) | Template-based (prebuilt models) |
| Custom schemas | Pydantic → JSON schema (any structure) | Fixed prebuilt fields or custom training |
| Novel document types | Works without training | Requires custom model training |
| Prebuilt models | None (universal parser) | 30+ (invoice, receipt, tax, mortgage) |
| BIR form support | Via schema definition (no training) | Requires custom model training |
| Container deployment | Cloud API only | Docker containers available |
| Pricing | API-based (per page) | $1.50/1000 pages (S0) |
| Offline capability | No | Container with billing endpoint |
| Visual grounding | Bounding boxes + confidence | Bounding boxes + confidence |
| RAG integration | Built-in semantic chunking | Layout → chunking (manual) |
| Async processing | Native (up to 6,000 pages) | Batch API |

## IPAI Integration Strategy

**Use both — complementary, not competing**:

| Document Type | Best Tool | Why |
|---------------|-----------|-----|
| **BIR tax forms** (2307, 2316, 1601-C) | ADE | No training needed — define schema, extract |
| **Standard invoices** | Azure DI prebuilt | Proven prebuilt model, lower cost |
| **Standard receipts** | Azure DI prebuilt | Proven prebuilt model |
| **Mixed/novel documents** | ADE | Agentic approach handles unseen formats |
| **High-volume batch** | Azure DI container | On-prem, predictable latency |
| **RAG document ingestion** | ADE | Built-in semantic chunking |

### Pipeline Architecture

```
Document Upload (Odoo / n8n webhook)
    ↓
Classification Agent (ADE split)
    ├── Invoice → Azure DI prebuilt-invoice → Odoo account.move
    ├── Receipt → Azure DI prebuilt-receipt → Odoo hr.expense
    ├── BIR Form → ADE extract (Pydantic schema) → Odoo tax record
    └── Unknown → ADE parse + extract (flexible schema) → review queue
```

### n8n Workflow

```
1. Webhook receives document upload
2. ADE split → classify document type
3. Route to appropriate extractor:
   - Known types → Azure DI prebuilt
   - Novel types → ADE schema extraction
4. Structured JSON → Odoo XML-RPC create
5. Result → ops.run_events (Supabase SSOT)
6. Notify via Slack
```

### Secrets

```bash
# Add to Azure Key Vault (kv-ipai-dev)
VISION_AGENT_API_KEY=<landing-ai-api-key>
```
