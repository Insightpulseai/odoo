# Supabase Features Overview

**Source:** https://supabase.com/docs
**Status:** Production Ready (2025)
**IPAI Project ID:** spdtwktxdalcfigzeqrz

---

## Core Features

Supabase is the Postgres development platform that provides:

- PostgreSQL Database
- Authentication (GoTrue)
- Instant APIs (PostgREST)
- Edge Functions (Deno)
- Realtime subscriptions
- Storage
- Vector embeddings

---

## PostgreSQL Database

### Managed PostgreSQL

| Feature | Details |
|---------|---------|
| Engine | Full PostgreSQL |
| Connection pooling | PgBouncer |
| Compute | Configurable |
| Disk | Configurable type + IOPS |
| Access | Direct Postgres connections |

### Extensions Supported

- pgvector (vector embeddings)
- PostGIS
- pg_graphql
- pg_cron
- And 40+ more

---

## Authentication (GoTrue)

### Authentication Methods

| Method | Status |
|--------|--------|
| Email/Password | Supported |
| Magic Links | Supported |
| OAuth (Google, GitHub, Apple, etc.) | Supported |
| SSO (SAML) | Supported |
| Phone/SMS | Via third-party |

### Row Level Security (RLS)

```sql
-- Example: Users can only see their own data
CREATE POLICY "Users view own data" ON documents
  FOR SELECT
  USING (auth.uid() = user_id);

-- Example: Authenticated users can insert
CREATE POLICY "Auth users can insert" ON documents
  FOR INSERT
  WITH CHECK (auth.role() = 'authenticated');
```

---

## Real-time Features

### Capabilities

| Feature | Description |
|---------|-------------|
| Postgres Changes | Listen to INSERTs, UPDATEs, DELETEs |
| Broadcast | Send messages between users |
| Presence | Track online users |

### Implementation

```javascript
// Subscribe to database changes
const subscription = supabase
  .channel('table-changes')
  .on('postgres_changes',
    { event: '*', schema: 'public', table: 'messages' },
    (payload) => console.log(payload)
  )
  .subscribe();
```

---

## Edge Functions

### Overview

- Globally distributed TypeScript functions
- Deno runtime
- NPM module support
- Node built-in API support

### Use Cases

| Use Case | Example |
|----------|---------|
| HTTP endpoints | REST APIs |
| Webhooks | Stripe, GitHub |
| Image generation | OG images |
| AI inference | OpenAI orchestration |

### Example

```typescript
// supabase/functions/hello/index.ts
import { serve } from 'https://deno.land/std@0.168.0/http/server.ts';

serve(async (req) => {
  const { name } = await req.json();
  return new Response(
    JSON.stringify({ message: `Hello ${name}!` }),
    { headers: { 'Content-Type': 'application/json' } }
  );
});
```

### 2025 Updates

- Create/update Edge Functions from dashboard
- New "Code" tab for viewing/editing
- Edge Function tester (Postman-like)

---

## Vector Storage (2025)

### Vector Buckets (Public Alpha)

- Store vector embeddings at scale
- Index and query embeddings
- Ideal for AI/ML applications

```sql
-- Example: Create vector column
ALTER TABLE documents
ADD COLUMN embedding vector(1536);

-- Example: Similarity search
SELECT * FROM documents
ORDER BY embedding <-> query_embedding
LIMIT 5;
```

---

## Storage

### Features

| Feature | Details |
|---------|---------|
| File storage | S3-compatible |
| CDN | Global distribution |
| Transformations | Image resize, format conversion |
| Access control | RLS policies |

---

## Pricing (2025)

| Plan | Price | Includes |
|------|-------|----------|
| Free | $0 | 500MB DB, 50K MAU |
| Pro | $25/month | 8GB DB, 100K MAU, compute credits |
| Team | $599/month | Enhanced support, SLA |
| Enterprise | Custom | Dedicated resources |

---

## IPAI Integration Points

### Current Usage (per CLAUDE.md)

```
Supabase: spdtwktxdalcfigzeqrz (external integrations only)

Note: Odoo uses local PostgreSQL, NOT Supabase
Supabase is only for n8n workflows, task bus, external integrations
```

### Integration Architecture

```
┌─────────────────────────────────────────┐
│           IPAI Stack                     │
├─────────────────────────────────────────┤
│  Odoo CE ◄──► PostgreSQL 15 (local)     │
│     │                                    │
│     └──► n8n ◄──► Supabase              │
│              │      ├── Task bus        │
│              │      ├── Webhooks        │
│              │      └── External APIs   │
│              │                          │
│              └──► AI Agents             │
└─────────────────────────────────────────┘
```

### Recommended Supabase Uses

1. **Task Bus:** Async job queue via Postgres
2. **n8n Workflows:** Webhook endpoints, data storage
3. **AI Embeddings:** Vector storage for RAG
4. **External APIs:** Third-party integrations

### NOT Recommended

- Odoo transactional data (use local PG)
- High-frequency Odoo writes
- Core business logic

---

## Sources

- [Supabase Home](https://supabase.com/)
- [Supabase Features](https://supabase.com/features)
- [Supabase Docs - Features](https://supabase.com/docs/guides/getting-started/features)
- [Edge Functions](https://supabase.com/docs/guides/functions)
- [Supabase Changelog](https://supabase.com/changelog)
- [Supabase GitHub](https://github.com/supabase/supabase)
