-- Migration: Add Supabase project reference to ops.projects
-- Purpose: Link OdooOps projects to Supabase projects for Platform Kit integration
-- Date: 2026-02-15

-- Add supabase_project_ref column
ALTER TABLE ops.projects
ADD COLUMN supabase_project_ref TEXT;

-- Add unique constraint (one Supabase project per OdooOps project)
ALTER TABLE ops.projects
ADD CONSTRAINT supabase_project_ref_unique UNIQUE (supabase_project_ref);

-- Create index for lookups
CREATE INDEX idx_projects_supabase_ref ON ops.projects(supabase_project_ref);

-- Add column comment
COMMENT ON COLUMN ops.projects.supabase_project_ref IS 'Supabase project reference ID for Platform Kit integration';
