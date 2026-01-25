-- Silver Layer Tables
-- Normalized and type-enforced data

-- Programs from Notion
CREATE TABLE IF NOT EXISTS ${catalog}.silver.notion_programs (
    program_id STRING NOT NULL COMMENT 'Notion program UUID',
    name STRING COMMENT 'Program name',
    status STRING COMMENT 'Program status',
    owner STRING COMMENT 'Program owner name',
    start_date DATE COMMENT 'Program start date',
    end_date DATE COMMENT 'Program end date',
    budget DECIMAL(18, 2) COMMENT 'Total program budget',
    last_modified_at TIMESTAMP COMMENT 'Last modification in Notion',
    _etl_loaded_at TIMESTAMP NOT NULL COMMENT 'ETL load timestamp',
    CONSTRAINT pk_programs PRIMARY KEY (program_id)
)
USING DELTA
COMMENT 'Normalized programs from Notion'
TBLPROPERTIES (
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true'
);

-- Projects from Notion
CREATE TABLE IF NOT EXISTS ${catalog}.silver.notion_projects (
    project_id STRING NOT NULL COMMENT 'Notion project UUID',
    name STRING COMMENT 'Project name',
    program_id STRING COMMENT 'Parent program ID',
    status STRING COMMENT 'Project status',
    priority STRING COMMENT 'Project priority',
    owner STRING COMMENT 'Project owner name',
    start_date DATE COMMENT 'Project start date',
    end_date DATE COMMENT 'Project end date',
    budget DECIMAL(18, 2) COMMENT 'Project budget',
    actual DECIMAL(18, 2) COMMENT 'Actual spend to date',
    last_modified_at TIMESTAMP COMMENT 'Last modification in Notion',
    _etl_loaded_at TIMESTAMP NOT NULL COMMENT 'ETL load timestamp',
    CONSTRAINT pk_projects PRIMARY KEY (project_id),
    CONSTRAINT fk_projects_program FOREIGN KEY (program_id)
        REFERENCES ${catalog}.silver.notion_programs(program_id)
)
USING DELTA
COMMENT 'Normalized projects from Notion'
TBLPROPERTIES (
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true'
);

-- Budget lines from Notion
CREATE TABLE IF NOT EXISTS ${catalog}.silver.notion_budget_lines (
    budget_line_id STRING NOT NULL COMMENT 'Notion budget line UUID',
    project_id STRING NOT NULL COMMENT 'Parent project ID',
    category STRING COMMENT 'Budget category',
    description STRING COMMENT 'Line item description',
    amount DECIMAL(18, 2) COMMENT 'Line amount',
    line_type STRING COMMENT 'Type: Budget, Actual, or Forecast',
    line_date DATE COMMENT 'Transaction/forecast date',
    _etl_loaded_at TIMESTAMP NOT NULL COMMENT 'ETL load timestamp',
    CONSTRAINT pk_budget_lines PRIMARY KEY (budget_line_id),
    CONSTRAINT fk_budget_lines_project FOREIGN KEY (project_id)
        REFERENCES ${catalog}.silver.notion_projects(project_id)
)
USING DELTA
COMMENT 'Normalized budget lines from Notion'
TBLPROPERTIES (
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true'
);

-- Risks from Notion
CREATE TABLE IF NOT EXISTS ${catalog}.silver.notion_risks (
    risk_id STRING NOT NULL COMMENT 'Notion risk UUID',
    project_id STRING NOT NULL COMMENT 'Parent project ID',
    name STRING COMMENT 'Risk name/title',
    category STRING COMMENT 'Risk category',
    severity STRING COMMENT 'Risk severity: High, Medium, Low',
    probability STRING COMMENT 'Risk probability',
    status STRING COMMENT 'Risk status: Open, Mitigated, Closed',
    mitigation STRING COMMENT 'Mitigation strategy',
    last_modified_at TIMESTAMP COMMENT 'Last modification in Notion',
    _etl_loaded_at TIMESTAMP NOT NULL COMMENT 'ETL load timestamp',
    CONSTRAINT pk_risks PRIMARY KEY (risk_id),
    CONSTRAINT fk_risks_project FOREIGN KEY (project_id)
        REFERENCES ${catalog}.silver.notion_projects(project_id)
)
USING DELTA
COMMENT 'Normalized risks from Notion'
TBLPROPERTIES (
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true'
);

-- Azure Advisor recommendations
CREATE TABLE IF NOT EXISTS ${catalog}.silver.azure_advisor_recommendations (
    recommendation_id STRING NOT NULL COMMENT 'Azure recommendation ID',
    name STRING COMMENT 'Recommendation name',
    category STRING COMMENT 'Advisor category: Cost, Security, etc.',
    impact STRING COMMENT 'Impact level',
    impacted_field STRING COMMENT 'Impacted resource type',
    impacted_value STRING COMMENT 'Impacted resource name',
    short_description STRING COMMENT 'Problem description',
    subscription_id STRING COMMENT 'Azure subscription ID',
    resource_group STRING COMMENT 'Resource group name',
    _etl_loaded_at TIMESTAMP NOT NULL COMMENT 'ETL load timestamp',
    CONSTRAINT pk_advisor PRIMARY KEY (recommendation_id)
)
USING DELTA
COMMENT 'Normalized Azure Advisor recommendations'
TBLPROPERTIES (
    'delta.autoOptimize.optimizeWrite' = 'true'
);
