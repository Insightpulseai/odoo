---
name: azure-data-scientist
description: >
  Azure Data Scientist Associate (DP-100) grounded skill. Covers ML solution design,
  data exploration, model training, AutoML, hyperparameter tuning, model deployment,
  MLflow, and responsible AI dashboards. Use when working with Databricks ML, model
  serving, evaluation pipelines, or gold mart analytics.
  Triggers on: DP-100, Azure ML, Databricks ML, model serving, MLflow, AutoML,
  hyperparameter tuning, model evaluation, gold marts, DLT pipeline.
version: "1.0.0"
updated: "2026-04-18"
scope: repo
certification_source: "DP-100: Microsoft Azure Data Scientist Associate"
learn_path: "https://learn.microsoft.com/en-us/credentials/certifications/azure-data-scientist/"
feeds_scoring: "Solutions Partner Data & AI — Skilling metric (+4 pts)"
---

# Azure Data Scientist Associate (DP-100) — Agent Skill

You are grounded in the DP-100 certification knowledge domain. Use `mcp__microsoft-learn__microsoft_docs_search` for real-time grounding.

## When to activate

- Working with Databricks workspace (`dbw-ipai-dev`) or Unity Catalog
- Managing model serving endpoints (11 endpoints: Llama 4, Qwen3, gpt-4.1-mini)
- Building or reviewing DLT pipelines (Bronze → Silver → Gold)
- Evaluating model quality or agent performance metrics
- Working with MLflow experiment tracking or model registry
- Designing gold mart analytics or Genie space queries

## Knowledge domains (DP-100 exam skills)

### 1. Design and prepare an ML solution (20-25%)
- Determine appropriate compute for training (GPU, CPU, Spark)
- Design data management solutions (datasets, datastores, feature stores)
- Design model training solutions (pipelines, experiments)

**IPAI mapping:**
| Component | IPAI Resource | Use |
|---|---|---|
| Workspace | `dbw-ipai-dev` (Premium, Unity Catalog) | ML workspace |
| Compute | Databricks clusters (on-demand) | Training + serving |
| Data | `stipaidevlake` (ADLS Gen2) | Feature store + training data |
| Feature engineering | Gold mart views (6 views, 103 bronze rows) | Pre-computed features |
| Pipeline | DLT (Bronze → Silver → Gold) | Data preparation |

### 2. Explore data and train models (35-40%)
- Perform EDA with Spark DataFrames
- Train models using scikit-learn, PyTorch, or AutoML
- Tune hyperparameters (grid search, Bayesian, early stopping)
- Use MLflow for experiment tracking

**IPAI mapping:**
- Lakehouse Federation (`odoo_erp` foreign catalog) provides zero-copy PG read
- Gold views serve as pre-computed analytical features
- Databricks notebooks for EDA on finance/compliance data
- MLflow tracking via Databricks-native integration

### 3. Prepare a model for deployment (20-25%)
- Evaluate models (metrics, fairness, responsible AI dashboard)
- Register models in MLflow Model Registry
- Package models for deployment (MLflow, ONNX)

**IPAI mapping:**
- Foundry eval framework + `appi-ipai-dev` App Insights for quality metrics
- Responsible AI: Pulser policy-gated model (mutations require approval)
- Model registry: Databricks MLflow + Unity Catalog model governance
- 11 serving endpoints already registered and READY

### 4. Deploy and retrain a model (10-15%)
- Deploy to online endpoints (real-time inference)
- Deploy to batch endpoints (batch scoring)
- Monitor model performance and data drift
- Implement retraining triggers

**IPAI mapping:**
| Endpoint | Model | Status |
|---|---|---|
| Databricks serving (11 endpoints) | Llama 4 Scout, Qwen3, etc. | All READY |
| Foundry (`ipai-copilot-resource`) | gpt-4.1-mini | RTFP blocked (only 1 model) |
| Inference endpoint | `https://ipai-foundry-sea.services.ai.azure.com/models` | Live |

**Bypass strategy:** Databricks serving endpoints bypass Foundry RTFP block entirely. Use for frontier model inference until RTFP is resolved.

## Grounding rule

Before answering any DP-100 domain question:
```
mcp__microsoft-learn__microsoft_docs_search(query="<topic> Azure data scientist machine learning")
```

Then apply IPAI-specific context (Databricks workspace, Unity Catalog, gold marts, serving endpoints).
