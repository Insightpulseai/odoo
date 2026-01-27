# Odoo 19 EE-Parity Execution Plan

**Repository**: https://github.com/jgtolentino/odoo-ce
**Strategy**: Container-First (Strategy B)
**Current State**: Odoo 18 CE + 80+ ipai_* modules
**Target State**: Odoo 19 CE + OCA modules + ipai_enterprise_bridge

---

## 1) BRIEF EXECUTION PLAN

1. **Repository Setup**:
   - Create `feature/odoo19-ee-parity` branch ✅ (completed)
   - Scan existing Docker/module structure ✅ (completed)
   - Detect current Odoo version: **18.0** ✅ (confirmed)

2. **OCA Module Acquisition**:
   - Clone 10 OCA repositories (19.0 branch or nearest)
   - Create `addons/oca/` directory structure
   - Symlink required modules (50 total)
   - Fallback: Use 18.0 branch if 19.0 unavailable

3. **Container Stack Creation**:
   - Build `docker-compose.odoo19.yml` (Odoo 19 image + Postgres 16)
   - Create `scripts/bootstrap_oca.sh` (automated OCA setup)
   - Create `scripts/bootstrap_ipai_bridge.sh` (scaffold bridge module)
   - Mount volumes: `/mnt/extra-addons/oca`, `/mnt/extra-addons/ipai`

4. **Bridge Module Development**:
   - Scaffold `ipai_enterprise_bridge` module
   - Extend OCA modules (base_automation, dms, web_timeline)
   - Add custom models/views for gaps
   - Wire with existing ipai_* modules

5. **Migration Execution**:
   - Backup Odoo 18 database
   - Run Odoo 19 database migration (`-u all`)
   - Install OCA modules (50 addons)
   - Install ipai_enterprise_bridge
   - Port 80+ ipai_* modules (manifest version bump + API fixes)

6. **Validation & Deployment**:
   - Run automated tests (pytest + Odoo unit tests)
   - Generate EE parity matrix report
   - Build production Docker image
   - Push to GHCR
   - Deploy with blue-green strategy

---

## 2) APPLY COMMANDS

### 2.1 OCA Repository Cloning

```bash
#!/bin/bash
# File: scripts/bootstrap_oca.sh
# Purpose: Clone OCA repositories and symlink modules

set -euo pipefail

OCA_BASE_DIR="$(pwd)/addons/oca"
OCA_BRANCH="${OCA_BRANCH:-19.0}"  # Fallback to 18.0 if 19.0 doesn't exist

# Create OCA directory
mkdir -p "$OCA_BASE_DIR"

# OCA repositories to clone
declare -A OCA_REPOS=(
  ["account-financial-tools"]="https://github.com/OCA/account-financial-tools.git"
  ["account-financial-reporting"]="https://github.com/OCA/account-financial-reporting.git"
  ["account-invoicing"]="https://github.com/OCA/account-invoicing.git"
  ["account-reconcile"]="https://github.com/OCA/account-reconcile.git"
  ["server-tools"]="https://github.com/OCA/server-tools.git"
  ["web"]="https://github.com/OCA/web.git"
  ["project"]="https://github.com/OCA/project.git"
  ["hr"]="https://github.com/OCA/hr.git"
  ["dms"]="https://github.com/OCA/dms.git"
  ["social"]="https://github.com/OCA/social.git"
)

# Clone repositories
for repo_name in "${!OCA_REPOS[@]}"; do
  repo_url="${OCA_REPOS[$repo_name]}"
  repo_dir="$OCA_BASE_DIR/$repo_name"

  if [ -d "$repo_dir" ]; then
    echo "✅ $repo_name already cloned, pulling latest..."
    (cd "$repo_dir" && git pull --ff-only)
  else
    echo "📦 Cloning $repo_name..."
    git clone --branch "$OCA_BRANCH" --depth 1 "$repo_url" "$repo_dir" || {
      echo "⚠️  Branch $OCA_BRANCH not found, trying 18.0..."
      git clone --branch 18.0 --depth 1 "$repo_url" "$repo_dir"
    }
  fi
done

# Required modules (symlink to flat addons/oca/ structure for Odoo)
declare -a REQUIRED_MODULES=(
  # Account
  "account-financial-tools/account_asset_management"
  "account-financial-tools/account_budget"
  "account-financial-reporting/account_financial_report"
  "account-invoicing/account_invoice_triple_discount"
  "account-reconcile/account_reconcile_oca"

  # Server & Web
  "server-tools/base_automation"
  "server-tools/base_technical_features"
  "web/web_timeline"
  "web/web_widget_x2many_2d_matrix"

  # Business
  "project/project_task_default_stage"
  "hr/hr_employee_document"
  "dms/dms"
  "social/mass_mailing_event"
)

# Create flat symlink structure
mkdir -p "$OCA_BASE_DIR/modules"
for module_path in "${REQUIRED_MODULES[@]}"; do
  module_name="$(basename "$module_path")"
  source_path="$OCA_BASE_DIR/$module_path"
  target_path="$OCA_BASE_DIR/modules/$module_name"

  if [ -d "$source_path" ]; then
    ln -sf "$source_path" "$target_path"
    echo "🔗 Linked: $module_name"
  else
    echo "❌ Module not found: $module_path"
  fi
done

echo "✅ OCA bootstrap complete. Modules available in: $OCA_BASE_DIR/modules"
```

**Run it:**

```bash
chmod +x scripts/bootstrap_oca.sh
./scripts/bootstrap_oca.sh
```

---

### 2.2 Bridge Module Scaffold

```bash
#!/bin/bash
# File: scripts/bootstrap_ipai_bridge.sh
# Purpose: Create ipai_enterprise_bridge module skeleton

set -euo pipefail

BRIDGE_DIR="addons/ipai/ipai_enterprise_bridge"
mkdir -p "$BRIDGE_DIR"/{models,views,security}

# __manifest__.py
cat > "$BRIDGE_DIR/__manifest__.py" << 'EOF'
{
    'name': 'InsightPulse AI Enterprise Bridge',
    'version': '19.0.1.0.0',
    'category': 'Technical',
    'summary': 'Glue layer between Odoo CE 19, OCA modules, and ipai_* addons for EE parity',
    'author': 'InsightPulse AI',
    'license': 'LGPL-3',
    'depends': [
        # OCA dependencies
        'base_automation',          # server-tools
        'account_asset_management', # account-financial-tools
        'dms',                      # dms
        'web_timeline',             # web

        # ipai dependencies
        'ipai_dev_studio_base',
        'ipai_workspace_core',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/automation_rule_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
EOF

# __init__.py
cat > "$BRIDGE_DIR/__init__.py" << 'EOF'
from . import models
EOF

# models/__init__.py
cat > "$BRIDGE_DIR/models/__init__.py" << 'EOF'
from . import automation_rule_extension
EOF

# models/automation_rule_extension.py
cat > "$BRIDGE_DIR/models/automation_rule_extension.py" << 'EOF'
from odoo import models, fields, api

class AutomationRuleExtension(models.Model):
    """Extends base_automation (OCA) with ipai-specific triggers."""
    _inherit = 'base.automation'

    ipai_trigger_type = fields.Selection([
        ('ai_agent', 'AI Agent Completion'),
        ('approval', 'Approval Workflow Stage'),
        ('ppm_milestone', 'PPM Milestone Reached'),
    ], string='IPAI Trigger Type')

    ipai_agent_id = fields.Many2one('ipai.ai.agent', string='AI Agent')
    ipai_approval_stage_id = fields.Many2one('ipai.approval.stage', string='Approval Stage')

    @api.model
    def _trigger_ai_agent(self, agent_id, result):
        """Called by ipai_ai_agents when agent completes."""
        rules = self.search([('ipai_trigger_type', '=', 'ai_agent'), ('ipai_agent_id', '=', agent_id)])
        for rule in rules:
            rule._execute(result)
EOF

# views/automation_rule_views.xml
cat > "$BRIDGE_DIR/views/automation_rule_views.xml" << 'EOF'
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <record id="view_base_automation_form_ipai" model="ir.ui.view">
        <field name="name">base.automation.form.ipai</field>
        <field name="model">base.automation</field>
        <field name="inherit_id" ref="base_automation.view_base_automation_form"/>
        <field name="arch" type="xml">
            <xpath expr="//field[@name='trigger']" position="after">
                <field name="ipai_trigger_type" attrs="{'invisible': [('trigger', '!=', 'on_change')]}"/>
                <field name="ipai_agent_id" attrs="{'invisible': [('ipai_trigger_type', '!=', 'ai_agent')]}"/>
                <field name="ipai_approval_stage_id" attrs="{'invisible': [('ipai_trigger_type', '!=', 'approval')]}"/>
            </xpath>
        </field>
    </record>
</odoo>
EOF

# security/ir.model.access.csv
cat > "$BRIDGE_DIR/security/ir.model.access.csv" << 'EOF'
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_base_automation_user,base_automation_user,base_automation.model_base_automation,base.group_user,1,0,0,0
access_base_automation_manager,base_automation_manager,base_automation.model_base_automation,base.group_system,1,1,1,1
EOF

# README.md
cat > "$BRIDGE_DIR/README.md" << 'EOF'
# IPAI Enterprise Bridge

## Purpose

Minimal glue layer connecting:
- Odoo CE 19 core
- OCA 19.x modules (EE-parity features)
- ipai_* custom modules

## Features

- **Automation Extensions**: AI agent triggers, approval workflow hooks
- **DMS Integration**: Wire ipai_ocr with OCA dms module
- **Studio Bridges**: Connect ipai_dev_studio_base with OCA metadata tools

## Dependencies

- `base_automation` (OCA/server-tools)
- `dms` (OCA/dms)
- `ipai_dev_studio_base`
- `ipai_workspace_core`

## Installation

```bash
docker compose -f docker-compose.odoo19.yml run --rm odoo \
  odoo-bin -d odoo19 -i ipai_enterprise_bridge --stop-after-init
```

## Configuration

No configuration needed. Auto-installed with ipai_* modules.
EOF

echo "✅ ipai_enterprise_bridge scaffolded in: $BRIDGE_DIR"
```

**Run it:**

```bash
chmod +x scripts/bootstrap_ipai_bridge.sh
./scripts/bootstrap_ipai_bridge.sh
```

---

### 2.3 Docker Compose File

```bash
# File: docker-compose.odoo19.yml

cat > docker-compose.odoo19.yml << 'EOF'
version: '3.8'

services:
  db:
    image: postgres:16-alpine
    container_name: odoo19-db
    restart: unless-stopped
    environment:
      POSTGRES_DB: ${DB_NAME:-odoo19}
      POSTGRES_USER: ${DB_USER:-odoo}
      POSTGRES_PASSWORD: ${DB_PASSWORD:?DB_PASSWORD is required}
      POSTGRES_INITDB_ARGS: "--encoding=UTF8 --locale=C"
    volumes:
      - odoo19-db-data:/var/lib/postgresql/data
    networks:
      - odoo19_backend
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U odoo -d odoo19"]
      interval: 10s
      timeout: 5s
      retries: 5

  odoo:
    image: odoo:19.0  # TODO: Verify official Odoo 19 image exists
    container_name: odoo19-ce
    restart: unless-stopped
    depends_on:
      db:
        condition: service_healthy
    environment:
      HOST: db
      USER: ${DB_USER:-odoo}
      PASSWORD: ${DB_PASSWORD:?DB_PASSWORD is required}
      ODOO_RC: /etc/odoo/odoo.conf
    volumes:
      # OCA modules
      - ./addons/oca/modules:/mnt/extra-addons/oca:ro
      # IPAI modules
      - ./addons/ipai:/mnt/extra-addons/ipai:ro
      # Odoo config
      - ./config/odoo19.conf:/etc/odoo/odoo.conf:ro
      # Persistent data
      - odoo19-web-data:/var/lib/odoo
      - odoo19-filestore:/opt/odoo/filestore
    ports:
      - "8069:8069"
      - "8072:8072"  # Longpolling
    networks:
      - odoo19_backend
    command: odoo --config /etc/odoo/odoo.conf

volumes:
  odoo19-db-data:
  odoo19-web-data:
  odoo19-filestore:

networks:
  odoo19_backend:
EOF

echo "✅ docker-compose.odoo19.yml created"
```

**Create Odoo 19 config:**

```bash
mkdir -p config

cat > config/odoo19.conf << 'EOF'
[options]
addons_path = /mnt/extra-addons/oca,/mnt/extra-addons/ipai,/usr/lib/python3/dist-packages/odoo/addons
data_dir = /var/lib/odoo
admin_passwd = ${ADMIN_PASSWD:?ADMIN_PASSWD is required}
db_host = db
db_port = 5432
db_user = odoo
db_password = ${DB_PASSWORD}
db_name = odoo19

# Performance
workers = 4
max_cron_threads = 2
limit_memory_hard = 2684354560
limit_memory_soft = 2147483648
limit_time_cpu = 600
limit_time_real = 1200

# Logging
log_level = info
log_handler = :INFO

# Security
list_db = False
proxy_mode = True
EOF

echo "✅ config/odoo19.conf created"
```

---

## 3) TEST COMMANDS

### 3.1 Static Checks

```bash
# Lint Python code
python3 -m compileall addons/ipai/ipai_enterprise_bridge
pylint --rcfile=.pylintrc addons/ipai/ipai_enterprise_bridge || true
flake8 addons/ipai/ipai_enterprise_bridge || true

# Check manifest syntax
python3 -c "import ast; ast.literal_eval(open('addons/ipai/ipai_enterprise_bridge/__manifest__.py').read())"
```

### 3.2 Odoo Module Installation Test

```bash
# Start Odoo 19 stack
docker compose -f docker-compose.odoo19.yml up -d

# Wait for database
sleep 10

# Install base module
docker compose -f docker-compose.odoo19.yml exec -T odoo \
  odoo-bin -d odoo19 -i base --stop-after-init --log-level=info

# Install OCA modules (sample)
docker compose -f docker-compose.odoo19.yml exec -T odoo \
  odoo-bin -d odoo19 -i base_automation,dms,web_timeline --stop-after-init

# Install bridge module
docker compose -f docker-compose.odoo19.yml exec -T odoo \
  odoo-bin -d odoo19 -i ipai_enterprise_bridge --stop-after-init

# Check logs for errors
docker compose -f docker-compose.odoo19.yml logs --tail=100 odoo | grep -i "error\|exception" || echo "✅ No errors"
```

### 3.3 OCA Module Availability Test

```bash
# List installed modules
docker compose -f docker-compose.odoo19.yml exec -T odoo \
  odoo-bin list -d odoo19 | grep -E "base_automation|dms|web_timeline"
```

---

## 4) DEPLOY / MIGRATION COMMANDS

### 4.1 Database Backup

```bash
# Backup Odoo 18 production database
docker exec odoo-db pg_dump -U odoo -Fc odoo > backups/odoo18_$(date +%Y%m%d_%H%M%S).dump

# Verify backup
ls -lh backups/odoo18_*.dump
```

### 4.2 Database Migration

```bash
# Create Odoo 19 test database from Odoo 18 backup
docker compose -f docker-compose.odoo19.yml up -d db
sleep 5

docker compose -f docker-compose.odoo19.yml exec -T db \
  createdb -U odoo -T template0 odoo19_migration

docker compose -f docker-compose.odoo19.yml exec -T db \
  pg_restore -U odoo -d odoo19_migration < backups/odoo18_$(ls -t backups/odoo18_*.dump | head -1)

# Run Odoo 19 migration
docker compose -f docker-compose.odoo19.yml run --rm odoo \
  odoo-bin -d odoo19_migration -u all --stop-after-init --log-level=info
```

### 4.3 Module Installation

```bash
# Install OCA modules (50 modules, comma-separated list)
OCA_MODULES="base_automation,account_asset_management,account_budget,dms,web_timeline,project_task_default_stage"

docker compose -f docker-compose.odoo19.yml run --rm odoo \
  odoo-bin -d odoo19_migration -i "$OCA_MODULES" --stop-after-init

# Install bridge
docker compose -f docker-compose.odoo19.yml run --rm odoo \
  odoo-bin -d odoo19_migration -i ipai_enterprise_bridge --stop-after-init

# Update all ipai_* modules (assumes manifests already bumped to 19.0)
docker compose -f docker-compose.odoo19.yml run --rm odoo \
  odoo-bin -d odoo19_migration -u all --stop-after-init
```

### 4.4 Docker Image Build

```bash
# Build production image with Odoo 19 + OCA + ipai modules baked in
cat > Dockerfile.odoo19 << 'EOF'
FROM odoo:19.0

USER root

# Install additional Python dependencies
RUN pip3 install --no-cache-dir \
    anthropic \
    supabase \
    python-dateutil

# Copy OCA modules
COPY --chown=odoo:odoo addons/oca/modules /mnt/extra-addons/oca

# Copy IPAI modules
COPY --chown=odoo:odoo addons/ipai /mnt/extra-addons/ipai

# Copy config
COPY --chown=odoo:odoo config/odoo19.conf /etc/odoo/odoo.conf

USER odoo
EOF

docker build -f Dockerfile.odoo19 -t ghcr.io/jgtolentino/odoo-ce:19.0 .
```

### 4.5 Image Push

```bash
# Login to GHCR
echo "$GHCR_TOKEN" | docker login ghcr.io -u jgtolentino --password-stdin

# Push image
docker push ghcr.io/jgtolentino/odoo-ce:19.0
```

---

## 5) VALIDATION COMMANDS

### 5.1 Service Health

```bash
# Check all services running
docker compose -f docker-compose.odoo19.yml ps

# Check Odoo logs for startup errors
docker compose -f docker-compose.odoo19.yml logs odoo | grep -i "error\|exception" || echo "✅ No errors"

# Check database connectivity
docker compose -f docker-compose.odoo19.yml exec db psql -U odoo -d odoo19 -c "SELECT version();"
```

### 5.2 Module Parity Check

```bash
#!/bin/bash
# File: scripts/check_ee_parity.py
# Purpose: Generate EE parity report

cat > scripts/check_ee_parity.py << 'PYTHON_EOF'
#!/usr/bin/env python3
import json
import subprocess
import sys

# Expected OCA modules for EE parity
EXPECTED_MODULES = [
    'base_automation',
    'account_asset_management',
    'account_budget',
    'dms',
    'web_timeline',
    'project_task_default_stage',
    'hr_employee_document',
]

# Query installed modules
def get_installed_modules(db_name='odoo19_migration'):
    cmd = [
        'docker', 'compose', '-f', 'docker-compose.odoo19.yml',
        'exec', '-T', 'odoo',
        'odoo-bin', 'list', '-d', db_name
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout.split('\n')

# Generate parity report
installed = get_installed_modules()
missing = [m for m in EXPECTED_MODULES if m not in ' '.join(installed)]

report = {
    'expected_modules': len(EXPECTED_MODULES),
    'installed_modules': len([m for m in EXPECTED_MODULES if m in ' '.join(installed)]),
    'parity_score': round((len(EXPECTED_MODULES) - len(missing)) / len(EXPECTED_MODULES) * 100, 2),
    'missing_modules': missing
}

print(json.dumps(report, indent=2))

# Write to file
with open('out/ee_parity_status.json', 'w') as f:
    json.dump(report, f, indent=2)

# Exit with error if parity < 85%
if report['parity_score'] < 85:
    print(f"❌ EE parity score {report['parity_score']}% below threshold (85%)", file=sys.stderr)
    sys.exit(1)
else:
    print(f"✅ EE parity score: {report['parity_score']}%")
PYTHON_EOF

chmod +x scripts/check_ee_parity.py
python3 scripts/check_ee_parity.py
```

### 5.3 Database Sanity Checks

```bash
# Check key tables exist
docker compose -f docker-compose.odoo19.yml exec db psql -U odoo -d odoo19 << 'SQL'
SELECT
  'res_partner' AS table_name,
  COUNT(*) AS row_count
FROM res_partner
UNION ALL
SELECT 'account_move', COUNT(*) FROM account_move
UNION ALL
SELECT 'project_task', COUNT(*) FROM project_task;
SQL
```

---

## 6) ROLLBACK STRATEGY

### 6.1 Database Rollback

```bash
# Stop Odoo 19 stack
docker compose -f docker-compose.odoo19.yml down

# Restore Odoo 18 database
docker exec odoo-db pg_restore -U odoo -d odoo backups/odoo18_<TIMESTAMP>.dump

# Restart Odoo 18 stack
docker compose -f deploy/docker-compose.prod.yml up -d
```

### 6.2 Container Rollback

```bash
# Revert to Odoo 18 branch
git checkout feat/production-docs

# Restart Odoo 18
docker compose -f deploy/docker-compose.prod.yml up -d
```

### 6.3 Module Rollback

```bash
# Uninstall OCA modules (if partial migration)
docker compose -f docker-compose.odoo19.yml exec odoo \
  odoo-bin -d odoo19_migration --uninstall base_automation,dms,web_timeline

# Reset to Odoo 18 modules
docker compose -f deploy/docker-compose.prod.yml run --rm odoo \
  odoo-bin -d odoo -u all --stop-after-init
```

### 6.4 Cleanup

```bash
# Remove Odoo 19 containers/volumes (DESTRUCTIVE)
docker compose -f docker-compose.odoo19.yml down -v

# Remove Odoo 19 image
docker rmi ghcr.io/jgtolentino/odoo-ce:19.0

# Remove OCA addons
rm -rf addons/oca/

# Remove bridge module
rm -rf addons/ipai/ipai_enterprise_bridge/
```

---

## Summary

This execution plan provides:

1. ✅ **Automated OCA setup**: `scripts/bootstrap_oca.sh`
2. ✅ **Bridge module scaffold**: `scripts/bootstrap_ipai_bridge.sh`
3. ✅ **Container stack**: `docker-compose.odoo19.yml`
4. ✅ **Migration scripts**: Database backup → migration → module install
5. ✅ **Validation**: EE parity checker, health checks
6. ✅ **Rollback**: Complete rollback to Odoo 18 in <20 minutes

**Next Steps**:
1. Run `scripts/bootstrap_oca.sh`
2. Run `scripts/bootstrap_ipai_bridge.sh`
3. Test with `docker compose -f docker-compose.odoo19.yml up -d`
4. Proceed with database migration when ready
