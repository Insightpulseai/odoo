-- =============================================================================
-- RAG Hybrid Search Upgrade (Kapa-style)
-- =============================================================================
-- Adds: versioning, provenance, hybrid retrieval (vector + lexical), citations
-- Compatible with existing rag.documents and rag.chunks schema
-- =============================================================================

-- Enable extensions for hybrid search
create extension if not exists pg_trgm;

-- =============================================================================
-- 1. Extend rag.documents with versioning and provenance
-- =============================================================================

alter table rag.documents
  add column if not exists canonical_url text,
  add column if not exists doc_version text,
  add column if not exists commit_sha text,
  add column if not exists visibility text default 'internal',
  add column if not exists content_checksum text;

-- Index for visibility filtering
create index if not exists idx_documents_visibility
  on rag.documents (tenant_id, visibility, source_type);

-- Index for version queries
create index if not exists idx_documents_version
  on rag.documents (tenant_id, doc_version, updated_at desc);

-- Index for deduplication by checksum
create index if not exists idx_documents_checksum
  on rag.documents (tenant_id, content_checksum)
  where content_checksum is not null;

-- =============================================================================
-- 2. Extend rag.chunks with structure-aware fields
-- =============================================================================

alter table rag.chunks
  add column if not exists section_path text,
  add column if not exists embedding_model text default 'text-embedding-3-small',
  add column if not exists language text default 'en',
  add column if not exists tsv tsvector;

-- Keep tsvector updated automatically
create or replace function rag.chunks_tsv_update()
returns trigger language plpgsql as $func$
begin
  new.tsv := to_tsvector('simple', coalesce(new.content, ''));
  return new;
end;
$func$;

drop trigger if exists trg_chunks_tsv on rag.chunks;
create trigger trg_chunks_tsv
  before insert or update of content
  on rag.chunks
  for each row execute function rag.chunks_tsv_update();

-- Backfill existing chunks (safe - only updates null tsv)
update rag.chunks
set tsv = to_tsvector('simple', coalesce(content, ''))
where tsv is null;

-- =============================================================================
-- 3. Indexes for hybrid search (lexical + vector)
-- =============================================================================

-- Full-text search index (GIN on tsvector)
create index if not exists idx_chunks_tsv
  on rag.chunks using gin (tsv);

-- Trigram index for fuzzy matching (module names, xmlids, error codes)
create index if not exists idx_chunks_trgm
  on rag.chunks using gin (content gin_trgm_ops);

-- Vector index (HNSW preferred, fallback to IVFFlat if pgvector < 0.5.0)
-- Uncomment ONE of the following based on your pgvector version:

-- Option A: HNSW (pgvector >= 0.5.0, better for incremental inserts)
-- create index if not exists idx_chunks_hnsw
--   on rag.chunks using hnsw (embedding vector_cosine_ops)
--   with (m = 16, ef_construction = 64);

-- Option B: IVFFlat (pgvector < 0.5.0, good for bulk inserts)
create index if not exists idx_chunks_ivfflat
  on rag.chunks using ivfflat (embedding vector_cosine_ops)
  with (lists = 100);

-- Section path index for hierarchical filtering
create index if not exists idx_chunks_section_path
  on rag.chunks (tenant_id, section_path);

-- Language filtering index
create index if not exists idx_chunks_language
  on rag.chunks (tenant_id, language);

-- =============================================================================
-- 4. Hybrid Search RPC (vector + lexical retrieval)
-- =============================================================================

create or replace function rag.search_hybrid(
  p_tenant_id uuid,
  p_query text,
  p_query_embedding vector(1536),
  p_top_k int default 12,
  p_source_type text default null,
  p_visibility text default null,
  p_doc_version text default null,
  p_language text default 'en',
  p_vector_weight float default 0.65,
  p_lexical_weight float default 0.35
)
returns table (
  chunk_id uuid,
  document_id uuid,
  score float,
  content text,
  metadata jsonb,
  section_path text,
  canonical_url text,
  doc_version text,
  commit_sha text
)
language sql stable
as $func$
with
-- Vector similarity search (cosine distance)
v as (
  select
    c.id as chunk_id,
    c.document_id,
    (1 - (c.embedding <=> p_query_embedding))::float as vscore
  from rag.chunks c
  join rag.documents d on d.id = c.document_id
  where c.tenant_id = p_tenant_id
    and c.embedding is not null
    and (p_source_type is null or d.source_type = p_source_type)
    and (p_visibility is null or d.visibility = p_visibility)
    and (p_doc_version is null or d.doc_version = p_doc_version)
    and (p_language is null or c.language = p_language)
  order by c.embedding <=> p_query_embedding
  limit (p_top_k * 3)
),
-- Lexical search (full-text + trigram)
t as (
  select
    c.id as chunk_id,
    c.document_id,
    ts_rank(c.tsv, plainto_tsquery('simple', p_query))::float as tscore
  from rag.chunks c
  join rag.documents d on d.id = c.document_id
  where c.tenant_id = p_tenant_id
    and (p_source_type is null or d.source_type = p_source_type)
    and (p_visibility is null or d.visibility = p_visibility)
    and (p_doc_version is null or d.doc_version = p_doc_version)
    and (p_language is null or c.language = p_language)
    and c.tsv @@ plainto_tsquery('simple', p_query)
  order by ts_rank(c.tsv, plainto_tsquery('simple', p_query)) desc
  limit (p_top_k * 3)
),
-- Merge and rank by weighted score
s as (
  select
    coalesce(v.chunk_id, t.chunk_id) as chunk_id,
    coalesce(v.document_id, t.document_id) as document_id,
    (coalesce(v.vscore, 0) * p_vector_weight +
     coalesce(t.tscore, 0) * p_lexical_weight) as score
  from v
  full outer join t using (chunk_id, document_id)
)
select
  s.chunk_id,
  s.document_id,
  s.score,
  c.content,
  c.metadata,
  c.section_path,
  d.canonical_url,
  d.doc_version,
  d.commit_sha
from s
join rag.chunks c on c.id = s.chunk_id
join rag.documents d on d.id = c.document_id
order by s.score desc
limit p_top_k;
$func$;

comment on function rag.search_hybrid is
'Hybrid retrieval combining vector similarity (65%) and lexical search (35%) with version/visibility filtering';

-- =============================================================================
-- 5. Exact Match RPC (for module names, xmlids, error codes)
-- =============================================================================

create or replace function rag.search_exact(
  p_tenant_id uuid,
  p_query text,
  p_top_k int default 6,
  p_source_type text default null,
  p_visibility text default null
)
returns table (
  chunk_id uuid,
  document_id uuid,
  content text,
  metadata jsonb,
  section_path text,
  canonical_url text,
  doc_version text
)
language sql stable
as $func$
select
  c.id as chunk_id,
  c.document_id,
  c.content,
  c.metadata,
  c.section_path,
  d.canonical_url,
  d.doc_version
from rag.chunks c
join rag.documents d on d.id = c.document_id
where c.tenant_id = p_tenant_id
  and (p_source_type is null or d.source_type = p_source_type)
  and (p_visibility is null or d.visibility = p_visibility)
  and (
    c.content ilike '%' || p_query || '%' or
    c.metadata::text ilike '%' || p_query || '%'
  )
order by
  case when c.content ilike p_query then 0 else 1 end,
  similarity(c.content, p_query) desc
limit p_top_k;
$func$;

comment on function rag.search_exact is
'Exact/fuzzy string matching for module names, xmlids, error codes (bypasses embeddings)';

-- =============================================================================
-- 6. Multi-source routing RPC (Kapa-style search order)
-- =============================================================================

create or replace function rag.search_multi_source(
  p_tenant_id uuid,
  p_query text,
  p_query_embedding vector(1536),
  p_top_k_per_source int default 3,
  p_source_order text[] default array[
    'ipai_odoo_ce',
    'ipai_finance_ppm',
    'oca_account_financial_tools',
    'oca_reporting_engine',
    'odoo_docs'
  ]
)
returns table (
  chunk_id uuid,
  document_id uuid,
  source_type text,
  score float,
  content text,
  metadata jsonb,
  canonical_url text,
  doc_version text,
  commit_sha text
)
language plpgsql stable
as $func$
declare
  source text;
begin
  for source in select unnest(p_source_order) loop
    return query
    select
      r.chunk_id,
      r.document_id,
      source as source_type,
      r.score,
      r.content,
      r.metadata,
      r.canonical_url,
      r.doc_version,
      r.commit_sha
    from rag.search_hybrid(
      p_tenant_id,
      p_query,
      p_query_embedding,
      p_top_k_per_source,
      source,
      null  -- visibility filter (internal sources already filtered by source name)
    ) r
    order by r.score desc
    limit p_top_k_per_source;
  end loop;
end;
$func$;

comment on function rag.search_multi_source is
'Search across multiple sources in priority order (internal docs first, then OCA, then Odoo official)';

-- =============================================================================
-- 7. Citation formatting helper
-- =============================================================================

create or replace function rag.format_citation(
  p_canonical_url text,
  p_section_path text default null,
  p_doc_version text default null,
  p_commit_sha text default null
)
returns jsonb
language sql immutable
as $func$
select jsonb_build_object(
  'url', p_canonical_url,
  'section', p_section_path,
  'version', p_doc_version,
  'commit', substring(p_commit_sha from 1 for 7),
  'anchor',
    case
      when p_section_path is not null
      then '#' || lower(regexp_replace(p_section_path, '[^a-z0-9]+', '-', 'g'))
      else null
    end
);
$func$;

comment on function rag.format_citation is
'Format chunk metadata into Kapa-style citation object with URL, section anchor, version, commit';

-- =============================================================================
-- 8. Feedback loop tables (for continuous quality improvement)
-- =============================================================================

create table if not exists rag.questions (
  id uuid primary key default gen_random_uuid(),
  tenant_id uuid not null references core.tenants on delete cascade,
  question text not null,
  query_embedding vector(1536),
  user_id uuid references core.users on delete set null,
  session_id text,
  created_at timestamptz default now()
);

create table if not exists rag.answers (
  id uuid primary key default gen_random_uuid(),
  tenant_id uuid not null references core.tenants on delete cascade,
  question_id uuid not null references rag.questions on delete cascade,
  answer text not null,
  citations jsonb default '[]'::jsonb,
  search_method text, -- 'hybrid', 'exact', 'multi_source'
  confidence_score float,
  generation_model text,
  created_at timestamptz default now()
);

create table if not exists rag.answer_votes (
  id uuid primary key default gen_random_uuid(),
  tenant_id uuid not null references core.tenants on delete cascade,
  answer_id uuid not null references rag.answers on delete cascade,
  user_id uuid references core.users on delete set null,
  vote int check (vote in (-1, 0, 1)), -- thumbs down, neutral, thumbs up
  feedback_text text,
  created_at timestamptz default now(),
  unique (answer_id, user_id)
);

create table if not exists rag.eval_sets (
  id uuid primary key default gen_random_uuid(),
  tenant_id uuid not null references core.tenants on delete cascade,
  name text not null,
  description text,
  questions jsonb not null, -- array of {question, expected_answer, expected_citations}
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

-- Indexes for feedback loop
create index if not exists idx_questions_tenant
  on rag.questions (tenant_id, created_at desc);

create index if not exists idx_answers_question
  on rag.answers (question_id, created_at desc);

create index if not exists idx_answer_votes_answer
  on rag.answer_votes (answer_id);

create index if not exists idx_eval_sets_tenant
  on rag.eval_sets (tenant_id, updated_at desc);

-- RLS policies for feedback tables
alter table rag.questions enable row level security;
alter table rag.answers enable row level security;
alter table rag.answer_votes enable row level security;
alter table rag.eval_sets enable row level security;

create policy questions_tenant_isolation on rag.questions
  using (tenant_id = core.current_tenant_id());

create policy answers_tenant_isolation on rag.answers
  using (tenant_id = core.current_tenant_id());

create policy answer_votes_tenant_isolation on rag.answer_votes
  using (tenant_id = core.current_tenant_id());

create policy eval_sets_tenant_isolation on rag.eval_sets
  using (tenant_id = core.current_tenant_id());

-- =============================================================================
-- 9. Version management helper functions
-- =============================================================================

create or replace function rag.get_latest_version(
  p_tenant_id uuid,
  p_source_type text
)
returns text
language sql stable
as $func$
select doc_version
from rag.documents
where tenant_id = p_tenant_id
  and source_type = p_source_type
  and doc_version is not null
order by updated_at desc
limit 1;
$func$;

comment on function rag.get_latest_version is
'Get the most recently ingested version for a given source type';

-- =============================================================================
-- 10. Performance monitoring view
-- =============================================================================

create or replace view rag.search_performance as
select
  date_trunc('hour', q.created_at) as hour,
  count(*) as total_questions,
  count(distinct q.user_id) as unique_users,
  avg(a.confidence_score) as avg_confidence,
  sum(case when v.vote = 1 then 1 else 0 end)::float /
    nullif(count(v.id), 0) as thumbs_up_rate,
  avg(extract(epoch from (a.created_at - q.created_at))) as avg_response_time_sec
from rag.questions q
left join rag.answers a on a.question_id = q.id
left join rag.answer_votes v on v.answer_id = a.id
group by date_trunc('hour', q.created_at)
order by hour desc;

comment on view rag.search_performance is
'Hourly aggregated metrics for RAG search performance monitoring';

-- =============================================================================
-- Complete
-- =============================================================================

-- Verify critical indexes exist
do $verify$
declare
  missing_indexes text[];
begin
  select array_agg(idx) into missing_indexes
  from (values
    ('idx_chunks_tsv'),
    ('idx_chunks_trgm'),
    ('idx_chunks_ivfflat'),
    ('idx_documents_visibility')
  ) as required(idx)
  where not exists (
    select 1 from pg_indexes
    where indexname = required.idx
  );

  if array_length(missing_indexes, 1) > 0 then
    raise warning 'Missing indexes: %', missing_indexes;
  else
    raise notice 'All critical hybrid search indexes verified ✓';
  end if;
end;
$verify$;
