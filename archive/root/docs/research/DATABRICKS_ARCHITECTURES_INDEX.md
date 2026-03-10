# Databricks Architecture Center -- Comprehensive Index

**URL**: [databricks.com/resources/architectures](https://www.databricks.com/resources/architectures)
**Research Date**: 2026-03-07
**Branch**: `claude/review-signavio-url-HffM8`

> Scalable lakehouse architectures, blueprints and best practices for unifying data, governance and AI -- built for engineers and architects.

---

## Table of Contents

1. [Architecture Center Reference Architectures](#1-architecture-center-reference-architectures)
2. [Foundational Architecture Patterns](#2-foundational-architecture-patterns)
3. [Well-Architected Lakehouse Framework](#3-well-architected-lakehouse-framework)
4. [Data Engineering Architectures](#4-data-engineering-architectures)
5. [Machine Learning & AI Architectures](#5-machine-learning--ai-architectures)
6. [Data Governance & Security](#6-data-governance--security)
7. [Cloud Deployment Architectures](#7-cloud-deployment-architectures)
8. [Integration Architectures](#8-integration-architectures)
9. [Industry-Specific Architectures](#9-industry-specific-architectures)
10. [Performance & Cost Optimization](#10-performance--cost-optimization)
11. [Platform Components](#11-platform-components)
12. [Downloadable PDF Reference Architectures](#12-downloadable-pdf-reference-architectures)

---

## 1. Architecture Center Reference Architectures

**URL**: [databricks.com/resources/architectures](https://www.databricks.com/resources/architectures)

### Cross-Industry / Platform

| # | Title | URL | Pattern | Target Use Case |
|---|-------|-----|---------|-----------------|
| 1 | **Data Ingestion Reference Architecture** | [Link](https://www.databricks.com/resources/architectures/data-ingestion-reference-architecture) | Batch + CDC + Streaming into Medallion | Modernizing data pipelines with Lakeflow Connect, Auto Loader, Structured Streaming |
| 2 | **Intelligent Data Warehousing on Databricks** | [Link](https://www.databricks.com/resources/architectures/intelligent-data-warehousing-on-databricks) | Lakehouse-based DWH with AI | Modern DWH combining streaming/batch, governed storage, scalable SQL analytics |
| 3 | **Data Intelligence End-to-End (Azure)** | [Link](https://www.databricks.com/resources/architectures/data-intelligence-architecture-end-to-end-with-azure-databricks) | End-to-end lakehouse on Azure | ETL, DWH, AI, real-time analytics, GenAI apps |

### Cybersecurity

| # | Title | URL | Pattern | Target Use Case |
|---|-------|-----|---------|-----------------|
| 4 | **Security Lakehouse** | [Link](https://www.databricks.com/resources/architectures/reference-architecture-for-security-lakehouse) | Bronze/Silver/Gold security data lake | Centralized security data; detection, response, reporting |
| 5 | **Security Operations** | [Link](https://www.databricks.com/resources/architectures/reference-architecture-for-security-operations) | Unified SecOps platform | SIEM integration, threat hunting, alert enrichment |

### Financial Services

| # | Title | URL | Pattern | Target Use Case |
|---|-------|-----|---------|-----------------|
| 6 | **Investment Management** | [Link](https://www.databricks.com/resources/architectures/financial-services-investment-management-reference-architecture) | Lakehouse for capital markets | Multi-asset class integration, investment analytics |
| 7 | **Credit Loss Forecasting (CECL)** | [Link](https://www.databricks.com/resources/architectures/credit-loss-forecasting-reference-architecture) | Regulatory-compliant forecasting | CECL, CCAR, IFRS 9; auditable credit loss forecasting |

### Insurance (6 Architectures)

| # | Title | URL | Target Use Case |
|---|-------|-----|-----------------|
| 8 | **Customer 360 for Insurance** | [Link](https://www.databricks.com/resources/architectures/c360-reference-architecture-for-insurance) | Holistic policyholder view, churn prediction, fraud detection |
| 9 | **AI-Powered Claims Assessment** | [Link](https://www.databricks.com/resources/architectures/ai-powered-claims-reference-architecture-for-insurance) | Accelerated claim settlements, fraud detection |
| 10 | **Underwriting Analytics** | [Link](https://www.databricks.com/resources/architectures/underwriting-analytics-reference-architecture) | Holistic risk profiles for underwriting |
| 11 | **Distribution Optimization** | [Link](https://www.databricks.com/resources/architectures/distribution-optimization-reference-architecture-for-insurance) | Quote-to-bind rates, agent productivity |
| 12 | **Catastrophe Modeling** | [Link](https://www.databricks.com/resources/architectures/catastrophe-modeling-reference-architecture-for-insurance) | Loss prediction, geospatial + ML modeling |
| 13 | **Actuarial Modeling** | [Link](https://www.databricks.com/resources/architectures/actuarial-modeling-reference-architecture-for-insurance) | Actuarial analytics for underwriting |

### Healthcare

| # | Title | URL | Target Use Case |
|---|-------|-----|-----------------|
| 14 | **Patient Personalization** | [Link](https://www.databricks.com/resources/architectures/healthcare-patient-personalization-reference-architecture) | Personalized patient care journeys |

### Manufacturing & Energy

| # | Title | URL | Target Use Case |
|---|-------|-----|-----------------|
| 15 | **Digital Supply Chain** | [Link](https://www.databricks.com/resources/architectures/manufacturing-digital-supply-chain-reference-architecture) | AI-driven quoting, supplier assessment, replenishment |
| 16 | **Industrial AI** | [Link](https://www.databricks.com/resources/architectures/industrial-ai-reference-architecture-for-manufacturing) | OEE analytics, predictive maintenance, edge AI |
| 17 | **Office of CFO (Manufacturing/Energy)** | Referenced from Industrial AI page | Financial analytics for manufacturing/energy |
| 18 | **Energy Grid Operations** | [Link](https://www.databricks.com/resources/architectures/energy-grid-operations-reference-architecture) | Grid performance and operations analytics |

### Retail & Telecom

| # | Title | URL | Target Use Case |
|---|-------|-----|-----------------|
| 19 | **Retail Demand Forecasting** | [Link](https://www.databricks.com/resources/architectures/retail-demand-forecasting-reference-architecture) | AI-powered demand forecasting from POS/e-commerce/ERP |
| 20 | **Telecom Network Performance** | [Link](https://www.databricks.com/resources/architectures/telecom-network-performance-monitoring-reference-architecture) | Network performance and customer experience analytics |

---

## 2. Foundational Architecture Patterns

### Medallion Architecture (Bronze / Silver / Gold)

**URLs**: [docs](https://docs.databricks.com/aws/en/lakehouse/medallion) | [glossary](https://www.databricks.com/glossary/medallion-architecture)

| Layer | Purpose | Data Model | Key Characteristics |
|-------|---------|-----------|---------------------|
| **Bronze** | Raw data ingestion | String/VARIANT/binary fields | No cleanup; preserve fidelity; protect against schema changes |
| **Silver** | Cleansed and validated | 3NF-like / Data Vault-like | Drop nulls, quarantine invalid records, join datasets |
| **Gold** | Business-ready / consumption | De-normalized, read-optimized | Fewer joins; business rules applied; project-specific |

**Tooling**: Spark Declarative Pipelines (formerly Delta Live Tables) with streaming tables and materialized views for incremental refresh.

### Delta Lake

**URL**: [docs.databricks.com/aws/en/delta/](https://docs.databricks.com/aws/en/delta/)

- Open-source storage layer extending Parquet with file-based transaction log
- ACID transactions, schema enforcement, time travel, scalable metadata
- Default format for all Databricks tables
- Performance: data skipping (min/max statistics), file compaction, Z-Ordering, Liquid Clustering

### Data Lakehouse

**URL**: [databricks.com/product/data-lakehouse](https://www.databricks.com/product/data-lakehouse)

- Combines reliability/performance of data warehouses with flexibility/scale of data lakes
- Eliminates dual lake-warehouse complexity
- Unified platform for data engineering, BI, and ML workloads

### Data Mesh on Databricks

**URLs**: [Part 1](https://www.databricks.com/blog/databricks-lakehouse-and-data-mesh-part-1) | [Part 2](https://www.databricks.com/blog/building-data-mesh-based-databricks-lakehouse-part-2)

| Component | Role in Data Mesh |
|-----------|-------------------|
| **Unity Catalog** | Central policy enforcement; federated governance; metadata management |
| **Delta Sharing** | Open protocol for cross-domain, cross-cloud, cross-org data sharing |
| **Workspace-per-Domain** | Domain autonomy with shared governance |
| **Data Contracts** | Formal alignment between domains |
| **Hub & Spoke Model** | Centralized shareable assets + domain-specific spokes |

---

## 3. Well-Architected Lakehouse Framework

**URL**: [docs.databricks.com/aws/en/lakehouse-architecture/well-architected](https://docs.databricks.com/aws/en/lakehouse-architecture/well-architected)

Seven pillars (vs Azure WAF's five):

| # | Pillar | Focus Area | Key Practices |
|---|--------|-----------|---------------|
| 1 | **Operational Excellence** | Operate, manage, monitor | CI/CD for DevOps + MLOps; IaC; config-as-code |
| 2 | **Security, Privacy & Compliance** | Protect data, meet regulations | HIPAA, SOC 2, PCI-DSS; compliance security profile; encryption |
| 3 | **Reliability** | Data integrity, pipeline resilience | ACID via Delta Lake; layered architecture; schema enforcement |
| 4 | **Performance Optimization** | Query and pipeline speed | Data skipping, compaction, Z-Ordering, Liquid Clustering |
| 5 | **Cost Optimization** | Minimize spending | Right-sizing compute, serverless SQL, auto-scaling |
| 6 | **Data and AI Governance** | Unified governance | Unity Catalog; row/column ACL; lineage; audit logs |
| 7 | **Interoperability & Usability** | Open formats, cross-platform | Delta, Iceberg support; Lakehouse Federation; open APIs |

---

## 4. Data Engineering Architectures

### Streaming (Structured Streaming + Declarative Pipelines)

**URLs**: [DLT](https://www.databricks.com/product/delta-live-tables) | [Streaming Tables](https://docs.databricks.com/aws/en/ldp/streaming-tables)

| Component | Description |
|-----------|-------------|
| **Streaming Tables** | Delta tables with incremental processing; each row handled once; append-only ingestion |
| **Materialized Views** | Precomputed views with automatic incremental refresh |
| **Spark Declarative Pipelines** | Declarative ETL framework; automates orchestration, compute, monitoring, DQ |
| **Two Ingestion Patterns** | (1) Direct streaming from Kafka/Kinesis (lower latency) or (2) Cloud storage via Auto Loader |
| **CDC Support** | APPLY CHANGES APIs for SCD Type 1 and Type 2; handles out-of-sequence records |

### Lakeflow Connect (Managed Ingestion)

**URL**: [docs.databricks.com/aws/en/ingestion/overview](https://docs.databricks.com/aws/en/ingestion/overview)

- Managed connectors for enterprise applications, databases, cloud storage, message buses
- Governed by Unity Catalog
- Orchestrated by Lakeflow Jobs

### Lakehouse Federation (Query Without Moving Data)

**URL**: [docs.databricks.com/aws/en/query-federation/](https://docs.databricks.com/aws/en/query-federation/)

- Query MySQL, PostgreSQL, Redshift, Snowflake, Azure SQL, BigQuery, Oracle, Teradata without copying data
- Queries pushed down to source systems via JDBC
- Two modes: **Query Federation** (on-demand) and **Catalog Federation** (direct file access)
- Governed by Unity Catalog with lineage and access controls
- Requires DBR 13.3 LTS+, Pro or Serverless SQL warehouses

---

## 5. Machine Learning & AI Architectures

### Mosaic AI Platform

**URL**: [databricks.com/product/artificial-intelligence](https://www.databricks.com/product/artificial-intelligence)

| Capability | Description |
|-----------|-------------|
| **Agent Framework** | Production-scale agent systems; supports LangGraph, LangChain, OpenAI, LlamaIndex, custom Python |
| **Agent Bricks** (June 2025) | Automated domain-specific AI agents; multi-agent supervisor; LLM judge quality tracking |
| **Model Serving** | Serverless auto-scaling endpoints; CPU/GPU; scale-to-zero; automatic feature lookup |
| **Vector Search** | Storage-Optimized; billions of vectors; 7x lower cost; backbone of RAG |
| **AI Evaluation** | MLflow Evaluation with LLM Judges for automated quality scoring |
| **AI Gateway** | Centralized model management and routing |

### RAG Architecture

**URL**: [databricks.com/product/machine-learning/retrieval-augmented-generation](https://www.databricks.com/product/machine-learning/retrieval-augmented-generation)

```
Data Sources -> Delta Tables (governed) -> Mosaic AI Vector Search
                                                    |
                                              RAG Pipeline
                                                    |
                              MLflow Tracking + Tracing (every step, tool call, latency, cost)
                                                    |
                              MLflow Evaluation + LLM Judges -> UC Model Registry
                                                                      |
                                                              Model Serving Endpoint
                                                              (logs traces back to lakehouse)
```

### MLOps Reference Architecture (Big Book of MLOps)

**URL**: [databricks.com/blog/big-book-mlops-updated-generative-ai](https://www.databricks.com/blog/big-book-mlops-updated-generative-ai)

- Updated for Generative AI with new LLMOps section
- Key components: MLflow 3.0 (redesigned for GenAI), Databricks Asset Bundles (IaC), prompt versioning
- MLflow Tracing: native autologging for 20+ GenAI frameworks; OpenTelemetry-compatible

### Feature Store

**URLs**: [Product](https://www.databricks.com/product/feature-store) | [Docs](https://docs.databricks.com/aws/en/machine-learning/feature-store/)

| Component | Description |
|-----------|-------------|
| **Offline Store** | Feature tables as Delta tables; discovery, training, batch inference |
| **Online Store** (Lakebase) | Low-latency serving; serverless; scales to billions |
| **Feature Serving Endpoints** | Auto-scaling, high-availability; also serves structured data for RAG |
| **FeatureSpec** | User-defined feature + function sets; managed in Unity Catalog |
| **Automatic Feature Lookup** | Model Serving auto-resolves features via Unity Catalog lineage |

### Agentic AI / Compound AI Systems

**URLs**: [Blog](https://www.databricks.com/blog/ai-agent-systems) | [Agent Bricks](https://www.databricks.com/product/artificial-intelligence/agent-bricks)

| Component | Role |
|-----------|------|
| **LLM/Central Agent** | Decision-making core |
| **Memory** | Short-term (working context) + Long-term (episodic, cross-session) |
| **Planning** | Task decomposition and execution |
| **Tools** | Functions, API calls, retrieval, tool invocations |
| **Multi-Agent Supervisor** | Orchestrate across Genie spaces, LLM agents, MCP tools |
| **Modular Design** | Separate deterministic, partially ambiguous, and creative components |

---

## 6. Data Governance & Security

### Unity Catalog Architecture

**URLs**: [Docs](https://docs.databricks.com/aws/en/data-governance/unity-catalog/) | [Product](https://www.databricks.com/product/unity-catalog)

**Hierarchy**: Metastore -> Catalogs -> Schemas -> Tables/Views/Volumes/Models/Functions

| Capability | Description |
|-----------|-------------|
| **Access Control** | Hierarchical privilege model; account to row/column level; RBAC + ABAC |
| **Audit Logging** | User-level audit logs for all data access |
| **Data Lineage** | Runtime lineage across queries; column-level; visualized in Catalog Explorer |
| **Data Discovery** | Tags, comments, search across all assets |
| **UC Metrics** (2025) | Business metrics as first-class assets |
| **Iceberg Managed Tables** (2025 Preview) | Delta + Iceberg interop with liquid clustering |
| **System Tables** | Metadata tables: billing, compute usage, lineage, query history |

### Compliance Architectures

**URL**: [databricks.com/trust/architecture](https://www.databricks.com/trust/architecture)

| Standard | Databricks Support |
|----------|-------------------|
| **HIPAA** | BAA agreements; compliance security profile; HW-accelerated encryption |
| **SOC 2 Type 2** | Security, Availability, Processing Integrity, Confidentiality |
| **PCI-DSS** | Compliant on AWS |
| **ISO 27001** | Certified |
| **GDPR/CCPA** | Data lineage for traceability; deletion support |
| **BCBS 239 / SOX** | Lineage and auditability for regulatory tracing |

**Architecture Pattern**: Control plane (Databricks-managed) + Compute plane (customer VPC); hard segregation. Compliance security profile adds automatic cluster updates, enhanced monitoring, hardened Ubuntu Advantage OS.

### Zero Trust Architecture

- "Never trust, always verify" model
- Unity Catalog validates permissions on every request, issuing short-lived, down-scoped tokens
- System tables provide retrospective monitoring (access logs, query history, lineage)
- Integrates with third-party tools (e.g., Immuta) for ABAC

---

## 7. Cloud Deployment Architectures

### AWS

**Key Components:**
- **Control Plane** (Databricks-managed): Web app, cluster manager, jobs service, REST APIs
- **Classic Compute Plane** (Customer VPC): Spark clusters in customer account
- **Serverless Compute Plane** (Databricks account): Managed compute, same region

**VPC Architecture:**
- Default: Databricks creates managed VPC per workspace
- Customer-Managed VPC: Full network control; required for PrivateLink
- Subnet requirements: Min 2 subnets in different AZs, netmask /17 to /26
- Secure Cluster Connectivity ("No Public IPs"): All nodes get private IPs only

**PrivateLink (3 types):**
- **Inbound (front-end)**: User-to-workspace via Transit VPC
- **Classic (back-end)**: Classic compute to control plane
- **Outbound (serverless)**: Serverless compute to customer resources via NCCs

Sources: [VPC](https://docs.databricks.com/aws/en/security/network/classic/customer-managed-vpc) | [PrivateLink](https://docs.databricks.com/aws/en/security/network/concepts/privatelink-concepts)

### Azure

**Key Components:**
- **Control Plane**: Microsoft-managed Azure subscription
- **Data Plane**: Locked VNet in customer subscription

**VNet Injection:**
- Deploy clusters into customer-managed VNet
- Requires two dedicated subnets: container (private) and host (public), min /26 CIDR
- Subnet delegation to `Microsoft.Databricks/workspaces`

**Secure Cluster Connectivity (SCC):** No public IPs; compute connects to control plane through relay

Sources: [VNet Injection](https://learn.microsoft.com/en-us/azure/databricks/security/network/classic/vnet-inject) | [WAF Best Practices](https://learn.microsoft.com/en-us/azure/well-architected/service-guides/azure-databricks)

### GCP

**Notable Design Decisions:**
- **Kubernetes-based runtime** (GKE) -- unique to GCP deployment
- Native integration with GCS, BigQuery, Pub/Sub, Looker
- Private Service Connect for private networking
- Three workspace storage buckets per classic workspace

Sources: [Architecture](https://docs.databricks.com/gcp/en/getting-started/architecture) | [Networking](https://docs.databricks.com/gcp/en/security/network/)

### Multi-Cloud Patterns

**Three Requirements for Portability:**
1. Open, portable data format with common security model (Delta Lake + Unity Catalog)
2. Common foundation services across clouds (Spark, Photon, MLflow)
3. Open APIs enabling single codebase across platforms

**Key Patterns:**
- One Databricks Account per cloud provider; SCIM for identity sync
- **Delta Sharing** for cross-cloud data access
- Hub-and-spoke architecture for centralized data with federated access
- Delta deep clone for cross-cloud replication and DR
- Terraform with Databricks provider (13.2M+ installs) for multi-cloud IaC

### Hub-Spoke & Private Link

**Azure Hub-Spoke Pattern:**
- **Transit VNet (Hub)**: Inbound private endpoints for workspace access + browser SSO
- **Workspace VNet (Spoke)**: Azure Databricks workspace + classic private endpoints
- Spokes peer with hub; Azure Firewall in hub for egress filtering
- Separate private endpoint for browser authentication recommended

**AWS Hub-Spoke Pattern:** Similar -- Transit VPC (hub) + Compute Plane VPC (spoke)

---

## 8. Integration Architectures

### Snowflake (Lakehouse Federation)

- **Connection**: JDBC-based via Unity Catalog metastore
- **Foreign Catalog**: Mirrors Snowflake database in Unity Catalog
- **Two modes**: Query Federation (pushdown to Snowflake) or Catalog Federation (direct file access)
- **Auth**: OAuth, Basic Auth, PEM Private Key, Microsoft Entra ID

Source: [docs.databricks.com/aws/en/query-federation/snowflake](https://docs.databricks.com/aws/en/query-federation/snowflake)

### Power BI / Tableau

**Power BI Methods:**
1. Power BI Desktop + Databricks SQL (most common)
2. Direct Publish from Databricks to Power BI Service
3. Partner Connect (pre-configured connection)
4. Tabular Editor Bridge (advanced semantic modeling)

**Storage Modes:** DirectQuery (real-time), Import (performance), Dual (hybrid)
**Tableau:** Create datasources from Unity Catalog tables directly from Databricks UI

Source: [docs.databricks.com/aws/en/partners/bi/power-bi](https://docs.databricks.com/aws/en/partners/bi/power-bi)

### Kafka / Event Hubs (Streaming)

- Structured Streaming Kafka Connector + Medallion Architecture
- Azure Event Hubs exposes Kafka-compatible endpoint (no special library needed)
- Bootstrap: `{EH_NAMESPACE}.servicebus.windows.net:9093` with SASL_SSL
- **Auth**: Shared Access Key, Entra ID (OAuth), Unity Catalog Service Credentials (recommended)

Source: [docs.databricks.com/aws/en/connect/streaming/kafka](https://docs.databricks.com/aws/en/connect/streaming/kafka)

### dbt

- Use `dbt-databricks` adapter (not `dbt-spark`), version 1.8.0+
- Recommended compute: **Databricks SQL Warehouses**
- Production: dbt task type in Databricks Jobs (Lakeflow Jobs)
- Staging/intermediate/mart maps to medallion (bronze/silver/gold)

Source: [docs.databricks.com/aws/en/partners/prep/dbt](https://docs.databricks.com/aws/en/partners/prep/dbt)

### Airflow (Orchestration)

**Operators:**
- **DatabricksRunNowOperator** (recommended): Triggers existing job via API
- **DatabricksSubmitRunOperator**: Submits ad-hoc job spec
- **DatabricksWorkflowTaskGroup**: Auto-creates job from notebook operators

**Competing/Complementary:** Lakeflow Jobs (native orchestrator) for data-aware triggers, Unity Catalog integration, built-in lineage

Source: [docs.databricks.com/aws/en/jobs/how-to/use-airflow-with-jobs](https://docs.databricks.com/aws/en/jobs/how-to/use-airflow-with-jobs)

### Terraform / IaC

- Databricks Terraform Provider: 13.2M+ installs
- **Separation**: Terraform for infrastructure (workspaces, clusters, Unity Catalog, networking); DABs for application deployment (jobs, notebooks, SQL, dashboards)

Source: [docs.databricks.com/aws/en/dev-tools/ci-cd/best-practices](https://docs.databricks.com/aws/en/dev-tools/ci-cd/best-practices)

### CI/CD (Databricks Asset Bundles)

- IaC framework: jobs, pipelines, clusters, notebooks as version-controlled YAML (`bundle.yaml`)
- Multi-environment targets (`mode: development` auto-prefixes per user)
- Monorepo support with multiple independent bundles
- Uses Terraform under the hood
- Auth: Workload identity federation recommended

Source: [docs.databricks.com/aws/en/dev-tools/bundles/](https://docs.databricks.com/aws/en/dev-tools/bundles/)

---

## 9. Industry-Specific Architectures

### Financial Services

**URL**: [databricks.com/solutions/industries/financial-services](https://www.databricks.com/solutions/industries/financial-services)

| Use Case | Key Capabilities |
|----------|-----------------|
| **Risk Management** | Unified risk + finance data; CECL, stress testing, liquidity risk |
| **Fraud Detection** | ML-powered AML transaction monitoring; KYC at billions scale |
| **AI Compliance** | Multi-agent compliance assistant; reasoning over structured + unstructured |
| **Regulatory** | NIST, ISO, GDPR, PCI DSS, FINRA, AML, Basel III/IV, DORA controls |

### Healthcare & Life Sciences

**URL**: [databricks.com/solutions/industries/healthcare-and-life-sciences](https://www.databricks.com/solutions/industries/healthcare-and-life-sciences)

**Solution Accelerators:**
- **FHIR Interoperability (dbignite)**: Extract FHIR resources for EDA
- **Automated PHI Removal**: HIPAA-compliant de-identification
- **Digital Pathology**: Whole slide image segmentation + metastasis classification
- **DICOM Medical Imaging (Pixels 2.0)**: Scalable ingestion of hundreds of formats; MONAI integration
- **Provider MDM**: AI-powered record dedup via Vector Search + embeddings
- **Real-World Evidence**: Drug efficacy from real-world patient data

### Manufacturing & IoT

**Industrial AI Architecture:**
```
Industrial Systems (ERP, Sensors, Equipment)
    -> Industrial DataOps
        -> Bronze (raw telemetry)
            -> Silver (ML training inputs)
                -> Gold (OEE dashboards, compliance, alerts)
                    -> AI Agents (field service, production control, root cause)
                        -> Edge Deployment (models trained in cloud, deployed to edge)
```

**IoT Data Scale:** Software-defined vehicles up to 30 TB/day; manufacturing 200-500% data growth in 5 years
**Results:** 20% production output increase, 25% reduction in unplanned downtime (McKinsey)

### Retail & CPG

- Out-of-stock detection via IoT/RFID + streaming analytics
- Customer 360 and personalization
- Supply chain optimization
- AI-powered demand forecasting

### Media & Entertainment

- Recommendation engines, CLV modules, streaming QoS, gaming toxicity detection
- Single view of all data including unstructured (video, images, voice)

### Public Sector

- Partner-delivered solutions for cost reduction and faster innovation
- Purpose-built Solution Accelerators as fully functional notebooks

### Telecom

- Network performance monitoring at scale
- Customer experience analytics

---

## 10. Performance & Cost Optimization

### Cluster Sizing & Autoscaling

- **Sizing factors**: Total executor cores (parallelism), memory (in-memory data), local storage (shuffles/caching)
- **Autoscaling**: Dynamic worker reallocation; serverless more sophisticated than classic
- **Serverless DLT Vertical Autoscaling**: Auto-detects OOM and reallocates to higher-memory instances
- **Instance Pools**: No DBU charge for idle pool instances (only cloud VM cost)

### Photon Engine

**URL**: [databricks.com/product/photon](https://www.databricks.com/product/photon)

- **Written in C++**; vectorized query engine
- Up to **12x better price/performance** vs other cloud DWH
- Compatible with Spark SQL and DataFrame APIs (not UDFs, RDD, Dataset APIs)
- Default on SQL warehouses and serverless compute
- **DBU multiplier for classic**: 2.5x (Azure/GCP), 2.9x (AWS)
- 2025: Predictive Query Execution + Vectorized Shuffle (up to 50% cost reduction)

### Serverless Compute

- Near-zero startup latency (2-6 seconds)
- Auto-enabled Photon and autoscaling
- No cluster creation permission required; automatic optimization
- No public IP addresses; private connectivity
- Supported: Notebook, Python script, dbt, Python wheel, JAR
- **Cost break-even**: ~30 minutes; sub-10-min favors serverless; >30 min favors classic

### Delta Lake Optimization

**Liquid Clustering** (recommended for all new tables):
- Replaces both partitioning and Z-ordering
- Tree-based algorithm for balanced data layout (uniform file sizes)
- Keys changeable without rewriting existing data
- Incremental: only new data re-clustered
- Requires DBR 15.2+ GA

**Z-Ordering:**
- Best for static, well-known query patterns and batch processing
- Requires manual OPTIMIZE + ZORDER maintenance
- Not compatible with Liquid Clustering or partitioning

**Best Practices:**
- Limit clustering keys to 1-4 columns
- Do not partition tables under ~1TB
- Each partition: 1-10 GB minimum
- Run VACUUM after OPTIMIZE to reclaim space

### Cost Optimization Checklist

1. Auto-terminate idle clusters
2. Autoscaling to match workload phases
3. Separate interactive vs job workloads (job clusters = lower DBU)
4. Serverless SQL Warehouses with Intelligent Workload Management (IWM)
5. Instance Pools for classic compute
6. Cost accountability -- assign ownership to teams/users
7. Monitor waste signals: idle compute >30%, ranges that never move, family mismatches

---

## 11. Platform Components

### DBSQL (Databricks SQL) Warehouse

**URL**: [databricks.com/product/databricks-sql](https://www.databricks.com/product/databricks-sql)

| Type | Characteristics |
|------|----------------|
| **Classic** | Compute in customer account; manual scaling |
| **Pro** | Enhanced features (query history, profiling) |
| **Serverless** | 2-6s startup; auto-scaling; IWM; Predictive IO |

**Key Features:** Photon (built-in), Intelligent Workload Management (ML-powered resource prediction), Predictive IO (scan optimization)

### Databricks Apps

**URL**: [docs.databricks.com/aws/en/dev-tools/databricks-apps/](https://docs.databricks.com/aws/en/dev-tools/databricks-apps/)

- Containerized web apps on serverless platform
- Supports **Python** (Streamlit, Dash, Gradio) and **Node.js** (React, Angular, Svelte, Express)
- Each app: unique URL, isolated runtime, own identity
- Governed by Unity Catalog; OAuth authentication
- Config: `app.yaml` + `databricks.yml`

### Databricks Marketplace

**URL**: [docs.databricks.com/aws/en/marketplace/](https://docs.databricks.com/aws/en/marketplace/)

- Built on **Delta Sharing** (open protocol for secure cross-platform data exchange)
- Assets: Datasets, notebooks, Solution Accelerators, ML/AI models, **MCP servers**
- Unity Catalog integration; Clean Rooms for privacy-centric collaboration
- 2025 Partners: SAP, S&P Global, FactSet, IAS, Infor Nexus, Magnite, SambaTV

### Solution Accelerators

**URL**: [databricks.com/solutions/accelerators](https://www.databricks.com/solutions/accelerators)

- **50+ accelerators** on [GitHub](https://github.com/databricks-industry-solutions) and Marketplace
- Cover: risk management, churn prevention, digital pathology, gaming toxicity, geospatial, time series, CV, NLP
- Typical PoC timeline: 2 weeks from ideation

### 2025 Platform Milestones

| Milestone | Impact |
|-----------|--------|
| **Photon Predictive Execution + Vectorized Shuffle** | Up to 50% cost reduction for heavy workloads |
| **Lakehouse Federation GA** | Query BigQuery, Oracle, Teradata without copying |
| **Lakebase** | Serverless PostgreSQL engine unifying OLTP + OLAP |
| **DBSQL Native AI Functions** | LLM calls directly in SQL queries |
| **MCP Servers on Marketplace** | Shareable agentic AI components |
| **Agent Bricks** | Automated multi-agent system creation |

---

## 12. Downloadable PDF Reference Architectures

**URL**: [docs.databricks.com/aws/en/lakehouse-architecture/reference](https://docs.databricks.com/aws/en/lakehouse-architecture/reference)

11x17 (A3) format PDFs, available per cloud:

| Architecture | AWS | Azure | GCP |
|---|---|---|---|
| **Batch ETL** | [PDF](https://docs.databricks.com/aws/en/lakehouse-architecture/reference) | [PDF](https://learn.microsoft.com/en-us/azure/databricks/lakehouse-architecture/reference) | [PDF](https://docs.databricks.com/gcp/en/lakehouse-architecture/reference) |
| **Spark Structured Streaming** | Available | Available | Available |
| **Lakeflow Connect** | Available | Available | Available |
| **ML and AI** | Available | Available | Available |
| **Gen AI Application** | Available | Available | Available |
| **BI & SQL Analytics** | Available | Available | Available |
| **Combined (all-in-one)** | [Direct PDF](https://docs.databricks.com/_extras/documents/reference-architecture-databricks-on-aws.pdf) | -- | -- |

---

## Quick Reference: Key URLs

| Resource | URL |
|----------|-----|
| Architecture Center | https://www.databricks.com/resources/architectures |
| Lakehouse Architecture Docs | https://docs.databricks.com/aws/en/lakehouse-architecture/ |
| Reference Architecture PDFs (AWS) | https://docs.databricks.com/aws/en/lakehouse-architecture/reference |
| Well-Architected Framework | https://docs.databricks.com/aws/en/lakehouse-architecture/well-architected |
| Unity Catalog | https://docs.databricks.com/aws/en/data-governance/unity-catalog/ |
| Mosaic AI | https://www.databricks.com/product/artificial-intelligence |
| Delta Lake | https://docs.databricks.com/aws/en/delta/ |
| Medallion Architecture | https://docs.databricks.com/aws/en/lakehouse/medallion |
| Lakehouse Federation | https://docs.databricks.com/aws/en/query-federation/ |
| Solution Accelerators | https://www.databricks.com/solutions/accelerators |
| Industry Solutions GitHub | https://github.com/databricks-industry-solutions |
| Trust & Security | https://www.databricks.com/trust/architecture |
| Databricks Asset Bundles | https://docs.databricks.com/aws/en/dev-tools/bundles/ |
| MLOps (Big Book, updated) | https://www.databricks.com/blog/big-book-mlops-updated-generative-ai |

---

## Framework Interconnection

```
Databricks Architecture Center
|
+-- Foundational Patterns
|   +-- Medallion Architecture (Bronze/Silver/Gold)
|   +-- Delta Lake (storage layer)
|   +-- Data Lakehouse (unified platform)
|   +-- Data Mesh (federated domains)
|
+-- Well-Architected Framework (7 pillars)
|   +-- Operational Excellence
|   +-- Security, Privacy & Compliance
|   +-- Reliability
|   +-- Performance Optimization
|   +-- Cost Optimization
|   +-- Data and AI Governance
|   +-- Interoperability & Usability
|
+-- Reference Architectures (20+ on Architecture Center)
|   +-- Cross-Industry (Data Ingestion, DWH, E2E Azure)
|   +-- Cybersecurity (Security Lakehouse, SecOps)
|   +-- Financial Services (Investment Mgmt, Credit Loss)
|   +-- Insurance (Customer 360, Claims, Underwriting, Cat Modeling, Actuarial, Distribution)
|   +-- Healthcare (Patient Personalization)
|   +-- Manufacturing (Industrial AI, Digital Supply Chain, CFO)
|   +-- Energy (Grid Operations)
|   +-- Retail (Demand Forecasting)
|   +-- Telecom (Network Performance)
|
+-- AI/ML Stack
|   +-- Mosaic AI (Agent Framework, Agent Bricks, Model Serving)
|   +-- RAG Architecture (Vector Search + MLflow)
|   +-- MLOps / LLMOps (Big Book of MLOps)
|   +-- Feature Store (Offline + Online via Lakebase)
|   +-- Compound AI / Multi-Agent Systems
|
+-- Cloud Deployments
|   +-- AWS (Customer VPC, PrivateLink, Secure Cluster Connectivity)
|   +-- Azure (VNet Injection, SCC, Hub-Spoke)
|   +-- GCP (GKE-based runtime, Private Service Connect)
|   +-- Multi-Cloud (Delta Sharing, Terraform, Hub-Spoke)
|
+-- Integrations
    +-- BI: Power BI, Tableau
    +-- Streaming: Kafka, Event Hubs
    +-- Transform: dbt
    +-- Orchestration: Airflow, Lakeflow Jobs
    +-- IaC: Terraform, DABs
    +-- Federation: Snowflake, Redshift, BigQuery, etc.
```

---

*Research compiled: 2026-03-07*
*Branch: claude/review-signavio-url-HffM8*
