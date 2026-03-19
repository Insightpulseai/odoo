# Object Relationship Document (ORD)

## IPAI AI Platform for Odoo CE/OCA 18

**Version**: 1.0.0
**Last Updated**: 2025-01-06

---

## Document Purpose

This Object Relationship Document (ORD) defines the core objects, their attributes, ownership, relationships, and lifecycle management for the IPAI AI Platform.

---

## 1. Domain Overview

### 1.1 Domain Boundaries

The IPAI AI Platform spans three primary domains:

| Domain | Purpose | Primary Tables |
|--------|---------|----------------|
| **AI Core** | Provider management, conversation threads, messages | `ipai_ai_provider`, `ipai_ai_thread`, `ipai_ai_message`, `ipai_ai_citation` |
| **Integrations** | External event intake, knowledge indexing | `ipai_ai_event`, `kb_chunks` (Supabase) |
| **Workspaces** | Team organization, access control | `ipai_workspace`, `ipai_workspace_member` |

### 1.2 External Dependencies

| System | Purpose | Interface |
|--------|---------|-----------|
| Supabase | Knowledge base storage, vector search | REST API / RPCs |
| LLM Provider | Text generation | OpenAI-compatible API |
| n8n | Integration workflows | Webhooks |

---

## 2. Object Definitions

### 2.1 AI Provider (`ipai.ai.provider`)

**Purpose**: Registry of AI service providers with configuration and statistics.

#### Attributes

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | Integer | Auto | Primary key |
| `name` | Char | Yes | Display name |
| `sequence` | Integer | No | Ordering (default: 10) |
| `provider_type` | Selection | Yes | `kapa`, `openai`, `anthropic`, `ollama` |
| `active` | Boolean | No | Soft delete (default: True) |
| `company_id` | Many2one | Yes | Parent company |
| `is_default` | Boolean | No | Default for company (default: False) |
| `total_requests` | Integer | No | Statistics counter |
| `total_tokens` | Integer | No | Token usage counter |
| `avg_latency_ms` | Float | No | Average response time |

#### Constraints

- Only one `is_default=True` per `company_id`
- `provider_type` must be from allowed selection

#### Ownership

- **Created by**: System admins
- **Managed by**: Company-level AI admins
- **Access**: Read by all users in company

#### Lifecycle

1. **Creation**: Admin creates provider with configuration
2. **Active**: Provider serves requests, statistics updated
3. **Inactive**: `active=False`, no new requests
4. **Deletion**: Restricted if threads exist (cascade protection)

---

### 2.2 AI Thread (`ipai.ai.thread`)

**Purpose**: Conversation container for a user's interaction with an AI provider.

#### Attributes

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | Integer | Auto | Primary key |
| `name` | Char | Computed | First 50 chars of first user message |
| `provider_id` | Many2one | Yes | AI provider |
| `company_id` | Many2one | Related | From provider |
| `external_thread_id` | Char | No | External provider thread ID |
| `user_id` | Many2one | Yes | Thread owner |
| `state` | Selection | No | `active`, `closed` (default: active) |
| `message_count` | Integer | Computed | Number of messages |

#### Relationships

- **Belongs to**: `ipai.ai.provider`, `res.users`
- **Has many**: `ipai.ai.message`
- **Inherits**: `mail.thread` (for activity tracking)

#### Ownership

- **Created by**: User (via API)
- **Owned by**: `user_id`
- **Access**: Only owner can access (record rules)

#### Lifecycle

1. **Creation**: Automatic on first message
2. **Active**: Conversation ongoing
3. **Closed**: User explicitly closes or inactivity timeout
4. **Deletion**: Cascade deletes messages

---

### 2.3 AI Message (`ipai.ai.message`)

**Purpose**: Individual message in a conversation thread.

#### Attributes

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | Integer | Auto | Primary key |
| `thread_id` | Many2one | Yes | Parent thread |
| `role` | Selection | Yes | `user`, `assistant`, `system` |
| `content` | Text | Yes | Message content |
| `provider_latency_ms` | Integer | No | Response time (assistant only) |
| `provider_status` | Char | No | HTTP status or error code |
| `confidence` | Float | No | 0.0 to 1.0 (assistant only) |
| `tokens_used` | Integer | No | Token count |
| `citation_count` | Integer | Computed | Number of citations |

#### Relationships

- **Belongs to**: `ipai.ai.thread`
- **Has many**: `ipai.ai.citation`

#### Ownership

- **Created by**: System (via service layer)
- **Owned by**: Thread owner (via thread)
- **Access**: Only thread owner can access

#### Lifecycle

1. **Creation**: Appended to thread (immutable)
2. **Active**: Displayed in conversation
3. **Deletion**: Cascade from thread only

#### Business Rules

- Messages are **append-only** (no updates)
- `role='user'` messages created on user input
- `role='assistant'` messages created after LLM response
- `role='system'` messages for internal prompts (optional)

---

### 2.4 AI Citation (`ipai.ai.citation`)

**Purpose**: Source reference for an assistant message.

#### Attributes

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | Integer | Auto | Primary key |
| `message_id` | Many2one | Yes | Parent message |
| `rank` | Integer | No | Display order (default: 1) |
| `source_id` | Char | No | External source identifier |
| `title` | Char | No | Source title |
| `url` | Char | No | Source URL |
| `snippet` | Text | No | Relevant excerpt |
| `score` | Float | No | Relevance score |

#### Relationships

- **Belongs to**: `ipai.ai.message`

#### Ownership

- **Created by**: System (from RAG results)
- **Owned by**: Message owner (via thread)

#### Business Rules

- Citations ordered by `rank` ascending
- URLs must be valid when present
- Snippet limited to 500 characters

---

### 2.5 AI Prompt (`ipai.ai.prompt`)

**Purpose**: Reusable prompt templates for consistent AI interactions.

#### Attributes

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | Integer | Auto | Primary key |
| `name` | Char | Yes | Display name |
| `code` | Char | Yes | Unique lookup key |
| `template` | Text | Yes | Prompt template with variables |
| `variables_json` | Text | No | JSON array of variable names |
| `active` | Boolean | No | Active flag (default: True) |
| `company_id` | Many2one | No | Company scope (null = global) |

#### Variables Syntax

Templates use `{{variable_name}}` placeholders:

```
You are a helpful assistant for {{company_name}}.
The user is asking about: {{user_query}}
Use these sources: {{evidence}}
```

#### Ownership

- **Created by**: Admins
- **Access**: All users can read active prompts

---

### 2.6 AI Audit (`ipai.ai.audit`)

**Purpose**: Audit trail for all AI operations.

#### Attributes

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | Integer | Auto | Primary key |
| `operation` | Selection | Yes | `ask`, `search`, `feedback` |
| `provider_id` | Many2one | No | Provider used |
| `user_id` | Many2one | Yes | User performing operation |
| `thread_id` | Many2one | No | Related thread |
| `message_id` | Many2one | No | Related message |
| `request_json` | Text | No | Sanitized request payload |
| `response_json` | Text | No | Sanitized response payload |
| `latency_ms` | Integer | No | Operation duration |
| `status` | Selection | No | `success`, `error`, `timeout` |
| `error_message` | Text | No | Error details |

#### Retention

- Default: 90 days
- Configurable via system parameter
- PII redaction applied before storage

---

### 2.7 AI Event (`ipai.ai.event`)

**Purpose**: Inbound integration event log.

#### Attributes

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | Integer | Auto | Primary key |
| `source` | Char | Yes | Source system (`n8n`, `github`, `slack`) |
| `event_type` | Char | Yes | Event type (`push`, `issue.created`) |
| `ref` | Char | No | External reference ID |
| `payload_json` | Text | No | Full event payload |
| `processed` | Boolean | No | Processing flag (default: False) |
| `processed_date` | Datetime | No | When processed |
| `processor_id` | Many2one | No | Who processed |
| `notes` | Text | No | Processing notes |

#### Processing Flow

1. Event received via `/ipai_ai_connectors/event`
2. Token validated
3. Event persisted with `processed=False`
4. Optional: queue_job processes event
5. `processed=True` on completion

---

### 2.8 Workspace (`ipai.workspace`)

**Purpose**: Team space container (Notion teamspace equivalent).

#### Attributes

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | Integer | Auto | Primary key |
| `name` | Char | Yes | Space name |
| `description` | Text | No | Description |
| `visibility` | Selection | Yes | `private`, `internal`, `public` |
| `company_id` | Many2one | Yes | Company |
| `project_id` | Many2one | No | Linked project |
| `channel_id` | Many2one | No | Linked discuss channel |
| `active` | Boolean | No | Active flag |
| `create_uid` | Many2one | No | Creator |

#### Visibility Levels

| Level | Description |
|-------|-------------|
| `private` | Only explicit members |
| `internal` | All company employees |
| `public` | All authenticated users |

#### Auto-Created Components

On workspace creation:
1. `project.project` with matching name
2. `mail.channel` with matching name
3. `ipai.workspace.member` for creator as owner

---

### 2.9 Workspace Member (`ipai.workspace.member`)

**Purpose**: User membership in a workspace.

#### Attributes

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | Integer | Auto | Primary key |
| `workspace_id` | Many2one | Yes | Parent workspace |
| `user_id` | Many2one | Yes | Member user |
| `role` | Selection | Yes | `member`, `admin`, `owner` |

#### Role Permissions

| Role | Read | Write | Manage Members | Delete Space |
|------|------|-------|----------------|--------------|
| `member` | Yes | Yes | No | No |
| `admin` | Yes | Yes | Yes | No |
| `owner` | Yes | Yes | Yes | Yes |

---

### 2.10 KB Chunks (`kb.chunks`) - Supabase

**Purpose**: Vector-indexed content chunks for RAG retrieval.

#### Attributes

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | BigInt | Auto | Primary key |
| `tenant_ref` | Text | Yes | Tenant identifier (`odoo_company:1`) |
| `source_type` | Text | Yes | Source type (`odoo_task`, `odoo_kb`) |
| `source_ref` | Text | Yes | Source reference (`project.task:123`) |
| `title` | Text | No | Content title |
| `url` | Text | No | Source URL |
| `content` | Text | Yes | Chunk content |
| `embedding` | Vector(1536) | No | OpenAI embedding |
| `updated_at` | Timestamp | No | Last update |

#### Unique Constraint

`(tenant_ref, source_type, source_ref)` ensures upsert behavior.

#### Search RPCs

| RPC | Parameters | Returns |
|-----|------------|---------|
| `kb.search_chunks` | `tenant_ref`, `query_embedding`, `limit` | Rows with `score` |
| `kb.search_chunks_text` | `tenant_ref`, `query`, `limit` | Rows (fallback) |

---

## 3. Relationship Matrix

| From | To | Type | Description |
|------|----|------|-------------|
| `ipai_ai_thread` | `ipai_ai_provider` | Many2one | Thread uses provider |
| `ipai_ai_thread` | `res_users` | Many2one | Thread owned by user |
| `ipai_ai_message` | `ipai_ai_thread` | Many2one | Message in thread |
| `ipai_ai_citation` | `ipai_ai_message` | Many2one | Citation for message |
| `ipai_ai_audit` | `ipai_ai_provider` | Many2one | Audit tracks provider |
| `ipai_ai_audit` | `res_users` | Many2one | Audit by user |
| `ipai_workspace` | `res_company` | Many2one | Space in company |
| `ipai_workspace` | `project_project` | Many2one | Space has project |
| `ipai_workspace` | `mail_channel` | Many2one | Space has channel |
| `ipai_workspace_member` | `ipai_workspace` | Many2one | Member of space |
| `ipai_workspace_member` | `res_users` | Many2one | User is member |

---

## 4. Security Model

### 4.1 Record Rules

| Model | Rule | Domain |
|-------|------|--------|
| `ipai.ai.provider` | Company scope | `[('company_id', '=', user.company_id.id)]` |
| `ipai.ai.thread` | User only | `[('user_id', '=', user.id)]` |
| `ipai.ai.message` | Via thread | `[('thread_id.user_id', '=', user.id)]` |
| `ipai.ai.citation` | Via message | `[('message_id.thread_id.user_id', '=', user.id)]` |
| `ipai_workspace` | Membership | See complex rule below |

### 4.2 Workspace Access Rule

```python
# Private: only members
# Internal: all company users
# Public: all authenticated users
domain = """
    ['|',
        ('visibility', '=', 'public'),
        '|',
        '&', ('visibility', '=', 'internal'),
            ('company_id', '=', user.company_id.id),
        ('member_ids.user_id', '=', user.id)
    ]
"""
```

---

## 5. API Contracts

### 5.1 Odoo JSON-RPC Endpoints

| Endpoint | Method | Auth | Purpose |
|----------|--------|------|---------|
| `/ipai_ai/bootstrap` | POST | Session | Get agents, user context |
| `/ipai_ai/ask` | POST | Session | Submit question, get answer |
| `/ipai_ai/feedback` | POST | Session | Submit rating |
| `/ipai_ai_connectors/event` | POST | Token | Receive integration events |

### 5.2 Supabase RPCs

| RPC | Parameters | Returns |
|-----|------------|---------|
| `kb.search_chunks` | `tenant_ref`, `query_embedding`, `limit` | Matching chunks |
| `kb.search_chunks_text` | `tenant_ref`, `query`, `limit` | Text-matched chunks |

---

## 6. Change Log

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-01-06 | Initial ORD |

---

*End of Document*
