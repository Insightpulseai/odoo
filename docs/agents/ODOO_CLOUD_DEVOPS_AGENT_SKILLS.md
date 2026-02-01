# Odoo Cloud DevOps Agent Skills

**Last Updated**: 2026-01-28
**Purpose**: Capability matrix for AI agents managing Odoo.sh-class and Cloudpepper-class hosting
**Scope**: Self-hosted Odoo CE 18 on DigitalOcean with open-stack parity

---

## 1. Core Capabilities

### 1.1. Infrastructure as Code (IaC)

**Knowledge Required**:
- Docker Compose for service orchestration
- Nginx for reverse proxy and virtual host configuration
- PostgreSQL 16 for database management
- Let's Encrypt/Certbot for TLS certificate automation
- UFW for firewall configuration

**Skills**:
- Read and write `docker-compose.yml` files
- Generate nginx configuration for virtual hosts
- Create systemd services for Docker Compose
- Configure automated certificate renewal
- Apply firewall rules for production security

**Example Operations**:
```bash
# Deploy new service to stack
docker compose up -d new-service

# Update nginx configuration
cp deploy/nginx/erp.insightpulseai.com.conf /etc/nginx/conf.d/
nginx -t && systemctl reload nginx

# Renew TLS certificates
certbot renew --nginx --non-interactive
```

---

### 1.2. Git-Based Deployment

**Knowledge Required**:
- Git workflows (feature branches, main, tags)
- Semantic versioning for releases
- Git hooks for pre-deploy validation
- Rollback strategies using git tags

**Skills**:
- Pull latest changes from main branch
- Create deployment tags (v18.0.1.0.0)
- Rollback to previous tag on failure
- Manage git remotes (origin for GitHub, odoo-server for production)

**Example Operations**:
```bash
# Deploy latest changes
cd /opt/odoo-ce/repo
git pull origin main
docker compose restart odoo

# Tag and deploy release
git tag -a v18.0.1.0.0 -m "Release: Finance PPM + BIR compliance"
git push origin v18.0.1.0.0

# Rollback to previous version
git checkout v18.0.0.9.0
docker compose restart odoo
```

---

### 1.3. Database Management

**Knowledge Required**:
- PostgreSQL administration (pg_dump, pg_restore)
- Odoo database operations (module install/upgrade)
- PII scrubbing for staging environments
- WAL archiving for point-in-time recovery

**Skills**:
- Backup databases to DigitalOcean Spaces
- Restore databases from backups
- Sanitize production data for staging
- Execute Odoo module upgrades via CLI

**Example Operations**:
```bash
# Backup production database
docker compose exec postgres pg_dump -U odoo -d odoo > /opt/odoo-ce/backups/daily/odoo_$(date +%Y%m%d).sql

# Restore to staging (with PII scrubbing)
./scripts/deploy/scrub_pii.py < odoo_prod.sql > odoo_staging.sql
docker compose exec postgres psql -U odoo -d odoo_staging < odoo_staging.sql

# Upgrade modules
docker compose exec odoo odoo -d odoo -u ipai_finance_ppm --stop-after-init
```

---

### 1.4. Module Deployment

**Knowledge Required**:
- Odoo module structure (`__manifest__.py`, models/, views/)
- OCA conventions and compliance requirements
- Module dependencies and installation order
- Hot-reload mechanisms for development

**Skills**:
- Deploy custom `ipai_*` modules to production
- Install/upgrade OCA dependencies
- Validate module manifests for syntax errors
- Restart Odoo with new modules

**Example Operations**:
```bash
# Deploy new module
cp -r addons/ipai/ipai_new_module /opt/odoo-ce/data/addons/
docker compose exec odoo odoo -d odoo -i ipai_new_module --stop-after-init
docker compose restart odoo

# Upgrade existing module
docker compose exec odoo odoo -d odoo -u ipai_finance_ppm --stop-after-init
```

---

### 1.5. Monitoring & Observability

**Knowledge Required**:
- Health check endpoints (`/web/health`)
- Log aggregation patterns (Docker logs, nginx logs)
- Metrics collection (PostgreSQL stats, Odoo performance)
- Alert routing (n8n workflows → Mattermost)

**Skills**:
- Configure health check monitoring
- Query Docker logs for error detection
- Create Grafana dashboards for Odoo metrics
- Set up alert thresholds and notification workflows

**Example Operations**:
```bash
# Check service health
curl -f https://erp.insightpulseai.com/web/health || echo "Health check failed"

# View Odoo logs
docker compose logs -f --tail=100 odoo

# PostgreSQL connection monitoring
docker compose exec postgres psql -U odoo -c "SELECT count(*) FROM pg_stat_activity;"

# Check disk usage
df -h | grep /opt/odoo-ce
```

---

## 2. Advanced Capabilities

### 2.1. Preview Environments (Ephemeral Instances)

**Knowledge Required**:
- Dynamic subdomain routing (`pr-123.dev.insightpulseai.com`)
- Docker Compose templating for per-PR stacks
- TTL-based cleanup mechanisms
- GitHub Actions integration

**Skills**:
- Generate unique docker-compose configs per PR
- Create DNS records via DigitalOcean API
- Deploy ephemeral Odoo instances
- Automate teardown after PR merge

**Example Workflow**:
```yaml
# .github/workflows/preview-env-deploy.yml
name: Deploy Preview Environment
on:
  pull_request:
    types: [opened, synchronize]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Deploy to preview
        run: |
          export PR_NUM=${{ github.event.pull_request.number }}
          ./scripts/deploy/create_preview_env.sh $PR_NUM
      - name: Comment PR
        run: |
          gh pr comment $PR_NUM --body "Preview: https://pr-$PR_NUM.dev.insightpulseai.com"
```

---

### 2.2. Staging Restore with PII Scrubbing

**Knowledge Required**:
- Data anonymization techniques (faker library)
- Odoo data model (res.partner, hr.employee)
- SQL pattern matching for sensitive fields
- Verification strategies for scrubbing completeness

**Skills**:
- Export production database
- Identify and anonymize PII fields
- Validate anonymization results
- Import to staging environment

**Example Script**:
```python
# scripts/deploy/scrub_pii.py
import re
from faker import Faker

fake = Faker()

def scrub_email(email):
    """Replace real email with fake"""
    if '@' in email:
        return fake.email()
    return email

def scrub_phone(phone):
    """Replace real phone with fake"""
    if phone and len(phone) >= 10:
        return fake.phone_number()
    return phone

# Apply to SQL dump
def scrub_sql_dump(input_sql, output_sql):
    with open(input_sql) as f, open(output_sql, 'w') as out:
        for line in f:
            # Scrub emails
            line = re.sub(r'[\w.-]+@[\w.-]+', lambda m: scrub_email(m.group()), line)
            # Scrub phones
            line = re.sub(r'\+?\d{10,}', lambda m: scrub_phone(m.group()), line)
            out.write(line)
```

---

### 2.3. Automated Backup Verification

**Knowledge Required**:
- Backup restoration testing patterns
- Smoke test strategies for restored databases
- Mattermost webhook integration for alerts
- Cron scheduling for automated jobs

**Skills**:
- Restore backup to temporary database
- Run smoke tests on restored data
- Alert on restoration failures
- Clean up temporary databases

**Example Script**:
```bash
# scripts/deploy/test_backup_restore.sh
#!/bin/bash
set -e

BACKUP_FILE="/opt/odoo-ce/backups/daily/odoo_$(date +%Y%m%d).sql"
TEST_DB="odoo_restore_test_$(date +%s)"

# Restore to temporary database
docker compose exec postgres createdb -U odoo $TEST_DB
docker compose exec postgres psql -U odoo -d $TEST_DB < $BACKUP_FILE

# Smoke test: check table counts
TABLE_COUNT=$(docker compose exec postgres psql -U odoo -d $TEST_DB -t -c "SELECT count(*) FROM information_schema.tables WHERE table_schema='public';")

if [ "$TABLE_COUNT" -lt 100 ]; then
    echo "❌ Backup restore failed: only $TABLE_COUNT tables found"
    curl -X POST "$MATTERMOST_WEBHOOK_URL" -d '{"text":"⚠️ Backup restore test failed"}'
    exit 1
fi

# Cleanup
docker compose exec postgres dropdb -U odoo $TEST_DB

echo "✅ Backup restore test passed: $TABLE_COUNT tables"
```

---

### 2.4. DNS Automation

**Knowledge Required**:
- DigitalOcean DNS API
- Let's Encrypt DNS-01 challenge
- Dynamic subdomain creation
- TTL management

**Skills**:
- Create A/CNAME records via API
- Configure TLS certificates for new subdomains
- Update nginx configurations for new hosts
- Clean up DNS records after environment teardown

**Example Script**:
```bash
# scripts/deploy/create_dns_record.sh
#!/bin/bash
set -e

SUBDOMAIN=$1
DROPLET_IP="178.128.112.214"
DOMAIN="insightpulseai.com"

# Create A record via DigitalOcean API
curl -X POST "https://api.digitalocean.com/v2/domains/$DOMAIN/records" \
  -H "Authorization: Bearer $DO_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"type\":\"A\",\"name\":\"$SUBDOMAIN\",\"data\":\"$DROPLET_IP\",\"ttl\":300}"

# Wait for DNS propagation
sleep 60

# Request TLS certificate
certbot certonly --nginx -d "$SUBDOMAIN.$DOMAIN" --non-interactive --agree-tos

echo "✅ DNS record created: $SUBDOMAIN.$DOMAIN → $DROPLET_IP"
```

---

### 2.5. Performance Monitoring

**Knowledge Required**:
- Odoo performance metrics (request latency, database query time)
- PostgreSQL query analysis (EXPLAIN, pg_stat_statements)
- Nginx access log analysis
- Grafana dashboard creation

**Skills**:
- Enable PostgreSQL slow query logging
- Analyze Odoo RPC call performance
- Create Grafana dashboards for KPIs
- Set alert thresholds for performance degradation

**Example Queries**:
```sql
-- Top 10 slowest queries (requires pg_stat_statements)
SELECT
    query,
    mean_exec_time,
    calls
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 10;

-- Active connections
SELECT
    datname,
    count(*) as connections
FROM pg_stat_activity
GROUP BY datname;

-- Table sizes
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
LIMIT 20;
```

---

## 3. Security & Compliance

### 3.1. Secret Management

**Knowledge Required**:
- Environment variable patterns (.env files)
- Supabase Vault for sensitive configuration
- Git-ignored file patterns
- Secret rotation strategies

**Skills**:
- Store secrets in `.env` files (git-ignored)
- Retrieve secrets from Supabase Vault
- Rotate database passwords
- Validate secret references in code

---

### 3.2. Firewall Configuration

**Knowledge Required**:
- UFW (Uncomplicated Firewall) rules
- Port exposure strategy (22, 80, 443 only)
- Rate limiting for SSH
- DDoS mitigation via DigitalOcean

**Skills**:
- Configure UFW rules for production
- Enable rate limiting on SSH
- Monitor firewall logs for intrusion attempts
- Block malicious IPs

**Example Configuration**:
```bash
# Enable firewall
ufw default deny incoming
ufw default allow outgoing

# Allow SSH (rate limited)
ufw limit 22/tcp

# Allow HTTP/HTTPS
ufw allow 80/tcp
ufw allow 443/tcp

# Enable
ufw enable
```

---

### 3.3. TLS Certificate Management

**Knowledge Required**:
- Let's Encrypt/Certbot
- Certificate renewal automation
- CAA DNS records
- HTTPS enforcement

**Skills**:
- Request certificates for new domains
- Automate renewal via cron
- Validate certificate expiration
- Configure nginx for HTTPS-only

---

## 4. Odoo-Specific Skills

### 4.1. Module Development

**Knowledge Required**:
- Odoo 18 module structure
- OCA conventions (`__manifest__.py` fields)
- QWeb template inheritance
- Model/view/security patterns

**Skills**:
- Scaffold new `ipai_*` modules
- Create OCA-compliant manifests
- Write QWeb view inheritance
- Define access rights in `ir.model.access.csv`

---

### 4.2. BIR Compliance (Philippines)

**Knowledge Required**:
- BIR form requirements (1601-C, 2550Q, 2316)
- Philippine tax calculation rules (TRAIN Law)
- SSS/PhilHealth/Pag-IBIG contribution tables
- Alphalist export formats

**Skills**:
- Generate BIR 1601-C reports
- Calculate withholding taxes
- Export Alphalist CSV
- Validate BIR form accuracy

---

### 4.3. Finance PPM Workflows

**Knowledge Required**:
- Logical framework (Goal → Outcome → IM → Outputs → Activities)
- Month-end close procedures
- BIR deadline tracking
- Task automation via `ir.cron`

**Skills**:
- Create logframe records
- Auto-generate month-end close tasks
- Schedule BIR deadline alerts
- Monitor completion percentages

---

## 5. Integration Skills

### 5.1. n8n Workflow Orchestration

**Knowledge Required**:
- n8n workflow JSON structure
- Webhook triggers
- HTTP request nodes
- Mattermost notification nodes

**Skills**:
- Create n8n workflows for automation
- Configure webhook endpoints
- Integrate with Odoo XML-RPC
- Send Mattermost alerts

---

### 5.2. Mattermost ChatOps

**Knowledge Required**:
- Mattermost webhook format
- Interactive message buttons
- Slash command integration
- Bot user configuration

**Skills**:
- Send alerts to Mattermost channels
- Create approval workflows with buttons
- Configure Mattermost bot users
- Integrate with n8n for bidirectional communication

---

### 5.3. Apache Superset BI

**Knowledge Required**:
- Superset dataset configuration
- SQL Lab query interface
- Dashboard creation
- Chart types (ECharts)

**Skills**:
- Create Superset datasets from PostgreSQL
- Build dashboards for finance KPIs
- Configure row-level security
- Embed dashboards in Odoo

---

## 6. Operational Runbooks

### 6.1. Production Deployment

**Checklist**:
1. ✅ Backup database
2. ✅ Pull latest changes from main
3. ✅ Run module upgrades (`--stop-after-init`)
4. ✅ Restart Odoo service
5. ✅ Verify health check
6. ✅ Monitor logs for errors (5 minutes)
7. ✅ Rollback if smoke tests fail

---

### 6.2. Database Restore

**Checklist**:
1. ✅ Identify backup file (daily/weekly/monthly)
2. ✅ Stop Odoo service
3. ✅ Drop existing database (if restoring to same name)
4. ✅ Create new database
5. ✅ Restore from backup file
6. ✅ Start Odoo service
7. ✅ Run smoke tests

---

### 6.3. Module Upgrade

**Checklist**:
1. ✅ Backup database
2. ✅ Stop Odoo service
3. ✅ Update module code
4. ✅ Run upgrade command (`-u <module_name>`)
5. ✅ Start Odoo service
6. ✅ Verify module functionality
7. ✅ Rollback if upgrade fails

---

## 7. Documentation References

- **Canonical DNS**: `docs/infra/CANONICAL_DNS_INSIGHTPULSEAI.md`
- **Odoo Pack**: `docs/infra/CANONICAL_ODOO_PACK.md`
- **Odoo.sh Parity**: `docs/parity/odoo_sh/ODOO_SH_FEATURES_MAP.md`
- **Parity Backlog**: `docs/parity/odoo_sh/PARITY_BACKLOG.md`
- **OCA Conventions**: https://github.com/OCA/odoo-community.org
- **Odoo 18 Docs**: https://www.odoo.com/documentation/18.0/
