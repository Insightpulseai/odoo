# AI Agents & RAG

> **Slug**: `ai-agents`
> **Module**: `ipai_ai_agents`

## Overview

AI Agents provides Odoo 19-style "Ask AI" functionality for Odoo CE 18, with RAG (Retrieval-Augmented Generation) powered by Supabase and OpenAI-compatible LLMs.

## Features

- **AI Agents**: Configurable agents with custom system prompts
- **Knowledge Sources**: Connect docs sites, GitHub repos, PDFs
- **RAG Pipeline**: Retrieve evidence from Supabase KB, generate grounded answers
- **Citations**: Every answer includes source citations
- **Confidence Gating**: Uncertain responses are flagged
- **Feedback Loop**: Users can mark responses helpful/unhelpful

## Models

- `ipai.ai.agent` - Agent configuration and prompts
- `ipai.ai.thread` - Conversation threads
- `ipai.ai.message` - Individual messages with citations
- `ipai.ai.source` - Knowledge source definitions

## API Endpoints

### Bootstrap

```http
POST /ipai_ai_agents/bootstrap
```

Returns available agents for the current user.

### Ask

```http
POST /ipai_ai_agents/ask
Content-Type: application/json

{
  "agent_id": 1,
  "message": "How do I create a sales order?",
  "thread_id": null
}
```

### Feedback

```http
POST /ipai_ai_agents/feedback
Content-Type: application/json

{
  "message_id": 123,
  "feedback": "positive",
  "reason": "Very helpful!"
}
```

## Configuration

See [Configuration → AI Agents](Configuration#ai-agents) for setup instructions.

## Technical Details

- [Kapa-Plus Spec](../spec/kapa-plus/)
- [Kapa-Reverse Spec](../spec/kapa-reverse/)

## Dependencies

- `base`
- `web`
- `mail`

## Related Modules

- `ipai_ai_agents_ui` - React/Fluent UI panel
- `ipai_ai_connectors` - Inbound integration events
