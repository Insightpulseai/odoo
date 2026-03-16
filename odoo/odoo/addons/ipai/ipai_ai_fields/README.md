# AI Fields

Retrieval-Augmented Generation pipeline for AI agents.

AI-powered field population

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

1. Install the module
2. Go to Settings > IPAI > AI Fields
3. Configure as needed

## License

LGPL-3
