-- supabase/migrations/20260223000003_kb_vector.sql

create table public.kb_chunks (
  id uuid default uuid_generate_v4() primary key,
  path text not null,       -- Source file or URL path
  span text,                -- Line numbers or exact span description
  text_content text not null,
  text_hash text not null,  -- Useful for deduplication during sync
  meta jsonb default '{}'::jsonb not null, -- Metadata (tags, original timestamp)
  created_at timestamptz default now() not null,
  updated_at timestamptz default now() not null,
  unique(path, text_hash)
);

create table public.kb_embeddings (
  id uuid default uuid_generate_v4() primary key,
  chunk_id uuid references public.kb_chunks(id) on delete cascade not null,
  embedding vector(1536) not null, -- Assuming OpenAI text-embedding-3-small
  model text not null,
  created_at timestamptz default now() not null,
  unique(chunk_id, model)
);

-- Index for similarity search
create index on public.kb_embeddings using ivfflat (embedding vector_cosine_ops) with (lists = 100);

-- Enable RLS
alter table public.kb_chunks enable row level security;
alter table public.kb_embeddings enable row level security;

-- Policies (Admins/Agents can manage; Team can read)
create policy "Team can read KB chunks"
  on public.kb_chunks for select
  using (public.has_role('member') or public.has_role('admin') or public.has_role('agent'));

create policy "Agents can insert KB chunks"
  on public.kb_chunks for insert
  with check (public.has_role('agent') or public.has_role('admin'));

create policy "Agents can update KB chunks"
  on public.kb_chunks for update
  using (public.has_role('agent') or public.has_role('admin'));

create policy "Agents can delete KB chunks"
  on public.kb_chunks for delete
  using (public.has_role('agent') or public.has_role('admin'));

-- Embedding Policies
create policy "Team can read KB embeddings"
  on public.kb_embeddings for select
  using (public.has_role('member') or public.has_role('admin') or public.has_role('agent'));

create policy "Agents can insert KB embeddings"
  on public.kb_embeddings for insert
  with check (public.has_role('agent') or public.has_role('admin'));

create policy "Agents can update KB embeddings"
  on public.kb_embeddings for update
  using (public.has_role('agent') or public.has_role('admin'));

create policy "Agents can delete KB embeddings"
  on public.kb_embeddings for delete
  using (public.has_role('agent') or public.has_role('admin'));

-- Trigger for updated_at
create trigger chunk_updated_at
  before update on public.kb_chunks
  for each row execute function public.handle_updated_at();

