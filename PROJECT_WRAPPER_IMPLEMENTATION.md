# Finance PPM Project Wrapper Implementation
*Odoo 18 Community Edition - Standard Project Module Integration*

## 🎯 Implementation Strategy

**Objective:** Merge standard Odoo `project` module into Finance PPM to leverage Kanban, Subtasks, Chatter, and Timeline views while keeping Finance-specific fields.

## 📋 Implementation Steps

### 1. Update Manifest & Dependencies

**File:** `__manifest__.py`
```python
{
    'name': 'Finance PPM',
    'version': '18.0.1.0.0',
    'category': 'Finance',
    'summary': 'Finance Portfolio & Project Management',
    'depends': [
        'project',           # Standard project module
        'board',             # Dashboard functionality
        'web_timeline',      # Timeline/Gantt view (if available)
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/project_task_views.xml',
        'views/finance_menus.xml',
        'data/project_data.xml',
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
```

### 2. Extend Standard Task Model

**File:** `models/project_task.py`
```python
from odoo import models, fields, api

class ProjectTask(models.Model):
    _inherit = 'project.task'
    
    # Finance-specific fields
    finance_code = fields.Char(
        string='Finance Code',
        help='Employee code like RIM, BOM, CKVC'
    )
    
    reviewer_id = fields.Many2one(
        'res.users',
        string='Reviewer/Consulted',
        help='Person responsible for reviewing the task'
    )
    
    approver_id = fields.Many2one(
        'res.users',
        string='Approver/Accountable',
        help='Person responsible for final approval'
    )
    
    finance_deadline_type = fields.Selection([
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('annual', 'Annual'),
    ], string='Finance Deadline Type')
    
    # Link to finance person directory
    finance_person_id = fields.Many2one(
        'ipai_finance_person',
        string='Finance Person'
    )
    
    # Duration fields for finance workflow
    prep_duration = fields.Float(string='Prep Duration (Days)')
    review_duration = fields.Float(string='Review Duration (Days)')
    approval_duration = fields.Float(string='Approval Duration (Days)')
    
    # Finance categories
    finance_category = fields.Selection([
        ('foundation_corp', 'Foundation & Corp'),
        ('revenue_wip', 'Revenue/WIP'),
        ('vat_tax', 'VAT & Tax Reporting'),
        ('working_capital', 'Working Capital'),
        ('compliance', 'Compliance'),
        ('administrative', 'Administrative'),
    ], string='Finance Category')
```

### 3. Extend Task Form View

**File:** `views/project_task_views.xml`
```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <!-- Extend standard project task form -->
    <record id="view_task_form_finance_inherit" model="ir.ui.view">
        <field name="name">project.task.form.finance.inherit</field>
        <field name="model">project.task</field>
        <field name="inherit_id" ref="project.view_task_form2"/>
        <field name="arch" type="xml">
            <!-- Add Finance Roles tab -->
            <xpath expr="//page[@name='specification']" position="after">
                <page string="Finance Roles">
                    <group>
                        <group string="Finance Assignment">
                            <field name="finance_code"/>
                            <field name="finance_person_id"/>
                            <field name="finance_category"/>
                        </group>
                        <group string="Approval Workflow">
                            <field name="reviewer_id"/>
                            <field name="approver_id"/>
                            <field name="finance_deadline_type"/>
                        </group>
                    </group>
                    <group string="Duration Planning">
                        <field name="prep_duration"/>
                        <field name="review_duration"/>
                        <field name="approval_duration"/>
                    </group>
                </page>
            </xpath>
            
            <!-- Add finance code to main form -->
            <xpath expr="//field[@name='name']" position="after">
                <field name="finance_code" class="oe_inline"/>
            </xpath>
        </field>
    </record>
</odoo>
```

### 4. Create Finance Operations Action

**File:** `views/finance_menus.xml`
```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <!-- Finance Master Project -->
    <record id="project_finance_master" model="project.project">
        <field name="name">Finance Month-End & Tax Cycle</field>
        <field name="description">Master project for finance month-end closing and tax compliance</field>
        <field name="privacy_visibility">employees</field>
        <field name="active">true</field>
    </record>

    <!-- Window Action for Finance Operations -->
    <record id="action_finance_operations" model="ir.actions.act_window">
        <field name="name">Active Operations</field>
        <field name="res_model">project.task</field>
        <field name="view_mode">kanban,tree,form,calendar,timeline,activity</field>
        <field name="domain">[('project_id', '=', ref('ipai_finance_ppm.project_finance_master'))]</field>
        <field name="context">{
            'search_default_my_tasks': 1,
            'default_project_id': ref('ipai_finance_ppm.project_finance_master')
        }</field>
        <field name="help" type="html">
            <p class="o_view_nocontent_smiling_face">
                Create your first finance operation task!
            </p>
        </field>
    </record>

    <!-- Update Menu Structure -->
    <menuitem id="menu_finance_operations" 
              name="Monthly Tasks" 
              parent="menu_finance_ppm_main"
              action="action_finance_operations"
              sequence="10"/>
</odoo>
```

### 5. Project Data Setup

**File:** `data/project_data.xml`
```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <!-- Finance Project Stages -->
    <record id="project_task_type_finance_todo" model="project.task.type">
        <field name="name">To Do</field>
        <field name="sequence">1</field>
    </record>
    
    <record id="project_task_type_finance_in_progress" model="project.task.type">
        <field name="name">In Progress</field>
        <field name="sequence">2</field>
    </record>
    
    <record id="project_task_type_finance_in_review" model="project.task.type">
        <field name="name">In Review</field>
        <field name="sequence">3</field>
    </record>
    
    <record id="project_task_type_finance_done" model="project.task.type">
        <field name="name">Done</field>
        <field name="sequence">4</field>
    </record>
</odoo>
```

## 🚀 Migration Strategy

### Option A: Keep Existing Data (Recommended)

**File:** `migrations/migrate_tasks.py`
```python
from odoo import api, SUPERUSER_ID

def migrate_finance_tasks(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    
    # Get finance master project
    finance_project = env.ref('ipai_finance_ppm.project_finance_master')
    
    # Migrate existing tasks from old model to project.task
    old_tasks = env['ipai_finance_task_template'].search([])
    
    for old_task in old_tasks:
        # Create new project task
        new_task = env['project.task'].create({
            'name': old_task.name,
            'project_id': finance_project.id,
            'finance_code': old_task.employee_code_id.code if old_task.employee_code_id else False,
            'finance_category': old_task.category,
            'prep_duration': old_task.prep_duration,
            'review_duration': old_task.review_duration,
            'approval_duration': old_task.approval_duration,
            'stage_id': env.ref('ipai_finance_ppm.project_task_type_finance_todo').id,
        })
    
    print(f"Migrated {len(old_tasks)} tasks to project module")
```

### Option B: Clean Install (No Migration)

**File:** `migrations/clean_install.py`
```python
from odoo import api, SUPERUSER_ID

def clean_install(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    
    # Drop old model tables if they exist
    cr.execute("DROP TABLE IF EXISTS ipai_finance_task_template CASCADE")
    
    print("Clean install completed - old model removed")
```

## 📊 Benefits of This Approach

### ✅ Standard Features Gained
- **Kanban Board**: Drag-and-drop task management
- **Subtasks**: Break down complex finance tasks
- **Chatter**: Communication and audit trail
- **Timeline View**: Resource scheduling with `web_timeline`
- **Calendar View**: Deadline tracking
- **Activity Planning**: Automatic scheduling
- **Reporting**: Built-in analytics and dashboards
- **Mobile Access**: Native mobile support

### ✅ Finance-Specific Features Retained
- **Finance Codes**: RIM, BOM, CKVC assignments
- **Approval Workflow**: Reviewer/Approver assignments
- **Finance Categories**: Month-end close categories
- **Duration Planning**: Prep/Review/Approval durations
- **Directory Integration**: Link to finance person records

## 🎯 Implementation Checklist

- [ ] Update `__manifest__.py` with dependencies
- [ ] Create `models/project_task.py` with custom fields
- [ ] Create `views/project_task_views.xml` with form extensions
- [ ] Create `views/finance_menus.xml` with new actions
- [ ] Create `data/project_data.xml` with project setup
- [ ] Choose migration strategy (A or B)
- [ ] Update module and test functionality
- [ ] Import WBS CSV into new project structure

## 🔄 Post-Implementation Steps

1. **Install/Update Module**: Apply the changes to your Odoo instance
2. **Import WBS Data**: Use the `finance_wbs.csv` to populate the new project
3. **Test Workflows**: Verify Kanban, Chatter, and approval workflows work
4. **Train Team**: Show team the new interface and features
5. **Monitor Usage**: Track adoption and make adjustments as needed

This implementation gives you the best of both worlds: all standard Odoo project management features with your Finance PPM specific requirements, ready for the November 2025 close process.
