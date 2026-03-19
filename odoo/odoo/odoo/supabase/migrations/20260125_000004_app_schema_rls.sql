-- App Schema with RLS
-- Application-owned entities with Row Level Security

create schema if not exists app;

-- Organizations (tenants)
create table if not exists app.orgs (
  id uuid primary key default gen_random_uuid(),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  name text not null,
  slug text not null unique,
  settings jsonb not null default '{}'::jsonb
);

-- Organization members
create table if not exists app.org_members (
  org_id uuid not null references app.orgs(id) on delete cascade,
  user_id uuid not null,
  role text not null default 'member' check (role in ('org_owner', 'org_admin', 'member', 'viewer')),
  created_at timestamptz not null default now(),
  primary key (org_id, user_id)
);

-- Projects
create table if not exists app.projects (
  id uuid primary key default gen_random_uuid(),
  org_id uuid not null references app.orgs(id) on delete cascade,
  name text not null,
  description text,
  status text not null default 'active' check (status in ('active', 'archived', 'completed')),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

-- Tasks
create table if not exists app.tasks (
  id uuid primary key default gen_random_uuid(),
  project_id uuid not null references app.projects(id) on delete cascade,
  title text not null,
  description text,
  status text not null default 'todo' check (status in ('todo', 'in_progress', 'done', 'cancelled')),
  assignee_id uuid,
  due_date date,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

-- Indexes
create index if not exists idx_app_org_members_user on app.org_members(user_id);
create index if not exists idx_app_projects_org on app.projects(org_id);
create index if not exists idx_app_tasks_project on app.tasks(project_id);
create index if not exists idx_app_tasks_assignee on app.tasks(assignee_id);

-- Updated_at triggers
create or replace function app.set_updated_at()
returns trigger language plpgsql as $$
begin
  new.updated_at = now();
  return new;
end $$;

drop trigger if exists trg_app_orgs_updated_at on app.orgs;
create trigger trg_app_orgs_updated_at
before update on app.orgs
for each row execute function app.set_updated_at();

drop trigger if exists trg_app_projects_updated_at on app.projects;
create trigger trg_app_projects_updated_at
before update on app.projects
for each row execute function app.set_updated_at();

drop trigger if exists trg_app_tasks_updated_at on app.tasks;
create trigger trg_app_tasks_updated_at
before update on app.tasks
for each row execute function app.set_updated_at();

-- Enable RLS on all tables
alter table app.orgs enable row level security;
alter table app.org_members enable row level security;
alter table app.projects enable row level security;
alter table app.tasks enable row level security;

-- RLS Policies: Organizations
create policy "orgs_select_member"
on app.orgs for select
using (
  exists (
    select 1 from app.org_members m
    where m.org_id = app.orgs.id
      and m.user_id = auth.uid()
  )
);

create policy "orgs_insert_authenticated"
on app.orgs for insert
with check (auth.uid() is not null);

create policy "orgs_update_owner_admin"
on app.orgs for update
using (
  exists (
    select 1 from app.org_members m
    where m.org_id = app.orgs.id
      and m.user_id = auth.uid()
      and m.role in ('org_owner', 'org_admin')
  )
);

create policy "orgs_delete_owner"
on app.orgs for delete
using (
  exists (
    select 1 from app.org_members m
    where m.org_id = app.orgs.id
      and m.user_id = auth.uid()
      and m.role = 'org_owner'
  )
);

-- RLS Policies: Organization Members
create policy "members_select_same_org"
on app.org_members for select
using (
  exists (
    select 1 from app.org_members m
    where m.org_id = app.org_members.org_id
      and m.user_id = auth.uid()
  )
);

create policy "members_insert_admin"
on app.org_members for insert
with check (
  exists (
    select 1 from app.org_members m
    where m.org_id = app.org_members.org_id
      and m.user_id = auth.uid()
      and m.role in ('org_owner', 'org_admin')
  )
  or not exists (
    select 1 from app.org_members m
    where m.org_id = app.org_members.org_id
  )
);

create policy "members_update_owner"
on app.org_members for update
using (
  exists (
    select 1 from app.org_members m
    where m.org_id = app.org_members.org_id
      and m.user_id = auth.uid()
      and m.role = 'org_owner'
  )
);

create policy "members_delete_admin"
on app.org_members for delete
using (
  exists (
    select 1 from app.org_members m
    where m.org_id = app.org_members.org_id
      and m.user_id = auth.uid()
      and m.role in ('org_owner', 'org_admin')
  )
  and app.org_members.user_id != auth.uid()
);

-- RLS Policies: Projects
create policy "projects_select_org_member"
on app.projects for select
using (
  exists (
    select 1 from app.org_members m
    where m.org_id = app.projects.org_id
      and m.user_id = auth.uid()
  )
);

create policy "projects_insert_org_member"
on app.projects for insert
with check (
  exists (
    select 1 from app.org_members m
    where m.org_id = app.projects.org_id
      and m.user_id = auth.uid()
  )
);

create policy "projects_update_org_admin"
on app.projects for update
using (
  exists (
    select 1 from app.org_members m
    where m.org_id = app.projects.org_id
      and m.user_id = auth.uid()
      and m.role in ('org_owner', 'org_admin')
  )
);

create policy "projects_delete_org_admin"
on app.projects for delete
using (
  exists (
    select 1 from app.org_members m
    where m.org_id = app.projects.org_id
      and m.user_id = auth.uid()
      and m.role in ('org_owner', 'org_admin')
  )
);

-- RLS Policies: Tasks
create policy "tasks_select_project_member"
on app.tasks for select
using (
  exists (
    select 1 from app.projects p
    join app.org_members m on m.org_id = p.org_id
    where p.id = app.tasks.project_id
      and m.user_id = auth.uid()
  )
);

create policy "tasks_insert_project_member"
on app.tasks for insert
with check (
  exists (
    select 1 from app.projects p
    join app.org_members m on m.org_id = p.org_id
    where p.id = app.tasks.project_id
      and m.user_id = auth.uid()
  )
);

create policy "tasks_update_assignee_or_admin"
on app.tasks for update
using (
  app.tasks.assignee_id = auth.uid()
  or exists (
    select 1 from app.projects p
    join app.org_members m on m.org_id = p.org_id
    where p.id = app.tasks.project_id
      and m.user_id = auth.uid()
      and m.role in ('org_owner', 'org_admin')
  )
);

create policy "tasks_delete_admin"
on app.tasks for delete
using (
  exists (
    select 1 from app.projects p
    join app.org_members m on m.org_id = p.org_id
    where p.id = app.tasks.project_id
      and m.user_id = auth.uid()
      and m.role in ('org_owner', 'org_admin')
  )
);

comment on schema app is 'Application-owned entities with RLS';
comment on table app.orgs is 'Organizations (tenants)';
comment on table app.org_members is 'Organization membership with roles';
comment on table app.projects is 'Projects within organizations';
comment on table app.tasks is 'Tasks within projects';
