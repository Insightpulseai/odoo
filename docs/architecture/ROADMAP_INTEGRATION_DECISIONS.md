# Roadmap Integration Decisions

## Decision 1: Native PostgreSQL logical replication for operational mirror

**Status:** Accepted

**Context:** Odoo's data needs to be available in near-real-time for frontends, Foundry agents, and external APIs. The operational mirror target is self-hosted Supabase (PostgreSQL).

**Decision:** Use native PostgreSQL logical replication from Azure Database for PostgreSQL (flexible server) to Supabase's PostgreSQL instance.

**Rationale:**
- Native PG-to-PG, no middleware required
- Sub-second latency
- Azure Database for PostgreSQL supports logical replication with `wal_level=logical`
- Eliminates n8n as a data replication layer

**Prerequisites:**
- Set `wal_level=logical` on Azure PG source
- Grant replication permissions to the replication user
- Ensure network path between Azure PG and Supabase VM
- Monitor WAL growth and IOPS during initial sync

**Supersedes:** n8n-based CDC workflow for Odoo → Supabase data sync.

---

## Decision 2: Fabric mirroring for analytics distribution

**Status:** Accepted

**Context:** Odoo's operational data needs to be available in Databricks for governed analytics, data products, executive dashboards, and decision apps.

**Decision:** Use Microsoft Fabric Database Mirroring from Azure Database for PostgreSQL into OneLake. Databricks consumes OneLake through the documented Azure Databricks serverless compute integration path.

**Rationale:**
- Low-cost, low-latency mirroring into Delta/Parquet format
- Read-only SQL analytics endpoint over mirrored tables
- Eliminates custom JDBC extract jobs
- Continuous replication, not batch

**Prerequisites:**
- Fabric workspace provisioned (F2 SKU minimum)
- Azure PG source configured for mirroring (WAL + snapshot overhead)
- Databricks serverless compute with appropriate network/access to OneLake
- Monitor source DB pressure during initial snapshot

**Supersedes:** Databricks JDBC extract from Odoo PostgreSQL.

**Note:** Do not assume Unity Catalog natively mounts OneLake without validating the specific integration path in your environment. Use the documented OneLake integration via Databricks serverless compute.

---

## Decision 3: Plane as workflow projection and command surface only

**Status:** Accepted

**Context:** Plane (self-hosted) is the project management UI for work tracking, cycles, sprints, and team coordination. It needs access to roadmap initiative data but must not become a second source of truth.

**Decision:** Plane participates via webhook/API as a command source and projection target. It is not co-authoritative with Odoo.

**Rationale:**
- Unrestricted bidirectional sync creates dual authority and conflict resolution debt
- Plane's REST API and webhooks support clean integration without shared write ownership
- Odoo validates and persists all canonical state transitions

**Integration pattern:**
- Plane → webhook → n8n → Odoo API (command: status change, reassignment, etc.)
- Odoo → n8n → Plane API (projection: updated status, assignments, milestones)
- Conflict resolution: Odoo wins, Plane is overwritten on next sync

---

## Decision 4: Supabase as read model only

**Status:** Accepted

**Context:** Self-hosted Supabase provides PostgREST, realtime subscriptions, Auth/RLS, and Edge Functions. It serves frontends, Foundry agents, and external API consumers.

**Decision:** Supabase is a read-optimized operational mirror. No direct client writes to canonical roadmap tables.

**Rationale:**
- Prevents split-brain between Odoo canonical tables and Supabase copies
- Supabase Postgres Changes provides realtime subscriptions for the roadmap frontend
- At higher scale, migrate live UI to Supabase Broadcast

**Write path for clients:**
- Clients that need to modify roadmap data must write through Odoo API (directly or via Supabase Edge Function proxy)
- Supabase Edge Functions may proxy writes to Odoo API, but must not write directly to mirrored canonical tables

---

## Decision 5: Databricks Apps for analytical/decision surfaces only

**Status:** Accepted

**Context:** Databricks Apps (GA) support governed interactive data/AI applications. They are a natural fit for executive dashboards, campaign analytics, and decision tools.

**Decision:** Use Databricks Apps for governed analytical and decision experiences. They are not the canonical transactional system for roadmap authoring.

**Rationale:**
- Databricks Apps are optimized for analytical workloads, not transactional CRUD
- Roadmap authoring belongs in Odoo (operational) and Plane (workflow)
- Databricks consumes curated Gold data products, not raw operational mirrors

**Examples of valid Databricks App use:**
- Executive KPI dashboard
- Campaign ROI explorer
- Financial health monitor
- Customer segmentation browser

**Not valid:**
- Roadmap initiative creation/editing
- Status transitions
- Milestone management

---

*Last updated: 2026-03-17*
