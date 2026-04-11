---
name: azure-foundry-grounding
description: Validate RAG grounding configuration including knowledge base bindings, vector indexes, chunking strategy, and retrieval eval quality
version: "1.0"
compatibility:
  hosts: [github-copilot, claude-code, codex-cli, cursor, gemini-cli]
tags: [foundry, evals, architecture, governance]
---

# azure-foundry-grounding

**Impact tier**: P2 -- Quality / Accuracy

## Purpose

Validate RAG/grounding configuration including Foundry knowledge base bindings,
Azure AI Search vector indexes, retrieval evaluation pipelines, and document
chunking strategy. Ensures grounding is properly scoped to the IPAI knowledge
bases (Odoo 18 docs, Azure platform, Databricks), is not over-engineered for
MVP, and retrieval quality meets the minimum threshold before any agent is
promoted to staging.

## When to Use

- After adding or updating a knowledge base (new documents, reindex).
- When agent responses show hallucination or out-of-date Odoo guidance.
- Before promoting a grounded agent from dev to staging.
- When retrieval evaluation scores drop below threshold.

## Required Evidence (inspect these repo paths first)

| Path | What to look for |
|------|-----------------|
| `ssot/agents/knowledge-bindings.yaml` | KB name, index name, scope, active flag |
| `ssot/ai/sources.yaml` | Document sources: blob containers, folder paths, update cadence |
| `ssot/ai/topics.yaml` | Topic scoping per agent to prevent over-retrieval |
| `scripts/ai-search/populate-index.py` | Chunking strategy, embedding model, batch size |
| `scripts/ai-search/validate-index.py` | Index health checks, document count assertions |
| `scripts/foundry/run_retrieval_eval.py` | Eval dataset path, threshold, metric names |
| `docs/architecture/ai/FOUNDRY_LANDING_ZONE.md` | KB registry, retrieval architecture decisions |

## Microsoft Learn MCP Usage

Run at least these queries:

1. `microsoft_docs_search("Azure AI Foundry grounding knowledge base vector search")`
   -- retrieves Foundry IQ grounding, knowledge base creation, index binding.
2. `microsoft_docs_search("Azure AI Search vector index chunking strategy embedding")`
   -- retrieves recommended chunk sizes, overlap, embedding model selection.
3. `microsoft_docs_search("Azure AI Foundry retrieval evaluation RAG quality metrics")`
   -- retrieves built-in eval metrics: groundedness, relevance, coherence, F1.
4. `microsoft_docs_search("Azure AI Search semantic ranking hybrid query")`
   -- retrieves hybrid vector + keyword query, semantic ranker configuration.

Optional:

5. `microsoft_code_sample_search("azure ai search vector index python", language="python")`
6. `microsoft_docs_fetch("https://learn.microsoft.com/en-us/azure/ai-services/agents/how-to/tools/azure-ai-search")`

## Workflow

1. **Inspect repo** -- Read `ssot/agents/knowledge-bindings.yaml` and
   `ssot/ai/topics.yaml`. Record: which agents have KB bindings, the index
   name and embedding model, topic scope applied, and the eval threshold
   in `run_retrieval_eval.py`.
2. **Query MCP** -- Run queries 1-4. Capture recommended chunk size for
   structured docs (512-1024 tokens with 10% overlap), semantic ranking
   enablement steps, and Foundry IQ binding API shape.
3. **Compare** -- Identify: (a) agents without topic scoping (over-retrieval
   risk), (b) indexes using default chunk size without justification, (c)
   missing eval runs in evidence directory, (d) eval threshold below 0.7
   for groundedness.
4. **Patch** -- Update `ssot/agents/knowledge-bindings.yaml` with topic scope
   per agent. Update `scripts/ai-search/populate-index.py` with validated
   chunk strategy. Add/update eval dataset in `agents/evals/` and run
   `run_retrieval_eval.py` to capture baseline scores.
5. **Verify** -- `validate-index.py` reports document count > 0 and no
   missing embeddings. Retrieval eval groundedness score >= 0.7. No agent
   with `grounded: true` in `ssot/ai/agents.yaml` lacks a KB binding entry.

## Outputs

| File | Change |
|------|--------|
| `ssot/agents/knowledge-bindings.yaml` | Topic scope, index metadata, active flag |
| `ssot/ai/sources.yaml` | Confirmed source paths, update cadence |
| `scripts/ai-search/populate-index.py` | Chunk size, overlap, embedding model |
| `agents/evals/retrieval-baseline.jsonl` | Eval dataset with ground-truth answers |
| `docs/architecture/ai/FOUNDRY_LANDING_ZONE.md` | KB registry entries updated |
| `docs/evidence/<stamp>/azure-foundry-grounding/` | Eval scores, MCP excerpts, index stats |

## Completion Criteria

- [ ] Every agent with `grounded: true` in `ssot/ai/agents.yaml` has a matching entry in `knowledge-bindings.yaml`.
- [ ] Each KB binding has an explicit `topic_scope` list (not wildcard).
- [ ] `validate-index.py` runs without error and reports document count > 0.
- [ ] Retrieval eval groundedness score >= 0.7 for at least one eval dataset.
- [ ] Chunk size and overlap are documented in `populate-index.py` with a comment citing the MCP source.
- [ ] Evidence directory contains eval score output and MCP excerpts.
