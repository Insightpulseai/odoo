# Lakehouse -- Constitution

> **Version**: 1.0.0
> **Status**: Active
> **Last Updated**: 2026-03-08

---

## Purpose

The lakehouse is the self-hosted data platform for InsightPulse AI. It provides medallion-architecture data processing, SQL warehousing, and ML model tracking using exclusively open-source components. This constitution defines the non-negotiable rules that govern all lakehouse artifacts, infrastructure, and runtime behavior.

---

## Non-Negotiables

### 1. Self-Hosted Only, No Cloud Vendor Lock-In

Every component in the lakehouse stack must be deployable on infrastructure we own (DigitalOcean droplets, on-prem, or equivalent). No managed cloud services (Databricks SaaS, AWS Glue, Azure Synapse, Google BigQuery) may be introduced as runtime dependencies.

**Allowed**: Self-hosted OSS on our own VMs, S3-compatible storage (MinIO), self-managed PostgreSQL.

**Prohibited**: Any component that requires a vendor account to function at runtime (Databricks Runtime, Snowflake, AWS EMR as a service).

---

### 2. Medallion Architecture is Mandatory

All data flowing through the lakehouse must follow the Bronze-Silver-Gold layering model.

| Layer | Purpose | Storage Path |
|-------|---------|--------------|
| **Bronze** | Raw ingested data, unmodified from source | `s3://lakehouse/bronze/` |
| **Silver** | Cleaned, normalized, deduplicated, schema-conformant | `s3://lakehouse/silver/` |
| **Gold** | Business-ready aggregates, embeddings, analytics marts | `s3://lakehouse/gold/` |

No table may skip a layer. Bronze data must exist before Silver can be produced from it, and Silver before Gold.

---

### 3. Contracts-First: Every Delta Table Requires a YAML Contract

Every Delta table in the lakehouse must have a corresponding YAML contract file in `contracts/delta/`. The contract is the source of truth for:

- Column names, types, and nullability
- Partitioning strategy
- Primary key and merge key definitions
- Data retention policy

A table without a contract is not a valid lakehouse table. The CI pipeline (`scripts/lakehouse/validate_contracts.py`) must pass before any schema change is merged.

---

### 4. Lakehouse is Separate from Odoo

The lakehouse and Odoo are distinct subsystems that share PostgreSQL as a common storage engine but operate on different schemas and databases.

| System | Database | Purpose |
|--------|----------|---------|
| Odoo | `odoo` / `odoo_dev` | ERP transactional data |
| Lakehouse | `lakehouse` | Analytical data, RAG, embeddings |
| MLflow | `mlflow` | Model tracking metadata |
| n8n | `n8n` | Workflow orchestration metadata |

Odoo data enters the lakehouse only via explicit ingestion pipelines (Bronze layer). The lakehouse never writes back to Odoo databases.

---

### 5. All Components Must Be Open-Source

Every software component in the lakehouse stack must be licensed under an OSI-approved open-source license.

**Accepted licenses**: Apache-2.0, MIT, BSD-2-Clause, BSD-3-Clause, LGPL-3.0, MPL-2.0, PostgreSQL License.

**Current stack**:

| Component | License | Version |
|-----------|---------|---------|
| Apache Spark | Apache-2.0 | 3.5 |
| Delta Lake | Apache-2.0 | 2.4.0 |
| Trino | Apache-2.0 | latest |
| MinIO | AGPL-3.0 | latest |
| MLflow | Apache-2.0 | latest |
| PostgreSQL | PostgreSQL License | 15 |
| n8n | Sustainable Use License (self-hosted) | latest |

If a component changes its license to a non-OSS license, it must be replaced within one release cycle.

---

### 6. Data Retention is Per-Contract, Not Global

Each Delta table contract specifies its own `retention_days` value. There is no global retention policy. This allows Bronze raw data to have long retention (365+ days) while intermediate Silver tables can have shorter retention if appropriate.

The `retention_days` field in each contract YAML governs how long data is kept before vacuum operations may remove it.

---

### 7. Immutable Bronze Layer

Bronze data is append-only. Once a row is written to the Bronze layer, it is never updated or deleted (except by retention-based vacuum). All corrections and transformations happen in the Silver layer.

---

### 8. Multi-Tenant by Default

All tables must include a `tenant_id` column of type `uuid`. Queries without tenant scoping are prohibited in application code. The `tenant_id` column is present in all four existing contracts and must be present in any new contract.

---

## Enforcement

- **CI Gate**: `scripts/lakehouse/validate_contracts.py` validates all contracts on every PR.
- **Schema Drift Detection**: `scripts/lakehouse/coverage_audit.py` reports coverage gaps.
- **Docker Compose Validation**: `infra/lakehouse/compose.lakehouse.yml` is the canonical service definition.

---

## Amendment Process

Changes to this constitution require:

1. A PR modifying this file with a clear rationale in the PR description.
2. Evidence that the change does not violate any existing contract.
3. Update to `spec/lakehouse/tasks.md` if the change introduces new work.
