---
name: prismalab-evidence-extraction
description: Extract structured data from research papers using Azure Document Intelligence and GPT-4.1 vision. Automates PICO extraction, risk of bias assessment, and data table population.
---

# PrismaLab Evidence Extraction Skill

## When to Use
- User needs to extract data from included studies (PDFs)
- User needs PICO elements extracted from abstracts/full text
- User needs risk of bias assessment (RoB 2, ROBINS-I, Newcastle-Ottawa)
- User needs to populate data extraction forms

## Azure Services Used
- **Document Intelligence** (`docai-ipai-dev`): PDF text/table extraction (prebuilt-read, prebuilt-layout)
- **Azure AI Foundry** (`ipai-copilot-resource`): GPT-4.1 for structured extraction + GPT-4.1 vision for figures/tables
- **Azure AI Search** (`srch-ipai-dev-sea`): RAG for methodology guidance

## Extraction Pipeline

### Step 1: PDF Ingestion
```python
# Azure Document Intelligence — extract text + tables from study PDF
from azure.ai.documentintelligence import DocumentIntelligenceClient

client = DocumentIntelligenceClient(
    endpoint="https://docai-ipai-dev.cognitiveservices.azure.com",
    credential=DefaultAzureCredential()
)

poller = client.begin_analyze_document(
    "prebuilt-layout",
    document=pdf_bytes,
    output_content_format="markdown"
)
result = poller.result()
# result.content = full markdown with tables preserved
```

### Step 2: PICO Extraction
```python
# GPT-4.1 structured extraction
extraction_prompt = """
Extract the following from this study:

1. Population: age, sex, condition, setting, sample size per arm
2. Intervention: type, dose/intensity, duration, frequency
3. Comparator: type, description
4. Outcomes: primary outcome(s), secondary outcome(s), measurement tools, timepoints
5. Study design: RCT/cohort/case-control/cross-sectional
6. Follow-up duration
7. Funding source
8. Country/setting

Return as structured JSON.
"""
```

### Step 3: Numerical Data Extraction
For meta-analysis input, extract:
```json
{
  "study_id": "Smith2024",
  "outcome": "HbA1c reduction",
  "intervention": {"n": 150, "mean": -1.2, "sd": 0.8},
  "control": {"n": 148, "mean": -0.4, "sd": 0.7},
  "timepoint_weeks": 24
}
```

For dichotomous outcomes:
```json
{
  "study_id": "Jones2023",
  "outcome": "Complete remission",
  "intervention": {"events": 45, "total": 120},
  "control": {"events": 28, "total": 118}
}
```

### Step 4: Risk of Bias Assessment
Use GPT-4.1 to pre-assess, human confirms:

**RoB 2 (for RCTs):**
| Domain | Assessment | Support |
|--------|-----------|---------|
| Randomization | Low/High/Some concerns | Quote from paper |
| Deviations from intervention | Low/High/Some concerns | Quote |
| Missing outcome data | Low/High/Some concerns | Quote |
| Outcome measurement | Low/High/Some concerns | Quote |
| Selection of reported result | Low/High/Some concerns | Quote |

**ROBINS-I (for non-randomized):**
Domains: confounding, selection, classification, deviations, missing data, measurement, reported result

### Step 5: Figure/Table Extraction (GPT-4.1 Vision)
```python
# For studies where key data is in figures (e.g., Kaplan-Meier curves)
response = client.chat.completions.create(
    model="gpt-4.1",
    messages=[{
        "role": "user",
        "content": [
            {"type": "text", "text": "Extract the survival rates at 6, 12, and 24 months from this Kaplan-Meier curve. Return as JSON."},
            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image}"}}
        ]
    }]
)
```

## Quality Standards
- All AI-extracted data must be verified by a human reviewer
- Double extraction recommended (AI + human, or two humans)
- Report extraction agreement rate
- Flag uncertain extractions for manual review
- Preserve source quotes for traceability
