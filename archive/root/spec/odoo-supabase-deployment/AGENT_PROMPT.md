# Agent Prompt: Deep Research — Odoo + Supabase Monorepo Production Deployment on DigitalOcean

> **Instructions for Research Agent**: Execute each phase below sequentially. For each research question, provide **evidence-backed answers** with citations (URLs, version numbers, dates). Do NOT provide theoretical advice — find what production Odoo deployments actually do.

---

## Context

You are researching production deployment best practices for a monorepo containing:

- **Odoo CE 19.0** — open-source ERP (Python 3.12+, PostgreSQL 16)
- **OCA modules** — 14 repos from the Odoo Community Association vendored in `external-src/`
- **Custom modules** — 92 `ipai_*` addons (only 4 installed in production currently)
- **Supabase** — integration layer (NOT the Odoo database): 42 Edge Functions, pgvector RAG, Vault, Auth, Realtime
- **DigitalOcean** — single droplet (4GB, SGP1) + Managed PostgreSQL 16
- **Co-located services** — n8n, Superset, OCR adapter, Auth service on same droplet
- **Domain** — `insightpulseai.com` with subdomains: erp, n8n, ocr, auth, superset

The deployment currently works but needs hardening, optimization, and proven patterns applied.

---

## Phase 1: OCA Monorepo Patterns (Search & Analyze)

### Task 1.1: OCA Dependency Management
Search for how mature Odoo integrators manage OCA dependencies in production:

```
Search queries:
- "OCA monorepo deployment" site:github.com
- "odoo OCA git submodule production"
- "odoo addon management oca pip install"
- Camptocamp odoo deployment architecture
- Acsone odoo deployment pattern
- Tecnativa odoo module management
- "oca maintainer tools" deployment workflow
```

**Deliverable**: Table comparing approaches (submodule vs subtree vs pip vs vendored) with pros/cons from real deployments.

### Task 1.2: OCA CI/CD Quality Gates
Research the OCA-standard quality pipeline:

```
Search queries:
- OCA pre-commit hooks configuration 2025 2026
- "oca-pylint" "oca-autopep8" CI configuration
- OCA maintainer-quality-tools GitHub Actions
- "pytest-odoo" CI pipeline example
- OCA runboat testing infrastructure
```

**Deliverable**: Recommended CI pipeline stages with OCA tool versions pinned.

### Task 1.3: Addon Path Architecture
Research how the addon path should be structured:

```
Search queries:
- odoo 19 addons-path best practice
- "odoo addons path" OCA custom modules order
- odoo module namespace collision resolution
- OCA module flattening Docker build
```

**Deliverable**: Recommended addon path order with rationale.

---

## Phase 2: Docker Production Patterns (Search & Analyze)

### Task 2.1: Odoo Docker Best Practices
Search for production-grade Odoo Dockerfiles:

```
Search queries:
- site:github.com "odoo" "Dockerfile" "multi-stage" OCA
- Camptocamp docker-odoo-project
- "odoo docker production" hardened
- Tecnativa doodba Docker template
- acsone/docker-odoo repository
- odoo Docker Hub official image security
```

**Deliverable**: Reference Dockerfile pattern with multi-stage build, security hardening, and OCA integration.

### Task 2.2: Docker Compose Production Patterns
Research compose patterns for Odoo + supporting services:

```
Search queries:
- "docker-compose" odoo production nginx/caddy postgresql
- odoo longpolling websocket docker proxy
- odoo workers configuration Docker
- "docker compose" odoo "health check" production
- pgbouncer odoo Docker connection pooling
```

**Deliverable**: Annotated production compose file with resource limits, health checks, and service dependencies.

### Task 2.3: stunnel vs Direct TLS for Managed PostgreSQL
Research alternatives to the current stunnel approach:

```
Search queries:
- DigitalOcean managed PostgreSQL sslmode require Odoo
- odoo db_sslmode configuration
- pgbouncer TLS managed database
- stunnel PostgreSQL alternative Docker
- "sslmode=verify-full" DigitalOcean managed database
```

**Deliverable**: Recommendation on whether stunnel is necessary or if `db_sslmode=require` suffices for DO Managed PG.

---

## Phase 3: DigitalOcean Infrastructure (Search & Analyze)

### Task 3.1: Droplet Sizing for Odoo
Research resource requirements:

```
Search queries:
- odoo production server requirements RAM CPU
- odoo workers memory calculation formula
- DigitalOcean droplet odoo deployment sizing
- odoo "limit_memory_soft" production recommendation
- odoo 4GB RAM production feasibility
```

**Deliverable**: Resource model showing memory allocation per service, with recommended droplet tier.

### Task 3.2: PostgreSQL Tuning for Odoo on DO Managed
Research PostgreSQL tuning specific to Odoo workloads:

```
Search queries:
- postgresql.conf odoo tuning
- odoo PostgreSQL shared_buffers work_mem
- DigitalOcean managed PostgreSQL custom configuration
- pgtune odoo workload settings
- odoo PostgreSQL connection pooling configuration
```

**Deliverable**: PostgreSQL parameter recommendations for Odoo on DO Managed PG (4GB–8GB RAM).

### Task 3.3: Networking & Security
Research network architecture:

```
Search queries:
- DigitalOcean VPC private networking Docker
- Cloudflare proxy DigitalOcean SSL strict
- DigitalOcean firewall vs UFW best practice
- odoo xmlrpc security rate limiting
- nginx/caddy rate limiting login endpoint
```

**Deliverable**: Network architecture diagram with security layers.

---

## Phase 4: Supabase Integration Patterns (Search & Analyze)

### Task 4.1: Supabase as Sidecar to Self-Hosted App
Research patterns for using Supabase alongside non-Supabase databases:

```
Search queries:
- supabase integration external database
- supabase edge functions webhook ingestion pattern
- supabase "dead letter queue" webhook retry
- supabase auth with external application
- supabase realtime external database events
```

**Deliverable**: Integration architecture patterns with retry/DLQ strategy.

### Task 4.2: Supabase CI/CD
Research Supabase deployment automation:

```
Search queries:
- supabase CLI CI CD GitHub Actions
- "supabase db push" production workflow
- supabase edge functions deploy CI
- supabase migration strategy production
- supabase preview branches CI
```

**Deliverable**: Supabase deployment pipeline integrated with the Odoo release cycle.

### Task 4.3: Supabase Cost & Limits
Research Pro plan boundaries:

```
Search queries:
- supabase pro plan limits 2025 2026
- supabase edge function invocation limits
- supabase database size limit pro plan
- supabase self-hosted vs cloud cost comparison
```

**Deliverable**: Cost model with limit thresholds and risk mitigation.

---

## Phase 5: Security Hardening (Search & Analyze)

### Task 5.1: Odoo Security Best Practices
```
Search queries:
- odoo production security hardening checklist
- odoo admin_passwd master password production
- "list_db = False" odoo security
- odoo XMLRPC JSON-RPC security disable
- odoo session cookie security SameSite
- OWASP odoo ERP security assessment
```

**Deliverable**: Security hardening checklist with Odoo-specific items.

### Task 5.2: Container & Infrastructure Security
```
Search queries:
- Docker container security best practices production 2025
- Trivy GitHub Actions Docker image scanning
- CIS Docker benchmark automated
- DigitalOcean droplet security hardening Ubuntu
- Docker secrets vs env files production
```

**Deliverable**: Container security configuration with CI scanning integration.

---

## Phase 6: Monitoring & Observability (Search & Analyze)

### Task 6.1: Odoo Monitoring
```
Search queries:
- odoo production monitoring prometheus grafana
- odoo worker utilization metrics
- odoo longpolling monitoring
- "sentry" odoo module 19.0
- odoo performance dashboard production
```

**Deliverable**: Monitoring stack recommendation feasible on 4GB RAM.

### Task 6.2: Logging Architecture
```
Search queries:
- odoo centralized logging production
- Docker logging driver json-file max-size
- loki grafana lightweight logging Docker
- odoo structured logging JSON
```

**Deliverable**: Logging configuration for 5+ services on one droplet.

---

## Phase 7: Backup & Disaster Recovery (Search & Analyze)

### Task 7.1: Backup Strategy
```
Search queries:
- odoo backup strategy production
- DigitalOcean managed PostgreSQL PITR backup
- odoo filestore backup automation
- odoo "ir.attachment" backup considerations
- pg_dump vs pg_basebackup odoo
```

**Deliverable**: Backup automation scripts with verification and rotation.

### Task 7.2: Disaster Recovery
```
Search queries:
- odoo disaster recovery plan
- DigitalOcean droplet snapshot recovery time
- odoo database restore procedure production
- infrastructure as code DigitalOcean terraform
```

**Deliverable**: DR runbook with documented RTO/RPO targets.

---

## Phase 8: Performance & Scaling (Search & Analyze)

### Task 8.1: Odoo Performance Tuning
```
Search queries:
- odoo workers calculation formula CPU RAM
- odoo "max_cron_threads" production
- odoo asset bundling CDN production
- odoo PostgreSQL missing indexes performance
- odoo database query optimization
```

**Deliverable**: Performance tuning config with benchmark methodology.

### Task 8.2: Scaling Strategy
```
Search queries:
- odoo horizontal scaling multi-node
- odoo shared filestore NFS S3
- odoo session storage Redis production
- odoo load balancer configuration
- DigitalOcean load balancer odoo websocket
```

**Deliverable**: Scaling roadmap from single droplet to multi-node.

---

## Phase 9: Cost Optimization (Search & Analyze)

### Task 9.1: DigitalOcean Cost Model
```
Search queries:
- DigitalOcean pricing 2025 2026 droplet managed database
- DigitalOcean reserved droplet pricing annual
- DigitalOcean bandwidth pricing hidden costs
- DigitalOcean vs Hetzner vs OVH odoo hosting cost
```

**Deliverable**: Monthly cost breakdown with optimization opportunities.

---

## Phase 10: Synthesis & Recommendations (Compile)

### Task 10.1: Architecture Decision Records
For each major decision, write an ADR following:
```
# ADR-NNNN: [Title]

## Status: Proposed

## Context
[What is the issue?]

## Decision
[What did we decide?]

## Consequences
[What are the tradeoffs?]

## Evidence
[Links, benchmarks, case studies]
```

### Task 10.2: Consolidated Findings Report
Compile all phase results into a single structured report:
```
spec/odoo-supabase-deployment/findings.md
```

Structure:
1. Executive Summary (5 sentences max)
2. Current State Assessment (gaps and risks)
3. Recommended Architecture (with diagram)
4. Implementation Priority (P0/P1/P2)
5. Cost Model
6. Risk Register
7. Appendix: Full Research Notes

---

## Output Requirements

| Requirement | Detail |
|-------------|--------|
| **Citations** | Every claim must have a URL, version number, or date |
| **Evidence over opinion** | Prefer benchmarks, case studies, and documented production deployments |
| **Actionable** | Each finding must map to a concrete action (config change, script, workflow) |
| **Versioned** | Pin all tool/image versions (no `latest` tags) |
| **Cost-aware** | Include cost implications for every recommendation |
| **Testable** | Each recommendation must have a verification command or check |

---

## Anti-Patterns to Avoid

- Do NOT recommend Kubernetes for a single-droplet deployment unless the cost/benefit is clear
- Do NOT recommend tools that add more operational burden than they solve
- Do NOT suggest Enterprise-only features (this is CE + OCA only)
- Do NOT recommend cloud-native services that create vendor lock-in (keep self-hosted options viable)
- Do NOT provide "best practice" advice without evidence of who actually does it and at what scale
- Do NOT suggest changes that break the current working deployment before the new one is verified

---

## Reference: Current File Layout

```
/home/user/odoo/
├── addons/ipai/              # 49 namespaced custom modules
├── addons/ipai_*             # 43 standalone custom modules
├── external-src/             # 14 OCA git repos (submodules)
├── web/                     # 28 applications
├── pkgs/                 # 8 shared packages
├── supabase/                 # Supabase config, migrations, functions
│   ├── config.toml
│   ├── migrations/           # 103 migration files
│   └── functions/            # 42 Edge Functions
├── infra/deploy/             # Production deployment configs
│   ├── PRODUCTION_SETUP.md
│   ├── docker-compose.prod.yml
│   ├── odoo.conf
│   └── nginx/
├── docker-compose.yml        # Dev compose (canonical)
├── Dockerfile                # Odoo 18 + OCA production image
├── scripts/                  # 550+ automation scripts
│   ├── supabase/             # 40+ Supabase utilities
│   ├── deploy/               # Deployment scripts
│   └── ci/                   # CI utilities
├── docs/arch/        # Infrastructure SSOT
│   ├── PROD_RUNTIME_SNAPSHOT.md
│   ├── runtime_identifiers.json
│   └── RUNTIME_IDENTIFIERS.md
├── .github/workflows/        # 153 GitHub Actions workflows
└── spec/odoo-supabase-deployment/  # THIS spec bundle
    ├── research.md            # Research questions (companion doc)
    └── AGENT_PROMPT.md        # THIS file
```

---

## Timing

Execute phases 1–9 in parallel where possible (search queries are independent). Phase 10 (synthesis) requires all phases to complete first.

**Priority order if time-constrained**:
1. Phase 2 (Docker) — most immediate impact
2. Phase 3 (DigitalOcean) — infrastructure right-sizing
3. Phase 5 (Security) — non-negotiable for production
4. Phase 1 (OCA) — module management patterns
5. Phase 4 (Supabase) — integration hardening
6. Phase 8 (Performance) — tuning
7. Phase 6 (Monitoring) — observability
8. Phase 7 (Backup) — data protection
9. Phase 9 (Cost) — optimization
