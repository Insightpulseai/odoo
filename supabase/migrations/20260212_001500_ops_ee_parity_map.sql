-- ============================================================================
-- ops.ee_parity_map - Odoo EE→CE+OCA Parity Matrix
-- ============================================================================
-- Purpose: Evidence-based EE→CE+OCA module mapping with scraper output
-- Spec: Task #2 - Parity matrix generator
-- Created: 2026-02-12
-- ============================================================================

-- ============================================================================
-- ops.ee_parity_map - EE feature mapping to CE+OCA equivalents
-- ============================================================================
create table ops.ee_parity_map (
  id uuid primary key default gen_random_uuid(),

  -- EE Feature
  ee_app_name text not null,
  ee_app_slug text not null,
  ee_category text not null,
  ee_description text,
  ee_url text,

  -- CE+OCA Equivalence
  parity_level text not null check (parity_level in ('full', 'partial', 'alternative', 'missing')),
  ce_modules text[], -- Array of built-in CE modules that provide partial coverage
  oca_modules text[], -- Array of OCA modules (format: "repo/module_name")
  ipai_modules text[], -- Array of custom ipai_* modules

  -- Evidence
  evidence_urls text[], -- Array of URLs proving equivalence (OCA repos, apps.odoo.com)
  confidence_score numeric(3,2) check (confidence_score >= 0.0 and confidence_score <= 1.0),
  notes text,

  -- Metadata
  scraped_at timestamptz not null default now(),
  verified_at timestamptz,
  verified_by uuid references auth.users(id) on delete set null,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),

  constraint unique_ee_app unique(ee_app_slug)
);

create index ops_ee_parity_map_category_idx on ops.ee_parity_map(ee_category);
create index ops_ee_parity_map_parity_level_idx on ops.ee_parity_map(parity_level);
create index ops_ee_parity_map_confidence_idx on ops.ee_parity_map(confidence_score desc);
create index ops_ee_parity_map_scraped_at_idx on ops.ee_parity_map(scraped_at desc);

comment on table ops.ee_parity_map is 'EE→CE+OCA parity matrix with evidence URLs';
comment on column ops.ee_parity_map.parity_level is 'full: 100% coverage | partial: 50-99% | alternative: different approach | missing: no equivalent';
comment on column ops.ee_parity_map.confidence_score is 'Evidence confidence: 0.0-1.0 based on verification depth';

-- ============================================================================
-- ops.ee_parity_stats - Aggregated parity statistics view
-- ============================================================================
create or replace view ops.ee_parity_stats as
select
  ee_category,
  count(*) as total_features,
  count(*) filter (where parity_level = 'full') as full_parity,
  count(*) filter (where parity_level = 'partial') as partial_parity,
  count(*) filter (where parity_level = 'alternative') as alternative,
  count(*) filter (where parity_level = 'missing') as missing,
  round(avg(confidence_score) * 100, 1) as avg_confidence,
  round(
    (count(*) filter (where parity_level = 'full') * 1.0 +
     count(*) filter (where parity_level = 'partial') * 0.7 +
     count(*) filter (where parity_level = 'alternative') * 0.5) / count(*) * 100,
    1
  ) as parity_score
from ops.ee_parity_map
group by ee_category
order by parity_score desc;

comment on view ops.ee_parity_stats is 'Category-level parity statistics for odooops-console dashboard';

-- ============================================================================
-- ops.ee_parity_gaps - Missing features ordered by priority
-- ============================================================================
create or replace view ops.ee_parity_gaps as
select
  ee_category,
  ee_app_name,
  ee_app_slug,
  ee_description,
  ee_url,
  parity_level,
  confidence_score,
  notes,
  scraped_at,
  case ee_category
    when 'Accounting' then 1
    when 'Sales' then 2
    when 'HR' then 3
    when 'Project' then 4
    when 'Marketing' then 5
    when 'Website' then 6
    else 10
  end as priority_order
from ops.ee_parity_map
where parity_level in ('partial', 'missing')
order by priority_order, confidence_score desc;

comment on view ops.ee_parity_gaps is 'Missing/partial features prioritized for implementation';

-- ============================================================================
-- Trigger for updated_at
-- ============================================================================
create trigger ops_ee_parity_map_updated_at
  before update on ops.ee_parity_map
  for each row
  execute function ops.set_updated_at();

-- ============================================================================
-- Grants
-- ============================================================================
grant select on ops.ee_parity_map to authenticated;
grant select on ops.ee_parity_stats to authenticated;
grant select on ops.ee_parity_gaps to authenticated;

-- ============================================================================
-- Example usage
-- ============================================================================

-- Insert from scraper output:
-- INSERT INTO ops.ee_parity_map (
--   ee_app_name, ee_app_slug, ee_category, ee_description, ee_url,
--   parity_level, ce_modules, oca_modules, ipai_modules,
--   evidence_urls, confidence_score, notes
-- ) VALUES (
--   'Documents', 'documents', 'Productivity', 'Document Management System with OCR',
--   'https://apps.odoo.com/apps/modules/19.0/documents/',
--   'full',
--   ARRAY[]::text[],
--   ARRAY['document-management/dms', 'document-management/dms_field'],
--   ARRAY[]::text[],
--   ARRAY['https://github.com/OCA/document-management'],
--   0.95,
--   'OCA DMS provides full feature parity with EE Documents'
-- );

-- Query parity statistics:
-- SELECT * FROM ops.ee_parity_stats;

-- Find gaps:
-- SELECT * FROM ops.ee_parity_gaps LIMIT 10;
