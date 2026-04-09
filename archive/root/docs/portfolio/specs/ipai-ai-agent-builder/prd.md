# PRD: IPAI AI Agent Builder

## Overview

The IPAI AI Agent Builder provides Odoo 18 AI Agents feature parity for CE/OCA deployments, enabling organizations to create intelligent agents that combine LLM capabilities with structured tool execution and RAG-based knowledge retrieval.

## Problem Statement

Odoo 18 Enterprise introduces an "AI Agents" framework with:
- Agents with configurable system prompts and response styles
- Topics as instruction bundles that assign specific tools
- Sources (files/URLs/knowledge) for RAG-based context
- Tool execution for business actions

CE/OCA users lack access to this functionality. This module bridges that gap.

## Target Users

1. **System Administrators**: Configure agents, topics, and tools
2. **Business Users**: Interact with agents via chat interfaces
3. **Developers**: Create custom tools and integrations

## Core Features

### F1: Agent Management

**Description**: Create and manage AI agents with configurable behavior.

**Requirements**:
- Define agent name, system prompt, response style
- Select LLM provider (ChatGPT, Gemini) and model
- Enable/disable agents
- Associate topics with agents

**Data Model**:
```
ipai.ai.agent
├── name: Char
├── system_prompt: Text
├── style: Selection (professional, friendly, concise, detailed)
├── provider: Selection (openai, google)
├── model: Char
├── enabled: Boolean
├── company_id: Many2one (res.company)
└── topic_ids: One2many (ipai.ai.topic)
```

### F2: Topic Management

**Description**: Organize agent instructions into reusable topics.

**Requirements**:
- Define topic name and instructions
- Assign tools to topics
- Topics are agent-specific

**Data Model**:
```
ipai.ai.topic
├── name: Char
├── agent_id: Many2one (ipai.ai.agent)
├── instructions: Text
└── tool_ids: Many2many (ipai.ai.tool)
```

### F3: Tool Registry

**Description**: Register and manage callable business actions.

**Requirements**:
- Define tool key, name, description
- Specify Python entrypoint (module:function)
- Permission gating via Odoo groups
- Support dry_run mode
- Track allowed models for tool calls

**Data Model**:
```
ipai.ai.tool
├── key: Char (unique)
├── name: Char
├── description: Text
├── python_entrypoint: Char
├── group_ids: Many2many (res.groups)
├── dry_run_supported: Boolean
└── active: Boolean
```

### F4: Source Management (RAG)

**Description**: Ingest knowledge sources for retrieval-augmented generation.

**Requirements**:
- Support source types: file, URL, knowledge base, model field
- Track ingestion status
- Store metadata as JSON

**Data Model**:
```
ipai.ai.source
├── name: Char
├── agent_id: Many2one (ipai.ai.agent)
├── source_type: Selection (file, url, kb, model_field)
├── locator: Text
├── metadata: Text (JSON)
├── ingest_status: Selection (pending, processing, done, error)
└── chunk_ids: One2many (ipai.ai.chunk)
```

### F5: RAG Pipeline

**Description**: Chunk, embed, and retrieve knowledge for context augmentation.

**Requirements**:
- Deterministic chunking (fixed size + overlap)
- Content hashing for deduplication
- Vector embeddings via OpenAI API
- Cosine similarity retrieval with stable tie-breaking

**Data Model**:
```
ipai.ai.chunk
├── source_id: Many2one (ipai.ai.source)
├── index: Integer
├── content: Text
├── content_hash: Char
├── token_count: Integer
└── embedding_ids: One2many (ipai.ai.embedding)

ipai.ai.embedding
├── chunk_id: Many2one (ipai.ai.chunk)
├── vector: Text (JSON array)
├── model: Char
├── dimensions: Integer
└── created_at: Datetime
```

### F6: Chat API

**Description**: REST endpoint for agent conversations.

**Endpoint**: `POST /ipai/ai/v1/agent/<agent_id>/chat`

**Request**:
```json
{
  "message": "string",
  "context": {"key": "value"},
  "stream": false
}
```

**Response**:
```json
{
  "run_id": 123,
  "response": "string",
  "tool_calls": [{"tool_key": "...", "status": "..."}],
  "sources": [{"chunk_id": 1, "score": 0.95}]
}
```

### F7: Tool Execution API

**Description**: Internal endpoint for tool invocation.

**Endpoint**: `POST /ipai/ai/v1/tool/<tool_key>/invoke`

**Requirements**:
- Permission checking before execution
- Full audit logging
- Dry-run support

### F8: Observability

**Description**: Track all agent interactions for debugging and compliance.

**Data Model**:
```
ipai.ai.run
├── agent_id: Many2one (ipai.ai.agent)
├── user_id: Many2one (res.users)
├── input: Text
├── output: Text
├── provider: Char
├── model: Char
├── latency_ms: Integer
├── created_at: Datetime
└── event_ids: One2many (ipai.ai.run.event)

ipai.ai.run.event
├── run_id: Many2one (ipai.ai.run)
├── event_type: Selection (start, rag, llm, tool, end, error)
├── payload: Text (JSON)
└── created_at: Datetime

ipai.ai.tool.call
├── run_id: Many2one (ipai.ai.run)
├── tool_id: Many2one (ipai.ai.tool)
├── input_json: Text
├── output_json: Text
├── status: Selection (pending, success, error, dry_run)
├── error_message: Text
└── created_at: Datetime
```

### F9: Config-as-Code

**Description**: YAML-based configuration for reproducible deployments.

**File Structure**:
```
config/ipai_ai/agents/
├── default_agent.yaml
├── sales_agent.yaml
└── support_agent.yaml
```

**YAML Format**:
```yaml
agent:
  name: Sales Assistant
  system_prompt: |
    You are a helpful sales assistant...
  style: professional
  provider: openai
  model: gpt-4o

topics:
  - name: Lead Management
    instructions: |
      Help users create and manage leads...
    tools:
      - crm_create_lead
      - crm_update_lead

sources:
  - name: Product Catalog
    type: url
    locator: https://example.com/products.pdf
```

## Non-Functional Requirements

### Performance
- RAG retrieval < 500ms for 10K chunks
- LLM response streaming support
- Async embedding generation

### Security
- API key encryption at rest
- Role-based access control
- Audit logging for compliance

### Scalability
- Support for 100+ agents per instance
- 1M+ chunks across all sources
- Concurrent chat sessions

## Success Metrics

1. **Feature Parity**: 90%+ coverage of Odoo 18 AI Agents functionality
2. **Adoption**: 5+ active agents configured within 30 days of deployment
3. **Performance**: 95th percentile response time < 3s
4. **Reliability**: 99.5% uptime for chat endpoints

## Out of Scope

- Real-time voice interaction
- Image/video analysis
- Custom model training
- Multi-modal embeddings (text-only initially)
