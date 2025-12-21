-- Form Builder (Studio) Schema
-- Replaces: Odoo Studio (Enterprise)

-- Forms (form definitions)
CREATE TABLE IF NOT EXISTS studio_forms (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    slug TEXT UNIQUE NOT NULL,
    description TEXT,
    model_name TEXT, -- Odoo model this form maps to (optional)
    status TEXT DEFAULT 'draft' CHECK (status IN ('draft', 'published', 'archived')),
    version INT DEFAULT 1,
    layout JSONB DEFAULT '{"type": "vertical", "columns": 1}',
    settings JSONB DEFAULT '{}',
    created_by UUID REFERENCES auth.users(id),
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- Fields (form field definitions)
CREATE TABLE IF NOT EXISTS studio_fields (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    form_id UUID REFERENCES studio_forms(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    label TEXT NOT NULL,
    field_type TEXT NOT NULL CHECK (field_type IN (
        'text', 'textarea', 'number', 'decimal', 'date', 'datetime',
        'select', 'multiselect', 'checkbox', 'radio', 'file', 'image',
        'relation', 'computed', 'section', 'separator'
    )),
    position INT DEFAULT 0,
    column INT DEFAULT 1,
    required BOOLEAN DEFAULT false,
    readonly BOOLEAN DEFAULT false,
    default_value JSONB,
    options JSONB DEFAULT '{}', -- For select/multiselect: {choices: [...]}
    validation JSONB DEFAULT '{}', -- {min, max, pattern, custom_rule}
    relation_config JSONB, -- {model, field, domain}
    compute_formula TEXT, -- For computed fields
    visibility_rule JSONB, -- Conditional visibility
    help_text TEXT,
    placeholder TEXT,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now(),
    UNIQUE(form_id, name)
);

-- Views (generated Odoo XML views)
CREATE TABLE IF NOT EXISTS studio_views (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    form_id UUID REFERENCES studio_forms(id) ON DELETE CASCADE,
    view_type TEXT NOT NULL CHECK (view_type IN ('form', 'tree', 'kanban', 'calendar', 'graph')),
    xml_content TEXT NOT NULL,
    is_active BOOLEAN DEFAULT true,
    generated_at TIMESTAMPTZ DEFAULT now()
);

-- Submissions (form data when not linked to Odoo)
CREATE TABLE IF NOT EXISTS studio_submissions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    form_id UUID REFERENCES studio_forms(id) ON DELETE CASCADE,
    data JSONB NOT NULL,
    submitted_by UUID REFERENCES auth.users(id),
    submitted_at TIMESTAMPTZ DEFAULT now(),
    status TEXT DEFAULT 'submitted' CHECK (status IN ('submitted', 'processing', 'completed', 'rejected'))
);

-- Audit log
CREATE TABLE IF NOT EXISTS studio_audit (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    entity_type TEXT NOT NULL CHECK (entity_type IN ('form', 'field', 'view', 'submission')),
    entity_id UUID NOT NULL,
    action TEXT NOT NULL,
    changed_by UUID REFERENCES auth.users(id),
    change_summary JSONB,
    timestamp TIMESTAMPTZ DEFAULT now()
);

-- Indexes
CREATE INDEX idx_studio_fields_form ON studio_fields(form_id);
CREATE INDEX idx_studio_fields_position ON studio_fields(form_id, position);
CREATE INDEX idx_studio_views_form ON studio_views(form_id);
CREATE INDEX idx_studio_submissions_form ON studio_submissions(form_id);
CREATE INDEX idx_studio_submissions_status ON studio_submissions(status);

-- Row Level Security
ALTER TABLE studio_forms ENABLE ROW LEVEL SECURITY;
ALTER TABLE studio_fields ENABLE ROW LEVEL SECURITY;
ALTER TABLE studio_submissions ENABLE ROW LEVEL SECURITY;
