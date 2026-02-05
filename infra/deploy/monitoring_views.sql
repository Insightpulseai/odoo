-- Superset helper views for ipai_monitoring schema
CREATE OR REPLACE VIEW ipai_monitoring.v_service_uptime_daily AS
SELECT
  service_name,
  date_trunc('day', checked_at) AS day,
  count(*) AS total_checks,
  sum(CASE WHEN is_up THEN 1 ELSE 0 END) AS up_checks,
  round(100.0 * sum(CASE WHEN is_up THEN 1 ELSE 0 END) / count(*), 2) AS uptime_pct
FROM ipai_monitoring.service_health_checks
GROUP BY service_name, date_trunc('day', checked_at);

CREATE OR REPLACE VIEW ipai_monitoring.v_backup_status_daily AS
SELECT
  source_db,
  date_trunc('day', verified_at) AS day,
  count(*) AS total_runs,
  sum(CASE WHEN success THEN 1 ELSE 0 END) AS success_runs,
  round(100.0 * sum(CASE WHEN success THEN 1 ELSE 0 END) / count(*), 2) AS success_pct
FROM ipai_monitoring.backup_verifications
GROUP BY source_db, date_trunc('day', verified_at);
