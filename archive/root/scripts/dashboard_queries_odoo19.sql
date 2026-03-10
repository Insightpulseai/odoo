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
    pp.name                         AS project_name_raw,
    CASE
        WHEN pp.name LIKE '%BIR%' THEN 'BIR Tax Filing'
        WHEN pp.name LIKE '%Month-End%' THEN 'Month-End Close'
        ELSE 'Other'
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
        WHEN pt.name LIKE '%2550M%'   THEN '2550M'
        WHEN pt.name LIKE '%2550Q%'   THEN '2550Q'
        WHEN pt.name LIKE '%1601-EQ%' THEN '1601-EQ'
        WHEN pt.name LIKE '%1702Q%'   THEN '1702Q'
        WHEN pt.name LIKE '%1702-RT%' THEN '1702-RT'
        WHEN pt.name LIKE '%1604-CF%' THEN '1604-CF'
        WHEN pt.name LIKE '%1604-E%'  THEN '1604-E'
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
    pp.name LIKE '%BIR Tax Filing%'
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
-- View 7: Logframe — Goal KPI
-- On-time completion rate across both projects (Goal indicator)
-- ---------------------------------------------------------------------------
CREATE OR REPLACE VIEW v_logframe_goal_kpi AS
SELECT
    'Goal' AS logframe_level,
    'On-time filing & closing rate' AS kpi_name,
    COUNT(pt.id) AS total_tasks,
    COUNT(CASE WHEN ptt.name = 'Done' THEN 1 END) AS completed_tasks,
    COUNT(CASE WHEN ptt.name = 'Done'
               AND (pt.date_deadline IS NULL OR pt.write_date::date <= pt.date_deadline)
          THEN 1 END) AS completed_on_time,
    ROUND(
        COUNT(CASE WHEN ptt.name = 'Done'
                   AND (pt.date_deadline IS NULL OR pt.write_date::date <= pt.date_deadline)
              THEN 1 END) * 100.0 /
        NULLIF(COUNT(CASE WHEN ptt.name = 'Done' THEN 1 END), 0),
        1
    ) AS on_time_pct,
    CASE
        WHEN COUNT(CASE WHEN ptt.name = 'Done'
                        AND (pt.date_deadline IS NULL OR pt.write_date::date <= pt.date_deadline)
                   THEN 1 END) * 100.0 /
             NULLIF(COUNT(CASE WHEN ptt.name = 'Done' THEN 1 END), 0) >= 95
        THEN 'GREEN'
        WHEN COUNT(CASE WHEN ptt.name = 'Done'
                        AND (pt.date_deadline IS NULL OR pt.write_date::date <= pt.date_deadline)
                   THEN 1 END) * 100.0 /
             NULLIF(COUNT(CASE WHEN ptt.name = 'Done' THEN 1 END), 0) >= 80
        THEN 'AMBER'
        ELSE 'RED'
    END AS rag_status
FROM
    project_task pt
    JOIN project_project pp ON pt.project_id = pp.id
    LEFT JOIN project_task_type ptt ON pt.stage_id = ptt.id
WHERE
    pp.name LIKE '%Finance PPM%';

-- ---------------------------------------------------------------------------
-- View 8: Logframe — Outcome KPI
-- Average processing delay per task (Outcome indicator: <1 day)
-- ---------------------------------------------------------------------------
CREATE OR REPLACE VIEW v_logframe_outcome_kpi AS
SELECT
    'Outcome' AS logframe_level,
    'Avg processing delay (days)' AS kpi_name,
    pp.name AS project_name,
    COUNT(CASE WHEN ptt.name = 'Done' THEN 1 END) AS completed_tasks,
    ROUND(
        AVG(
            CASE WHEN ptt.name = 'Done' AND pt.date_deadline IS NOT NULL
                 THEN GREATEST(pt.write_date::date - pt.date_deadline, 0)
            END
        ), 1
    ) AS avg_delay_days,
    CASE
        WHEN AVG(
            CASE WHEN ptt.name = 'Done' AND pt.date_deadline IS NOT NULL
                 THEN GREATEST(pt.write_date::date - pt.date_deadline, 0)
            END
        ) <= 1 THEN 'GREEN'
        WHEN AVG(
            CASE WHEN ptt.name = 'Done' AND pt.date_deadline IS NOT NULL
                 THEN GREATEST(pt.write_date::date - pt.date_deadline, 0)
            END
        ) <= 3 THEN 'AMBER'
        ELSE 'RED'
    END AS rag_status
FROM
    project_task pt
    JOIN project_project pp ON pt.project_id = pp.id
    LEFT JOIN project_task_type ptt ON pt.stage_id = ptt.id
WHERE
    pp.name LIKE '%Finance PPM%'
GROUP BY
    pp.name;

-- ---------------------------------------------------------------------------
-- View 9: Logframe — IM1 KPI (Month-End Closing)
-- Closing reconciliation rate + adjustment count
-- ---------------------------------------------------------------------------
CREATE OR REPLACE VIEW v_logframe_im1_kpi AS
SELECT
    'IM1' AS logframe_level,
    'Month-End Closing' AS objective,
    DATE_TRUNC('month', pt.date_deadline)::DATE AS period_month,
    TO_CHAR(pt.date_deadline, 'YYYY-MM') AS month_label,
    COUNT(pt.id) AS total_closing_tasks,
    COUNT(CASE WHEN ptt.name = 'Done' THEN 1 END) AS reconciled_tasks,
    COUNT(CASE WHEN ptt.name NOT IN ('Done', 'Cancelled') THEN 1 END) AS pending_adjustments,
    ROUND(
        COUNT(CASE WHEN ptt.name = 'Done' THEN 1 END) * 100.0 /
        NULLIF(COUNT(pt.id), 0), 1
    ) AS reconciliation_pct,
    CASE
        WHEN COUNT(CASE WHEN ptt.name = 'Done' THEN 1 END) * 100.0 /
             NULLIF(COUNT(pt.id), 0) >= 95 THEN 'GREEN'
        WHEN COUNT(CASE WHEN ptt.name = 'Done' THEN 1 END) * 100.0 /
             NULLIF(COUNT(pt.id), 0) >= 75 THEN 'AMBER'
        ELSE 'RED'
    END AS rag_status
FROM
    project_task pt
    JOIN project_project pp ON pt.project_id = pp.id
    LEFT JOIN project_task_type ptt ON pt.stage_id = ptt.id
WHERE
    pp.name = 'Finance PPM - Month-End Close'
    AND pt.date_deadline IS NOT NULL
GROUP BY
    DATE_TRUNC('month', pt.date_deadline),
    TO_CHAR(pt.date_deadline, 'YYYY-MM')
ORDER BY
    period_month;

-- ---------------------------------------------------------------------------
-- View 10: Logframe — IM2 KPI (Tax Filing Compliance)
-- BIR filing rate vs deadlines by form type
-- ---------------------------------------------------------------------------
CREATE OR REPLACE VIEW v_logframe_im2_kpi AS
SELECT
    'IM2' AS logframe_level,
    'Tax Filing Compliance' AS objective,
    CASE
        WHEN pt.name LIKE '%1601-C%'  THEN '1601-C'
        WHEN pt.name LIKE '%0619-E%'  THEN '0619-E'
        WHEN pt.name LIKE '%2550M%'   THEN '2550M'
        WHEN pt.name LIKE '%2550Q%'   THEN '2550Q'
        WHEN pt.name LIKE '%1601-EQ%' THEN '1601-EQ'
        WHEN pt.name LIKE '%1702Q%'   THEN '1702Q'
        WHEN pt.name LIKE '%1702-RT%' THEN '1702-RT'
        WHEN pt.name LIKE '%1604-CF%' THEN '1604-CF'
        WHEN pt.name LIKE '%1604-E%'  THEN '1604-E'
        ELSE 'Other'
    END AS bir_form,
    COUNT(pt.id) AS total_filings,
    COUNT(CASE WHEN ptt.name = 'Done' THEN 1 END) AS filed,
    COUNT(CASE WHEN ptt.name = 'Done'
               AND pt.write_date::date <= pt.date_deadline
          THEN 1 END) AS filed_on_time,
    COUNT(CASE WHEN pt.date_deadline < CURRENT_DATE
               AND ptt.name NOT IN ('Done', 'Cancelled')
          THEN 1 END) AS overdue,
    ROUND(
        COUNT(CASE WHEN ptt.name = 'Done'
                   AND pt.write_date::date <= pt.date_deadline
              THEN 1 END) * 100.0 /
        NULLIF(COUNT(CASE WHEN ptt.name = 'Done' THEN 1 END), 0),
        1
    ) AS on_time_filing_pct,
    CASE
        WHEN COUNT(CASE WHEN pt.date_deadline < CURRENT_DATE
                        AND ptt.name NOT IN ('Done', 'Cancelled')
                   THEN 1 END) = 0 THEN 'GREEN'
        WHEN COUNT(CASE WHEN pt.date_deadline < CURRENT_DATE
                        AND ptt.name NOT IN ('Done', 'Cancelled')
                   THEN 1 END) <= 2 THEN 'AMBER'
        ELSE 'RED'
    END AS rag_status
FROM
    project_task pt
    JOIN project_project pp ON pt.project_id = pp.id
    LEFT JOIN project_task_type ptt ON pt.stage_id = ptt.id
WHERE
    pp.name = 'Finance PPM - BIR Tax Filing'
GROUP BY
    CASE
        WHEN pt.name LIKE '%1601-C%'  THEN '1601-C'
        WHEN pt.name LIKE '%0619-E%'  THEN '0619-E'
        WHEN pt.name LIKE '%2550M%'   THEN '2550M'
        WHEN pt.name LIKE '%2550Q%'   THEN '2550Q'
        WHEN pt.name LIKE '%1601-EQ%' THEN '1601-EQ'
        WHEN pt.name LIKE '%1702Q%'   THEN '1702Q'
        WHEN pt.name LIKE '%1702-RT%' THEN '1702-RT'
        WHEN pt.name LIKE '%1604-CF%' THEN '1604-CF'
        WHEN pt.name LIKE '%1604-E%'  THEN '1604-E'
        ELSE 'Other'
    END
ORDER BY
    bir_form;

-- ---------------------------------------------------------------------------
-- View 11: Logframe — Outputs KPI
-- Consolidated output completion across both projects
-- ---------------------------------------------------------------------------
CREATE OR REPLACE VIEW v_logframe_outputs_kpi AS
SELECT
    'Outputs' AS logframe_level,
    TO_CHAR(CURRENT_DATE, 'YYYY-MM') AS current_period,
    -- Output 1: Journal entries and accruals finalized (Month-End Close project)
    (SELECT COUNT(*) FROM project_task pt
     JOIN project_project pp ON pt.project_id = pp.id
     LEFT JOIN project_task_type ptt ON pt.stage_id = ptt.id
     WHERE pp.name = 'Finance PPM - Month-End Close'
       AND ptt.name = 'Done') AS je_accruals_completed,
    (SELECT COUNT(*) FROM project_task pt
     JOIN project_project pp ON pt.project_id = pp.id
     WHERE pp.name = 'Finance PPM - Month-End Close') AS je_accruals_total,
    -- Output 2: All BIR forms filed (BIR Tax Filing project)
    (SELECT COUNT(*) FROM project_task pt
     JOIN project_project pp ON pt.project_id = pp.id
     LEFT JOIN project_task_type ptt ON pt.stage_id = ptt.id
     WHERE pp.name = 'Finance PPM - BIR Tax Filing'
       AND ptt.name = 'Done') AS bir_forms_filed,
    (SELECT COUNT(*) FROM project_task pt
     JOIN project_project pp ON pt.project_id = pp.id
     WHERE pp.name = 'Finance PPM - BIR Tax Filing') AS bir_forms_total,
    -- Output 3: Reports reviewed and approved
    (SELECT COUNT(*) FROM project_task pt
     JOIN project_project pp ON pt.project_id = pp.id
     LEFT JOIN project_task_type ptt ON pt.stage_id = ptt.id
     WHERE pp.name LIKE '%Finance PPM%'
       AND ptt.name IN ('Done', 'Pending Approval')) AS reports_reviewed,
    -- Overall
    (SELECT COUNT(*) FROM project_task pt
     JOIN project_project pp ON pt.project_id = pp.id
     LEFT JOIN project_task_type ptt ON pt.stage_id = ptt.id
     WHERE pp.name LIKE '%Finance PPM%'
       AND ptt.name = 'Done') AS total_completed,
    (SELECT COUNT(*) FROM project_task pt
     JOIN project_project pp ON pt.project_id = pp.id
     WHERE pp.name LIKE '%Finance PPM%') AS total_tasks;

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
        GRANT SELECT ON v_logframe_goal_kpi TO superset;
        GRANT SELECT ON v_logframe_outcome_kpi TO superset;
        GRANT SELECT ON v_logframe_im1_kpi TO superset;
        GRANT SELECT ON v_logframe_im2_kpi TO superset;
        GRANT SELECT ON v_logframe_outputs_kpi TO superset;
        RAISE NOTICE 'Granted SELECT on all 11 views to superset role';
    ELSE
        RAISE NOTICE 'superset role not found - skipping grants';
    END IF;
END $$;

-- Verification (11 views)
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
SELECT 'v_finance_team', COUNT(*) FROM information_schema.views WHERE table_name = 'v_finance_team'
UNION ALL
SELECT 'v_logframe_goal_kpi', COUNT(*) FROM information_schema.views WHERE table_name = 'v_logframe_goal_kpi'
UNION ALL
SELECT 'v_logframe_outcome_kpi', COUNT(*) FROM information_schema.views WHERE table_name = 'v_logframe_outcome_kpi'
UNION ALL
SELECT 'v_logframe_im1_kpi', COUNT(*) FROM information_schema.views WHERE table_name = 'v_logframe_im1_kpi'
UNION ALL
SELECT 'v_logframe_im2_kpi', COUNT(*) FROM information_schema.views WHERE table_name = 'v_logframe_im2_kpi'
UNION ALL
SELECT 'v_logframe_outputs_kpi', COUNT(*) FROM information_schema.views WHERE table_name = 'v_logframe_outputs_kpi';
