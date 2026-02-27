-- Supabase Edge Function Scheduled Bindings (pg_cron)
-- Origin: Inventory Agent Sweep (Action item: Formalize Edge Function Schedulers)

-- We explicitly bind known scheduled edge functions to pg_cron extension
create extension if not exists pg_cron;

-- 1. cron-processor (Assuming every minute execution based on name)
select cron.schedule(
    'invoke-cron-processor',
    '* * * * *', -- Every minute
    $$
    select net.http_post(
        url:='http://supabase_kong:8000/functions/v1/cron-processor',
        headers:='{"Content-Type": "application/json", "Authorization": "Bearer ' || current_setting('request.jwt.claim.role', true) || '"}'::jsonb,
        body:='{}'::jsonb
    ) as request_id;
    $$
);

-- 2. repo-hygiene-runner (Assuming nightly based on common CI tasks)
select cron.schedule(
    'invoke-repo-hygiene',
    '0 2 * * *', -- 2 AM UTC daily
    $$
    select net.http_post(
        url:='http://supabase_kong:8000/functions/v1/repo-hygiene-runner',
        headers:='{"Content-Type": "application/json", "Authorization": "Bearer ' || current_setting('request.jwt.claim.role', true) || '"}'::jsonb,
        body:='{}'::jsonb
    ) as request_id;
    $$
);

-- 3. ops-advisory-scan (Assuming weekly security sweep)
select cron.schedule(
    'invoke-ops-advisory-scan',
    '0 3 * * 0', -- 3 AM UTC Sunday
    $$
    select net.http_post(
        url:='http://supabase_kong:8000/functions/v1/ops-advisory-scan',
        headers:='{"Content-Type": "application/json", "Authorization": "Bearer ' || current_setting('request.jwt.claim.role', true) || '"}'::jsonb,
        body:='{}'::jsonb
    ) as request_id;
    $$
);
