# Odoo Enterprise to CE+OCA Technical Mapping Guide

**Repository**: `odoo-ce` (jgtolentino/odoo-ce)
**Odoo Series**: 18.0 CE + OCA baseline
**Reference**: Odoo 19 EE introspection (Contacts, Knowledge, PoS, Studio, AI, IoT)
**Last Updated**: 2026-01-20
**Status**: Canonical technical guide for EE → CE migration

---

## 1. Overview

This guide classifies Odoo Enterprise features into four buckets:

| Bucket | Description |
|--------|-------------|
| **CE-Native** | Features already present in Odoo 18 CE core or trivial OCA equivalents |
| **EE → OCA Replacement** | EE features with mature OCA/community modules covering 80-100% use-cases |
| **EE → ipai_enterprise_bridge** | Features needing model/field compatibility with no good OCA equivalent |
| **Out-of-scope / Ignore** | Features explicitly not replicated; data dropped at migration |

**Key Principle**: `ipai_enterprise_bridge` provides **minimal model/field compatibility**, **redirection** to CE/OCA models, and **safe stubs** for dropped functionality. It never re-implements full EE products.

---

## 2. Feature Classification Matrix

### 2.1 General & UI

| Feature | Status | Strategy |
|---------|--------|----------|
| Desktop / Web UI | CE-Native | Standard CE web client |
| Mobile (Android / iOS) | CE-Native | Standard responsive web views |
| Unlimited support, upgrades | Commercial, not technical | Own support processes |

**Bridge needed**: None

---

### 2.2 Contacts / CRM Base

| Feature | Status | Strategy |
|---------|--------|----------|
| Contacts (Address book) | CE-Native | `contacts` module in CE |
| Basic CRM (leads/opportunities) | CE-Native + OCA | `crm` + OCA `crm` extensions |
| Partner extra EE fields | Bridge | Handle via `ipai_enterprise_bridge` |

**Bridge needed**: Only for extra fields introduced by EE modules that reference `res.partner` (AI, Knowledge, IoT, PoS linkages).

---

### 2.3 Product & Pricelists

| Feature | Status | Strategy |
|---------|--------|----------|
| Product templates, variants | CE-Native | `product` module |
| Price lists, packaging, labels | CE-Native | Already in CE |
| Product attributes | CE-Native | Standard CE functionality |

**Bridge needed**: None. `product.*` models are **authoritative** from CE. Never shadow or override.

---

### 2.4 Knowledge (Notion-like Wiki)

**Status**: EE-only. No direct CE equivalent.

**Key Models** (from 19 EE introspection):
- `knowledge.article`
- `knowledge.article.favorite`
- `knowledge.article.member`
- `knowledge.article.stage`

**Dependencies**: `portal`, `html_editor`, `mail`, `web_hierarchy`, `web_unsplash`

**Strategy**: `ipai_enterprise_bridge` required.

| Component | Implementation |
|-----------|---------------|
| **Shadow Models** | Create `_name`-compatible models with minimal fields |
| **Fields to keep** | `id`, `name`, `body`, `parent_id`, permissions fields |
| **UI exposure** | None (read-only, no menus) |
| **Migration** | Load EE records → export to PDF/HTML attachments or external docs system |
| **Redirection** | Computed URL field pointing to replacement system (Scout GenieView) |

```python
# Bridge pattern for knowledge.article
class KnowledgeArticle(models.Model):
    _name = "knowledge.article"
    _description = "Knowledge Article (Bridge)"

    name = fields.Char(string="Title", required=True)
    body = fields.Html(string="Content")
    parent_id = fields.Many2one("knowledge.article", string="Parent")
    active = fields.Boolean(default=True)
    # External link to replacement system
    external_url = fields.Char(string="External URL", compute="_compute_external_url")
```

---

### 2.5 AI App

**Status**: EE-only.

**Key Models** (from 19 EE introspection):
- `ai.agent`
- `ai.topic`
- `ai.composer` (optional)

**Strategy**: `ipai_enterprise_bridge` as proxy to Pulser/custom agent framework.

| Component | Implementation |
|-----------|---------------|
| **Shim Models** | `ai.agent` shim that `_inherits` or links to `ipai.agent` |
| **Field subset** | `name`, `description`, `topic_id`, `provider`, `model`, `config`, `active` |
| **Behavior** | CRUD operations write-through to Pulser/Supabase registry |
| **Migration** | EE AI agents → `ipai` agent definitions, keep `ipai_source_agent_id` for traceability |

```python
# Bridge pattern for ai.agent
class AiAgent(models.Model):
    _name = "ai.agent"
    _description = "AI Agent (Bridge to IPAI)"

    name = fields.Char(required=True)
    description = fields.Text()
    provider = fields.Char()  # e.g., "anthropic", "openai"
    model = fields.Char()  # e.g., "claude-3-opus"
    config = fields.Text()  # JSON config
    active = fields.Boolean(default=True)
    # Link to IPAI canonical agent
    ipai_agent_id = fields.Many2one("ipai.agent", string="IPAI Agent")
    ipai_source_agent_id = fields.Integer(string="Original EE Agent ID")
```

---

### 2.6 Studio (`web_studio`)

**Status**: EE-only. No OCA equivalent.

**Strategy**: Minimal stubs + pre-migration cleanup.

| Component | Implementation |
|-----------|---------------|
| **Pre-migration** | Flatten Studio customizations to standard modules/XML or delete |
| **Bridge behavior** | Ensure `ir.model.data.studio = True` doesn't break loading |
| **UI exposure** | None (no Studio menus on CE) |

**Fields to stub**:
```python
# Ensure these system model fields exist
class IrModelData(models.Model):
    _inherit = "ir.model.data"
    studio = fields.Boolean(default=False)
```

---

### 2.7 Point of Sale (`point_of_sale`)

**Status**: CE has basic PoS; advanced features (restaurant, IoT integration) are EE.

**Strategy**: Dual track.

| Track | Implementation |
|-------|---------------|
| **Production PoS** | Use CE PoS + OCA addons (`OCA/pos`, `OCA/pos-management`) |
| **EE data (historical)** | Light-weight shadow models, mark as archived |
| **Migration** | Summarize EE `pos.order` → `account.move` / Scout retail tables |

```python
# Bridge pattern for historical pos.order
class PosOrder(models.Model):
    _name = "pos.order"
    _description = "POS Order (Bridge - Historical)"

    name = fields.Char(required=True)
    date_order = fields.Datetime()
    partner_id = fields.Many2one("res.partner")
    amount_total = fields.Float()
    state = fields.Selection([
        ('draft', 'Draft'),
        ('paid', 'Paid'),
        ('archived', 'Archived'),
    ], default='archived')
    # All imported EE orders are archived
    _sql_constraints = [
        ('state_archived', "CHECK(state = 'archived')", "Bridge POS orders must be archived")
    ]
```

---

### 2.8 IoT (`iot`)

**Status**: EE-only.

**Strategy**: Drop functionality, optional stub for FK safety.

| Component | Implementation |
|-----------|---------------|
| **Models** | Minimal `iot.box`, `iot.device` with basic fields |
| **State** | Mark all as inactive |
| **UI** | None |

```python
# Stub for iot.box
class IotBox(models.Model):
    _name = "iot.box"
    _description = "IoT Box (Stub)"

    name = fields.Char(required=True)
    identifier = fields.Char()
    ip = fields.Char()
    active = fields.Boolean(default=False)  # Always inactive
```

---

### 2.9 Other Matrix Areas

| Area | EE-only Features | Strategy |
|------|------------------|----------|
| **Accounting/Finance** | Consolidation, OCR, Spreadsheet | OCA `account-financial-tools`, `account-reports`; bridge only for unmapped models |
| **Expenses/Payroll** | OCR receipts, country payroll engines | OCA HR/Payroll where available; drop advanced features |
| **Documents + Sign** | Full `documents`, `sign` apps | External DMS (Supabase/Drive) + e-sign provider; or thin `ipai_documents_bridge` |
| **Social/SMS/Marketing** | Automation campaigns, SMS credits | 3rd-party marketing stack; keep contact/event data only |
| **Helpdesk/Field Service** | EE-only versions | OCA `helpdesk` / `field-service` as canonical; bridge EE data out |

---

## 3. `ipai_enterprise_bridge` Technical Design

### 3.1 Module Scope

```python
# addons/ipai/ipai_enterprise_bridge/__manifest__.py
{
    "name": "IPAI Enterprise Bridge",
    "version": "18.0.1.0.0",
    "depends": [
        "base", "mail", "web", "portal",  # Core
        "account", "stock",  # If keeping PoS summaries
        "ipai_workspace_core",  # IPAI foundation
    ],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "data/bridge_groups.xml",
    ],
}
```

### 3.2 Model Patterns

| Pattern | Use Case | Implementation |
|---------|----------|----------------|
| **Shadow Model** | Read-only replicas of EE models | Same `_name`, minimal fields, `auto = False` for SQL views |
| **Shim Model** | Redirect to canonical CE/IPAI model | `_inherits` or explicit `Many2one` to real model |
| **Null Object / Stub** | Drop functionality, preserve FK safety | Same `_name`, only `name` field |

### 3.3 Migration Rules

| EE Module | Migration Behavior |
|-----------|-------------------|
| **Knowledge** | Import to shadow → generate attachments/external docs → store cross-link |
| **AI app** | EE `ai.agent` → create `ipai.agent` + matching shim record |
| **PoS** | Summarize `pos.order` → accounting/Scout tables → skeletal shadow for history |
| **IoT** | Import minimal metadata if needed; no runtime behavior |
| **Studio** | Ensure `ir.model.data.studio` flag exists; no UI |

### 3.4 Security Model

- All bridge models in dedicated security group: **"IPAI Enterprise Bridge - Admin only"**
- No standard menus; if needed, under **"IPAI / Technical / EE Bridge"**
- Default: read-only for non-admin users

---

## 4. CE/OCA Implementation Priority

### 4.1 Core ERP (First-class Citizens)

Use CE + OCA as primary implementation:

| Domain | OCA Repositories |
|--------|-----------------|
| Accounting | `account-financial-tools`, `account-reconcile`, `account-financial-reporting` |
| Sales | `sale-workflow`, `sale-reporting` |
| Purchase | `purchase-workflow` |
| Inventory | `stock-logistics-warehouse`, `stock-logistics-workflow` |
| HR | `hr`, `payroll`, `timesheet` |
| Project | `project` |
| Website/eCommerce | Standard CE |

### 4.2 OCA Baseline (from oca.lock.json)

| Tier | Repositories | Purpose |
|------|--------------|---------|
| 0 | server-tools, server-ux, server-backend | Foundation |
| 1 | web | Platform UX |
| 2 | queue | Background processing |
| 4 | reporting-engine, mis-builder | Reporting & BI |
| 7 | rest-framework | API layer |
| 9 | sale-workflow, purchase-workflow, project | Workflow extensions |

---

## 5. Migration Playbook

### 5.1 Pre-Migration (19 EE Sandbox)

```bash
# 1. Export EE-specific data
odoo-bin shell -d ee_sandbox << 'EOF'
# Export knowledge articles
articles = env['knowledge.article'].search([])
# ... serialize to JSON/XML
EOF

# 2. Flatten Studio customizations
# Export as standard modules or delete experimental ones

# 3. Archive PoS data
# Summarize orders, mark sessions as closed
```

### 5.2 Transform (ETL)

```python
# Transform EE data to CE/OCA/Bridge format
def transform_knowledge_article(ee_article):
    return {
        'name': ee_article['name'],
        'body': ee_article['body'],
        'parent_id': ee_article['parent_id'],
        'active': True,
        'external_url': f"https://docs.example.com/{ee_article['id']}"
    }

def transform_ai_agent(ee_agent):
    ipai_agent = create_ipai_agent(ee_agent)
    return {
        'name': ee_agent['name'],
        'ipai_agent_id': ipai_agent.id,
        'ipai_source_agent_id': ee_agent['id'],
    }
```

### 5.3 Load (18 CE + OCA + Bridge)

```bash
# Install bridge module
odoo-bin -d ce_prod -i ipai_enterprise_bridge --stop-after-init

# Import transformed data
odoo-bin shell -d ce_prod << 'EOF'
# Load knowledge articles
for article_data in transformed_articles:
    env['knowledge.article'].create(article_data)
# ... etc
EOF
```

### 5.4 Verification

```bash
# Verify models exist
odoo-bin shell -d ce_prod << 'EOF'
print("Knowledge articles:", env['knowledge.article'].search_count([]))
print("AI agents:", env['ai.agent'].search_count([]))
print("Bridge PoS orders:", env['pos.order'].search_count([('state', '=', 'archived')]))
EOF

# Verify no runtime errors
curl -s -o /dev/null -w "%{http_code}" http://localhost:8069/web/health
```

---

## 6. Decommissioning Plan

| Phase | EE Feature | Target State |
|-------|------------|--------------|
| Phase 1 | Knowledge | Fully migrated to Scout GenieView / external docs |
| Phase 2 | AI app | Fully proxied to Pulser/IPAI agents |
| Phase 3 | PoS history | Archived, only for reporting lookups |
| Phase 4 | Studio metadata | Ignored, no impact on runtime |
| Phase 5 | IoT | Dropped entirely |

After decommissioning, bridge models become **read-only archives** with no business logic.

---

## 7. Related Documentation

| Document | Path | Purpose |
|----------|------|---------|
| OCA Installation Guide | `/docs/OCA_INSTALLATION_GUIDE.md` | OCA module installation |
| OCA Style Contract | `/docs/OCA_STYLE_CONTRACT.md` | Module conventions |
| Enterprise Bridge Policy | `/addons/ipai/ipai_enterprise_bridge/POLICY.md` | Bridge module policy |
| CE/OCA Project Stack | `/docs/CE_OCA_PROJECT_STACK.md` | Full stack architecture |

---

## 8. Quick Reference

### EE Feature → Strategy Lookup

```
Knowledge        → Bridge (shadow) → External docs
AI app           → Bridge (shim)  → Pulser/IPAI agents
Studio           → Bridge (stub)  → Ignore
PoS (advanced)   → Bridge (shadow) → CE PoS + OCA
IoT              → Bridge (stub)  → Drop
Documents        → Bridge or drop → External DMS
Sign             → Drop           → External e-sign
Consolidation    → OCA            → account-financial-tools
Spreadsheet      → OCA            → spreadsheet_oca
```

### Model Pattern Lookup

```
EE Model              CE/OCA/Bridge
knowledge.article  →  ipai_enterprise_bridge (shadow)
ai.agent           →  ipai_enterprise_bridge (shim → ipai.agent)
pos.order          →  CE pos.order + bridge (archived history)
iot.box            →  ipai_enterprise_bridge (stub)
ir.model.data      →  CE + studio field (stub)
```

---

**Version**: 1.0.0
**Last Updated**: 2026-01-20
**Branch**: 18.0
