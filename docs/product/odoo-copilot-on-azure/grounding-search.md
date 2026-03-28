# Grounding and Search

> Azure AI Search role, grounding boundaries, and safety controls for Odoo Copilot.

## Grounding Architecture

Odoo Copilot answers are grounded in two complementary data planes:

| Plane | Source | Mechanism | Latency |
|-------|--------|-----------|---------|
| **Record context** | Odoo PostgreSQL (via ORM) | Tool calls that read Odoo models | Low (direct DB) |
| **Document knowledge** | Azure AI Search index | RAG retrieval at prompt time | Medium (search query) |

Record context is always primary. Document knowledge supplements when the user
question references policies, SOPs, contracts, or knowledge not stored as Odoo
records.

## Azure AI Search Role

| Capability | Status | Notes |
|------------|--------|-------|
| Index provisioning | Planned | `srch-ipai-dev` resource exists |
| Document ingestion | Planned | PDF, DOCX, Markdown via Azure AI Document Intelligence |
| Semantic ranking | Planned | Hybrid (keyword + vector) with semantic reranker |
| Foundry knowledge connection | Target | Agent Service connects to search index natively |
| Odoo-side RAG fallback | Current | Module can query search index directly if not using Agent Service |

## Index Design

```
Index: odoo-copilot-knowledge
  Fields:
    - id (key)
    - content (searchable, vector)
    - title (searchable, filterable)
    - source_type (filterable): policy | sop | contract | help | faq
    - department (filterable): finance | hr | ops | general
    - last_updated (sortable)
    - chunk_sequence (sortable)
    - embedding (vector, dimensions: 1536)
```

## Grounding Boundaries

### What is grounded

- Odoo record fields visible to the current user (respects ACLs and record rules)
- Documents indexed in Azure AI Search with appropriate department/source filters
- System configuration values from `ir.config_parameter` (non-secret)

### What is never grounded

- Raw SQL query results (copilot uses ORM tools, never direct SQL)
- Records the current user cannot access via Odoo security model
- Documents not present in the search index
- Secrets, API keys, or credentials from any source

### Hallucination Controls

| Control | Mechanism |
|---------|-----------|
| Citation requirement | Responses must reference source record IDs or document titles |
| Confidence threshold | Search results below relevance threshold are excluded |
| Fallback behavior | If no grounding data found, copilot states it cannot answer rather than guessing |
| Tool-first policy | Factual claims about Odoo data must come from tool calls, not model knowledge |

## Safety Controls

| Control | Implementation |
|---------|---------------|
| Content filtering | Azure AI Content Safety on Foundry endpoint |
| PII handling | No PII stored in search index metadata; PII in content follows data classification |
| Prompt injection defense | System prompt is not overridable by user input; tool results are treated as data |
| Output filtering | Responses are filtered for harmful content before rendering |
| Data residency | All data stays in Southeast Asia Azure region (search index + Foundry) |

## Search vs Action Boundary

The copilot distinguishes between:

1. **Search queries** -- answered from grounding data (records + documents), read-only
2. **Action requests** -- routed to Odoo action tools, require explicit confirmation

A user asking "what is our expense policy?" triggers a search query.
A user asking "approve this expense report" triggers an action request.

The copilot must never perform an action when the user asked a question, and
must never fabricate an answer when the user requested an action.
