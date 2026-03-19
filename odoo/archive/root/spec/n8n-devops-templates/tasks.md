# Tasks — n8n DevOps Templates Integration

## E1: SSOT Catalog
- [x] Create ssot/integrations/n8n_devops_templates.yaml
- [x] Define template_policy (allowed triggers, forbidden patterns)
- [x] Define telemetry contract (ops.runs, ops.run_events)
- [ ] Add CI validation for catalog schema

## E2: Deploy Notify Pipeline (active)
- [ ] Map deployment-notify.json to catalog entry ops_mapping
- [ ] Map vercel-drain-handler.json to catalog entry ops_mapping
- [ ] Add idempotency_key emission (deploy:{provider}:{deploy_id})
- [ ] Verify ops.runs + ops.run_events written on execution

## E3: GitHub Webhook Ops Router
- [ ] Normalize github-events-handler.json under catalog slug
- [ ] Normalize github-router.json under catalog slug
- [ ] Normalize github-deploy-trigger.json under catalog slug
- [ ] Implement delivery_id-based idempotency
- [ ] Add Slack/Vercel/Supabase fan-out routing
- [ ] Test: zero duplicate alerts under webhook retries

## E4: DO Droplet Provisioning
- [ ] Import DO droplet creation pattern from n8n template library
- [ ] Normalize to ops.runs with do:droplet:{name}:{region} key
- [ ] Register do_access_token as secret consumer
- [ ] Add Advisor signals (Reliability, Cost)

## E5: Incident Intake Router
- [ ] Create incident-intake-router workflow
- [ ] Implement fingerprint-based dedup
- [ ] Implement update-vs-create policy
- [ ] Add rate limit guard with backoff
- [ ] Register in catalog with ops_mapping

## E6: Secrets Rotation Reminder
- [ ] Create weekly cron workflow
- [ ] Read ssot/secrets/registry.yaml rotation_policy
- [ ] Compare against last_rotated timestamps
- [ ] Alert overdue rotations via Slack
- [ ] Register in catalog with ops_mapping

## E7: Advisor Integration
- [ ] Wire automation_coverage scoring
- [ ] Wire failure_rate scoring
- [ ] Wire cost_signals scoring
- [ ] Wire security_compliance scoring
- [ ] Dashboard: template health overview

## E8: Template API Harvester (stretch)
- [ ] n8n template API client (list/search/fetch)
- [ ] Normalize fetched templates to catalog entry format
- [ ] Policy validation gate before activation
- [ ] Store normalized JSON in automations/n8n/templates/
