---
name: databricks-compute-jobs-ops
description: Manage Databricks compute resources and job execution via CLI
microsoft_capability_family: "Azure / Databricks"
---

# Databricks Compute & Jobs Ops Skill

## Purpose

Manage Databricks compute resources and job execution via the Databricks CLI (v0.205+).
Covers clusters create/start/stop/delete, cluster policies, instance pools, jobs create/run/list, and pipelines.

## Owner

databricks-cli-operator

## Preconditions

- Databricks CLI v0.205+ installed
- Authentication configured (profile or environment variables)
- Appropriate permissions for compute and job management

## Covered Operations

### Clusters

- `databricks clusters list` — list all clusters
- `databricks clusters get --cluster-id <id>` — get cluster details
- `databricks clusters create --json <spec>` — create cluster from JSON spec
- `databricks clusters start --cluster-id <id>` — start terminated cluster
- `databricks clusters restart --cluster-id <id>` — restart running cluster
- `databricks clusters delete --cluster-id <id>` — permanently delete cluster (destructive)
- `databricks clusters permanent-delete --cluster-id <id>` — hard delete

### Cluster Policies

- `databricks cluster-policies list` — list policies
- `databricks cluster-policies get --cluster-policy-id <id>` — get policy details
- `databricks cluster-policies create --json <spec>` — create policy

### Instance Pools

- `databricks instance-pools list` — list pools
- `databricks instance-pools get --instance-pool-id <id>` — get pool details
- `databricks instance-pools create --json <spec>` — create pool

### Jobs

- `databricks jobs list` — list all jobs
- `databricks jobs get --job-id <id>` — get job details
- `databricks jobs create --json <spec>` — create job from JSON spec
- `databricks jobs run-now --job-id <id>` — trigger job run
- `databricks jobs delete --job-id <id>` — delete job (destructive)
- `databricks runs list --job-id <id>` — list runs for a job
- `databricks runs get --run-id <id>` — get run details
- `databricks runs cancel --run-id <id>` — cancel running job

### Pipelines (Delta Live Tables / Spark Declarative Pipelines)

- `databricks pipelines list` — list pipelines
- `databricks pipelines get --pipeline-id <id>` — get pipeline details
- `databricks pipelines create --json <spec>` — create pipeline
- `databricks pipelines start --pipeline-id <id>` — start pipeline update
- `databricks pipelines stop --pipeline-id <id>` — stop pipeline
- `databricks pipelines delete --pipeline-id <id>` — delete pipeline (destructive)

## Disallowed Operations

- Interactive cluster terminal access (requires Databricks UI)
- Direct notebook execution (use Jobs API)
- Workspace artifact management (use databricks-workspace-ops)

## Output Contract

- All commands use `--output json`
- Cluster list returns array with `cluster_id`, `cluster_name`, `state`
- Job runs return `run_id`, `state.life_cycle_state`, `state.result_state`
- Pipeline updates return `update_id`, `state`

## Verification

- After cluster create: poll `clusters get` until state is `RUNNING`
- After job run-now: poll `runs get` until `life_cycle_state` is `TERMINATED` and check `result_state`
- After pipeline start: poll `pipelines get` until state is `IDLE` (completed)
