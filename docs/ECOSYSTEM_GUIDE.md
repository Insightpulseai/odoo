# Odoo CE Ecosystem Guide for AI Agents

**Production Server**: 159.223.75.148 (odoo-erp-prod)
**Primary Domain**: https://erp.insightpulseai.com
**Last Updated**: 2025-12-17

---

## 🎯 Quick Navigation

### For AI Agents: How to Interact with This System

**Q: I need to query the Odoo database**
→ Use: `ssh root@159.223.75.148 "docker exec -i odoo-db psql -U odoo -d production -c \"YOUR_SQL\""`

**Q: I need to access Odoo via XML-RPC**
→ Use: `python3 scripts/YOUR_SCRIPT.py` (see `scripts/fix_home_to_dashboard.py` for example)
→ URL: `https://erp.insightpulseai.com/xmlrpc/2/common` (common) or `/xmlrpc/2/object` (object)

**Q: I need to install/upgrade an Odoo module**
→ Use: `ssh root@159.223.75.148 "docker exec odoo-ce /usr/bin/odoo -c /etc/odoo/odoo.conf -d production --init MODULE_NAME --stop-after-init --http-port=8070"`

**Q: I need to check Odoo logs**
→ Use: `ssh root@159.223.75.148 "docker logs odoo-ce --tail=50"`

**Q: I need to restart Odoo**
→ Use: `ssh root@159.223.75.148 "docker restart odoo-ce"`

**Q: Where are the module files?**
→ Server: `/opt/odoo-ce/addons/ipai_*/`
→ Local: `addons/ipai_*/`

---

## 📦 Container Inventory

### Primary Odoo Stack

| Container | Image | Role | Database | Ports | Network |
|-----------|-------|------|----------|-------|---------|
| `odoo-ce` | odoo:18.0 | Main Odoo ERP | `production` (primary), `odoo` (test) | 127.0.0.1:8069→8069 | odoo-ce_odoo_network |
| `odoo-db` | postgres:16-alpine | Odoo PostgreSQL | `production`, `odoo` | 5432 (internal) | odoo-ce_odoo_network |

### Integration Services

| Container | Image | Role | Database | Ports | Network |
|-----------|-------|------|----------|-------|---------|
| `odoo-webhook-1` | odoo-webhook | Webhook processor | Uses `odoo-db` | 8101 (internal) | odoo_app_network |
| `odoo-keycloak-1` | quay.io/keycloak/keycloak:24.0 | SSO/Auth | `odoo-keycloak-postgres-1` | 0.0.0.0:8080→8080 | odoo_insightpulse-network |
| `odoo-keycloak-redis-1` | redis:7-alpine | Keycloak cache | N/A | 127.0.0.1:6379→6379 | odoo_insightpulse-network |
| `odoo-keycloak-postgres-1` | postgres:15-alpine | Keycloak DB | `keycloak` | 5432 (internal) | odoo_insightpulse-network |

### Communication Services

| Container | Image | Role | Database | Ports | Network |
|-----------|-------|------|----------|-------|---------|
| `odoo-mattermost-1` | mattermost/mattermost-team-edition:latest | Team chat | `odoo-mattermost-postgres-1` | 0.0.0.0:8065→8065 | odoo_insightpulse-network |
| `odoo-mattermost-postgres-1` | postgres:15-alpine | Mattermost DB | `mattermost` | 5432 (internal) | odoo_insightpulse-network |

### Workflow Automation

| Container | Image | Role | Database | Ports | Network |
|-----------|-------|------|----------|-------|---------|
| `n8n-postgres-1` | postgres:15-alpine | n8n DB | `n8n` | 5432 (internal) | n8n_n8n |

### Supporting Services (Other Droplets)

| Service | Location | Role | Access |
|---------|----------|------|--------|
| PaddleOCR-VL | 188.166.237.231 (ocr-service-droplet) | OCR processing | https://ade-ocr-backend-*.ondigitalocean.app |
| n8n | 159.223.75.148 (odoo-erp-prod) | Workflow automation | https://ipa.insightpulseai.com |

---

## 🗄️ Database Mapping

### Odoo Main Database (`odoo-db` container)

| Database Name | Owner | Purpose | Access | Tables |
|---------------|-------|---------|--------|--------|
| `production` | odoo | **PRIMARY** - Live production data | All Odoo modules | ~500+ tables |
| `odoo` | odoo | Test/development database | Testing only | ~500+ tables |
| `postgres` | odoo | System database | PostgreSQL internal | N/A |

**Connection Details**:
- **Internal (Docker)**: `postgresql://odoo:PASSWORD@odoo-db:5432/production`
- **External (SSH Tunnel)**: `ssh root@159.223.75.148 "docker exec -i odoo-db psql -U odoo -d production"`

### Key Odoo Tables (production database)

**Core Tables**:
- `res_users` - User accounts
- `res_company` - Company settings
- `ir_module_module` - Installed modules
- `ir_config_parameter` - System parameters
- `ir_ui_menu` - Menu structure
- `ir_actions_act_window` - Window actions

**Finance Tables**:
- `hr_expense` - Expense records
- `ipai_cash_advance.cash_advance` - Cash advances
- `ipai_ocr_expense.ocr_expense_log` - OCR logs
- `ipai_finance.bir_schedule` - BIR filing schedule

**Project Tables**:
- `project_project` - Projects
- `project_task` - Tasks
- `project_milestone` - Milestones
- `project_task_checklist` - Checklists
- `ipai_ppm_monthly_close.ppm_monthly_close` - Month-end close schedules

**Equipment Tables**:
- `ipai_equipment.equipment` - Equipment catalog
- `ipai_equipment.booking` - Equipment bookings
- `ipai_equipment.incident` - Equipment incidents

**Document Tables**:
- `ipai_docs.doc` - Documents
- `ipai_docs.doc_tag` - Tags
- `ipai_workspace_core.workspace` - Workspaces

### External Databases

| Database | Container | Purpose | Access |
|----------|-----------|---------|--------|
| `keycloak` | odoo-keycloak-postgres-1 | SSO user data | Via Keycloak admin |
| `mattermost` | odoo-mattermost-postgres-1 | Chat messages | Via Mattermost admin |
| `n8n` | n8n-postgres-1 | Workflow definitions | Via n8n UI |

---

## 🌐 Proxy Paths & Routing

### Nginx/Traefik Proxy Configuration

**Primary Domain**: `erp.insightpulseai.com`

**Proxy Rules**:
```
https://erp.insightpulseai.com/* → odoo-ce:8069 (Odoo CE 18.0)
```

### Odoo URL Structure

**Authentication**:
- `https://erp.insightpulseai.com/web/login?db=production` - Login page
- `https://erp.insightpulseai.com/web/database/selector` - Database selector

**Main Application** (requires authentication):
- `https://erp.insightpulseai.com/odoo` - Apps Dashboard (icon grid)
- `https://erp.insightpulseai.com/odoo/apps` - Apps menu
- `https://erp.insightpulseai.com/web/webclient` - Full web client

**Custom Routes** (via `ipai_custom_routes` module):
- `https://erp.insightpulseai.com/odoo/discuss` → Discuss app
- `https://erp.insightpulseai.com/odoo/calendar` → Calendar app
- `https://erp.insightpulseai.com/odoo/project` → Project app
- `https://erp.insightpulseai.com/odoo/expenses` → Expenses app

**Model Access Patterns**:
```
https://erp.insightpulseai.com/odoo/MODEL_NAME                    # List view
https://erp.insightpulseai.com/odoo/MODEL_NAME/RECORD_ID          # Form view
https://erp.insightpulseai.com/odoo/apps/MODULE_ID/MODEL/RECORD_ID # Module detail
```

**Examples**:
- `https://erp.insightpulseai.com/odoo/res.users` - Users list
- `https://erp.insightpulseai.com/odoo/project.task` - Tasks list
- `https://erp.insightpulseai.com/odoo/hr.expense` - Expenses list
- `https://erp.insightpulseai.com/odoo/apps/118/ir.module.module/118` - ipai_custom_routes module detail

**API Endpoints**:
- `https://erp.insightpulseai.com/xmlrpc/2/common` - XML-RPC authentication
- `https://erp.insightpulseai.com/xmlrpc/2/object` - XML-RPC object operations
- `https://erp.insightpulseai.com/jsonrpc` - JSON-RPC API
- `https://erp.insightpulseai.com/ipai/finance/ppm` - Finance PPM dashboard
- `https://erp.insightpulseai.com/ipai/finance/ppm/api/*` - Finance PPM API

### Integration Service Endpoints

**Keycloak (SSO)**:
- `http://159.223.75.148:8080` - Keycloak admin console
- Internal: `http://odoo-keycloak-1:8080`

**Mattermost (Chat)**:
- `http://159.223.75.148:8065` - Mattermost web UI
- Internal: `http://odoo-mattermost-1:8065`

**n8n (Workflows)**:
- `https://ipa.insightpulseai.com` - n8n web UI
- Internal: Varies by n8n container setup

**OCR Service**:
- `https://ade-ocr-backend-*.ondigitalocean.app` - PaddleOCR-VL API
- POST `/ocr/extract` - Extract receipt data
- POST `/ocr/batch` - Batch processing

---

## 📂 Directory Structure (Simplified for AI Agents)

### Repository Root (`/Users/tbwa/Documents/GitHub/odoo-ce`)

```
odoo-ce/
├── addons/                          # Custom Odoo modules (MAIN WORK AREA)
│   ├── ipai_cash_advance/          # Cash advance management
│   ├── ipai_ce_branding/           # Custom branding
│   ├── ipai_ce_cleaner/            # UI cleanup
│   ├── ipai_clarity_ppm_parity/    # Clarity PPM integration ⭐
│   ├── ipai_custom_routes/         # Clean URL routes (NEW) ⭐
│   ├── ipai_default_home/          # Default home page (DEPRECATED)
│   ├── ipai_dev_studio_base/       # Development tools
│   ├── ipai_docs/                  # Document management
│   ├── ipai_docs_project/          # Project docs integration
│   ├── ipai_equipment/             # Asset/equipment tracking
│   ├── ipai_expense/               # Expense management
│   ├── ipai_finance_ppm/           # Finance PPM dashboard 🚧
│   ├── ipai_industry_accounting_firm/
│   ├── ipai_industry_marketing_agency/
│   ├── ipai_ocr_expense/           # OCR automation ⭐
│   ├── ipai_ppm_monthly_close/     # Month-end closing ⭐
│   └── ipai_workspace_core/        # Workspace base
│
├── docs/                            # Documentation
│   ├── SITEMAP.md                  # URL structure and navigation ⭐
│   ├── ECOSYSTEM_GUIDE.md          # This file ⭐
│   ├── ODOO_INTEGRATION.md         # Odoo + n8n + Mattermost
│   ├── N8N_WORKFLOWS.md            # n8n workflow patterns
│   └── MONITORING.md               # Performance monitoring
│
├── scripts/                         # Automation scripts
│   ├── cleanup_users_xmlrpc.py     # User management via XML-RPC
│   ├── fix_home_to_dashboard.py    # Fix user home page
│   ├── install_default_home.py     # Module installation
│   ├── fix_home_page.sql           # SQL fixes
│   └── smoke-odoo-api.sh           # API smoke tests
│
├── infra/                           # Infrastructure configs
│   ├── do/                         # DigitalOcean specs
│   └── docker/                     # Docker configs
│
├── spec.md                          # Auto-generated repo tree
├── CLAUDE.md                        # Project orchestration rules ⭐
└── README.md                        # Project overview
```

### Server File Structure (`/opt/odoo-ce` on 159.223.75.148)

```
/opt/odoo-ce/
├── addons/                          # Same as repo (synced via git pull)
│   ├── ipai_*/                     # All InsightPulse modules
│   └── (mirrors local repo)
│
├── odoo/                            # Odoo core source (read-only)
│   ├── addons/                     # Standard Odoo modules
│   └── odoo/                       # Core framework
│
└── data/                            # Runtime data
    ├── filestore/                  # Uploaded files
    └── sessions/                   # Session data
```

### Container File Structure

**Odoo Container** (`odoo-ce`):
```
/opt/odoo-ce/addons/          # Custom modules
/usr/lib/python3/dist-packages/odoo/  # Odoo core
/etc/odoo/odoo.conf           # Configuration file
/var/log/odoo/                # Log files
```

**Database Container** (`odoo-db`):
```
/var/lib/postgresql/data/     # PostgreSQL data directory
```

---

## 🔧 Common Operations for AI Agents

### 1. Deploy Module Changes

```bash
# Local: Commit changes
git add addons/ipai_MODULE_NAME/
git commit -m "Description"
git push origin BRANCH_NAME

# Server: Pull and restart
ssh root@159.223.75.148 "cd /opt/odoo-ce && git pull origin BRANCH_NAME && docker restart odoo-ce"
```

### 2. Query Database

```bash
# Via SSH tunnel
ssh root@159.223.75.148 "docker exec -i odoo-db psql -U odoo -d production -c \"SELECT * FROM res_users WHERE login = 'admin';\""

# Interactive session
ssh root@159.223.75.148 "docker exec -it odoo-db psql -U odoo -d production"
```

### 3. Install/Upgrade Module

```bash
# Via CLI (preferred for automation)
ssh root@159.223.75.148 "docker exec odoo-ce /usr/bin/odoo -c /etc/odoo/odoo.conf -d production --init ipai_MODULE_NAME --stop-after-init --http-port=8070"

# Via XML-RPC (Python script)
python3 scripts/install_MODULE_NAME.py
```

### 4. Check Logs

```bash
# Odoo application logs
ssh root@159.223.75.148 "docker logs odoo-ce --tail=100"

# Follow logs in real-time
ssh root@159.223.75.148 "docker logs odoo-ce -f"

# PostgreSQL logs
ssh root@159.223.75.148 "docker logs odoo-db --tail=50"
```

### 5. Restart Services

```bash
# Restart Odoo only
ssh root@159.223.75.148 "docker restart odoo-ce"

# Restart database (USE WITH CAUTION)
ssh root@159.223.75.148 "docker restart odoo-db"

# Restart all Odoo-related containers
ssh root@159.223.75.148 "docker restart odoo-ce odoo-db odoo-webhook-1"
```

### 6. Update Module List

```bash
# Via XML-RPC
python3 -c "
import xmlrpc.client
common = xmlrpc.client.ServerProxy('https://erp.insightpulseai.com/xmlrpc/2/common')
uid = common.authenticate('production', 'admin', 'PASSWORD', {})
models = xmlrpc.client.ServerProxy('https://erp.insightpulseai.com/xmlrpc/2/object')
models.execute_kw('production', uid, 'PASSWORD', 'ir.module.module', 'update_list', [[]])
print('Module list updated')
"
```

---

## 🚨 Important Reminders for AI Agents

### DO ✅

- **Always use absolute paths**: `/opt/odoo-ce/addons/ipai_MODULE/`
- **Check database before SQL operations**: `docker exec -i odoo-db psql -U odoo -l`
- **Verify container is running**: `docker ps | grep odoo-ce`
- **Use production database**: `-d production` (not `odoo`)
- **Commit and push changes**: Always deploy via git
- **Restart Odoo after file changes**: `docker restart odoo-ce`
- **Check logs after operations**: `docker logs odoo-ce --tail=50`

### DON'T ❌

- **Don't use local Docker commands for production**: All production deployments via DigitalOcean or server Docker
- **Don't modify `odoo` database**: Use `production` database only
- **Don't hardcode passwords**: Use environment variables or prompt for input
- **Don't skip validation**: Always verify changes before claiming success
- **Don't assume XML-RPC endpoint**: Verify URL first (it may be /odoo/xmlrpc or /xmlrpc/2)
- **Don't use `tree` view mode**: Use `list` in Odoo 18 CE
- **Don't use `gantt` view in CE**: Gantt is Enterprise-only

### Error Recovery

**If module doesn't appear in Apps list**:
1. SSH into server
2. Check module exists: `ls /opt/odoo-ce/addons/ipai_MODULE_NAME/`
3. Update apps list (via UI or XML-RPC)
4. Restart Odoo: `docker restart odoo-ce`
5. Clear browser cache and retry

**If database connection fails**:
1. Verify container running: `docker ps | grep odoo-db`
2. Check database exists: `docker exec -i odoo-db psql -U odoo -l`
3. Verify network: `docker network inspect odoo-ce_odoo_network`

**If XML-RPC fails with 404**:
1. Try alternative URL: `/odoo/xmlrpc/2/common` instead of `/xmlrpc/2/common`
2. Verify proxy_mode in odoo.conf: `proxy_mode = True`
3. Check Odoo is running: `curl https://erp.insightpulseai.com`

---

## 📊 Module Status Dashboard

| Module | Status | Database | URL |
|--------|--------|----------|-----|
| ipai_clarity_ppm_parity | ✅ Installed | production | /odoo/project.project |
| ipai_ppm_monthly_close | ✅ Installed | production | /odoo/ipai_ppm_monthly_close.ppm_monthly_close |
| ipai_ocr_expense | ✅ Installed | production | /odoo/ipai_ocr_expense.ocr_expense_log |
| ipai_custom_routes | 🆕 Deployed | production | /odoo/apps/118 |
| ipai_default_home | ⚠️ Deprecated | production | (replaced by ipai_custom_routes) |
| ipai_finance_ppm | 🚧 In Progress | production | /ipai/finance/ppm |

---

## 🔗 External Dependencies

### DigitalOcean Services

**Project**: fin-workspace (29cde7a1-8280-46ad-9fdf-dea7b21a7825)

**Apps**:
- odoo-saas-platform
- mattermost-rag
- devops-engineer
- bi-architect
- finance-ssc-expert
- odoo-developer-agent
- multi-agent-orchestrator
- superset-analytics (superset.insightpulseai.com)
- mcp-coordinator (mcp.insightpulseai.com)

**Droplets**:
- odoo-erp-prod (159.223.75.148) - Main Odoo server
- ocr-service-droplet (188.166.237.231) - PaddleOCR-VL service

### Supabase

**Project**: xkxyvboeubffxxbebsll
**URL**: https://xkxyvboeubffxxbebsll.supabase.co
**Use**: Analytics, ETL, task queue (separate from Odoo DB)

### External APIs

- **PaddleOCR-VL**: Receipt OCR processing
- **OpenAI**: GPT-4o-mini for post-OCR processing
- **n8n**: Workflow automation engine

---

**End of Ecosystem Guide** | Generated: 2025-12-17 | For AI Agent Navigation
