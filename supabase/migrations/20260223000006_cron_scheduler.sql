-- supabase/migrations/20260223000006_cron_scheduler.sql

-- Enable extensions
create extension if not exists pg_cron;
create extension if not exists pg_net;

-- Store the Edge Function URL + token in a config table (non-secret)
create table if not exists ops.edge_targets (
  name text primary key,
  url text not null,
  created_at timestamptz not null default now()
);

-- Note: In production you replace this URL with the actual project URL via ENV replacement
insert into ops.edge_targets(name, url)
values ('jobs_worker_tick', 'https://127.0.0.1:54321/functions/v1/tick')
on conflict (name) do update set url = excluded.url;

create or replace function ops.invoke_edge(name text, bearer_token text)
returns void
language plpgsql
as $$
declare
  target_url text;
begin
  select url into target_url from ops.edge_targets where ops.edge_targets.name = name;
  if target_url is null then
    raise exception 'Unknown edge target: %', name;
  end if;

  perform net.http_post(
    url := target_url,
    headers := jsonb_build_object(
      'content-type','application/json',
      'authorization', format('Bearer %s', bearer_token)
    ),
    body := '{}'::jsonb
  );
end;
$$;

-- Schedule every minute
-- We use a dummy token for local dev, which should be overridden in production vault
select cron.schedule(
  'jobs-worker-tick-every-minute',
  '* * * * *',
  $$select ops.invoke_edge('jobs_worker_tick', current_setting('app.jobs_tick_token', true));$$
);
