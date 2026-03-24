---
name: azure-document-intelligence
description: "Azure Document Intelligence skill — Extract structured data from documents using prebuilt and custom models. Produces integration code, entity contracts, and verification artifacts."
microsoft_capability_family: "Azure / AI / Document Intelligence"
---

# Azure Document Intelligence Skill

You are executing the Azure Document Intelligence Skill.

## Objective

Implement document extraction pipelines using Azure Document Intelligence (formerly Form Recognizer). Produce working integration code, SSOT entity contracts, and verification evidence.

## Triggers

- "extract PDF", "analyze document", "OCR invoice"
- "read receipt", "process tax form", "document intelligence"
- "form recognizer", "PDF extraction", "batch document analysis"
- "custom model training", "document classification"

## Required Outputs

1. **Integration code**: Python module or API client for the target model
2. **Entity contract**: YAML entity definition for extracted fields (in `ssot/` if new domain)
3. **Verification**: Endpoint connectivity test + sample extraction proof

## Execution Procedure

### Phase 1: Model Selection

Identify the correct prebuilt or custom model:

| Document Type | Model ID |
|---------------|----------|
| General OCR | `prebuilt-read` |
| Tables/structure | `prebuilt-layout` |
| Invoices | `prebuilt-invoice` |
| Receipts | `prebuilt-receipt` |
| ID documents | `prebuilt-idDocument` |
| W-2 tax forms | `prebuilt-tax.us.w2` |
| Bank statements | `prebuilt-bankStatement` |
| Contracts | `prebuilt-contract` |
| Custom forms | Train via Studio or API |

### Phase 2: Implementation

```python
import os
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.core.credentials import AzureKeyCredential

endpoint = os.getenv("AZURE_DI_ENDPOINT")
key = os.getenv("AZURE_DI_KEY")
if not endpoint or not key:
    raise ValueError("AZURE_DI_ENDPOINT and AZURE_DI_KEY not set in environment")

client = DocumentIntelligenceClient(endpoint, AzureKeyCredential(key))
```

### Phase 3: Verification

```bash
# Endpoint health
curl -s -o /dev/null -w "%{http_code}" \
  "${AZURE_DI_ENDPOINT}/documentintelligence/info?api-version=2024-11-30" \
  -H "Ocp-Apim-Subscription-Key: ${AZURE_DI_KEY}"
```

## Guardrails

- Never hardcode API keys — use `os.getenv()` exclusively
- Never log document content in CI — PII risk
- Use managed identity (`DefaultAzureCredential`) in production
- Container deployments require `Eula=accept` + billing endpoint
- Batch jobs must use SAS-scoped blob URLs, not account keys
