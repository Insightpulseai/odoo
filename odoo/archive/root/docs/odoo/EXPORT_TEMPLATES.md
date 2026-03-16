# Odoo Export Template System

This document describes the data dictionary-driven template generation system for Odoo imports.

## Overview

The system uses a **data dictionary** stored in Supabase (`odoo_dict` schema) to define:

1. **Field definitions** - Technical metadata for each importable field
2. **Templates** - Predefined column sets for specific use cases
3. **Validation rules** - Required fields, types, relationships

This approach treats the **data dictionary itself as data**, enabling:

- Programmatic template generation
- Import validation
- Documentation generation
- Schema evolution tracking

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Data Dictionary (odoo_dict)                  │
├─────────────────────────────────────────────────────────────────┤
│  fields table          │  templates table      │  import_runs   │
│  - model_name          │  - slug               │  - audit log   │
│  - field_name          │  - field_names[]      │                │
│  - import_column       │  - model_name         │                │
│  - required            │                       │                │
│  - example_value       │                       │                │
└─────────────────────────────────────────────────────────────────┘
            │                       │
            ▼                       ▼
┌───────────────────┐    ┌───────────────────┐
│  Edge Function    │    │  Python Script    │
│  (Supabase)       │    │  (Local)          │
└───────────────────┘    └───────────────────┘
            │                       │
            ▼                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                 Generated Templates (CSV/XLSX/JSON)             │
└─────────────────────────────────────────────────────────────────┘
```

## Quick Start

### Generate Templates Locally (No Supabase)

```bash
# List available models
python scripts/generate_odoo_template.py --list-models

# List predefined templates
python scripts/generate_odoo_template.py --list-templates

# Generate a specific template
python scripts/generate_odoo_template.py --template finance-ppm-tasks --output templates/

# Generate with example row
python scripts/generate_odoo_template.py --template finance-ppm-tasks --include-examples

# Generate all templates
python scripts/generate_odoo_template.py --all --output templates/

# Generate for any model
python scripts/generate_odoo_template.py --model project.task --format xlsx
```

### Generate Templates via Supabase Edge Function

```bash
# Get CSV template for a model
curl "https://<project>.supabase.co/functions/v1/odoo-template-export?model=project.task"

# Get CSV template from predefined template
curl "https://<project>.supabase.co/functions/v1/odoo-template-export?template=finance-ppm-tasks"

# Get JSON field metadata
curl "https://<project>.supabase.co/functions/v1/odoo-template-export?model=project.task&format=json"

# Include example row
curl "https://<project>.supabase.co/functions/v1/odoo-template-export?template=finance-ppm-tasks&include_examples=true"
```

## Available Templates

| Slug | Model | Fields | Description |
|------|-------|--------|-------------|
| `finance-ppm-tasks` | project.task | 13 | Full task import for month-end closing and tax filing |
| `finance-ppm-tasks-minimal` | project.task | 5 | Minimal task import with required fields only |
| `finance-ppm-projects` | project.project | 7 | Project import for finance programs |
| `project-stages` | project.task.type | 4 | Stage definitions for project kanban |
| `project-tags` | project.tags | 3 | Tag definitions for task categorization |
| `hr-employees` | hr.employee | 6 | Employee master data for assignment references |
| `analytic-accounts` | account.analytic.account | 5 | Analytic accounts for project cost tracking |

## Available Models

| Model | Fields | Domain |
|-------|--------|--------|
| `project.project` | 11 | project |
| `project.task` | 15 | finance |
| `project.tags` | 3 | project |
| `project.task.type` | 5 | project |
| `hr.employee` | 8 | hr |
| `account.analytic.account` | 6 | finance |

## Field Metadata

Each field in the dictionary includes:

| Property | Type | Description |
|----------|------|-------------|
| `model_name` | string | Odoo model (e.g., `project.task`) |
| `field_name` | string | Technical field name (e.g., `date_deadline`) |
| `label` | string | Human-friendly label |
| `field_type` | string | Odoo type: `char`, `many2one`, `date`, `float`, `many2many` |
| `required` | boolean | Whether field is required for import |
| `is_key` | boolean | True for External ID fields |
| `relation_model` | string | Target model for relational fields |
| `import_column` | string | Exact header text for CSV import |
| `description` | string | Business meaning (e.g., finance PPM context) |
| `example_value` | string | Sample value for templates |
| `default_value` | string | Default if not provided |
| `sequence` | int | Column order in templates |

## Import Column Headers

The `import_column` field contains the **exact text** that Odoo expects in CSV headers:

| Field | Import Column |
|-------|---------------|
| `x_external_ref` | External ID |
| `name` | Name |
| `project_id` | Project |
| `company_id` | Company |
| `user_ids` | Assigned to |
| `date_deadline` | Planned Date |
| `tag_ids` | Tags |
| `depend_on_ids` | Depends on |

## Database Schema

### odoo_dict.fields

```sql
CREATE TABLE odoo_dict.fields (
    id                bigserial PRIMARY KEY,
    model_name        text NOT NULL,
    field_name        text NOT NULL,
    label             text NOT NULL,
    field_type        text NOT NULL,
    required          boolean NOT NULL DEFAULT false,
    is_key            boolean NOT NULL DEFAULT false,
    relation_model    text,
    import_column     text NOT NULL,
    description       text,
    example_value     text,
    default_value     text,
    domain            text DEFAULT 'general',
    module_required   text,
    sequence          int NOT NULL DEFAULT 100,
    is_active         boolean NOT NULL DEFAULT true,
    created_at        timestamptz NOT NULL DEFAULT now(),
    updated_at        timestamptz NOT NULL DEFAULT now(),
    UNIQUE (model_name, field_name)
);
```

### odoo_dict.templates

```sql
CREATE TABLE odoo_dict.templates (
    id                bigserial PRIMARY KEY,
    slug              text UNIQUE NOT NULL,
    name              text NOT NULL,
    description       text,
    model_name        text NOT NULL,
    field_names       text[] NOT NULL,
    domain            text DEFAULT 'general',
    is_active         boolean NOT NULL DEFAULT true,
    created_at        timestamptz NOT NULL DEFAULT now(),
    updated_at        timestamptz NOT NULL DEFAULT now()
);
```

## Helper Functions

### Get Import Headers for a Model

```sql
SELECT * FROM odoo_dict.get_import_headers('project.task');
-- Returns: External ID, Name of the Tasks?, Description, Project, ...
```

### Get Headers for a Template

```sql
SELECT * FROM odoo_dict.get_template_headers('finance-ppm-tasks');
-- Returns: import_column, field_name, required
```

### Validate Import Headers

```sql
SELECT * FROM odoo_dict.validate_import_headers(
    'project.task',
    ARRAY['External ID', 'Name of the Tasks?', 'Project', 'Unknown Column']
);
-- Returns status per header: valid, unknown, or missing
```

## Adding New Fields

### Via SQL

```sql
INSERT INTO odoo_dict.fields (
    model_name, field_name, label, field_type, required, is_key,
    relation_model, import_column, description, example_value,
    domain, sequence
) VALUES (
    'project.task',
    'x_custom_field',
    'Custom Field',
    'char',
    false,
    false,
    NULL,
    'Custom Field',
    'Description of what this field does',
    'Example Value',
    'finance',
    200
);
```

### Via Python Script

Edit `scripts/generate_odoo_template.py` and add to the `FIELDS` list:

```python
DictField(
    model_name="project.task",
    field_name="x_custom_field",
    label="Custom Field",
    field_type="char",
    required=False,
    is_key=False,
    relation_model=None,
    import_column="Custom Field",
    description="Description of what this field does",
    example_value="Example Value",
    default_value=None,
    domain="finance",
    sequence=200,
),
```

## Adding New Templates

### Via SQL

```sql
INSERT INTO odoo_dict.templates (slug, name, description, model_name, field_names, domain)
VALUES (
    'custom-task-template',
    'Custom Task Template',
    'A custom subset of task fields',
    'project.task',
    ARRAY['x_external_ref', 'name', 'project_id', 'date_deadline'],
    'custom'
);
```

### Via Python Script

Edit `scripts/generate_odoo_template.py` and add to the `TEMPLATES` list:

```python
Template(
    slug="custom-task-template",
    name="Custom Task Template",
    description="A custom subset of task fields",
    model_name="project.task",
    field_names=["x_external_ref", "name", "project_id", "date_deadline"],
    domain="custom",
),
```

## Deployment

### Apply Supabase Migration

```bash
supabase db push
```

### Seed the Dictionary

```bash
psql "$POSTGRES_URL" -f supabase/seeds/003_odoo_dict_seed.sql
```

### Deploy Edge Function

```bash
supabase functions deploy odoo-template-export
```

## Related Files

| File | Purpose |
|------|---------|
| `supabase/migrations/20260121100001_odoo_data_dictionary.sql` | Schema migration |
| `supabase/seeds/003_odoo_dict_seed.sql` | Seed data |
| `supabase/functions/odoo-template-export/index.ts` | Edge function |
| `scripts/generate_odoo_template.py` | Local generator (no Supabase) |

## Best Practices

1. **Always use External ID** - Include `x_external_ref` for idempotent imports
2. **Required fields** - Ensure all required fields are present in templates
3. **Relational fields** - Use names or External IDs, not database IDs
4. **Many2many fields** - Use comma-separated values (e.g., `Tag1,Tag2`)
5. **Dependencies** - Reference by External ID (e.g., `FIN_CLOSE_DAY1_CUTOFF`)

## See Also

- [SEEDING_STRATEGY.md](../../db/seeds/SEEDING_STRATEGY.md) - Overall seeding strategy
- [data/import_templates/README.md](../../data/import_templates/README.md) - Existing import templates
- [data/finance_seed/README.md](../../data/finance_seed/README.md) - Finance seed data
