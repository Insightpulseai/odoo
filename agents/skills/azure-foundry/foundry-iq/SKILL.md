# Skill: Foundry IQ — Knowledge Grounding

## Metadata

| Field | Value |
|-------|-------|
| **id** | `azure-foundry-iq` |
| **domain** | `azure_foundry` |
| **source** | https://learn.microsoft.com/en-us/azure/foundry/agents/concepts/what-is-foundry-iq |
| **extracted** | 2026-03-15 |
| **applies_to** | agents, foundry |
| **tags** | knowledge, rag, grounding, search, permissions, agentic-retrieval |

---

## What It Is

Managed knowledge layer that turns enterprise data into reusable, permission-aware knowledge bases for AI agents. Built on Azure AI Search with agentic retrieval.

## Components

| Component | Description |
|-----------|-------------|
| **Knowledge Base** | Top-level resource orchestrating retrieval. Controls which sources to query and retrieval reasoning effort (minimal/low/medium). |
| **Knowledge Sources** | Connections to indexed (Blob, SharePoint, OneLake) or remote (web) content. |
| **Agentic Retrieval** | Multi-query pipeline: decompose → parallel subqueries → semantic rerank → unified response. Optional LLM for query planning. |

## Capabilities

- Connect one knowledge base to multiple agents
- Auto document chunking, vector embedding, metadata extraction
- Keyword, vector, or hybrid queries across sources
- Multi-query agentic retrieval with LLM query planning
- Extractive data with citations for traceability
- ACL sync + Purview sensitivity labels → query-time permission enforcement
- Queries run under caller's Entra identity (end-to-end permissions)

## Knowledge Sources

| Source | Type |
|--------|------|
| Azure Blob Storage | Indexed |
| SharePoint | Indexed |
| OneLake (Fabric) | Indexed |
| Public web | Remote |

## IQ Family

| IQ | Layer | Purpose |
|----|-------|---------|
| **Foundry IQ** | Enterprise data | Structured + unstructured data across Azure, SharePoint, web |
| **Fabric IQ** | Analytics | Ontologies, semantic models, graphs over OneLake/Power BI |
| **Work IQ** | Collaboration | Documents, meetings, chats, workflows from M365 |

## IPAI Mapping

| Foundry IQ | IPAI Equivalent | Gap |
|-----------|-----------------|-----|
| Knowledge base | `agents/knowledge-base/` + Azure AI Search index | Need to create search index |
| Agentic retrieval | ipai-odoo-copilot retrieval-grounding-contract.md | Pattern documented, not yet deployed |
| ACL enforcement | Not implemented | **Gap — no permission-aware retrieval** |
| Auto chunking | Not implemented | **Gap — manual document prep** |
| Citation tracing | Not implemented | **Gap — needed for compliance** |

### Adoption Path

1. Create Azure AI Search index (`srch-ipai-dev`) with knowledge sources
2. Index: Odoo docs, OCA docs, BIR rules, internal KB articles
3. Create Foundry IQ knowledge base pointing to index
4. Connect to ipai-odoo-copilot-azure agent
5. Enable ACL sync for permission-aware responses
