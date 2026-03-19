# Retrieval Grounding Contract

> Version: 1.0.0
> Last updated: 2026-03-15
> Parent: runtime-contract.md (C-30)
> Status: Phase 2B — Not yet active

## Purpose

Define how the copilot retrieves, filters, and uses source documents to ground advisory responses. Grounding reduces hallucination and provides source provenance.

## Architecture

```
User prompt
    ↓
Backend builds context envelope (with retrieval_scope)
    ↓
Backend queries Azure AI Search with:
  - user query (semantic search)
  - filter: kb_scope IN retrieval_scope
  - filter: group_ids/any(g:search.in(g, 'user_groups'))
    ↓
Search returns top-K chunks with provenance
    ↓
Backend injects chunks into thread message as [RETRIEVAL_CONTEXT]
    ↓
Agent reasons over user query + grounded context
    ↓
Response includes source attribution
```

## Search Service

| Property | Value |
|----------|-------|
| Service | `srch-ipai-dev` |
| Endpoint | `https://srch-ipai-dev.search.windows.net/` |
| API key | Vaulted at `ipai-odoo-dev-kv/srch-ipai-dev-api-key` |
| Index name | `ipai-knowledge-index` |

## Index Schema

| Field | Type | Searchable | Filterable | Notes |
|-------|------|-----------|-----------|-------|
| `id` | Edm.String | — | key | Chunk unique ID |
| `title` | Edm.String | yes | — | Source document title |
| `content` | Edm.String | yes | — | Chunk text (max 2000 chars) |
| `kb_scope` | Edm.String | — | yes | Knowledge base scope identifier |
| `group_ids` | Collection(Edm.String) | — | yes | Security trimming groups |
| `source_file` | Edm.String | — | yes | Source file path |
| `chunk_index` | Edm.Int32 | — | — | Chunk position in source |
| `last_updated` | Edm.DateTimeOffset | — | yes | Content freshness |

## Knowledge Base Scopes

| Scope | Content | Access |
|-------|---------|--------|
| `general-kb` | Product overview, onboarding, user guides | All authenticated users |
| `finance-close-kb` | Month-end close, year-end, reconciliation | finance.* roles |
| `bir-compliance` | BIR filing, VAT, withholding tax | finance.* roles |
| `marketing-playbooks` | Campaigns, lead pipeline, brand | marketing.* roles |
| `analytics-kb` | Dashboard docs, KPI definitions | analytics.* roles |
| `ops-kb` | Platform operations, runbooks | ops.* roles |
| `infrastructure-kb` | Deployment, infrastructure | ops.admin only |
| `audit-evidence` | Audit trails, compliance evidence | finance.close.approver only |

## Chunking Contract

| Parameter | Value |
|-----------|-------|
| Max chunk size | 2000 characters |
| Overlap | 200 characters |
| Chunk boundary | Paragraph (prefer `\n\n`) |
| Metadata preserved | title, kb_scope, group_ids, source_file |
| Encoding | UTF-8 |

## Security Trimming

At query time, the backend applies two filters:

1. **Scope filter**: `kb_scope` must be in user's `retrieval_scope`
2. **Group filter**: `group_ids/any(g:search.in(g, '<user_group_ids>'))`

Both filters are applied server-side before results reach the agent. The agent never sees documents outside the user's authorized scope.

## Retrieval Injection Format

```
[RETRIEVAL_CONTEXT]
Source: month-end-close-checklist.md (finance-close-kb)
---
Step 1: Review all unposted journal entries...
Step 2: Reconcile bank statements...
---

Source: bir-filing-calendar.md (bir-compliance)
---
Monthly: 1601-C due on 10th, 2550M due on 20th...
---
[/RETRIEVAL_CONTEXT]

<user message here>
```

## Agent Instructions for Grounded Responses

The system prompt must instruct the agent to:

1. Prefer information from `[RETRIEVAL_CONTEXT]` over parametric knowledge
2. Cite the source document when using retrieved information
3. Say "Based on our knowledge base..." when grounding from retrieval
4. Say "Based on general Odoo knowledge..." when answering without retrieval
5. Never fabricate citations or source references
6. If retrieval returns empty results, answer from system prompt knowledge with appropriate caveats

## Eval Criteria

| Metric | Threshold |
|--------|-----------|
| Grounded answer accuracy | >= 90% |
| Source attribution correctness | >= 85% |
| Empty-search graceful degradation | 100% |
| Security trimming violation | 0 |
| Stale document handling | Warn user when source > 90 days old |

## Population and Refresh

- Initial population: `scripts/ai-search/populate-index.py`
- Validation: `scripts/ai-search/validate-index.py`
- Content source: `agents/knowledge-base/` directory
- Refresh cadence: On content change (CI-triggered) or weekly minimum
- Stale threshold: 90 days without update triggers warning in responses

## Dependencies

- `context-envelope-contract.md` — provides `retrieval_scope` and `groups`
- `infra/entra/role-tool-mapping.yaml` — maps roles to retrieval scopes
- `agents/knowledge-base/index-schema.json` — index definition
