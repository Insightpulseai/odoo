-- Enable pgvector extension
create extension if not exists vector;

-- Create schema for docs
create schema if not exists docs;

-- Chunks table
create table if not exists docs.chunks (
  id bigserial primary key,
  source text not null,       -- e.g. "kb/finance_close/bir_1601c.md"
  url text,                   -- e.g. "internal://bir/1601c"
  title text,                 -- e.g. "BIR 1601-C SOP"
  section text,               -- e.g. "Deadlines"
  chunk_index int not null,   -- ordering within source
  content text not null,      -- actual text
  content_hash text not null, -- for drift detection / idempotency
  created_at timestamptz default now()
);

-- Embeddings table (1:1 with chunks, separate for cleanliness)
create table if not exists docs.embeddings (
  chunk_id bigint primary key references docs.chunks(id) on delete cascade,
  embedding vector(1536) not null, -- OpenAI text-embedding-ada-002 / text-embedding-3-small dimension
  created_at timestamptz default now()
);

-- Index for similarity search
-- Using ivfflat as a safe default for smaller datasets; HNSW is better for scale but ivfflat is simpler for bootstrapping
create index if not exists embeddings_ivfflat
  on docs.embeddings using ivfflat (embedding vector_cosine_ops) with (lists=100);

-- RPC function for simple similarity search
create or replace function docs.search_chunks(q vector(1536), k int default 8)
returns table (chunk_id bigint, score float4)
language sql stable as $$
  select e.chunk_id, (1 - (e.embedding <=> q))::float4 as score
  from docs.embeddings e
  order by e.embedding <=> q
  limit k
$$;
