# Notion x Finance PPM Runbook

## Quick Reference

### Service URLs

| Service | URL | Purpose |
|---------|-----|---------|
| Control Room | https://ppm.internal | Dashboard |
| Databricks | https://adb-xxx.azuredatabricks.net | Workspace |
| Notion | https://notion.so/workspace | Source data |

### Common Commands

```bash
# Verify all components
./scripts/ppm/verify-all.sh

# Deploy Databricks jobs
./scripts/ppm/deploy-databricks.sh prod

# Run data quality checks
./scripts/ppm/run-dq-checks.sh

# Start Control Room locally
cd apps/control-room && npm run dev
```

## Incident Response

### P1: Control Room Down

**Symptoms**: Dashboard returns 500 errors or is unreachable

**Steps**:
1. Check App Service health
   ```bash
   az webapp show --name notion-ppm-controlroom --query state
   ```
2. Check application logs
   ```bash
   az webapp log tail --name notion-ppm-controlroom
   ```
3. Verify Databricks SQL warehouse is running
4. Check environment variables are set correctly
5. Restart application if needed
   ```bash
   az webapp restart --name notion-ppm-controlroom
   ```

### P2: Sync Job Failure

**Symptoms**: Data is stale (> 30 minutes old)

**Steps**:
1. Check job run status in Databricks
   ```bash
   databricks jobs list --output json | jq '.jobs[] | {name, job_id}'
   databricks runs list --job-id <JOB_ID> --limit 5
   ```
2. View job run logs
   ```bash
   databricks runs get-output --run-id <RUN_ID>
   ```
3. Common issues:
   - **Notion API rate limit**: Wait 1 minute, retry
   - **Invalid token**: Regenerate Notion integration token
   - **Schema change**: Update column mapping in `notion_mapping.yaml`
4. Manual sync trigger
   ```bash
   databricks jobs run-now --job-id <NOTION_SYNC_JOB_ID>
   ```

### P3: Data Quality Issues

**Symptoms**: DQ score drops below 95%

**Steps**:
1. Query DQ issues table
   ```sql
   SELECT * FROM ppm_gold.dq_issues
   WHERE detected_at > current_timestamp() - INTERVAL 24 HOURS
   ORDER BY severity DESC
   ```
2. Common issues:
   - **Null values**: Check Notion database for missing fields
   - **Orphan records**: Verify relation properties are intact
   - **Invalid values**: Update validation rules or fix source data
3. After fixing, trigger DQ job
   ```bash
   databricks jobs run-now --job-id <DQ_CHECKS_JOB_ID>
   ```

### P4: Slow Dashboard

**Symptoms**: Pages take > 5 seconds to load

**Steps**:
1. Check SQL warehouse query performance
   ```sql
   SELECT * FROM system.query.history
   WHERE start_time > current_timestamp() - INTERVAL 1 HOUR
   ORDER BY duration_ms DESC
   LIMIT 10
   ```
2. Optimize slow queries:
   - Add table statistics: `ANALYZE TABLE ppm_gold.xxx COMPUTE STATISTICS`
   - Review Z-ordering: `OPTIMIZE ppm_gold.xxx ZORDER BY (id)`
3. Scale up SQL warehouse if needed
4. Check for missing indexes or partitions

## Regular Operations

### Daily Checks

```bash
#!/bin/bash
# Morning check script

echo "=== Job Status ==="
databricks jobs list --output json | jq '.jobs[] | {name, job_id}'

echo "=== Recent Runs ==="
databricks runs list --limit 10 --output json | jq '.runs[] | {run_id, state, start_time}'

echo "=== Data Freshness ==="
# Query from Control Room API
curl -s https://ppm.internal/api/kpis | jq '.freshness_minutes'
```

### Weekly Maintenance

1. **Review DQ trends**
   ```sql
   SELECT DATE(checked_at), AVG(dq_score) as avg_score
   FROM ppm_gold.control_room_status
   WHERE checked_at > current_date() - INTERVAL 7 DAYS
   GROUP BY 1 ORDER BY 1
   ```

2. **Check table sizes**
   ```sql
   DESCRIBE DETAIL ppm_bronze.notion_programs;
   DESCRIBE DETAIL ppm_silver.programs;
   ```

3. **Vacuum old files**
   ```sql
   VACUUM ppm_bronze.notion_programs RETAIN 168 HOURS;
   VACUUM ppm_silver.programs RETAIN 168 HOURS;
   ```

### Monthly Tasks

1. **Rotate Notion token**
   - Generate new integration token in Notion
   - Update Databricks secret scope
   - Update Control Room environment

2. **Review access permissions**
   - Audit Notion integration access
   - Review Databricks group memberships

3. **Performance tuning**
   - Analyze query patterns
   - Optimize frequently accessed tables
   - Review cluster sizing

## Configuration Changes

### Adding a New Notion Database

1. Create database in Notion with required properties
2. Grant integration access to the database
3. Add mapping to `config/notion_mapping.yaml`:
   ```yaml
   new_database:
     database_id: "${NOTION_NEW_DB}"
     columns:
       - notion_property: "Name"
         column_name: "name"
         column_type: "STRING"
   ```
4. Add Pydantic model to `models.py`
5. Update DAB jobs to include new database
6. Deploy changes

### Modifying Sync Schedule

1. Update `resources/jobs.yml`:
   ```yaml
   schedule:
     quartz_cron_expression: "0 */30 * * * ?"  # Every 30 min
     timezone_id: UTC
   ```
2. Deploy DAB bundle
   ```bash
   databricks bundle deploy -t prod
   ```

### Adding New KPI

1. Create gold table with aggregation logic
2. Add API route in Control Room:
   ```typescript
   // src/app/api/kpis/new-metric/route.ts
   export async function GET() {
     const result = await queryDatabricks('SELECT ... FROM ppm_gold.new_metric');
     return Response.json(result);
   }
   ```
3. Add component to dashboard
4. Deploy Control Room

## Disaster Recovery

### Backup Locations

| Data | Backup Method | Retention |
|------|---------------|-----------|
| Delta tables | Time travel | 30 days |
| Notion data | Notion export | Manual |
| Config files | Git repository | Permanent |
| Secrets | Key Vault backup | 90 days |

### Recovery Procedures

**Restore Delta Table**:
```sql
-- View table history
DESCRIBE HISTORY ppm_silver.programs;

-- Restore to previous version
RESTORE TABLE ppm_silver.programs TO VERSION AS OF 42;

-- Or restore to timestamp
RESTORE TABLE ppm_silver.programs TO TIMESTAMP AS OF '2024-01-01 00:00:00';
```

**Full Resync from Notion**:
```bash
# Clear watermarks to trigger full sync
databricks fs rm dbfs:/ppm/watermarks/ -r

# Run sync job
databricks jobs run-now --job-id <NOTION_SYNC_JOB_ID>
```

## Contacts

| Role | Contact | Escalation |
|------|---------|------------|
| On-call | ppm-oncall@company.com | PagerDuty |
| Data Engineering | data-eng@company.com | Slack #data-eng |
| Platform | platform@company.com | Slack #platform |
