# databricks-mlops-architecture — Checklist

## Training Orchestration
- [ ] Training pipeline uses Databricks Jobs/Workflows (not manual notebook runs)
- [ ] All pipeline code is Git-backed via Repos integration
- [ ] Data preparation, training, and evaluation are separate workflow tasks
- [ ] Task dependencies and retry policies are defined
- [ ] Compute cluster configuration is specified (autoscaling, instance types)

## Promotion Gates
- [ ] Dev -> Staging gate criteria defined (metric thresholds, test results)
- [ ] Staging -> Production gate criteria defined (validation period, business sign-off)
- [ ] Promotion is automated or semi-automated (not purely manual)
- [ ] Gate failures block promotion with clear diagnostics

## Model Registry
- [ ] Models registered in MLflow Model Registry or Unity Catalog
- [ ] Version numbering and stage transitions are tracked
- [ ] Model lineage (training data, parameters, metrics) is recorded
- [ ] Model artifacts are versioned and reproducible

## Serving
- [ ] Batch scoring: scheduled Jobs write to governed Delta tables
- [ ] Real-time serving: Model Serving endpoints configured with traffic splitting
- [ ] SLA defined for each serving mode (latency, throughput, availability)
- [ ] Rollback path defined (revert to previous model version)

## Monitoring
- [ ] Training pipeline health monitored (success/failure, duration, cost)
- [ ] Model performance monitored (accuracy drift, prediction distribution)
- [ ] Serving health monitored (latency, throughput, error rate)
- [ ] Alerting configured for all critical thresholds
- [ ] Data drift detection configured (feature distribution monitoring)

## Lifecycle Management
- [ ] Automated retraining triggers defined (schedule or drift-based)
- [ ] Model retirement criteria defined
- [ ] Cost attribution per model/pipeline is tracked
- [ ] Documentation covers the full lifecycle from training to retirement
