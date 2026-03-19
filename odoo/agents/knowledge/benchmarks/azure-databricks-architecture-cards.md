# Azure Databricks Architecture Cards — Benchmark Knowledge Base

> Source: Microsoft Learn architecture collection for Azure Databricks.
> Purpose: Feed benchmark skills that shape the Databricks skill system.
> Updated: 2026-03-17

---

## Card Inventory

| # | Card Title | Priority | Rationale |
|---|-----------|----------|-----------|
| 1 | Use Azure Databricks to Orchestrate MLOps | **Primary** | Directly shapes MLOps orchestration skill — training, staging, production, model lifecycle |
| 2 | Use the many-models architecture approach | **Primary** | Directly shapes multi-model governance — model-per-domain, inventory, cost control |
| 3 | Use AI to Forecast Customer Orders | **Conditional** | Scenario archetype (retail/FMCG); useful pattern but not control-plane relevant |
| 4 | IoT analytics with Azure Data Explorer and Azure IoT Hub | **Defer** | Optional adjacent benchmark; only relevant if streaming telemetry is in scope |

---

## Card 1: MLOps Orchestration (Primary)

**Source**: "Use Azure Databricks to Orchestrate MLOps"

### Key Architecture Concepts

- **Training orchestration**: Databricks Jobs/Workflows manage training pipelines end-to-end (data prep, feature engineering, model training, evaluation)
- **Staging/production path**: Models promote through dev -> staging -> production with gate checks at each boundary
- **Batch scoring and serving promotion**: Batch inference via Jobs; real-time serving via Model Serving endpoints with traffic splitting
- **Model lifecycle handoff**: MLflow Model Registry tracks versions, stages, and transitions; Unity Catalog for governance
- **Git integration**: Repos integration for version-controlled notebooks and code; CI/CD via GitHub Actions or Azure DevOps Pipelines
- **Jobs/Workflows**: Multi-task workflows with task dependencies, conditional execution, and retry policies

### Influence on Skill System

This card defines the canonical MLOps orchestration pattern for our Databricks skills. It establishes:
- How training pipelines should be structured (not ad-hoc notebook runs)
- What promotion gates look like (automated tests, metric thresholds)
- How model serving is managed (endpoint deployment, A/B traffic)
- Where Git integration fits (source control for all pipeline code)

### Cross-References

- Skill: `agents/skills/databricks-mlops-architecture/`
- Existing: `agents/skills/databricks-model-serving-production-readiness/`
- Existing: `agents/skills/databricks-pipeline-production-readiness/`

---

## Card 2: Many-Models Governance (Primary)

**Source**: "Use the many-models architecture approach"

### Key Architecture Concepts

- **When to split models**: By domain (sales vs. churn), by segment (region, product line), by use case (forecast vs. classification), by tenant (multi-tenant SaaS)
- **Model inventory and cost control**: Centralized registry for all models; compute cost attribution per model; lifecycle management (retire stale models)
- **Specialized model routing**: Request routing to the correct model based on input features, tenant ID, or domain context
- **Model-per-domain pattern**: Each business domain owns its model(s); shared feature stores but independent training pipelines
- **Model-per-tenant pattern**: Tenant-specific models for personalization; shared architecture with tenant-scoped data isolation

### Influence on Skill System

This card defines governance for multi-model portfolios. It establishes:
- Decision framework for when one model vs. many is appropriate
- Inventory discipline (every model registered, versioned, cost-tracked)
- Routing patterns (how requests reach the right model)
- Retirement criteria (when to decommission a model)

### Cross-References

- Skill: `agents/skills/many-models-governance/`
- Existing: `agents/skills/databricks-model-serving-production-readiness/`
- Existing: `agents/skills/databricks-agent-production-readiness/`

---

## Card 3: Forecasting Solution Design (Conditional)

**Source**: "Use AI to Forecast Customer Orders"

### Key Architecture Concepts

- **Retail/FMCG scenario blueprint**: Demand forecasting for inventory optimization, supply chain planning
- **Analytics + prediction + action loop**: Historical analysis -> model training -> forecast generation -> business action (reorder, staffing)
- **Feature engineering for time series**: Lag features, rolling aggregates, calendar effects, external signals (weather, promotions)
- **Evaluation**: MAPE, RMSE, forecast bias; backtesting on holdout periods

### Influence on Skill System

This is a **scenario archetype**, not a control-plane skill. It provides:
- A reusable pattern for demand/forecast workloads
- Feature engineering recipes for time-series problems
- Evaluation methodology for forecast accuracy

**Guardrail**: This card does not influence core platform architecture. It is a domain-specific application pattern that can be instantiated when a forecasting use case arises.

### Cross-References

- Skill: `agents/skills/forecasting-solution-design/`
- Related domain pack: `ssot/capabilities/domain_packs.yaml` (retail_media)

---

## Card 4: IoT Analytics (Defer)

**Source**: "IoT analytics with Azure Data Explorer and Azure IoT Hub"

### Key Architecture Concepts

- **Streaming telemetry ingestion**: IoT Hub -> Azure Data Explorer (ADX) for high-volume time-series data
- **Near-real-time analytics**: ADX Kusto queries for anomaly detection, dashboarding
- **Device management**: IoT Hub device registry, twin management
- **Edge processing**: Azure IoT Edge for local compute before cloud ingestion

### Influence on Skill System

This card is **deferred** unless streaming telemetry is explicitly in scope. It provides:
- A fit-assessment pattern: is IoT/streaming actually needed for this workload?
- Prevention of accidental scope expansion into IoT architecture

**Guardrail**: IoT analytics is an optional adjacent benchmark. Do not include in core platform architecture unless a concrete streaming telemetry requirement exists.

### Cross-References

- Skill: `agents/skills/iot-analytics-fit-assessment/`
- Assessment type: Judge (returns IN_SCOPE / OUT_OF_SCOPE / CONDITIONAL)

---

## Usage Rules

1. **Primary cards** (MLOps, Many-Models) feed directly into the Databricks skill system and influence architecture decisions
2. **Conditional cards** (Forecasting) are instantiated only when a matching use case arises
3. **Deferred cards** (IoT) require explicit scope confirmation before activation
4. All cards are benchmarks — they shape target capability, not implementation specifics
5. Implementation stays grounded in the existing Azure/Foundry/Databricks/Odoo stack
