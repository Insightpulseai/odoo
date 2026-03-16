# IPAI AI RAG

Retrieval-Augmented Generation pipeline for AI agents.

## Overview

This module provides the RAG (Retrieval-Augmented Generation) pipeline that enables AI agents to access and utilize knowledge from various sources. It handles text chunking, embedding generation, and similarity-based retrieval.

## Features

- **Source Management**: Ingest files, URLs, and knowledge bases
- **Deterministic Chunking**: Fixed-size chunks with configurable overlap
- **Content Hashing**: SHA-256 hashing for deduplication
- **Vector Embeddings**: OpenAI embeddings API integration
- **Similarity Search**: Cosine similarity with stable tie-breaking

## Installation

```bash
# Install via Docker (requires ipai_ai_agent_builder)
docker compose exec odoo-core odoo -d odoo_core -i ipai_ai_rag --stop-after-init
```

## Configuration

### Chunk Settings

Configure in Odoo Settings > AI Agent Builder:

- **Chunk Size**: Default 1000 tokens
- **Chunk Overlap**: Default 200 tokens
- **Retrieval Top K**: Default 5 chunks

### Embedding Model

Default: `text-embedding-3-small`

Configure via system parameter `ipai.ai.embedding_model`.

## Source Types

| Type | Locator Format | Description |
|------|----------------|-------------|
| `file` | Upload binary | Direct file upload |
| `url` | `https://...` | Fetch content from URL |
| `kb` | KB reference | Knowledge base integration |
| `model_field` | `model:field:domain` | Extract from Odoo records |

## Usage

### Ingest a Source

```python
source = env['ipai.ai.source'].create({
    'name': 'Product Docs',
    'agent_id': agent.id,
    'source_type': 'url',
    'locator': 'https://example.com/docs.pdf',
})
source.action_ingest()
```

### Retrieve Context

```python
retrieval_service = env['ipai.ai.retrieval.service']
context = retrieval_service.retrieve_context(agent, "How do I create a lead?")
```

## RAG Contract

### Determinism Guarantees

- **Chunking**: Fixed `chunk_size` + `overlap` = same chunks
- **Hashing**: SHA-256 ensures content-based deduplication
- **Retrieval**: Stable tie-breaking (`score DESC, chunk_id ASC`)

### Prompt Assembly Order

1. System prompt
2. Topic instructions
3. Retrieved context (top-k chunks)
4. User message

## Dependencies

- Python: `tiktoken`, `openai`, `requests`
- Odoo: `ipai_ai_agent_builder`

## License

LGPL-3
