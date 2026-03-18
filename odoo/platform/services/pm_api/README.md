# Process Mining API

Local-first query service for Odoo Copilot process mining insights.

## Overview

This API provides endpoints to query process mining data from the `pm.*` schema in your Odoo PostgreSQL database. It's designed to run locally alongside your Odoo instance, keeping all sensitive process data within your infrastructure.

## Prerequisites

1. PostgreSQL with the `pm.*` schema applied:
   ```bash
   psql -d odoo_dev -f db/process_mining/001_pm_schema.sql
   psql -d odoo_dev -f db/process_mining/010_p2p_etl.sql
   ```

2. Python 3.11+

## Installation

```bash
cd services/pm_api
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Configuration

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
# Edit .env with your database connection
```

## Running

```bash
export PM_DB_DSN="postgres://odoo:odoo@localhost:5432/odoo_dev"
uvicorn app.main:app --host 0.0.0.0 --port 8787
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/pm/{process}/summary` | GET | Process summary (cases, duration, etc.) |
| `/pm/{process}/bottlenecks` | GET | Top edges by latency |
| `/pm/{process}/variants` | GET | Top variants by frequency |
| `/pm/{process}/cases/{id}` | GET | Case detail with timeline |
| `/pm/{process}/deviations` | GET | List deviations |
| `/pm/{process}/etl/run` | POST | Trigger incremental ETL |

## Example Queries

```bash
# Process summary
curl http://localhost:8787/pm/p2p/summary

# Top 5 bottlenecks
curl "http://localhost:8787/pm/p2p/bottlenecks?limit=5"

# Top variants
curl "http://localhost:8787/pm/p2p/variants?limit=10"

# Case detail
curl http://localhost:8787/pm/p2p/cases/p2p:po:123

# High severity deviations
curl "http://localhost:8787/pm/p2p/deviations?severity=high&limit=20"

# Run ETL
curl -X POST http://localhost:8787/pm/p2p/etl/run
```

## Docker

```bash
docker build -t pm-api .
docker run -e PM_DB_DSN="postgres://odoo:odoo@host.docker.internal:5432/odoo_dev" -p 8787:8787 pm-api
```

## Development

```bash
pip install -e ".[dev]"
pytest
```
