# IPAI Data Connectors — Constitution

> **Version**: 1.0.0
> **Status**: Active
> **Last Updated**: 2026-01-25
> **Related Docs**: [prd.md](prd.md) | [plan.md](plan.md) | [tasks.md](tasks.md)

---

## 1. Purpose

IPAI Data Connectors is a self-hosted, open connector platform that delivers Fivetran-style ELT into a Databricks-style lakehouse and Odoo CE/OCA stack. This constitution defines the non-negotiable rules, architectural constraints, and governance principles that all connector implementations MUST follow.

---

## 2. Non-Negotiable Rules

### 2.1 License & Legal Compliance

| Rule ID | Rule | Rationale |
|---------|------|-----------|
| LC-001 | **MUST NOT** copy, reverse-engineer, or reuse proprietary Fivetran connector code | License compliance |
| LC-002 | **MUST** build against official source APIs only (Google, GitHub, etc.) | Clean-room implementation |
| LC-003 | **MUST** comply with each provider's API Terms of Service | Legal compliance |
| LC-004 | **MUST** use OSS-compatible licenses (MIT, Apache-2.0) for all connector code | Open source compatibility |
| LC-005 | **MUST NOT** store OAuth tokens or API keys in Git repositories | Security compliance |

### 2.2 Architecture Constraints

| Rule ID | Rule | Rationale |
|---------|------|-----------|
| AC-001 | All connectors **MUST** be Dockerized and horizontally scalable | Deployment consistency |
| AC-002 | Control plane data **MUST** reside in Supabase (configs, state, runs) | Single source of truth |
| AC-003 | Secrets **MUST** be stored in Supabase Vault or equivalent secure storage | Security |
| AC-004 | All connector outputs **MUST** follow Bronze/Silver/Gold lakehouse pattern | Data architecture |
| AC-005 | Connectors **MUST** support idempotent upserts for at-least-once delivery | Reliability |
| AC-006 | All API calls **MUST** implement exponential backoff with quota awareness | Rate limit compliance |

### 2.3 Data Flow Rules

| Rule ID | Rule | Rationale |
|---------|------|-----------|
| DF-001 | Bronze layer: raw JSON/CSV with minimal transformation | Auditability |
| DF-002 | Silver layer: deduplicated, typed Parquet with partitioning | Query performance |
| DF-003 | Gold layer: business-ready views in Postgres/Supabase | BI accessibility |
| DF-004 | All records **MUST** include `emitted_at`, `source`, `stream`, `cursor` metadata | Lineage tracking |
| DF-005 | Schema changes **MUST** trigger automated alerts before breaking downstream | Stability |

### 2.4 Connector Implementation Rules

| Rule ID | Rule | Rationale |
|---------|------|-----------|
| CI-001 | Each connector **MUST** have a YAML spec defining source_type, auth, sync_mode, schedule | Declarative config |
| CI-002 | Connectors **MUST** implement incremental sync where supported by source API | Cost efficiency |
| CI-003 | Full sync **MUST** be available as fallback for all connectors | Recovery capability |
| CI-004 | Connector state **MUST** persist cursor/bookmark for resumability | Fault tolerance |
| CI-005 | All connector code **MUST** pass linting, type checks, and unit tests before merge | Code quality |

### 2.5 Security & Access Control

| Rule ID | Rule | Rationale |
|---------|------|-----------|
| SA-001 | All network traffic **MUST** use HTTPS/TLS encryption | Data in transit security |
| SA-002 | Control plane tables **MUST** enforce Supabase RLS policies | Access control |
| SA-003 | OAuth tokens **MUST** support automated refresh before expiry | Reliability |
| SA-004 | Connector workers **MUST NOT** have direct access to secrets; fetch via secure RPC | Least privilege |
| SA-005 | All credential rotations **MUST** be logged with timestamp and actor | Audit trail |

---

## 3. Naming Conventions

### 3.1 Connector Naming

```
ipai_connector_<source_type>
```

Examples:
- `ipai_connector_ga4`
- `ipai_connector_google_ads`
- `ipai_connector_github`
- `ipai_connector_odoo`

### 3.2 Table Naming

| Layer | Pattern | Example |
|-------|---------|---------|
| Bronze | `raw_<source>_<stream>` | `raw_ga4_events` |
| Silver | `<source>_<entity>` | `ga4_sessions` |
| Gold | `gold_<domain>_<entity>` | `gold_marketing_campaigns` |

### 3.3 Job Naming

```
sync_<source>_<stream>_<mode>
```

Examples:
- `sync_ga4_events_incremental`
- `sync_github_commits_full`

---

## 4. Governance Principles

### 4.1 Change Management

1. **Spec-First**: All new connectors MUST have an approved YAML spec before implementation
2. **Review Required**: All connector changes require code review by at least one data engineer
3. **Staging Validation**: All connectors MUST pass staging sync before production deployment
4. **Rollback Ready**: Every deployment MUST have documented rollback procedure

### 4.2 Quality Gates (CI Enforcement)

| Gate | Criteria | Block Merge |
|------|----------|-------------|
| Lint | `black`, `isort`, `flake8` pass | Yes |
| Type Check | `mypy` or `pyright` pass | Yes |
| Unit Tests | 80%+ coverage on connector logic | Yes |
| Dry-Run Sync | Sandbox sync completes without error | Yes |
| Schema Validation | YAML spec validates against schema | Yes |
| Data Quality | Row counts, null thresholds within limits | Yes |

### 4.3 SLA Definitions

| Tier | Sync Frequency | Max Latency | Retry Policy |
|------|----------------|-------------|--------------|
| Critical | Hourly | 15 min | 5 retries, 2^n backoff |
| Standard | Daily | 2 hours | 3 retries, 2^n backoff |
| Best Effort | Weekly | 24 hours | 2 retries, linear backoff |

---

## 5. Scope Boundaries

### 5.1 In Scope

- Self-hosted connector engine with Docker workers
- Google ecosystem connectors (GA4, Ads, GSC, YouTube, BigQuery)
- DevOps connectors (GitHub, Vercel, Supabase, DigitalOcean)
- Odoo CE/OCA extraction and integration
- Lakehouse Bronze/Silver/Gold architecture
- Agent/MCP integration for automation
- Supabase-based control plane

### 5.2 Out of Scope

- Multi-tenant SaaS offering (single-tenant focus)
- Recreating full Fivetran connector catalog
- Databricks notebooks or Unity Catalog replication
- Real-time CDC/streaming (batch-first)
- Proprietary Fivetran or Databricks code usage

---

## 6. Failure Modes & Mitigation

| Failure Mode | Impact | Mitigation |
|--------------|--------|------------|
| API rate limit exceeded | Sync delays | Per-connector quota config, exponential backoff |
| OAuth token expired | Sync failure | Proactive refresh, alert 24h before expiry |
| Schema drift in source | Data quality issues | Schema introspection, automated migration scripts |
| Worker crash mid-sync | Data loss risk | Checkpoint-based resume, idempotent writes |
| Destination full | Sync blocked | Storage monitoring, auto-archive old Bronze data |
| Secret leak | Security breach | Vault-only storage, CI secret scan, immediate rotation |

---

## 7. Compliance & Audit

### 7.1 Logging Requirements

- All connector runs MUST log: start_time, end_time, rows_processed, status, error_summary
- All credential access MUST log: timestamp, actor, secret_id, action
- Logs MUST be retained for 90 days minimum

### 7.2 Data Retention

| Layer | Retention | Archive Policy |
|-------|-----------|----------------|
| Bronze | 30 days | Archive to cold storage |
| Silver | 1 year | Partition pruning |
| Gold | Indefinite | No auto-delete |

### 7.3 Access Audit

- Monthly review of connector access permissions
- Quarterly review of active OAuth tokens
- Annual review of data retention compliance

---

## 8. Success Criteria

| Metric | Target | Measurement |
|--------|--------|-------------|
| Sync success rate | ≥ 95% | Successful runs / total runs |
| Time-to-add-connector | ≤ 3 days | From spec approval to staging deploy |
| Time-to-dashboard | ≤ 1 week | From new source to production dashboard |
| Ad-hoc ETL reduction | ≥ 70% | Custom scripts replaced by connectors |
| Odoo EE parity coverage | ≥ 80% | Data needs met by self-hosted stack |

---

## 9. Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | 2026-01-25 | IPAI Team | Initial constitution |

---

*This constitution is enforced via CI workflow `spec-kit-enforce.yml`. Violations block merge to main.*
