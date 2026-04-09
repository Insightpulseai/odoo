# Skill: AI-First Odoo Studio Equivalent

## Metadata

| Field | Value |
|-------|-------|
| **id** | `ai-studio-equivalent` |
| **domain** | `odoo_ce` |
| **source** | Power Pages Copilot patterns + Odoo Studio feature set |
| **extracted** | 2026-03-16 |
| **applies_to** | odoo, agents, web |
| **tags** | studio, low-code, copilot, form-builder, view-generator, ai-first, ee-parity |

---

## What This Replaces

Odoo Studio is an **Enterprise-only** visual builder ($$$) that lets non-developers create custom apps, views, forms, reports, and automations without writing code. We replace it with an **AI-first** approach: describe what you want → copilot generates Odoo-compliant XML/Python → deploys as an `ipai_*` module.

## Odoo Studio → AI Studio Parity Matrix

| Odoo Studio Feature | AI Studio Equivalent | How |
|---------------------|---------------------|-----|
| **Drag-and-drop form builder** | Natural language → form XML | Copilot generates `<form>` view XML from description |
| **Custom list/tree views** | NL → list view XML | Copilot generates `<list>` view XML |
| **Custom kanban views** | NL → kanban XML | Copilot generates `<kanban>` view XML |
| **Custom fields** | NL → model Python + XML | Copilot generates field definitions + views |
| **Custom apps** | NL → full module scaffold | Copilot generates `__manifest__.py`, models, views, security |
| **Automated actions** | NL → `ir.actions.server` XML | Copilot generates server actions |
| **Report builder** | NL → QWeb report template | Copilot generates report XML |
| **Dashboard builder** | NL → dashboard XML | Copilot generates `<dashboard>` view |
| **Theme/style editor** | NL → SCSS + asset bundle | Copilot generates theme overrides |
| **Approval workflows** | NL → state machine + buttons | Copilot generates workflow model + views |
| **Access rights editor** | NL → `ir.model.access.csv` + groups | Copilot generates security config |
| **Menu editor** | NL → `ir.ui.menu` XML | Copilot generates menu items |
| **Website page builder** | NL → website page (Odoo Website module) | Copilot generates website view |
| **Custom filters/groups** | NL → search view XML | Copilot generates `<search>` view |

## Architecture

```
User (natural language request via Odoo Discuss or web widget)
    ↓
ipai-odoo-copilot (Foundry Agent)
    ↓ understands: Odoo 18 ORM, view types, module structure
    ↓ references: odoo18-* skills (75+ domain skills)
    ↓ validates: OCA coding standards, IPAI naming convention
    ↓
Generates one of:
    ├── View XML (form/list/kanban/search/dashboard/report)
    ├── Model Python (fields, compute, constraints)
    ├── Security CSV (access rights)
    ├── Menu XML (navigation)
    ├── Action XML (server actions, automated actions)
    ├── Full module scaffold (manifest + models + views + security)
    └── Theme SCSS (styling overrides)
    ↓
Output modes:
    ├── Preview: show generated code for review
    ├── Draft module: create ipai_custom_<name>/ in addons/ipai/
    ├── Direct apply: install/update module on target DB
    └── PR: create branch + PR for review before deploy
```

## Copilot Prompt Patterns

### Pattern 1: Create a Custom Form

**User says:**
> "Create a form for tracking equipment maintenance requests with fields for equipment name, location, issue description, priority, and assigned technician"

**Copilot generates:**

```python
# models/maintenance_request.py
from odoo import _, api, fields, models

class MaintenanceRequest(models.Model):
    _name = 'ipai.maintenance.request'
    _description = 'Equipment Maintenance Request'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'priority desc, create_date desc'

    name = fields.Char(string='Request', required=True)
    equipment_name = fields.Char(string='Equipment', required=True)
    location = fields.Char(string='Location')
    description = fields.Text(string='Issue Description')
    priority = fields.Selection([
        ('0', 'Normal'),
        ('1', 'Low'),
        ('2', 'Medium'),
        ('3', 'High'),
    ], default='0', string='Priority')
    technician_id = fields.Many2one('hr.employee', string='Assigned Technician')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('in_progress', 'In Progress'),
        ('done', 'Done'),
    ], default='draft', tracking=True)

    def action_submit(self):
        self.ensure_one()
        self.state = 'submitted'

    def action_start(self):
        self.ensure_one()
        self.state = 'in_progress'

    def action_done(self):
        self.ensure_one()
        self.state = 'done'
```

```xml
<!-- views/maintenance_request_views.xml -->
<record id="maintenance_request_view_form" model="ir.ui.view">
    <field name="name">ipai.maintenance.request.form</field>
    <field name="model">ipai.maintenance.request</field>
    <field name="arch" type="xml">
        <form>
            <header>
                <button name="action_submit" type="object" string="Submit"
                        class="btn-primary" invisible="state != 'draft'"/>
                <button name="action_start" type="object" string="Start"
                        class="btn-primary" invisible="state != 'submitted'"/>
                <button name="action_done" type="object" string="Done"
                        class="btn-success" invisible="state != 'in_progress'"/>
                <field name="state" widget="statusbar"/>
            </header>
            <sheet>
                <group>
                    <group>
                        <field name="name"/>
                        <field name="equipment_name"/>
                        <field name="location"/>
                    </group>
                    <group>
                        <field name="priority" widget="priority"/>
                        <field name="technician_id"/>
                    </group>
                </group>
                <notebook>
                    <page string="Description">
                        <field name="description"/>
                    </page>
                </notebook>
            </sheet>
            <chatter/>
        </form>
    </field>
</record>
```

### Pattern 2: Add Fields to Existing Model

**User says:**
> "Add a 'tax_exempt' boolean and 'exemption_reason' text field to the partner form"

**Copilot generates:**

```python
# models/res_partner.py
from odoo import fields, models

class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_tax_exempt = fields.Boolean(string='Tax Exempt')
    exemption_reason = fields.Text(string='Exemption Reason')
```

```xml
<!-- views/res_partner_views.xml -->
<record id="res_partner_view_form_tax_exempt" model="ir.ui.view">
    <field name="name">res.partner.form.tax.exempt</field>
    <field name="model">res.partner</field>
    <field name="inherit_id" ref="base.view_partner_form"/>
    <field name="arch" type="xml">
        <xpath expr="//field[@name='vat']" position="after">
            <field name="is_tax_exempt"/>
            <field name="exemption_reason"
                   invisible="not is_tax_exempt"/>
        </xpath>
    </field>
</record>
```

### Pattern 3: Create Automated Action

**User says:**
> "When an expense report total exceeds 50,000 PHP, automatically assign it to the Finance Manager for review"

**Copilot generates:**

```xml
<!-- data/ir_actions_server.xml -->
<record id="action_auto_assign_high_value_expense" model="ir.actions.server">
    <field name="name">Auto-assign high-value expenses</field>
    <field name="model_id" ref="hr_expense.model_hr_expense_sheet"/>
    <field name="state">code</field>
    <field name="code">
for record in records:
    if record.total_amount > 50000:
        finance_mgr = env['hr.employee'].search(
            [('job_title', 'ilike', 'Finance Manager')], limit=1
        )
        if finance_mgr:
            record.message_subscribe(partner_ids=[finance_mgr.user_id.partner_id.id])
            record.activity_schedule(
                'mail.mail_activity_data_todo',
                summary=_('High-value expense review: %s', record.name),
                user_id=finance_mgr.user_id.id,
            )
    </field>
</record>
```

### Pattern 4: Full Module Scaffold

**User says:**
> "Create a module for tracking client meeting notes with date, attendees, topics discussed, action items, and follow-up date"

**Copilot generates complete module:**

```
addons/ipai/ipai_meeting_notes/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   └── meeting_note.py
├── views/
│   ├── meeting_note_views.xml
│   └── meeting_note_menus.xml
├── security/
│   ├── ir.model.access.csv
│   └── security.xml
└── data/
    └── meeting_note_data.xml
```

## Power Pages Patterns Applied to Odoo

| Power Pages Feature | Odoo AI Studio Implementation |
|---------------------|------------------------------|
| **Copilot site creation** | Describe app → full module generated |
| **Pages workspace** | Views workspace: form/list/kanban/search |
| **Styling workspace** | Theme SCSS generation |
| **Data workspace** | Model/field definition from NL |
| **Security workspace** | Access rights + web roles from NL |
| **Dataverse integration** | ORM model generation |
| **Bootstrap responsive** | Odoo 18 responsive framework |
| **Template library** | Module template families |

## Implementation Layers

### Layer 1: View Generator (Quick Win)

Copilot generates view XML from natural language. No new models — extends existing ones.

**Effort**: 1 week
**Value**: Replaces Studio's most-used feature (visual form/list editing)

### Layer 2: Field + Model Generator

Copilot generates Python model code with fields, computes, and constraints.

**Effort**: 1 week
**Value**: Replaces Studio's custom field/model creation

### Layer 3: Full Module Scaffold

Copilot generates complete module from description: manifest, models, views, security, menus.

**Effort**: 2 weeks
**Value**: Replaces Studio's custom app creation

### Layer 4: Action + Automation Generator

Copilot generates server actions, automated actions, and scheduled actions from NL.

**Effort**: 1 week
**Value**: Replaces Studio's automation features

### Layer 5: Report Generator

Copilot generates QWeb report templates from NL description.

**Effort**: 1 week
**Value**: Replaces Studio's report builder

## Copilot Tools Required

| Tool | Purpose | Status |
|------|---------|--------|
| `odoo_scaffold` | Generate module directory structure | Exists (`odoo-bin scaffold`) |
| `odoo_install` | Install/update generated module | Exists (`odoo-module-install.yml`) |
| `xml_validate` | Validate generated view XML | Build |
| `python_lint` | Lint generated Python (ruff) | Exists |
| `odoo_test` | Run tests on generated module | Exists (`ci-odoo.yml`) |
| `git_branch` | Create branch for review | Exists (`gh-safe`) |

## Knowledge Required (Already in Skills)

| Skill | Provides |
|-------|---------|
| `odoo18-orm/SKILL.md` | Model class patterns, field types, ORM methods |
| `odoo18-frontend/SKILL.md` | View types, XML structure, widgets |
| `odoo18-module/SKILL.md` | Module structure, manifest, naming |
| `odoo18-security/SKILL.md` | Access rights, groups, record rules |
| `odoo18-actions/SKILL.md` | Server actions, automated actions |
| `oca-development-standards/SKILL.md` | OCA quality standards |
| `odoo18-coding-guidelines/SKILL.md` | Coding conventions |

## Concur/Studio Parity Impact

| Feature | Before AI Studio | After AI Studio |
|---------|-----------------|----------------|
| Custom forms | Manual XML or Studio (EE) | NL → XML (free) |
| Custom fields | Manual Python or Studio (EE) | NL → Python (free) |
| Custom apps | Manual scaffold or Studio (EE) | NL → full module (free) |
| Automations | Manual code or Studio (EE) | NL → server actions (free) |
| Reports | Manual QWeb or Studio (EE) | NL → report template (free) |
| **EE parity delta** | Studio = EE-only feature | **AI Studio = CE-native** |

**This closes the biggest single EE parity gap** — Studio is the #1 reason companies pay for Enterprise.

## Foundry Copilot Integration

The AI Studio capability is delivered through `ipai-odoo-copilot` (already registered as a Foundry agent):

```yaml
# Addition to agents__runtime__odoo_copilot__v1.manifest.yaml
capabilities:
  - navigational
  - informational
  - transactional
  - compliance_intel
  - studio_equivalent    # NEW — AI-first visual builder replacement
```

### Copilot Interaction Modes

| Mode | How | When |
|------|-----|------|
| **Odoo Discuss** | Chat with copilot bot in Discuss channel | Quick field additions, view tweaks |
| **Web widget** | Overlay panel in Odoo backend | Full module creation, guided workflow |
| **CLI** | `claude "create an Odoo module for..."` | Developer workflow |
| **PR workflow** | Copilot creates branch + PR for review | Team workflow with approval |

## Release Mapping

| Release | AI Studio Feature |
|---------|-------------------|
| **R1** (Month 1) | View generator (form/list from NL) — read-only copilot |
| **R2** (Month 2) | Field + model generator — draft module creation |
| **R3** (Month 3) | Full scaffold + automation generator |
| **R4** (Month 4) | Report generator + theme editor |

## Why This is Better Than Odoo Studio

| Advantage | Detail |
|-----------|--------|
| **Free** | No Enterprise license required |
| **AI-first** | Describe in natural language, not drag-and-drop |
| **Code output** | Generates real modules (version-controlled, testable) |
| **OCA-compliant** | Follows OCA standards automatically |
| **Reviewable** | Creates PRs for team review before deploy |
| **Composable** | Generated modules work with CI/CD pipeline |
| **Extensible** | Generated code can be manually refined |
| **Multi-surface** | Works via Discuss, web widget, CLI, or PR workflow |

Odoo Studio produces opaque customizations tied to the database. AI Studio produces **real, portable, version-controlled Odoo modules**.
