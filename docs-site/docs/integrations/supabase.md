# Supabase (Deprecated)

!!! warning "Fully deprecated 2026-03-26"
    Supabase is no longer used in the InsightPulse AI platform. All services have been replaced by Azure-native equivalents: Entra ID (auth), Azure Key Vault (secrets), Azure Container Apps (serverless functions), Databricks (pgvector/ML). This page is retained for historical reference only.

Supabase was the identity and real-time data authority for InsightPulse AI.

## Project reference

| Property | Value |
|----------|-------|
| **Project ID** | `spdtwktxdalcfigzeqrz` |
| **Role** | Auth identity, Edge Functions, Realtime, pgvector, Vault, Storage |

!!! warning "Deprecated Supabase projects"
    - `xkxyvboeubffxxbebsll` -- deprecated, do not use
    - `ublqmilcjtpnflofprkr` -- deprecated, do not use

## Ownership boundaries

Supabase **owns**:

- Auth identity (users, sessions, tokens)
- Edge Functions (serverless compute for integrations)
- Realtime (WebSocket subscriptions for live data)
- pgvector (operational embeddings for RAG)
- Vault (secret management for Edge Functions)
- Storage (file buckets for documents, attachments)

Supabase **does not own**:

- ERP data (Odoo owns all transactional records)
- Analytical data (ADLS owns the data lake)
- T&E data (SAP Concur is the system of record)

## Odoo as relying party

Odoo consumes a **minimal projection** of Supabase identity. The mirror contract defines exactly which fields Odoo may read:

| Field | Type | Source | Purpose |
|-------|------|--------|---------|
| `uuid` | UUID | Supabase Auth | Unique user identifier |
| `email` | string | Supabase Auth | User email address |
| `org_id` | UUID | Supabase custom claims | Organization / company mapping |
| `company_name` | string | Supabase custom claims | Display name for organization |
| `role` | string | Supabase custom claims | Role for access control |

!!! note "Minimal projection"
    Odoo stores only these fields in its `res.users` extension. All other identity data stays in Supabase.

## pgvector for operational RAG

Supabase pgvector serves **operational** use cases:

- Semantic search over documents and records
- Agent memory for AI assistants
- Real-time similarity matching

pgvector is **not** for analytical or historical embeddings. Use ADLS for those workloads.

```sql
-- Example: semantic search function
select * from match_documents(
  query_embedding := $1,
  match_threshold := 0.78,
  match_count := 10
);
```

## Security requirements

| Requirement | Implementation |
|-------------|----------------|
| Row-level security | RLS enabled on all tables with user/org policies |
| Function search path | All functions declare explicit `search_path` to prevent injection |
| API key rotation | Keys stored in Vault, rotated on schedule |
| Edge Function secrets | Bound via Vault references, never hardcoded |

## Features to activate

| Feature | Status | Purpose |
|---------|--------|---------|
| Realtime | Activate per table | Live subscriptions for dashboard updates |
| Storage | Activate buckets | Document and attachment storage |
| pg_cron | Enable extension | Scheduled database maintenance tasks |
