# Databricks Data Engineering Workbench

DAB-first repo structure for ETL, DLT, Jobs, and optional agent systems.

> **See also**: [Data Science Platform](../../docs/databricks/DATA_SCIENCE_PLATFORM.md) | [Data Science Agent](../../docs/databricks/DATA_SCIENCE_AGENT.md)

## Structure

```
infra/databricks/
├── databricks.yml              # DAB root configuration (required)
├── resources/                  # IaC resource definitions
│   ├── jobs.yml               # Job definitions
│   ├── schemas.yml            # Unity Catalog schemas
│   ├── pipelines/             # DLT pipeline definitions
│   ├── clusters/              # Cluster configurations
│   ├── schedules/             # Schedule definitions
│   └── permissions/           # UC grants and permissions
├── src/workbench/             # Installable Python package
│   ├── config/                # Configuration management
│   ├── connectors/            # Data source connectors
│   ├── bronze/                # Raw data ingestion
│   ├── silver/                # Data transformation
│   ├── gold/                  # Business marts
│   ├── dlt/                   # Delta Live Tables pipelines
│   ├── observability/         # Data quality & lineage
│   └── utils/                 # Shared utilities
├── notebooks/                 # Thin wrappers for Databricks UI
├── sql/                       # Unity Catalog DDL
├── tests/                     # Unit and integration tests
├── config/                    # Environment-specific configs
├── scripts/                   # Automation scripts
└── agent_systems/             # Agent Bricks boundary
```

## Quick Start

### 1. Validate Bundle

```bash
cd infra/databricks
databricks bundle validate
```

### 2. Deploy to Dev

```bash
databricks bundle deploy --target dev
```

### 3. Run Tests

```bash
./scripts/test.sh
```

## Environment Targets

| Target  | Catalog      | Description                    |
|---------|--------------|--------------------------------|
| dev     | dev_ppm      | Development workspace          |
| staging | staging_ppm  | Pre-production validation      |
| prod    | ppm          | Production (service principal) |

## Medallion Architecture

### Bronze (Raw Data)
- Notion API sync
- Azure Resource Graph ingestion
- Watermark-based incremental loads

### Silver (Transformed)
- Schema normalization
- Data type casting
- Deduplication

### Gold (Business Marts)
- Budget vs Actual metrics
- Forecast calculations
- Risk summaries
- Control Room status

## CI/CD

GitHub Actions workflows handle:
- Bundle validation on PR
- Deploy to dev on merge to main
- Deploy to staging on release candidate tags
- Deploy to prod on release tags

## Local Development

```bash
# Install dependencies
pip install -e ".[dev]"

# Format code
./scripts/fmt.sh

# Run linting
./scripts/lint.sh

# Run tests
./scripts/test.sh

# Validate bundle
./scripts/bundle-validate.sh
```
