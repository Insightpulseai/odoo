# Implementation Plan: IPAI AI Agent Builder

## Phase 1: Foundation (Core Models & Infrastructure)

### 1.1 Create Module Scaffolds
- `addons/ipai_ai_agent_builder/` - Core agent/topic/tool registry
- `addons/ipai_ai_rag/` - RAG pipeline (chunking, embeddings, retrieval)
- `addons/ipai_ai_tools/` - Tool interface, execution, auditing

### 1.2 Data Models
Create Odoo models:
- `ipai.ai.agent` - Agent definitions
- `ipai.ai.topic` - Topic instruction bundles
- `ipai.ai.tool` - Tool registry
- `ipai.ai.source` - Knowledge sources
- `ipai.ai.chunk` - Content chunks
- `ipai.ai.embedding` - Vector embeddings
- `ipai.ai.run` - Conversation runs
- `ipai.ai.run.event` - Run events
- `ipai.ai.tool.call` - Tool invocation audit

### 1.3 Security
- Access control CSV for all models
- Security groups: `ipai_ai_user`, `ipai_ai_manager`, `ipai_ai_admin`
- Record rules for multi-company isolation

## Phase 2: RAG Pipeline

### 2.1 Chunking Service
- Implement `IpaiAiChunkingService` (AbstractModel)
- Fixed-size chunking with configurable overlap
- SHA-256 content hashing for deduplication
- Token counting (tiktoken-compatible)

### 2.2 Embedding Service
- Implement `IpaiAiEmbeddingService` (AbstractModel)
- OpenAI embeddings API integration
- Batch processing for efficiency
- Caching to avoid re-embedding unchanged content

### 2.3 Retrieval Service
- Implement `IpaiAiRetrievalService` (AbstractModel)
- Cosine similarity calculation
- Stable tie-breaking (score DESC, chunk_id ASC)
- Top-k retrieval with configurable k

### 2.4 Source Ingestion
- File upload handling
- URL content fetching
- Model field extraction
- Async processing queue

## Phase 3: LLM Integration

### 3.1 Provider Abstraction
- `IpaiAiProviderBase` - Abstract provider interface
- `IpaiAiProviderOpenAI` - ChatGPT implementation
- `IpaiAiProviderGoogle` - Gemini implementation

### 3.2 Prompt Assembly
- System prompt injection
- Topic instructions
- RAG context formatting
- Tool definitions (function calling)

### 3.3 Response Handling
- Streaming support
- Tool call detection and routing
- Error handling and retries

## Phase 4: Tool Framework

### 4.1 Tool Registry
- Python entrypoint loading
- Permission validation
- Schema validation for inputs/outputs

### 4.2 Built-in Tools
- `crm_create_lead` - Create CRM lead
- `calendar_create_event` - Schedule calendar event
- `sale_create_order` - Create sale order

### 4.3 Execution Engine
- Permission gating (Odoo groups)
- Dry-run mode support
- Full audit logging

## Phase 5: API Layer

### 5.1 REST Endpoints
- `POST /ipai/ai/v1/agent/<id>/chat` - Chat with agent
- `POST /ipai/ai/v1/source/<id>/ingest` - Trigger ingestion
- `POST /ipai/ai/v1/tool/<key>/invoke` - Internal tool invoke
- `GET /ipai/ai/v1/agent/<id>/runs` - List runs

### 5.2 Authentication
- Session-based for Odoo users
- API key support for external integration
- Rate limiting

## Phase 6: Config-as-Code

### 6.1 YAML Schema
- Agent definition schema
- Topic definition schema
- Tool mapping schema
- Source definition schema

### 6.2 Seed Script
- `scripts/ipai_ai_seed.sh` - Idempotent loader
- Create/update logic (no duplicates)
- Validation before apply

### 6.3 Default Configurations
- `config/ipai_ai/agents/default.yaml`
- Example agent configurations

## Phase 7: Testing

### 7.1 Unit Tests
- Chunking determinism
- Embedding cache key generation
- Retrieval tie-breaking
- Tool permission checking

### 7.2 Integration Tests
- YAML → agent creation flow
- Source ingestion pipeline
- RAG query end-to-end
- Tool execution with audit

### 7.3 Performance Tests
- Retrieval latency benchmarks
- Concurrent chat session handling

## Phase 8: Documentation & Polish

### 8.1 Module Documentation
- README.md for each module
- DEPLOYMENT_CHECKLIST.md
- API documentation

### 8.2 XML Data
- Demo data for testing
- Default configuration records

### 8.3 Views (Optional Enhancement)
- Agent management views
- Run history views
- Tool audit views

## File Structure

```
addons/
├── ipai_ai_agent_builder/
│   ├── __manifest__.py
│   ├── __init__.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── ai_agent.py
│   │   ├── ai_topic.py
│   │   ├── ai_tool.py
│   │   ├── ai_run.py
│   │   ├── ai_run_event.py
│   │   ├── ai_tool_call.py
│   │   └── res_config_settings.py
│   ├── controllers/
│   │   ├── __init__.py
│   │   └── main.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── provider_base.py
│   │   ├── provider_openai.py
│   │   └── provider_google.py
│   ├── security/
│   │   ├── ir.model.access.csv
│   │   └── security.xml
│   ├── data/
│   │   └── ai_agent_data.xml
│   ├── views/
│   │   ├── ai_agent_views.xml
│   │   └── res_config_settings_views.xml
│   └── tests/
│       ├── __init__.py
│       └── test_ai_agent.py
│
├── ipai_ai_rag/
│   ├── __manifest__.py
│   ├── __init__.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── ai_source.py
│   │   ├── ai_chunk.py
│   │   └── ai_embedding.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── chunking_service.py
│   │   ├── embedding_service.py
│   │   └── retrieval_service.py
│   ├── security/
│   │   └── ir.model.access.csv
│   └── tests/
│       ├── __init__.py
│       ├── test_chunking.py
│       └── test_retrieval.py
│
├── ipai_ai_tools/
│   ├── __manifest__.py
│   ├── __init__.py
│   ├── models/
│   │   └── __init__.py
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── crm_tools.py
│   │   ├── calendar_tools.py
│   │   └── sale_tools.py
│   ├── services/
│   │   ├── __init__.py
│   │   └── tool_executor.py
│   ├── security/
│   │   └── ir.model.access.csv
│   └── tests/
│       ├── __init__.py
│       └── test_tool_execution.py

config/
└── ipai_ai/
    └── agents/
        ├── default.yaml
        └── sales_assistant.yaml

scripts/
└── ipai_ai_seed.sh
```

## Dependencies

### Python Packages
- `tiktoken` - Token counting
- `openai` - OpenAI API
- `google-generativeai` - Gemini API
- `pyyaml` - YAML parsing
- `requests` - HTTP client

### Odoo Modules
- `base`
- `web`
- `mail`
- `crm` (for built-in tools)
- `calendar` (for built-in tools)
- `sale` (for built-in tools)

## Milestones

| Milestone | Deliverables | Acceptance Criteria |
|-----------|--------------|---------------------|
| M1 | Module scaffolds + core models | Models created, migrations run |
| M2 | RAG pipeline | Chunking, embedding, retrieval working |
| M3 | LLM integration | ChatGPT + Gemini providers functional |
| M4 | Tool framework | 3 built-in tools with audit trail |
| M5 | API + Config | REST endpoints + YAML seed working |
| M6 | Tests + Docs | All tests pass, docs complete |
