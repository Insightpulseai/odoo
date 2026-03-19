-- =============================================================================
-- memory.* v1 — Agentic Long-Term + Semantic Memory Primitives
-- =============================================================================
-- Contract: platform/db/contracts/memory_contract.json
-- Requires: pgvector extension
-- Idempotent: safe to re-run (CREATE IF NOT EXISTS patterns throughout)
-- =============================================================================

create extension if not exists vector;

create schema if not exists memory;

-- =============================================================================
-- Custom Types
-- =============================================================================

do $$ begin
  if not exists (select 1 from pg_type where typname = 'memory_scope') then
    create type memory.memory_scope as enum ('global', 'tenant', 'user', 'session');
  end if;
  if not exists (select 1 from pg_type where typname = 'memory_kind') then
    create type memory.memory_kind as enum ('fact', 'preference', 'episode', 'chunk', 'cache');
  end if;
end $$;

-- =============================================================================
-- Core Table: memory.items
-- =============================================================================
-- Normalized table for facts, preferences, episodes, chunks, and cache entries.
-- Supports both structured (content_json) and semantic (embedding) retrieval.

create table if not exists memory.items (
  id uuid primary key default gen_random_uuid(),
  tenant_id uuid null,
  user_id uuid null,
  agent_id text not null,
  scope memory.memory_scope not null default 'tenant',
  kind memory.memory_kind not null,
  title text null,
  content text not null,
  content_json jsonb null,
  embedding vector(1536) null,
  metadata jsonb not null default '{}'::jsonb,
  source text null,
  score_hint real null,
  expires_at timestamptz null,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index if not exists memory_items_agent_kind_idx
  on memory.items (agent_id, kind, scope);

-- Vector index (ivfflat). Requires ANALYZE + enough rows to be effective.
create index if not exists memory_items_embedding_ivfflat
  on memory.items using ivfflat (embedding vector_cosine_ops) with (lists = 100);

-- TTL support index
create index if not exists memory_items_expires_at_idx
  on memory.items (expires_at) where expires_at is not null;

-- =============================================================================
-- Sessions Table: memory.sessions
-- =============================================================================
-- Anchors agent execution sessions for audit and context retrieval.

create table if not exists memory.sessions (
  id uuid primary key default gen_random_uuid(),
  tenant_id uuid null,
  user_id uuid null,
  agent_id text not null,
  started_at timestamptz not null default now(),
  ended_at timestamptz null,
  metadata jsonb not null default '{}'::jsonb
);

create index if not exists memory_sessions_agent_user_idx
  on memory.sessions (agent_id, user_id, started_at desc);

-- =============================================================================
-- Semantic Cache: memory.semantic_cache
-- =============================================================================
-- Prompt -> response caching with vector similarity for near-match retrieval.

create table if not exists memory.semantic_cache (
  id uuid primary key default gen_random_uuid(),
  tenant_id uuid null,
  agent_id text not null,
  prompt text not null,
  prompt_embedding vector(1536) not null,
  response text not null,
  metadata jsonb not null default '{}'::jsonb,
  hit_count bigint not null default 0,
  last_hit_at timestamptz null,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index if not exists memory_semantic_cache_agent_idx
  on memory.semantic_cache (agent_id, created_at desc);

create index if not exists memory_semantic_cache_embedding_ivfflat
  on memory.semantic_cache using ivfflat (prompt_embedding vector_cosine_ops) with (lists = 100);

-- =============================================================================
-- Updated-At Trigger
-- =============================================================================

create or replace function memory.set_updated_at()
returns trigger language plpgsql as $$
begin
  new.updated_at := now();
  return new;
end $$;

drop trigger if exists trg_memory_items_updated_at on memory.items;
create trigger trg_memory_items_updated_at
before update on memory.items
for each row execute function memory.set_updated_at();

drop trigger if exists trg_memory_cache_updated_at on memory.semantic_cache;
create trigger trg_memory_cache_updated_at
before update on memory.semantic_cache
for each row execute function memory.set_updated_at();

-- =============================================================================
-- Vector Retrieval Function: memory.search_items
-- =============================================================================
-- Standardized cosine-similarity search for agent memory retrieval.
-- RLS-safe: relies on table-level policies for tenant/user filtering.

create or replace function memory.search_items(
  p_agent_id text,
  p_query_embedding vector(1536),
  p_match_count int default 8,
  p_kind memory.memory_kind default null,
  p_scope memory.memory_scope default null
)
returns table (
  id uuid,
  agent_id text,
  kind memory.memory_kind,
  scope memory.memory_scope,
  title text,
  content text,
  metadata jsonb,
  similarity real
)
language sql stable as $$
  select
    i.id,
    i.agent_id,
    i.kind,
    i.scope,
    i.title,
    i.content,
    i.metadata,
    1 - (i.embedding <=> p_query_embedding) as similarity
  from memory.items i
  where i.agent_id = p_agent_id
    and (p_kind is null or i.kind = p_kind)
    and (p_scope is null or i.scope = p_scope)
    and i.embedding is not null
    and (i.expires_at is null or i.expires_at > now())
  order by i.embedding <=> p_query_embedding
  limit p_match_count;
$$;

-- =============================================================================
-- Row Level Security (RLS)
-- =============================================================================
-- IMPORTANT: These are placeholder policies. Wire to your canonical tenant
-- isolation strategy (JWT claims, mapping tables, etc.) before production.

alter table memory.items enable row level security;
alter table memory.sessions enable row level security;
alter table memory.semantic_cache enable row level security;

-- Permissive "owner-only" fallback policies.
-- user_id must match auth.uid() when set; null user_id = service-level access.
do $$ begin
  -- memory.items
  begin
    create policy memory_items_owner
    on memory.items
    for all
    using (user_id is null or user_id = auth.uid())
    with check (user_id is null or user_id = auth.uid());
  exception when duplicate_object then null;
  end;

  -- memory.sessions
  begin
    create policy memory_sessions_owner
    on memory.sessions
    for all
    using (user_id is null or user_id = auth.uid())
    with check (user_id is null or user_id = auth.uid());
  exception when duplicate_object then null;
  end;

  -- memory.semantic_cache (service-level: all agents can read/write)
  begin
    create policy memory_cache_service
    on memory.semantic_cache
    for all
    using (true)
    with check (true);
  exception when duplicate_object then null;
  end;
end $$;

-- =============================================================================
-- End of memory.* v1 migration
-- =============================================================================
