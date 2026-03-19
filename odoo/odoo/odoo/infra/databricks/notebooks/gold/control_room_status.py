# Databricks notebook source
# MAGIC %md
# MAGIC # Control Room Status
# MAGIC
# MAGIC Collects job run metadata and pipeline health for Control Room dashboard.

# COMMAND ----------

import json
from datetime import datetime, timedelta
from pyspark.sql.functions import col, lit, current_timestamp
from databricks.sdk import WorkspaceClient

# COMMAND ----------

CATALOG = spark.conf.get("spark.databricks.catalog", "ppm")
GOLD_SCHEMA = "gold"

# Initialize Databricks client
w = WorkspaceClient()

# COMMAND ----------

# Get all jobs tagged with our bundle
our_jobs = []

for job in w.jobs.list():
    tags = job.settings.tags if job.settings and job.settings.tags else {}
    if tags.get("team") == "platform" or "notion" in job.settings.name.lower() or "ppm" in job.settings.name.lower():
        our_jobs.append(job)

print(f"Found {len(our_jobs)} jobs to track")

# COMMAND ----------

# Collect job status
job_records = []

for job in our_jobs:
    job_id = str(job.job_id)

    # Get latest runs
    runs = list(w.jobs.list_runs(job_id=job.job_id, limit=10))

    last_run = runs[0] if runs else None
    last_success = next((r for r in runs if r.state and r.state.result_state and r.state.result_state.value == "SUCCESS"), None)

    job_record = {
        "job_id": job_id,
        "job_name": job.settings.name,
        "job_type": (job.settings.tags or {}).get("layer", "unknown"),
        "last_run_status": last_run.state.result_state.value if last_run and last_run.state and last_run.state.result_state else "PENDING",
        "last_run_time": datetime.fromtimestamp(last_run.start_time / 1000) if last_run and last_run.start_time else None,
        "last_run_duration_seconds": int((last_run.end_time - last_run.start_time) / 1000) if last_run and last_run.end_time else None,
        "last_success_time": datetime.fromtimestamp(last_success.start_time / 1000) if last_success and last_success.start_time else None,
        "next_run_time": None,  # Would need schedule parsing
        "schedule": job.settings.schedule.quartz_cron_expression if job.settings and job.settings.schedule else None,
    }

    job_records.append(job_record)
    print(f"  {job.settings.name}: {job_record['last_run_status']}")

# COMMAND ----------

# Create DataFrame
if job_records:
    jobs_df = spark.createDataFrame(job_records)
    jobs_df = jobs_df.withColumn("last_sync_time", current_timestamp())

    jobs_df.show(truncate=False)

    # Write to gold table
    gold_table = f"{CATALOG}.{GOLD_SCHEMA}.control_room_status"

    jobs_df.write \
        .format("delta") \
        .mode("overwrite") \
        .option("overwriteSchema", "true") \
        .saveAsTable(gold_table)

    print(f"Written {len(job_records)} job records to {gold_table}")

# COMMAND ----------

# Collect job run history
run_records = []

for job in our_jobs[:10]:  # Limit to first 10 jobs for performance
    runs = list(w.jobs.list_runs(job_id=job.job_id, limit=20))

    for run in runs:
        run_record = {
            "run_id": str(run.run_id),
            "job_id": str(job.job_id),
            "job_name": job.settings.name,
            "status": run.state.result_state.value if run.state and run.state.result_state else "RUNNING",
            "start_time": datetime.fromtimestamp(run.start_time / 1000) if run.start_time else None,
            "end_time": datetime.fromtimestamp(run.end_time / 1000) if run.end_time else None,
            "duration_seconds": int((run.end_time - run.start_time) / 1000) if run.end_time else None,
            "error_message": run.state.state_message if run.state else None,
            "triggered_by": run.trigger.value if run.trigger else "UNKNOWN",
        }
        run_records.append(run_record)

# COMMAND ----------

if run_records:
    runs_df = spark.createDataFrame(run_records)

    runs_table = f"{CATALOG}.{GOLD_SCHEMA}.control_room_status_runs"

    runs_df.write \
        .format("delta") \
        .mode("overwrite") \
        .option("overwriteSchema", "true") \
        .saveAsTable(runs_table)

    print(f"Written {len(run_records)} run records to {runs_table}")

# COMMAND ----------

# Calculate summary metrics
total_jobs = len(job_records)
success_jobs = len([j for j in job_records if j["last_run_status"] == "SUCCESS"])
failed_jobs = len([j for j in job_records if j["last_run_status"] == "FAILED"])
running_jobs = len([j for j in job_records if j["last_run_status"] == "RUNNING"])

overall_status = "healthy"
if failed_jobs > 0:
    overall_status = "degraded"
if failed_jobs > total_jobs / 2:
    overall_status = "unhealthy"

summary = {
    "total_jobs": total_jobs,
    "successful_jobs": success_jobs,
    "failed_jobs": failed_jobs,
    "running_jobs": running_jobs,
    "overall_status": overall_status,
    "timestamp": datetime.utcnow().isoformat()
}

print(f"\nSummary: {summary}")

# COMMAND ----------

dbutils.notebook.exit(json.dumps(summary))
