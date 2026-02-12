# OdooOps Platform Constitution

**Version**: 1.0.0
**Status**: Draft
**Last Updated**: 2026-02-12
**Owner**: InsightPulse AI Platform Team

---

## Purpose

**OdooOps Platform** is an API-first, CLI-automatable PaaS for Odoo 19 CE that delivers deterministic, repeatable deployments through GitOps patterns and policy-driven infrastructure management.

### What This Is

- A **self-hostable Odoo.sh alternative** with full API control
- A **branch-based CI/CD platform** for Odoo development workflows
- A **policy engine** for environment promotion and lifecycle management
- A **deterministic build system** with reproducible artifacts

### What This Is Not

- ❌ A SaaS offering requiring external hosting
- ❌ A UI-driven platform (CLI/API-first philosophy)
- ❌ An Odoo Enterprise replacement (CE + OCA foundation)
- ❌ A general-purpose PaaS (Odoo-optimized only)

---

## Non-Negotiables

### 1. Everything is Code

**Principle**: All platform operations must be expressible as code and version-controlled.

**Requirements**:
- Configuration as YAML/JSON (no database-stored config)
- Deployment policies defined in git-tracked manifests
- Environment definitions in declarative format
- API-first design (CLI wraps API, not vice versa)

**Rationale**: Enables GitOps workflows, audit trails, and disaster recovery through infrastructure-as-code.

### 2. Deterministic Builds

**Principle**: Same input (commit SHA + policy) produces identical output environment.

**Requirements**:
- Lockfile-based dependency resolution (requirements.txt.lock, package-lock.json)
- Pinned base images with content-addressable references
- Build artifact caching with content hashes
- Reproducible database states through migration idempotency

**Rationale**: Eliminates "works on my machine" problems and ensures staging accurately represents production.

### 3. API-First Control Plane

**Principle**: Every platform operation accessible via REST API with authentication.

**Requirements**:
- OpenAPI 3.1 specification for all endpoints
- JWT-based authentication with scope-based authorization
- Rate limiting and quota enforcement
- Comprehensive error responses with troubleshooting context

**Rationale**: Enables automation, third-party integrations, and custom tooling without UI dependencies.

### 4. Branch-Based Isolation

**Principle**: Each git branch gets isolated environment with dedicated resources.

**Requirements**:
- Unique database per environment (no shared schemas)
- Isolated filestore and sessions
- Network-level separation (internal DNS per env)
- Resource quotas per branch type (dev/staging/prod)

**Rationale**: Prevents cross-contamination, enables parallel feature development, and supports safe experimentation.

### 5. Policy-Driven Lifecycle

**Principle**: Environment promotion governed by declarative policies, not manual approval.

**Requirements**:
- Branch mapping rules (develop→dev, release/*→staging, main→prod)
- Health gate requirements (tests, migrations, smoke checks)
- Auto-promotion triggers (commit to protected branch)
- TTL policies for ephemeral environments

**Rationale**: Reduces human error, enforces consistency, and accelerates delivery velocity.

---

## Success Metrics

### Developer Experience

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Time to First Deployment** | < 15 minutes | From repo clone to live dev environment |
| **Build Time (Clean)** | < 8 minutes | Full build without cache |
| **Build Time (Cached)** | < 2 minutes | Incremental build with layer cache |
| **Environment Spin-up** | < 3 minutes | New branch environment creation |
| **CLI Command Latency** | < 200ms | API response time (p95) |

### Platform Reliability

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Deployment Success Rate** | > 98% | Successful deployments / total attempts |
| **Rollback Time** | < 5 minutes | From failure detection to previous version live |
| **Environment Uptime** | > 99.5% | Scheduled availability (prod environments) |
| **Database Backup SLA** | < 1 hour RPO | Maximum data loss window |
| **Build Reproducibility** | 100% | Same commit SHA produces identical artifact |

### Operational Efficiency

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Infrastructure Cost per Env** | < $50/month | Average cost (dev/staging environments) |
| **Storage Efficiency** | > 80% deduplication | Shared layer reuse across environments |
| **Database Clone Time** | < 10 minutes | Prod database → staging clone |
| **Automated Test Coverage** | > 80% | Lines covered by CI test suite |
| **Manual Intervention Rate** | < 2% | Deployments requiring human action |

---

## Design Tenets

### 1. CLI is the Primary Interface

**Tenet**: Users interact primarily through `odooops` CLI, not web dashboard.

**Implications**:
- Documentation emphasizes command-line workflows
- Web UI (if present) is read-only observability layer
- All features ship with CLI support on day one
- API documentation is first-class (OpenAPI spec required)

**Example**:
```bash
# Create new environment
odooops env create feature/crm-reports --branch=feature/crm-reports

# Deploy to staging
odooops deploy staging --branch=release/v2.1 --wait

# Restore database
odooops db restore production --backup=2026-02-12-03-00 --to=staging
```

### 2. Convention over Configuration

**Tenet**: Sensible defaults with explicit override capability.

**Implications**:
- Git branch naming infers environment type (feature/* → dev, release/* → staging)
- Standard resource quotas by environment tier (dev: 2 workers, prod: 8 workers)
- Default backup schedules (prod: 6h, staging: 24h, dev: never)
- Override via `.odooops.yaml` in repository root

**Example**:
```yaml
# .odooops.yaml (optional overrides)
environments:
  production:
    workers: 12
    backup_schedule: "0 */3 * * *"  # Every 3 hours
    resource_limits:
      cpu: "4000m"
      memory: "8Gi"
```

### 3. Fail Fast with Actionable Errors

**Tenet**: Errors provide clear remediation steps, not vague messages.

**Implications**:
- Structured error responses with error codes and documentation links
- Pre-flight validation before expensive operations
- Health checks block deployment on failure (no silent degrades)
- Error messages include exact CLI command to fix

**Example**:
```json
{
  "error": "MIGRATION_PENDING",
  "message": "Database has 3 pending migrations",
  "remediation": "Run 'odooops db migrate staging' to apply migrations",
  "migrations": ["0042_add_crm_fields", "0043_rename_table", "0044_create_index"],
  "docs": "https://docs.odooops.io/errors/MIGRATION_PENDING"
}
```

### 4. Optimize for Common Workflows

**Tenet**: 80% of operations should be single-command actions.

**Implications**:
- `odooops push` handles build + test + deploy pipeline
- `odooops rollback` automatically identifies last good version
- `odooops logs` tails logs from all services in environment
- `odooops shell` drops into environment with context pre-loaded

**Common Workflows**:
```bash
# Feature development cycle
odooops env create feature/new-reports
odooops push --wait
odooops logs --follow
odooops destroy feature/new-reports  # When merged

# Production hotfix
odooops branch hotfix/urgent-fix --from=production
odooops push hotfix/urgent-fix --to=staging --wait
odooops promote staging production --confirm
```

### 5. Security by Default

**Tenet**: Secure defaults without sacrificing developer experience.

**Implications**:
- All API endpoints require authentication (no public endpoints)
- Database credentials rotated per environment
- Secrets managed via encrypted vault, never in git
- Network policies isolate environments by default

**Security Controls**:
- JWT tokens with 12-hour expiry
- IP allowlists for production environments
- Audit log for all control plane operations
- Encrypted database backups with customer-managed keys

---

## Architectural Principles

### Separation of Concerns

**Control Plane** (orchestration, API, CLI):
- API server (FastAPI/Python)
- Policy engine (declarative YAML rules)
- Build scheduler (celery workers)
- Database migration runner

**Data Plane** (runtime Odoo environments):
- Odoo application servers (Gunicorn workers)
- PostgreSQL databases (per environment)
- nginx reverse proxies (per environment)
- Redis caches (shared per node)

**Monitoring Plane** (observability - see observability spec):
- OpenTelemetry collector
- Prometheus metrics
- Loki log aggregation
- AlertManager

### State Management

**Immutable Infrastructure**:
- Container images are immutable (tagged with commit SHA)
- Environments are cattle, not pets (destroy and recreate)
- Configuration changes trigger full redeploy

**Persistent State**:
- Database: External managed PostgreSQL (DigitalOcean Managed DB)
- Filestore: S3-compatible object storage (DigitalOcean Spaces)
- Backups: Versioned snapshots with retention policies

**Ephemeral State**:
- Build artifacts: Cached with 7-day TTL
- Session data: Redis with 24-hour TTL
- Logs: Forwarded to aggregator (not stored locally)

### Resource Allocation

**Environment Tiers**:

| Tier | Workers | CPU | Memory | Database | Storage | TTL |
|------|---------|-----|--------|----------|---------|-----|
| **Production** | 8 | 4 cores | 8GB | Shared managed | 100GB | Permanent |
| **Staging** | 4 | 2 cores | 4GB | Shared managed | 50GB | Permanent |
| **Dev (Named)** | 2 | 1 core | 2GB | Dedicated mini | 10GB | 14 days |
| **Dev (Ephemeral)** | 1 | 0.5 core | 1GB | Dedicated mini | 5GB | 7 days |

**Quota Enforcement**:
- Per-user environment limits (e.g., 3 concurrent dev envs)
- Storage quotas with hard limits (no auto-expansion)
- CPU throttling when exceeding allocation
- Network egress limits (prevents runaway costs)

---

## Adoption Criteria

### Minimum Viable Platform (MVP)

Before declaring "v1.0 ready":

- [ ] **Core API**: 20 endpoints (env CRUD, deploy, logs, backup/restore)
- [ ] **CLI**: 15 commands covering common workflows
- [ ] **Git Integration**: Webhook-driven deployments from GitHub
- [ ] **Policy Engine**: Branch mapping + health gates working
- [ ] **Database Management**: Backup/restore/clone operations
- [ ] **Documentation**: OpenAPI spec + CLI usage guide + architecture diagram

### Production Readiness

Before deploying real customer workloads:

- [ ] **Uptime**: 99.5% availability over 30-day period
- [ ] **Performance**: < 200ms API latency (p95)
- [ ] **Security**: Passed external penetration test
- [ ] **Disaster Recovery**: Tested full restore from backup
- [ ] **Observability**: Prometheus + Loki + AlertManager integrated
- [ ] **Support**: Runbooks for 10 most common failure scenarios

### Feature Completeness

Before considering feature-complete:

- [ ] **Multi-tenancy**: Isolated tenants with quota enforcement
- [ ] **Custom Domains**: HTTPS with Let's Encrypt automation
- [ ] **Database Masking**: PII anonymization for non-prod clones
- [ ] **SSH/Shell Access**: Ephemeral access with audit logging
- [ ] **Mail Neutralization**: Outbound email capture for dev/staging
- [ ] **Backup Retention**: Tiered retention (7d dev, 30d staging, 90d prod)

---

## Constraints and Limitations

### Technical Constraints

**Database**:
- PostgreSQL 16 only (Odoo 19 requirement)
- No sharding support (single database per environment)
- Backup window: 10 minutes of downtime for large databases (>50GB)

**Networking**:
- Internal DNS resolution only (no public IPs for dev environments)
- Outbound HTTPS required (for addon downloads, Let's Encrypt)
- Ingress limited to HTTPS (no HTTP or custom ports)

**Storage**:
- Filestore must support POSIX semantics (NFS or S3FS)
- Maximum 1TB per environment (hard limit)
- No support for customer-provided storage backends

### Operational Constraints

**Deployment**:
- Maximum 10 concurrent deployments (queued beyond that)
- Build timeouts at 30 minutes (hard limit)
- Deployment rollback limited to 10 most recent versions

**Monitoring**:
- 30-day retention for metrics and logs (see observability spec)
- No real-time streaming (15-second polling interval minimum)
- Alert de-duplication with 5-minute window

**Support**:
- Self-hosted (no SLA from InsightPulse AI)
- Community-driven troubleshooting
- Commercial support available separately

---

## Evolution and Governance

### Version Strategy

**Semantic Versioning**: `MAJOR.MINOR.PATCH`

- **MAJOR**: Breaking API changes (backward incompatible)
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes and security updates

**Deprecation Policy**:
- 2 minor versions notice before removal
- Deprecation warnings in API responses
- Migration guides for breaking changes

### Specification Ownership

**Primary Owner**: InsightPulse AI Platform Team
**Reviewers**: DevOps team, Security team, Odoo developers
**Approval Process**: RFC for major changes, PR review for minor updates

**Change Process**:
1. Propose change via GitHub issue (with "spec-change" label)
2. Draft amendment to constitution/PRD
3. Review with stakeholders (1-week feedback period)
4. Merge after approval (requires 2 approvals from core team)
5. Update implementation plan and tasks

---

## References

### Related Specifications

- **`spec/odoo-sh-next/`**: Original platform spec (14.3K lines) - foundation for this spec
- **`spec/platform-kit/`**: Generic platform patterns and abstractions
- **`spec/odooops-observability-enterprise-pack/`**: Observability layer extending this platform

### External Standards

- **OpenAPI 3.1**: API specification format
- **Conventional Commits**: Git commit message format
- **OCA Guidelines**: Odoo module development standards
- **OWASP Top 10**: Security baseline requirements
- **12-Factor App**: Application architecture principles

### Documentation

- **Architecture**: `docs/architecture/PROD_RUNTIME_SNAPSHOT.md`
- **CI/CD**: `.github/workflows/cd-production.yml`
- **Monitoring**: `infra/monitoring/docker-compose.monitoring.yml`
- **Supabase**: `docs/ai/SUPABASE.md`

---

**Document Status**: ✅ Constitution finalized
**Next Steps**: Create PRD, Plan, and Tasks documents
**Review Cadence**: Quarterly (or on major platform changes)
