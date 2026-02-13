# Deep Research: Odoo + Supabase Monorepo — OCA-Style Production Deployment on DigitalOcean

> **Status**: Research Phase
> **Scope**: Production-grade deployment architecture for Odoo CE 19 + Supabase integration layer + OCA monorepo on DigitalOcean
> **Last Updated**: 2026-02-13

---

## Research Objective

Conduct exhaustive research into proven, battle-tested practices for deploying an **Odoo CE 19 + Supabase + OCA monorepo** to **DigitalOcean production infrastructure**. The goal is a deployment architecture that is reproducible, secure, cost-efficient, and operationally sound — not theoretical, but grounded in what works at scale in real OCA/Odoo deployments.

---

## Current State (As-Is)

| Dimension | Current Value |
|-----------|--------------|
| **Odoo Version** | CE 19.0 (dev compose) / CE 18.0 (prod Dockerfile + droplet) |
| **Database** | DigitalOcean Managed PostgreSQL 16 (`odoo-db-sgp1`, port 25060) |
| **Compute** | Single DO droplet `178.128.112.214` (4GB RAM, 80GB, SGP1, Ubuntu 22.04) |
| **Reverse Proxy** | Caddy 2 (auto-SSL) in production; nginx also configured |
| **DB Tunnel** | stunnel (Alpine container → DO Managed PG over TLS) |
| **Container Runtime** | Docker + Docker Compose |
| **Custom Modules** | 92 total (49 namespaced `ipai/`, 43 standalone); only 4 installed in prod |
| **OCA Integration** | 14 OCA repos in `external-src/`, flattened during Docker build |
| **Supabase** | Project `spdtwktxdalcfigzeqrz` — integration/intelligence layer (NOT Odoo DB) |
| **Supabase Features** | 42 Edge Functions, pgvector RAG, Vault, Realtime, Auth, 103 migrations |
| **CI/CD** | 153 GitHub Actions workflows |
| **Domain** | `insightpulseai.com` (erp, n8n, ocr, auth, superset subdomains) |
| **Co-located Services** | n8n, Superset, OCR adapter, Auth service — all on same droplet |

---

## Research Questions (Exhaustive)

### 1. OCA Monorepo Deployment Patterns

#### 1.1 OCA Module Management in Production
- What are the proven patterns for managing OCA modules in a monorepo alongside custom addons?
- How do mature Odoo deployments (Camptocamp, Acsone, Tecnativa, Therp) structure their OCA dependencies?
- `git submodule` vs `git subtree` vs vendored copies vs `pip install odoo-addon-*` — what do production shops actually use?
- How should `external-src/` (14 OCA repos) be versioned, pinned, and updated in CI?
- What is the OCA-recommended approach for Odoo 19 addon path resolution when mixing OCA + custom?

#### 1.2 OCA Pre-commit & Quality Gates
- What OCA pre-commit hooks are mandatory for production-grade modules?
- How should `oca-autopep8`, `oca-pylint`, `oca-check-manifests` be integrated into CI for a monorepo with 92 modules?
- What is the minimum viable OCA quality gate that prevents broken modules from reaching production?

#### 1.3 OCA Module Flattening Strategy
- Current approach: flatten all OCA modules from 14 repos into single `/mnt/addons/oca` during Docker build. Is this the best practice or an anti-pattern?
- How do collision detection and namespace isolation work at scale?
- Should OCA modules be installed via pip (`pip install odoo19-addon-account-financial-reporting`) instead of source copy?

---

### 2. Docker & Container Architecture

#### 2.1 Odoo Docker Image Best Practices
- What is the proven Dockerfile pattern for Odoo 19 CE + OCA in production?
- Multi-stage builds: what stages are standard? (deps → build → runtime)
- How should the addon path be structured in the final image?
- What are the security hardening steps for Odoo Docker images? (non-root user, read-only filesystem, tmpfs for `/tmp`, no shell)
- Image size optimization: what layers to combine, what to exclude?
- Reproducibility: digest pinning vs tag pinning vs custom base image?

#### 2.2 Docker Compose for Production
- What services belong in a production compose file for Odoo + Supabase integration?
- How should the stunnel/DB tunnel pattern be replaced or hardened?
- Is there a better pattern than stunnel for connecting to DO Managed PostgreSQL over TLS? (e.g., `sslmode=require` direct, pgbouncer with TLS, etc.)
- Health check patterns that actually work for Odoo (not just `/web/health` — what about longpolling, cron workers, bus)?
- Resource limits (`deploy.resources.limits`) for Odoo containers on 4GB RAM droplets?
- Named volumes vs bind mounts for filestore, logs, config?

#### 2.3 Container Orchestration
- Docker Compose vs Docker Swarm vs Kubernetes (K3s) on DigitalOcean — what's the right tool for a single-droplet deployment?
- When does it make sense to move to DOKS (DigitalOcean Kubernetes Service)?
- How to handle zero-downtime deployments with Docker Compose? (blue-green, rolling?)
- Container restart policies and auto-healing patterns that work in production?

---

### 3. DigitalOcean Infrastructure

#### 3.1 Droplet Architecture
- Is a single 4GB droplet sufficient for Odoo 19 + n8n + Superset + OCR + Auth? What are the resource ceilings?
- What is the recommended droplet sizing for Odoo 19 with 4 installed modules vs 20+ modules?
- CPU-optimized vs memory-optimized vs general-purpose droplets for Odoo workloads?
- SGP1 region: any known issues with managed database latency, image pulls, or DNS?

#### 3.2 DigitalOcean Managed Database
- Best practices for DO Managed PostgreSQL 16 with Odoo 19?
- Connection pooling: built-in DO pooler vs pgbouncer sidecar vs Odoo's `db_maxconn`?
- Backup strategy: DO automated backups + custom `pg_dump` schedule — what's the right combination?
- Read replicas: when do Odoo deployments need them? How to configure Odoo for read-replica offloading?
- PostgreSQL tuning for Odoo: `shared_buffers`, `work_mem`, `effective_cache_size`, `maintenance_work_mem` — what values for 4GB RAM?
- SSL/TLS mode: `sslmode=require` vs `sslmode=verify-full` — what does DO Managed support?

#### 3.3 Networking & DNS
- Cloudflare + DO: optimal proxy mode (full strict, flexible, DNS-only)?
- Internal networking: VPC, private IP, Floating IP for HA?
- DO Firewall vs UFW vs both — what's the recommended layering?
- Rate limiting at the reverse proxy layer for Odoo `/web/login` and `/xmlrpc`?

#### 3.4 DigitalOcean App Platform vs Droplet
- Has anyone successfully deployed Odoo to DO App Platform? What are the limitations?
- Cost comparison: Droplet ($24/mo 4GB) vs App Platform vs DOKS for this workload?

---

### 4. Reverse Proxy & SSL/TLS

#### 4.1 Caddy vs Nginx vs Traefik
- Current: Caddy 2. Is this the best choice for Odoo?
- Odoo-specific proxy requirements: WebSocket for longpolling (`/websocket`), large upload support, `proxy_mode = True` headers?
- What Caddy/nginx config is needed for Odoo 19's new bus/websocket architecture?
- Multi-service reverse proxy (Odoo + n8n + Superset + OCR + Auth) on a single IP — best practice config?
- Let's Encrypt rate limits with 5+ subdomains on one IP?

#### 4.2 SSL/TLS Hardening
- What TLS configuration is recommended for Odoo in production?
- HSTS, OCSP stapling, certificate transparency — what's mandatory?
- mTLS between services on the same host — overkill or necessary?

---

### 5. Supabase Integration Layer

#### 5.1 Supabase as Sidecar to Odoo
- What are proven patterns for using Supabase alongside a self-hosted application (not as the primary database)?
- How should the Odoo → Supabase webhook pipeline be hardened for production? (retry logic, dead letter queue, idempotency)
- HMAC-SHA256 webhook verification: current implementation uses 5-minute replay window — is this sufficient?
- Edge Function cold starts: how to mitigate for critical paths (auth, webhook ingestion)?

#### 5.2 Supabase + Odoo Data Sync
- Event-driven sync (current) vs CDC (Change Data Capture) vs direct DB link — which pattern scales better?
- How to handle eventual consistency between Odoo PostgreSQL and Supabase PostgreSQL?
- Shadow tables for verification: is this a proven pattern or custom? What are alternatives?
- Data reconciliation strategies when sync diverges?

#### 5.3 Supabase Infrastructure
- Supabase Pro plan limitations relevant to this deployment (edge function invocations, database size, bandwidth)?
- Self-hosted Supabase on the same droplet vs cloud Supabase — cost/complexity tradeoff?
- Supabase CLI in CI: `supabase db push`, `supabase functions deploy` — production workflow best practices?

---

### 6. CI/CD Pipeline

#### 6.1 GitHub Actions for Odoo
- What CI pipeline stages are standard for OCA-grade Odoo deployments?
- Test matrix: Odoo version × Python version × PostgreSQL version — what combinations to test?
- How to run Odoo module tests in CI without a full Odoo instance? (pytest-odoo, odoo-bin `--test-enable`)
- Container image build and push: GitHub Container Registry vs DockerHub vs DO Container Registry?
- Deployment trigger: on push to `main` vs manual approval vs tag-based releases?

#### 6.2 Continuous Deployment to DigitalOcean
- SSH-based deployment vs `doctl` CLI vs GitHub Actions + DO API — what's the most reliable?
- Blue-green deployment on a single droplet: is it feasible? How?
- Database migration safety: how to run Odoo module upgrades (`-u`) without downtime?
- Rollback strategy: database snapshots before deploy, Docker image tags, or both?

#### 6.3 153 Workflows — Consolidation
- Current repo has 153 GitHub Actions workflows. What is a sustainable number?
- Reusable workflow patterns for Odoo monorepos?
- How to prevent workflow sprawl while maintaining comprehensive gating?

---

### 7. Security

#### 7.1 Odoo Security Hardening
- `admin_passwd` (master password): how should it be managed in production? (DO NOT expose via compose env vars)
- `list_db = False`: mandatory in production? What else to disable?
- XMLRPC/JSON-RPC security: IP allowlisting, rate limiting, authentication hardening?
- Odoo session security: cookie settings, CSRF, SameSite, Secure flag?
- File upload security: allowed MIME types, size limits, malware scanning?

#### 7.2 Container Security
- Docker socket exposure risks with co-located services?
- Image scanning: Trivy, Grype, Snyk — what integrates best with GitHub Actions?
- Runtime security: AppArmor, seccomp profiles for Odoo containers?
- Secrets management: Docker secrets vs `.env` files vs external vault (HashiCorp, DO 1-Click)?

#### 7.3 Database Security
- DO Managed PostgreSQL: what security features to enable? (connection limit, SSL enforcement, trusted sources)
- Principle of least privilege: `odoo_app` user permissions — what grants are needed, what should be revoked?
- Database encryption at rest: does DO Managed handle this automatically?
- Audit logging: `pgaudit` extension on DO Managed PostgreSQL?

---

### 8. Monitoring & Observability

#### 8.1 Metrics & Alerting
- What metrics matter for Odoo production? (response time, worker utilization, cron execution, database connections)
- Prometheus + Grafana on a 4GB droplet — feasible? Alternatives?
- DO Monitoring (built-in) vs external: what gaps does DO monitoring leave?
- Uptime monitoring: Uptime Robot, Betterstack, Checkly — what integrates with the current stack?

#### 8.2 Logging
- Centralized logging for 5+ services on one droplet?
- Odoo log levels in production: what's the right balance? (`warning` vs `info`)
- Log rotation: logrotate vs Docker log driver (`json-file` with max-size)?
- Structured logging for Odoo: is it possible/practical?

#### 8.3 Error Tracking
- Sentry for Odoo: how to integrate? Is the community module maintained for 19.0?
- Error alerting pipeline: Odoo → Sentry → Slack?

---

### 9. Performance & Scaling

#### 9.1 Odoo Performance Tuning
- `workers` setting: formula for calculating based on CPU cores and RAM?
- `max_cron_threads`: best practice for production?
- `limit_memory_soft` / `limit_memory_hard`: values for 4GB RAM shared with other services?
- `limit_time_cpu` / `limit_time_real`: what values prevent runaway requests without killing legitimate long operations?
- Odoo asset bundling and caching: CDN integration, `--load-language`, pre-compilation?
- Database query optimization: Odoo-specific PostgreSQL indexes that are commonly missing?

#### 9.2 Horizontal Scaling
- When to move from single droplet to multi-droplet? What triggers the decision?
- Odoo multi-worker + longpolling architecture on multiple nodes?
- Shared filestore: NFS, DO Spaces, S3-compatible — what works with Odoo?
- Session storage: file-based vs Redis vs database — what's recommended for multi-node?
- Load balancing: DO Load Balancer vs HAProxy vs Caddy upstream — cost and complexity?

#### 9.3 Caching
- Odoo's built-in caching: what's cached by default?
- Redis/Varnish in front of Odoo: when is it needed?
- CDN for Odoo static assets: Cloudflare vs DO CDN vs BunnyCDN?

---

### 10. Backup & Disaster Recovery

#### 10.1 Backup Strategy
- DO Managed PostgreSQL automated backups: retention, PITR, recovery time?
- Custom backup schedule: `pg_dump` frequency, retention policy, offsite storage?
- Filestore backup: what needs to be backed up beyond the database?
- Odoo-specific backup considerations: `ir.attachment`, report cache, session data?

#### 10.2 Disaster Recovery
- RTO/RPO targets for a small-medium Odoo deployment?
- Recovery procedure: droplet failure, database failure, data corruption?
- Cross-region replication: DO Managed PG read replicas across regions?
- Infrastructure as Code: can the entire stack be recreated from the repo? What's missing?

---

### 11. Cost Optimization

#### 11.1 DigitalOcean Cost Model
- Current estimated monthly cost for: 1 droplet + managed PG + DNS + bandwidth?
- Cost comparison: current architecture vs DO App Platform vs DOKS vs bare metal?
- Reserved instances / annual billing: what savings are available?
- Bandwidth costs: what are the hidden costs with 5+ services on one IP?

#### 11.2 Supabase Cost Model
- Pro plan ($25/mo): what are the limits that could trigger overages?
- Edge function invocation limits relevant to the 42 deployed functions?
- Database size limits: 8GB included — how much of this is used by 103 migrations + seeds?
- When does self-hosted Supabase become cheaper than cloud?

---

### 12. Multi-Service Co-location

#### 12.1 Service Isolation
- Running Odoo + n8n + Superset + OCR + Auth on one droplet: resource contention risks?
- Docker resource limits per service: what values prevent one service from starving others?
- Network isolation between services: Docker networks, localhost binding, firewall rules?
- When should each service be split to its own droplet?

#### 12.2 Service Dependencies
- Startup order and dependency management in Docker Compose?
- Health check cascading: if stunnel dies, does Odoo restart? If Odoo dies, does Caddy show maintenance page?
- Shared volumes and port conflicts between co-located services?

---

## Research Sources (Prioritized)

### Primary Sources
1. **OCA Official Documentation** — oca.github.io, OCA/maintainer-tools, OCA/maintainer-quality-tools
2. **Odoo 19 Documentation** — odoo.com/documentation/19.0 (deployment, performance, security)
3. **DigitalOcean Documentation** — docs.digitalocean.com (managed databases, droplets, networking)
4. **Supabase Documentation** — supabase.com/docs (edge functions, auth, realtime, self-hosting)
5. **Docker Official Best Practices** — docs.docker.com (multi-stage builds, security, compose)

### Secondary Sources
6. **OCA GitHub Repositories** — github.com/OCA (14 repos in use: server-tools, account-financial-reporting, etc.)
7. **Camptocamp Engineering Blog** — Odoo deployment patterns at scale
8. **Acsone Technical Blog** — OCA contribution and deployment practices
9. **Odoo Community Forums** — community.odoo.com (deployment section)
10. **DigitalOcean Community Tutorials** — digitalocean.com/community/tutorials (Odoo + PostgreSQL)

### Tertiary Sources
11. **Odoo GitHub Issues** — github.com/odoo/odoo (performance, deployment, Docker)
12. **PostgreSQL Wiki** — wiki.postgresql.org (tuning for Odoo workloads)
13. **OWASP** — owasp.org (web application security for ERP systems)
14. **CIS Benchmarks** — Docker, PostgreSQL, Ubuntu hardening benchmarks

---

## Expected Deliverables

| Deliverable | Format | Purpose |
|-------------|--------|---------|
| **Architecture Decision Records** | `docs/adr/NNNN-*.md` | Document key deployment decisions with rationale |
| **Production Docker Compose** | `infra/deploy/docker-compose.prod.v2.yml` | Battle-tested compose for all services |
| **Odoo 19 Production Dockerfile** | `Dockerfile.v3` | Multi-stage, hardened, OCA-ready |
| **Deployment Runbook** | `infra/deploy/RUNBOOK.md` | Step-by-step with verification at each stage |
| **PostgreSQL Tuning Config** | `infra/deploy/postgresql.conf.recommended` | Tuned for Odoo on 4GB–8GB RAM |
| **Nginx/Caddy Config** | `infra/deploy/caddy/Caddyfile.prod` | Multi-service reverse proxy with hardening |
| **CI/CD Pipeline** | `.github/workflows/cd-production-v2.yml` | Consolidated deployment workflow |
| **Monitoring Stack Config** | `infra/monitoring/` | Prometheus + Grafana or lightweight alternative |
| **Backup Automation** | `scripts/backup/` | Automated backup with verification and rotation |
| **Cost Model** | `docs/architecture/COST_MODEL.md` | Monthly cost breakdown with optimization plan |

---

## Constraints & Non-Negotiables

1. **Odoo database stays on DigitalOcean Managed PostgreSQL** — NOT Supabase
2. **Supabase is the integration layer only** — webhooks, auth, edge functions, RAG, realtime
3. **CE only** — no Enterprise modules, no odoo.com IAP
4. **OCA first** — prefer OCA modules over custom `ipai_*`
5. **Secrets in `.env` files** — never hardcoded in source
6. **Single domain**: `insightpulseai.com` — `.net` is deprecated
7. **Cost-conscious** — optimize for the DO $24–48/mo droplet tier
8. **Reproducible** — entire stack must be rebuildable from repo + secrets
9. **Python 3.12+** — Odoo 19 requirement
10. **No UI clickpaths** — everything must be CLI/CI automatable

---

## Success Criteria

- [ ] All research questions answered with evidence (links, benchmarks, case studies)
- [ ] Architecture decisions documented with tradeoffs
- [ ] Production compose file tested and verified
- [ ] Deployment runbook executable end-to-end without human intervention
- [ ] Monitoring covers all critical services
- [ ] Backup and recovery tested with documented RTO/RPO
- [ ] Cost model validated against actual DO billing
- [ ] Security posture assessed against OWASP Top 10 and CIS benchmarks
