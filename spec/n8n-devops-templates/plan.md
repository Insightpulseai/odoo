# Plan — n8n DevOps Templates Integration

## Phase 1 — SSOT Catalog + Active Template (Week 1)
- Create ssot/integrations/n8n_devops_templates.yaml
- Document deploy-notify-pipeline as first "active" template
  (maps existing deployment-notify.json + vercel-drain-handler.json)
- Add ops_mapping to existing workflows
- Verify telemetry: ops.runs + ops.run_events written on execution

## Phase 2 — GitHub Webhook Router (Week 2)
- Normalize existing github-events-handler.json, github-router.json,
  github-deploy-trigger.json under github-webhook-ops-router slug
- Implement delivery_id-based idempotency
- Add fan-out to Slack, Vercel, Supabase Edge Functions
- Verify: zero duplicate alerts under webhook retries

## Phase 3 — DO Provisioning + Incident Intake (Week 3-4)
- Import DO droplet creation template from n8n library
- Normalize to ops.runs with do:droplet:{name}:{region} idempotency
- Create incident-intake-router (Sentry/monitoring → work item)
- Implement fingerprint-based dedup (update vs create policy)
- Add rate limit guard with backoff

## Phase 4 — Secrets Rotation + Advisor (Week 4-5)
- Create secrets-rotation-reminder cron template
- Read ssot/secrets/registry.yaml rotation_policy fields
- Alert on overdue rotations via Slack
- Wire all 5 templates to Advisor scoring engine:
  - automation_coverage
  - failure_rate
  - cost_signals
  - security_compliance

## Phase 5 — Template API Harvester (Week 6, stretch)
- Programmatic n8n template API integration
- Fetch/search DevOps category templates
- Normalize to catalog entry format
- Policy validation gate before activation
