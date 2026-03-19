# Supabase Feature Prioritization Rubric

**Status**: Active
**Created**: 2026-02-12
**Portfolio Initiative**: PORT-2026-011
**Evidence**: EVID-20260212-006

---

## Philosophy

**Build on substrate, replace apps.**

Supabase provides two distinct layers:
1. **Core Substrate**: PostgreSQL-based infrastructure that would require massive engineering effort to replicate
2. **Replaceable Apps**: UI layers and convenience features that can be substituted with custom solutions

This rubric guides build-vs-buy decisions to maximize leverage while minimizing vendor lock-in.

---

## Core Substrate (Never Replace)

These components are deeply integrated with PostgreSQL's wire protocol and represent years of engineering effort. Keep and build on top of them.

### 1. PostgreSQL 16 (Database Engine)
- **Why Core**: Industry-standard relational database with 30+ years of development
- **Wire Protocol**: Native PostgreSQL protocol (port 5432)
- **Vendor Lock-in**: Zero (standard SQL, pg_dump/pg_restore)
- **Custom Value**: Extensions (pgvector, pg_cron, pgroonga), RLS policies
- **Decision**: **KEEP** - Foundation of entire stack

### 2. PostgREST (Auto-Generated REST API)
- **Why Core**: Zero-config REST API from PostgreSQL schema
- **Wire Protocol**: HTTP/REST over PostgreSQL introspection
- **Vendor Lock-in**: Low (open-source PostgREST, self-hostable)
- **Custom Value**: Automatic API generation, RLS enforcement
- **Decision**: **KEEP** - Eliminates 90% of backend boilerplate

### 3. GoTrue (Authentication + RLS)
- **Why Core**: Tight integration with PostgreSQL RLS (Row-Level Security)
- **Wire Protocol**: JWT tokens validated at PostgreSQL layer
- **Vendor Lock-in**: Medium (GoTrue-specific JWT claims, can migrate to Auth0/Clerk)
- **Custom Value**: RLS policies tied to `auth.uid()`, SSO integration
- **Decision**: **KEEP** - RLS integration is irreplaceable

### 4. Realtime (Postgres Change Data Capture)
- **Why Core**: Native PostgreSQL logical replication
- **Wire Protocol**: WebSocket over pg_logical replication slots
- **Vendor Lock-in**: Medium (Realtime server is open-source, self-hostable)
- **Custom Value**: n8n triggers, Odoo sync, live dashboards
- **Decision**: **KEEP** - Powers automation workflows

### 5. Edge Functions (Deno Runtime)
- **Why Core**: Serverless compute with direct Supabase client integration
- **Wire Protocol**: Deno Deploy (V8 isolates)
- **Vendor Lock-in**: Low (standard Deno code, portable to Cloudflare Workers/Vercel)
- **Custom Value**: 42 Edge Functions for BIR filing, Plane sync, n8n bridge
- **Decision**: **KEEP** - Migration path exists but low ROI

### 6. Vault (Secrets Management)
- **Why Core**: PostgreSQL-native encrypted storage with RLS
- **Wire Protocol**: PostgreSQL `pgsodium` extension
- **Vendor Lock-in**: Low (pgsodium is open-source)
- **Custom Value**: API keys, OAuth tokens, encryption keys
- **Decision**: **KEEP** - Simpler than HashiCorp Vault

### 7. pg_vector (Embeddings)
- **Why Core**: PostgreSQL extension for vector similarity search
- **Wire Protocol**: Native PostgreSQL types and indexes
- **Vendor Lock-in**: Zero (standard pg_vector extension)
- **Custom Value**: AI-powered search, semantic matching
- **Decision**: **KEEP** - Industry standard for embeddings

---

## Replaceable Apps (Build Parity)

These are UI layers or convenience features that can be substituted with custom solutions tailored to our workflows.

### 1. Studio (Database Admin UI)
- **Why Replaceable**: Generic CRUD UI, not workflow-specific
- **Replacement**: Custom Odoo admin module (`ipai_supabase_admin`)
- **Benefits**: Odoo-native UI, custom workflows, RLS visualization
- **Migration Effort**: Medium (2-3 weeks for basic CRUD)
- **Decision**: **REPLACE** - Better integration with Odoo

### 2. Branching (Preview Environments)
- **Why Replaceable**: Git-based migrations achieve same goal
- **Replacement**: `supabase/migrations/` + CI/CD pipeline
- **Benefits**: Version control, rollback capability, audit trail
- **Migration Effort**: Low (already using migrations)
- **Decision**: **REPLACE** - Already using git-based migrations

### 3. CLI (Deployment Tooling)
- **Why Replaceable**: Generic deployment interface
- **Replacement**: Custom `scripts/supabase/` automation scripts
- **Benefits**: Odoo-specific deployment workflows, multi-environment handling
- **Migration Effort**: Low (1 week for core commands)
- **Decision**: **REPLACE** - Custom scripts for Odoo workflows

### 4. Storage (Large File Hosting)
- **Why Replaceable**: S3-compatible API
- **Replacement**: MinIO (self-hosted) or DigitalOcean Spaces
- **Benefits**: Cost optimization ($5/TB vs $10/TB), no egress fees
- **Migration Effort**: Medium (2 weeks for migration scripts)
- **Decision**: **REPLACE** - Cost savings at scale

---

## Decision Matrix

Use this scoring system to classify new Supabase features:

| Criteria | Core (3) | Strategic (2) | Tactical (1) | Replace (0) |
|----------|----------|---------------|--------------|-------------|
| **Wire Protocol Dependency** | PostgreSQL native | HTTP/REST standard | Proprietary API | UI layer |
| **Vendor Lock-in** | Zero (open standard) | Low (open-source) | Medium (migratable) | High (vendor-specific) |
| **Customization Needs** | Minimal (works OOTB) | Moderate (config) | High (requires code) | Extreme (full rebuild) |
| **Engineering Effort** | Years (impossible) | Months (hard) | Weeks (feasible) | Days (easy) |

**Scoring**:
- **9-12 points**: KEEP (Core Substrate)
- **6-8 points**: KEEP (Strategic Value)
- **3-5 points**: EVALUATE (Case-by-case)
- **0-2 points**: REPLACE (Build Parity)

---

## Examples

### Example 1: Authentication (GoTrue)

| Criterion | Score | Rationale |
|-----------|-------|-----------|
| Wire Protocol | 3 | JWT validated at PostgreSQL RLS layer |
| Vendor Lock-in | 2 | Open-source GoTrue, migratable to Auth0 |
| Customization | 3 | Works OOTB with RLS policies |
| Engineering Effort | 3 | Years to replicate RLS integration |
| **Total** | **11** | **KEEP** (Core Substrate) |

**Decision**: Keep GoTrue. RLS integration with `auth.uid()` is irreplaceable without massive engineering effort.

---

### Example 2: Storage (S3-Compatible)

| Criterion | Score | Rationale |
|-----------|-------|-----------|
| Wire Protocol | 1 | S3-compatible API (industry standard) |
| Vendor Lock-in | 1 | Migratable to any S3 provider |
| Customization | 1 | Generic file storage, no workflow logic |
| Engineering Effort | 0 | Days to migrate to MinIO/Spaces |
| **Total** | **3** | **REPLACE** (Build Parity) |

**Decision**: Replace with MinIO for cost optimization. S3 API is standardized, migration scripts straightforward.

---

### Example 3: Realtime (Change Data Capture)

| Criterion | Score | Rationale |
|-----------|-------|-----------|
| Wire Protocol | 3 | PostgreSQL logical replication |
| Vendor Lock-in | 2 | Open-source Realtime server |
| Customization | 3 | Powers n8n triggers, Odoo sync |
| Engineering Effort | 3 | Years to replicate CDC + WebSocket |
| **Total** | **11** | **KEEP** (Core Substrate) |

**Decision**: Keep Realtime. Powers critical automation workflows (n8n triggers, Plane sync, live dashboards).

---

### Example 4: Studio (Admin UI)

| Criterion | Score | Rationale |
|-----------|-------|-----------|
| Wire Protocol | 0 | UI layer over PostgREST |
| Vendor Lock-in | 0 | Vendor-specific UI |
| Customization | 0 | Generic CRUD, not workflow-specific |
| Engineering Effort | 1 | Weeks to build Odoo admin module |
| **Total** | **1** | **REPLACE** (Build Parity) |

**Decision**: Replace with `ipai_supabase_admin` Odoo module. Better workflow integration, RLS visualization, audit trails.

---

## Current Feature Audit (42 Edge Functions)

**Methodology**: Classify all 42 Edge Functions using the decision matrix.

### Core Substrate Usage (KEEP)

**PostgreSQL (42/42 functions)**:
- All Edge Functions use Supabase client for database access
- Standard SQL queries, RLS policies enforced
- Decision: **KEEP** - Foundation of all operations

**PostgREST (38/42 functions)**:
- Auto-generated REST API for CRUD operations
- Functions: `plane-sync`, `bir-forms-lookup`, `email-processor`, `task-bus`
- Decision: **KEEP** - Eliminates backend boilerplate

**GoTrue Auth (35/42 functions)**:
- JWT validation, RLS policy enforcement
- Functions: User-facing APIs require authentication
- Decision: **KEEP** - RLS integration irreplaceable

**Realtime (12/42 functions)**:
- n8n triggers: `task-bus`, `plane-sync`, `odoo-sync`
- Live dashboards: `analytics-dashboard`, `okr-tracker`
- Decision: **KEEP** - Powers automation

**Edge Functions Runtime (42/42)**:
- All serverless compute in Deno
- Migration path: Cloudflare Workers, Vercel Functions
- Decision: **KEEP** - Low lock-in, high value

**Vault (8/42 functions)**:
- API key storage: `bir-api-client`, `plane-sync`, `slack-connector`
- OAuth tokens: `zoho-mail-bridge`, `google-workspace-sync`
- Decision: **KEEP** - Simpler than alternatives

**pg_vector (3/42 functions)**:
- Semantic search: `knowledge-base-search`, `document-similarity`
- AI features: `smart-categorization`
- Decision: **KEEP** - Industry standard

### Replaceable Apps (EVALUATE/REPLACE)

**Studio (Usage: 0)**:
- Current: Use for ad-hoc queries, schema inspection
- Replacement: `ipai_supabase_admin` Odoo module
- Decision: **REPLACE** - Better Odoo integration

**Branching (Usage: 0)**:
- Current: Using git-based migrations instead
- Replacement: Existing `supabase/migrations/` workflow
- Decision: **REPLACE** - Already migrated

**CLI (Usage: 90% of deployments)**:
- Current: `supabase db push`, `supabase functions deploy`
- Replacement: Custom `scripts/supabase/deploy.sh`
- Decision: **EVALUATE** - High usage but tactical commands

**Storage (Usage: 2/42 functions)**:
- Functions: `document-upload`, `receipt-storage`
- Current cost: ~$50/month for 500GB
- Replacement: MinIO self-hosted (~$5/month)
- Decision: **REPLACE** - 10x cost savings

---

## Strategic Portfolio Links

**Related Initiatives**:
- PORT-2026-011: Integration Hardening & Compliance (this initiative)
- PORT-2026-008: Supabase Storage → MinIO Migration
- PORT-2026-009: `ipai_supabase_admin` Odoo Module

**Related Specs**:
- `docs/portfolio/specs/ipai-supabase-parity/` (if exists)
- `spec/IPAI-SUPABASE-001/` - Supabase admin module spec

**Current Supabase Usage Summary**:
- 42 Edge Functions (Deno runtime)
- 12 Realtime subscriptions (n8n triggers)
- 35 RLS-protected tables (auth integration)
- 8 Vault secrets (API keys, OAuth tokens)
- 3 pg_vector indexes (semantic search)
- 2 Storage buckets (document uploads, receipts)

---

## Decision Log

**2026-02-12**: Initial rubric created (PORT-2026-011)
- **Outcome**: 7 core substrate features identified (KEEP)
- **Outcome**: 4 replaceable apps identified (REPLACE/EVALUATE)
- **Next Steps**: Audit all 42 Edge Functions, create migration plans for Storage → MinIO

**Future Decisions** (to be documented here):
- CLI replacement: Custom `scripts/supabase/` automation
- Storage migration: MinIO deployment + data migration scripts
- Studio replacement: `ipai_supabase_admin` Odoo module development

---

## Verification Commands

**Audit Edge Functions**:
```bash
ls -1 supabase/functions/ | wc -l
# Expected: 42

# List functions using each substrate feature
grep -r "createClient" supabase/functions/ | wc -l  # PostgreSQL usage
grep -r "auth.getUser" supabase/functions/ | wc -l  # GoTrue usage
grep -r "channel(" supabase/functions/ | wc -l     # Realtime usage
grep -r "storage.from" supabase/functions/ | wc -l  # Storage usage
```

**Classify Features**:
```bash
# Generate feature classification matrix
grep -E "(Core|Strategic|Tactical|Replace)" docs/strategy/SUPABASE_FEATURE_RUBRIC.md | wc -l
# Expected: 11 classifications (7 core + 4 replaceable)
```

---

*Rubric created: 2026-02-12*
*Status: Active*
*Portfolio Initiative: PORT-2026-011*
