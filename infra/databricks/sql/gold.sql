-- Gold Layer Tables
-- Business-ready marts and aggregations

-- Budget vs Actual metrics
CREATE TABLE IF NOT EXISTS ${catalog}.gold.ppm_budget_vs_actual (
    project_id STRING NOT NULL COMMENT 'Project UUID',
    project_name STRING COMMENT 'Project name',
    program_id STRING COMMENT 'Parent program ID',
    status STRING COMMENT 'Project status',
    budget DECIMAL(18, 2) COMMENT 'Total budget',
    actual DECIMAL(18, 2) COMMENT 'Total actual spend',
    forecast DECIMAL(18, 2) COMMENT 'Total forecast',
    variance DECIMAL(18, 2) COMMENT 'Budget minus actual',
    burn_rate_pct DECIMAL(5, 2) COMMENT 'Actual/Budget percentage',
    _etl_loaded_at TIMESTAMP NOT NULL COMMENT 'ETL load timestamp',
    CONSTRAINT pk_budget_actual PRIMARY KEY (project_id)
)
USING DELTA
COMMENT 'Budget vs actual metrics by project'
TBLPROPERTIES (
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true'
);

-- Forecast with run-rate projections
CREATE TABLE IF NOT EXISTS ${catalog}.gold.ppm_forecast (
    project_id STRING NOT NULL COMMENT 'Project UUID',
    project_name STRING COMMENT 'Project name',
    budget DECIMAL(18, 2) COMMENT 'Total budget',
    actual DECIMAL(18, 2) COMMENT 'Total actual',
    burn_rate_pct DECIMAL(5, 2) COMMENT 'Current burn rate',
    run_rate_forecast DECIMAL(18, 2) COMMENT 'Projected total based on run rate',
    projected_variance DECIMAL(18, 2) COMMENT 'Budget minus projected',
    health_status STRING COMMENT 'Health status: Over Budget, At Risk, On Track, Under Budget',
    start_date DATE COMMENT 'Project start date',
    end_date DATE COMMENT 'Project end date',
    _etl_loaded_at TIMESTAMP NOT NULL COMMENT 'ETL load timestamp',
    CONSTRAINT pk_forecast PRIMARY KEY (project_id)
)
USING DELTA
COMMENT 'Project forecasts with run-rate projections'
TBLPROPERTIES (
    'delta.autoOptimize.optimizeWrite' = 'true'
);

-- Risk summary rollups
CREATE TABLE IF NOT EXISTS ${catalog}.gold.ppm_risk_summary (
    project_id STRING NOT NULL COMMENT 'Project UUID',
    total_risks INT COMMENT 'Total number of risks',
    open_risks INT COMMENT 'Number of open risks',
    high_severity INT COMMENT 'High severity risks count',
    medium_severity INT COMMENT 'Medium severity risks count',
    low_severity INT COMMENT 'Low severity risks count',
    critical_open INT COMMENT 'High severity AND open risks',
    risk_score INT COMMENT 'Weighted risk score',
    _etl_loaded_at TIMESTAMP NOT NULL COMMENT 'ETL load timestamp',
    CONSTRAINT pk_risk_summary PRIMARY KEY (project_id)
)
USING DELTA
COMMENT 'Risk summary metrics by project'
TBLPROPERTIES (
    'delta.autoOptimize.optimizeWrite' = 'true'
);

-- Enriched projects summary
CREATE TABLE IF NOT EXISTS ${catalog}.gold.ppm_projects_summary (
    project_id STRING NOT NULL COMMENT 'Project UUID',
    name STRING COMMENT 'Project name',
    program_id STRING COMMENT 'Parent program ID',
    program_name STRING COMMENT 'Program name',
    status STRING COMMENT 'Project status',
    priority STRING COMMENT 'Project priority',
    owner STRING COMMENT 'Project owner',
    start_date DATE COMMENT 'Start date',
    end_date DATE COMMENT 'End date',
    budget DECIMAL(18, 2) COMMENT 'Total budget',
    actual DECIMAL(18, 2) COMMENT 'Total actual',
    variance DECIMAL(18, 2) COMMENT 'Budget variance',
    burn_rate_pct DECIMAL(5, 2) COMMENT 'Burn rate percentage',
    total_risks INT COMMENT 'Total risks',
    open_risks INT COMMENT 'Open risks',
    risk_score INT COMMENT 'Risk score',
    overall_health STRING COMMENT 'Overall health: Critical, At Risk, Healthy',
    _etl_loaded_at TIMESTAMP NOT NULL COMMENT 'ETL load timestamp',
    CONSTRAINT pk_projects_summary PRIMARY KEY (project_id)
)
USING DELTA
COMMENT 'Enriched projects summary with budget and risk data'
TBLPROPERTIES (
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true'
);

-- Control Room pipeline status
CREATE TABLE IF NOT EXISTS ${catalog}.gold.control_room_status (
    job_id STRING NOT NULL COMMENT 'Databricks job ID',
    job_name STRING COMMENT 'Job name',
    last_run_id STRING COMMENT 'Last run ID',
    last_run_status STRING COMMENT 'Last run status',
    last_run_duration_sec INT COMMENT 'Last run duration in seconds',
    last_run_start_time TIMESTAMP COMMENT 'Last run start time',
    last_run_end_time TIMESTAMP COMMENT 'Last run end time',
    schedule_cron STRING COMMENT 'Schedule cron expression',
    next_scheduled_run TIMESTAMP COMMENT 'Next scheduled run time',
    _etl_loaded_at TIMESTAMP NOT NULL COMMENT 'ETL load timestamp',
    CONSTRAINT pk_control_room PRIMARY KEY (job_id)
)
USING DELTA
COMMENT 'Pipeline health and status metrics'
TBLPROPERTIES (
    'delta.autoOptimize.optimizeWrite' = 'true'
);

-- Data quality issues log
CREATE TABLE IF NOT EXISTS ${catalog}.gold.dq_issues (
    issue_id STRING NOT NULL COMMENT 'Unique issue ID',
    table_name STRING NOT NULL COMMENT 'Table with issue',
    check_name STRING NOT NULL COMMENT 'DQ check name',
    check_type STRING COMMENT 'Check type: not_null, unique, etc.',
    failed_rows INT COMMENT 'Number of failed rows',
    total_rows INT COMMENT 'Total rows checked',
    failure_pct DECIMAL(5, 2) COMMENT 'Failure percentage',
    threshold_pct DECIMAL(5, 2) COMMENT 'Configured threshold',
    severity STRING COMMENT 'Issue severity',
    detected_at TIMESTAMP NOT NULL COMMENT 'When issue was detected',
    resolved_at TIMESTAMP COMMENT 'When issue was resolved',
    _etl_loaded_at TIMESTAMP NOT NULL COMMENT 'ETL load timestamp'
)
USING DELTA
COMMENT 'Data quality issues log'
TBLPROPERTIES (
    'delta.autoOptimize.optimizeWrite' = 'true'
);
