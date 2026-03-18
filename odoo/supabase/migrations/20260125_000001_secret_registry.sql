create schema if not exists ops;

create table if not exists ops.secret_registry (
  secret_name text primary key,
  status text not null default 'active' check (status in ('active','deprecated','revoked')),
  last_updated_at timestamptz not null default now(),
  last_used_at timestamptz null,
  last_used_by text null,
  notes text null
);

create or replace function ops.touch_secret(_name text, _used_by text default null)
returns void
language plpgsql
security definer
as $$
begin
  insert into ops.secret_registry(secret_name, last_used_at, last_used_by)
  values (_name, now(), _used_by)
  on conflict (secret_name) do update
    set last_used_at = excluded.last_used_at,
        last_used_by = excluded.last_used_by;
end $$;

revoke all on schema ops from public;
revoke all on all tables in schema ops from public;
