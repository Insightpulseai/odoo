-- PHASE 1: CMS ORG-SCOPING
-- Creates CMS tables if they don't exist, then adds org_id columns

-- ============================================================================
-- CREATE CMS TABLES (if they don't exist)
-- ============================================================================

-- CMS Pages
create table if not exists public.cms_pages (
  id uuid primary key default gen_random_uuid(),
  slug text unique not null,
  title text not null,
  status text not null default 'draft' check (status in ('draft','published','archived')),
  published_at timestamptz,
  seo jsonb default '{}',
  content_html text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

-- CMS Sections
create table if not exists public.cms_sections (
  id uuid primary key default gen_random_uuid(),
  page_id uuid references public.cms_pages(id) on delete cascade,
  type text not null,
  position int not null default 0,
  payload jsonb not null default '{}',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

-- CMS Use Cases
create table if not exists public.cms_use_cases (
  id uuid primary key default gen_random_uuid(),
  slug text unique not null,
  title text not null,
  description text,
  category text,
  model text,
  features text[] default '{}',
  author text,
  image_url text,
  href text,
  status text not null default 'published' check (status in ('draft','published','archived')),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

-- CMS Artifacts (AI outputs, audit trail)
create table if not exists public.cms_artifacts (
  id uuid primary key default gen_random_uuid(),
  artifact_type text not null,
  source text,
  prompt text,
  output jsonb not null,
  status text not null default 'draft' check (status in ('draft','approved','rejected')),
  created_at timestamptz not null default now()
);

-- Updated_at trigger (if not exists)
create or replace function public.cms_set_updated_at()
returns trigger language plpgsql as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

drop trigger if exists trg_cms_pages_updated_at on public.cms_pages;
create trigger trg_cms_pages_updated_at
before update on public.cms_pages
for each row execute function public.cms_set_updated_at();

drop trigger if exists trg_cms_sections_updated_at on public.cms_sections;
create trigger trg_cms_sections_updated_at
before update on public.cms_sections
for each row execute function public.cms_set_updated_at();

drop trigger if exists trg_cms_use_cases_updated_at on public.cms_use_cases;
create trigger trg_cms_use_cases_updated_at
before update on public.cms_use_cases
for each row execute function public.cms_set_updated_at();

comment on table public.cms_pages is 'CMS pages (homepage, docs, etc) - content only, layout in code';
comment on table public.cms_sections is 'Page sections - payload is pure JSON content, no HTML/CSS';
comment on table public.cms_use_cases is 'Use case library - referenced by sections or standalone';
comment on table public.cms_artifacts is 'AI-generated content artifacts with audit trail';

-- ============================================================================
-- ADD ORG_ID COLUMNS (org-scoping migration)
-- ============================================================================

-- Add org_id columns if they don't exist
do $$
begin
  if not exists (select 1 from information_schema.columns where table_schema='public' and table_name='cms_pages' and column_name='org_id') then
    alter table public.cms_pages add column org_id uuid references public.organizations(id);
  end if;

  if not exists (select 1 from information_schema.columns where table_schema='public' and table_name='cms_sections' and column_name='org_id') then
    alter table public.cms_sections add column org_id uuid references public.organizations(id);
  end if;

  if not exists (select 1 from information_schema.columns where table_schema='public' and table_name='cms_use_cases' and column_name='org_id') then
    alter table public.cms_use_cases add column org_id uuid references public.organizations(id);
  end if;

  if not exists (select 1 from information_schema.columns where table_schema='public' and table_name='cms_artifacts' and column_name='org_id') then
    alter table public.cms_artifacts add column org_id uuid references public.organizations(id);
  end if;
end $$;

-- ============================================================================
-- BACKFILL EXISTING DATA (assign to first org)
-- ============================================================================

-- Backfill existing CMS data with first org
do $$
declare
  first_org_id uuid;
begin
  -- Get first org (or null if none exist)
  select id into first_org_id from public.organizations order by created_at asc limit 1;

  -- Only backfill if we have an org
  if first_org_id is not null then
    update public.cms_pages set org_id = first_org_id where org_id is null;
    update public.cms_sections set org_id = first_org_id where org_id is null;
    update public.cms_use_cases set org_id = first_org_id where org_id is null;
    update public.cms_artifacts set org_id = first_org_id where org_id is null;
  end if;
end $$;

-- ============================================================================
-- ENFORCE NOT NULL (after backfill)
-- ============================================================================

-- Only enforce NOT NULL if there's data and it's been backfilled
do $$
begin
  -- Check if all rows have org_id before enforcing constraint
  if (select count(*) from public.cms_pages where org_id is null) = 0 then
    alter table public.cms_pages alter column org_id set not null;
  end if;

  if (select count(*) from public.cms_sections where org_id is null) = 0 then
    alter table public.cms_sections alter column org_id set not null;
  end if;

  if (select count(*) from public.cms_use_cases where org_id is null) = 0 then
    alter table public.cms_use_cases alter column org_id set not null;
  end if;

  if (select count(*) from public.cms_artifacts where org_id is null) = 0 then
    alter table public.cms_artifacts alter column org_id set not null;
  end if;
end $$;

-- ============================================================================
-- UPDATE CMS RLS POLICIES (org-scoped)
-- ============================================================================

-- Enable RLS
alter table public.cms_pages enable row level security;
alter table public.cms_sections enable row level security;
alter table public.cms_use_cases enable row level security;
alter table public.cms_artifacts enable row level security;

-- Public read policies (published only)
drop policy if exists "public_read_published_pages" on public.cms_pages;
create policy "public_read_published_pages"
on public.cms_pages for select
using (status = 'published');

drop policy if exists "public_read_published_sections" on public.cms_sections;
create policy "public_read_published_sections"
on public.cms_sections for select
using (
  exists (
    select 1 from public.cms_pages p
    where p.id = cms_sections.page_id
      and p.status = 'published'
  )
);

drop policy if exists "public_read_published_use_cases" on public.cms_use_cases;
create policy "public_read_published_use_cases"
on public.cms_use_cases for select
using (status = 'published');

-- Org member policies (CRUD access)
drop policy if exists "org_editors_manage_pages" on public.cms_pages;
create policy "org_editors_manage_pages"
on public.cms_pages for all
using (public.is_org_member(org_id))
with check (public.is_org_member(org_id));

drop policy if exists "org_editors_manage_sections" on public.cms_sections;
create policy "org_editors_manage_sections"
on public.cms_sections for all
using (public.is_org_member(org_id))
with check (public.is_org_member(org_id));

drop policy if exists "org_editors_manage_use_cases" on public.cms_use_cases;
create policy "org_editors_manage_use_cases"
on public.cms_use_cases for all
using (public.is_org_member(org_id))
with check (public.is_org_member(org_id));

drop policy if exists "org_members_read_artifacts" on public.cms_artifacts;
create policy "org_members_read_artifacts"
on public.cms_artifacts for select
using (public.is_org_member(org_id));

drop policy if exists "service_role_artifacts" on public.cms_artifacts;
create policy "service_role_artifacts"
on public.cms_artifacts for all
using (auth.role() = 'service_role');

-- Indexes for performance
create index if not exists idx_cms_pages_org_status on public.cms_pages(org_id, status);
create index if not exists idx_cms_pages_slug on public.cms_pages(slug);
create index if not exists idx_cms_sections_page_id on public.cms_sections(page_id);
create index if not exists idx_cms_sections_org_position on public.cms_sections(org_id, position);
create index if not exists idx_cms_use_cases_org_status on public.cms_use_cases(org_id, status);
create index if not exists idx_cms_artifacts_org_type_status on public.cms_artifacts(org_id, artifact_type, status);

-- Grant permissions
grant select on public.cms_pages to anon, authenticated;
grant select on public.cms_sections to anon, authenticated;
grant select on public.cms_use_cases to anon, authenticated;
grant all on public.cms_pages to authenticated;
grant all on public.cms_sections to authenticated;
grant all on public.cms_use_cases to authenticated;
grant all on public.cms_artifacts to service_role;
grant select on public.cms_artifacts to authenticated;
