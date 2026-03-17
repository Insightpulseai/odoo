# Supabase Features -- Comprehensive Index

**URL**: [supabase.com/features](https://supabase.com/features)
**Research Date**: 2026-03-07
**Branch**: `claude/review-signavio-url-HffM8`

> 79 features across 8 tags: authentication, database, functions, platform, realtime, storage, studio, vector.

---

## Table of Contents

1. [Pricing Tiers](#1-pricing-tiers)
2. [Database Features (18)](#2-database-features)
3. [Authentication Features (15)](#3-authentication-features)
4. [AI & Vector Features (5)](#4-ai--vector-features)
5. [Functions (3)](#5-functions)
6. [Realtime (7)](#6-realtime)
7. [Storage (5)](#7-storage)
8. [Platform & DevTools (12)](#8-platform--devtools)
9. [Studio (8)](#9-studio)
10. [Feature Maturity](#10-feature-maturity)
11. [IPAI Stack Relevance](#11-ipai-stack-relevance)

---

## 1. Pricing Tiers

| Tier | Price | Database | Storage | Egress | Auth MAU | Edge Fn Invocations |
|------|-------|----------|---------|--------|----------|-------------------|
| **Free** | $0/mo | 500 MB | 1 GB | 5 GB | 50K | 500K/mo |
| **Pro** | $25/mo + usage | 8 GB (auto-scales) | 100 GB | 250 GB | 100K | 2M/mo |
| **Team** | $599/mo + usage | 8 GB (auto-scales) | 100 GB | 2 TB | 500K | 2M/mo |
| **Enterprise** | Custom | Custom | Custom | Custom | Custom | Custom |

Key overage rates (Pro/Team): Bandwidth $0.09/GB, Auth MAU $0.00325/user. Free projects pause after 7 days inactivity. Max disk: 60 TB (Pro/Team).

---

## 2. Database Features

### Core Database

| Feature | Doc URL | Tier | Key Capabilities |
|---------|---------|------|-----------------|
| **Postgres Database** | [Docs](https://supabase.com/docs/guides/database/overview) | All | Full Postgres per project; direct SQL access; IPv4/IPv6; auto-scaling disk on paid plans |
| **Postgres Extensions** | [Docs](https://supabase.com/docs/guides/database/extensions) | All | 50+ extensions: pgvector, PostGIS, pgcrypto, pgjwt, pg_net, pg_cron, pg_stat_statements, http, pg_trgm; Trusted Language Extensions (pg_tle) |
| **Postgres Roles** | [Docs](https://supabase.com/docs/guides/database/postgres/roles) | All | Default roles: `postgres`, `anon`, `authenticated`, `service_role`, `authenticator`; custom roles; `auth.uid()`, `auth.jwt()` helpers |
| **OrioleDB** | [Docs](https://supabase.com/docs/guides/database/orioledb) | Experimental | Drop-in Postgres storage engine; index-organized tables; no VACUUM needed; up to 5.5x performance. **Limitation**: B-tree only (no HNSW/pgvector yet) |

### APIs

| Feature | Doc URL | Tier | Key Capabilities |
|---------|---------|------|-----------------|
| **Auto-generated REST API** (PostgREST) | [Docs](https://supabase.com/docs/guides/api) | All | Instant RESTful API from schema; single SQL statement per request; RLS enforcement; PostgREST v14: ~20% more RPS for GET |
| **Auto-generated GraphQL API** (pg_graphql) | [Docs](https://supabase.com/docs/guides/graphql) | All | GraphQL from schema; reflects FK relationships; RLS enforcement |

### Data Access & Connectivity

| Feature | Doc URL | Tier | Key Capabilities |
|---------|---------|------|-----------------|
| **Foreign Data Wrappers** | [Docs](https://supabase.com/docs/guides/database/extensions/wrappers/overview) | All | 13+ wrappers: Stripe, Firebase, BigQuery, ClickHouse, S3, Airtable, Redis, Snowflake, Paddle, Gravatar, Auth0, SQL Server, Logflare. Rust-native + Wasm. **No RLS** on FDWs. |
| **Read Replicas** | [Docs](https://supabase.com/docs/guides/platform/read-replicas) | Pro+ | Supavisor pool per replica; geo-routing (GET to nearest); multi-region |
| **Dedicated Poolers** | [Feature](https://supabase.com/features/dedicated-poolers) | Micro+ | Co-located PgBouncer; IPv4; full prepared statement support |
| **Supavisor** | [Docs](https://supabase.com/docs/guides/database/supavisor) | All | Transaction-mode pooling on port 6543; horizontally auto-scaling; ideal for serverless |
| **PrivateLink** | [Docs](https://supabase.com/docs/guides/platform/privatelink) | Enterprise | Private AWS connectivity; VPC Lattice; database + PgBouncer only (not API/Storage/Auth) |

### Data Operations

| Feature | Doc URL | Tier | Key Capabilities |
|---------|---------|------|-----------------|
| **Database Webhooks** | [Docs](https://supabase.com/docs/guides/database/webhooks) | All | HTTP POST/GET on INSERT/UPDATE/DELETE; `pg_net` (async, non-blocking); JSON payload |
| **Database Backups** | [Docs](https://supabase.com/docs/guides/platform/backups) | Pro+ | Daily auto-backups; 7-day (Pro), 14-day (Team), 30-day (Enterprise); PITR add-on (seconds-level) |
| **Cron** (pg_cron) | [Docs](https://supabase.com/docs/guides/cron) | All | Schedule jobs in Postgres; intervals down to 1-59 seconds; invoke DB functions, Edge Functions, webhooks |
| **Queues** (pgmq) | [Docs](https://supabase.com/docs/guides/queues) | All | Postgres-native durable message queue; guaranteed delivery; FIFO; exactly-once within visibility window; RLS support |
| **Declarative Schemas** | [Docs](https://supabase.com/docs/guides/local-development/declarative-database-schemas) | All | Define schema as `.sql` files; auto migration generation via `supabase db diff`; manages tables, views, functions, triggers, policies |
| **Replication** | [Docs](https://supabase.com/docs/guides/database/replication) | Pro+ (Alpha) | Logical replication to external destinations; CDC (INSERT/UPDATE/DELETE/TRUNCATE); destinations: Analytics Buckets (Iceberg), BigQuery |
| **Analytics Buckets** (Iceberg) | [Docs](https://supabase.com/docs/guides/storage/analytics/introduction) | Alpha | Apache Iceberg format; columnar Parquet on S3 Tables; compatible with DuckDB, Spark, PyIceberg |

---

## 3. Authentication Features

### Core Auth

| Feature | Doc URL | Tier | Key Capabilities |
|---------|---------|------|-----------------|
| **Email Login** | [Docs](https://supabase.com/docs/guides/auth) | All | Email + password; confirmation flow; password reset |
| **Phone Logins** | [Docs](https://supabase.com/docs/guides/auth/phone-login) | All | OTP via SMS; Twilio, MessageBird, Vonage |
| **Social Login** | [Docs](https://supabase.com/docs/guides/auth/social-login) | All | 20+ providers: Apple, Azure, Discord, Facebook, Figma, GitHub, GitLab, Google, Kakao, Keycloak, LinkedIn, Notion, Slack, Spotify, Twitch, Twitter/X, WorkOS, Zoom, Fly.io |
| **Passwordless / Magic Links** | [Docs](https://supabase.com/docs/guides/auth/passwordless-login) | All | Magic link via email; OTP via email or phone |
| **Multi-Factor Auth (MFA)** | [Docs](https://supabase.com/docs/guides/auth/auth-mfa/totp) | All | TOTP + phone verification; up to 10 factors; MFA enforcement (Pro+) |

### Enterprise & Advanced Auth

| Feature | Doc URL | Tier | Key Capabilities |
|---------|---------|------|-----------------|
| **SSO with SAML 2.0** | [Docs](https://supabase.com/docs/guides/auth/enterprise-sso/auth-sso-saml) | Pro+ | Azure AD/Entra, Okta, Google Workspace, PingIdentity, OneLogin |
| **OAuth 2.1 Server** | [Docs](https://supabase.com/docs/guides/auth/oauth-server) | All | Turn project into IdP; OIDC compliant; PKCE; "Sign in with [Your App]"; MCP server auth for AI agents |
| **Web3 Authentication** | [Docs](https://supabase.com/docs/guides/auth/auth-web3) | All | Ethereum (SIWE) + Solana (SIWS) wallet sign-in |
| **Third-Party Authentication** | [Docs](https://supabase.com/docs/guides/auth/third-party/overview) | All | Trust JWTs from external OIDC providers; asymmetric JWTs required |
| **Auth Hooks** | [Docs](https://supabase.com/docs/guides/auth/auth-hooks) | All | Custom Access Token Hook: modify JWT claims before issuance; HTTP or Postgres functions |
| **Captcha Protection** | [Docs](https://supabase.com/docs/guides/auth/auth-captcha) | All | CAPTCHA on sign-in/sign-up/password reset |
| **JWT Signing Keys** | [Docs](https://supabase.com/docs/guides/auth/signing-keys) | All | Asymmetric signing; key rotation |
| **Server-Side Auth** | [Docs](https://supabase.com/docs/guides/functions/auth) | All | Secure Edge Function endpoints with Auth; JWT verification |

### Authorization

| Feature | Doc URL | Tier | Key Capabilities |
|---------|---------|------|-----------------|
| **Row Level Security (RLS)** | [Docs](https://supabase.com/docs/guides/database/postgres/row-level-security) | All | Postgres-native; multiple policies per table; role targeting; `auth.uid()`, `auth.jwt()` helpers |
| **Role-Based Access Control (RBAC)** | [Docs](https://supabase.com/docs/guides/database/postgres/custom-claims-and-role-based-access-control-rbac) | All | Custom claims via Auth Hooks; `authorize()` helper; role hierarchy |

---

## 4. AI & Vector Features

| Feature | Doc URL | Tier | Key Capabilities |
|---------|---------|------|-----------------|
| **Vector Database** (pgvector) | [Docs](https://supabase.com/docs/guides/ai) | All | Store embeddings alongside relational data; cosine/inner product/L2; IVFFlat + HNSW indexes; `halfvec` (16-bit); millions of embeddings; LangChain integration |
| **Automatic Embeddings** | [Docs](https://supabase.com/docs/guides/ai/automatic-embeddings) | All | Trigger-based pipeline: pgmq + pg_net + pg_cron + Edge Functions; auto-update on content changes |
| **AI Integrations** | [Docs](https://supabase.com/docs/guides/ai) | All | OpenAI, Hugging Face; LangChain vector store; real-time AI processing |
| **Vector Buckets** | [Docs](https://supabase.com/docs/guides/storage/vector/introduction) | Alpha | Cold storage on S3 Vectors; specialized indexing; fast similarity search at scale |
| **MCP Server** | [Docs](https://supabase.com/docs/guides/getting-started/mcp) | All | 20+ tools for LLM-to-Supabase; Cursor/Claude/VS Code compatible; project management, schema design, queries; read-only mode; custom MCP via Edge Functions + mcp-lite |

---

## 5. Functions

| Feature | Doc URL | Tier | Key Capabilities | Limits |
|---------|---------|------|-----------------|--------|
| **Edge Functions** (Deno) | [Docs](https://supabase.com/docs/guides/functions) | All (Free: 500K, Pro: 2M) | TypeScript/JavaScript; globally distributed; V8 isolate; fast cold starts (ESZip); background tasks; WebSocket support | CPU: 2s/req; idle timeout: 150s; max size: 20 MB; no port 25/587 |
| **Regional Invocations** | [Docs](https://supabase.com/docs/guides/functions/regional-invocation) | All | Execute in nearest region or specified region via `x-region` header; co-locate with DB for bulk ops |
| **Persistent Storage** | [Docs](https://supabase.com/docs/guides/functions/ephemeral-storage) | All | Mount S3 buckets as persistent file storage; files survive between invocations; up to 97% faster cold starts; POSIX-like API |

---

## 6. Realtime

| Feature | Doc URL | Tier | Key Capabilities |
|---------|---------|------|-----------------|
| **Broadcast** | [Docs](https://supabase.com/docs/guides/realtime/broadcast) | All | Client-to-client messaging via channels; global delivery; low latency; REST API support |
| **Broadcast Authorization** | [Docs](https://supabase.com/docs/guides/realtime/broadcast) | All | RLS-based send/receive permissions on private channels |
| **Broadcast Replay** | [Feature](https://supabase.com/features/realtime-broadcast-replay) | Alpha | Late-joining clients catch up on missed messages |
| **Broadcast from Database** | [Docs](https://supabase.com/docs/guides/realtime/broadcast) | All | `realtime.send()` and `realtime.broadcast_changes()` from Postgres; WAL-based; partitioned tables (auto-cleanup 3 days) |
| **Postgres Changes** | [Docs](https://supabase.com/docs/guides/realtime/postgres-changes) | All | Listen to INSERT/UPDATE/DELETE in real-time; RLS per subscriber; filter by event/schema/table. **Scaling note**: 100 users = 100 reads per change; use Broadcast for scale |
| **Presence** | [Docs](https://supabase.com/docs/guides/realtime/presence) | All | Track/sync user state across clients; CRDT-backed in-memory KV; online indicators; collaborative editing |
| **Presence Authorization** | [Feature](https://supabase.com/features/realtime-presence-authorization) | All | RLS-based access control for Presence channels |

---

## 7. Storage

| Feature | Doc URL | Tier | Key Capabilities |
|---------|---------|------|-----------------|
| **File Storage** | [Docs](https://supabase.com/docs/guides/storage) | All (Free: 1GB, Pro: 100GB) | Multi-protocol: S3-compatible, REST, TUS resumable; RLS on buckets; public/private; up to 500 GB per file |
| **Image Transformations** | [Docs](https://supabase.com/docs/guides/storage/serving/image-transformations) | Pro+ | On-the-fly resize/optimize; Next.js image loader support |
| **Resumable Uploads** | [Docs](https://supabase.com/docs/guides/storage) | All | TUS protocol; resume interrupted uploads; Uppy client support |
| **CDN / Smart CDN** | [Feature](https://supabase.com/features/cdn) | All | 285+ cities globally; cache large files; smart revalidation at edge |
| **S3 Compatibility** | [Docs](https://supabase.com/docs/guides/storage/s3/compatibility) | All | Full S3-compatible provider; PutObject; any S3 client; interoperable with TUS/REST |

---

## 8. Platform & DevTools

| Feature | Doc URL | Tier | Key Capabilities |
|---------|---------|------|-----------------|
| **CLI** | [Docs](https://supabase.com/docs/guides/cli) | All | Local dev environment; migrations; schema diff; branch management; Edge Function deploy; SQL snippets (Git-friendly) |
| **Branching** | [Docs](https://supabase.com/docs/guides/deployment) | Pro+ | Persistent (staging) + ephemeral (PR preview) branches; `config.toml` auto-sync via Git; region selection |
| **Log Drains** | [Docs](https://supabase.com/docs/guides/platform/log-drains) | Pro+ | Export to Datadog, custom HTTP endpoints; Syslog/Loki planned |
| **Management API** | [Docs](https://supabase.com/docs/reference/api/introduction) | All | Programmatic project/org management; PAT or OAuth2 auth; rate limited |
| **Terraform Provider** | [Docs](https://supabase.com/docs/guides/deployment/terraform) | All | IaC for database, auth, storage, API config; import existing projects |
| **Security & Performance Advisor** | [Docs](https://supabase.com/docs/guides/database/database-advisors) | All | Actionable security/performance insights; FK indexing recommendations |
| **SOC 2 Compliance** | [Docs](https://supabase.com/docs/guides/security/soc-2-compliance) | Team+ | SOC 2 Type 2; annual audits; reports available on Team/Enterprise |
| **Custom Domains** | [Docs](https://supabase.com/docs/guides/platform/custom-domains) | Pro+ | White-label APIs; required for HTML/XHTML from Edge Functions |
| **Network Restrictions** | [Docs](https://supabase.com/docs/guides/platform/network-restrictions) | Pro+ | IP allowlisting for database connections |
| **SSL Enforcement** | [Docs](https://supabase.com/docs/guides/platform/ssl-enforcement) | All | Enforce SSL on Postgres/Supavisor; `verify-full` support; HTTP APIs always SSL |
| **Reports & Metrics** | [Docs](https://supabase.com/docs/guides/telemetry/reports) | All | Prometheus-compatible (~200 series); supabase-grafana dashboard (200+ charts); Auth/Storage/Realtime/Functions/API/Database reports |
| **Supabase ETL** | [Feature](https://supabase.com/features/supabase-etl) | Pro+ (Alpha) | Rust CDC pipeline; reads WAL; near real-time replication to Iceberg/BigQuery |

---

## 9. Studio

| Feature | Doc URL | Tier | Key Capabilities |
|---------|---------|------|-----------------|
| **Visual Schema Designer** | [Feature](https://supabase.com/features/visual-schema-designer) | All | Drag-and-drop schema; visual relationships; no SQL required |
| **SQL Editor** | [Feature](https://supabase.com/features/sql-editor) | All | Syntax highlighting; auto-completion; execution history; shared snippets; AI-assisted |
| **Supabase AI Assistant** | [Feature](https://supabase.com/features/ai-assistant) | All | NL-to-SQL; context-aware; error debugging; schema generation |
| **Email Templates** | [Feature](https://supabase.com/features/email-templates) | All | Customizable: signup, magic link, password reset, email change, invite; HTML editor |
| **User Impersonation** | [Feature](https://supabase.com/features/user-impersonation) | All | Experience app as any user; test RLS policies |
| **Vault** | [Docs](https://supabase.com/docs/guides/database/vault) | All | Encrypt secrets in Postgres; used by FDWs for credentials |
| **Policy Templates** | [Feature](https://supabase.com/features/policy-templates) | All | Pre-built RLS policy library; one-click application |
| **Foreign Key Selector** | [Feature](https://supabase.com/features/foreign-key-selector) | All | Visual FK relationship management |

---

## 10. Feature Maturity

| Stage | Meaning | Features |
|-------|---------|----------|
| **Experimental** | Early access, API unstable | OrioleDB |
| **Private Alpha** | Invite-only | Replication/ETL |
| **Public Alpha** | Open access, API may change | Vector Buckets, Analytics Buckets, Broadcast Replay |
| **Generally Available** | Production-ready | Most features (70+) |

---

## 11. IPAI Stack Relevance

### Currently Used (per CLAUDE.md)

| Supabase Feature | IPAI Usage | Status |
|-----------------|-----------|--------|
| **Database** (208 tables) | External integrations, task bus | Active |
| **Functions** (59 functions) | Edge Functions for webhooks/automation | Active |
| **pgvector** | AI search | Installed |
| **Auth** | 9 req/24h | Underutilized |
| **Storage** | 0 usage | Not activated |
| **Realtime** | 0 usage | Not activated |

### Features to Activate (per CLAUDE.md)

| Feature | IPAI Application | Priority |
|---------|-----------------|----------|
| **Realtime** (Broadcast + Postgres Changes) | Live dashboards, Odoo sync notifications | High |
| **Storage** (S3-compatible + CDN) | BIR document storage, replace S3/Cloudinary | High |
| **pg_cron** | Replace n8n for DB-only jobs (e.g., refresh materialized views) | Medium |
| **Queues** (pgmq) | MCP Jobs integration, task orchestration | Medium |
| **Automatic Embeddings** | AI-powered search across Odoo data | Medium |
| **MCP Server** | Claude Code integration for schema management | Low |

### Security Actions (per CLAUDE.md)

```sql
-- Fix function search_path (200+ functions)
-- Enable RLS on unprotected tables
ALTER TABLE public."SsoDetails" ENABLE ROW LEVEL SECURITY;
ALTER TABLE public."UserOrganization" ENABLE ROW LEVEL SECURITY;
```

---

## Quick Reference: Key URLs

| Resource | URL |
|----------|-----|
| Features Page | https://supabase.com/features |
| Documentation | https://supabase.com/docs |
| Pricing | https://supabase.com/pricing |
| Database Docs | https://supabase.com/docs/guides/database/overview |
| Auth Docs | https://supabase.com/docs/guides/auth |
| Edge Functions | https://supabase.com/docs/guides/functions |
| Realtime Docs | https://supabase.com/docs/guides/realtime |
| Storage Docs | https://supabase.com/docs/guides/storage |
| AI / Vectors | https://supabase.com/docs/guides/ai |
| Extensions | https://supabase.com/docs/guides/database/extensions |
| MCP Server | https://supabase.com/docs/guides/getting-started/mcp |
| CLI | https://supabase.com/docs/guides/cli |
| Self-Hosting | https://supabase.com/docs/guides/self-hosting/docker |
| Wrappers (FDW) | https://supabase.com/docs/guides/database/extensions/wrappers/overview |
| API Reference | https://supabase.com/docs/reference/api/introduction |
| Status | https://status.supabase.com |

---

*Research compiled: 2026-03-07*
*Branch: claude/review-signavio-url-HffM8*
