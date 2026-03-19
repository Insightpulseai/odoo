# Connector Justification: ipai_ask_ai

## What this module does
AI chat agent integration with provider toggles for ChatGPT and Google Gemini, providing a conversational interface with secure API key storage, channel-based message history, and an AFC (Accounting/Finance/Compliance) RAG service for domain-specific context retrieval.

## What it is NOT
- Not an OCA parity addon
- Not an EE-module reimplementation

## Why LOC exceeds 1000
The module totals 1,418 LOC because it contains a full chat service layer (`ask_ai_service.py` at 698 LOC) handling multi-provider orchestration, streaming responses, and conversation context management; a dedicated AFC RAG service (360 LOC) for finance-domain document retrieval; channel management for persistent chat history; and REST API controllers for the chat frontend.

## Planned reduction path
- Extract `afc_rag_service.py` into `ipai_ai_rag` as a domain-specific retrieval plugin
- Split `ask_ai_service.py` into provider-specific adapters reusing `ipai_ai_agent_builder` provider classes
- Move shared provider configuration (API keys, model selection) into a common settings mixin
