# PRD: Integration Control Plane

> Product Requirements Document for the `ctrl` schema -- cross-system identity resolution, entity linking, sync state tracking, and integration event logging.

---

## Overview

The Integration Control Plane provides infrastructure-level tables and RPCs in Supabase for managing cross-system entity relationships. It answers: "Given an entity in System A, what is the corresponding entity in System B?" and "What is the current sync state between any two systems?"

This generalizes the existing `odoo.entity_mappings` and `odoo.sync_cursors` patterns (defined in `spec/schema/entities.yaml`) to support arbitrary system pairs: Odoo, Plane, Supabase app tables, n8n, Slack, and future integrations.

---

## Schema: `ctrl`

### Table: `ctrl.identity_map`

**Purpose**: Cross-system entity identity resolution. Maps a system-specific entity reference to a canonical UUID.

```sql
CREATE SCHEMA IF NOT EXISTS ctrl;

CREATE TABLE ctrl.identity_map (
    id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    system_name     text NOT NULL,
    system_entity_type text NOT NULL,
    system_entity_id   text NOT NULL,
    canonical_entity_type text NOT NULL,
    canonical_entity_id   uuid NOT NULL,
    metadata        jsonb DEFAULT '{}',
    created_at      timestamptz NOT NULL DEFAULT now(),
    updated_at      timestamptz NOT NULL DEFAULT now(),

    CONSTRAINT uq_identity_map_system_entity
        UNIQUE (system_name, system_entity_type, system_entity_id)
);

CREATE INDEX idx_identity_map_canonical
    ON ctrl.identity_map (canonical_entity_type, canonical_entity_id);

CREATE INDEX idx_identity_map_system
    ON ctrl.identity_map (system_name, system_entity_type);

COMMENT ON TABLE ctrl.identity_map IS
    'Cross-system entity identity resolution. Maps system-specific entity references to canonical UUIDs.';
```

**Example rows**:

| system_name | system_entity_type | system_entity_id | canonical_entity_type | canonical_entity_id |
|-------------|-------------------|-------------------|----------------------|---------------------|
| plane | issue | PROJ-123 | task | `a1b2c3d4-...` |
| odoo | project.task | 456 | task | `a1b2c3d4-...` |
| supabase | app.tasks | `a1b2c3d4-...` | task | `a1b2c3d4-...` |

**Use case**: "Given Plane issue PROJ-123, find the corresponding Odoo task and Supabase record" -- resolve the canonical ID, then look up all systems mapped to that canonical ID.

**Relationship to `odoo.entity_mappings`**: The existing `odoo.entity_mappings` table maps Supabase UUIDs to Odoo integer IDs for a specific Odoo instance. `ctrl.identity_map` generalizes this to any system pair. Existing `odoo.entity_mappings` rows can be projected into `ctrl.identity_map` with `system_name='odoo'` and `system_name='supabase'`.

---

### Table: `ctrl.entity_links`

**Purpose**: Bidirectional entity relationships across systems. Tracks how entities in different systems relate to each other.

```sql
CREATE TYPE ctrl.link_type AS ENUM ('sync', 'derived', 'reference');

CREATE TABLE ctrl.entity_links (
    id                  uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    source_system       text NOT NULL,
    source_entity_type  text NOT NULL,
    source_entity_id    text NOT NULL,
    target_system       text NOT NULL,
    target_entity_type  text NOT NULL,
    target_entity_id    text NOT NULL,
    link_type           ctrl.link_type NOT NULL,
    metadata            jsonb DEFAULT '{}',
    created_at          timestamptz NOT NULL DEFAULT now(),

    CONSTRAINT uq_entity_link
        UNIQUE (source_system, source_entity_type, source_entity_id,
                target_system, target_entity_type, target_entity_id, link_type)
);

CREATE INDEX idx_entity_links_source
    ON ctrl.entity_links (source_system, source_entity_type, source_entity_id);

CREATE INDEX idx_entity_links_target
    ON ctrl.entity_links (target_system, target_entity_type, target_entity_id);

COMMENT ON TABLE ctrl.entity_links IS
    'Bidirectional entity relationships across systems. Tracks sync, derived, and reference links.';
```

**Link types**:
- `sync` -- entities are kept in sync (e.g., Odoo invoice mirror in Supabase)
- `derived` -- one entity was created from another (e.g., CRM deal spawned a Plane project)
- `reference` -- loose association without sync obligation (e.g., Slack thread references an Odoo task)

**Example rows**:

| source_system | source_entity_type | source_entity_id | target_system | target_entity_type | target_entity_id | link_type |
|--------------|-------------------|-------------------|--------------|-------------------|-------------------|-----------|
| odoo | account.move | 789 | supabase | odoo_mirror.invoices | `uuid-...` | sync |
| supabase | app.deals | `uuid-...` | plane | project | PROJ-42 | derived |
| slack | message | 1709234567.001 | odoo | project.task | 456 | reference |

---

### Table: `ctrl.sync_state`

**Purpose**: Sync progress tracking per system pair per entity type. Generalizes `odoo.sync_cursors` for any system pair.

```sql
CREATE TYPE ctrl.sync_status AS ENUM ('idle', 'syncing', 'error', 'paused');

CREATE TABLE ctrl.sync_state (
    id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    source_system   text NOT NULL,
    target_system   text NOT NULL,
    entity_type     text NOT NULL,
    cursor_value    text,
    last_sync_at    timestamptz,
    sync_status     ctrl.sync_status NOT NULL DEFAULT 'idle',
    error_message   text,
    metadata        jsonb DEFAULT '{}',
    updated_at      timestamptz NOT NULL DEFAULT now(),

    CONSTRAINT uq_sync_state_pair
        UNIQUE (source_system, target_system, entity_type)
);

CREATE INDEX idx_sync_state_status
    ON ctrl.sync_state (sync_status);

COMMENT ON TABLE ctrl.sync_state IS
    'Sync progress tracking per system pair per entity type. Extends odoo.sync_cursors pattern for any system pair.';
```

**Relationship to `odoo.sync_cursors`**: The existing table tracks sync progress per Odoo instance per entity. `ctrl.sync_state` generalizes this: `source_system='odoo'`, `target_system='supabase'` is equivalent to a row in `odoo.sync_cursors`. The addition of `sync_status` and `error_message` adds operational visibility.

**Example rows**:

| source_system | target_system | entity_type | cursor_value | sync_status | last_sync_at |
|--------------|--------------|-------------|--------------|-------------|--------------|
| odoo | supabase | res.partner | 2026-03-07T10:00:00Z | idle | 2026-03-07T10:00:00Z |
| plane | supabase | issue | cursor_abc123 | syncing | 2026-03-07T09:55:00Z |
| supabase | odoo | app.tasks | 2026-03-07T08:00:00Z | error | 2026-03-07T08:00:00Z |

---

### Table: `ctrl.integration_events`

**Purpose**: Immutable event log for all cross-system operations. Used for audit trail, debugging, and replay.

```sql
CREATE TYPE ctrl.event_type AS ENUM (
    'entity_created',
    'entity_updated',
    'entity_deleted',
    'sync_started',
    'sync_completed',
    'sync_failed',
    'link_created',
    'conflict_detected',
    'conflict_resolved'
);

CREATE TABLE ctrl.integration_events (
    id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    event_type      ctrl.event_type NOT NULL,
    source_system   text NOT NULL,
    target_system   text,
    entity_type     text NOT NULL,
    entity_id       text NOT NULL,
    payload         jsonb DEFAULT '{}',
    created_at      timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX idx_integration_events_type
    ON ctrl.integration_events (event_type, created_at DESC);

CREATE INDEX idx_integration_events_system
    ON ctrl.integration_events (source_system, target_system, created_at DESC);

CREATE INDEX idx_integration_events_entity
    ON ctrl.integration_events (entity_type, entity_id, created_at DESC);

CREATE INDEX idx_integration_events_created
    ON ctrl.integration_events (created_at DESC);

COMMENT ON TABLE ctrl.integration_events IS
    'Immutable event log for all cross-system operations. Retention: 90 days (configurable).';
```

**Retention**: 90 days by default. Implement via pg_cron:

```sql
SELECT cron.schedule(
    'ctrl-events-retention',
    '0 3 * * *',
    $$DELETE FROM ctrl.integration_events WHERE created_at < now() - interval '90 days'$$
);
```

**Example rows**:

| event_type | source_system | target_system | entity_type | entity_id | payload |
|-----------|--------------|--------------|-------------|-----------|---------|
| entity_created | plane | supabase | issue | PROJ-123 | `{"title": "Fix bug"}` |
| sync_completed | odoo | supabase | res.partner | batch_42 | `{"count": 150, "duration_ms": 2340}` |
| conflict_detected | odoo | plane | project.task | 456 | `{"field": "status", "odoo": "done", "plane": "in_progress"}` |

---

## RPC Functions

### `resolve_identity`

Resolve a system-specific entity to its canonical ID.

```sql
CREATE OR REPLACE FUNCTION ctrl.resolve_identity(
    p_system text,
    p_entity_type text,
    p_entity_id text
) RETURNS uuid
LANGUAGE sql STABLE
SET search_path = ctrl, pg_temp
AS $$
    SELECT canonical_entity_id
    FROM ctrl.identity_map
    WHERE system_name = p_system
      AND system_entity_type = p_entity_type
      AND system_entity_id = p_entity_id;
$$;

COMMENT ON FUNCTION ctrl.resolve_identity IS
    'Resolve a system-specific entity reference to its canonical UUID.';
```

### `link_entities`

Create a bidirectional link between two entities in different systems.

```sql
CREATE OR REPLACE FUNCTION ctrl.link_entities(
    p_source_system text,
    p_source_entity_type text,
    p_source_entity_id text,
    p_target_system text,
    p_target_entity_type text,
    p_target_entity_id text,
    p_link_type ctrl.link_type DEFAULT 'reference'
) RETURNS uuid
LANGUAGE plpgsql
SET search_path = ctrl, pg_temp
AS $$
DECLARE
    v_link_id uuid;
BEGIN
    INSERT INTO ctrl.entity_links (
        source_system, source_entity_type, source_entity_id,
        target_system, target_entity_type, target_entity_id,
        link_type
    ) VALUES (
        p_source_system, p_source_entity_type, p_source_entity_id,
        p_target_system, p_target_entity_type, p_target_entity_id,
        p_link_type
    )
    ON CONFLICT ON CONSTRAINT uq_entity_link DO UPDATE
        SET metadata = ctrl.entity_links.metadata
    RETURNING id INTO v_link_id;

    RETURN v_link_id;
END;
$$;

COMMENT ON FUNCTION ctrl.link_entities IS
    'Create or return existing link between two entities in different systems. Idempotent.';
```

### `advance_cursor`

Advance the sync cursor for a system pair + entity type.

```sql
CREATE OR REPLACE FUNCTION ctrl.advance_cursor(
    p_source_system text,
    p_target_system text,
    p_entity_type text,
    p_new_cursor text
) RETURNS void
LANGUAGE plpgsql
SET search_path = ctrl, pg_temp
AS $$
BEGIN
    INSERT INTO ctrl.sync_state (
        source_system, target_system, entity_type,
        cursor_value, last_sync_at, sync_status, updated_at
    ) VALUES (
        p_source_system, p_target_system, p_entity_type,
        p_new_cursor, now(), 'idle', now()
    )
    ON CONFLICT ON CONSTRAINT uq_sync_state_pair DO UPDATE
        SET cursor_value = p_new_cursor,
            last_sync_at = now(),
            sync_status = 'idle',
            error_message = NULL,
            updated_at = now();
END;
$$;

COMMENT ON FUNCTION ctrl.advance_cursor IS
    'Advance sync cursor for a system pair + entity type. Creates row if not exists. Idempotent.';
```

### `log_event`

Log an integration event to the immutable event log.

```sql
CREATE OR REPLACE FUNCTION ctrl.log_event(
    p_event_type ctrl.event_type,
    p_source_system text,
    p_target_system text,
    p_entity_type text,
    p_entity_id text,
    p_payload jsonb DEFAULT '{}'
) RETURNS uuid
LANGUAGE sql
SET search_path = ctrl, pg_temp
AS $$
    INSERT INTO ctrl.integration_events (
        event_type, source_system, target_system,
        entity_type, entity_id, payload
    ) VALUES (
        p_event_type, p_source_system, p_target_system,
        p_entity_type, p_entity_id, p_payload
    )
    RETURNING id;
$$;

COMMENT ON FUNCTION ctrl.log_event IS
    'Log an integration event. Append-only, immutable.';
```

---

## RLS Policies

```sql
-- ctrl tables are NOT exposed via PostgREST API.
-- Access restricted to service_role and specific Edge Functions.

ALTER TABLE ctrl.identity_map ENABLE ROW LEVEL SECURITY;
ALTER TABLE ctrl.entity_links ENABLE ROW LEVEL SECURITY;
ALTER TABLE ctrl.sync_state ENABLE ROW LEVEL SECURITY;
ALTER TABLE ctrl.integration_events ENABLE ROW LEVEL SECURITY;

-- Service role bypass (Supabase default for service_role)
-- No anon or authenticated policies -- these tables are internal.
```

---

## Cross-References

- `spec/schema/entities.yaml` -- existing `odoo.sync_cursors` and `odoo.entity_mappings` definitions
- `spec/odoo-decoupled-platform/prd.md` -- Odoo decoupled architecture, FR-3 (Data Sync)
- `spec/parallel-control-planes/prd.md` -- multi-control-plane bridge pattern
- `docs/infra/ODOO_SUPABASE_MASTER_PATTERN.md` -- Supabase as State + Event Bus pattern
