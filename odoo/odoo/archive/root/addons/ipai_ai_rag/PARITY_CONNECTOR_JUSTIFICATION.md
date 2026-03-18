# Connector Justification: ipai_ai_rag

## What this module does
Provides a RAG (Retrieval-Augmented Generation) pipeline for AI agents, covering source ingestion (files, URLs, knowledge bases), deterministic text chunking, OpenAI vector embeddings, and cosine-similarity retrieval with stable tie-breaking.

## What it is NOT
- Not an OCA parity addon
- Not an EE-module reimplementation

## Why LOC exceeds 1000
The module reaches 1,079 LOC because it implements three independent service layers (chunking with configurable size/overlap, embedding with batch processing, and retrieval with cosine similarity), three model classes (source, chunk, embedding), SHA-256 content deduplication, token-accurate counting via tiktoken, and a test suite covering chunking and retrieval determinism.

## Planned reduction path
- Extract the chunking and embedding services into a shared `ipai_ai_core` library alongside `ipai_ai_agent_builder` provider code
- Move test fixtures into shared conftest to reduce test duplication
- Consider merging `ai_chunk` and `ai_embedding` models into a single model with state tracking
