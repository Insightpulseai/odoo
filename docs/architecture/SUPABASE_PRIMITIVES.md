# Supabase Platform Primitives: Decision Framework

**Version**: 1.0.0
**Date**: 2026-02-12
**Status**: Active
**Scope**: Strategic architecture decisions for Supabase vs. alternative tools

---

## Executive Summary

This document provides a **5-criterion scoring rubric** to determine which Supabase features should be prioritized as **platform primitives** (sticky, high-leverage infrastructure) vs. which should use alternative tools (Plane, Superset, Odoo, etc.).

**Decision Principle**: Use Supabase for **system-of-record capabilities** with strong security, leverage, and portability. Use alternatives for **presentation layer** and **domain-specific tooling**.

**Framework Output**:
- **High Priority (≥4.0)**: Auth, Database, Storage, Vault, Edge Functions, RLS
- **Medium Priority (3.0-4.0)**: Realtime (CDC), Monitoring (basic)
- **Low Priority (<3.0)**: UI Dashboards, Analytics UI, Studio (use Plane/Superset/Odoo)

---

## 1. Decision Framework Overview

### 1.1 Purpose

This framework answers: **"Should we use Supabase for X, or use an alternative tool?"**

**Use this framework when**:
- Evaluating new Supabase features
- Deciding between Supabase and domain tools (Plane, Superset, n8n)
- Planning infrastructure investments
- Migrating from one platform to another

### 1.2 Five Criteria (Weighted)

| Criterion | Weight | Question |
|-----------|--------|----------|
| **SoR Fit** | 35% | Does this hold canonical data or enforce critical policies? |
| **Security** | 25% | Does this provide security primitives (RLS, auth, audit)? |
| **Leverage** | 20% | Does this reduce custom code and operational toil? |
| **Portability** | 10% | How difficult is migration to alternatives? |
| **Latency/Cost** | 10% | What's the performance and cost impact? |

**Total Score**: 1.0 (minimum) to 5.0 (maximum)

**Decision Thresholds**:
- **≥4.0**: High Priority — Use Supabase, invest in deep integration
- **3.0-4.0**: Medium Priority — Use Supabase with escape hatches
- **<3.0**: Low Priority — Prefer alternatives, use Supabase sparingly

---

## 2. Scoring Rubric Details

### 2.1 System-of-Record Fit (35% weight)

**Definition**: Does this feature hold canonical data or enforce critical business/security policies?

**Scoring Scale**:
- **5.0**: Primary system-of-record for critical data (Auth, Database, Vault)
- **4.0**: Secondary SoR with strong consistency needs (Storage, Edge Functions)
- **3.0**: Derived data with eventual consistency (Realtime CDC)
- **2.0**: Presentation layer with no data persistence (Dashboards)
- **1.0**: External tooling better suited (Analytics, Project Management)

**Examples**:
- **5.0**: PostgreSQL Database (holds all canonical business data)
- **4.0**: Vault (canonical secrets storage)
- **3.0**: Realtime (mirrors database state, not primary)
- **1.0**: Supabase Studio UI (Plane/Odoo provide better PM/BI)

### 2.2 Security Primitives (25% weight)

**Definition**: Does this provide foundational security capabilities (RLS, auth, audit, encryption)?

**Scoring Scale**:
- **5.0**: Core security primitive (Auth, RLS, Vault)
- **4.0**: Security-enhancing feature (Storage ACLs, Edge Function auth)
- **3.0**: Security-neutral (Realtime observability)
- **2.0**: Potential security surface (UI dashboards, third-party integrations)
- **1.0**: Security risk without mitigation (public analytics, unaudited features)

**Examples**:
- **5.0**: Row-Level Security (RLS) — Zero-trust data access control
- **4.0**: Supabase Auth — OAuth2, JWT, MFA enforcement
- **3.0**: Realtime — Secure by RLS inheritance, but adds attack surface
- **1.0**: Public Studio dashboards — Prefer internal Superset with auth

### 2.3 Leverage (20% weight)

**Definition**: Does this reduce custom code, operational toil, and infrastructure complexity?

**Scoring Scale**:
- **5.0**: Replaces 1,000+ lines of custom code (Auth, Database, RLS)
- **4.0**: Replaces 500+ lines or significant ops burden (Edge Functions, Storage)
- **3.0**: Moderate leverage, some custom code still needed (Realtime)
- **2.0**: Minimal leverage, alternatives equally easy (Monitoring)
- **1.0**: Negative leverage, adds complexity (UI dashboards vs. Superset)

**Examples**:
- **5.0**: Supabase Auth — Replaces auth service + session management + OAuth integration
- **4.0**: Edge Functions — Replaces API gateway + serverless deployment + scaling
- **2.0**: Monitoring — Grafana/Prometheus equally viable
- **1.0**: Studio Analytics — Superset provides richer BI with less lock-in

### 2.4 Portability (10% weight)

**Definition**: How difficult is it to migrate away from this feature?

**Scoring Scale**:
- **5.0**: Standard protocol, easy migration (PostgreSQL, S3-compatible Storage)
- **4.0**: Moderate migration effort, standard patterns (Auth with JWT, Edge Functions via Deno)
- **3.0**: Vendor-specific but documented (Realtime CDC)
- **2.0**: Significant migration cost (Studio-specific workflows)
- **1.0**: High lock-in, no standard alternative (Supabase-only features)

**Examples**:
- **5.0**: PostgreSQL Database — Standard SQL, pg_dump portability
- **4.0**: Storage — S3 API compatible, easy migration to AWS/MinIO
- **3.0**: Realtime — Vendor-specific, but can replace with Hasura/PostgREST
- **1.0**: Studio UI — Supabase-specific, no export/import

### 2.5 Latency & Cost (10% weight)

**Definition**: What are the performance and cost implications?

**Scoring Scale**:
- **5.0**: Low latency, predictable cost (Database, Storage)
- **4.0**: Acceptable latency, cost-effective (Auth, Edge Functions)
- **3.0**: Variable latency/cost, needs optimization (Realtime at scale)
- **2.0**: High cost for value delivered (Studio for BI vs. Superset)
- **1.0**: Performance bottleneck or cost prohibitive (Realtime for high-throughput)

**Examples**:
- **5.0**: PostgreSQL — Sub-10ms queries, predictable pricing
- **4.0**: Edge Functions — <100ms cold start, pay-per-execution
- **3.0**: Realtime — <500ms propagation, cost scales with connections
- **1.0**: Studio Analytics — High cost for limited BI features vs. Superset (free)

---

## 3. Feature Evaluation Matrix

### 3.1 Core Platform (High Priority ≥4.0)

| Feature | SoR | Security | Leverage | Portability | Latency/Cost | **Total** | Priority |
|---------|-----|----------|----------|-------------|--------------|-----------|----------|
| **PostgreSQL Database** | 5.0 | 5.0 | 5.0 | 5.0 | 5.0 | **5.0** | HIGH |
| **Row-Level Security (RLS)** | 5.0 | 5.0 | 5.0 | 5.0 | 5.0 | **5.0** | HIGH |
| **Supabase Auth** | 5.0 | 5.0 | 5.0 | 4.0 | 4.0 | **4.7** | HIGH |
| **Supabase Vault** | 5.0 | 5.0 | 4.0 | 3.0 | 5.0 | **4.5** | HIGH |
| **Storage (S3)** | 4.0 | 4.0 | 4.0 | 5.0 | 5.0 | **4.3** | HIGH |
| **Edge Functions (Deno)** | 4.0 | 4.0 | 4.0 | 4.0 | 4.0 | **4.0** | HIGH |

**Rationale**: These are **platform primitives** — foundational capabilities that:
- Hold canonical data or enforce critical policies
- Provide security at the infrastructure level
- Replace thousands of lines of custom code
- Maintain portability through standard protocols
- Deliver predictable performance and cost

**Recommendation**: **Invest heavily**. Deep integration, long-term commitment, infrastructure-level dependency.

---

### 3.2 Strategic Infrastructure (Medium Priority 3.0-4.0)

| Feature | SoR | Security | Leverage | Portability | Latency/Cost | **Total** | Priority |
|---------|-----|----------|----------|-------------|--------------|-----------|----------|
| **Realtime (CDC)** | 3.0 | 3.0 | 3.0 | 3.0 | 3.0 | **3.0** | MEDIUM |
| **PostgREST API** | 4.0 | 4.0 | 4.0 | 4.0 | 4.0 | **4.0** | MEDIUM-HIGH |
| **Monitoring (Basic)** | 2.0 | 3.0 | 3.0 | 4.0 | 3.0 | **3.0** | MEDIUM |

**Rationale**: These features provide **strategic value** but:
- Have viable alternatives (Hasura, Grafana, custom WebSockets)
- Require careful cost/performance monitoring at scale
- Should maintain **escape hatches** for migration

**Recommendation**: **Use with caution**. Build abstraction layers, monitor costs, maintain fallback strategies.

---

### 3.3 Presentation & Domain Tools (Low Priority <3.0)

| Feature | SoR | Security | Leverage | Portability | Latency/Cost | **Total** | Priority |
|---------|-----|----------|----------|-------------|--------------|-----------|----------|
| **Studio UI (Analytics)** | 1.0 | 2.0 | 1.0 | 1.0 | 2.0 | **1.4** | LOW |
| **Studio UI (Dashboard)** | 1.0 | 2.0 | 1.0 | 1.0 | 2.0 | **1.4** | LOW |
| **Studio UI (Table Editor)** | 2.0 | 2.0 | 2.0 | 1.0 | 3.0 | **2.0** | LOW |

**Rationale**: These are **presentation-layer features** where:
- **Superset** (BI/Analytics) provides richer features, open-source, self-hosted
- **Plane** (Project Management) provides better PM workflows than Studio
- **Odoo** (Business Apps) provides domain-specific UIs

**Recommendation**: **Prefer alternatives**. Use Superset for BI, Plane for PM, Odoo for business UIs. Supabase Studio only for ad-hoc database inspection.

---

## 4. Decision Workflows

### 4.1 When to Choose Supabase

**Use Supabase when**:
1. **System-of-Record**: Feature holds canonical data or policies
2. **Security Primitive**: Feature enforces access control or encryption
3. **High Leverage**: Feature replaces >500 lines of custom code
4. **Standard Protocol**: Feature uses PostgreSQL, S3, OAuth, JWT
5. **Cost-Effective**: Predictable pricing at expected scale

**Example**: User authentication
- ✅ SoR: Canonical user identities
- ✅ Security: OAuth2, JWT, MFA enforcement
- ✅ Leverage: Replaces auth service + session management
- ✅ Standard: OAuth2/OIDC protocols
- ✅ Cost: $0-$25/month for <10K users
- **Decision**: Use Supabase Auth (score: 4.7)

---

### 4.2 When to Choose Alternatives

**Use Alternatives when**:
1. **Presentation Layer**: UI dashboards, analytics, project management
2. **Domain-Specific**: BI (Superset), PM (Plane), ERP (Odoo)
3. **High Lock-In**: Vendor-specific features with no migration path
4. **Cost Prohibitive**: Supabase pricing doesn't scale with usage
5. **Better Tooling**: Alternative has richer features or ecosystem

**Example**: Business intelligence dashboards
- ❌ SoR: Derived/aggregated data, not canonical
- ❌ Security: Presentation layer, auth handled upstream
- ❌ Leverage: Superset provides richer BI features
- ❌ Standard: Supabase Studio is vendor-specific
- ❌ Cost: Superset self-hosted is free vs. Studio add-on
- **Decision**: Use Apache Superset (Supabase score: 1.4)

---

### 4.3 When to Use Both (Hybrid)

**Use Hybrid Approach when**:
1. **Development**: Supabase Studio for quick prototypes
2. **Production**: Migrate to alternatives for scale/features
3. **Fallback**: Maintain Supabase as backup for alternatives
4. **Transition**: Gradual migration from Supabase to specialized tools

**Example**: Database management
- **Development**: Supabase Studio for quick table edits
- **Production**: Odoo models for business logic + RLS for security
- **Monitoring**: Superset for BI + Supabase Studio for ad-hoc queries
- **Automation**: Edge Functions for glue + n8n for complex workflows

---

## 5. Current Stack Alignment

### 5.1 InsightPulseAI Stack (2026-02-12)

| Component | Tool | Supabase Role | Score | Justification |
|-----------|------|---------------|-------|---------------|
| **Database** | Supabase PostgreSQL | Primary SoR | 5.0 | Canonical data, RLS enforcement |
| **Auth** | Supabase Auth | Primary | 4.7 | OAuth2, JWT, MFA |
| **Storage** | Supabase Storage | Primary | 4.3 | S3-compatible, RLS-protected |
| **Secrets** | Supabase Vault | Primary | 4.5 | Encrypted secrets, audit trail |
| **API** | Edge Functions | Primary | 4.0 | Serverless glue, Deno runtime |
| **Realtime** | Supabase Realtime | Secondary | 3.0 | CDC mirroring, n8n alternative |
| **BI/Analytics** | Apache Superset | Primary | N/A | Superset score: 4.5 vs. Studio 1.4 |
| **Project Mgmt** | Plane | Primary | N/A | Plane score: 4.2 vs. Studio 1.4 |
| **ERP** | Odoo CE 19 | Primary | N/A | Domain-specific, Supabase as data layer |
| **Automation** | n8n + Edge Functions | Hybrid | 3.5 | n8n for workflows, EF for glue |

**Sticky Primitives** (High investment):
- ✅ PostgreSQL Database
- ✅ RLS Policies
- ✅ Supabase Auth
- ✅ Supabase Vault
- ✅ Supabase Storage
- ✅ Edge Functions

**Replaceable Services** (Low lock-in):
- ❌ Studio UI → Use Superset, Plane, Odoo
- ❌ Studio Analytics → Use Superset
- ❌ Realtime (if cost scales) → Migrate to Hasura/PostgREST

---

### 5.2 Migration Risk Assessment

| Feature | Migration Difficulty | Estimated Effort | Risk Level |
|---------|---------------------|------------------|------------|
| **PostgreSQL** | Low (pg_dump) | 1-2 days | LOW |
| **Auth** | Medium (JWT standard) | 1-2 weeks | MEDIUM |
| **Storage** | Low (S3 API) | 2-5 days | LOW |
| **Vault** | Medium (secret export) | 3-5 days | MEDIUM |
| **Edge Functions** | Medium (Deno std) | 1-2 weeks | MEDIUM |
| **RLS Policies** | High (PostgreSQL-specific) | 2-4 weeks | HIGH |

**Mitigation Strategy**:
1. **Abstraction Layers**: Wrap Supabase APIs in internal SDKs
2. **Standard Protocols**: Prefer PostgreSQL, S3, OAuth over vendor-specific
3. **Documentation**: Maintain migration playbooks for each primitive
4. **Testing**: Regular migration drills to alternative platforms

---

## 6. Strategic Recommendations

### 6.1 Double Down (High Priority)

**Invest heavily in these Supabase features**:
1. **PostgreSQL + RLS**: Core data platform, enforce zero-trust access
2. **Supabase Auth**: User identity, OAuth2, JWT, MFA
3. **Supabase Vault**: Secrets management, audit trail
4. **Supabase Storage**: File storage with RLS integration
5. **Edge Functions**: Serverless glue code, Deno runtime

**Actions**:
- Deep integration with Odoo, Plane, n8n
- RLS policies for every table
- Edge Functions for all external integrations
- Vault for all secrets (no .env files)

---

### 6.2 Use Sparingly (Medium Priority)

**Use with escape hatches and cost monitoring**:
1. **Realtime (CDC)**: Only for low-latency needs, monitor connection costs
2. **PostgREST API**: Use for simple CRUD, complex logic in Edge Functions
3. **Monitoring**: Basic metrics OK, use Grafana for production observability

**Actions**:
- Abstraction layer for Realtime (easy swap to WebSockets)
- Cost alerts for Realtime connections >1K
- Grafana for production monitoring + alerting

---

### 6.3 Prefer Alternatives (Low Priority)

**Use specialized tools instead of Supabase**:
1. **BI/Analytics**: Apache Superset (self-hosted, richer features)
2. **Project Management**: Plane (Kanban, roadmaps, OKRs)
3. **Business UIs**: Odoo (domain-specific modules)
4. **Complex Workflows**: n8n (visual automation, 400+ integrations)

**Actions**:
- Superset for all BI dashboards
- Plane for all project/task management
- Odoo for business processes (HR, Finance, CRM)
- n8n for workflow automation

---

## 7. Evaluation Examples

### 7.1 Example 1: Email Notifications

**Question**: Should we use Supabase for BIR email notifications?

**Evaluation**:
| Criterion | Score | Rationale |
|-----------|-------|-----------|
| SoR Fit | 2.0 | Email is a notification surface, not data storage |
| Security | 3.0 | Email contains sensitive data, needs encryption |
| Leverage | 3.0 | Edge Functions reduce custom code vs. self-hosted SMTP |
| Portability | 4.0 | Standard SMTP, easy to migrate |
| Latency/Cost | 4.0 | Edge Functions are cost-effective for email |
| **Total** | **3.1** | MEDIUM |

**Decision**: Use **hybrid approach**:
- Odoo module for email composition and scheduling
- Supabase Edge Function for SMTP delivery via Zoho
- Alternative: n8n for complex email workflows

**Implemented**: ✅ `supabase/functions/bir-urgent-alert/` (Phase 2)

---

### 7.2 Example 2: BIR Compliance Tracking

**Question**: Should we use Supabase for BIR compliance tracking?

**Evaluation**:
| Criterion | Score | Rationale |
|-----------|-------|-----------|
| SoR Fit | 5.0 | BIR deadlines are canonical compliance data |
| Security | 5.0 | RLS enforces agency-level access control |
| Leverage | 4.0 | PostgreSQL replaces custom deadline management |
| Portability | 5.0 | Standard PostgreSQL, easy migration |
| Latency/Cost | 5.0 | Simple CRUD operations, low cost |
| **Total** | **4.8** | HIGH |

**Decision**: Use **Supabase PostgreSQL**:
- Odoo module `ipai_bir_tax_compliance` for business logic
- Supabase PostgreSQL for canonical deadline data
- RLS policies for agency-level isolation
- Plane integration for OKR tracking (presentation layer)

**Implemented**: ✅ Odoo + Supabase hybrid (Phases 1-3)

---

### 7.3 Example 3: Analytics Dashboard

**Question**: Should we use Supabase Studio for BIR analytics?

**Evaluation**:
| Criterion | Score | Rationale |
|-----------|-------|-----------|
| SoR Fit | 1.0 | Derived data, not canonical |
| Security | 2.0 | Presentation layer, auth upstream |
| Leverage | 1.0 | Superset provides richer BI features |
| Portability | 1.0 | Studio is vendor-specific |
| Latency/Cost | 2.0 | Studio limited vs. Superset self-hosted |
| **Total** | **1.4** | LOW |

**Decision**: Use **Apache Superset**:
- Superset for BI dashboards, charts, SQL queries
- Supabase PostgreSQL as data source (read-only connection)
- Tableau for published dashboards (GenieView)

**Implemented**: ✅ Superset integration (existing)

---

## 8. Continuous Evaluation

### 8.1 Review Triggers

**Re-evaluate Supabase features when**:
1. **New Feature Launch**: Supabase releases new capability
2. **Cost Spike**: Monthly bill increases >20% month-over-month
3. **Performance Issues**: Latency >500ms or downtime events
4. **Migration Opportunity**: Alternative tool provides 2x better value
5. **Quarterly Review**: Scheduled architecture assessment

### 8.2 Scoring Updates

**Update this framework when**:
1. **Weight Changes**: Business priorities shift (e.g., security becomes 40%)
2. **New Criteria**: Additional factors emerge (e.g., compliance, AI readiness)
3. **Threshold Adjustments**: High/medium/low boundaries change
4. **Stack Evolution**: New tools enter/exit the ecosystem

### 8.3 Decision Log

**Document all framework decisions in**:
- `docs/evidence/<YYYYMMDD-HHMM>/supabase-decision/`
- Include: Feature name, scores, rationale, alternatives considered, decision outcome

---

## 9. Appendix

### 9.1 Glossary

- **SoR (System-of-Record)**: Authoritative source of truth for data
- **RLS (Row-Level Security)**: PostgreSQL row-based access control
- **CDC (Change Data Capture)**: Real-time database change streaming
- **Edge Functions**: Serverless functions (Deno runtime on Supabase)
- **Vault**: Encrypted secrets storage with audit trail
- **PostgREST**: Auto-generated REST API from PostgreSQL schema

### 9.2 References

- [Supabase Pricing](https://supabase.com/pricing)
- [Apache Superset](https://superset.apache.org/)
- [Plane Documentation](https://docs.plane.so/)
- [Odoo CE 19](https://www.odoo.com/documentation/19.0/)
- [Strategic Architecture Plan](../evidence/20260212-2045/constitution/IMPLEMENTATION.md)

### 9.3 Changelog

| Date | Version | Change |
|------|---------|--------|
| 2026-02-12 | 1.0.0 | Initial framework creation (Phase 4) |

---

**Maintained by**: InsightPulseAI Architecture Team
**Last Updated**: 2026-02-12
**Next Review**: 2026-05-12 (Quarterly)
