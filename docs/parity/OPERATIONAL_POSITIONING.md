# Operational Positioning: IPAI Odoo Stack

**Generated**: 2026-01-28
**Stack**: Odoo 18 CE + OCA + IPAI Enterprise Bridge
**Deployment Model**: Self-hosted, AI-first, cloud-native

---

## Executive Summary

This document describes the operational architecture, deployment model, and integration boundaries for the IPAI Odoo stack in production and staging environments.

**Key Operational Characteristics**:
- **Self-Hosted**: DigitalOcean droplets, no Odoo.com dependencies
- **Microservices**: Odoo + PostgreSQL + n8n + Supabase + Apache Superset
- **AI-First**: Custom AI agents, OCR, automation via OpenAI/Claude
- **Cost-Optimized**: ~$50-100/month infrastructure vs $10K-$50K/year Enterprise

---

## Deployment Architecture

### Production Environment

**Hosting**: DigitalOcean (self-hosted)
**Primary Droplet**: odoo-erp-prod (159.223.75.148)
- **Specs**: SGP1 / 4GB RAM / 80GB Disk
- **Services**: Odoo 18 CE, PostgreSQL 16, n8n
- **DNS**: erp.insightpulseai.net

**Secondary Droplet**: ocr-service-droplet (188.166.237.231)
- **Specs**: SGP1 / 8GB RAM / 80GB Disk
- **Services**: Agent Service (Claude 3.5 Sonnet), OCR Service (PaddleOCR-VL)
- **DNS**: ocr.insightpulseai.net

```
┌─────────────────────────────────────────────────────────────┐
│          Production Architecture (Self-Hosted)              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   n8n ◄──► Odoo CE 19 ◄──► PostgreSQL 16                  │
│    │         (8069)          (5432)                         │
│    │                                                        │
│    ├──► Supabase (external integrations, storage)          │
│    ├──► Apache Superset (BI dashboards)                    │
│    ├──► OCR Service (PaddleOCR-VL + OpenAI)                │
│    └──► Claude Agents (automation, AI workflows)           │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Staging Environment

**Location**: `sandbox/dev/` (local development sandbox)
**Services**: Odoo 18 CE + PostgreSQL 16 (Docker Compose)
**Purpose**: Module development, OCA testing, pre-production validation

```yaml
# docker-compose.yml (simplified)
services:
  db:
    image: postgres:16-alpine
    ports: ["5433:5432"]

  odoo:
    image: ghcr.io/jgtolentino/odoo-ce:19.0-ee-parity
    ports: ["8069:8069", "8072:8072"]
    command: --dev=reload,qweb,werkzeug,xml
```

---

## Integration Boundaries

### Core ERP (Odoo 18 CE)
**Scope**: Financial accounting, HR, project management, CRM
**Data Owner**: Odoo PostgreSQL database
**Access**: REST API, XML-RPC, ORM (Python)

**Key Modules**:
- Accounting: Bank reconciliation, financial reports, asset management
- HR: Payroll (PH), attendance, leave management
- Projects: Tasks, timesheets, planning
- CRM: Leads, opportunities, sales pipeline

### External AI/ML Layer
**Purpose**: Replace Odoo Enterprise AI/OCR with custom models

| Feature | Odoo EE Approach | Our Approach |
|---------|-----------------|--------------|
| **Document OCR** | Odoo.com IAP subscription | PaddleOCR-VL (self-hosted) + OpenAI gpt-4o-mini |
| **Email Classification** | Odoo.com AI model | Claude 3.5 Sonnet via n8n |
| **Lead Scoring** | Odoo.com predictive | Custom scikit-learn model |
| **Invoice Matching** | Odoo.com OCR + matching | PaddleOCR + fuzzy matching |

**Integration Method**:
- **n8n Workflows**: Trigger on Odoo events → Call AI service → Update Odoo
- **Supabase Edge Functions**: Real-time processing for high-frequency events
- **Direct API Calls**: From IPAI modules to external AI endpoints

### BI/Analytics Layer (Apache Superset)
**Purpose**: Replace Odoo Enterprise Spreadsheet/BI with self-hosted analytics

**Data Flow**:
```
Odoo PostgreSQL → Supabase (ETL) → Apache Superset (visualization)
                    ↓
                Bronze/Silver/Gold tables (medallion architecture)
```

**Features**:
- Financial dashboards (P&L, balance sheet, cash flow)
- Project analytics (burn rate, resource utilization)
- HR metrics (headcount, attendance, leave balance)
- Custom BI reports (BIR compliance, multi-employee consolidation)

**Cost Savings**: $5K-$10K/year vs Odoo Enterprise Spreadsheet module

### Automation Layer (n8n)
**Purpose**: Replace Odoo Studio automation with self-hosted workflows

**Workflow Examples**:
1. **BIR Tax Filing**: Schedule → Query Odoo → Generate PDF → Store → Notify
2. **Expense Approval**: Webhook → Validate rules → Route → Update → Alert
3. **Performance Monitor**: Query Odoo logs → Compute metrics → Alert if threshold exceeded

**Integration Points**:
- **Odoo XML-RPC**: Read/write Odoo data
- **Webhooks**: Trigger n8n on Odoo events
- **PostgreSQL Direct**: Query database for analytics
- **External APIs**: Supabase, Mattermost, Twilio, OpenAI

---

## Support Model

### Internal Operations
**Primary Support**: In-house engineering team
**Tools**: GitHub Issues, n8n incident workflows, Claude Code agents
**SLA**: Best-effort (no formal SLA, faster than Enterprise)

### Community Support
**OCA Community**: GitHub Issues, OCA maintainers
**Response Time**: Variable (community-driven)
**Contribution Model**: Submit fixes upstream for shared benefit

### Commercial Support (Optional)
**OCA Services**: Available for critical issues (~$5K-$10K/year if needed)
**Custom Development**: IPAI team handles all customizations
**Cost**: $0 baseline vs $10K-$50K/year Enterprise support

---

## Deployment Workflow

### Module Deployment Process
```bash
# 1. Development (local sandbox)
cd sandbox/dev
docker compose up -d
# Develop ipai_* modules

# 2. Testing
./scripts/ci/run_odoo_tests.sh
./scripts/verify.sh

# 3. Commit
git add addons/ipai/module_name/
git commit -m "feat(module): add feature X"
git push origin feature-branch

# 4. CI/CD (GitHub Actions)
# - Lint checks
# - Unit tests
# - Compliance scan (scripts/parity/check_no_enterprise_code.sh)
# - Build Docker image

# 5. Production deployment
ssh root@159.223.75.148
cd /opt/odoo-ce
git pull origin main
docker compose restart odoo-core
```

### Zero-Downtime Deployment Strategy
**Method**: Blue-green deployment with database migration pre-check

```bash
# 1. Deploy to "green" container
docker compose up -d odoo-green

# 2. Run migrations
docker exec odoo-green odoo -d production -u all --stop-after-init

# 3. Health check
curl -f http://localhost:8069/web/health

# 4. Switch nginx upstream (blue → green)
nginx -s reload

# 5. Terminate old "blue" container
docker compose stop odoo-blue
```

---

## Data Sovereignty

### Data Residency
**Primary Database**: DigitalOcean Singapore (SGP1)
**Backup Storage**: DigitalOcean Spaces (SGP1)
**No Data Sharing**: Zero data transmitted to Odoo.com or third parties

**Exceptions** (with data minimization):
- **OpenAI API**: Anonymized text for OCR post-processing (30-day retention)
- **Supabase**: Database sync for BI (data owned, no third-party access)

### GDPR/Privacy Compliance
- ✅ Data processor agreements in place (DigitalOcean, Supabase)
- ✅ No Odoo.com data sharing (self-hosted stack)
- ✅ Data retention policies configured (90 days for logs, 7 years for financial)
- ✅ Right to erasure implemented (Odoo GDPR module + custom scripts)

---

## Monitoring & Observability

### Health Checks
**Odoo**: `/web/health` endpoint (HTTP 200 = healthy)
**PostgreSQL**: Connection pool monitoring (PgBouncer)
**n8n**: Workflow execution status (API)
**Supabase**: Edge Function logs (Supabase dashboard)

### Alerting
**Critical Alerts** (immediate notification):
- Odoo server down (>2 minutes)
- PostgreSQL connection failure
- Disk usage >85%
- Memory usage >90%

**Warning Alerts** (review within 24h):
- Odoo response time >3 seconds (P95)
- Database query time >1 second
- Failed n8n workflows >5%

**Alert Channels**:
- Mattermost (deprecated - replaced with email)
- Email (finance@insightpulseai.com)
- n8n incident workflows (auto-remediation)

### Performance Metrics
**Target SLAs** (self-imposed):
- **Uptime**: 99.5% (43.8 hours downtime/year acceptable)
- **Response Time**: <2 seconds (P95)
- **Database Queries**: <500ms (P95)
- **OCR Processing**: <30 seconds per document

---

## Disaster Recovery

### Backup Strategy
**PostgreSQL**:
- **Full Backup**: Daily at 2 AM UTC (pg_dump)
- **Incremental**: WAL archiving (every 15 minutes)
- **Retention**: 30 days full, 7 days incremental
- **Storage**: DigitalOcean Spaces (SGP1)

**Odoo Filestore**:
- **Backup**: Daily rsync to Supabase Storage
- **Retention**: 30 days
- **Size**: ~5GB (attachments, documents)

### Recovery Procedures
**RTO (Recovery Time Objective)**: 4 hours
**RPO (Recovery Point Objective)**: 15 minutes (via WAL archiving)

**Recovery Steps**:
```bash
# 1. Provision new droplet (if primary failed)
doctl compute droplet create odoo-erp-prod-recovery ...

# 2. Restore PostgreSQL
psql < backup_2026-01-28.sql

# 3. Restore filestore
aws s3 sync s3://odoo-backups/filestore /opt/odoo/filestore

# 4. Start Odoo
docker compose up -d

# 5. Verify
curl -f http://localhost:8069/web/health
```

---

## Cost Analysis

### Monthly Infrastructure Costs
| Component | Provider | Cost |
|-----------|----------|------|
| **Odoo Droplet** (4GB) | DigitalOcean | $24/month |
| **OCR Droplet** (8GB) | DigitalOcean | $48/month |
| **PostgreSQL** (included) | Self-hosted | $0 |
| **Backups** (100GB) | DO Spaces | $5/month |
| **Bandwidth** (~500GB) | DigitalOcean | $10/month |
| **Supabase** (Pro plan) | Supabase | $25/month |
| **OpenAI API** (~1M tokens/month) | OpenAI | $20/month |
| **Domain + SSL** | Let's Encrypt | $0 (free) |
| **Total** | | **~$132/month** |

### Annual Cost Comparison
| Scenario | Annual Cost | Notes |
|----------|-------------|-------|
| **Our Stack** (self-hosted) | **~$1,584/year** | Full control, AI-first |
| **Odoo Enterprise** (20 users) | ~$40,000/year | $2K/user/year |
| **Odoo.sh** (hosting) | ~$10,000/year | Managed hosting |
| **Total Enterprise** | **~$50,000/year** | Official Enterprise + hosting |
| **Savings** | **~$48,416/year** | 97% cost reduction |

---

## Security Posture

### Infrastructure Security
- ✅ Firewall rules (UFW): Only ports 80, 443, 22 exposed
- ✅ SSH key-only authentication (no password login)
- ✅ Fail2ban: Auto-ban after 5 failed login attempts
- ✅ SSL/TLS: Let's Encrypt certificates (auto-renewal)
- ✅ PostgreSQL: No public access (localhost only)

### Application Security
- ✅ Odoo RLS (Row-Level Security): Multi-tenant data isolation
- ✅ Supabase RLS policies: Database-level access control
- ✅ n8n credential vault: Encrypted credential storage
- ✅ Secret management: Environment variables, no hardcoded keys

### Compliance Scanning
**CI/CD Gate**: `scripts/parity/check_no_enterprise_code.sh`
- Runs on every commit
- Blocks merge if violations detected
- Verifies no Enterprise code present

---

## Scalability & Growth

### Current Capacity
- **Users**: 20 concurrent (tested)
- **Records**: 500K+ (database size: 15GB)
- **Throughput**: 500 requests/minute (sustained)

### Scaling Strategy (if >50 users)
1. **Vertical Scaling** (first step):
   - Upgrade droplet: 4GB → 8GB RAM
   - Cost: +$24/month
   - Capacity: 50-100 users

2. **Horizontal Scaling** (if >100 users):
   - Add second Odoo container (load-balanced)
   - PostgreSQL read replicas
   - Cost: +$50-100/month
   - Capacity: 100-500 users

3. **Managed Database** (if >500 users):
   - DigitalOcean Managed PostgreSQL
   - Cost: +$100-200/month
   - Benefit: Automatic backups, failover

**Key Point**: Still <$5K/year at 500 users vs $1M/year Odoo Enterprise

---

## Migration Path (Future Odoo 19 Upgrade)

### Pre-Requisites for Odoo 19 Upgrade
1. ✅ OCA 19.0 ecosystem mature (≥50% modules ported)
2. ⏳ IPAI modules tested on 19 CE staging
3. ⏳ Database migration script validated
4. ⏳ Zero-downtime migration plan finalized

### Estimated Timeline
**Q2 2026**: OCA 19.0 branch stabilization monitoring
**Q3 2026**: IPAI module compatibility testing (staging)
**Q4 2026**: Production upgrade (if OCA ecosystem ready)

**Fallback**: Remain on 18 CE + OCA 18 if 19 migration risky

---

## Conclusion

**Operational Model**: Self-hosted, cost-optimized, AI-first ERP stack
**Cost Efficiency**: 97% savings vs Odoo Enterprise ($1.6K vs $50K/year)
**Data Sovereignty**: 100% data ownership, no vendor lock-in
**Scalability**: Proven to 20 users, roadmap to 500+ users
**Support**: Internal ops + OCA community (faster than Enterprise)

**Recommendation**: Current operational model is production-ready and sustainable for TBWA/W9 use cases.

---

**Report Version**: 1.0.0
**Next Review**: Q2 2026 (operational metrics review)
