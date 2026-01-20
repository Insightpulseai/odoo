# Odoo Data Model Artifacts

This folder contains canonical, generated representations of the Odoo CE data model as defined by this repository's addons.

---

## Quick View: IPAI AI Platform ERD

```mermaid
erDiagram
    %% Odoo Core
    res_company {
        integer id PK
        varchar name
    }
    res_users {
        integer id PK
        varchar name
        varchar login UK
        integer company_id FK
    }
    project_project {
        integer id PK
        varchar name
        integer company_id FK
        integer user_id FK
    }
    project_task {
        integer id PK
        varchar name
        text description
        integer project_id FK
    }

    %% AI Provider & Thread
    ipai_ai_provider {
        integer id PK
        varchar name
        varchar provider_type "kapa|openai|anthropic"
        boolean active
        integer company_id FK
    }
    ipai_ai_thread {
        integer id PK
        varchar name
        integer provider_id FK
        integer user_id FK
        varchar state "active|closed"
    }
    ipai_ai_message {
        integer id PK
        integer thread_id FK
        varchar role "user|assistant|system"
        text content
        integer tokens_used
    }
    ipai_ai_citation {
        integer id PK
        integer message_id FK
        varchar title
        varchar url
        float score
    }
    ipai_ai_prompt {
        integer id PK
        varchar name
        varchar code UK
        text template
        integer company_id FK
    }

    %% Workspace
    ipai_workspace {
        integer id PK
        varchar name
        varchar visibility "private|internal|public"
        integer company_id FK
        integer project_id FK
    }
    ipai_workspace_member {
        integer id PK
        integer workspace_id FK
        integer user_id FK
        varchar role "member|admin|owner"
    }

    %% Relationships
    res_users ||--o{ res_company : "belongs_to"
    project_project ||--o{ res_company : "belongs_to"
    project_task ||--o{ project_project : "belongs_to"
    ipai_ai_provider ||--o{ res_company : "belongs_to"
    ipai_ai_thread ||--o{ ipai_ai_provider : "uses"
    ipai_ai_thread ||--o{ res_users : "owned_by"
    ipai_ai_message ||--o{ ipai_ai_thread : "belongs_to"
    ipai_ai_citation ||--o{ ipai_ai_message : "belongs_to"
    ipai_ai_prompt ||--o{ res_company : "scoped_to"
    ipai_workspace ||--o{ res_company : "belongs_to"
    ipai_workspace ||--o| project_project : "contains"
    ipai_workspace_member ||--o{ ipai_workspace : "belongs_to"
    ipai_workspace_member ||--o{ res_users : "is_user"
```

---

## Quick View: Shadow Schema Architecture

```mermaid
erDiagram
    %% Odoo PostgreSQL (Source)
    res_partner {
        bigint id PK
        varchar name
        varchar email
        timestamp write_date
    }
    account_move {
        bigint id PK
        varchar name
        varchar state
        numeric amount_total
        timestamp write_date
    }
    sale_order {
        bigint id PK
        varchar name
        varchar state
        numeric amount_total
        timestamp write_date
    }

    %% Supabase Shadow (Target)
    odoo_shadow_res_partner {
        bigint id PK
        varchar name
        varchar email
        timestamp _odoo_write_date
        timestamp _synced_at
        varchar _sync_hash
    }
    odoo_shadow_account_move {
        bigint id PK
        varchar name
        varchar state
        numeric amount_total
        timestamp _odoo_write_date
        timestamp _synced_at
    }
    odoo_shadow_sale_order {
        bigint id PK
        varchar name
        varchar state
        numeric amount_total
        timestamp _odoo_write_date
        timestamp _synced_at
    }

    %% Metadata Tables
    odoo_shadow_meta {
        bigint id PK
        varchar table_name UK
        varchar odoo_model
        bigint row_count
        timestamp last_sync_at
    }
    odoo_shadow_watermark {
        bigint id PK
        varchar table_name UK
        timestamp last_write_date
        bigint last_id
        bigint rows_synced
    }
    odoo_shadow_sync_log {
        uuid sync_run_id PK
        varchar table_name
        varchar status
        bigint rows_inserted
        bigint duration_ms
    }

    %% Sync Relationships
    res_partner ||--|| odoo_shadow_res_partner : "mirrors"
    account_move ||--|| odoo_shadow_account_move : "mirrors"
    sale_order ||--|| odoo_shadow_sale_order : "mirrors"
    odoo_shadow_meta ||--o{ odoo_shadow_watermark : "tracks"
    odoo_shadow_meta ||--o{ odoo_shadow_sync_log : "logs"
```

---

## Quick View: Finance PPM Core

```mermaid
erDiagram
    %% Close Orchestration
    a1_close_cycle {
        integer id PK
        varchar name
        varchar period_type "monthly|quarterly|yearly"
        date period_start
        date period_end
        varchar state "draft|in_progress|completed"
        integer company_id FK
    }
    a1_tasklist {
        integer id PK
        varchar name
        integer close_cycle_id FK
        date period_start
        date period_end
        varchar state
        float progress
    }
    a1_task {
        integer id PK
        varchar name
        integer tasklist_id FK
        integer owner_id FK
        integer reviewer_id FK
        varchar state "draft|prep|review|approved"
        date prep_deadline
        date review_deadline
    }
    a1_check {
        integer id PK
        varchar name
        varchar check_type
        varchar severity "info|warning|blocker"
        integer company_id FK
    }
    a1_check_result {
        integer id PK
        integer check_id FK
        integer task_id FK
        varchar result "pass|fail|skip"
        text evidence
    }

    %% Relationships
    a1_close_cycle ||--o{ a1_tasklist : "contains"
    a1_tasklist ||--o{ a1_task : "contains"
    a1_task ||--o{ a1_check_result : "has"
    a1_check ||--o{ a1_check_result : "defines"
```

---

## Quick View: OCA Queue Job

```mermaid
erDiagram
    queue_job {
        integer id PK
        varchar uuid UK
        varchar name
        text func_string
        varchar channel "root|high|medium|low"
        varchar state "pending|enqueued|started|done|failed"
        integer priority
        timestamp date_created
        timestamp date_started
        timestamp date_done
        integer max_retries
        integer retry
        text result
        text exc_info
    }
    queue_job_channel {
        integer id PK
        varchar name UK
        integer parent_id FK
        integer capacity
    }

    queue_job_channel ||--o{ queue_job_channel : "parent"
    queue_job }o--|| queue_job_channel : "channel"
```

---

## Contents

### Schema Definitions
| File | Format | Description |
|------|--------|-------------|
| `ODOO_CANONICAL_SCHEMA.dbml` | DBML | Canonical schema for dbdiagram.io (132KB, 357 models) |
| `ODOO_MODEL_INDEX.json` | JSON | Machine-readable index of models, fields, relations |
| `ODOO_ORM_MAP.md` | Markdown | ORM map linking Odoo models, tables, and fields |
| `ODOO_MODULE_DELTAS.md` | Markdown | Per-module deltas highlighting new and extended tables |
| `ODOO_SHADOW_SCHEMA.sql` | SQL | Auto-generated shadow schema DDL (288 tables) |

### Diagram Formats
| File | Format | Viewer |
|------|--------|--------|
| `ODOO_ERD.mmd` | Mermaid | GitHub, [Mermaid Live](https://mermaid.live) |
| `ODOO_ERD.puml` | PlantUML | [PlantUML Online](https://www.plantuml.com/plantuml) |
| `IPAI_AI_PLATFORM_ERD.mmd` | Mermaid | GitHub (rendered above) |
| `EXTENDED_PLATFORM_ERD.mmd` | Mermaid | GitHub, Mermaid Live |

### Extended Schemas
| File | Description |
|------|-------------|
| `EXTENDED_PLATFORM_SCHEMA.dbml` | Extended platform DBML (OCA modules) |
| `IPAI_AI_PLATFORM_SCHEMA.dbml` | AI platform DBML (IPAI modules) |
| `IPAI_FINANCE_OKR_SCHEMA.dbml` | Finance OKR schema |
| `MULTI_TENANT_PROVIDER_SCHEMA.dbml` | Multi-tenant provider schema |
| `SCOUT_CES_ANALYTICS_SCHEMA.dbml` | Scout/CES analytics schema |
| `insightpulse_canonical.dbml` | InsightPulse canonical schema |

### Documentation
| File | Purpose |
|------|---------|
| `SHADOW_SCHEMA_FEASIBILITY.md` | Technical feasibility analysis for shadow mirroring |
| `SUPERSET_ERD_INTEGRATION.md` | How to embed ERDs in Superset dashboards |

---

## View DBML Online

Import any `.dbml` file into [dbdiagram.io](https://dbdiagram.io):

1. Go to https://dbdiagram.io/d
2. Click **Import** → **From DBML**
3. Paste contents of any `.dbml` file

**Direct links** (copy content from):
- [ODOO_CANONICAL_SCHEMA.dbml](./ODOO_CANONICAL_SCHEMA.dbml) - Full Odoo schema
- [IPAI_AI_PLATFORM_SCHEMA.dbml](./IPAI_AI_PLATFORM_SCHEMA.dbml) - AI platform
- [EXTENDED_PLATFORM_SCHEMA.dbml](./EXTENDED_PLATFORM_SCHEMA.dbml) - OCA extensions

---

## Regenerate Locally

### All formats (DBML, Mermaid, PlantUML)
```bash
python scripts/generate_odoo_dbml.py
```

### Shadow schema DDL
```bash
python scripts/generate_shadow_ddl.py
```

### Graphviz formats (DOT, SVG, PNG)
```bash
# Requires: apt-get install graphviz
python scripts/generate_erd_graphviz.py --format all
```

### IPAI modules only
```bash
python scripts/generate_erd_graphviz.py --filter ipai_ --format all
```

### From live database (requires DB connection)
```bash
psql -f scripts/erd_dot.sql -t -A > erd.dot
dot -Tsvg erd.dot -o erd.svg
```

---

## CI/CD Automation

ERDs are automatically regenerated when:
- Model files change in `addons/ipai/**/models/**`
- Migration files change in `db/migrations/**`
- Generator scripts are updated

### Workflows
| Workflow | Purpose |
|----------|---------|
| `erd-graphviz.yml` | Generates ERD from codebase (no DB required) |
| `erd-schemaspy.yml` | Generates ERD from live database (requires DB secrets) |

---

## Color Legend

| Color | Meaning |
|-------|---------|
| Light Green | IPAI custom modules (`ipai_*`) |
| Light Yellow | Odoo core models (`res_*`, `ir_*`) |
| Light Gray | Relation tables (`*_rel`) |
| Light Blue | Other tables |

---

## API Access

### Supabase Edge Function
```bash
# Get SVG ERD
curl https://spdtwktxdalcfigzeqrz.supabase.co/functions/v1/serve-erd?format=svg

# IPAI modules only
curl https://spdtwktxdalcfigzeqrz.supabase.co/functions/v1/serve-erd?format=svg&filter=ipai
```

### GitHub Raw URLs
```markdown
![ERD](https://raw.githubusercontent.com/jgtolentino/odoo-ce/main/docs/data-model/ODOO_ERD.svg)
```

---

## Schema Statistics

| Metric | Value |
|--------|-------|
| Total Odoo Models | 357 |
| Stored Fields | 2,847 |
| IPAI Custom Models | 80+ |
| Shadow Tables | 288 |
| DBML Size | 132KB |

---

*Last updated: 2026-01-20*
