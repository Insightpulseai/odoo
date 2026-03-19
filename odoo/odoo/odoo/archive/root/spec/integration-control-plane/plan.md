# Plan: Integration Control Plane

> Implementation phases for the `ctrl` schema, RPCs, and Edge Function integration.

---

## Phase 1: Schema + Identity Map + Entity Links

**Goal**: Establish the `ctrl` schema and the two core relationship tables.

### Steps

1. Create Supabase migration: `ctrl` schema creation
2. Create `ctrl.identity_map` table with unique constraint and indexes
3. Create `ctrl.entity_links` table with `ctrl.link_type` enum, unique constraint, and indexes
4. Create `resolve_identity()` RPC
5. Create `link_entities()` RPC
6. Enable RLS on both tables (service_role only, no anon/authenticated policies)
7. Write seed data for dev/test: sample identity mappings for Odoo + Supabase + Plane

### Verification

```bash
# Migration applies cleanly
supabase db push --dry-run

# Tables exist
psql "$POSTGRES_URL" -c "SELECT count(*) FROM ctrl.identity_map;"
psql "$POSTGRES_URL" -c "SELECT count(*) FROM ctrl.entity_links;"

# RPC works
psql "$POSTGRES_URL" -c "SELECT ctrl.resolve_identity('odoo', 'project.task', '456');"
```

### Dependencies

- Supabase project `spdtwktxdalcfigzeqrz` accessible
- Migration naming follows existing `supabase/migrations/` conventions

---

## Phase 2: Sync State + Cursor Management

**Goal**: Generalize `odoo.sync_cursors` into `ctrl.sync_state` for any system pair.

### Steps

1. Create `ctrl.sync_status` enum
2. Create `ctrl.sync_state` table with unique constraint and indexes
3. Create `advance_cursor()` RPC (upsert with idempotency)
4. Backfill existing `odoo.sync_cursors` data into `ctrl.sync_state` (source=odoo, target=supabase)
5. Add monitoring query for stale cursors (last_sync_at > 1 hour with status != paused)

### Verification

```bash
# Cursor advance is idempotent
psql "$POSTGRES_URL" -c "
    SELECT ctrl.advance_cursor('odoo', 'supabase', 'res.partner', '2026-03-07T10:00:00Z');
    SELECT ctrl.advance_cursor('odoo', 'supabase', 'res.partner', '2026-03-07T10:00:00Z');
    SELECT count(*) FROM ctrl.sync_state
    WHERE source_system='odoo' AND target_system='supabase' AND entity_type='res.partner';
" -- should return 1

# Status tracking works
psql "$POSTGRES_URL" -c "
    SELECT source_system, target_system, entity_type, sync_status
    FROM ctrl.sync_state;
"
```

### Dependencies

- Phase 1 complete (schema exists)

---

## Phase 3: Integration Events + Event Logging

**Goal**: Immutable event log for audit, debugging, and replay of all cross-system operations.

### Steps

1. Create `ctrl.event_type` enum
2. Create `ctrl.integration_events` table with time-based indexes
3. Create `log_event()` RPC
4. Enable RLS (service_role only)
5. Set up pg_cron retention job (90-day default)
6. Create monitoring view: `ctrl.v_recent_events` (last 24 hours, grouped by event_type)

### Verification

```bash
# Event logging works
psql "$POSTGRES_URL" -c "
    SELECT ctrl.log_event(
        'sync_completed', 'odoo', 'supabase', 'res.partner', 'batch_1',
        '{\"count\": 50}'::jsonb
    );
"

# Retention job scheduled
psql "$POSTGRES_URL" -c "SELECT * FROM cron.job WHERE jobname = 'ctrl-events-retention';"
```

### Dependencies

- Phase 1 complete (schema exists)
- pg_cron extension enabled in Supabase

---

## Phase 4: Edge Functions + n8n Integration

**Goal**: Expose identity resolution and event logging as callable Edge Functions for n8n workflows and external systems.

### Steps

1. Create Edge Function `ctrl-resolve-identity`:
   - Input: `{ system, entity_type, entity_id }`
   - Output: `{ canonical_entity_id, all_mappings: [...] }`
   - Auth: service_role key required

2. Create Edge Function `ctrl-log-event`:
   - Input: `{ event_type, source_system, target_system, entity_type, entity_id, payload }`
   - Output: `{ event_id }`
   - Auth: service_role key required

3. Create n8n workflow template: `n8n/workflows/ctrl-identity-resolver.json`
   - HTTP Request node calls `ctrl-resolve-identity`
   - Used in sync pipelines to resolve cross-system IDs

4. Create n8n workflow template: `n8n/workflows/ctrl-event-logger.json`
   - HTTP Request node calls `ctrl-log-event`
   - Used as a sub-workflow in all integration pipelines

5. Update `docs/infra/ODOO_SUPABASE_MASTER_PATTERN.md` with ctrl schema reference

### Verification

```bash
# Edge Function responds
curl -s -H "Authorization: Bearer $SUPABASE_SERVICE_ROLE_KEY" \
    "$SUPABASE_URL/functions/v1/ctrl-resolve-identity" \
    -d '{"system":"odoo","entity_type":"project.task","entity_id":"456"}' \
    | jq .canonical_entity_id

# n8n workflow importable
curl -X POST "http://localhost:5678/api/v1/workflows" \
    -H "X-N8N-API-KEY: $N8N_API_KEY" \
    -d @n8n/workflows/ctrl-identity-resolver.json
```

### Dependencies

- Phases 1-3 complete
- Supabase Edge Functions runtime available
- n8n instance accessible

---

## Migration Naming Convention

All migrations for this spec follow the existing pattern in `supabase/migrations/`:

```
supabase/migrations/YYYYMMDD_ctrl_phase1_identity_map.sql
supabase/migrations/YYYYMMDD_ctrl_phase1_entity_links.sql
supabase/migrations/YYYYMMDD_ctrl_phase2_sync_state.sql
supabase/migrations/YYYYMMDD_ctrl_phase3_integration_events.sql
```

---

## Cross-References

- `spec/integration-control-plane/constitution.md` -- non-negotiable rules
- `spec/integration-control-plane/prd.md` -- table definitions and RPCs
- `spec/schema/entities.yaml` -- existing entity schema to extend
- `docs/infra/ODOO_SUPABASE_MASTER_PATTERN.md` -- integration patterns
