-- supabase/migrations/20260223000002_auth_rbac.sql

-- 1. Create table structure
create table public.roles (
  id uuid default uuid_generate_v4() primary key,
  name text not null unique,
  description text
);

create table public.profiles (
  id uuid references auth.users(id) on delete cascade primary key,
  email text,
  full_name text,
  avatar_url text,
  created_at timestamptz default now() not null,
  updated_at timestamptz default now() not null
);

create table public.user_roles (
  id uuid default uuid_generate_v4() primary key,
  user_id uuid references public.profiles(id) on delete cascade not null,
  role_id uuid references public.roles(id) on delete cascade not null,
  created_at timestamptz default now() not null,
  unique(user_id, role_id)
);

-- 2. Seed basic roles
insert into public.roles (name, description) values
  ('admin', 'Full system access'),
  ('manager', 'Odoo ops manager access'),
  ('agent', 'Automated agent service role'),
  ('member', 'Standard team member');

-- 3. RBAC Helper Function
create or replace function public.has_role(role_name text)
returns boolean
language sql stable
security definer
set search_path = public
as $$
  select exists (
    select 1
    from public.user_roles ur
    join public.roles r on r.id = ur.role_id
    where ur.user_id = auth.uid()
      and r.name = role_name
  );
$$;

-- 4. Enable RLS
alter table public.roles enable row level security;
alter table public.profiles enable row level security;
alter table public.user_roles enable row level security;

-- 5. Policies
-- Roles are public read-only
create policy "Roles are viewable by everyone" on public.roles for select using (true);

-- Profiles
create policy "Users can view own profile" on public.profiles for select using (auth.uid() = id);
create policy "Admins can view all profiles" on public.profiles for select using (public.has_role('admin'));
create policy "Users can update own profile" on public.profiles for update using (auth.uid() = id);
create policy "Admins can update all profiles" on public.profiles for update using (public.has_role('admin'));

-- User Roles
create policy "Users can view own roles" on public.user_roles for select using (auth.uid() = user_id);
create policy "Admins can view all roles" on public.user_roles for select using (public.has_role('admin'));
create policy "Only admins can manage user roles" on public.user_roles for all using (public.has_role('admin'));

-- Trigger to update 'updated_at'
create or replace function public.handle_updated_at()
returns trigger
language plpgsql
as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

create trigger profile_updated_at
  before update on public.profiles
  for each row execute function public.handle_updated_at();

