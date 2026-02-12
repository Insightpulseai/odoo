# Documentation Enhancement Specification v2.0

**Status:** Design Specification
**Priority:** MEDIUM
**Scope:** Repository-wide documentation updates
**Version:** 1.0.0

---

## Overview

This specification addresses critical documentation gaps identified during the dual-track enhancement plan:

1. **IP Address Placeholders:** Replace `<PRODUCTION_IP>` with canonical IP `178.128.112.214`
2. **Repository Name Updates:** Replace `jgtolentino/odoo` with `Insightpulseai/odoo`
3. **CLI-Only Deployment Patterns:** Add no-UI database operation recipes
4. **Production Validation Checklist:** Create structured verification procedures

**Strategic Context:**
- Production deployment readiness (Finance PPM Phase 3)
- "No UI clickpath instructions" policy enforcement
- Canonical endpoint documentation for agent automation

---

## Audit Results

### 1. IP Address Placeholders

**File:** `docs/pages/runbooks.md:14`
```bash
ssh root@<PRODUCTION_IP>
```

**Fix:** Replace with canonical IP:
```bash
ssh root@178.128.112.214
```

**Rationale:** Placeholder forces manual replacement, breaks automation, contradicts agent contract.

---

### 2. Repository Name Outdated References

**Scope:** 100+ files containing `jgtolentino/odoo`

**Critical Files (Sample):**
- `docs/ODOO_ADDONS_PATH_CONFIGURATION.md` - Docker image reference
- `docs/DOCKER_VALIDATION_GUIDE.md` - Registry URL
- `docs/REPOSITORY_STRUCTURE.md` - Remote URL documentation
- `docs/pages/runbooks.md:11` - GitHub CLI commands
- `README.md` - Repository badges and URLs

**Example Fix:**
```diff
- gh run list --workflow "ci-odoo.yml" --repo jgtolentino/odoo
+ gh run list --workflow "ci-odoo.yml" --repo Insightpulseai/odoo
```

**Scope:**
- GitHub Actions workflow references
- Docker image URIs
- Git remote URLs
- Badge URLs in README
- Documentation cross-references

---

### 3. Missing CLI-Only Patterns

**Gap:** Production runbooks assume Docker Compose UI-based workflows
**Need:** CLI-only module installation and database operations

**New Section:** `docs/pages/runbooks.md` - "CLI-Only Database Operations"

```markdown
## CLI-Only Database Operations

### Module Installation (No UI)

**Production Environment:**
- Container: odoo-prod
- Database: odoo (DigitalOcean Managed PostgreSQL 16)
- Config: /etc/odoo/odoo.conf

**Install Module:**
```bash
docker exec odoo-prod /usr/bin/odoo \
  -c /etc/odoo/odoo.conf \
  -d odoo \
  -i ipai_finance_ppm_umbrella \
  --stop-after-init \
  --log-level=info
```

**Verify Module State:**
```bash
docker exec odoo-prod /usr/bin/odoo shell -c /etc/odoo/odoo.conf -d odoo << 'PYEOF'
module = env['ir.module.module'].search([('name', '=', 'ipai_finance_ppm_umbrella')])
print(f"State: {module.state}")
assert module.state == 'installed', f"Expected installed, got {module.state}"
PYEOF
```

**Uninstall Module (Rollback):**
```bash
docker exec odoo-prod /usr/bin/odoo \
  -c /etc/odoo/odoo.conf \
  -d odoo \
  -u ipai_finance_ppm_umbrella \
  --stop-after-init
```

**Update Module List:**
```bash
docker exec odoo-prod /usr/bin/odoo shell -c /etc/odoo/odoo.conf -d odoo << 'PYEOF'
env['ir.module.module'].update_list()
print("✅ Module list updated")
PYEOF
```

### Database Validation (No UI)

**Check Record Counts:**
```bash
docker exec odoo-prod /usr/bin/odoo shell -c /etc/odoo/odoo.conf -d odoo << 'PYEOF'
users = env['res.users'].search([('active', '=', True)])
print(f"Active users: {len(users)}")

tasks = env['project.task'].search([])
print(f"Total tasks: {len(tasks)}")
PYEOF
```

**Verify Specific User:**
```bash
docker exec odoo-prod /usr/bin/odoo shell -c /etc/odoo/odoo.conf -d odoo << 'PYEOF'
ckvc = env['res.users'].search([('login', '=', 'ckvc')])
if ckvc:
    print(f"✅ CKVC found: {ckvc.name} (ID: {ckvc.id})")
else:
    print("❌ CKVC not found")
PYEOF
```

### Performance Validation

**Query Timing:**
```bash
docker exec odoo-prod /usr/bin/odoo shell -c /etc/odoo/odoo.conf -d odoo << 'PYEOF'
import time

start = time.time()
users = env['res.users'].search([])
duration = time.time() - start
print(f"User query: {duration:.3f}s for {len(users)} records")
assert duration < 1.0, f"Query too slow: {duration:.3f}s"
PYEOF
```
```

---

### 4. Production Validation Checklist

**New File:** `docs/pages/production-validation.md`

```markdown
# Production Validation Checklist

## Pre-Deployment Validation

### Code Quality
- [ ] All CI gates pass on main branch
- [ ] Seed data consistency gate passes
- [ ] Enterprise code scan shows 0 violations
- [ ] No linting or type errors

### Module Verification
- [ ] Module `__manifest__.py` version incremented
- [ ] Dependencies declared correctly
- [ ] Demo data disabled (`"demo": False`)
- [ ] Security groups defined
- [ ] Access rights configured

### Database Preparation
- [ ] Database backup created (< 1 hour old)
- [ ] Database authentication tested (psycopg2 test passes)
- [ ] Module not already installed in production
- [ ] Sufficient database storage available

## Deployment Validation

### Module Installation
- [ ] Module update_list successful
- [ ] Module install completed without errors
- [ ] Module state = 'installed'
- [ ] Container restart successful
- [ ] No errors in container logs

### Seed Data Validation
- [ ] Expected user records present
- [ ] Seed record counts match thresholds
- [ ] Foreign key references intact
- [ ] No orphaned records

### Performance Validation
- [ ] Web UI accessible (https://erp.insightpulseai.com)
- [ ] Query performance < 2 seconds
- [ ] No JavaScript errors in browser console
- [ ] Menu items render correctly

## Post-Deployment Validation

### Health Checks
- [ ] Health endpoint returns 200 (http://localhost:8069/web/health)
- [ ] Database connection pool healthy
- [ ] Cron jobs running (if applicable)
- [ ] Email notifications working (if applicable)

### Rollback Readiness
- [ ] Rollback procedure documented
- [ ] Database backup location confirmed
- [ ] Uninstall command tested (in staging)
- [ ] Downtime window communicated (if needed)

## Verification Commands

### Database Authentication Test
```bash
docker exec odoo-prod python3 << 'PYEOF'
import psycopg2
import os

password = os.environ.get('DB_PASSWORD', 'DISCOVERED_PASSWORD_HERE')

try:
    conn = psycopg2.connect(
        host="private-odoo-db-sgp1-do-user-27714628-0.g.db.ondigitalocean.com",
        port=25060,
        database="odoo",
        user="doadmin",
        password=password,
        sslmode="require"
    )
    cur = conn.cursor()
    cur.execute("SELECT 1")
    print("✅ Authentication successful")
    conn.close()
except Exception as e:
    print(f"❌ Authentication failed: {type(e).__name__}: {str(e)[:200]}")
PYEOF
```

### Module State Verification
```bash
docker exec odoo-prod /usr/bin/odoo shell -c /etc/odoo/odoo.conf -d odoo << 'PYEOF'
module = env['ir.module.module'].search([('name', '=', 'ipai_finance_ppm_umbrella')])
print(f"State: {module.state}")
print(f"Version: {module.latest_version}")
assert module.state == 'installed', f"Expected installed, got {module.state}"
print("✅ Module successfully installed")
PYEOF
```

### Seed Data Validation
```bash
cd /Users/tbwa/Documents/GitHub/Insightpulseai/odoo
python3 scripts/finance_ppm_seed_audit.py

# Expected output:
# {
#   "employees_count": 9,
#   "bir_count": 144,
#   "tasks_count": 36,
#   "raci_count": 9,
#   "errors": [],
#   "pass": true
# }
```

### Performance Validation
```bash
docker exec odoo-prod /usr/bin/odoo shell -c /etc/odoo/odoo.conf -d odoo << 'PYEOF'
import time

start = time.time()
users = env['res.users'].search([])
duration = time.time() - start
print(f"User query: {duration:.3f}s for {len(users)} records")
assert duration < 1.0, f"Query too slow: {duration:.3f}s"

print("✅ Performance within acceptable limits")
PYEOF
```

## Escalation

**Critical Issues:**
- Module installation fails → Contact: DevOps team
- Database authentication fails → Contact: DBA team
- Performance degradation → Contact: Infrastructure team
- Data corruption → Initiate rollback immediately

**References:**
- Production runbook: `docs/runbooks/finance-ppm-production-deployment.md`
- Rollback procedure: `docs/pages/rollback-procedures.md`
- Monitoring dashboard: https://erp.insightpulseai.com/monitoring
```

---

## Production Endpoints Canonical Documentation

**New File:** `docs/architecture/production-endpoints.md`

```markdown
# Production Endpoints Registry

**Last Updated:** 2026-02-13
**Status:** Canonical SSOT
**Purpose:** Single source of truth for all production IPs, domains, and service endpoints

---

## Primary Infrastructure

### DigitalOcean Droplet

**IP Address:** `178.128.112.214`
**Hostname:** `odoo-prod-01`
**Region:** SGP1 (Singapore)
**OS:** Ubuntu 22.04 LTS
**SSH Access:**
```bash
ssh root@178.128.112.214
```

**Services:**
- Odoo CE 19.0 (container: `odoo-prod`)
- n8n automation
- Nginx reverse proxy
- Docker runtime

---

## Domain Configuration

**Primary Domain:** `insightpulseai.com`
**DNS Provider:** Cloudflare (delegated from Spacesquare)

| Subdomain | Type | Target | Service |
|-----------|------|--------|---------|
| erp | A | 178.128.112.214 | Odoo ERP |
| n8n | A | 178.128.112.214 | n8n automation |
| auth | A | 178.128.112.214 | Authentication |
| ocr | A | 178.128.112.214 | OCR service |

**SSL/TLS:** Let's Encrypt via Certbot
**HTTPS:** Enforced (HTTP → HTTPS redirect)

---

## Database Configuration

**Provider:** DigitalOcean Managed PostgreSQL 16
**Connection:**
- **Host:** `private-odoo-db-sgp1-do-user-27714628-0.g.db.ondigitalocean.com`
- **Port:** `25060`
- **User:** `doadmin`
- **Database:** `odoo` (NOT `odoo_prod` - common misconception)
- **SSL:** `require` (mandatory)

**Password Management:**
- Environment variable: `DB_PASSWORD` (injected via Docker Compose)
- Rotation: Managed via `doctl databases user reset`

**Connection Test:**
```bash
docker exec odoo-prod python3 << 'PYEOF'
import psycopg2
import os
conn = psycopg2.connect(
    host="private-odoo-db-sgp1-do-user-27714628-0.g.db.ondigitalocean.com",
    port=25060,
    database="odoo",
    user="doadmin",
    password=os.environ.get('DB_PASSWORD'),
    sslmode="require"
)
cur = conn.cursor()
cur.execute("SELECT 1")
print("✅ Connection successful")
conn.close()
PYEOF
```

---

## Service Endpoints

### Odoo ERP
- **Public URL:** https://erp.insightpulseai.com
- **Health Check:** http://localhost:8069/web/health (internal)
- **Container:** `odoo-prod`
- **Port:** 8069 (internal), 443 (external via Nginx)

### n8n Automation
- **Public URL:** https://n8n.insightpulseai.com
- **Container:** `n8n`
- **Port:** 5678

### OCR Service (PaddleOCR-VL)
- **Public URL:** https://ocr.insightpulseai.com
- **Container:** `ocr-service`
- **Port:** 8000

---

## Email Configuration

**Provider:** Zoho Mail
**SMTP:**
- **Host:** `smtp.zoho.com`
- **Port:** `587` (STARTTLS)
- **User:** `noreply@insightpulseai.com`
- **From:** `InsightPulse AI <noreply@insightpulseai.com>`

**Configuration:**
```python
# /etc/odoo/odoo.conf
smtp_server = smtp.zoho.com
smtp_port = 587
smtp_user = noreply@insightpulseai.com
smtp_password = ${ZOHO_SMTP_PASSWORD}
smtp_ssl = False
smtp_starttls = True
```

---

## Deprecated Endpoints (DO NOT USE)

| Item | Replacement | Deprecated Date |
|------|-------------|-----------------|
| `insightpulseai.net` | `insightpulseai.com` | 2026-02 |
| Mattermost (`chat.insightpulseai.com`) | Slack | 2026-01-28 |
| Mailgun SMTP | Zoho Mail | 2026-02 |

---

## Monitoring & Observability

**Logs:**
```bash
# Odoo container logs
docker logs odoo-prod --tail 50 --follow

# Nginx access logs
tail -f /var/log/nginx/access.log

# Nginx error logs
tail -f /var/log/nginx/error.log
```

**Metrics:**
```bash
# Container stats
docker stats odoo-prod

# Database connection count
docker exec odoo-prod /usr/bin/odoo shell -c /etc/odoo/odoo.conf -d odoo << 'PYEOF'
import psycopg2
# ... connection count query ...
PYEOF
```

---

## Security

**Firewall Rules (UFW):**
- 22/tcp (SSH) - restricted to specific IPs
- 80/tcp (HTTP) - redirect to HTTPS
- 443/tcp (HTTPS) - public
- 5432/tcp (PostgreSQL) - blocked (managed DB only)

**SSL Certificates:**
```bash
# Renewal check
certbot renew --dry-run

# Certificate expiry
certbot certificates
```

---

## References

- Infrastructure SSOT: `docs/architecture/PROD_RUNTIME_SNAPSHOT.md`
- Machine-readable: `docs/architecture/runtime_identifiers.json`
- Deployment timeline: `docs/pages/deployment-timeline.md`
- Runbooks: `docs/pages/runbooks.md`
```

---

## README Enhancement

**File:** `README.md`

**New Section (append before "Contributing"):**

```markdown
## Production Deployment Validation

### Prerequisites

- [ ] All CI gates pass on main branch
- [ ] Database backup created (< 1 hour old)
- [ ] Production SSH access verified

### Module Installation (CLI-Only)

**Production Environment:**
- **Droplet:** 178.128.112.214 (`odoo-prod-01`)
- **Container:** `odoo-prod`
- **Database:** `odoo` @ `private-odoo-db-sgp1-do-user-27714628-0.g.db.ondigitalocean.com:25060`

**Install Module:**
```bash
ssh root@178.128.112.214

docker exec odoo-prod /usr/bin/odoo \
  -c /etc/odoo/odoo.conf \
  -d odoo \
  -i ipai_finance_ppm_umbrella \
  --stop-after-init \
  --log-level=info
```

**Verify Installation:**
```bash
docker exec odoo-prod /usr/bin/odoo shell -c /etc/odoo/odoo.conf -d odoo << 'PYEOF'
module = env['ir.module.module'].search([('name', '=', 'ipai_finance_ppm_umbrella')])
assert module.state == 'installed', f"Expected installed, got {module.state}"
print("✅ Module successfully installed")
PYEOF
```

**Rollback:**
```bash
docker exec odoo-prod /usr/bin/odoo \
  -c /etc/odoo/odoo.conf \
  -d odoo \
  -u ipai_finance_ppm_umbrella \
  --stop-after-init
```

### Validation Checklist

- [ ] Module state = 'installed'
- [ ] Seed data audit passes (210 records)
- [ ] Web UI accessible (https://erp.insightpulseai.com)
- [ ] Query performance < 2 seconds
- [ ] No errors in container logs

### References

- **Production Endpoints:** [docs/architecture/production-endpoints.md](docs/architecture/production-endpoints.md)
- **Runbooks:** [docs/pages/runbooks.md](docs/pages/runbooks.md)
- **Validation Checklist:** [docs/pages/production-validation.md](docs/pages/production-validation.md)
```

---

## Implementation Checklist

### Phase 1: IP Address Replacement (LOW RISK)

**Files to Update:**
- [ ] `docs/pages/runbooks.md` - Replace `<PRODUCTION_IP>` with `178.128.112.214`
- [ ] Create `docs/architecture/production-endpoints.md` (canonical registry)

**Validation:**
```bash
# Ensure no placeholders remain
grep -r "<PRODUCTION_IP>\|YOUR_IP" docs/
```

### Phase 2: Repository Name Updates (MEDIUM RISK)

**Strategy:** Global search-and-replace with verification

**Command:**
```bash
# Dry run first
find docs/ README.md -type f -exec grep -l "jgtolentino/odoo" {} \; | \
  xargs -I{} echo "Would update: {}"

# Actual replacement (after approval)
find docs/ README.md -type f -exec grep -l "jgtolentino/odoo" {} \; | \
  xargs -I{} sed -i '' 's|jgtolentino/odoo|Insightpulseai/odoo|g' {}
```

**Validation:**
```bash
# Verify no old references remain (excluding git history)
grep -r "jgtolentino/odoo" docs/ README.md | grep -v ".git"
```

**Files to Update (Sample):**
- [ ] `docs/ODOO_ADDONS_PATH_CONFIGURATION.md`
- [ ] `docs/DOCKER_VALIDATION_GUIDE.md`
- [ ] `docs/REPOSITORY_STRUCTURE.md`
- [ ] `docs/pages/runbooks.md`
- [ ] `README.md`

### Phase 3: CLI-Only Patterns (NEW CONTENT)

**Files to Create/Update:**
- [ ] `docs/pages/runbooks.md` - Add "CLI-Only Database Operations" section
- [ ] `docs/pages/production-validation.md` - Create new validation checklist
- [ ] `README.md` - Add "Production Deployment Validation" section

### Phase 4: Production Endpoints Documentation (NEW CONTENT)

**Files to Create:**
- [ ] `docs/architecture/production-endpoints.md` - Canonical SSOT

---

## Testing Strategy

### Documentation Validation

**Link Checking:**
```bash
# Check for broken internal links
find docs/ -name "*.md" -exec grep -oP '\[.*?\]\(\K[^)]+' {} \; | \
  grep -v "^http" | \
  while read link; do
    [[ -f "$link" ]] || echo "Broken link: $link"
  done
```

**Placeholder Detection:**
```bash
# Ensure no TODOs/placeholders in production docs
grep -r "TODO\|FIXME\|PLACEHOLDER" docs/pages/ docs/architecture/
```

**Command Validation:**
```bash
# Test all bash commands in runbooks (dry-run mode)
shellcheck docs/pages/runbooks.md || true
```

---

## Rollback Strategy

**Safe Rollback:**
```bash
# Revert documentation changes
git checkout HEAD -- docs/pages/runbooks.md
git checkout HEAD -- docs/architecture/production-endpoints.md
git checkout HEAD -- README.md
```

**Risk Assessment:**
- **LOW RISK:** Documentation-only changes, no code execution
- **Reversible:** Git history preserves all previous versions
- **No Downtime:** Documentation changes don't affect production services

---

## Success Criteria

- [ ] All `<PRODUCTION_IP>` placeholders replaced with `178.128.112.214`
- [ ] All `jgtolentino/odoo` references updated to `Insightpulseai/odoo`
- [ ] CLI-only deployment patterns documented in runbooks
- [ ] Production validation checklist created and tested
- [ ] Production endpoints canonical documentation created
- [ ] README enhanced with deployment validation section
- [ ] No broken internal links
- [ ] No TODO/FIXME/PLACEHOLDER in production docs

---

## Future Enhancements (Out of Scope)

- **Automated Link Checking:** CI workflow for broken link detection
- **Documentation Testing:** Validate command examples in CI
- **Versioned Documentation:** Historical documentation for previous deployments
- **MkDocs Enhancement:** Visual diagrams for infrastructure topology
- **Runbook Automation:** Convert runbooks to executable scripts

---

## References

- Gate Contract: `docs/architecture/gate-contract-v2.md`
- Existing Runbooks: `docs/pages/runbooks.md`
- Deployment Timeline: `docs/pages/deployment-timeline.md`
- Production Runtime: `docs/architecture/PROD_RUNTIME_SNAPSHOT.md`

---

**Status:** Design specification complete. Implementation ready.
**Priority:** MEDIUM (improves operational clarity, enables automation)
**Effort:** 4-6 hours (search-replace + new documentation + validation)
