# Examples — databricks-model-serving-production-readiness

## Example 1: Demand forecasting model (PASS)

**Input**: MLflow model registered in Unity Catalog with training data lineage. Staging validation: RMSE < 0.05 on holdout set. Serving endpoint: provisioned throughput, P95 latency < 200ms, autoscaling 2-8 instances. Token-based auth, private endpoint. A/B serving enabled with 90/10 traffic split for new versions. Drift monitoring via Databricks Lakehouse Monitoring. Governance: approval by ML lead, audit trail in Unity Catalog, PII-free compliance tag.

**Output**:
- Readiness: PRODUCTION-READY
- All dimensions PASS
- Governance: COMPLIANT — approval trail complete
- SLA feasibility: Achievable — P95 < 200ms with provisioned throughput
- No blocking gaps

## Example 2: Classification model without drift monitoring (CONDITIONALLY-READY)

**Input**: Model in Unity Catalog. Staging validation passed. Serving endpoint with autoscaling. Token auth. No traffic splitting. No drift monitoring configured. Governance approval exists but no compliance tags.

**Output**:
- Readiness: CONDITIONALLY-READY
- Blocking gaps:
  - No drift monitoring — must configure Lakehouse Monitoring or equivalent
  - No traffic splitting — must enable A/B serving for safe rollout
- Advisory gaps:
  - Missing compliance tags — add data classification and PII tags
- Governance: PARTIAL — approval exists but tagging incomplete
- Remediation: Enable Lakehouse Monitoring for data drift. Configure A/B serving. Add compliance tags to model in Unity Catalog.

## Example 3: Model deployed direct-to-prod (NOT-READY)

**Input**: Model trained in notebook, pushed directly to production serving endpoint. Not registered in Unity Catalog. No staging environment. No governance approval. Public endpoint with no rate limiting. No monitoring.

**Output**:
- Readiness: NOT-READY
- Blocking gaps:
  - Model not registered in Unity Catalog — no lineage or versioning
  - No staging validation — direct-to-prod deployment
  - No governance approval — no audit trail
  - No endpoint security — public with no rate limiting
  - No monitoring — no latency, error, or drift tracking
- Remediation: Register model in Unity Catalog with lineage. Create staging environment and validation pipeline. Implement governance approval workflow. Add endpoint auth and rate limiting. Configure monitoring dashboards.
