-- supabase/migrations/20260223000005_jobs_rpc.sql

create schema if not exists ops;

create or replace function ops.claim_jobs(p_worker_id text, p_limit int default 1)
returns setof ops.jobs
language plpgsql
as $$
begin
  return query
  with cte as (
    select id
    from ops.jobs
    where status = 'queued'
      and locked_at is null
      and run_after <= now()
    order by id asc
    for update skip locked
    limit p_limit
  )
  update ops.jobs j
    set status = 'running',
        locked_at = now(),
        locked_by = p_worker_id,
        attempts = attempts + 1,
        updated_at = now()
  from cte
  where j.id = cte.id
  returning j.*;
end;
$$;
