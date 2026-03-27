# Medallion Architecture: Mandatory Lanes

The InsightPulseAI platform enforces a strict, governed analytics architecture based on the Microsoft Modern Analytics reference model.

## Canonical Hard Architecture Decisions

The following pillars are **MANDATORY** and non-optional:

1.  **Azure Databricks**: The mandatory data-engineering core and governed lakehouse plane.
2.  **Unity Catalog**: The mandatory governance layer for all data and AI assets.
3.  **Medallion Structure**: The mandatory data-product structure (Bronze, Silver, Gold).
4.  **Power BI**: The primary mandatory business-consumption and reporting layer.
5.  **Microsoft Fabric**: The mandatory complementary mirroring and semantic-consumption layer (adjunct to Databricks, not a replacement).
6.  **Platform Controls**: Entra ID (Identity), Key Vault (Secrets), and Azure DevOps/GitHub (Delivery) are the mandatory platform controls.

---

## 1. Bronze Lane (Raw / Ingestion)
- **Role**: REQUIRED raw landing zone for all source data.
- **Authority**: Databricks (engineering) + Fabric (mirroring).
- **Paths**:
  - **Databricks-Native**: Ingestion via Auto Loader (ADLS Gen2), Event Hubs, and Lakehouse Federation.
  - **Fabric-Native**: Mirroring of Azure PostgreSQL / Odoo operational data directly into OneLake for immediate downstream curation.
- **Constraint**: n8n is for orchestration only; it is **NOT** the CDC/analytical replication backbone.

## 2. Silver Lane (Normalized / Conformed)
- **Role**: REQUIRED cleansed, typed, and conformed data layer.
- **Authority**: Databricks + Unity Catalog.
- **Metadata**: Governed by Unity Catalog; stored as Delta tables on ADLS Gen2 (UniForm).
- **Process**: dbt-driven transformations and schema validation.

## 3. Gold Lane (Curated / Marts)
- **Role**: REQUIRED business-ready aggregates and domain-specific marts.
- **Authority**: Databricks + Unity Catalog.
- **Serving**: Served via **Databricks SQL Serverless**.
- **Output**: Governed data products ready for semantic consumption.

## 4. Consumption Lane (Reporting / AI)
- **Role**: REQUIRED business-facing surface for reports and insights.
- **Primary Surface**: **Power BI** (connected live to Unity Catalog and Databricks SQL).
- **Secondary Surface**: **Databricks Apps** for agentic data products (MLflow ResponsesAgent over Gold martyrs).
- **Complementary Surface**: Fabric for semantic integration and OneLake-native analytics.
- **AI Integration**: Azure AI Foundry, OpenAI, and Feature Store/Vector Search within Databricks.

---
**Governance SSOT**: Unity Catalog + Agent Factory V2
**Code Authority**: `data-intelligence` repo
**Status**: MANDATORY
