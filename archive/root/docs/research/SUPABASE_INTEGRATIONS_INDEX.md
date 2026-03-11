# Supabase Integrations -- Comprehensive Index

**URL**: [supabase.com/partners/integrations](https://supabase.com/partners/integrations)
**Research Date**: 2026-03-07
**Branch**: `claude/review-signavio-url-HffM8`

> 110+ integrations across 10 categories: API, App Templates, Auth, Caching/Offline-First, Data Platform, DevTools, Foreign Data Wrapper, Low-Code, Messaging, Storage.

---

## Table of Contents

1. [API Integrations (5)](#1-api-integrations)
2. [Auth Integrations (12+)](#2-auth-integrations)
3. [Caching / Offline-First (5)](#3-caching--offline-first)
4. [Data Platform (17+)](#4-data-platform)
5. [DevTools (35+)](#5-devtools)
6. [Foreign Data Wrappers (14+)](#6-foreign-data-wrappers)
7. [Low-Code (17+)](#7-low-code)
8. [Messaging (3)](#8-messaging)
9. [Client Libraries (6+)](#9-client-libraries)
10. [Ecosystem](#10-ecosystem)
11. [IPAI Stack Relevance](#11-ipai-stack-relevance)

---

## 1. API Integrations

| Integration | What It Does | Connection Method | Key Use Cases |
|-------------|-------------|-------------------|---------------|
| **Stacksync** | Bi-directional real-time sync between Supabase and CRMs | Direct Postgres connection | CRM data sync via SQL instead of API calls |
| **Stream** | Activity feeds, chat, and video APIs | REST API / client libraries | Social feeds, in-app messaging with Supabase as data store |
| **Zapier** | No-code workflow automation (6000+ apps) | REST API | Cross-app automation, event-driven workflows |
| **Zuplo** | Fully-managed API gateway | Proxies API requests; handles JWT tokens | Public API creation, rate limiting, developer portals |
| **n8n** | Open-source workflow automation (400+ nodes) | Built-in Supabase node + direct Postgres | Complex multi-step workflows, database-triggered automations |

---

## 2. Auth Integrations

All third-party auth providers follow a common pattern: provider issues JWT signed with Supabase's signing secret, used by the Supabase client to enforce RLS policies.

| Provider | Auth Method | Integration Pattern | Key Differentiator |
|----------|------------|---------------------|-------------------|
| **Arengu** | Form-based auth, passwordless | API + Auth hooks | Visual auth flow builder |
| **Auth0** | OAuth 2.0, SAML, social, MFA | Third-party auth; JWT with RLS | Enterprise-grade; broadest protocol support (Okta) |
| **Authsignal** | Step-up MFA, passwordless | Adds MFA after Supabase sign-in; no-code rules | Drop-in MFA at any point in user journey |
| **Clerk** | Session-based, social, MFA | Official "Connect with Supabase" one-click | Easiest setup; first-class Supabase integration |
| **Corbado** | Passkeys (Face ID, Touch ID, Windows Hello) | Web component + webhook user sync | 4x higher login success rates; gradual migration |
| **Keyri** | QR-based biometric auth | Mobile SDK -> QR scan -> `setSession()` | One-step biometric via phone QR scan |
| **Kinde** | OAuth 2.0, social, MFA | JWT with RLS | Developer-focused; generous free tier |
| **NextAuth (Auth.js)** | OAuth, credentials, magic links | Session JWT integration | Open-source; framework-native for Next.js |
| **Ory** | OAuth 2.0, OIDC, SAML | JWT integration | Fully open-source; self-hostable |
| **Passage (1Password)** | Passkeys, passwordless | Two lines of code; pre-built UI | Backed by 1Password; simplest passkey impl |
| **Stytch** | Passwordless (magic links, OTP, biometrics) | JWT integration | Enterprise passwordless with fraud prevention |
| **SuperTokens** | Email/password, social, passwordless, MFA | Open-source; self-hosted or managed | No vendor lock-in; self-hostable |

---

## 3. Caching / Offline-First

| Tool | Sync Pattern | Offline? | Supabase Integration | Best For |
|------|-------------|----------|---------------------|----------|
| **ElectricSQL** | Local-first via Postgres logical replication | Full read/write + conflict resolution | Docker connecting to Supabase Postgres | Web apps needing local-first architecture |
| **PowerSync** | Postgres-to-SQLite real-time sync | Full read/write; upload queue | Non-invasive (no schema changes); self-hostable or cloud | Flutter, React Native, Kotlin, Swift mobile apps |
| **Readyset** | Server-side query caching | N/A (server-side) | Sits between app and Postgres | Read-heavy workloads needing acceleration |
| **Replicache** | Client-side sync framework | Offline read/write + optimistic updates | Backend strategy implementation | Web apps with instant UI + sync |
| **RxDB** | Client-side reactive database | Full offline-first | PostgREST pull/push + Realtime for live updates | Web/React Native with complex client queries |

---

## 4. Data Platform

### Analytics & BI

| Integration | Type | Connection | Key Capability |
|-------------|------|-----------|----------------|
| **Astrato Analytics** | BI / Dashboards | Direct Postgres (live SQL, no ETL) | Pixel-perfect, white-labeled embedded dashboards |
| **Basedash** | Admin / Dashboards | Direct connection + 600+ tool sync | Instant data exploration, auto-generated SQL |
| **Buster** | AI Analytics | Direct database | Open-source Tableau alt; NL queries; AI visualizations |
| **Draxlr** | BI / Dashboards | Direct Postgres | Lightweight BI; SQL or no-code; charts/dashboards |
| **Dreambase** | AI-native Analytics | Sits on top of Supabase | AI analytics in 30 seconds; schema-aware; no hallucinated SQL |
| **Explo** | Embedded Analytics | Direct database | LLM-powered analytics embedded into products |
| **InsightBase** | AI Analytics | Direct database | Chat with your database; NL-to-SQL |
| **Trevor.io** | Self-serve Analytics | Direct Postgres | Team-wide data access; no-code query builder |

### ETL / CDC / Replication

| Integration | Type | Connection | Key Capability |
|-------------|------|-----------|----------------|
| **Artie** | Real-time CDC | CDC streaming from Postgres | Sub-minute replication to Snowflake, BigQuery, Redshift, Databricks |
| **Byteline Sync** | Cross-platform Sync | Event-driven CRUD mirroring | Bi-directional sync with Google Sheets, Airtable, HubSpot |
| **ClickHouse ClickPipes** | OLAP Analytics | FDW or CDC pipeline | Column-oriented analytics on Supabase data |
| **RisingWave** | Stream Processing | CDC from Supabase | Real-time analytics via stream processing |
| **Springtail** | Read Replicas | Shared storage layer | Elastic replicas in seconds; handles traffic spikes |

### CMS / Data Management

| Integration | Type | Connection | Key Capability |
|-------------|------|-----------|----------------|
| **Directus** | Headless CMS | Self-hosted on Supabase Postgres | Dynamic REST/GraphQL APIs; no-code data management |
| **Bemi** | Audit Trail | Postgres extension | Automatic audit trails for tables |
| **Parallel** | Data Enrichment | Edge Functions + API | Real-time company enrichment pipeline |
| **Spice AI** | Data & AI Platform | Zero-ETL SQL federation | Federation, acceleration, hybrid search for AI agents |

---

## 5. DevTools

### Search & Communication

| Integration | Category | Connection | Key Use Case |
|-------------|----------|-----------|-------------|
| **Algolia** | Search | Supabase-Algolia Connector; scheduled sync | Lightning-fast full-text search from Supabase tables |
| **AutoSend** | Email Automation | API/webhooks | Automated email sequences from Supabase events |
| **Postmark** | Transactional Email | API/Edge Functions | Reliable transactional email delivery |
| **Resend** | Email API | API/Edge Functions | Developer-focused email sending |
| **Mux** | Video API | `@mux/supabase` package; Edge Functions as webhooks | Video processing; semantic search with pgvector |

### Infrastructure & Security

| Integration | Category | Connection | Key Use Case |
|-------------|----------|-----------|-------------|
| **Cloudflare Workers** | Edge Compute | `supabase-js` or Hyperdrive (direct Postgres with pooling) | Edge functions accessing Supabase with low latency |
| **DBOS** | Durable Workflows | Direct Postgres | Failure-resilient workflows |
| **Doppler** | Secrets Management | Syncs to Edge Functions env vars | Multi-cloud secrets at enterprise scale |
| **Infisical** | Secrets Management | Syncs via Access Token; `Deno.env.get()` | Open-source secrets management |
| **Sequin** | CDC / Event Streaming | Postgres logical replication | Exactly-once processing to Kafka, SQS, Redis, HTTP |

### Frameworks & ORMs

| Integration | Category | Connection | Key Use Case |
|-------------|----------|-----------|-------------|
| **Nuxt** | Vue.js Framework | `@nuxtjs/supabase` module | Full-stack Vue.js with Supabase backend |
| **Prisma** | ORM | Direct Postgres connection string | Type-safe database access with migrations |
| **React-admin** | Admin Framework | `ra-supabase` data provider | Instant admin panels/CMS on Supabase |
| **refine** | React Framework | Built-in Supabase data provider | Admin dashboards; B2B apps; zero boilerplate |
| **Streamlit** | Data Apps | `st_supabase_connection` connector | Python data apps connected to Supabase |
| **Tamagui** | UI Framework | Starter kit with Supabase auth | Cross-platform React Native + Web (100% code sharing) |

### Dev Environments & Tools

| Integration | Category | Connection | Key Use Case |
|-------------|----------|-----------|-------------|
| **ChartDB** | Schema Visualization | OAuth + auto schema sync | Visual ER diagrams and schema docs |
| **CodeSandbox** | Cloud IDE | Project templates | Browser-based dev with Supabase pre-configured |
| **Deepnote** | Data Notebooks | Postgres connection | Collaborative data analysis |
| **DhiWise** | Code Generation | Flutter/React generation | Rapid app scaffolding with Supabase |
| **LiteLLM** | LLM Gateway | API integration | Unified LLM proxy with Supabase data store |
| **ParadeDB** | Postgres Search | Extension | Full-text search + analytics inside Postgres |
| **PostgresAI** | DB Optimization | Direct Postgres | AI-powered query optimization |
| **Replibyte** | Database Seeding | Postgres dump/restore | Seed dev DBs with masked production data |
| **pgMustard** | Query Optimization | EXPLAIN plan analysis | Visual explain plans for slow queries |

### Hosting & Deployment

| Integration | Category | Connection | Key Use Case |
|-------------|----------|-----------|-------------|
| **Vercel** | Hosting | Native integration; manage Supabase from Vercel dashboard | Full-stack deployment with Supabase backend |
| **Stormkit** | Hosting | Full-stack JS deployment | Deploy apps using Supabase |
| **Trigger.dev** | Background Jobs | Database webhooks / event triggers | Background processing from Supabase events |
| **Windmill** | Workflow Automation | Direct Postgres + API key | Scripts, flows, and apps with Supabase |
| **Zapp!** | Flutter IDE | Browser-based | Build Flutter apps with Supabase in browser |

### Other DevTools

| Integration | Notes |
|-------------|-------|
| **Nordcraft** | Web Development Engine |
| **Openfort** | Gaming/Web3 wallet infrastructure |
| **Scriptonia** | Script-based automation |

---

## 6. Foreign Data Wrappers

Built on the open-source **Supabase Wrappers** framework (Rust, pgrx). Supports Postgres v14, v15, v16.

### Native (Rust) FDWs

| FDW | Data Source | Read | Write | Query Pushdown |
|-----|-----------|------|-------|---------------|
| **BigQuery** | Google BigQuery | Yes | Yes | WHERE, ORDER BY, LIMIT |
| **ClickHouse** | ClickHouse OLAP | Yes | Yes | Yes |
| **Stripe** | Stripe API (customers, invoices, subscriptions) | Yes | Yes | -- |
| **Firebase** | Firestore + Auth Users | Yes | No | -- |
| **Airtable** | Airtable bases | Yes | No | -- |
| **S3** | AWS S3 (CSV, JSON, Parquet) | Yes | No | -- |
| **Logflare** | Logflare logs | Yes | No | -- |
| **Auth0** | Auth0 users | Yes | -- | -- |
| **SQL Server** | Microsoft SQL Server | Yes | No | -- |
| **Redis** | Redis KV | Yes | No | -- |

### WebAssembly (Wasm) FDWs

| FDW | Data Source | Notes |
|-----|-----------|-------|
| **Snowflake** | Snowflake DWH | Wasm-powered |
| **Paddle** | Paddle payments | Wasm-powered |
| **Gravatar** | Public Gravatar profiles | Wasm-powered |
| **Infura** | Ethereum blockchain | Real-time blockchain queries via SQL |

**Security**: FDWs do NOT provide RLS. Store foreign tables in private schemas. Use Supabase Vault for credentials.

---

## 7. Low-Code

| Platform | Type | Connection | Key Capability |
|----------|------|-----------|----------------|
| **Appsmith** | Internal tools | Direct Postgres / REST API | Dashboards, CRUD, admin panels |
| **Clutch** | App builder | Listed as partner | Prototype to production |
| **Dezbor** | App builder (AI) | Listed as partner | AI-powered admin panels |
| **Draftbit** | Mobile app builder | API connection | React Native mobile apps |
| **DrapCode** | No-code web apps | Direct Postgres (host/port/db/user/pass) | Drag-and-drop with auto-synced tables |
| **DronaHQ** | Internal tools | Direct connection | Custom apps combining multiple databases |
| **FlutterFlow** | Flutter app builder | Native (API URL + anon key) | Visual Flutter with Supabase auth/data/realtime |
| **Forest Admin** | Admin panel | Direct database | Auto-generated admin from schema |
| **Frontend Zero to One** | Auto-generated UI | OpenAPI spec from PostgREST | Instant app from database; zero drag-and-drop |
| **ILLA** | Low-code platform | Listed as partner | Internal tools and dashboards |
| **Internal** | Internal tools | Listed as partner | Admin and ops tools |
| **Jet Admin** | Admin panel | Direct database | No-code admin panels and business apps |
| **Plasmic** | Visual React builder | React component integration | Pixel-perfect UI with Supabase data binding |
| **Retool** | Internal tools | Direct Postgres or REST API | Admin panels, CRUD (limited real-time) |
| **Voltapp** | No-code app builder | HTTP + database connector | Desktop/mobile with visual "branching tree" code |
| **WeWeb** | No-code frontend | Native REST + GraphQL connectors | First-class Supabase integration; flexible web UIs |
| **YepCode** | Integration/automation | API integration | Code-first automation |

**Multi-frontend**: Multiple low-code frontends (WeWeb web, FlutterFlow mobile, Retool internal) can connect to the same Supabase backend.

---

## 8. Messaging

| Integration | Type | Integration Pattern | Key Capability |
|-------------|------|-------------------|----------------|
| **Loops** | Email marketing + transactional | SMTP for Auth emails; DB Webhooks; Incoming Webhooks | Beautiful email templates; replaces Supabase's basic auth emails |
| **OneSignal** | Push notifications, SMS, email, in-app | DB Webhooks + Edge Functions -> OneSignal API | Cross-platform push (FCM for Android); SMS; in-app |
| **Zavu** | Unified messaging (SMS, WhatsApp, Telegram, Email, Voice) | Single API | ML-powered smart routing; most cost-effective channel |

---

## 9. Client Libraries

### Official

| Language | Package | Install | Key Features |
|----------|---------|---------|-------------|
| **JavaScript/TypeScript** | `supabase-js` | `npm install @supabase/supabase-js` | Isomorphic; database, auth, realtime, storage, functions |
| **Python** | `supabase-py` | `pip install supabase` | Sub-libs: postgrest-py, gotrue-py, realtime-py, storage-py, functions-py |
| **Flutter/Dart** | `supabase-flutter` | `flutter pub add supabase_flutter` | Native Flutter integration |
| **Swift** | `supabase-swift` | Swift Package Manager | Sub-libs: postgrest-swift, auth-swift, realtime-swift, storage-swift |

### Community

| Language | Package | Notes |
|----------|---------|-------|
| **Kotlin** | `supabase-kt` | Stable, V2 API |
| **C#** | `supabase-csharp` | Community maintained |
| **Rust** | Community packages | Via supabase-community GitHub |

---

## 10. Ecosystem

### Supabase vs Firebase (2026)

| Dimension | Supabase | Firebase |
|-----------|----------|---------|
| **Database** | PostgreSQL (relational, SQL, joins) | Firestore/RTDB (NoSQL, document) |
| **Open Source** | Yes (self-hostable) | No (proprietary) |
| **Offline** | Needs PowerSync/ElectricSQL | Best-in-class mobile offline |
| **Security** | SQL-based RLS (powerful, granular) | Security rules (simpler) |
| **AI/Vectors** | pgvector native | Firebase Studio + Gemini + Vertex AI |
| **Pricing** | Predictable tiers | Per-operation (can spike) |
| **Vendor Lock-in** | Low (standard Postgres, pg_dump) | High (NoSQL, full rewrite to leave) |

### Self-Hosting

- **Docker Compose**: Official `docker-compose.yml` with all services
- Services: Studio, Realtime, Storage, imgproxy, postgres-meta, PostgreSQL, Edge Runtime
- Replace all placeholder secrets before production
- No telemetry; selective services (remove unused ones)
- Self-managed: uptime, scaling, updates, backups

### Local Development

```bash
supabase init          # Create project
supabase start         # Run local stack (Postgres, Auth, Storage, Realtime, Edge Runtime, Studio)
supabase db push       # Deploy migrations to remote
supabase functions deploy  # Deploy Edge Functions
```

---

## 11. IPAI Stack Relevance

### Currently Used Integrations

| Integration | IPAI Usage |
|-------------|-----------|
| **n8n** | Workflow automation (self-hosted); Supabase node for task bus |
| **Supabase Database** | External integrations, MCP Jobs schema |
| **Edge Functions** | Webhook handlers, automation |
| **pgvector** | AI search (installed but underutilized) |

### Recommended Integrations to Evaluate

| Integration | IPAI Application | Priority |
|-------------|-----------------|----------|
| **Sequin** | CDC from Supabase to n8n/Kafka for real-time Odoo sync | High |
| **PowerSync** | Offline-first mobile access to Odoo data | Medium |
| **Loops** | Better transactional email for Odoo notifications | Medium |
| **OneSignal** | Push notifications for mobile Odoo users | Medium |
| **Prisma** | Type-safe DB access for MCP servers (TypeScript) | Medium |
| **Algolia** | Fast full-text search across Supabase + Odoo data | Low |
| **Retool/WeWeb** | Admin dashboards on Supabase data | Low |

### FDW Opportunities

| FDW | IPAI Application |
|-----|-----------------|
| **Stripe** | Query Stripe data directly from Supabase SQL |
| **Firebase** (if migrating) | Read Firebase data during migration |
| **S3** | Query CSV/Parquet files from DO Spaces |
| **BigQuery** | Analytics integration |

---

## Summary Statistics

| Category | Count |
|----------|-------|
| API | 5 |
| Auth | 12+ |
| Caching / Offline-First | 5 |
| Data Platform | 17+ |
| DevTools | 35+ |
| Foreign Data Wrappers | 14+ |
| Low-Code | 17+ |
| Messaging | 3 |
| Client Libraries | 6+ |
| **Total** | **110+** |

---

*Research compiled: 2026-03-07*
*Branch: claude/review-signavio-url-HffM8*
