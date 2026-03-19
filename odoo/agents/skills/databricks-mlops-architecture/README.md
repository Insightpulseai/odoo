# databricks-mlops-architecture

Designs MLOps orchestration architecture using Azure Databricks, covering training pipelines, promotion gates, serving configuration, and model lifecycle management.

## When to use
- New ML workload requiring end-to-end orchestration design
- MLOps pipeline architecture review
- Model promotion workflow design (dev -> staging -> production)
- Training-to-serving pipeline setup

## Key rule
MLOps orchestration must be fully codified -- no ad-hoc notebook runs in production. All training and serving pipelines require Git-backed code, defined promotion gates, and monitoring.

## Source
"Use Azure Databricks to Orchestrate MLOps" -- Microsoft Learn architecture card.

## Cross-references
- `agents/knowledge/benchmarks/azure-databricks-architecture-cards.md` (Card 1)
- `agent-platform/ssot/learning/databricks_architecture_card_map.yaml`
- `agents/skills/databricks-model-serving-production-readiness/`
- `agents/skills/databricks-pipeline-production-readiness/`
