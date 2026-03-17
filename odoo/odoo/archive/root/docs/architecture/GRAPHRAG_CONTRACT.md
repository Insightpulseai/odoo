# GRAPHRAG_CONTRACT.md — GraphRAG KB Layer Schema Contract

```
contract_version: 1.0.0
indexer_version:  1.1.0
status:           active
applies_to:       supabase/migrations/20260223000008_kb_graph_layer.sql
last_updated:     2026-02-23
```

This contract defines the canonical schema for the GraphRAG knowledge-graph layer
(`kb_nodes` + `kb_edges`) in Supabase. It governs:

- Allowed node and edge kinds
- Required + optional fields per kind
- Permitted (src_kind → dst_kind) pairs
- Uniqueness and cascade rules
- Provenance requirements
- Path normalization (the `kb_chunks.path ↔ kb_nodes.path` join key)

---

## 1. Node Kinds

### 1.1 Emitted by indexer (`scripts/build_kb_graph.py`)

| kind | `type` field | `name` | `path` | `module` | `attrs` |
|------|-------------|--------|--------|----------|---------|
| `OdooModule` | `OdooModule` | module directory name (e.g. `ipai_finance_ppm`) | repo-relative dir path | same as name | `{version, author, category, depends[]}` |
| `File` | `File` | filename (e.g. `project_task_integration.py`) | repo-relative file path | owning module name | `{}` |
| `Model` | `Model` | Python class name (e.g. `ProjectTask`) | path of defining file | owning module name | `{}` |

### 1.2 Reserved (defined in schema, not yet emitted)

| kind | Description | Planned source |
|------|-------------|----------------|
| `View` | Odoo XML view (`<record model="ir.ui.view">`) | Views scanner (future) |
| `Asset` | Static asset file (JS/CSS/SCSS) | Asset scanner (future) |
| `AssetBundle` | Odoo asset bundle declaration | Bundle scanner (future) |
| `Controller` | `@http.route` controller method | Controller scanner (future) |
| `Doc` | Documentation file (`.md`, `.rst`) | Doc scanner (future) |

### 1.3 Required fields per node (enforced by DB constraints)

| Field | DB column | Constraint | Notes |
|-------|-----------|-----------|-------|
| `type` | `type text not null` | CHECK not null | One of the kinds above |
| `name` | `name text not null` | CHECK not null | Human-readable identifier |
| `edit_policy` | `edit_policy text not null default 'editable'` | CHECK in (editable, overlay_only, no_touch) | Derived from addon_kind |
| `git_sha` | `git_sha text` | No constraint | Must be populated at write time (see §7) |

### 1.4 Optional fields

`path`, `module`, `addon_kind`, `attrs` (jsonb, default `{}`)

---

## 2. Edge Kinds

### 2.1 Emitted by indexer

| kind | Meaning | Allowed src_kind | Allowed dst_kind | Cardinality |
|------|---------|-----------------|-----------------|-------------|
| `DEFINED_IN` | Node is defined in / belongs to | `File` | `OdooModule` | N:1 |
| `DEFINED_IN` | Node is defined in | `Model` | `File` | N:1 |
| `DEPENDS_ON` | Module declares dependency | `OdooModule` | `OdooModule` | N:M |
| `INHERITS_FROM` | Odoo model `_inherit` | `Model` | `Model` | N:M |

### 2.2 Reserved (defined in schema, not yet emitted)

| kind | Planned src → dst |
|------|------------------|
| `CALLS` | `Controller → Model` |
| `ASSET_IN_BUNDLE` | `Asset → AssetBundle` |
| `REMOVES` | `Model → Model` (unlink override) |
| `OVERLAYS` | `Model → Model` (ipai override of OCA model) |
| `IMPORTS` | `File → File` |

### 2.3 Required fields per edge

| Field | DB column | Notes |
|-------|-----------|-------|
| `src_id` | `uuid not null references kb_nodes(id) on delete cascade` | FK to source node |
| `dst_id` | `uuid not null references kb_nodes(id) on delete cascade` | FK to destination node |
| `type` | `text not null` | Edge kind string |
| `git_sha` | `text` | Must be populated at write time (see §7) |

---

## 3. Uniqueness Rules

### Node uniqueness

```sql
UNIQUE (type, path, name)  -- constraint: kb_nodes_type_path_name_uniq
```

Two nodes are identical if they share the same type, path, and name. The indexer uses
`ON CONFLICT ON CONSTRAINT kb_nodes_type_path_name_uniq DO UPDATE` to upsert.

**Implication**: a `Model` node named `ProjectTask` defined in two different files will
create two distinct nodes (different `path`). This is correct — different files means
different override inheritance chains.

### Edge uniqueness

```sql
UNIQUE (src_id, dst_id, type)  -- constraint: kb_edges_src_dst_type_uniq
```

At most one edge of a given type may exist between any ordered (src, dst) pair.
The indexer uses `ON CONFLICT ... DO NOTHING`.

---

## 4. Deletion and Cascade Semantics

The schema uses `ON DELETE CASCADE` on both FK columns in `kb_edges`:

```sql
src_id uuid not null references public.kb_nodes(id) on delete cascade,
dst_id uuid not null references public.kb_nodes(id) on delete cascade,
```

**Consequence**: deleting a `kb_node` row automatically deletes all edges where it
appears as `src_id` OR `dst_id`. No orphan edges can exist.

**Do not** manually delete individual edge rows to "disconnect" nodes — delete the
node itself to cascade, or let the indexer upsert (idempotent).

---

## 5. Policy Zones

| `addon_kind` | `edit_policy` | What it means |
|-------------|--------------|---------------|
| `ipai` | `editable` | Custom ipai_* modules — all development happens here |
| `generated` | `editable` | Runtime-generated content — safe to regenerate |
| `oca` | `overlay_only` | OCA community modules — `_inherit` only, never patch directly |
| `core` | `no_touch` | Odoo CE core addons — read-only reference |
| `vendor` | `no_touch` | Third-party vendored code — read-only |

These values are enforced by DB check constraints on both `kb_nodes.addon_kind` and
`kb_chunks.addon_kind`:

```sql
CHECK (addon_kind in ('core','oca','ipai','vendor','generated'))
CHECK (edit_policy in ('editable','overlay_only','no_touch'))
```

**Agent query pattern** (only fetch editable nodes):

```sql
SELECT type, name, path, module
FROM kb_nodes
WHERE addon_kind = 'ipai' AND edit_policy = 'editable'
ORDER BY type, name;
```

---

## 6. Path Normalization Rule

> **This is the canonical join key between `kb_chunks.path` and `kb_nodes.path`.**

### Rule

Every `path` value stored in either `kb_chunks` or `kb_nodes` MUST conform to:

| Property | Value |
|----------|-------|
| Base | Repo root (`REPO_ROOT`) |
| Format | Repo-relative, forward-slash separated |
| Leading slash | **None** — paths do NOT start with `/` |
| OS separator | Always `/` (never `\`) |
| Example | `addons/ipai/ipai_finance_ppm/models/project_task_integration.py` |

### How the indexer computes paths

```python
rel_path = str(py_file.relative_to(REPO_ROOT))
# On macOS/Linux this produces: addons/ipai/ipai_finance_ppm/models/...
# On Windows this would produce backslashes — indexer must normalize:
rel_path = rel_path.replace("\\", "/")
```

The current indexer (`build_kb_graph.py`) relies on `pathlib` on POSIX systems and
is correct. If running on Windows, add `.replace("\\", "/")` explicitly.

### Cross-layer join

```sql
-- Find text chunks that belong to editable modules
SELECT c.content, c.span_start, c.span_end,
       n.module, n.addon_kind, n.edit_policy
FROM kb_chunks c
JOIN kb_nodes n ON c.path = n.path
WHERE n.edit_policy = 'editable'
  AND n.type = 'File'
ORDER BY n.module, c.path, c.span_start;
```

### When ingesting text chunks

The knowledge-base text ingestor (future) MUST normalize paths with the same rule
before writing to `kb_chunks.path`. Failure to normalize will break the join.

---

## 7. Provenance Requirements

Every upsert to `kb_nodes` or `kb_edges` MUST populate `git_sha` with the short
commit SHA of the HEAD at run time:

```python
git_sha = subprocess.check_output(
    ["git", "rev-parse", "--short", "HEAD"],
    cwd=REPO_ROOT, text=True
).strip()
```

This enables cache-invalidation queries:

```sql
-- Nodes changed in the last run
SELECT type, name, path FROM kb_nodes
WHERE git_sha = '4ba21eac'
ORDER BY updated_at DESC;
```

---

## 8. Manifest and Contract Version Tracking

After each successful indexer run, a manifest is written to
`reports/graphrag_manifest.json`:

```json
{
  "contract_version": "1.0.0",
  "indexer_version": "1.1.0",
  "git_sha": "<short-sha>",
  "timestamp": "<ISO8601-UTC>",
  "addons_path": "addons/ipai",
  "input_checksum": "<sha256-of-sorted-py-paths>",
  "stats": {
    "nodes_written": 386,
    "edges_written": 337
  }
}
```

The CI gate (`.github/workflows/graphrag-indexer-check.yml`) validates this manifest.

**Bumping the contract version**: when an incompatible schema change is made (new
required field, changed uniqueness constraint, removed node/edge kind), increment
`contract_version` here and in `docs/architecture/INDEX.json` and
`reports/graphrag_manifest.json`.

---

## 9. Indexer Invariants

After any indexer run, these conditions MUST hold:

1. All `DEFINED_IN` edges have `src_id` pointing to a `File` or `Model` node and
   `dst_id` pointing to a `File` or `OdooModule` node.
2. All `DEPENDS_ON` edges connect two `OdooModule` nodes.
3. All `INHERITS_FROM` edges connect two `Model` nodes.
4. No `kb_edges` row exists without a matching `kb_nodes` row for both `src_id`
   and `dst_id` (enforced by FK + cascade).
5. No node has `addon_kind = null` when its path starts with `addons/ipai/`,
   `addons/oca/`, or `addons/odoo/`.
6. Every node has `git_sha IS NOT NULL`.

---

## 10. Re-run Policy

```
Rule (Invariant 9 from REPO_MAP.md):
  Re-run `python scripts/build_kb_graph.py` after any module changes.
```

Automation path:
- Post-merge CI hook (`.github/workflows/graphrag-indexer-check.yml`) validates the
  manifest is fresh relative to the commit.
- The manifest `input_checksum` detects when `.py` files changed but the indexer
  was not re-run.

---

*Last updated: 2026-02-23 | contract_version: 1.0.0 | indexer_version: 1.1.0*
