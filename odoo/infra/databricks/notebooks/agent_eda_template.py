# Databricks notebook source
# MAGIC %md
# MAGIC # Data Science Agent - EDA Template
# MAGIC
# MAGIC This notebook is designed to be used with Databricks Data Science Agent.
# MAGIC Open the Assistant panel, select **Agent Mode**, and use the prompts below.
# MAGIC
# MAGIC ## Quick Start Prompts
# MAGIC
# MAGIC Copy one of these prompts into the Agent:
# MAGIC
# MAGIC **Basic EDA:**
# MAGIC ```
# MAGIC Describe this dataset. Perform EDA to understand column statistics
# MAGIC and visualize the distribution of values. Think like a data scientist.
# MAGIC ```
# MAGIC
# MAGIC **Quality Audit:**
# MAGIC ```
# MAGIC Audit this dataset for data quality issues: nulls, duplicates,
# MAGIC outliers, and schema anomalies. Create a quality scorecard.
# MAGIC ```
# MAGIC
# MAGIC **Trend Analysis:**
# MAGIC ```
# MAGIC Analyze trends over time. Identify seasonality, anomalies,
# MAGIC and forecast the next 30 days with confidence intervals.
# MAGIC ```

# COMMAND ----------

# MAGIC %md
# MAGIC ## Configuration
# MAGIC Set your target table below. The Agent will use this as context.

# COMMAND ----------

# Configuration - Update these values
CATALOG = "samples"
SCHEMA = "bakehouse"
TABLE = "sales_transactions"

# Full table path
TABLE_PATH = f"{CATALOG}.{SCHEMA}.{TABLE}"
print(f"Target table: {TABLE_PATH}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Data Preview
# MAGIC Quick look at the data before engaging the Agent.

# COMMAND ----------

# Preview the data
df = spark.table(TABLE_PATH)
display(df.limit(100))

# COMMAND ----------

# Basic stats
print(f"Row count: {df.count():,}")
print(f"Column count: {len(df.columns)}")
print(f"Columns: {', '.join(df.columns)}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Agent Workspace
# MAGIC
# MAGIC The cells below are left empty for the Data Science Agent to populate.
# MAGIC
# MAGIC **Instructions:**
# MAGIC 1. Open Assistant panel (right sidebar)
# MAGIC 2. Toggle to **Agent** mode
# MAGIC 3. Enter your prompt referencing `@{TABLE}`
# MAGIC 4. Review and approve the Agent's plan
# MAGIC 5. Allow code execution when prompted

# COMMAND ----------

# Agent-generated code will appear below
# ----------------------------------------


# COMMAND ----------



# COMMAND ----------



# COMMAND ----------



# COMMAND ----------

# MAGIC %md
# MAGIC ## Export Results
# MAGIC
# MAGIC After the Agent completes analysis, export results to a Delta table.

# COMMAND ----------

# Uncomment and modify to export Agent results
# OUTPUT_TABLE = f"{CATALOG}.{SCHEMA}.agent_analysis_{TABLE}"
#
# # If Agent created a results DataFrame, save it
# # results_df.write.mode("overwrite").saveAsTable(OUTPUT_TABLE)
# print(f"Results exported to: {OUTPUT_TABLE}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Sync to MCP Jobs (Optional)
# MAGIC
# MAGIC Push analysis metadata to MCP Jobs for downstream processing.

# COMMAND ----------

# Uncomment to sync with MCP Jobs
# import requests
#
# MCP_JOBS_URL = "https://v0-open-in-v0-aw4uzb0sw-tbwa.vercel.app/api/jobs/enqueue"
#
# response = requests.post(MCP_JOBS_URL, json={
#     "source": "databricks",
#     "jobType": "analytics_complete",
#     "payload": {
#         "notebook": dbutils.notebook.entry_point.getDbutils().notebook().getContext().notebookPath().get(),
#         "table": TABLE_PATH,
#         "timestamp": str(spark.sql("SELECT current_timestamp()").collect()[0][0])
#     }
# })
#
# print(f"MCP Job enqueued: {response.json()}")
