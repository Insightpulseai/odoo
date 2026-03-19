# Identity & SQL Policy

## Authentication Rules

- Use profiles for multi-workspace environments
- Environment variables for CI/CD (DATABRICKS_HOST, DATABRICKS_TOKEN)
- Service principals for automated/non-interactive operations
- Never store tokens in version control
- Rotate tokens per organizational policy

## Identity Management Rules

- User creation follows least-privilege principle
- Groups map to organizational roles (data-engineers, analysts, admins)
- Service principals for each automated system (CI, orchestration, monitoring)
- User/SP deletion is destructive — verify no active sessions or jobs before removal
- Group deletion cascades permission removal — audit group membership first

## SQL Warehouse Rules

- Auto-stop must be enabled (default: 30 minutes)
- Warehouse sizing should match workload (2X-Small for dev, larger for production)
- Serverless compute preference when available and cost-effective
- Pro warehouse type for production (better concurrency and optimization)
- Monitor warehouse utilization — stop idle warehouses

## Destructive Operation Guards

- User/group/SP deletion requires confirmation
- Warehouse deletion requires confirmation — check for active queries first
- Never delete the last admin user or admin group

## Cost Controls

- Auto-stop on all warehouses
- Minimum cluster count of 1 for non-production
- Monitor SQL warehouse compute hours
- Use spot instances for development warehouses where available
