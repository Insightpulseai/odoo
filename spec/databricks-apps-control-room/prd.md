# Databricks Apps Control Room — Product Requirements

> Real-time monitoring and management of data connectors and pipelines.

## Problem

With 5 connector sources (Notion, GitHub, Odoo PG, Azure RG, generic) syncing data through DLT pipelines, the team needs:
- Visibility into sync status across all connectors
- Immediate alerting on failures
- Ability to trigger replays from checkpoints
- Schema drift detection and resolution
- SLA tracking for data freshness

## Solution: Connector Control Room

A Databricks App providing a unified dashboard for all connector operations.

### Features

#### 1. Sync Status Dashboard
- Real-time status of all 5 connector sync jobs
- Last successful sync timestamp per source
- Current run status (running/succeeded/failed/pending)
- Data volume metrics (rows synced, bytes transferred)

#### 2. Failure Management
- Failure alert feed with error details
- Root cause categorization (auth, schema, network, data)
- One-click replay from last checkpoint
- Failure trend analysis (recurring vs. transient)

#### 3. Schema Drift Detection
- Automatic detection of source schema changes
- Impact analysis (which downstream tables affected)
- Drift resolution workflow (approve, reject, auto-migrate)
- Schema version history

#### 4. SLA Tracking
- Data freshness SLAs per source (e.g., Notion < 15min, GitHub < 1hr)
- SLA breach alerts
- Historical SLA compliance reports
- Freshness heatmap across all sources

#### 5. Replay Management
- Checkpoint browser (list available replay points)
- Selective replay (single source or all)
- Replay progress tracking
- Post-replay validation

### Technical Architecture

| Component | Technology | Notes |
|-----------|-----------|-------|
| UI Framework | Streamlit | Databricks Apps native |
| Data Source | Unity Catalog gold tables | `connector_state`, `sync_metrics`, `schema_versions` |
| Alerting | Databricks SQL alerts | Email + Slack integration |
| Auth | Databricks workspace SSO | No separate auth |
| Deployment | DABs | `infra/databricks/src/apps/control_room/` |

### Users
- **Primary**: Data engineers (daily monitoring)
- **Secondary**: Platform team (SLA reporting)
- **Tertiary**: Engineering leads (incident review)

### Non-Goals
- NOT a general-purpose BI tool (that's Superset)
- NOT for business users directly (they use Superset dashboards)
- NOT for managing Odoo data (that's Odoo itself)
- NOT for CI/CD monitoring (that's GitHub Actions)
