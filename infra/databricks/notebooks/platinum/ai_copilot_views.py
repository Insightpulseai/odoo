# Databricks notebook source
# MAGIC %md
# MAGIC # Platinum Layer — AI Copilot SQL Views
# MAGIC
# MAGIC Creates AI-enabled SQL views that Power BI can query via DirectQuery.
# MAGIC These views use `ai_query()` to call Azure OpenAI through the
# MAGIC `ipai-azure-openai` model serving endpoint.
# MAGIC
# MAGIC **Purpose**: Power BI Copilot alternative without Fabric F2 capacity.
# MAGIC Power BI connects to SQL Warehouse → queries these views → gets
# MAGIC AI-enriched results rendered in reports.
# MAGIC
# MAGIC **Requires**: Serverless SQL Warehouse, Runtime 15.4 LTS+

# COMMAND ----------

# MAGIC %md
# MAGIC ## Setup

# COMMAND ----------

catalog = spark.conf.get("bundle.catalog", "dev_ppm")
schema_gold = spark.conf.get("bundle.schema_gold", "gold")
schema_platinum = "platinum"

spark.sql(f"USE CATALOG {catalog}")
spark.sql(f"CREATE SCHEMA IF NOT EXISTS {schema_platinum}")
spark.sql(f"USE SCHEMA {schema_platinum}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. Budget Narrative — AI-generated variance explanation

# COMMAND ----------

spark.sql(f"""
CREATE OR REPLACE VIEW {catalog}.{schema_platinum}.ai_budget_narrative AS
SELECT
    project_name,
    budget_total,
    actual_total,
    variance_pct,
    ai_query(
        'ipai-azure-openai',
        CONCAT(
            'You are a finance analyst. In 2-3 sentences, explain this ',
            'budget variance for project "', project_name, '": ',
            'Budget: ', CAST(budget_total AS STRING),
            ', Actual: ', CAST(actual_total AS STRING),
            ', Variance: ', CAST(variance_pct AS STRING), '%.',
            ' Flag if this needs attention.'
        ),
        modelParameters => named_struct(
            'max_tokens', 150,
            'temperature', 0.3
        )
    ) AS ai_narrative,
    current_timestamp() AS generated_at
FROM {catalog}.{schema_gold}.ppm_budget_vs_actual
WHERE ABS(variance_pct) > 5.0
""")

print("Created: ai_budget_narrative")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Risk Assessment — AI-scored risk severity

# COMMAND ----------

spark.sql(f"""
CREATE OR REPLACE VIEW {catalog}.{schema_platinum}.ai_risk_assessment AS
SELECT
    risk_id,
    risk_title,
    risk_description,
    project_name,
    current_severity,
    ai_query(
        'ipai-azure-openai',
        CONCAT(
            'You are a risk analyst for a finance operations team. ',
            'Assess this risk and respond with ONLY a JSON object: ',
            '{{"severity_score": <1-10>, "category": "<financial|operational|compliance|strategic>", ',
            '"recommendation": "<1 sentence>", "escalate": <true|false>}}. ',
            'Risk: "', risk_title, '" — ', risk_description
        ),
        responseFormat => '{{
            "type": "json_schema",
            "json_schema": {{
                "name": "risk_assessment",
                "schema": {{
                    "type": "object",
                    "properties": {{
                        "severity_score": {{"type": "integer"}},
                        "category": {{"type": "string"}},
                        "recommendation": {{"type": "string"}},
                        "escalate": {{"type": "boolean"}}
                    }},
                    "required": ["severity_score", "category", "recommendation", "escalate"]
                }},
                "strict": true
            }}
        }}'
    ) AS ai_assessment,
    current_timestamp() AS assessed_at
FROM {catalog}.{schema_gold}.ppm_risk_summary
""")

print("Created: ai_risk_assessment")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. Project Health Summary — Natural language status

# COMMAND ----------

spark.sql(f"""
CREATE OR REPLACE VIEW {catalog}.{schema_platinum}.ai_project_health AS
SELECT
    project_id,
    project_name,
    project_status,
    completion_pct,
    days_remaining,
    budget_total,
    actual_total,
    ai_query(
        'ipai-azure-openai',
        CONCAT(
            'Summarize this project health in 2 sentences for an executive: ',
            'Project: "', project_name, '", ',
            'Status: ', project_status, ', ',
            'Completion: ', CAST(completion_pct AS STRING), '%, ',
            'Days remaining: ', CAST(days_remaining AS STRING), ', ',
            'Budget: ', CAST(budget_total AS STRING),
            ', Spent: ', CAST(actual_total AS STRING), '. ',
            'Include a traffic light rating (GREEN/AMBER/RED).'
        ),
        modelParameters => named_struct(
            'max_tokens', 100,
            'temperature', 0.2
        )
    ) AS ai_health_summary,
    current_timestamp() AS summarized_at
FROM {catalog}.{schema_gold}.ppm_projects
""")

print("Created: ai_project_health")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. Forecast Commentary — AI explanation of run-rate

# COMMAND ----------

spark.sql(f"""
CREATE OR REPLACE VIEW {catalog}.{schema_platinum}.ai_forecast_commentary AS
SELECT
    project_name,
    forecast_month,
    forecast_amount,
    run_rate,
    trend_direction,
    ai_query(
        'ipai-azure-openai',
        CONCAT(
            'As a finance analyst, explain this forecast in 1-2 sentences: ',
            'Project "', project_name, '" ',
            'forecast for ', forecast_month, ': ',
            'Amount: ', CAST(forecast_amount AS STRING),
            ', Run rate: ', CAST(run_rate AS STRING),
            ', Trend: ', trend_direction, '. ',
            'Note any concerns.'
        ),
        modelParameters => named_struct(
            'max_tokens', 100,
            'temperature', 0.3
        )
    ) AS ai_commentary,
    current_timestamp() AS generated_at
FROM {catalog}.{schema_gold}.ppm_forecast
""")

print("Created: ai_forecast_commentary")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 5. Ad-hoc Query View — Parameterized AI analysis
# MAGIC
# MAGIC This view is queried from Power BI with a parameter:
# MAGIC `SELECT * FROM platinum.ai_adhoc_query WHERE question = 'What projects are over budget?'`

# COMMAND ----------

spark.sql(f"""
CREATE OR REPLACE FUNCTION {catalog}.{schema_platinum}.ask_copilot(
    question STRING
)
RETURNS STRING
COMMENT 'Ad-hoc AI analysis over PPM gold tables. Pass a natural language question.'
RETURN ai_query(
    'ipai-azure-openai',
    CONCAT(
        'You are a finance copilot for InsightPulse AI. ',
        'You have access to these tables in the gold layer: ',
        'ppm_budget_vs_actual (project budgets and actuals), ',
        'ppm_forecast (monthly forecasts and run rates), ',
        'ppm_risk_summary (project risks and severity), ',
        'ppm_projects (project status, completion, timelines). ',
        'Answer this question concisely: ', question
    ),
    modelParameters => named_struct(
        'max_tokens', 300,
        'temperature', 0.4
    )
)
""")

print("Created: ask_copilot() UDF")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Verification

# COMMAND ----------

views = spark.sql(f"""
    SELECT table_name, table_type
    FROM {catalog}.information_schema.tables
    WHERE table_schema = '{schema_platinum}'
    ORDER BY table_name
""")
views.display()

# COMMAND ----------

routines = spark.sql(f"""
    SELECT routine_name, routine_type
    FROM {catalog}.information_schema.routines
    WHERE routine_schema = '{schema_platinum}'
""")
routines.display()

print("Platinum AI layer ready. Connect Power BI to SQL Warehouse.")
