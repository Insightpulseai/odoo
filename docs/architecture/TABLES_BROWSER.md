# Tables Browser Architecture

> Supabase Studio-style database tables browser with schema grouping and exposed schemas.

## Overview

The Tables Browser provides a visual interface for exploring database tables, views, and materialized views. It follows the Supabase Studio design pattern with:

- **Schema grouping**: Tables organized by database schema
- **Exposed schemas**: Admin-controlled allowlist of schemas visible to non-admin users
- **Fast metadata**: Uses `pg_catalog` for instant row estimates (no full table scans)
- **On-demand details**: Exact row counts and sample data loaded when viewing a specific table

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Frontend (Next.js)                           │
├─────────────────────────────────────────────────────────────────────┤
│  /settings/database/tables        │  /settings/database/tables/     │
│  ├── TablesBrowser component      │  [schema]/[table]               │
│  ├── SchemaFilter                 │  └── Table detail view          │
│  └── TableCard grid               │      ├── Column metadata        │
│                                   │      ├── Exact row count        │
│                                   │      └── Sample rows (100)      │
├─────────────────────────────────────────────────────────────────────┤
│                         API Routes (Next.js)                         │
├─────────────────────────────────────────────────────────────────────┤
│  GET /api/tables                  │  Calls api.list_relations()     │
│  GET /api/tables/schemas          │  Calls api.list_schemas()       │
│  POST /api/tables/schemas         │  Calls api.toggle_schema_exp()  │
│  GET /api/tables/[schema]/[table] │  Calls get_table_columns(),     │
│                                   │  count_rows(), get_table_sample │
├─────────────────────────────────────────────────────────────────────┤
│                         Supabase (PostgreSQL)                        │
├─────────────────────────────────────────────────────────────────────┤
│  ops.exposed_schemas              │  Schema allowlist table         │
│  api.list_relations()             │  Fast relation listing RPC      │
│  api.list_schemas()               │  Schema listing with counts     │
│  api.count_rows()                 │  Exact row count (on-demand)    │
│  api.get_table_columns()          │  Column metadata via info_schema│
│  api.get_table_sample()           │  Sample rows as JSONB array     │
│  api.toggle_schema_exposure()     │  Toggle schema visibility       │
└─────────────────────────────────────────────────────────────────────┘
```

## Database Schema

### ops.exposed_schemas

Controls which schemas are exposed to non-admin users in the Tables browser.

```sql
create table ops.exposed_schemas (
    schema_name text primary key,
    exposed boolean not null default true,
    description text,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);
```

**RLS Policies:**
- `SELECT`: Allowed for all authenticated users
- `INSERT/UPDATE/DELETE`: Restricted to `service_role`

### Default Exposed Schemas

- `public` - Seeded as exposed by default

## RPC Functions

### api.list_relations(include_views, include_system)

Returns all database relations with estimated row counts.

**Performance**: Uses `pg_catalog.pg_class.reltuples` for instant estimates (no COUNT(*) scans).

```sql
-- Returns:
-- schema_name, relation_name, relation_type, row_estimate, is_exposed
select * from api.list_relations(
    include_views := true,   -- Include views
    include_system := false  -- Exclude pg_catalog, information_schema
);
```

**Relation Types:**
- `table` - Regular tables (relkind='r')
- `view` - Views (relkind='v')
- `materialized_view` - Materialized views (relkind='m')
- `partitioned_table` - Partitioned tables (relkind='p')

### api.count_rows(p_schema_name, p_relation_name)

Returns exact row count for a specific table. **Use sparingly** - performs full table scan.

```sql
select api.count_rows('public', 'users');
```

### api.get_table_columns(p_schema_name, p_table_name)

Returns column metadata including primary key information.

```sql
select * from api.get_table_columns('public', 'users');
-- Returns: column_name, data_type, is_nullable, column_default, ordinal_position, is_primary_key
```

### api.get_table_sample(p_schema_name, p_table_name, p_limit)

Returns sample rows as JSONB array. Limited to 1000 rows max.

```sql
select api.get_table_sample('public', 'users', 100);
```

### api.list_schemas()

Returns all schemas with exposure status and table counts.

```sql
select * from api.list_schemas();
-- Returns: schema_name, is_exposed, table_count, description
```

### api.toggle_schema_exposure(p_schema_name, p_exposed, p_description)

Toggles schema visibility. **Restricted to service_role.**

```sql
select api.toggle_schema_exposure('analytics', true, 'Analytics tables');
```

## Frontend Components

### TablesBrowser

Main component with:
- Search box (debounced, client-side filtering)
- Schema dropdown (All / Exposed / specific schema)
- View mode toggle (grid / list)
- Group by schema toggle
- Include views checkbox
- Refresh button

### TableCard

Individual table tile showing:
- Table name
- Schema name (when not grouped)
- Relation type icon (table/view/materialized)
- Estimated row count
- "exposed" badge for exposed schemas

### SchemaFilter

Listbox dropdown with:
- All Schemas (virtual option)
- Exposed Schemas (virtual option, filters to exposed=true)
- Grouped schema list (Exposed / Other sections)
- Table count per schema

## React Query Hooks

### useTables.ts

```typescript
// Fetch all relations
const { data, isLoading } = useRelations({ includeViews: true });

// Fetch schemas
const { data: schemas } = useSchemas();

// Fetch table details
const { data: details } = useTableDetails('public', 'users');

// Toggle schema exposure
const toggleMutation = useToggleSchemaExposure();
await toggleMutation.mutateAsync({ schemaName: 'analytics', exposed: true });
```

**Cache Configuration:**
- `staleTime: 60s` for relations and schemas
- `staleTime: 30s` for table details
- `refetchOnWindowFocus: false`

## API Routes

| Route | Method | Description |
|-------|--------|-------------|
| `/api/tables` | GET | List all relations |
| `/api/tables/schemas` | GET | List all schemas |
| `/api/tables/schemas` | POST | Toggle schema exposure |
| `/api/tables/[schema]/[table]` | GET | Get table details |

## Security Model

### Schema Exposure

1. **Default**: Only `public` schema is exposed
2. **Admin control**: Toggle via `api.toggle_schema_exposure()` (service_role only)
3. **Non-admin users**: Only see tables in exposed schemas via RLS

### RLS Implementation

```sql
-- ops.exposed_schemas
-- Read: All authenticated users
-- Write: service_role only

-- api.list_relations returns is_exposed flag
-- Frontend can filter by exposed schemas client-side
```

## File Locations

| File | Description |
|------|-------------|
| `supabase/migrations/20260124200001_ops_tables_browser.sql` | Database migration |
| `apps/control-room/src/hooks/useTables.ts` | React Query hooks |
| `apps/control-room/src/lib/supabase.ts` | Types (DatabaseRelation, etc.) |
| `apps/control-room/src/components/tables-browser/` | UI components |
| `apps/control-room/src/app/settings/database/tables/page.tsx` | Tables list page |
| `apps/control-room/src/app/settings/database/tables/[schema]/[table]/page.tsx` | Table detail page |
| `apps/control-room/src/app/api/tables/` | API routes |

## Usage

### View Tables

Navigate to `/settings/database/tables` to see all database tables.

### Filter by Schema

Use the schema dropdown to filter:
- **All Schemas**: Show everything
- **Exposed Schemas**: Show only tables in exposed schemas
- **Specific schema**: Show tables in that schema only

### View Table Details

Click any table card to view:
- Column definitions (name, type, nullable, default, primary key)
- Exact row count
- Sample data (first 100 rows)

### Expose a Schema (Admin)

```typescript
// Via API route
await fetch('/api/tables/schemas', {
  method: 'POST',
  body: JSON.stringify({ schema_name: 'analytics', exposed: true }),
});
```

## Performance Considerations

1. **Row estimates**: `pg_class.reltuples` provides instant estimates without scanning
2. **No full scans on list**: Never runs COUNT(*) for the table list
3. **On-demand exact counts**: Only fetched when viewing a specific table
4. **Sample rows**: Limited to 1000 max, uses LIMIT clause
5. **Client-side filtering**: Search and filter happen after initial fetch (fast for <1000 tables)

## Future Enhancements

- [ ] Table creation wizard
- [ ] Column editing
- [ ] Row editing with RLS awareness
- [ ] Real-time subscription for table changes
- [ ] Export to CSV/JSON
- [ ] SQL query builder

---

*Last updated: 2026-01-24*
