-- supabase/migrations/20260223000004_ops_integrations.sql

create schema if not exists ops;

-- Integrations registry (non-secret config only)
create table if not exists ops.integrations (
  id bigserial primary key,
  name text not null unique,
  enabled boolean not null default true,
  config jsonb not null default '{}'::jsonb,
  last_seen_at timestamptz,
  last_error_at timestamptz,
  error_count bigint not null default 0,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

-- Raw webhook landing (immutable-ish)
create table if not exists ops.webhook_events (
  id bigserial primary key,
  integration text not null,
  event_type text,
  idempotency_key text,
  signature_valid boolean not null default false,
  received_at timestamptz not null default now(),
  headers jsonb not null default '{}'::jsonb,
  payload jsonb not null,
  processed_at timestamptz,
  status text not null default 'received', -- received|queued|processed|failed
  error text
);

create unique index if not exists webhook_events_idempotency
on ops.webhook_events(integration, idempotency_key)
where idempotency_key is not null;

-- Durable jobs queue
create table if not exists ops.jobs (
  id bigserial primary key,
  integration text not null,
  job_type text not null,
  payload jsonb not null,
  run_after timestamptz not null default now(),
  attempts int not null default 0,
  max_attempts int not null default 10,
  locked_at timestamptz,
  locked_by text,
  status text not null default 'queued', -- queued|running|done|failed|dead
  last_error text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index if not exists jobs_queue_idx
on ops.jobs(status, run_after)
where status = 'queued';

-- Derived tables (optional but useful)
create table if not exists ops.deployments (
  id bigserial primary key,
  provider text not null default 'vercel',
  provider_id text,
  project_id text,
  env text,
  url text,
  status text,
  created_at timestamptz not null default now(),
  raw_event_id bigint references ops.webhook_events(id)
);

create table if not exists ops.billing_events (
  id bigserial primary key,
  provider text not null default 'stripe',
  provider_id text,
  customer_id text,
  event_type text,
  amount bigint,
  currency text,
  created_at timestamptz not null default now(),
  raw_event_id bigint references ops.webhook_events(id)
);

create table if not exists ops.email_events (
  id bigserial primary key,
  provider text not null default 'resend',
  provider_id text,
  to_email text,
  template text,
  status text,
  created_at timestamptz not null default now(),
  raw_event_id bigint references ops.webhook_events(id)
);

-- Lock down ops schema: service only
alter table ops.integrations enable row level security;
alter table ops.webhook_events enable row level security;
alter table ops.jobs enable row level security;
alter table ops.deployments enable row level security;
alter table ops.billing_events enable row level security;
alter table ops.email_events enable row level security;

-- No access for anon/authenticated (service role bypasses RLS)
create policy "deny_all_integrations" on ops.integrations for all using (false);
create policy "deny_all_webhook_events" on ops.webhook_events for all using (false);
create policy "deny_all_jobs" on ops.jobs for all using (false);
create policy "deny_all_deployments" on ops.deployments for all using (false);
create policy "deny_all_billing_events" on ops.billing_events for all using (false);
create policy "deny_all_email_events" on ops.email_events for all using (false);
