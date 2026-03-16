# Supabase Platform Review

> Review date: January 31, 2026
> Project: `superset` (Pro plan)
> Branch: `main` (Production)

This document reviews the current Supabase implementation against the latest platform capabilities documented at [supabase.com/docs/guides/platform](https://supabase.com/docs/guides/platform).

---

## Executive Summary

| Area | Status | Notes |
|------|--------|-------|
| Edge Functions | ✅ Implemented | 5 functions deployed |
| Database Schemas | ✅ Implemented | ops, advisor, mirror schemas |
| RLS Policies | ✅ Implemented | All tables protected |
| pg_cron Scheduling | ✅ Implemented | 7 cron jobs configured |
| Vault for Secrets | ✅ Implemented | Used for GitHub credentials |
| Database Branching | ⚠️ Not Used | Available on Pro plan |
| GitHub Integration | ✅ Connected | `jgtolentino/odoo-ce` |
| Vector/AI Features | 🔲 Not Implemented | New alpha features available |
| CDC Pipelines | 🔲 Not Implemented | New alpha feature |

---

## 1. Platform Features Currently Used

### 1.1 Edge Functions

| Function | Purpose | Cron Scheduled |
|----------|---------|----------------|
| `repo-auditor` | Repository governance checks | Yes (hourly) |
| `health-check` | System health monitoring | Yes (5 min) |
| `slack-alert` | Alert notifications | Yes (1 min) |
| `drift-detection` | Config drift detection | Yes (hourly) |
| `odoo-proxy` | Controlled Odoo writes | On-demand |

**Recommendation**: Consider the new [MCP Server deployment on Edge Functions](https://github.com/supabase/mcp-use) for AI agent integration.

### 1.2 Database Architecture

```
┌─────────────────────────────────────────────────┐
│ Schemas                                         │
├─────────────────────────────────────────────────┤
│ public   │ Standard application tables          │
│ ops      │ Observability telemetry              │
│ advisor  │ Governance checks & findings         │
│ mirror   │ Odoo read replicas                   │
└─────────────────────────────────────────────────┘
```

This aligns with Supabase best practices for schema organization.

### 1.3 Extensions in Use

| Extension | Purpose |
|-----------|---------|
| `pg_cron` | Job scheduling |
| `pgsodium` | Encryption for Vault |
| `vault` | Secret management |
| `pg_net` | HTTP requests from SQL |

### 1.4 CI/CD Integration

- **GitHub App**: Connected to `jgtolentino/odoo-ce`
- **Workflows**: `supabase-pr-checks`, `supabase-deploy`
- **Environments**: staging → production gating

---

## 2. Platform Features NOT Yet Implemented

### 2.1 Database Branching (Recommended)

**Status**: Available but not configured

The Supabase dashboard shows Branching is available on this Pro plan project. Current state:
- ✅ Production branch: `main` (updated Jan 25, 2026)
- ❌ No persistent branches (staging)
- ❌ No preview branches

**Recommendation**: Implement branching for safer schema migrations:

```bash
# Create staging persistent branch
supabase branches create staging --persistent

# Create preview branch for feature work
supabase branches create feature/new-advisor-checks
```

**Benefits**:
- Test migrations before production
- Preview branches for PR reviews
- Rollback capability
- Parallel development without conflicts

### 2.2 Vector Buckets (Alpha)

**Status**: Not implemented

New Supabase feature (public alpha) for cold storage of AI embeddings:
- Built on Amazon S3 Vectors
- Query engine for similarity search
- Cost-effective for large embedding collections

**Potential Use Cases**:
- Store AI agent memory embeddings
- Document embeddings for RAG
- Audit log embeddings for semantic search

### 2.3 Analytical Storage Buckets (Alpha)

**Status**: Not implemented

Specialized storage built on Apache Iceberg and AWS S3 Tables:
- Columnar storage for analytical workloads
- Better performance for `ops.*` historical queries
- Cost-effective for time-series data

**Potential Use Case**: Archive old `ops.events` and `ops.health` records.

### 2.4 CDC Pipelines (Private Alpha)

**Status**: Not available (private alpha)

Change Data Capture pipeline for replicating data to external destinations:
- Continuous replication to Iceberg
- Event streaming to external systems

**Future Use**: Could replace current mirror sync pattern with real-time CDC.

### 2.5 Stripe Sync Engine (New)

**Status**: Not implemented

One-click integration for syncing Stripe data:
- Customers, subscriptions, invoices, payments
- Query with standard SQL
- Real-time sync

**Potential Use**: If using Stripe for payments, this replaces custom sync logic.

---

## 3. Data API Upgrade

The Supabase Data API was upgraded to **PostgREST v14** with improvements:
- Better query performance
- Enhanced filtering options
- Improved error messages

**Action**: Verify `@supabase/supabase-js` client is updated to latest version.

---

## 4. Security Review

### 4.1 Current Security Posture

| Control | Status |
|---------|--------|
| RLS enabled on all tables | ✅ |
| Anonymous sign-ins disabled | ✅ |
| Service role restricted to Edge Functions | ✅ |
| Secrets in Vault | ✅ |
| JWT expiry configured (3600s) | ✅ |
| Refresh token rotation | ✅ |

### 4.2 Recommendations

1. **Enable MFA**: Consider enabling MFA for dashboard access
2. **Audit Logging**: Verify `auth.audit_log_entries` retention
3. **Network Restrictions**: Consider IP allowlisting for production

---

## 5. Branching Implementation Plan

### Phase 1: Staging Branch (Recommended)

```bash
# 1. Create persistent staging branch
supabase branches create staging --persistent

# 2. Update GitHub workflow to deploy to staging first
# Edit .github/workflows/supabase-deploy.yml
```

Update CI/CD workflow:

```yaml
# .github/workflows/supabase-deploy.yml
jobs:
  deploy-staging:
    environment: staging
    steps:
      - uses: supabase/setup-cli@v1
      - run: supabase db push --branch staging

  deploy-production:
    needs: deploy-staging
    environment: production
    steps:
      - uses: supabase/setup-cli@v1
      - run: supabase db push --branch main
```

### Phase 2: Preview Branches for PRs

```yaml
# .github/workflows/supabase-pr-preview.yml
on:
  pull_request:
    paths:
      - 'supabase/migrations/**'

jobs:
  create-preview:
    steps:
      - run: |
          supabase branches create preview-${{ github.event.number }}
          supabase db push --branch preview-${{ github.event.number }}
```

---

## 6. Cost Optimization

### Current Cost Drivers

| Resource | Usage | Optimization |
|----------|-------|--------------|
| Edge Function invocations | ~5 functions × cron frequency | Consider batching health checks |
| Database storage | ops.events growing | Implement TTL cleanup (already in cron) |
| Compute | Standard Pro allocation | Adequate for current workload |

### Recommendations

1. **Consolidate cron jobs**: `health-check-full` and `slack-alert-check` could be merged
2. **Archive old data**: Move `ops.events` > 30 days to analytical storage when available
3. **Monitor Advisor**: Use `advisor.v_cost_anomalies` view to catch cost spikes

---

## 7. Action Items

| Priority | Action | Effort |
|----------|--------|--------|
| High | Enable database branching for staging | Low |
| High | Verify supabase-js client version | Low |
| Medium | Create preview branch workflow for PRs | Medium |
| Medium | Evaluate Vector Buckets for AI embeddings | Medium |
| Low | Plan CDC pipeline adoption (when GA) | Future |
| Low | Evaluate Stripe Sync if applicable | Low |

---

## 8. Deployment Options

### 8.1 Current Deployment: Managed (Recommended)

This project uses **Supabase Cloud (Pro plan)**, which is the recommended approach for:
- Production workloads requiring high availability
- Automatic updates and security patches
- Managed backups and disaster recovery
- Access to all platform features (Branching, Edge Functions, etc.)

### 8.2 Self-Hosting Considerations

Per [Supabase Self-Hosting Docs](https://supabase.com/docs/guides/self-hosting), self-hosting is appropriate when:
- Full control over data is required
- Compliance requirements prevent managed services
- Air-gapped or isolated environments needed

**Self-hosting requirements**:
- Minimum 8GB RAM, 25GB SSD
- Docker Compose deployment
- Production SMTP server (AWS SES recommended)
- S3-compatible storage for files
- Secrets manager for credentials

**Self-hosting limitations**:
- Database Branching not available
- No automatic updates
- Manual security patching
- Increased operational overhead

### 8.3 Hybrid Approach

For this project's architecture (Supabase + Odoo), consider:

| Component | Deployment |
|-----------|------------|
| Supabase (Control Plane) | Managed Cloud (Pro) |
| Odoo (System of Record) | Self-hosted or Odoo.sh |
| Edge Functions | Supabase managed |
| Vercel (Frontend) | Managed |

This hybrid approach provides:
- Enterprise observability without Enterprise pricing
- Full control over business data (Odoo)
- Managed infrastructure for platform components

### 8.4 Architecture Components

Supabase consists of these open-source components:

| Component | Purpose |
|-----------|---------|
| PostgreSQL | Core database |
| PostgREST | RESTful API layer |
| GoTrue | Authentication |
| Kong | API Gateway |
| Realtime | WebSocket subscriptions |
| Storage | File management |
| Edge Runtime | Serverless functions |

All components are MIT/Apache 2 licensed and can be self-hosted if needed.

---

## 9. References

- [Supabase Platform Docs](https://supabase.com/docs/guides/platform)
- [Supabase Deployment & Branching](https://supabase.com/docs/guides/deployment)
- [Supabase Self-Hosting](https://supabase.com/docs/guides/self-hosting)
- [Supabase Self-Hosting with Docker](https://supabase.com/docs/guides/self-hosting/docker)
- [Supabase January 2026 Developer Update](https://github.com/orgs/supabase/discussions/41796)
- [PostgREST v14 Changelog](https://github.com/PostgREST/postgrest/releases)
- [MCP Server on Edge Functions](https://github.com/supabase/mcp-use)

---

## Appendix: Current Architecture Alignment

This project implements several enterprise patterns without requiring Enterprise plan:

| Enterprise Feature | Our Implementation |
|-------------------|-------------------|
| Log Drains | `ops.events` table with retention |
| Observability | `ops.*` schema + Edge Functions |
| Governance | `advisor.*` schema with checks |
| Cost Control | Custom cost tracking views |
| Audit Trail | `ops.events` append-only log |

The architecture is designed to grow into Enterprise features without redesign (see `supabase/ARCHITECTURE.md`).
