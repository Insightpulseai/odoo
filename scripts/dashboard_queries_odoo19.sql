-- =============================================================================
-- Finance PPM Dashboard SQL Views for Apache Superset
-- Odoo 19 CE PostgreSQL 16+
-- =============================================================================
-- Usage:
--   PGPASSWORD="$SUPERSET_DB_PASS" psql -h superset.insightpulseai.com \
--     -U superset -d superset < scripts/dashboard_queries_odoo19.sql
--
-- Creates 6 materialized views for Superset datasets.
-- =============================================================================

-- ---------------------------------------------------------------------------
-- View 1: Closing Task Summary
-- Aggregated view of all closing/BIR tasks with status
-- ---------------------------------------------------------------------------
CREATE OR REPLACE VIEW v_closing_task_summary AS
SELECT
    pt.id                           AS task_id,
    pt.name                         AS task_name,
    ptt.name                        AS stage_name,
    pp.name                         AS project_name,
    COALESCE(rp.name, 'Unassigned') AS assignee_name,
    COALESCE(ru.login, '')          AS assignee_email,
    pt.date_deadline                AS deadline,
    pt.planned_hours                AS planned_hours,
    pt.sequence                     AS task_sequence,
    pt.priority                     AS priority,
    pt.create_date                  AS created_at,
    pt.write_date                   AS updated_at,
    CASE
        WHEN ptt.name = 'Done'       THEN 'Completed'
        WHEN ptt.name = 'Cancelled'  THEN 'Cancelled'
        WHEN pt.date_deadline < CURRENT_DATE AND ptt.name NOT IN ('Done', 'Cancelled')
            THEN 'Overdue'
        ELSE 'In Progress'
    END                             AS status,
    CASE
        WHEN pt.name LIKE '%BIR%' OR pt.name LIKE '%1601%' OR pt.name LIKE '%0619%'
            OR pt.name LIKE '%2550%' OR pt.name LIKE '%1702%' OR pt.name LIKE '%1601-EQ%'
            THEN 'BIR Tax Filing'
        ELSE 'Month-End Close'
    END                             AS task_type
FROM
    project_task pt
    JOIN project_project pp ON pt.project_id = pp.id
    LEFT JOIN project_task_type ptt ON pt.stage_id = ptt.id
    LEFT JOIN project_task_user_rel ptu ON pt.id = ptu.task_id
    LEFT JOIN res_users ru ON ptu.user_id = ru.id
    LEFT JOIN res_partner rp ON ru.partner_id = rp.id
WHERE
    pp.name LIKE '%Finance PPM%'
ORDER BY
    pt.sequence;

-- ---------------------------------------------------------------------------
-- View 2: Stage Funnel
-- Task counts per stage for funnel/bar visualization
-- ---------------------------------------------------------------------------
CREATE OR REPLACE VIEW v_stage_funnel AS
SELECT
    ptt.name                        AS stage_name,
    ptt.sequence                    AS stage_sequence,
    COUNT(pt.id)                    AS task_count,
    SUM(pt.planned_hours)           AS total_planned_hours,
    ROUND(
        COUNT(pt.id) * 100.0 /
        NULLIF((SELECT COUNT(*) FROM project_task WHERE project_id = pp.id), 0),
        1
    )                               AS pct_of_total
FROM
    project_task pt
    JOIN project_project pp ON pt.project_id = pp.id
    JOIN project_task_type ptt ON pt.stage_id = ptt.id
WHERE
    pp.name LIKE '%Finance PPM%'
GROUP BY
    ptt.name, ptt.sequence, pp.id
ORDER BY
    ptt.sequence;

-- ---------------------------------------------------------------------------
-- View 3: Assignee Workload
-- Task counts and hours per team member
-- ---------------------------------------------------------------------------
CREATE OR REPLACE VIEW v_assignee_workload AS
SELECT
    COALESCE(rp.name, 'Unassigned') AS assignee_name,
    COALESCE(ru.login, '')          AS assignee_email,
    COUNT(pt.id)                    AS total_tasks,
    COUNT(CASE WHEN ptt.name = 'Done' THEN 1 END)          AS completed_tasks,
    COUNT(CASE WHEN ptt.name NOT IN ('Done', 'Cancelled') THEN 1 END) AS open_tasks,
    COUNT(CASE WHEN pt.date_deadline < CURRENT_DATE
               AND ptt.name NOT IN ('Done', 'Cancelled') THEN 1 END) AS overdue_tasks,
    COALESCE(SUM(pt.planned_hours), 0) AS total_planned_hours,
    ROUND(
        COUNT(CASE WHEN ptt.name = 'Done' THEN 1 END) * 100.0 /
        NULLIF(COUNT(pt.id), 0),
        1
    )                               AS completion_rate
FROM
    project_task pt
    JOIN project_project pp ON pt.project_id = pp.id
    LEFT JOIN project_task_type ptt ON pt.stage_id = ptt.id
    LEFT JOIN project_task_user_rel ptu ON pt.id = ptu.task_id
    LEFT JOIN res_users ru ON ptu.user_id = ru.id
    LEFT JOIN res_partner rp ON ru.partner_id = rp.id
WHERE
    pp.name LIKE '%Finance PPM%'
GROUP BY
    rp.name, ru.login
ORDER BY
    total_tasks DESC;

-- ---------------------------------------------------------------------------
-- View 4: Closing Timeline
-- Monthly progress tracking for timeline/line chart visualization
-- ---------------------------------------------------------------------------
CREATE OR REPLACE VIEW v_closing_timeline AS
SELECT
    DATE_TRUNC('month', pt.date_deadline)::DATE AS deadline_month,
    TO_CHAR(pt.date_deadline, 'YYYY-MM')        AS month_label,
    COUNT(pt.id)                                AS total_tasks,
    COUNT(CASE WHEN ptt.name = 'Done' THEN 1 END) AS completed,
    COUNT(CASE WHEN ptt.name NOT IN ('Done', 'Cancelled') THEN 1 END) AS pending,
    COUNT(CASE WHEN pt.date_deadline < CURRENT_DATE
               AND ptt.name NOT IN ('Done', 'Cancelled') THEN 1 END) AS overdue,
    ROUND(
        COUNT(CASE WHEN ptt.name = 'Done' THEN 1 END) * 100.0 /
        NULLIF(COUNT(pt.id), 0),
        1
    )                                           AS completion_pct
FROM
    project_task pt
    JOIN project_project pp ON pt.project_id = pp.id
    LEFT JOIN project_task_type ptt ON pt.stage_id = ptt.id
WHERE
    pp.name LIKE '%Finance PPM%'
    AND pt.date_deadline IS NOT NULL
GROUP BY
    DATE_TRUNC('month', pt.date_deadline),
    TO_CHAR(pt.date_deadline, 'YYYY-MM')
ORDER BY
    deadline_month;

-- ---------------------------------------------------------------------------
-- View 5: Tax Filing Calendar
-- BIR tax filing deadlines and status
-- ---------------------------------------------------------------------------
CREATE OR REPLACE VIEW v_tax_filing_calendar AS
SELECT
    pt.id                           AS task_id,
    pt.name                         AS filing_name,
    pt.date_deadline                AS deadline,
    ptt.name                        AS stage_name,
    COALESCE(rp.name, 'Unassigned') AS preparer,
    pt.description                  AS filing_details,
    CASE
        WHEN ptt.name = 'Done'       THEN 'Filed'
        WHEN ptt.name = 'Cancelled'  THEN 'Cancelled'
        WHEN pt.date_deadline < CURRENT_DATE THEN 'OVERDUE'
        WHEN pt.date_deadline < CURRENT_DATE + INTERVAL '7 days' THEN 'Due This Week'
        WHEN pt.date_deadline < CURRENT_DATE + INTERVAL '30 days' THEN 'Due This Month'
        ELSE 'Upcoming'
    END                             AS urgency,
    pt.date_deadline - CURRENT_DATE AS days_until_due,
    CASE
        WHEN pt.name LIKE '%1601-C%'  THEN '1601-C'
        WHEN pt.name LIKE '%0619-E%'  THEN '0619-E'
        WHEN pt.name LIKE '%2550Q%'   THEN '2550Q'
        WHEN pt.name LIKE '%1601-EQ%' THEN '1601-EQ'
        WHEN pt.name LIKE '%1702%'    THEN '1702-RT'
        ELSE 'Other'
    END                             AS bir_form
FROM
    project_task pt
    JOIN project_project pp ON pt.project_id = pp.id
    LEFT JOIN project_task_type ptt ON pt.stage_id = ptt.id
    LEFT JOIN project_task_user_rel ptu ON pt.id = ptu.task_id
    LEFT JOIN res_users ru ON ptu.user_id = ru.id
    LEFT JOIN res_partner rp ON ru.partner_id = rp.id
WHERE
    pp.name LIKE '%Finance PPM%'
    AND (
        pt.name LIKE '%BIR%' OR pt.name LIKE '%1601%' OR pt.name LIKE '%0619%'
        OR pt.name LIKE '%2550%' OR pt.name LIKE '%1702%'
    )
ORDER BY
    pt.date_deadline;

-- ---------------------------------------------------------------------------
-- View 6: Finance Team
-- Team directory with role and workload summary
-- ---------------------------------------------------------------------------
CREATE OR REPLACE VIEW v_finance_team AS
SELECT
    rp.name                         AS employee_name,
    ru.login                        AS email,
    COUNT(pt.id)                    AS total_tasks,
    COUNT(CASE WHEN ptt.name NOT IN ('Done', 'Cancelled') THEN 1 END) AS active_tasks,
    COUNT(CASE WHEN ptt.name = 'Done' THEN 1 END)          AS completed_tasks,
    MIN(pt.date_deadline)           AS next_deadline,
    MAX(pt.date_deadline)           AS last_deadline,
    ROUND(
        COUNT(CASE WHEN ptt.name = 'Done' THEN 1 END) * 100.0 /
        NULLIF(COUNT(pt.id), 0),
        1
    )                               AS completion_rate
FROM
    res_users ru
    JOIN res_partner rp ON ru.partner_id = rp.id
    JOIN project_task_user_rel ptu ON ru.id = ptu.user_id
    JOIN project_task pt ON ptu.task_id = pt.id
    JOIN project_project pp ON pt.project_id = pp.id
    LEFT JOIN project_task_type ptt ON pt.stage_id = ptt.id
WHERE
    pp.name LIKE '%Finance PPM%'
GROUP BY
    rp.name, ru.login
ORDER BY
    total_tasks DESC;

-- ---------------------------------------------------------------------------
-- Grant Superset read access
-- ---------------------------------------------------------------------------
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'superset') THEN
        GRANT SELECT ON v_closing_task_summary TO superset;
        GRANT SELECT ON v_stage_funnel TO superset;
        GRANT SELECT ON v_assignee_workload TO superset;
        GRANT SELECT ON v_closing_timeline TO superset;
        GRANT SELECT ON v_tax_filing_calendar TO superset;
        GRANT SELECT ON v_finance_team TO superset;
        RAISE NOTICE 'Granted SELECT on all views to superset role';
    ELSE
        RAISE NOTICE 'superset role not found - skipping grants';
    END IF;
END $$;

-- Verification
SELECT 'v_closing_task_summary' AS view_name, COUNT(*) AS status FROM information_schema.views WHERE table_name = 'v_closing_task_summary'
UNION ALL
SELECT 'v_stage_funnel', COUNT(*) FROM information_schema.views WHERE table_name = 'v_stage_funnel'
UNION ALL
SELECT 'v_assignee_workload', COUNT(*) FROM information_schema.views WHERE table_name = 'v_assignee_workload'
UNION ALL
SELECT 'v_closing_timeline', COUNT(*) FROM information_schema.views WHERE table_name = 'v_closing_timeline'
UNION ALL
SELECT 'v_tax_filing_calendar', COUNT(*) FROM information_schema.views WHERE table_name = 'v_tax_filing_calendar'
UNION ALL
SELECT 'v_finance_team', COUNT(*) FROM information_schema.views WHERE table_name = 'v_finance_team';
