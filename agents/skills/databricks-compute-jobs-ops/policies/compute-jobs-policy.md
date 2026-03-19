# Compute & Jobs Policy

## Cluster Lifecycle Rules

- Prefer job clusters (ephemeral) over all-purpose clusters for production workloads
- All-purpose clusters are for development and ad-hoc exploration only
- Cluster auto-termination must be configured (default: 120 minutes idle)
- Use cluster policies to enforce node type and autoscaling limits
- Never create clusters without auto-termination in production

## Job Execution Rules

- Jobs must be defined as JSON specs, not created interactively
- Job specs should be version-controlled in the repo
- Production jobs must have email/webhook notifications configured
- Job retry policies should be explicitly set (not relying on defaults)
- Cancel running jobs before deleting job definitions

## Pipeline Rules

- Pipelines follow Spark Declarative Pipelines (SDP) pattern
- Pipeline specs are code — version-controlled, not UI-created
- Development mode for testing, production mode for production runs
- Data quality expectations must be defined in pipeline code

## Destructive Operation Guards

- `clusters delete` terminates and removes — confirm cluster is not running critical workloads
- `jobs delete` removes job definition — cancel active runs first
- `pipelines delete` removes pipeline — stop active updates first
- All destructive operations require explicit confirmation

## Cost Controls

- Monitor cluster usage via `clusters list` — terminate idle clusters
- Use spot/preemptible instances for non-critical workloads
- Set max workers in autoscaling policies
