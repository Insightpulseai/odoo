# Tasks: Integration Control Plane

> Checklist for implementing the `ctrl` schema. All tasks pending.

---

## Phase 1: Schema + Identity Map + Entity Links

- [ ] Create migration: `ctrl` schema (`CREATE SCHEMA IF NOT EXISTS ctrl`)
- [ ] Create migration: `ctrl.identity_map` table with unique constraint and indexes
- [ ] Create migration: `ctrl.link_type` enum
- [ ] Create migration: `ctrl.entity_links` table with unique constraint and indexes
- [ ] Create RPC: `ctrl.resolve_identity(system, entity_type, entity_id) -> uuid`
- [ ] Create RPC: `ctrl.link_entities(source, target) -> uuid`
- [ ] Enable RLS on `ctrl.identity_map` (service_role only)
- [ ] Enable RLS on `ctrl.entity_links` (service_role only)
- [ ] Write seed data: sample identity mappings (Odoo + Supabase + Plane)
- [ ] Verify: migration applies cleanly (`supabase db push --dry-run`)

## Phase 2: Sync State + Cursor Management

- [ ] Create migration: `ctrl.sync_status` enum
- [ ] Create migration: `ctrl.sync_state` table with unique constraint and indexes
- [ ] Create RPC: `ctrl.advance_cursor(source, target, entity_type, cursor) -> void`
- [ ] Enable RLS on `ctrl.sync_state` (service_role only)
- [ ] Create backfill script: project existing `odoo.sync_cursors` rows into `ctrl.sync_state`
- [ ] Create monitoring query: stale cursor detection
- [ ] Verify: cursor advance is idempotent

## Phase 3: Integration Events + Event Logging

- [ ] Create migration: `ctrl.event_type` enum
- [ ] Create migration: `ctrl.integration_events` table with time-based indexes
- [ ] Create RPC: `ctrl.log_event(event_type, source, target, entity, payload) -> uuid`
- [ ] Enable RLS on `ctrl.integration_events` (service_role only)
- [ ] Create pg_cron retention job: 90-day cleanup
- [ ] Create monitoring view: `ctrl.v_recent_events` (last 24h grouped by type)
- [ ] Verify: event logging works end-to-end

## Phase 4: Edge Functions + n8n Integration

- [ ] Create Edge Function: `ctrl-resolve-identity`
- [ ] Create Edge Function: `ctrl-log-event`
- [ ] Create n8n workflow template: `ctrl-identity-resolver.json`
- [ ] Create n8n workflow template: `ctrl-event-logger.json`
- [ ] Update `docs/infra/ODOO_SUPABASE_MASTER_PATTERN.md` with ctrl schema reference
- [ ] Update `spec/schema/entities.yaml` with ctrl schema definition
- [ ] Verify: Edge Functions respond with correct data
- [ ] Verify: n8n workflows importable and functional

## Documentation

- [ ] Add `ctrl` schema to `spec/schema/entities.yaml` schema definitions section
- [ ] Cross-reference from `spec/odoo-decoupled-platform/prd.md`
- [ ] Add ctrl schema to repo architecture docs

---

## Status Summary

| Phase | Tasks | Done | Remaining |
|-------|-------|------|-----------|
| Phase 1 | 10 | 0 | 10 |
| Phase 2 | 7 | 0 | 7 |
| Phase 3 | 7 | 0 | 7 |
| Phase 4 | 8 | 0 | 8 |
| Docs | 3 | 0 | 3 |
| **Total** | **35** | **0** | **35** |
