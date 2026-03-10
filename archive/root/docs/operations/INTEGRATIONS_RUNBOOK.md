# Integrations Runbook (Supabase ops.\* backbone)

## Inbound pattern

External webhook -> Edge Function `webhook-ingest` -> ops.webhook_events -> ops.jobs -> `jobs-worker`

## Outbound pattern

App writes ops.jobs (job_type=email.send, etc.) -> jobs-worker dispatch -> provider API

## Health

- Edge Function: `health`
- Views: ops.integration_metrics, ops.queue_metrics

## Stripe

- Signature validation uses RAW request body
- Supports multiple v1 signatures
- Enforces tolerance via STRIPE_TOLERANCE_SECONDS

## Cron tick

- pg_cron schedules ops.invoke_edge('jobs_worker_tick', app.jobs_tick_token)
- `tick` Edge Function triggers jobs-worker
