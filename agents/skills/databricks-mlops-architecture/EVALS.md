# databricks-mlops-architecture — Evaluation Criteria

## Accuracy (target: 0.95)
- Architecture design correctly maps to Databricks capabilities (Jobs, Workflows, Model Serving, MLflow)
- Promotion gates reference appropriate metrics for the model type
- Serving configuration matches the stated requirements (batch, real-time, or both)

## Completeness (target: 0.95)
- All six areas covered: training orchestration, promotion gates, batch/real-time serving, model lifecycle, Git integration, monitoring
- No critical architecture component omitted
- Edge cases addressed (retraining triggers, rollback, cold start)

## Safety (target: 0.99)
- No designs that rely on manual notebook execution for production workloads
- No promotion paths that skip staging
- No serving configurations without rollback capability
- No architectures without monitoring and alerting

## Policy Adherence (target: 0.99)
- All pipeline code is Git-backed
- Promotion gates exist at every environment boundary
- Model artifacts are versioned and registered
- Cost and resource attribution is considered
- Databricks production-readiness guardrail is respected (GA/stable features only for production baseline)

## Failure Modes
| Mode | Detection | Mitigation |
|------|-----------|------------|
| Over-engineered design | Excessive components for simple workload | Match complexity to workload size |
| Missing promotion gate | No criteria between environments | Require explicit gate spec |
| No rollback path | Serving has no version revert | Require rollback definition |
| Ad-hoc execution | Notebook runs instead of Jobs | Reject non-codified pipelines |
