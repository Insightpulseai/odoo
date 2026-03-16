-- ops schema: job control-plane for n8n/workers/edge functions
create schema if not exists ops;

create table if not exists ops.runs (
  id bigserial primary key,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  source text not null,          -- n8n | slack | github | vercel | manual
  kind text not null,            -- ingestion | transform | export | notify | build
  status text not null default 'queued',  -- queued|running|succeeded|failed|canceled
  priority int not null default 100,
  dedupe_key text,               -- optional idempotency key
  payload jsonb not null default '{}'::jsonb,
  result jsonb
);

create index if not exists runs_status_priority_idx
  on ops.runs (status, priority, created_at);

create unique index if not exists runs_dedupe_key_uniq
  on ops.runs (dedupe_key)
  where dedupe_key is not null;

create table if not exists ops.run_events (
  id bigserial primary key,
  run_id bigint not null references ops.runs(id) on delete cascade,
  ts timestamptz not null default now(),
  level text not null default 'info',     -- info|warn|error
  message text not null,
  data jsonb
);

create index if not exists run_events_run_id_ts_idx
  on ops.run_events (run_id, ts);

create table if not exists ops.artifacts (
  id bigserial primary key,
  run_id bigint not null references ops.runs(id) on delete cascade,
  ts timestamptz not null default now(),
  kind text not null,                     -- log|file|url|json|metrics
  uri text,                               -- storage path or external url
  content jsonb                           -- inline small artifact
);

create index if not exists artifacts_run_id_ts_idx
  on ops.artifacts (run_id, ts);
