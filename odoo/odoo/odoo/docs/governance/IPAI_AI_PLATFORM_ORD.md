# IPAI AI Platform - Object Relationship Document (ORD)

## Overview

This document defines the core objects, their ownership patterns, relationships, and lifecycles for the IPAI AI Platform.

## Object Inventory

### Core AI Objects

| Object | Model | Module | Purpose |
|--------|-------|--------|---------|
| Provider | `ipai.ai.provider` | ipai_ai_core | AI provider configuration |
| Thread | `ipai.ai.thread` | ipai_ai_core | Conversation container |
| Message | `ipai.ai.message` | ipai_ai_core | Individual message in thread |
| Citation | `ipai.ai.citation` | ipai_ai_core | Source reference for message |

### Agent Objects

| Object | Model | Module | Purpose |
|--------|-------|--------|---------|
| Skill | `ipai.agent.skill` | ipai_agent_core | Workflow definition |
| Tool | `ipai.agent.tool` | ipai_agent_core | Callable action |
| Knowledge Source | `ipai.agent.knowledge.source` | ipai_agent_core | Context source |
| Run | `ipai.agent.run` | ipai_agent_core | Execution record |

### Integration Objects

| Object | Model | Module | Purpose |
|--------|-------|--------|---------|
| Event | `ipai.ai.event` | ipai_ai_connectors | Inbound integration event |
| Export Run | `ipai.kb.export.run` | ipai_ai_sources_odoo | KB export audit |

### External Objects

| Object | Table | Location | Purpose |
|--------|-------|----------|---------|
| KB Chunk | `kb.chunks` | Supabase | Searchable knowledge chunk |

## Ownership & Access Patterns

### Provider (`ipai.ai.provider`)

```
Ownership: Company-scoped
  - Each provider belongs to one company
  - One provider can be marked as default per company

Access Rules:
  - Users can read providers in their company
  - Only admins can create/modify providers

Relationships:
  - company_id → res.company (required)
  - Threads reference provider_id
```

### Thread (`ipai.ai.thread`)

```
Ownership: User-owned, Company-scoped
  - Created by user, belongs to user
  - Company inherited from provider

Access Rules:
  - Users can only access their own threads
  - Record rule: [('user_id', '=', user.id)]

Relationships:
  - provider_id → ipai.ai.provider (required)
  - user_id → res.users (required)
  - message_ids → ipai.ai.message (O2M)
```

### Message (`ipai.ai.message`)

```
Ownership: Thread-owned
  - Belongs to parent thread
  - Access follows thread ownership

Access Rules:
  - Users can access messages in their threads
  - Record rule: [('thread_id.user_id', '=', user.id)]

Relationships:
  - thread_id → ipai.ai.thread (required, cascade delete)
  - citation_ids → ipai.ai.citation (O2M)
```

### Citation (`ipai.ai.citation`)

```
Ownership: Message-owned
  - Belongs to parent message
  - Access follows message/thread ownership

Access Rules:
  - Follows message access rules

Relationships:
  - message_id → ipai.ai.message (required, cascade delete)
```

### Event (`ipai.ai.event`)

```
Ownership: Company-scoped
  - Events are company-isolated
  - Created by webhook, managed by admins

Access Rules:
  - Viewers: Read only
  - Managers: Full CRUD
  - System: Full access

Relationships:
  - company_id → res.company (required)
```

### Export Run (`ipai.kb.export.run`)

```
Ownership: Company-scoped
  - Created by cron job
  - Audit trail for exports

Access Rules:
  - Users: Read only
  - System: Full access

Relationships:
  - company_id → res.company (required)
```

### KB Chunk (Supabase)

```
Ownership: Tenant-scoped
  - tenant_ref = "odoo_company:{id}"
  - Managed by exporter cron

Access Rules (RLS):
  - Service role: Full access
  - Authenticated: Read own tenant only

Key:
  - Unique on (tenant_ref, source_type, source_ref)
```

## Lifecycle Diagrams

### Thread Lifecycle

```
                    ┌───────────┐
                    │   NEW     │
                    │  (Create) │
                    └─────┬─────┘
                          │
                          ▼
                    ┌───────────┐
                    │  ACTIVE   │
                    │           │◄──────┐
                    └─────┬─────┘       │
                          │             │
              ┌───────────┴───────────┐ │
              │                       │ │
              ▼                       ▼ │
        ┌───────────┐           ┌─────────┐
        │  CLOSED   │           │ Message │
        │           │           │  Added  │
        └───────────┘           └─────────┘

States:
  - active: Thread is in use
  - closed: Thread is archived (optional)

Transitions:
  - Create → Active (on first message)
  - Active → Closed (manual or auto-archive)
  - Messages can be added while Active
```

### Message Lifecycle

```
        ┌─────────────────────────────────────┐
        │           Thread Active             │
        └──────────────────┬──────────────────┘
                           │
                           ▼
                    ┌───────────┐
                    │  CREATE   │
                    │  Message  │
                    └─────┬─────┘
                          │
              ┌───────────┴───────────┐
              │                       │
              ▼                       ▼
        ┌───────────┐           ┌───────────┐
        │   USER    │           │ ASSISTANT │
        │  Message  │           │  Message  │
        └───────────┘           └─────┬─────┘
                                      │
                                      ▼
                                ┌───────────┐
                                │ Citations │
                                │  Added    │
                                └───────────┘

Message Types:
  - user: From human user
  - assistant: From AI
  - system: System-generated

Properties:
  - Immutable after creation
  - Citations added with assistant messages
```

### Event Lifecycle

```
        ┌─────────────────────────────────────┐
        │         Webhook Received            │
        └──────────────────┬──────────────────┘
                           │
                           ▼
                    ┌───────────┐
                    │ RECEIVED  │
                    └─────┬─────┘
                          │
          ┌───────────────┼───────────────┐
          │               │               │
          ▼               ▼               ▼
    ┌───────────┐   ┌───────────┐   ┌───────────┐
    │ PROCESSING│   │  IGNORED  │   │  (Future) │
    │           │   │           │   │  Handler  │
    └─────┬─────┘   └───────────┘   └───────────┘
          │
    ┌─────┴─────┐
    │           │
    ▼           ▼
┌───────────┐ ┌───────────┐
│ PROCESSED │ │  FAILED   │
│           │ │           │
└───────────┘ └───────────┘

States:
  - received: Event logged, awaiting processing
  - processing: Handler is working
  - processed: Successfully handled
  - failed: Handler error (see error_message)
  - ignored: Marked as not needed
```

### Export Run Lifecycle

```
        ┌─────────────────────────────────────┐
        │          Cron Triggered             │
        └──────────────────┬──────────────────┘
                           │
                           ▼
                    ┌───────────┐
                    │  RUNNING  │
                    └─────┬─────┘
                          │
                    ┌─────┴─────┐
                    │           │
                    ▼           ▼
              ┌───────────┐ ┌───────────┐
              │  SUCCESS  │ │  FAILED   │
              └───────────┘ └───────────┘

States:
  - running: Export in progress
  - success: Completed successfully
  - failed: Error occurred (see error_message)

Properties:
  - chunks_count: Number of chunks exported
  - duration_seconds: Time taken
```

## Data Integrity Rules

### Cascade Deletes

| Parent | Child | Behavior |
|--------|-------|----------|
| Thread | Message | CASCADE (delete messages) |
| Message | Citation | CASCADE (delete citations) |
| Provider | Thread | RESTRICT (cannot delete used provider) |

### Required Fields

| Object | Required Fields |
|--------|----------------|
| Provider | name, provider_type, company_id |
| Thread | provider_id, user_id |
| Message | thread_id, role, content |
| Citation | message_id |
| Event | source, event_type, company_id |
| Export Run | company_id |

### Constraints

| Object | Constraint | Description |
|--------|------------|-------------|
| Provider | Single default | Only one is_default per company |
| KB Chunk | Unique key | (tenant_ref, source_type, source_ref) |
| Event | Valid source | source ∈ {n8n, github, slack, custom} |

## Query Patterns

### Common Queries

**Get user's threads:**
```python
threads = env['ipai.ai.thread'].search([
    ('user_id', '=', user.id),
    ('state', '=', 'active'),
])
```

**Get thread messages with citations:**
```python
messages = thread.message_ids.sorted('create_date')
for msg in messages:
    citations = msg.citation_ids.sorted('rank')
```

**Get recent export runs:**
```python
runs = env['ipai.kb.export.run'].search([
    ('company_id', '=', company.id),
    ('started_at', '>=', since),
], order='started_at desc')
```

**Get pending events:**
```python
events = env['ipai.ai.event'].search([
    ('state', '=', 'received'),
    ('company_id', '=', company.id),
])
```

### Performance Indexes

| Table | Index | Columns |
|-------|-------|---------|
| ipai_ai_thread | thread_user_idx | user_id |
| ipai_ai_thread | thread_provider_idx | provider_id |
| ipai_ai_message | message_thread_idx | thread_id |
| ipai_ai_citation | citation_message_idx | message_id |
| ipai_ai_event | event_source_type_idx | source, event_type |
| ipai_ai_event | event_state_idx | state |
| kb.chunks | kb_chunks_tenant_idx | tenant_ref |
| kb.chunks | kb_chunks_embedding_idx | embedding (ivfflat) |

## Security Considerations

### Data Classification

| Object | Sensitivity | Notes |
|--------|-------------|-------|
| Thread/Message | User data | Contains user conversations |
| Citation | Reference | Points to source documents |
| Event | Integration | External system payloads |
| KB Chunk | Company data | Indexed business content |

### Access Control Summary

| Role | Threads | Messages | Events | Export Runs |
|------|---------|----------|--------|-------------|
| User | Own only | Own only | - | Read |
| Manager | - | - | Full | Read |
| System | Full | Full | Full | Full |

### Audit Requirements

- All message creates are timestamped
- Export runs track success/failure
- Events provide webhook audit trail
- Provider stats track usage
