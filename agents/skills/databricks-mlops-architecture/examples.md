# databricks-mlops-architecture — Examples

## Example 1: Churn Prediction MLOps Pipeline

**Input**: Design MLOps for a customer churn prediction model. Training data is 10M rows in Delta Lake. Model serves batch predictions daily and real-time predictions via API.

**Output**:

Architecture:
- Training: Databricks Job with 3 tasks (feature_engineering -> train_model -> evaluate)
- Batch serving: Scheduled Job runs daily, writes predictions to `gold.churn_predictions`
- Real-time serving: Model Serving endpoint with 2 model versions (champion/challenger)
- Registry: Unity Catalog model `ml.churn.churn_predictor`

Promotion gates:
- Dev -> Staging: AUC >= 0.82, all unit tests pass, data validation checks pass
- Staging -> Production: Shadow mode for 7 days, prediction distribution within 2 sigma of baseline

Monitoring:
- Training: job duration, feature drift (PSI), model metric trends
- Serving: p99 latency < 200ms, error rate < 0.1%, daily prediction volume within expected range

---

## Example 2: Recommendation Engine Orchestration

**Input**: Design MLOps for a product recommendation engine. Collaborative filtering + content-based hybrid. Batch retraining weekly, real-time serving required.

**Output**:

Architecture:
- Training: Weekly Job workflow (extract_interactions -> compute_embeddings -> train_cf -> train_cb -> ensemble -> evaluate)
- Feature store: Databricks Feature Store for user/item features
- Serving: Model Serving with feature lookup, traffic split 90/10 for A/B testing
- Registry: MLflow Model Registry with staging/production stages

Promotion gates:
- Dev -> Staging: NDCG@10 >= 0.35, coverage >= 40%, no cold-start regression
- Staging -> Production: A/B test significance p < 0.05 on click-through rate

Monitoring:
- Feature freshness: alert if feature store not updated within 24h
- Model quality: daily NDCG computation on holdout, alert on 5% degradation
- Serving: endpoint latency, throughput, error codes
