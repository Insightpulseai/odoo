-- =============================================================================
-- SKILL CERTIFICATION SEEDS
-- =============================================================================
-- Seeds for skill definitions, criteria, and example holders
-- =============================================================================

-- -----------------------------------------------------------------------------
-- Skill Definitions
-- -----------------------------------------------------------------------------

-- Frontend Design System Skills
INSERT INTO skills.skill_definitions (slug, title, description, category, level, spec_url, design_system_token)
VALUES
    (
        'nextjs-copilot-ui-pro',
        'Next.js Copilot UI – Professional',
        'Implements pixel-perfect Copilot/Fluent-style design system across all responsive breakpoints.',
        'frontend',
        'professional',
        'https://github.com/insightpulseai/ipai-design-tokens',
        'ipai/copilot-theme/v1'
    ),
    (
        'nextjs-copilot-ui-foundation',
        'Next.js Copilot UI – Foundation',
        'Basic understanding of Copilot design system with component usage.',
        'frontend',
        'foundation',
        'https://github.com/insightpulseai/ipai-design-tokens',
        'ipai/copilot-theme/v1'
    ),
    (
        'react-component-design',
        'React Component Design',
        'Creates reusable, accessible React components following design system patterns.',
        'frontend',
        'associate',
        NULL,
        'ipai/copilot-theme/v1'
    )
ON CONFLICT (slug) DO NOTHING;

-- Backend & Database Skills
INSERT INTO skills.skill_definitions (slug, title, description, category, level, spec_url, design_system_token)
VALUES
    (
        'supabase-dba-pro',
        'Supabase DBA – Professional',
        'Advanced Supabase database administration including RLS, migrations, and performance.',
        'backend',
        'professional',
        'https://supabase.com/docs',
        NULL
    ),
    (
        'supabase-rls-expert',
        'Supabase RLS – Expert',
        'Expert-level row-level security design and implementation for multi-tenant systems.',
        'backend',
        'expert',
        'https://supabase.com/docs/guides/auth/row-level-security',
        NULL
    ),
    (
        'postgresql-fundamentals',
        'PostgreSQL Fundamentals',
        'Core PostgreSQL skills including queries, indexes, and basic optimization.',
        'backend',
        'foundation',
        'https://www.postgresql.org/docs/',
        NULL
    ),
    (
        'odoo-oca-admin',
        'Odoo OCA Admin',
        'Odoo administration with OCA module ecosystem expertise.',
        'backend',
        'professional',
        'https://odoo-community.org/',
        NULL
    )
ON CONFLICT (slug) DO NOTHING;

-- AI & Agent Orchestration Skills
INSERT INTO skills.skill_definitions (slug, title, description, category, level, spec_url, design_system_token)
VALUES
    (
        'ipai-enterprise-copilot',
        'IPAI Enterprise Copilot',
        'Cross-system AI copilot for Odoo, Supabase, Vercel, DigitalOcean, and GitHub, with certified skills for finance, ops, and pixel-perfect design.',
        'ai-orchestration',
        'expert',
        'https://github.com/insightpulseai/spec/ipai-enterprise-copilot/prd.md',
        'ipai/copilot-theme/v1'
    ),
    (
        'mcp-tool-integration',
        'MCP Tool Integration',
        'Integrates Model Context Protocol tools for AI agent workflows.',
        'ai-orchestration',
        'associate',
        'https://modelcontextprotocol.io/',
        NULL
    ),
    (
        'rag-pipeline-design',
        'RAG Pipeline Design',
        'Designs and implements retrieval-augmented generation pipelines for AI systems.',
        'ai-orchestration',
        'professional',
        NULL,
        NULL
    )
ON CONFLICT (slug) DO NOTHING;

-- DevOps & Infrastructure Skills
INSERT INTO skills.skill_definitions (slug, title, description, category, level, spec_url, design_system_token)
VALUES
    (
        'docker-containerization',
        'Docker Containerization',
        'Docker container building, orchestration, and deployment.',
        'devops',
        'associate',
        'https://docs.docker.com/',
        NULL
    ),
    (
        'github-actions-ci',
        'GitHub Actions CI/CD',
        'Continuous integration and deployment with GitHub Actions.',
        'devops',
        'associate',
        'https://docs.github.com/en/actions',
        NULL
    ),
    (
        'vercel-deployment',
        'Vercel Deployment',
        'Next.js deployment and edge functions on Vercel platform.',
        'devops',
        'foundation',
        'https://vercel.com/docs',
        NULL
    )
ON CONFLICT (slug) DO NOTHING;

-- -----------------------------------------------------------------------------
-- Skill Criteria for nextjs-copilot-ui-pro
-- -----------------------------------------------------------------------------

WITH skill AS (
    SELECT id FROM skills.skill_definitions WHERE slug = 'nextjs-copilot-ui-pro'
)
INSERT INTO skills.skill_criteria (skill_id, code, description, weight, required)
SELECT
    skill.id,
    x.code,
    x.description,
    x.weight,
    x.required
FROM skill,
    (VALUES
        ('TOKEN_CONSISTENCY', 'All colors/spacing/typography from ipai-design-tokens; no hard-coded hex/rem values.', 2.0, true),
        ('RESPONSIVE_PARITY', 'Layout matches Figma on mobile/tablet/desktop within 4px tolerance.', 2.0, true),
        ('ACCESSIBILITY_A11Y', 'Meets WCAG AA (contrast, focus, semantics).', 1.5, true),
        ('THEME_SWITCH', 'Supports light/dark mode without visual regressions.', 1.5, true),
        ('COMPONENT_REUSE', 'Uses shared UI component library; no one-off clones.', 1.0, false)
    ) AS x(code, description, weight, required)
ON CONFLICT (skill_id, code) DO NOTHING;

-- -----------------------------------------------------------------------------
-- Skill Criteria for ipai-enterprise-copilot
-- -----------------------------------------------------------------------------

WITH skill AS (
    SELECT id FROM skills.skill_definitions WHERE slug = 'ipai-enterprise-copilot'
)
INSERT INTO skills.skill_criteria (skill_id, code, description, weight, required)
SELECT
    skill.id,
    x.code,
    x.description,
    x.weight,
    x.required
FROM skill,
    (VALUES
        ('RAG_OFFICIAL_DOCS', 'Answers must be RAG-grounded on official docs/PRDs (Supabase, Odoo, Mailgun, etc.) with source citations.', 2.0, true),
        ('ERP_ACTION_SAFETY', 'All Odoo/ERP actions go through audited, reversible commands with dry-run support.', 2.0, true),
        ('DESIGN_SYSTEM_PARITY', 'All UI actions respect ipai-design-tokens and pixel-perfect theme rules.', 1.5, true),
        ('MULTI_AGENT_ORCH', 'Uses Devstral/Dash/etc. via MCP with clear task boundaries and logs.', 1.5, true),
        ('TELEMETRY_FEEDBACK', 'Uses telemetry.runs + knowledge.qa_events to improve and close doc gaps.', 1.0, false)
    ) AS x(code, description, weight, required)
ON CONFLICT (skill_id, code) DO NOTHING;

-- -----------------------------------------------------------------------------
-- Skill Criteria for supabase-rls-expert
-- -----------------------------------------------------------------------------

WITH skill AS (
    SELECT id FROM skills.skill_definitions WHERE slug = 'supabase-rls-expert'
)
INSERT INTO skills.skill_criteria (skill_id, code, description, weight, required)
SELECT
    skill.id,
    x.code,
    x.description,
    x.weight,
    x.required
FROM skill,
    (VALUES
        ('RLS_ALL_TABLES', 'RLS enabled on all user-data tables with no bypassed routes.', 2.0, true),
        ('TENANT_ISOLATION', 'Multi-tenant queries always filter by tenant_id; no cross-tenant leaks.', 2.0, true),
        ('POLICY_AUDIT', 'All policies documented with rationale and tested.', 1.5, true),
        ('PERFORMANCE_OPT', 'Policies use indexed columns; no full table scans in common paths.', 1.0, false),
        ('MIGRATION_SAFETY', 'RLS changes tested in staging before production.', 1.0, false)
    ) AS x(code, description, weight, required)
ON CONFLICT (skill_id, code) DO NOTHING;

-- -----------------------------------------------------------------------------
-- Skill Criteria for mcp-tool-integration
-- -----------------------------------------------------------------------------

WITH skill AS (
    SELECT id FROM skills.skill_definitions WHERE slug = 'mcp-tool-integration'
)
INSERT INTO skills.skill_criteria (skill_id, code, description, weight, required)
SELECT
    skill.id,
    x.code,
    x.description,
    x.weight,
    x.required
FROM skill,
    (VALUES
        ('TOOL_REGISTRATION', 'MCP tools properly registered with schemas and descriptions.', 1.5, true),
        ('ERROR_HANDLING', 'Tools return structured errors with actionable messages.', 1.5, true),
        ('AUTH_SCOPES', 'Tools enforce appropriate authentication and authorization.', 1.5, true),
        ('LOGGING_AUDIT', 'All tool invocations logged for audit and debugging.', 1.0, false)
    ) AS x(code, description, weight, required)
ON CONFLICT (skill_id, code) DO NOTHING;

-- -----------------------------------------------------------------------------
-- Skill Holders (Agents)
-- -----------------------------------------------------------------------------

INSERT INTO skills.skill_holders (holder_type, holder_slug, display_name, meta)
VALUES
    (
        'agent',
        'Pulser.IPAIEnterpriseCopilot',
        'IPAI Enterprise Copilot',
        '{"stack":["odoo","supabase","vercel","digitalocean","github"],"mcp":true}'::jsonb
    ),
    (
        'agent',
        'Pulser.Devstral',
        'Devstral – Development Intelligence',
        '{"stack":["typescript","python","rust"],"specialty":"code-generation"}'::jsonb
    ),
    (
        'agent',
        'Pulser.Dash',
        'Dash – Creative Intelligence Dashboard Engineer',
        '{"stack":["nextjs","react","tailwind"],"specialty":"ui-design"}'::jsonb
    ),
    (
        'agent',
        'Pulser.Tide',
        'Tide – Data Pipeline Intelligence',
        '{"stack":["postgresql","supabase","dbt"],"specialty":"data-engineering"}'::jsonb
    ),
    (
        'agent',
        'Pulser.Sage',
        'Sage – Documentation Intelligence',
        '{"stack":["markdown","mdx","notion"],"specialty":"documentation"}'::jsonb
    ),
    (
        'agent',
        'Pulser.Bolt',
        'Bolt – DevOps Intelligence',
        '{"stack":["docker","github-actions","vercel","digitalocean"],"specialty":"deployment"}'::jsonb
    )
ON CONFLICT (holder_type, holder_slug) DO UPDATE
    SET display_name = EXCLUDED.display_name,
        meta = EXCLUDED.meta;

-- -----------------------------------------------------------------------------
-- Knowledge Sources
-- -----------------------------------------------------------------------------

INSERT INTO knowledge.sources (slug, kind, base_url, meta)
VALUES
    ('supabase-docs', 'docs', 'https://supabase.com/docs', '{"priority": 1}'::jsonb),
    ('odoo-oca-18', 'docs', 'https://odoo-community.org/', '{"version": "18.0"}'::jsonb),
    ('mailgun-docs', 'docs', 'https://documentation.mailgun.com/', '{}'::jsonb),
    ('vercel-docs', 'docs', 'https://vercel.com/docs', '{}'::jsonb),
    ('digitalocean-docs', 'docs', 'https://docs.digitalocean.com/', '{}'::jsonb),
    ('ipai-specs', 'spec', NULL, '{"internal": true}'::jsonb),
    ('ipai-prds', 'prd', NULL, '{"internal": true}'::jsonb),
    ('ipai-internal', 'internal', NULL, '{"claude_md": true}'::jsonb)
ON CONFLICT (slug) DO UPDATE
    SET kind = EXCLUDED.kind,
        base_url = EXCLUDED.base_url,
        meta = EXCLUDED.meta,
        updated_at = NOW();

-- -----------------------------------------------------------------------------
-- Verification Queries
-- -----------------------------------------------------------------------------

-- Verify skill definitions
SELECT slug, title, category, level
FROM skills.skill_definitions
ORDER BY category, level DESC;

-- Verify criteria counts
SELECT
    sd.slug,
    COUNT(sc.id) AS criteria_count,
    SUM(CASE WHEN sc.required THEN 1 ELSE 0 END) AS required_count
FROM skills.skill_definitions sd
LEFT JOIN skills.skill_criteria sc ON sc.skill_id = sd.id
GROUP BY sd.slug
ORDER BY sd.slug;

-- Verify holders
SELECT holder_type, holder_slug, display_name
FROM skills.skill_holders
ORDER BY holder_type, holder_slug;

-- Verify knowledge sources
SELECT slug, kind, base_url
FROM knowledge.sources
ORDER BY slug;
