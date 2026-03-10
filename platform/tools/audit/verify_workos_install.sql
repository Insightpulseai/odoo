-- =============================================================================
-- VERIFY WORKOS MODULE INSTALLATION
-- =============================================================================
-- Run this query against the Odoo database to verify module installation.
--
-- Usage:
--   psql -U odoo -d odoo -f verify_workos_install.sql
--
-- Expected: All modules should show state = 'installed'
-- =============================================================================

-- Module installation status
SELECT
    name,
    state,
    latest_version,
    CASE
        WHEN state = 'installed' THEN '✓ OK'
        WHEN state = 'to install' THEN '⏳ Pending'
        WHEN state = 'to upgrade' THEN '⏳ Upgrading'
        WHEN state = 'uninstalled' THEN '✗ Not installed'
        ELSE '? Unknown'
    END as status
FROM ir_module_module
WHERE name IN (
    'ipai_workos_affine',
    'ipai_workos_core',
    'ipai_workos_blocks',
    'ipai_workos_db',
    'ipai_workos_views',
    'ipai_workos_templates',
    'ipai_workos_collab',
    'ipai_workos_search',
    'ipai_workos_canvas',
    'ipai_platform_permissions',
    'ipai_platform_audit'
)
ORDER BY name;

-- Count summary
SELECT
    state,
    COUNT(*) as count
FROM ir_module_module
WHERE name LIKE 'ipai_workos%' OR name LIKE 'ipai_platform%'
GROUP BY state;

-- Models created by WorkOS modules
SELECT
    m.model,
    m.name,
    m.state
FROM ir_model m
WHERE m.model LIKE 'ipai.workos.%' OR m.model LIKE 'ipai.audit.%'
ORDER BY m.model;
