# IPAI Superset Connector - Technical Guide

> Complete technical documentation for embedding Apache Superset dashboards in Odoo 18 CE.

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Prerequisites](#prerequisites)
4. [Installation](#installation)
5. [Configuration](#configuration)
6. [Security Model](#security-model)
7. [Models Reference](#models-reference)
8. [API Endpoints](#api-endpoints)
9. [Frontend Components](#frontend-components)
10. [Authentication Flows](#authentication-flows)
11. [Row-Level Security](#row-level-security)
12. [Troubleshooting](#troubleshooting)
13. [Production Deployment](#production-deployment)

---

## Overview

The `ipai_superset_connector` module integrates Apache Superset BI dashboards into Odoo 18 CE using the official Superset Embedded SDK pattern with guest token authentication.

### Key Features

- **Guest Token Authentication**: No Superset login required for Odoo users
- **Dashboard Mapping**: Map Superset dashboard IDs to Odoo access controls
- **Row-Level Security (RLS)**: Scope data by company, user, or custom SQL clauses
- **Token Caching**: Minimize API calls with thread-safe token cache
- **Full Audit Trail**: Track every dashboard access for compliance
- **OWL Components**: Modern Odoo 18 frontend integration

### Module Information

| Field | Value |
|-------|-------|
| Technical Name | `ipai_superset_connector` |
| Version | 18.0.1.0.0 |
| License | LGPL-3 |
| Author | InsightPulse AI |
| Dependencies | `base`, `web` |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        ODOO 18 CE (erp.insightpulseai.net)              │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   User Browser                                                          │
│       │                                                                 │
│       ▼                                                                 │
│   ┌─────────────────────┐                                              │
│   │   OWL Component     │ ◄─── SupersetEmbed / SupersetDashboardList   │
│   │   (superset_embed.js)                                              │
│   └──────────┬──────────┘                                              │
│              │ POST /ipai/superset/guest_token/<id>                    │
│              ▼                                                         │
│   ┌─────────────────────┐                                              │
│   │   Controller        │ ◄─── main.py (SupersetEmbedController)       │
│   │   - Check ACL       │                                              │
│   │   - Build RLS       │                                              │
│   │   - Log Audit       │                                              │
│   └──────────┬──────────┘                                              │
│              │                                                         │
└──────────────┼─────────────────────────────────────────────────────────┘
               │
               │ (Option A: Direct Superset API)
               ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                   SUPERSET API (superset.insightpulseai.net)            │
├─────────────────────────────────────────────────────────────────────────┤
│   1. POST /api/v1/security/login         → access_token                 │
│   2. GET  /api/v1/security/csrf_token/   → csrf_token                   │
│   3. POST /api/v1/security/guest_token/  → guest_token                  │
└─────────────────────────────────────────────────────────────────────────┘

               │ (Option B: Self-Signed JWT - Recommended)
               ▼
┌─────────────────────────────────────────────────────────────────────────┐
│              TOKEN API (superset-embed-api.insightpulseai.net)          │
├─────────────────────────────────────────────────────────────────────────┤
│   GET /api/superset-token?dashboard_id=<uuid>                           │
│   - Signs JWT with shared SUPERSET_GUEST_TOKEN_SECRET                   │
│   - No Superset API call required                                       │
│   - Returns: { token, embedUrl, expiresAt }                             │
└─────────────────────────────────────────────────────────────────────────┘

               │
               ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    SUPERSET EMBEDDED DASHBOARD                          │
├─────────────────────────────────────────────────────────────────────────┤
│   iframe src: {superset_url}/superset/dashboard/{id}/?guest_token=...  │
│   - Validates JWT against GUEST_TOKEN_JWT_SECRET                        │
│   - Applies RLS rules from token payload                                │
│   - Renders dashboard with restricted data                              │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Prerequisites

### Superset Configuration

Superset must be configured for embedded dashboard support:

```python
# superset_config.py

# Enable embedding
EMBEDDED_SUPERSET = True

# Guest token JWT (must match Token API)
GUEST_TOKEN_JWT_SECRET = os.getenv("SUPERSET_GUEST_TOKEN_SECRET")
GUEST_TOKEN_JWT_AUDIENCE = os.getenv("SUPERSET_GUEST_TOKEN_AUDIENCE", "superset")
GUEST_ROLE_NAME = "Public"

# CORS for Odoo domain
ENABLE_CORS = True
CORS_OPTIONS = {
    "supports_credentials": True,
    "origins": ["https://erp.insightpulseai.net"],
    "methods": ["GET", "POST", "OPTIONS", "PUT", "DELETE"],
    "allow_headers": "*",
}

# CSP frame-ancestors
TALISMAN_ENABLED = True
TALISMAN_CONFIG = {
    "content_security_policy": {
        "frame-ancestors": ["https://erp.insightpulseai.net"],
    },
}

# Feature flags
FEATURE_FLAGS = {
    "EMBEDDED_SUPERSET": True,
    "ROW_LEVEL_SECURITY": True,
}
```

### Required Services

| Service | URL | Purpose |
|---------|-----|---------|
| Superset | https://superset.insightpulseai.net | BI dashboards |
| Token API | https://superset-embed-api.insightpulseai.net | Self-signed JWT service |
| Odoo | https://erp.insightpulseai.net | ERP host |

---

## Installation

### Install Module

```bash
# Via Odoo CLI
odoo -c /etc/odoo/odoo.conf -d YOUR_DB -i ipai_superset_connector --stop-after-init

# Via Docker
docker compose exec odoo-core odoo -d odoo_core -i ipai_superset_connector --stop-after-init
```

### Verify Installation

```bash
# Check module is installed
docker compose exec odoo-core odoo shell -d odoo_core << 'EOF'
module = env['ir.module.module'].search([('name', '=', 'ipai_superset_connector')])
print(f"Module: {module.name}, State: {module.state}")
EOF
```

### What Gets Created

| Object Type | Name | Description |
|-------------|------|-------------|
| Database Table | `ipai_superset_dashboard` | Dashboard mappings |
| Database Table | `ipai_superset_audit` | Access audit log |
| Security Group | `Superset User` | Can view dashboards |
| Security Group | `Superset Manager` | Can configure + audit |
| Menu | Analytics | Root menu (sequence 90) |
| Config Param | `ipai_superset.base_url` | Superset URL |
| Config Param | `ipai_superset.token_api_url` | Token API URL |

---

## Configuration

### System Parameters

Set these in Settings → Technical → System Parameters:

| Key | Value | Required |
|-----|-------|----------|
| `ipai_superset.base_url` | `https://superset.insightpulseai.net` | Yes |
| `ipai_superset.token_api_url` | `https://superset-embed-api.insightpulseai.net/api/superset-token` | Yes (for self-signed JWT) |
| `ipai_superset.username` | Service account username | No (legacy API mode) |
| `ipai_superset.password` | Service account password | No (legacy API mode) |
| `ipai_superset.embed_domain` | `https://erp.insightpulseai.net` | Yes |

### Via Shell

```python
# Odoo shell
env['ir.config_parameter'].sudo().set_param(
    'ipai_superset.base_url',
    'https://superset.insightpulseai.net'
)
env['ir.config_parameter'].sudo().set_param(
    'ipai_superset.token_api_url',
    'https://superset-embed-api.insightpulseai.net/api/superset-token'
)
env.cr.commit()
```

---

## Security Model

### Groups

| Group | XML ID | Permissions |
|-------|--------|-------------|
| Superset User | `group_superset_user` | Read active dashboards |
| Superset Manager | `group_superset_manager` | Full CRUD + audit read |

### Access Control (ir.model.access.csv)

```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_superset_dashboard_user,Dashboard User,model_ipai_superset_dashboard,group_superset_user,1,0,0,0
access_superset_dashboard_manager,Dashboard Manager,model_ipai_superset_dashboard,group_superset_manager,1,1,1,1
access_superset_audit_manager,Audit Manager,model_ipai_superset_audit,group_superset_manager,1,0,0,0
```

### Record Rules

| Rule | Model | Domain | Groups |
|------|-------|--------|--------|
| User Read | `ipai.superset.dashboard` | `[('active', '=', True)]` | Superset User |
| Manager Full | `ipai.superset.dashboard` | `[(1, '=', 1)]` | Superset Manager |
| Audit Read | `ipai.superset.audit` | `[(1, '=', 1)]` | Superset Manager |

---

## Models Reference

### ipai.superset.dashboard

Maps Superset dashboards to Odoo access controls.

| Field | Type | Description |
|-------|------|-------------|
| `name` | Char | Display name in Odoo |
| `superset_dashboard_id` | Char | Superset dashboard UUID (required, unique) |
| `description` | Text | Optional description |
| `sequence` | Integer | Display order (default: 10) |
| `active` | Boolean | Hidden if False |
| `allowed_group_ids` | Many2many → res.groups | Access control |
| `rls_by_company` | Boolean | Add `company_id = X` RLS |
| `rls_by_user` | Boolean | Add `user_id = X` RLS |
| `rls_custom_clause` | Char | Custom RLS SQL with placeholders |
| `hide_title` | Boolean | Hide dashboard title in embed |
| `hide_filters` | Boolean | Hide filter bar |
| `hide_charts_controls` | Boolean | Hide chart menus |

### ipai.superset.audit

Tracks every guest token issuance.

| Field | Type | Description |
|-------|------|-------------|
| `dashboard_id` | Many2one → ipai.superset.dashboard | Dashboard accessed |
| `user_id` | Many2one → res.users | User who accessed |
| `company_id` | Many2one → res.company | User's company |
| `rls_summary` | Char | RLS rules applied |
| `ip_address` | Char | Client IP (if available) |
| `create_date` | Datetime | Access timestamp |

---

## API Endpoints

### POST /ipai/superset/guest_token/<dashboard_id>

Get a guest token for embedding a dashboard.

**Auth**: `user` (Odoo session required)

**Response**:
```json
{
  "token": "eyJhbGciOiJIUzI1NiIs...",
  "superset_url": "https://superset.insightpulseai.net",
  "dashboard_id": 123
}
```

**Errors**:
- `AccessDenied`: Dashboard not found or user lacks permission
- `UserError`: Superset API failed

### POST /ipai/superset/dashboards

List dashboards accessible to the current user.

**Auth**: `user`

**Response**:
```json
[
  {
    "id": "abc-123-uuid",
    "name": "Sales Overview",
    "description": "Company-wide sales metrics",
    "odoo_record_id": 1
  }
]
```

### POST /ipai/superset/health

Check Superset API connectivity.

**Auth**: `user`

**Response**:
```json
{
  "status": "ok",
  "superset_version": {"version": "4.0.0"}
}
```

---

## Frontend Components

### SupersetEmbed (OWL Component)

Renders an embedded Superset dashboard in an iframe.

**Template**: `ipai_superset_connector.SupersetEmbed`

**Props**:
```javascript
{
  dashboard_id: { type: String },           // Superset dashboard ID
  dashboard_name: { type: String, optional: true },
  hide_title: { type: Boolean, optional: true },
  hide_filters: { type: Boolean, optional: true },
  hide_charts_controls: { type: Boolean, optional: true },
}
```

**Action Registration**:
```javascript
registry.category("actions").add("ipai_superset_embed", SupersetEmbed);
```

**Usage** (from model action):
```python
def action_open_embed(self):
    return {
        "name": self.name,
        "type": "ir.actions.client",
        "tag": "ipai_superset_embed",
        "params": {
            "dashboard_id": self.superset_dashboard_id,
            "dashboard_name": self.name,
            "hide_title": self.hide_title,
        },
    }
```

### SupersetDashboardList (OWL Component)

Shows available dashboards as cards.

**Template**: `ipai_superset_connector.SupersetDashboardList`

**Action Registration**:
```javascript
registry.category("actions").add("ipai_superset_dashboard_list", SupersetDashboardList);
```

---

## Authentication Flows

### Flow A: Direct Superset API (Legacy)

```
Odoo Controller
    │
    ├──► POST /api/v1/security/login
    │       Body: { username, password, provider: "db", refresh: true }
    │       Response: { access_token }
    │
    ├──► GET /api/v1/security/csrf_token/
    │       Header: Authorization: Bearer {access_token}
    │       Response: { result: csrf_token }
    │
    └──► POST /api/v1/security/guest_token/
            Headers:
              Authorization: Bearer {access_token}
              X-CSRFToken: {csrf_token}
            Body: { user, resources: [{ type: "dashboard", id }], rls: [...] }
            Response: { token }
```

**Pros**: Uses official Superset API
**Cons**: Requires Superset service account, 3 API calls per token

### Flow B: Self-Signed JWT (Recommended)

```
Odoo Controller
    │
    └──► GET https://superset-embed-api.insightpulseai.net/api/superset-token
            Query: ?dashboard_id={uuid}
            Response: { token, embedUrl, expiresAt }
```

**Pros**: Single call, no Superset credentials in Odoo, faster
**Cons**: Requires shared JWT secret between Token API and Superset

---

## Row-Level Security

### Built-in RLS Options

| Option | Field | Generated Clause |
|--------|-------|------------------|
| By Company | `rls_by_company` | `company_id = {user.company_id.id}` |
| By User | `rls_by_user` | `user_id = {user.id}` |

### Custom RLS Clause

Use `rls_custom_clause` with placeholders:

| Placeholder | Replaced With |
|-------------|---------------|
| `${company_id}` | User's company ID |
| `${user_id}` | User's ID |
| `${user_login}` | User's login email |

**Example**:
```sql
region IN (SELECT region FROM user_regions WHERE user_id = ${user_id})
```

### RLS in Token Payload

```json
{
  "user": { "username": "odoo_42", "first_name": "John", "last_name": "User" },
  "resources": [{ "type": "dashboard", "id": "abc-123" }],
  "rls": [
    { "clause": "company_id = 1" },
    { "clause": "user_id = 42" }
  ]
}
```

---

## Troubleshooting

### Dashboard Not Loading

**Symptom**: Blank iframe or CORS error

**Check**:
1. Superset CORS includes Odoo domain
2. CSP frame-ancestors includes Odoo domain
3. Dashboard is enabled for embedding in Superset UI

```bash
# Check Superset config
curl -I https://superset.insightpulseai.net/health
```

### Token API Errors

**Symptom**: "Failed to get dashboard token"

**Check**:
1. Token API is running: `curl https://superset-embed-api.insightpulseai.net/health`
2. JWT secrets match between Token API and Superset
3. Config parameter `ipai_superset.token_api_url` is set

### Access Denied

**Symptom**: User can't see dashboards

**Check**:
1. User is in `Superset User` group
2. Dashboard has `allowed_group_ids` that includes user's groups (or is empty for all)
3. Dashboard is `active = True`

```python
# Debug in Odoo shell
user = env['res.users'].browse(USER_ID)
print(user.groups_id.mapped('name'))

dashboard = env['ipai.superset.dashboard'].search([])
for d in dashboard:
    print(f"{d.name}: groups={d.allowed_group_ids.mapped('name')}, active={d.active}")
```

### Missing Audit Logs

**Symptom**: No entries in Access Audit

**Check**: Audit creation happens in controller - check for exceptions:

```bash
docker compose logs odoo-core 2>&1 | grep -i superset
```

---

## Production Deployment

### Environment Variables

**Token API** (`apps/superset-embed-api`):
```env
SUPERSET_GUEST_TOKEN_SECRET=your-shared-secret-here
SUPERSET_GUEST_TOKEN_AUDIENCE=superset
SUPERSET_DOMAIN=https://superset.insightpulseai.net
ALLOWED_ORIGINS=https://erp.insightpulseai.net
NODE_ENV=production
```

**Superset** (`infra/superset`):
```env
SUPERSET_GUEST_TOKEN_SECRET=your-shared-secret-here  # MUST MATCH TOKEN API
SUPERSET_GUEST_TOKEN_AUDIENCE=superset
SUPERSET_ALLOWED_EMBEDDED_DOMAINS=https://erp.insightpulseai.net
```

### Deployment Checklist

- [ ] Superset running with `EMBEDDED_SUPERSET = True`
- [ ] Token API running with matching JWT secret
- [ ] CORS configured for Odoo domain
- [ ] CSP frame-ancestors configured
- [ ] Module installed in Odoo
- [ ] Config parameters set (`ipai_superset.base_url`, `ipai_superset.token_api_url`)
- [ ] Users assigned to `Superset User` or `Superset Manager` groups
- [ ] Dashboard mappings created with Superset UUIDs
- [ ] Dashboards enabled for embedding in Superset UI

### Health Checks

```bash
# Superset
curl -f https://superset.insightpulseai.net/health

# Token API
curl -f https://superset-embed-api.insightpulseai.net/health

# Token generation test
curl "https://superset-embed-api.insightpulseai.net/api/superset-token?dashboard_id=test-uuid"
```

---

## File Reference

```
addons/ipai/ipai_superset_connector/
├── __init__.py
├── __manifest__.py
├── controllers/
│   ├── __init__.py
│   └── main.py                    # HTTP endpoints
├── data/
│   └── ir_config_parameter.xml    # Default config values
├── models/
│   ├── __init__.py
│   ├── superset_dashboard.py      # Dashboard mapping model
│   └── superset_audit.py          # Audit log model
├── security/
│   ├── ir.model.access.csv        # Model access rules
│   └── superset_security.xml      # Groups + record rules
├── services/
│   ├── __init__.py
│   └── superset_client.py         # Superset API client
├── static/
│   └── src/
│       ├── css/
│       │   └── superset_embed.css
│       ├── js/
│       │   └── superset_embed.js  # OWL components
│       └── xml/
│           └── superset_embed.xml # QWeb templates
└── views/
    ├── dashboard_views.xml        # Dashboard form/list
    ├── audit_views.xml            # Audit log views
    └── menu.xml                   # Menu items
```

---

## Related Documentation

- [Apache Superset Embedding Docs](https://superset.apache.org/docs/security/#embedded-dashboards)
- [Superset Embedded SDK](https://github.com/apache/superset/tree/master/superset-frontend/packages/superset-ui-embedded-sdk)
- [Odoo 18 OWL Documentation](https://www.odoo.com/documentation/18.0/developer/reference/frontend/owl.html)

---

*Last updated: 2026-01-12*
