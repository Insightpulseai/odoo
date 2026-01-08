# ipai_ai_agents (Odoo CE/OCA 18)

Odoo 19-style "Ask AI / AI agents" UX for Odoo CE 18:
- Command palette entry "Ask AI"
- Client action panel chat UI
- Server-side RAG: Supabase RPC retrieval + OpenAI-compatible LLM answering
- Citation-based responses with confidence scoring

## Features

- **AI Agents**: Configurable agents with custom system prompts
- **Knowledge Sources**: Connect docs sites, GitHub repos, PDFs
- **RAG Pipeline**: Retrieve evidence from Supabase KB, generate grounded answers
- **Citations**: Every answer includes source citations
- **Confidence Gating**: Uncertain responses are flagged
- **Feedback Loop**: Users can mark responses helpful/unhelpful

## Environment Variables (server)

### Required
- `IPAI_LLM_API_KEY` - OpenAI API key (or compatible provider)

### Supabase (for RAG)
- `IPAI_SUPABASE_URL` - e.g., `https://<project>.supabase.co`
- `IPAI_SUPABASE_SERVICE_ROLE_KEY` - Service role key (preferred)
- `IPAI_SUPABASE_ANON_KEY` - Anon key (fallback)

### Optional
- `IPAI_LLM_BASE_URL` - Default: `https://api.openai.com/v1`
- `IPAI_LLM_MODEL` - Default: `gpt-4o-mini`
- `IPAI_LLM_TEMPERATURE` - Default: `0.2`
- `IPAI_KB_RPC_EMBEDDING` - Default: `kb.search_chunks`
- `IPAI_KB_RPC_TEXT` - Default: `kb.search_chunks_text`

### Embeddings (optional; enables vector RPC)
- `IPAI_EMBEDDINGS_PROVIDER` - Set to `openai` to enable
- `IPAI_EMBEDDINGS_MODEL` - Default: `text-embedding-3-small`
- `IPAI_EMBEDDINGS_BASE_URL` - Defaults to `IPAI_LLM_BASE_URL`
- `IPAI_EMBEDDINGS_API_KEY` - Defaults to `IPAI_LLM_API_KEY`

## Supabase RPC Expectations

### Vector RPC (recommended)
```sql
-- POST /rest/v1/rpc/kb.search_chunks
-- Payload: { tenant_ref, query_embedding, limit }
-- Returns: { id, title, url, content, score }[]
```

### Text Fallback RPC
```sql
-- POST /rest/v1/rpc/kb.search_chunks_text
-- Payload: { tenant_ref, query, limit }
-- Returns: { id, title, url, content, score }[]
```

## API Endpoints

### Bootstrap (GET agents)
```
POST /ipai_ai_agents/bootstrap
```
Returns available agents for the current user/company.

### Ask (RAG + LLM)
```
POST /ipai_ai_agents/ask
{
  "agent_id": 1,
  "message": "How do I create a sales order?",
  "thread_id": null  // optional, for continuing conversation
}
```

### Feedback
```
POST /ipai_ai_agents/feedback
{
  "message_id": 123,
  "feedback": "positive",
  "reason": "Very helpful!"
}
```

### List Threads
```
POST /ipai_ai_agents/threads
{
  "agent_id": null,  // optional filter
  "limit": 20,
  "offset": 0
}
```

## Install

1. Add addon to addons-path
2. Update apps list
3. Install "IPAI AI Agents (CE/OCA 18)"
4. Configure environment variables
5. Access AI → Ask AI from the menu

## Dependencies

- `base`
- `web`
- `mail`
- Python: `requests`

## Related Modules

- `ipai_ai_agents_ui` - React/Fluent UI panel (optional enhanced UI)
- `ipai_ai_connectors` - Inbound integration events
- `ipai_ai_sources_odoo` - Export Odoo data to Supabase KB
