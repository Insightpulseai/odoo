---
name: azure-ai-engineer
description: >
  Azure AI Engineer Associate (AI-102) grounded skill. Covers AI solution planning,
  Document Intelligence, Azure AI Search, Azure OpenAI/Foundry integration, custom vision,
  NLP pipelines, and conversational AI. Use when building or reviewing AI service integrations.
  Triggers on: AI-102, AI Search, Document Intelligence, Foundry SDK, semantic search,
  vector search, RAG, custom models, AI pipeline, knowledge mining.
version: "1.0.0"
updated: "2026-04-18"
scope: repo
certification_source: "AI-102: Microsoft Azure AI Engineer Associate"
learn_path: "https://learn.microsoft.com/en-us/credentials/certifications/azure-ai-engineer/"
feeds_scoring: "Solutions Partner Data & AI — Skilling metric (+4 pts)"
---

# Azure AI Engineer Associate (AI-102) — Agent Skill

You are grounded in the AI-102 certification knowledge domain. Use `mcp__microsoft-learn__microsoft_docs_search` and `mcp__microsoft-learn__microsoft_docs_fetch` for real-time grounding.

## When to activate

- Building or reviewing AI Search indexes (`srch-ipai-dev-sea`)
- Working with Document Intelligence models (`docai-ipai-dev`)
- Integrating Foundry/OpenAI APIs (`ipai-copilot-resource`)
- Designing RAG pipelines or knowledge mining
- Building custom AI solutions with Azure AI Services SDK

## Knowledge domains (AI-102 exam skills)

### 1. Plan and manage an AI solution (15-20%)
- Select appropriate Azure AI services for a solution
- Plan and configure security (MI auth, Key Vault, network isolation)
- Create and manage an AI resource (Foundry resource, project)

**IPAI mapping:**
```
ipai-copilot-resource  →  Foundry resource (EUS2, S0)
  └── ipai-copilot     →  Foundry project (Failed provisioning — retry via portal)
docai-ipai-dev         →  Document Intelligence (SEA)
srch-ipai-dev-sea      →  AI Search with PE (SEA)
Auth: DefaultAzureCredential → id-ipai-dev MI
Secrets: kv-ipai-dev-sea (PE-only access)
```

### 2. Implement Document Intelligence solutions (10-15%)
- Analyze documents with prebuilt models
- Build custom extraction models
- Implement form processing pipelines

**IPAI implementation:**
- `ipai_doc_intel` Odoo module — prebuilt-invoice model (26 fields, 89-97% confidence)
- Custom TBWA models planned (CA form + Expense Report) — R3-S11
- SDK: `azure-ai-formrecognizer` → `azure-ai-documentintelligence`

### 3. Implement Azure AI Search solutions (15-20%)
- Create and manage search indexes
- Implement semantic ranking and vector search
- Build knowledge mining pipelines with skillsets

**IPAI implementation:**
- `srch-ipai-dev-sea` with private endpoint
- Foundry IQ uses AI Search for citation-backed grounding
- Vector search for Pulser knowledge base (planned R2)

### 4. Implement Azure OpenAI / Foundry solutions (15-20%)
- Deploy and manage model deployments
- Implement chat completions and embeddings
- Use Responses API (Agents v2)
- Implement RAG patterns

**IPAI implementation:**
```python
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential

client = AIProjectClient(
    endpoint="https://ipai-foundry-sea.services.ai.azure.com/api/projects/ipai-copilot",
    credential=DefaultAzureCredential(),
)
# Responses API for agent interactions
agent = client.agents.create_agent(model="gpt-4.1-mini", ...)
```

### 5. Implement NLP solutions (15-20%)
- Analyze text (sentiment, entities, key phrases, PII)
- Build conversational language understanding models
- Implement custom text classification

**IPAI application:** Pulser NLP for finance — extract tax codes from invoices, classify BIR form types, generate plain-language close summaries.

### 6. Implement knowledge mining and cognitive search (10-15%)
- Design skillset pipelines
- Implement incremental enrichment
- Build custom skills

**IPAI application:** Odoo data → AI Search index → Foundry IQ grounding → Pulser citation-backed responses.

## Grounding rule

Before answering any AI-102 domain question:
```
mcp__microsoft-learn__microsoft_docs_search(query="<topic> Azure AI engineer")
```

For implementation details, follow up with:
```
mcp__microsoft-learn__microsoft_docs_fetch(url="<specific doc URL from search>")
```

Then apply IPAI-specific context (resource names, endpoints, auth patterns).
