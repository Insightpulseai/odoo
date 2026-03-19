# Lakehouse Contract System

> **Last Updated**: 2026-03-08
> **Source Code**: `src/lakehouse/contracts.py`
> **Contract Directory**: `contracts/delta/`
> **CI Validator**: `scripts/lakehouse/validate_contracts.py`

---

## Overview

The contract system enforces schema consistency across the lakehouse. Every Delta table must have a corresponding YAML contract file that defines its columns, types, partitioning, and retention policy. The contract is the single source of truth for table structure -- Trino DDL, pipeline code, and documentation all derive from it.

---

## Contract YAML Format

Each contract is a YAML file in `contracts/delta/` with the following structure:

```yaml
# contracts/delta/<layer>_<table_name>.yaml

table: "<layer>.<table_name>"          # Fully qualified table name (e.g., "bronze.raw_pages")
location: "s3a://lakehouse/<layer>/<table_name>/"  # MinIO storage path
format: delta                          # Storage format (always "delta")
partition_by:                          # Partition columns (list)
  - source
  - crawled_date
primary_key:                           # Primary/merge key columns (list, optional)
  - tenant_id
  - canonical_url
merge_key: content_hash               # Column used for dedup/upsert (optional)
retention_days: 365                   # Data retention in days

columns:                              # Column definitions (dict)
  tenant_id:
    type: uuid
    nullable: false
    description: "Tenant identifier for multi-tenant isolation"
  source:
    type: varchar
    nullable: false
    description: "Data source identifier"
  canonical_url:
    type: varchar
    nullable: true
    description: "Canonical URL of the source page"
  # ... additional columns
```

### Field Reference

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `table` | string | Yes | -- | Fully qualified table name (`<schema>.<table>`) |
| `location` | string | Yes | -- | S3/MinIO storage path for Delta files |
| `format` | string | No | `delta` | Storage format |
| `partition_by` | list[string] | No | `[]` | Columns to partition by |
| `primary_key` | list[string] | No | `[]` | Primary key columns |
| `merge_key` | string | No | `null` | Column for upsert deduplication |
| `retention_days` | integer | No | `365` | Retention period in days |
| `columns` | dict | Yes | -- | Column definitions (see below) |

### Column Specification

Each column entry is a key-value pair where the key is the column name:

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `type` | string | No | `varchar` | Data type (see type mapping) |
| `nullable` | boolean | No | `true` | Whether NULLs are allowed |
| `description` | string | No | `null` | Human-readable column description |

### Supported Types

| Contract Type | Trino Type | Description |
|---------------|------------|-------------|
| `uuid` | `uuid` | UUID v4 identifier |
| `varchar` | `varchar` | Variable-length string |
| `integer` | `integer` | 32-bit integer |
| `double` | `double` | 64-bit floating point |
| `boolean` | `boolean` | True/false |
| `timestamp` | `timestamp` | Date and time |
| `date` | `date` | Date only |
| `array_double` | `array(double)` | Array of doubles (for vectors) |

---

## Existing Contracts

The lakehouse defines four contracts corresponding to the medallion layers:

### bronze.raw_pages

Raw crawled web pages, unmodified from the crawler output.

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| `tenant_id` | uuid | No | Tenant identifier |
| `source` | varchar | No | Source system (e.g., "confluence", "github") |
| `canonical_url` | varchar | Yes | Canonical URL of the page |
| `resolved_url` | varchar | Yes | Final resolved URL after redirects |
| `http_status` | integer | Yes | HTTP response status code |
| `content_hash` | varchar | Yes | SHA-256 hash of raw content |
| `content_type` | varchar | Yes | MIME type of the response |
| `raw_object_path` | varchar | Yes | Path to raw content in MinIO |
| `raw_text` | varchar | Yes | Extracted text content |
| `headers` | varchar | Yes | Response headers (JSON string) |
| `crawled_at` | timestamp | Yes | Crawl timestamp |
| `crawled_date` | date | Yes | Crawl date (partition column) |

Partitioned by: `source`, `crawled_date`

### silver.normalized_docs

Cleaned and normalized documents with extracted metadata.

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| `tenant_id` | uuid | No | Tenant identifier |
| `source` | varchar | No | Source system |
| `canonical_url` | varchar | Yes | Canonical URL |
| `title` | varchar | Yes | Document title |
| `content_hash` | varchar | Yes | Hash for deduplication |
| `content_md` | varchar | Yes | Content in Markdown format |
| `content_text` | varchar | Yes | Plain text content |
| `language` | varchar | Yes | Detected language code |
| `product` | varchar | Yes | Associated product name |
| `version` | varchar | Yes | Document version |
| `version_at` | timestamp | Yes | Version timestamp |
| `metadata` | varchar | Yes | Additional metadata (JSON string) |
| `normalized_at` | timestamp | Yes | Normalization timestamp |
| `normalized_date` | date | Yes | Normalization date (partition column) |

Partitioned by: `source`, `normalized_date`

### gold.chunks

Semantic document chunks for RAG retrieval.

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| `tenant_id` | uuid | No | Tenant identifier |
| `source` | varchar | No | Source system |
| `document_id` | uuid | Yes | Parent document identifier |
| `document_version_id` | uuid | Yes | Document version identifier |
| `chunk_id` | uuid | Yes | Unique chunk identifier |
| `ord` | integer | Yes | Chunk ordinal position |
| `heading` | varchar | Yes | Section heading |
| `content` | varchar | Yes | Chunk text content |
| `tokens` | integer | Yes | Token count |
| `char_start` | integer | Yes | Character start offset |
| `char_end` | integer | Yes | Character end offset |
| `metadata` | varchar | Yes | Additional metadata (JSON string) |
| `created_at` | timestamp | Yes | Creation timestamp |
| `chunk_date` | date | Yes | Chunk date (partition column) |

Partitioned by: `source`, `chunk_date`

### gold.embeddings

Vector embeddings for similarity search.

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| `tenant_id` | uuid | No | Tenant identifier |
| `embedding_id` | uuid | Yes | Unique embedding identifier |
| `chunk_id` | uuid | Yes | Associated chunk identifier |
| `model` | varchar | Yes | Embedding model name |
| `model_version` | varchar | Yes | Model version string |
| `dims` | integer | Yes | Embedding dimensions |
| `v` | array_double | Yes | Embedding vector |
| `norm` | double | Yes | Vector L2 norm |
| `created_at` | timestamp | Yes | Creation timestamp |
| `embed_date` | date | Yes | Embedding date (partition column) |

Partitioned by: `model`, `embed_date`

---

## How the Contract System Works

### Loading Contracts

`src/lakehouse/contracts.py` provides the `load_contracts()` function:

```python
from src.lakehouse import load_contracts

# Load all contracts from the default directory
contracts = load_contracts("contracts/delta")

# contracts is a dict: {"bronze.raw_pages": DeltaContract, ...}
for table_name, contract in contracts.items():
    print(f"{table_name}: {len(contract.columns)} columns")
```

The function:
1. Scans `contracts/delta/` for `*.yaml` files
2. Parses each file into a `DeltaContract` dataclass
3. Returns a dict mapping table names to contracts

### The DeltaContract Dataclass

```python
@dataclass(frozen=True)
class DeltaContract:
    table: str                          # e.g., "bronze.raw_pages"
    location: str                       # e.g., "s3a://lakehouse/bronze/raw_pages/"
    format: str = "delta"
    partition_by: tuple[str, ...] = ()
    primary_key: tuple[str, ...] = ()
    columns: tuple[ColumnSpec, ...] = ()
    merge_key: Optional[str] = None
    retention_days: int = 365
```

Key properties:
- `schema_name`: Extracts the schema portion (e.g., `"bronze"` from `"bronze.raw_pages"`)
- `table_name`: Extracts the table portion (e.g., `"raw_pages"` from `"bronze.raw_pages"`)
- `get_column(name)`: Look up a `ColumnSpec` by name

### Validating Contracts

The `validate()` method returns a list of error strings (empty if valid):

```python
errors = contract.validate()
if errors:
    for err in errors:
        print(f"ERROR: {err}")
```

Validation checks:
- `table` is not empty
- `location` is not empty
- At least one column is defined
- Every `partition_by` column exists in the column list
- Every `primary_key` column exists in the column list

### Generating Trino DDL

`generate_trino_ddl()` produces a `CREATE TABLE IF NOT EXISTS` statement:

```python
from src.lakehouse.contracts import load_contracts, generate_trino_ddl

contracts = load_contracts()
for name, contract in contracts.items():
    ddl = generate_trino_ddl(contract, catalog="delta")
    print(ddl)
```

Output example:

```sql
CREATE TABLE IF NOT EXISTS delta.bronze.raw_pages (
  tenant_id uuid,
  source varchar,
  canonical_url varchar,
  ...
  crawled_date date
)
WITH (
  location = 's3a://lakehouse/bronze/raw_pages/',
  partitioned_by = ARRAY['source', 'crawled_date']
);
```

The type mapping converts contract types to Trino SQL types (e.g., `array_double` becomes `array(double)`).

---

## Adding a New Contract

To add a new Delta table to the lakehouse:

**Step 1**: Create the contract YAML file.

```bash
# Create the contract file
touch contracts/delta/<layer>_<table_name>.yaml
```

**Step 2**: Define the schema. Use an existing contract as a template. Every contract must include:
- `table` with the `<layer>.<table_name>` format
- `location` pointing to the MinIO path
- `columns` with at least `tenant_id` (type `uuid`, nullable `false`)
- `partition_by` with at least one date column

**Step 3**: Validate the contract.

```bash
python scripts/lakehouse/validate_contracts.py
```

**Step 4**: Generate the Trino DDL (optional, for manual table creation).

```python
from src.lakehouse.contracts import load_contracts, generate_trino_ddl

contracts = load_contracts()
contract = contracts["<layer>.<table_name>"]
print(generate_trino_ddl(contract))
```

Or use the existing hand-written DDL as a reference: `scripts/lakehouse/create_delta_tables_trino.sql`.

**Step 5**: Apply the DDL in Trino.

```bash
docker exec -it lakehouse-trino trino < scripts/lakehouse/create_delta_tables_trino.sql
```

Or execute the generated DDL directly:

```bash
docker exec -it lakehouse-trino trino --execute "CREATE TABLE IF NOT EXISTS delta.<layer>.<table> ..."
```

**Step 6**: Update `scripts/lakehouse/create_delta_tables_trino.sql` to include the new table DDL for reproducibility.

---

## CI Validation

`scripts/lakehouse/validate_contracts.py` is designed to run in CI pipelines:

```bash
python scripts/lakehouse/validate_contracts.py
```

**Exit code 0**: All contracts are valid.
**Exit code 1**: Validation errors were found.

The validator:
1. Loads all contracts from `contracts/delta/`
2. Runs `validate()` on each contract
3. Reports errors and warnings per contract
4. Prints a summary with total contract count, error count, and warning count

Warnings (do not cause failure):
- No `primary_key` defined (acceptable for append-only tables)
- Short retention period (< 30 days)
- Column names that are SQL reserved words

---

## Coverage Audit

`scripts/lakehouse/coverage_audit.py` checks that data exists at each layer for configured sources:

```bash
# Text report
python scripts/lakehouse/coverage_audit.py

# JSON report
python scripts/lakehouse/coverage_audit.py --json

# Specific source only
python scripts/lakehouse/coverage_audit.py --source confluence

# Skip Trino queries (manifest-only check)
python scripts/lakehouse/coverage_audit.py --no-trino
```

The audit loads source manifests from `config/sources/*.yaml` and queries Trino for row counts at each layer. It reports coverage percentages and flags incomplete sources.
