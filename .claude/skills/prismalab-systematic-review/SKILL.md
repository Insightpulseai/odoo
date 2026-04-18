---
name: prismalab-systematic-review
description: Conduct PRISMA 2020-compliant systematic reviews using Azure AI services. Covers protocol development, search strategy, screening, and reporting.
---

# PrismaLab Systematic Review Skill

## When to Use
- User asks to plan or conduct a systematic review
- User needs a search strategy for databases (PubMed, Cochrane, Embase)
- User needs PRISMA 2020 checklist compliance
- User asks about inclusion/exclusion criteria

## Azure Services Used
- **Azure AI Foundry** (`ipai-copilot-resource`): GPT-4.1 for protocol drafting, search strategy generation
- **Azure AI Search** (`srch-ipai-dev-sea`, index: `prismalab-rag-v1`): RAG over methodology corpus
- **PubMed MCP** (via Claude.ai connector): Live database searching

## Workflow

### Step 1: Protocol Development
Generate a PROSPERO-ready protocol from a research question:
```
Input: "What is the effectiveness of AI-assisted diagnosis in diabetic retinopathy?"
Output: Structured protocol with PICO, objectives, search strategy, eligibility criteria
```

### Step 2: Search Strategy
Generate database-specific search strings:
```python
# PubMed search string generation
search = {
    "population": "diabetic retinopathy patients",
    "intervention": "artificial intelligence OR deep learning OR machine learning",
    "comparator": "ophthalmologist OR human expert",
    "outcome": "diagnostic accuracy OR sensitivity OR specificity",
    "filters": ["humans", "english", "2019-2026"]
}
```

Use Boolean operators adapted per database:
- PubMed: MeSH terms + free text with [tiab]
- Cochrane: MeSH + explosion
- Embase: Emtree terms

### Step 3: Screening
Two-phase screening approach:
1. **Title/Abstract screening**: Use GPT-4.1 to pre-classify relevance (human confirms)
2. **Full-text screening**: Azure Document Intelligence extracts text from PDFs, GPT-4.1 assesses eligibility

### Step 4: PRISMA Flow Diagram
Generate the PRISMA 2020 flow diagram data:
```
Records identified (n=X)
  → Duplicates removed (n=X)
  → Screened (n=X)
    → Excluded (n=X)
  → Full-text assessed (n=X)
    → Excluded with reasons (n=X)
  → Included in synthesis (n=X)
    → Quantitative synthesis (n=X)
```

## Quality Standards
- Always register protocol in PROSPERO before screening
- Minimum two independent reviewers for screening (AI can be one, human must be other)
- Report inter-rater reliability (Cohen's kappa)
- Follow PRISMA 2020 27-item checklist
- Declare AI assistance in methods section

## Limitations
- AI screening is assistive, not authoritative
- Always validate AI-generated search strategies with a librarian
- Full-text PDFs require publisher access (not all are open access)
