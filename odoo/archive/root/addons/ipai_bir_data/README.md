# IPAI BIR Data Templates

Data-only Odoo module providing predefined project templates for Philippine BIR tax filing and month-end closing workflows.

## What This Is

**Pure data templates** - no custom models, no database schema changes. Just XML records that populate standard Odoo `project.project` and `project.task.type` tables.

## What It Provides

### 1. BIR Tax Filing Project

- **Stages**: Preparation → Review → Submission → Done
- **Use Case**: Philippine Bureau of Internal Revenue tax filing workflows

### 2. Month-End Close Project

- **Stages**: Preparation → Review → Done
- **Use Case**: Monthly financial closing process

### 3. CSV Templates

- `templates/bir_projects.csv` - Project import template
- `templates/monthend_tasks.csv` - Task import template

## Installation

```bash
# Install via CLI
./odoo-bin -d <database> -i ipai_bir_data --stop-after-init

# Or via UI
Apps → Update Apps List → Search "IPAI BIR" → Install
```

## Verification

```bash
# Check projects created
psql -d <database> -c "SELECT name FROM project_project WHERE name IN ('BIR Tax Filing', 'Month-End Close');"

# Check stages attached
psql -d <database> -c "
SELECT p.name AS project, t.name AS stage, t.sequence
FROM project_project p
JOIN project_task_type_rel r ON r.project_id = p.id
JOIN project_task_type t ON t.id = r.type_id
WHERE p.name IN ('BIR Tax Filing', 'Month-End Close')
ORDER BY p.name, t.sequence;
"
```

## Usage

### Via UI

1. Go to **Project** app
2. Find "BIR Tax Filing" or "Month-End Close" project
3. Create tasks and move through stages

### Via CSV Import

```bash
# Import projects
# Project → Import → Upload templates/bir_projects.csv

# Import tasks
# Project → Tasks → Import → Upload templates/monthend_tasks.csv
```

### Via XML-RPC Script

```python
import xmlrpc.client

url = "http://localhost:8069"
db = "odoo_dev"
username = "admin"
password = "admin"

common = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common")
uid = common.authenticate(db, username, password, {})

models = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/object")

# Create task in BIR project
project_id = models.execute_kw(db, uid, password,
    'project.project', 'search',
    [[['name', '=', 'BIR Tax Filing']]], {'limit': 1})[0]

task_id = models.execute_kw(db, uid, password,
    'project.task', 'create',
    [{'name': '2026 Q1 BIR Filing', 'project_id': project_id}])
```

## Customization

### Add More Stages

Edit `data/bir_projects.xml` or `data/monthend_projects.xml`:

```xml
<record id="stage_custom" model="project.task.type">
  <field name="name">Custom Stage</field>
  <field name="sequence">25</field>
  <field name="project_ids" eval="[(4, ref('ipai_bir_data.project_bir_tax_filing'))]"/>
</record>
```

### Add More Projects

Create new XML file in `data/` and add to `__manifest__.py`:

```xml
<record id="project_custom" model="project.project">
  <field name="name">My Custom Project</field>
</record>
```

## Uninstallation

```bash
# Mark for removal
psql -d <database> -c "UPDATE ir_module_module SET state='to remove' WHERE name='ipai_bir_data';"

# Uninstall
./odoo-bin -d <database> -u ipai_bir_data --stop-after-init
```

This will remove the created projects and stages.

## vs. ipai_ppm_okr

| Feature        | ipai_bir_data           | ipai_ppm_okr                   |
| -------------- | ----------------------- | ------------------------------ |
| **Purpose**    | BIR/month-end templates | Full PPM+OKR governance        |
| **Approach**   | Data-only (XML)         | Custom models (17 tables)      |
| **Database**   | No schema changes       | New tables created             |
| **Use Case**   | Workflow templates      | Portfolio/Program/OKR tracking |
| **Complexity** | Low                     | High                           |

**Use `ipai_bir_data` if**: You just need BIR/month-end project templates
**Use `ipai_ppm_okr` if**: You need portfolio governance, OKR tracking, risk management

## License

LGPL-3.0
