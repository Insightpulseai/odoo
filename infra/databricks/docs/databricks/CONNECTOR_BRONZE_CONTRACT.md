# Connector Bronze Contract

> Frozen system column specification for all bronze connector tables.
> This contract is immutable — changes require a migration plan and version bump.

## System Columns

All bronze tables created by the connector SDK include these system columns:

| Column | Type | Nullable | Source | Description |
|--------|------|----------|--------|-------------|
| `_fivetran_id` | STRING | NOT NULL | SyncEngine | Deterministic row ID (SHA-256 of PK columns, 32 hex chars) |
| `_fivetran_synced` | TIMESTAMP | NOT NULL | SyncEngine | UTC timestamp when row was synced to Delta |
| `_fivetran_deleted` | BOOLEAN | NOT NULL | SyncEngine | Soft-delete flag (true = source deleted this row) |

## SCD2 History Columns (when `history_mode=true`)

| Column | Type | Nullable | Source | Description |
|--------|------|----------|--------|-------------|
| `_fivetran_active` | BOOLEAN | NOT NULL | SyncEngine | True for the current version of the row |
| `_fivetran_start` | TIMESTAMP | NOT NULL | SyncEngine | When this version became active |
| `_fivetran_end` | TIMESTAMP | NULL | SyncEngine | When this version was superseded (NULL = current) |

## Deterministic ID Contract

`_fivetran_id` is computed as:

```
SHA-256(f"{table_name}:{json.dumps(pk_data, sort_keys=True)}")[:32]
```

Where `pk_data` contains **only the declared primary key columns** from the connector's `TableDef.primary_key`. If no PK is declared, all data columns are used (fallback).

**Stability rule:** The same logical row (same PK values) always produces the same `_fivetran_id`, regardless of changes to mutable columns.

## Cursor Semantics

- Each connector maintains its own cursor shape in `connector_state.state_json`
- Cursors are **only advanced when a CHECKPOINT op is received**
- If no CHECKPOINT is emitted, the sync is treated as failed and state is not advanced
- This prevents data loss and duplicate ingestion on retry

## Table Properties

All bronze connector tables are created with:

```sql
USING DELTA
TBLPROPERTIES (
    'delta.enableChangeDataFeed' = 'true',
    'delta.autoOptimize.optimizeWrite' = 'true'
)
```

## Soft Delete Behavior

- DELETE ops set `_fivetran_deleted = true` (never physically delete rows)
- In SCD2 mode, DELETE also closes the active version (`_fivetran_active = false`)
- Downstream layers (silver/gold) should filter on `_fivetran_deleted = false`

## PK Stability Rules

1. Primary keys declared in `TableDef.primary_key` must be immutable in the source
2. PK columns must always be present in UPSERT op data
3. PK changes in the source result in a new row (different `_fivetran_id`)
4. Connectors must NOT change their PK declaration between versions without migration

## Raw Payload Convention

Connectors may include a `_raw_payload` column (type STRING) containing the full JSON response from the source API. This is optional but recommended for debugging and reprocessing.
