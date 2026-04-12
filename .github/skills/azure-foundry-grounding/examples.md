# azure-foundry-grounding -- Worked Examples

## Example 1: Knowledge Binding with Topic Scope

```yaml
# ssot/agents/knowledge-bindings.yaml
bindings:
  - agent: pulser-copilot
    grounded: true
    knowledge_bases:
      - name: odoo-18-docs
        index: odoo-kb-index
        embedding_model: text-embedding-3-large
        topic_scope:
          - odoo_accounting
          - odoo_sales
          - odoo_purchase
          - odoo_hr
        chunk_size_tokens: 512
        chunk_overlap_tokens: 51        # ~10% overlap
        semantic_ranker: true
        active: true
      - name: azure-platform-docs
        index: azure-platform-index
        embedding_model: text-embedding-3-large
        topic_scope:
          - azure_container_apps
          - azure_postgresql
          - azure_foundry
        active: true

  - agent: finance-judge
    grounded: true
    knowledge_bases:
      - name: odoo-18-docs
        index: odoo-kb-index
        topic_scope:
          - odoo_accounting
          - odoo_tax
          - bir_compliance
        active: true
```

Key decisions:
- Topic scope prevents cross-domain retrieval (e.g. HR queries pulling Databricks docs).
- Each binding declares embedding model and chunk strategy for reproducibility.

## Example 2: Index Population with Validated Chunk Strategy

```python
# scripts/ai-search/populate-index.py -- canonical pattern
# Chunk strategy: 512 tokens, 10% overlap
# Source: microsoft_docs_search("Azure AI Search chunking best practices")
# Recommendation: 256-1024 tokens; structured docs (API refs) benefit from smaller chunks.

CHUNK_SIZE = 512       # tokens
CHUNK_OVERLAP = 51     # ~10%
EMBEDDING_MODEL = "text-embedding-3-large"
BATCH_SIZE = 100

def chunk_document(text: str) -> list[str]:
    """Split document into overlapping chunks."""
    enc = tiktoken.get_encoding("cl100k_base")
    tokens = enc.encode(text)
    chunks = []
    start = 0
    while start < len(tokens):
        end = min(start + CHUNK_SIZE, len(tokens))
        chunks.append(enc.decode(tokens[start:end]))
        start += CHUNK_SIZE - CHUNK_OVERLAP
    return chunks
```

## Example 3: Retrieval Eval Score Interpretation

```
Step 1: microsoft_docs_search("Azure AI Foundry retrieval evaluation RAG quality metrics")
Result: Built-in evaluators: groundedness (0-1), relevance (0-1), coherence (0-1),
        fluency (0-1), F1 (exact match). Groundedness measures whether response
        is supported by retrieved context. Minimum recommended threshold: 0.7.

Step 2: Run eval script
$ python scripts/foundry/run_retrieval_eval.py \
    --dataset agents/evals/retrieval-baseline.jsonl \
    --agent pulser-copilot \
    --threshold 0.7

Output:
  groundedness:  0.83  PASS
  relevance:     0.79  PASS
  coherence:     0.91  PASS
  f1_score:      0.71  PASS

Step 3: Interpret failures
  If groundedness < 0.7: check chunk size (too large = diluted context),
  check topic scope (too broad = noisy retrieval), check embedding model
  version (outdated model = stale embeddings).
```

## Example 4: Index Validation Check

```python
# scripts/ai-search/validate-index.py -- health assertions
def validate_index(index_name: str, min_docs: int = 100):
    client = SearchIndexClient(endpoint=SEARCH_ENDPOINT, credential=credential)
    index = client.get_index(index_name)

    # Assert fields
    field_names = {f.name for f in index.fields}
    assert "content_vector" in field_names, "Missing vector field"
    assert "content" in field_names, "Missing content field"
    assert "source_url" in field_names, "Missing source_url field"

    # Assert document count
    search_client = SearchClient(endpoint=SEARCH_ENDPOINT, index_name=index_name, credential=credential)
    count = search_client.get_document_count()
    assert count >= min_docs, f"Index has {count} docs, expected >= {min_docs}"

    print(f"PASS: {index_name} has {count} documents, all required fields present")
```
