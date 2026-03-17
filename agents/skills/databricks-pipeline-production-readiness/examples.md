# Examples — databricks-pipeline-production-readiness

## Example 1: Batch ingestion pipeline (PASS)

**Input**: DLT pipeline defined in YAML, ingesting daily sales data from Azure SQL to Delta Lake. Jobs workflow scheduled at 02:00 UTC with 3 retries. Event log enabled, Slack alerting on failure. Dev/staging/prod workspaces separated. Delta table versioning for rollback. SLA: data available by 06:00 UTC.

**Output**:
- Pipeline type: Batch
- Readiness: PRODUCTION-READY
- All dimensions PASS
- Evidence: DLT YAML artifact, Jobs workflow config, event log screenshot, alerting config, workspace separation proof
- No blocking gaps

## Example 2: Streaming pipeline with missing observability (CONDITIONALLY-READY)

**Input**: Spark Structured Streaming pipeline reading from Event Hubs, writing to Delta Lake. Defined in notebook but orchestrated via Jobs. No alerting configured. Checkpoints enabled. Dev and prod share same workspace with catalog separation.

**Output**:
- Pipeline type: Streaming
- Readiness: CONDITIONALLY-READY
- Blocking gaps:
  - Alerting not configured — must add failure and SLA breach alerts
  - No metrics dashboard — must configure latency and throughput monitoring
- Advisory gaps:
  - Workspace separation preferred over catalog-only separation
  - Pipeline definition should migrate from notebook to SDP YAML for maintainability
- Remediation: Configure alerting via Jobs notification settings, create monitoring dashboard in Databricks SQL

## Example 3: CDC pipeline on Private Preview feature (NOT-READY)

**Input**: Change Data Capture pipeline using a Databricks feature currently in Private Preview. No SLA defined. Manual notebook execution. No environment separation.

**Output**:
- Pipeline type: CDC
- Readiness: NOT-READY
- Blocking gaps:
  - Feature in Private Preview — not acceptable as canonical production baseline per doctrine
  - No SLA defined
  - Manual notebook execution — not production-ready orchestration
  - No environment separation
- Remediation: Wait for GA or stable Public Preview. Define SLA. Migrate to Jobs workflow. Separate environments.
