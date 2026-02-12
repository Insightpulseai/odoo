-- BIR Forms Registry Migration
-- Created: 2026-02-12
-- Portfolio Initiative: PORT-2026-011
-- Purpose: Canonical registry for BIR forms scraped from bir.gov.ph/bir-forms

-- Create registry schema if not exists
CREATE SCHEMA IF NOT EXISTS registry;
COMMENT ON SCHEMA registry IS 'Canonical registries for external data sources (BIR forms, OCA modules, etc.)';

-- Create bir_forms table
CREATE TABLE IF NOT EXISTS registry.bir_forms (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    form_code TEXT NOT NULL UNIQUE,
    title TEXT NOT NULL,
    description TEXT,
    category TEXT,
    file_url TEXT,
    last_updated TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Add table comment
COMMENT ON TABLE registry.bir_forms IS 'BIR forms registry scraped from bir.gov.ph/bir-forms - canonical source for form metadata';

-- Add column comments
COMMENT ON COLUMN registry.bir_forms.form_code IS 'BIR form code (e.g., 1601-C, 2550Q, 1702-RT)';
COMMENT ON COLUMN registry.bir_forms.title IS 'Official form title from BIR website';
COMMENT ON COLUMN registry.bir_forms.description IS 'Form description/purpose';
COMMENT ON COLUMN registry.bir_forms.category IS 'Form category (e.g., Withholding Tax, Income Tax, VAT)';
COMMENT ON COLUMN registry.bir_forms.file_url IS 'Download URL for PDF/Excel form';
COMMENT ON COLUMN registry.bir_forms.last_updated IS 'Last scrape timestamp';
COMMENT ON COLUMN registry.bir_forms.metadata IS 'Additional metadata (version, revision date, instructions URL, etc.)';

-- Create indexes
CREATE INDEX idx_bir_forms_code ON registry.bir_forms(form_code);
CREATE INDEX idx_bir_forms_category ON registry.bir_forms(category);
CREATE INDEX idx_bir_forms_last_updated ON registry.bir_forms(last_updated DESC);
CREATE INDEX idx_bir_forms_metadata_gin ON registry.bir_forms USING GIN(metadata);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION registry.update_bir_forms_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger
DROP TRIGGER IF EXISTS bir_forms_updated_at ON registry.bir_forms;
CREATE TRIGGER bir_forms_updated_at
    BEFORE UPDATE ON registry.bir_forms
    FOR EACH ROW
    EXECUTE FUNCTION registry.update_bir_forms_updated_at();

-- RLS Policies
ALTER TABLE registry.bir_forms ENABLE ROW LEVEL SECURITY;

-- Public read access (forms data is public information)
DROP POLICY IF EXISTS "Public read access for BIR forms" ON registry.bir_forms;
CREATE POLICY "Public read access for BIR forms"
    ON registry.bir_forms
    FOR SELECT
    TO PUBLIC
    USING (true);

-- Service role write access (scraper automation)
DROP POLICY IF EXISTS "Service role write access for BIR forms" ON registry.bir_forms;
CREATE POLICY "Service role write access for BIR forms"
    ON registry.bir_forms
    FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);

-- Grant permissions
GRANT SELECT ON registry.bir_forms TO anon, authenticated;
GRANT ALL ON registry.bir_forms TO service_role;

-- Seed initial data from existing bir_forms.xml (if migration succeeds, scraper will update)
-- This ensures backward compatibility while transitioning to scraped data
INSERT INTO registry.bir_forms (form_code, title, category, metadata)
VALUES
    ('1601-C', 'Monthly Remittance Return of Income Taxes Withheld on Compensation', 'Withholding Tax', '{"source": "seed", "manual": true}'::jsonb),
    ('2550Q', 'Quarterly Value-Added Tax Return', 'VAT', '{"source": "seed", "manual": true}'::jsonb),
    ('1702-RT', 'Annual Income Tax Return (Regular)', 'Income Tax', '{"source": "seed", "manual": true}'::jsonb),
    ('1601-EQ', 'Quarterly Remittance Return of Creditable Income Taxes Withheld (Expanded)', 'Withholding Tax', '{"source": "seed", "manual": true}'::jsonb),
    ('2551Q', 'Quarterly Percentage Tax Return', 'Percentage Tax', '{"source": "seed", "manual": true}'::jsonb)
ON CONFLICT (form_code) DO NOTHING;

-- Verification query
-- SELECT COUNT(*) FROM registry.bir_forms;
-- Expected: 5 seed rows initially, 30+ after scraper runs
