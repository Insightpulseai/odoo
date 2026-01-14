-- ═══════════════════════════════════════════════════════════════════════════════
-- IPAI Memory Schema - Supabase Integration
-- ═══════════════════════════════════════════════════════════════════════════════
-- Purpose: Central memory store for AI agents (Claude/Codex) with vector search
-- Stack: Supabase Postgres + pgvector + Superset + n8n + MCP
-- ═══════════════════════════════════════════════════════════════════════════════

-- Enable required extensions
create extension if not exists "uuid-ossp";
create extension if not exists "vector";
create extension if not exists "pg_cron";
create extension if not exists "pg_stat_statements";

-- Create dedicated schema
create schema if not exists ipai_memory;

-- ═══════════════════════════════════════════════════════════════════════════════
-- Core Tables
-- ═══════════════════════════════════════════════════════════════════════════════

-- Sessions: one run/conversation/task
create table if not exists ipai_memory.sessions (
  id uuid primary key default gen_random_uuid(),
  agent_id text not null,              -- 'odoo-sandbox', 'superset-analyst', 'n8n-orchestrator'
  source text not null,                -- 'claude-web', 'codex-cli', 'mcp-server'
  started_at timestamptz not null default now(),
  finished_at timestamptz,
  topic text,                          -- short title/tag
  raw_tokens_est int,                  -- estimated context usage
  notes text,                          -- freeform summary
  metadata jsonb default '{}'::jsonb   -- additional context
);

-- Chunks: retrievable memory units (structured)
create table if not exists ipai_memory.chunks (
  id uuid primary key default gen_random_uuid(),
  session_id uuid not null references ipai_memory.sessions(id) on delete cascade,
  topic text not null,                 -- 'odoo-sandbox-baseline', 'mailgun-config'
  content text not null,               -- actual memory snippet/summary
  importance smallint default 1,       -- 1-5 scoring for retrieval priority
  created_at timestamptz not null default now(),
  metadata jsonb default '{}'::jsonb
);

-- Embeddings: vector representations for semantic search
create table if not exists ipai_memory.chunk_embeddings (
  chunk_id uuid primary key references ipai_memory.chunks(id) on delete cascade,
  embedding vector(1536),              -- OpenAI text-embedding-3-small dimension
  model text not null,                 -- 'text-embedding-3-small', 'text-embedding-3-large'
  created_at timestamptz not null default now()
);

-- Distilled: long-term stable knowledge (human-curated)
create table if not exists ipai_memory.distilled (
  id uuid primary key default gen_random_uuid(),
  topic text not null unique,          -- canonical topic name
  content text not null,               -- markdown summary
  source_chunks uuid[],                -- array of chunk IDs that contributed
  last_updated timestamptz not null default now(),
  metadata jsonb default '{}'::jsonb
);

-- ═══════════════════════════════════════════════════════════════════════════════
-- Indexes (Performance)
-- ═══════════════════════════════════════════════════════════════════════════════

-- Vector similarity search (IVFFlat for embeddings <1M rows)
create index if not exists idx_chunk_embeddings_vector
  on ipai_memory.chunk_embeddings
  using ivfflat (embedding vector_cosine_ops)
  with (lists = 100);

-- Text search on content
create index if not exists idx_chunks_content_gin
  on ipai_memory.chunks
  using gin(to_tsvector('english', content));

-- Session lookups
create index if not exists idx_sessions_agent_started
  on ipai_memory.sessions(agent_id, started_at desc);

-- Topic lookups
create index if not exists idx_chunks_topic
  on ipai_memory.chunks(topic);

-- ═══════════════════════════════════════════════════════════════════════════════
-- Functions (RPC API for MCP/n8n)
-- ═══════════════════════════════════════════════════════════════════════════════

-- Add memory chunk with optional embedding
create or replace function ipai_memory.add_memory(
  p_agent_id text,
  p_topic text,
  p_content text,
  p_importance int default 3,
  p_embedding vector default null,
  p_model text default null
) returns uuid as $$
declare
  v_session_id uuid;
  v_chunk_id uuid;
begin
  -- Create session if none exists for this agent/topic in last 5 minutes
  select id into v_session_id
  from ipai_memory.sessions
  where agent_id = p_agent_id
    and topic = p_topic
    and started_at > now() - interval '5 minutes'
  order by started_at desc
  limit 1;

  if v_session_id is null then
    insert into ipai_memory.sessions (agent_id, source, topic)
    values (p_agent_id, 'rpc', p_topic)
    returning id into v_session_id;
  end if;

  -- Insert chunk
  insert into ipai_memory.chunks (session_id, topic, content, importance)
  values (v_session_id, p_topic, p_content, p_importance)
  returning id into v_chunk_id;

  -- Insert embedding if provided
  if p_embedding is not null and p_model is not null then
    insert into ipai_memory.chunk_embeddings (chunk_id, embedding, model)
    values (v_chunk_id, p_embedding, p_model);
  end if;

  return v_chunk_id;
end;
$$ language plpgsql security definer;

-- Search memory (hybrid: vector + keyword)
create or replace function ipai_memory.search_memory(
  p_query_vector vector default null,
  p_query_text text default null,
  p_topic_filter text default null,
  p_limit int default 8
) returns table (
  chunk_id uuid,
  topic text,
  content text,
  importance smallint,
  created_at timestamptz,
  similarity_score float,
  metadata jsonb
) as $$
begin
  return query
  with vector_results as (
    select
      c.id,
      c.topic,
      c.content,
      c.importance,
      c.created_at,
      1 - (e.embedding <=> p_query_vector) as vector_score,
      c.metadata
    from ipai_memory.chunks c
    join ipai_memory.chunk_embeddings e on c.id = e.chunk_id
    where (p_topic_filter is null or c.topic = p_topic_filter)
      and p_query_vector is not null
    order by e.embedding <=> p_query_vector
    limit p_limit
  ),
  text_results as (
    select
      c.id,
      c.topic,
      c.content,
      c.importance,
      c.created_at,
      ts_rank(to_tsvector('english', c.content), plainto_tsquery('english', p_query_text)) as text_score,
      c.metadata
    from ipai_memory.chunks c
    where (p_topic_filter is null or c.topic = p_topic_filter)
      and p_query_text is not null
    order by text_score desc
    limit p_limit
  )
  select
    coalesce(v.id, t.id),
    coalesce(v.topic, t.topic),
    coalesce(v.content, t.content),
    coalesce(v.importance, t.importance),
    coalesce(v.created_at, t.created_at),
    coalesce(v.vector_score, 0) + coalesce(t.text_score, 0) as combined_score,
    coalesce(v.metadata, t.metadata)
  from vector_results v
  full outer join text_results t on v.id = t.id
  order by combined_score desc
  limit p_limit;
end;
$$ language plpgsql security definer;

-- List recent memories for agent
create or replace function ipai_memory.list_agent_memories(
  p_agent_id text,
  p_limit int default 20
) returns table (
  chunk_id uuid,
  topic text,
  content text,
  created_at timestamptz
) as $$
begin
  return query
  select
    c.id,
    c.topic,
    c.content,
    c.created_at
  from ipai_memory.chunks c
  join ipai_memory.sessions s on c.session_id = s.id
  where s.agent_id = p_agent_id
  order by c.created_at desc
  limit p_limit;
end;
$$ language plpgsql security definer;

-- ═══════════════════════════════════════════════════════════════════════════════
-- Views (Superset Analytics)
-- ═══════════════════════════════════════════════════════════════════════════════

-- Memory activity by agent
create or replace view ipai_memory.v_agent_activity as
select
  s.agent_id,
  count(distinct s.id) as session_count,
  count(c.id) as chunk_count,
  max(s.started_at) as last_active,
  count(distinct c.topic) as unique_topics
from ipai_memory.sessions s
left join ipai_memory.chunks c on s.id = c.session_id
group by s.agent_id;

-- Recent memory timeline
create or replace view ipai_memory.v_recent_memories as
select
  c.id as chunk_id,
  s.agent_id,
  c.topic,
  left(c.content, 200) as content_preview,
  c.importance,
  c.created_at,
  case when e.chunk_id is not null then true else false end as has_embedding
from ipai_memory.chunks c
join ipai_memory.sessions s on c.session_id = s.id
left join ipai_memory.chunk_embeddings e on c.id = e.chunk_id
order by c.created_at desc
limit 100;

-- Topic coverage
create or replace view ipai_memory.v_topic_coverage as
select
  topic,
  count(*) as chunk_count,
  avg(importance) as avg_importance,
  min(created_at) as first_seen,
  max(created_at) as last_updated
from ipai_memory.chunks
group by topic
order by chunk_count desc;

-- ═══════════════════════════════════════════════════════════════════════════════
-- Security (RLS + Roles)
-- ═══════════════════════════════════════════════════════════════════════════════

-- Create service roles
do $$
begin
  if not exists (select 1 from pg_roles where rolname = 'superset_readonly') then
    create role superset_readonly noinherit;
  end if;
  if not exists (select 1 from pg_roles where rolname = 'n8n_service') then
    create role n8n_service noinherit;
  end if;
  if not exists (select 1 from pg_roles where rolname = 'mcp_agent') then
    create role mcp_agent noinherit;
  end if;
end $$;

-- Grant permissions
grant usage on schema ipai_memory to superset_readonly, n8n_service, mcp_agent;

-- Superset: read-only
grant select on all tables in schema ipai_memory to superset_readonly;
grant select on all views in schema ipai_memory to superset_readonly;
alter default privileges in schema ipai_memory grant select on tables to superset_readonly;

-- n8n: read + write (ETL)
grant select, insert, update on all tables in schema ipai_memory to n8n_service;
grant execute on all functions in schema ipai_memory to n8n_service;

-- MCP: read + write via functions only
grant execute on function ipai_memory.add_memory to mcp_agent;
grant execute on function ipai_memory.search_memory to mcp_agent;
grant execute on function ipai_memory.list_agent_memories to mcp_agent;

-- Enable RLS on chunks (optional: per-agent isolation)
alter table ipai_memory.chunks enable row level security;

-- Policy: agents see only their own memories (via session)
create policy agent_isolation on ipai_memory.chunks
  for select
  using (
    session_id in (
      select id from ipai_memory.sessions
      where agent_id = current_setting('app.agent_id', true)
    )
  );

-- ═══════════════════════════════════════════════════════════════════════════════
-- Maintenance (pg_cron jobs)
-- ═══════════════════════════════════════════════════════════════════════════════

-- Auto-vacuum old sessions (>30 days, no distilled refs)
select cron.schedule(
  'vacuum-old-sessions',
  '0 2 * * *',  -- daily at 2 AM
  $$
  delete from ipai_memory.sessions
  where finished_at < now() - interval '30 days'
    and id not in (
      select unnest(source_chunks) from ipai_memory.distilled
    );
  $$
);

-- Refresh materialized view stats (if added later)
-- select cron.schedule('refresh-memory-stats', '0 * * * *', 'refresh materialized view ipai_memory.mv_stats;');

-- ═══════════════════════════════════════════════════════════════════════════════
-- Comments (Documentation)
-- ═══════════════════════════════════════════════════════════════════════════════

comment on schema ipai_memory is 'Central AI agent memory store with vector search';
comment on table ipai_memory.sessions is 'Agent execution sessions (one per conversation/task)';
comment on table ipai_memory.chunks is 'Retrievable memory units (structured notes)';
comment on table ipai_memory.chunk_embeddings is 'Vector embeddings for semantic search';
comment on table ipai_memory.distilled is 'Curated long-term knowledge (human-reviewed)';

comment on function ipai_memory.add_memory is 'RPC: Add memory chunk with optional embedding';
comment on function ipai_memory.search_memory is 'RPC: Hybrid vector+text search for retrieval';
comment on function ipai_memory.list_agent_memories is 'RPC: List recent memories for agent';

-- ═══════════════════════════════════════════════════════════════════════════════
-- Verification
-- ═══════════════════════════════════════════════════════════════════════════════

-- Test add_memory function
do $$
declare
  v_chunk_id uuid;
begin
  -- Add test memory
  select ipai_memory.add_memory(
    p_agent_id := 'odoo-dev-sandbox',
    p_topic := 'sandbox-baseline',
    p_content := 'Odoo 18 CE sandbox: http://localhost:8069/web/login, DB: odoo_dev_sandbox, Custom module: ipai_hello only',
    p_importance := 5
  ) into v_chunk_id;

  raise notice 'Test memory added: %', v_chunk_id;
end $$;

-- Verify tables created
select
  schemaname,
  tablename,
  rowsecurity
from pg_tables
where schemaname = 'ipai_memory'
order by tablename;

-- Verify functions created
select
  routine_schema,
  routine_name,
  routine_type
from information_schema.routines
where routine_schema = 'ipai_memory'
order by routine_name;
