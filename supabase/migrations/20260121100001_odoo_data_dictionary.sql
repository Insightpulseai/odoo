-- =============================================================================
-- Migration: Odoo Data Dictionary
-- Purpose: Schema-as-records for Odoo import template generation
-- Pattern: Data dictionary drives CSV/XLSX template headers + validation
-- Integration: Complements odoo_seed schema (20260121_odoo_seed_schema.sql)
-- =============================================================================

BEGIN;

-- -----------------------------------------------------------------------------
-- Schema: odoo_dict
-- Stores field definitions that describe how to import data into Odoo models
-- -----------------------------------------------------------------------------

CREATE SCHEMA IF NOT EXISTS odoo_dict;

COMMENT ON SCHEMA odoo_dict IS
'Canonical data dictionary for Odoo field definitions. Drives template generation and import validation.';

-- -----------------------------------------------------------------------------
-- 1. Fields Table (the data dictionary core)
-- Each row describes one field in an Odoo model for import purposes
-- -----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS odoo_dict.fields (
    id                bigserial PRIMARY KEY,

    -- Model identification
    model_name        text NOT NULL,              -- e.g., 'project.task', 'project.project'
    field_name        text NOT NULL,              -- technical field name, e.g., 'name', 'x_external_ref'

    -- Display
    label             text NOT NULL,              -- human-friendly label

    -- Type information
    field_type        text NOT NULL,              -- e.g., 'char', 'many2one', 'date', 'float', 'many2many'
    relation_model    text,                       -- target model for many2one/many2many

    -- Import behavior
    import_column     text NOT NULL,              -- exact header text for CSV/XLSX import
    required          boolean NOT NULL DEFAULT false,
    is_key            boolean NOT NULL DEFAULT false,  -- true for External ID fields

    -- Documentation
    description       text,                       -- business meaning (e.g., finance PPM context)
    example_value     text,                       -- sample value for templates
    default_value     text,                       -- default if not provided in import

    -- Categorization
    domain            text DEFAULT 'general',     -- e.g., 'finance', 'hr', 'project'
    module_required   text,                       -- Odoo module that must be installed (null = core)

    -- Template ordering
    sequence          int NOT NULL DEFAULT 100,   -- column order in generated templates

    -- Status
    is_active         boolean NOT NULL DEFAULT true,

    -- Audit
    created_at        timestamptz NOT NULL DEFAULT now(),
    updated_at        timestamptz NOT NULL DEFAULT now()
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_odoo_dict_fields_model_field
    ON odoo_dict.fields (model_name, field_name);

CREATE INDEX IF NOT EXISTS idx_odoo_dict_fields_model
    ON odoo_dict.fields (model_name);

CREATE INDEX IF NOT EXISTS idx_odoo_dict_fields_domain
    ON odoo_dict.fields (domain);

CREATE INDEX IF NOT EXISTS idx_odoo_dict_fields_active
    ON odoo_dict.fields (is_active) WHERE is_active = true;

COMMENT ON TABLE odoo_dict.fields IS
'Data dictionary for Odoo import fields. Each row defines one field for template generation and validation.';

-- -----------------------------------------------------------------------------
-- 2. Templates Table (predefined column sets for specific use cases)
-- -----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS odoo_dict.templates (
    id                bigserial PRIMARY KEY,

    -- Template identification
    slug              text UNIQUE NOT NULL,       -- e.g., 'finance-ppm-tasks', 'hr-employees'
    name              text NOT NULL,              -- human-friendly name
    description       text,

    -- Target model
    model_name        text NOT NULL,              -- primary model this template imports

    -- Field selection (ordered)
    field_names       text[] NOT NULL,            -- array of field_name values to include

    -- Metadata
    domain            text DEFAULT 'general',
    is_active         boolean NOT NULL DEFAULT true,

    -- Audit
    created_at        timestamptz NOT NULL DEFAULT now(),
    updated_at        timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_odoo_dict_templates_model
    ON odoo_dict.templates (model_name);

CREATE INDEX IF NOT EXISTS idx_odoo_dict_templates_domain
    ON odoo_dict.templates (domain);

COMMENT ON TABLE odoo_dict.templates IS
'Predefined template configurations for specific import use cases.';

-- -----------------------------------------------------------------------------
-- 3. Import Runs Log (audit trail for template-based imports)
-- -----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS odoo_dict.import_runs (
    id                uuid PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Template reference
    template_slug     text REFERENCES odoo_dict.templates(slug),
    model_name        text NOT NULL,

    -- Run metadata
    started_at        timestamptz NOT NULL DEFAULT now(),
    completed_at      timestamptz,

    -- Results
    status            text NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'running', 'success', 'partial', 'failed')),
    rows_total        int DEFAULT 0,
    rows_imported     int DEFAULT 0,
    rows_skipped      int DEFAULT 0,
    rows_failed       int DEFAULT 0,

    -- Errors
    error_log         jsonb DEFAULT '[]'::jsonb,

    -- Source
    source_file       text,                       -- original filename
    triggered_by      text                        -- 'manual', 'workflow', 'api'
);

CREATE INDEX IF NOT EXISTS idx_odoo_dict_import_runs_status
    ON odoo_dict.import_runs (status);

CREATE INDEX IF NOT EXISTS idx_odoo_dict_import_runs_template
    ON odoo_dict.import_runs (template_slug);

COMMENT ON TABLE odoo_dict.import_runs IS
'Audit log of template-based imports for traceability.';

-- -----------------------------------------------------------------------------
-- 4. Updated_at Trigger
-- -----------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION odoo_dict.set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_fields_updated
    BEFORE UPDATE ON odoo_dict.fields
    FOR EACH ROW EXECUTE FUNCTION odoo_dict.set_updated_at();

CREATE TRIGGER trg_templates_updated
    BEFORE UPDATE ON odoo_dict.templates
    FOR EACH ROW EXECUTE FUNCTION odoo_dict.set_updated_at();

-- -----------------------------------------------------------------------------
-- 5. Helper Functions for Template Generation
-- -----------------------------------------------------------------------------

-- Get ordered import columns for a model
CREATE OR REPLACE FUNCTION odoo_dict.get_import_headers(p_model_name text)
RETURNS TABLE (import_column text) AS $$
    SELECT f.import_column
    FROM odoo_dict.fields f
    WHERE f.model_name = p_model_name
      AND f.is_active = true
    ORDER BY f.sequence, f.id;
$$ LANGUAGE sql STABLE;

COMMENT ON FUNCTION odoo_dict.get_import_headers(text) IS
'Returns ordered import column headers for a model.';

-- Get ordered import columns for a template
CREATE OR REPLACE FUNCTION odoo_dict.get_template_headers(p_template_slug text)
RETURNS TABLE (import_column text, field_name text, required boolean) AS $$
    SELECT f.import_column, f.field_name, f.required
    FROM odoo_dict.templates t
    CROSS JOIN LATERAL unnest(t.field_names) WITH ORDINALITY AS fn(name, ord)
    JOIN odoo_dict.fields f ON f.model_name = t.model_name AND f.field_name = fn.name
    WHERE t.slug = p_template_slug
      AND f.is_active = true
    ORDER BY fn.ord;
$$ LANGUAGE sql STABLE;

COMMENT ON FUNCTION odoo_dict.get_template_headers(text) IS
'Returns ordered import column headers for a predefined template.';

-- Validate import data against dictionary
CREATE OR REPLACE FUNCTION odoo_dict.validate_import_headers(
    p_model_name text,
    p_headers text[]
)
RETURNS TABLE (
    header text,
    status text,
    field_name text,
    message text
) AS $$
DECLARE
    h text;
    f_record RECORD;
BEGIN
    -- Check each provided header
    FOREACH h IN ARRAY p_headers LOOP
        SELECT f.field_name, f.required INTO f_record
        FROM odoo_dict.fields f
        WHERE f.model_name = p_model_name
          AND f.import_column = h
          AND f.is_active = true;

        IF f_record.field_name IS NOT NULL THEN
            RETURN QUERY SELECT h, 'valid'::text, f_record.field_name, NULL::text;
        ELSE
            RETURN QUERY SELECT h, 'unknown'::text, NULL::text, 'Header not in data dictionary'::text;
        END IF;
    END LOOP;

    -- Check for missing required fields
    FOR f_record IN
        SELECT f.import_column, f.field_name
        FROM odoo_dict.fields f
        WHERE f.model_name = p_model_name
          AND f.required = true
          AND f.is_active = true
          AND f.import_column != ALL(p_headers)
    LOOP
        RETURN QUERY SELECT f_record.import_column, 'missing'::text, f_record.field_name, 'Required field not in headers'::text;
    END LOOP;
END;
$$ LANGUAGE plpgsql STABLE;

COMMENT ON FUNCTION odoo_dict.validate_import_headers(text, text[]) IS
'Validates import CSV headers against the data dictionary. Returns status per header.';

-- -----------------------------------------------------------------------------
-- 6. RLS Policies
-- -----------------------------------------------------------------------------

ALTER TABLE odoo_dict.fields ENABLE ROW LEVEL SECURITY;
ALTER TABLE odoo_dict.templates ENABLE ROW LEVEL SECURITY;
ALTER TABLE odoo_dict.import_runs ENABLE ROW LEVEL SECURITY;

-- Service role full access
CREATE POLICY "Service role full access to fields"
    ON odoo_dict.fields FOR ALL
    USING (auth.role() = 'service_role');

CREATE POLICY "Service role full access to templates"
    ON odoo_dict.templates FOR ALL
    USING (auth.role() = 'service_role');

CREATE POLICY "Service role full access to import_runs"
    ON odoo_dict.import_runs FOR ALL
    USING (auth.role() = 'service_role');

-- Authenticated users can read (for template generation)
CREATE POLICY "Authenticated users can read fields"
    ON odoo_dict.fields FOR SELECT
    USING (auth.role() = 'authenticated');

CREATE POLICY "Authenticated users can read templates"
    ON odoo_dict.templates FOR SELECT
    USING (auth.role() = 'authenticated');

COMMIT;
