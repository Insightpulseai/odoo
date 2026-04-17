---
name: azure-ai-fundamentals
description: >
  Azure AI Fundamentals (AI-900) grounded skill. Covers AI workloads, Azure AI Services,
  computer vision, NLP, generative AI, and Azure Machine Learning. Use when working with
  any Azure AI resource, evaluating AI service selection, or explaining AI concepts.
  Triggers on: AI-900, Azure AI, cognitive services, Foundry Tools, computer vision,
  NLP, generative AI, Azure ML, responsible AI.
version: "1.0.0"
updated: "2026-04-18"
scope: repo
certification_source: "AI-900: Microsoft Azure AI Fundamentals"
learn_path: "https://learn.microsoft.com/en-us/credentials/certifications/azure-ai-fundamentals/"
feeds_scoring: "Solutions Partner Data & AI — Skilling metric (+4 pts)"
---

# Azure AI Fundamentals (AI-900) — Agent Skill

You are grounded in the AI-900 certification knowledge domain. Use the `mcp__microsoft-learn__microsoft_docs_search` tool to fetch current Microsoft documentation before answering.

## When to activate

- User asks about Azure AI service selection or capabilities
- Working with `ipai-copilot-resource` (AIServices kind)
- Evaluating AI workload patterns (vision, NLP, generative, decision)
- Discussing responsible AI principles in Pulser agent design
- Comparing Azure AI Services vs Databricks serving endpoints

## Knowledge domains (AI-900 exam skills)

### 1. AI workloads and considerations (15-20%)
- Identify features of common AI workloads (anomaly detection, vision, NLP, generative)
- Identify guiding principles for responsible AI (fairness, reliability, privacy, inclusiveness, transparency, accountability)

**IPAI application:** Pulser's policy-gated model = responsible AI in practice. Mutating actions require approval = accountability + transparency.

### 2. Azure AI Services (25-30%)
- Identify Azure AI services (Vision, Speech, Language, Decision, Foundry)
- Identify capabilities of Azure AI Services for each workload type

**IPAI resources:**
| Service | IPAI Resource | Use |
|---|---|---|
| Azure AI Services | `ipai-copilot-resource` | Foundry inference (gpt-4.1-mini) |
| Document Intelligence | `docai-ipai-dev` | Invoice/receipt extraction |
| AI Search | `srch-ipai-dev-sea` | Semantic search + Foundry IQ grounding |

### 3. Computer Vision workloads (15-20%)
- Identify common types of computer vision solutions
- Identify Azure tools for vision (Custom Vision, Face, OCR)

**IPAI application:** Document Intelligence is a vision workload — OCR + layout extraction from invoices/forms.

### 4. NLP workloads (15-20%)
- Identify features of NLP workloads (key phrase extraction, entity recognition, sentiment, translation)
- Identify Azure tools for NLP

**IPAI application:** Pulser uses NLP for guided finance ops — plain-language summaries, blocker explanations, evidence request drafting.

### 5. Generative AI workloads (15-20%)
- Identify features of generative AI solutions
- Identify capabilities of Azure OpenAI Service (now Foundry)
- Identify responsible generative AI considerations

**IPAI application:** Pulser agents use Foundry (gpt-4.1-mini) for generative responses. Policy-gated: read-only tools approval-free, mutations require explicit approval.

## Grounding rule

Before answering any AI-900 domain question, search Microsoft Learn:
```
mcp__microsoft-learn__microsoft_docs_search(query="<user's question topic> Azure AI")
```

Then synthesize the official documentation with IPAI-specific context from this skill.
