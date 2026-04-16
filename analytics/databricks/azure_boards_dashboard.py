# Databricks notebook source
# MAGIC %md
# MAGIC # Azure Boards Dashboard — IPAI Platform
# MAGIC
# MAGIC Live dashboard from Azure DevOps Analytics OData.
# MAGIC Org: `insightpulseai` | Project: `ipai-platform`

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. Load data from ADO Analytics OData

# COMMAND ----------

import requests
import pandas as pd
from datetime import datetime

ADO_ORG = "insightpulseai"
ADO_PROJECT = "ipai-platform"
ODATA_BASE = f"https://analytics.dev.azure.com/{ADO_ORG}/{ADO_PROJECT}/_odata/v4.0-preview"

# Auth: use PAT from dbutils secrets or env var
# For dev: set AZURE_DEVOPS_PAT in cluster env vars or Databricks secrets
try:
    pat = dbutils.secrets.get(scope="ipai-secrets", key="azure-devops-pat")
except Exception:
    import os
    pat = os.environ.get("AZURE_DEVOPS_PAT", "")

if not pat:
    raise ValueError("Set AZURE_DEVOPS_PAT in cluster env vars or Databricks secrets scope 'ipai-secrets'")

headers = {"Authorization": f"Basic {__import__('base64').b64encode(f':{pat}'.encode()).decode()}"}

# COMMAND ----------

# Fetch work items
wi_url = (
    f"{ODATA_BASE}/WorkItems?"
    "$select=WorkItemId,Title,WorkItemType,State,IterationPath,AreaPath,Priority,Tags,CreatedDate,ChangedDate"
    "&$filter=State ne 'Removed'"
    "&$top=500"
)
wi_resp = requests.get(wi_url, headers=headers)
wi_resp.raise_for_status()
wi_data = wi_resp.json().get("value", [])
df_wi = pd.DataFrame(wi_data)

# Parse iteration name from path
df_wi["Iteration"] = df_wi["IterationPath"].apply(
    lambda p: p.split("\\")[-1] if "\\" in str(p) else "Unassigned"
)
df_wi["CreatedDate"] = pd.to_datetime(df_wi["CreatedDate"])
df_wi["ChangedDate"] = pd.to_datetime(df_wi["ChangedDate"])

print(f"Loaded {len(df_wi)} work items")
df_wi.head()

# COMMAND ----------

# Fetch iterations
iter_url = (
    f"{ODATA_BASE}/Iterations?"
    "$select=IterationId,IterationName,IterationPath,StartDate,EndDate,IsCurrentIteration"
)
iter_resp = requests.get(iter_url, headers=headers)
iter_resp.raise_for_status()
iter_data = iter_resp.json().get("value", [])
df_iter = pd.DataFrame(iter_data)

if not df_iter.empty:
    df_iter["StartDate"] = pd.to_datetime(df_iter["StartDate"])
    df_iter["EndDate"] = pd.to_datetime(df_iter["EndDate"])

print(f"Loaded {len(df_iter)} iterations")
df_iter

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Save to Unity Catalog (governed table)

# COMMAND ----------

# Convert to Spark DataFrames and save as UC tables
spark_wi = spark.createDataFrame(df_wi)
spark_wi.write.mode("overwrite").saveAsTable("ipai_dev.bronze.ado_work_items")

if not df_iter.empty:
    spark_iter = spark.createDataFrame(df_iter)
    spark_iter.write.mode("overwrite").saveAsTable("ipai_dev.bronze.ado_iterations")

print("Saved to ipai_dev.bronze.ado_work_items + ado_iterations")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. Summary KPIs

# COMMAND ----------

total = len(df_wi)
by_state = df_wi["State"].value_counts().to_dict()
by_type = df_wi["WorkItemType"].value_counts().to_dict()
by_iter = df_wi["Iteration"].value_counts().to_dict()

print(f"""
╔══════════════════════════════════════════╗
║   IPAI Platform — Azure Boards Summary   ║
╠══════════════════════════════════════════╣
║  Total Work Items:  {total:<20} ║
║  To Do:             {by_state.get('To Do', 0):<20} ║
║  Doing:             {by_state.get('Doing', 0):<20} ║
║  Done:              {by_state.get('Done', 0):<20} ║
╠══════════════════════════════════════════╣
║  Epics:             {by_type.get('Epic', 0):<20} ║
║  Issues:            {by_type.get('Issue', 0):<20} ║
║  Tasks:             {by_type.get('Task', 0):<20} ║
║  Bugs:              {by_type.get('Bug', 0):<20} ║
╠══════════════════════════════════════════╣
║  By Iteration:                           ║""")
for it, count in sorted(by_iter.items()):
    print(f"║    {it:<28} {count:<5}  ║")
print("╚══════════════════════════════════════════╝")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. Visualizations

# COMMAND ----------

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# -- Work items by State --
fig_state = px.pie(
    df_wi, names="State",
    title="Work Items by State",
    color_discrete_sequence=px.colors.qualitative.Set2,
    hole=0.4
)
fig_state.show()

# COMMAND ----------

# -- Work items by Iteration × State --
iter_order = ["R1-Foundation-30d", "R2-Core-Execution-60d", "R3-PH-Ops-Hardening-90d", "R4-GA", "Sprint 1", "Unassigned", "ipai-platform"]
cross = df_wi.groupby(["Iteration", "State"]).size().reset_index(name="Count")

fig_iter = px.bar(
    cross, x="Iteration", y="Count", color="State",
    title="Work Items by Iteration × State",
    category_orders={"Iteration": iter_order},
    color_discrete_sequence=px.colors.qualitative.Set2,
    barmode="stack"
)
fig_iter.update_layout(xaxis_tickangle=-30)
fig_iter.show()

# COMMAND ----------

# -- Work items by Type --
fig_type = px.bar(
    df_wi, x="WorkItemType",
    title="Work Items by Type",
    color="WorkItemType",
    color_discrete_sequence=px.colors.qualitative.Pastel
)
fig_type.update_layout(showlegend=False)
fig_type.show()

# COMMAND ----------

# -- Priority distribution --
df_wi["PriorityLabel"] = df_wi["Priority"].map({1: "P1 Critical", 2: "P2 High", 3: "P3 Medium", 4: "P4 Low"}).fillna("Unset")
fig_pri = px.histogram(
    df_wi, x="PriorityLabel",
    title="Work Items by Priority",
    color="PriorityLabel",
    category_orders={"PriorityLabel": ["P1 Critical", "P2 High", "P3 Medium", "P4 Low", "Unset"]}
)
fig_pri.update_layout(showlegend=False)
fig_pri.show()

# COMMAND ----------

# -- Timeline: Iterations gantt --
if not df_iter.empty:
    gantt_data = df_iter[df_iter["StartDate"].notna()].copy()
    if not gantt_data.empty:
        today_line = datetime.now()
        fig_gantt = px.timeline(
            gantt_data,
            x_start="StartDate", x_end="EndDate",
            y="IterationName",
            title="Release Timeline (R1 → R4)",
            color="IterationName",
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        fig_gantt.add_vline(x=today_line, line_dash="dash", line_color="red", annotation_text="Today")
        fig_gantt.update_yaxes(autorange="reversed")
        fig_gantt.show()

# COMMAND ----------

# -- Tag cloud (top 20 tags) --
all_tags = df_wi["Tags"].dropna().str.split("; ").explode()
tag_counts = all_tags.value_counts().head(20).reset_index()
tag_counts.columns = ["Tag", "Count"]

fig_tags = px.bar(
    tag_counts, x="Count", y="Tag", orientation="h",
    title="Top 20 Tags",
    color="Count",
    color_continuous_scale="Tealgrn"
)
fig_tags.update_layout(yaxis=dict(autorange="reversed"))
fig_tags.show()

# COMMAND ----------

# MAGIC %md
# MAGIC ## 5. Publish as Dashboard
# MAGIC
# MAGIC To convert this notebook into a Databricks Dashboard:
# MAGIC 1. Click the **kebab menu (⋮)** at the top right of this notebook
# MAGIC 2. Select **Create Dashboard from Notebook**
# MAGIC 3. Databricks auto-converts the plotly charts into dashboard tiles
# MAGIC 4. Share the dashboard URL with stakeholders
# MAGIC
# MAGIC Or create a SQL Dashboard manually using the UC tables:
# MAGIC ```sql
# MAGIC SELECT * FROM ipai_dev.bronze.ado_work_items
# MAGIC SELECT * FROM ipai_dev.bronze.ado_iterations
# MAGIC ```
