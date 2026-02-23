-- GraphRAG KB bootstrapping + graph layer for Insightpulseai/odoo
-- Self-contained: creates kb_chunks/kb_embeddings if absent, then adds
-- provenance fields + kb_nodes + kb_edges.
-- Idempotent (safe to re-run).

begin;

-- =========================================================
-- 0) Required extensions
-- =========================================================
create extension if not exists "uuid-ossp";
create extension if not exists "pgcrypto";
create extension if not exists "vector";

-- =========================================================
-- 1) kb_chunks — create if absent, then add provenance columns
-- =========================================================
create table if not exists public.kb_chunks (
  id          uuid        primary key default uuid_generate_v4(),
  document_id text        not null default '',
  content     text        not null default '',
  metadata    jsonb       not null default '{}'::jsonb,
  created_at  timestamptz not null default now(),
  updated_at  timestamptz not null default now()
);

-- Provenance columns (idempotent ADD IF NOT EXISTS)
alter table public.kb_chunks
  add column if not exists path        text,
  add column if not exists span_start  int,
  add column if not exists span_end    int,
  add column if not exists text_hash   text,
  add column if not exists git_sha     text,
  add column if not exists module      text,
  add column if not exists addon_kind  text,
  add column if not exists edit_policy text default 'editable';

do $$
begin
  if not exists (
    select 1 from pg_constraint where conname = 'kb_chunks_addon_kind_chk'
  ) then
    alter table public.kb_chunks
      add constraint kb_chunks_addon_kind_chk
      check (addon_kind is null or addon_kind in ('core','oca','ipai','vendor','generated'));
  end if;

  if not exists (
    select 1 from pg_constraint where conname = 'kb_chunks_edit_policy_chk'
  ) then
    alter table public.kb_chunks
      add constraint kb_chunks_edit_policy_chk
      check (edit_policy is null or edit_policy in ('editable','overlay_only','no_touch'));
  end if;
end $$;

create index if not exists kb_chunks_path_idx      on public.kb_chunks(path);
create index if not exists kb_chunks_git_sha_idx   on public.kb_chunks(git_sha);
create index if not exists kb_chunks_text_hash_idx on public.kb_chunks(text_hash);
create index if not exists kb_chunks_module_idx    on public.kb_chunks(module);
create index if not exists kb_chunks_kind_idx      on public.kb_chunks(addon_kind);
create index if not exists kb_chunks_policy_idx    on public.kb_chunks(edit_policy);

-- =========================================================
-- 2) kb_embeddings — create if absent, then add dims column
-- =========================================================
create table if not exists public.kb_embeddings (
  id         uuid                    primary key default uuid_generate_v4(),
  chunk_id   uuid                    not null references public.kb_chunks(id) on delete cascade,
  embedding  vector(1536)            not null,
  model      text                    not null,
  created_at timestamptz             not null default now(),
  unique(chunk_id, model)
);

alter table public.kb_embeddings
  add column if not exists dims int;

create index if not exists kb_embeddings_model_idx on public.kb_embeddings(model);

-- =========================================================
-- 3) kb_nodes — graph nodes with policy metadata
-- =========================================================
create table if not exists public.kb_nodes (
  id          uuid        primary key default uuid_generate_v4(),
  type        text        not null,
  -- File | OdooModule | Model | View | Asset | AssetBundle | Controller | Doc
  name        text        not null,
  path        text,
  module      text,
  addon_kind  text,
  -- core | oca | ipai | vendor | generated
  edit_policy text        not null default 'editable',
  -- editable | overlay_only | no_touch
  git_sha     text,
  attrs       jsonb       not null default '{}'::jsonb,
  created_at  timestamptz not null default now(),
  updated_at  timestamptz not null default now()
);

do $$
begin
  if not exists (select 1 from pg_constraint where conname = 'kb_nodes_addon_kind_chk') then
    alter table public.kb_nodes
      add constraint kb_nodes_addon_kind_chk
      check (addon_kind is null or addon_kind in ('core','oca','ipai','vendor','generated'));
  end if;

  if not exists (select 1 from pg_constraint where conname = 'kb_nodes_edit_policy_chk') then
    alter table public.kb_nodes
      add constraint kb_nodes_edit_policy_chk
      check (edit_policy in ('editable','overlay_only','no_touch'));
  end if;

  if not exists (select 1 from pg_constraint where conname = 'kb_nodes_type_path_name_uniq') then
    alter table public.kb_nodes
      add constraint kb_nodes_type_path_name_uniq unique (type, path, name);
  end if;
end $$;

-- Updated-at trigger
create or replace function public.kb_set_updated_at()
returns trigger language plpgsql as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

drop trigger if exists trg_kb_nodes_updated_at on public.kb_nodes;
create trigger trg_kb_nodes_updated_at
  before update on public.kb_nodes
  for each row execute function public.kb_set_updated_at();

create index if not exists kb_nodes_type_idx   on public.kb_nodes(type);
create index if not exists kb_nodes_kind_idx   on public.kb_nodes(addon_kind);
create index if not exists kb_nodes_policy_idx on public.kb_nodes(edit_policy);
create index if not exists kb_nodes_path_idx   on public.kb_nodes(path);
create index if not exists kb_nodes_module_idx on public.kb_nodes(module);

-- =========================================================
-- 4) kb_edges — directed, typed edges between nodes
-- =========================================================
create table if not exists public.kb_edges (
  id         uuid        primary key default uuid_generate_v4(),
  src_id     uuid        not null references public.kb_nodes(id) on delete cascade,
  dst_id     uuid        not null references public.kb_nodes(id) on delete cascade,
  type       text        not null,
  -- CALLS | DEPENDS_ON | INHERITS_FROM | ASSET_IN_BUNDLE | REMOVES | OVERLAYS | DEFINED_IN | IMPORTS
  attrs      jsonb       not null default '{}'::jsonb,
  git_sha    text,
  created_at timestamptz not null default now()
);

do $$
begin
  if not exists (select 1 from pg_constraint where conname = 'kb_edges_src_dst_type_uniq') then
    alter table public.kb_edges
      add constraint kb_edges_src_dst_type_uniq unique (src_id, dst_id, type);
  end if;
end $$;

-- Single-column traversal indexes
create index if not exists kb_edges_src_idx     on public.kb_edges(src_id);
create index if not exists kb_edges_dst_idx     on public.kb_edges(dst_id);
create index if not exists kb_edges_type_idx    on public.kb_edges(type);
create index if not exists kb_edges_git_sha_idx on public.kb_edges(git_sha);

-- Composite indexes for GraphRAG traversal:
-- "from node X, follow DEPENDS_ON edges" → (src_id, type)
-- "what nodes point to X via INHERITS_FROM" → (dst_id, type)
create index if not exists kb_edges_src_type_idx on public.kb_edges(src_id, type);
create index if not exists kb_edges_dst_type_idx on public.kb_edges(dst_id, type);

commit;
