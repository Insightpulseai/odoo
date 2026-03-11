-- update_phase_tags.sql
-- Bulk update tasks with phase tags after CSV import
--
-- Usage:
--   ssh root@erp.insightpulseai.net << 'EOF'
--   docker exec -i $(docker ps -q -f name=db) psql -U odoo -d odoo < update_phase_tags.sql
--   EOF
--
-- Or directly in PostgreSQL:
--   \i update_phase_tags.sql

BEGIN;

-- ============================================================================
-- STEP 1: Create Phase Tags (if they don't exist)
-- ============================================================================

-- Phase I: Initial & Compliance (color 1 = Red)
INSERT INTO project_tags (name, color, create_uid, write_uid, create_date, write_date)
SELECT 'Phase I: Initial & Compliance', 1, 1, 1, NOW(), NOW()
WHERE NOT EXISTS (
    SELECT 1 FROM project_tags WHERE name = 'Phase I: Initial & Compliance'
);

-- Phase II: Accruals & Amortization (color 2 = Orange)
INSERT INTO project_tags (name, color, create_uid, write_uid, create_date, write_date)
SELECT 'Phase II: Accruals & Amortization', 2, 1, 1, NOW(), NOW()
WHERE NOT EXISTS (
    SELECT 1 FROM project_tags WHERE name = 'Phase II: Accruals & Amortization'
);

-- Phase III: WIP (color 3 = Yellow)
INSERT INTO project_tags (name, color, create_uid, write_uid, create_date, write_date)
SELECT 'Phase III: WIP', 3, 1, 1, NOW(), NOW()
WHERE NOT EXISTS (
    SELECT 1 FROM project_tags WHERE name = 'Phase III: WIP'
);

-- Phase IV: Final Adjustments (color 4 = Light Blue)
INSERT INTO project_tags (name, color, create_uid, write_uid, create_date, write_date)
SELECT 'Phase IV: Final Adjustments', 4, 1, 1, NOW(), NOW()
WHERE NOT EXISTS (
    SELECT 1 FROM project_tags WHERE name = 'Phase IV: Final Adjustments'
);

-- ============================================================================
-- STEP 2: Create Category Tags (optional, for manual assignment)
-- ============================================================================

INSERT INTO project_tags (name, color, create_uid, write_uid, create_date, write_date)
SELECT unnest(ARRAY[
    'Payroll & Personnel',
    'Tax & Provisions',
    'VAT & Taxes',
    'CA Liquidations',
    'Accruals & Expenses',
    'Corporate Accruals',
    'Client Billings',
    'WIP/OOP Management',
    'Prior Period Review',
    'Reclassifications'
]), unnest(ARRAY[5, 6, 7, 8, 9, 10, 1, 2, 3, 4]), 1, 1, NOW(), NOW()
WHERE NOT EXISTS (
    SELECT 1 FROM project_tags WHERE name IN (
        'Payroll & Personnel',
        'Tax & Provisions',
        'VAT & Taxes',
        'CA Liquidations',
        'Accruals & Expenses',
        'Corporate Accruals',
        'Client Billings',
        'WIP/OOP Management',
        'Prior Period Review',
        'Reclassifications'
    )
);

-- ============================================================================
-- STEP 3: Assign Phase I Tag to tasks starting with [I.
-- ============================================================================

INSERT INTO project_tags_project_task_rel (project_task_id, project_tags_id)
SELECT t.id, pt.id
FROM project_task t
CROSS JOIN project_tags pt
WHERE pt.name = 'Phase I: Initial & Compliance'
  AND t.name LIKE '[I.%'
  AND NOT EXISTS (
      SELECT 1 FROM project_tags_project_task_rel r
      WHERE r.project_task_id = t.id
        AND r.project_tags_id = pt.id
  );

-- ============================================================================
-- STEP 4: Assign Phase II Tag to tasks starting with [II.
-- ============================================================================

INSERT INTO project_tags_project_task_rel (project_task_id, project_tags_id)
SELECT t.id, pt.id
FROM project_task t
CROSS JOIN project_tags pt
WHERE pt.name = 'Phase II: Accruals & Amortization'
  AND t.name LIKE '[II.%'
  AND NOT EXISTS (
      SELECT 1 FROM project_tags_project_task_rel r
      WHERE r.project_task_id = t.id
        AND r.project_tags_id = pt.id
  );

-- ============================================================================
-- STEP 5: Assign Phase III Tag to tasks starting with [III.
-- ============================================================================

INSERT INTO project_tags_project_task_rel (project_task_id, project_tags_id)
SELECT t.id, pt.id
FROM project_task t
CROSS JOIN project_tags pt
WHERE pt.name = 'Phase III: WIP'
  AND t.name LIKE '[III.%'
  AND NOT EXISTS (
      SELECT 1 FROM project_tags_project_task_rel r
      WHERE r.project_task_id = t.id
        AND r.project_tags_id = pt.id
  );

-- ============================================================================
-- STEP 6: Assign Phase IV Tag to tasks starting with [IV.
-- ============================================================================

INSERT INTO project_tags_project_task_rel (project_task_id, project_tags_id)
SELECT t.id, pt.id
FROM project_task t
CROSS JOIN project_tags pt
WHERE pt.name = 'Phase IV: Final Adjustments'
  AND t.name LIKE '[IV.%'
  AND NOT EXISTS (
      SELECT 1 FROM project_tags_project_task_rel r
      WHERE r.project_task_id = t.id
        AND r.project_tags_id = pt.id
  );

-- ============================================================================
-- STEP 7: Verification - Count tasks per phase tag
-- ============================================================================

SELECT
    pt.name AS tag_name,
    COUNT(r.project_task_id) AS task_count
FROM project_tags pt
LEFT JOIN project_tags_project_task_rel r ON r.project_tags_id = pt.id
WHERE pt.name LIKE 'Phase %'
GROUP BY pt.id, pt.name
ORDER BY pt.name;

-- ============================================================================
-- STEP 8: Show all tags created
-- ============================================================================

SELECT id, name, color
FROM project_tags
WHERE name LIKE 'Phase %'
   OR name IN (
       'Payroll & Personnel',
       'Tax & Provisions',
       'VAT & Taxes',
       'CA Liquidations',
       'Accruals & Expenses',
       'Corporate Accruals',
       'Client Billings',
       'WIP/OOP Management',
       'Prior Period Review',
       'Reclassifications'
   )
ORDER BY name;

COMMIT;

-- Success message
SELECT 'Phase tags assigned successfully!' AS status;
