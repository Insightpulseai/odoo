# Finance PPM Dashboard Implementation Guide for Odoo CE + OCA

## 🎯 OCA-Based Dashboard Views for Project Management

Since you're on **Odoo Community Edition (CE)** with OCA modules, here are the specific implementations using OCA alternatives for Enterprise features.

## 📊 1. Timeline View (Flight Gantt Replacement)

### OCA Solution: `web_timeline` Module

**Goal:** Visualize the overlap of RIM, BOM, and JPAL's tasks over the 8-day closing period.

### Implementation Steps:

1. **Install `web_timeline` Module**
   ```bash
   # Download from OCA/web repository
   git clone https://github.com/OCA/web.git
   cp -r web/web_timeline /path/to/your/custom-addons/
   ```

2. **Add Required Fields to Your Model**
   ```python
   # In your ipai_finance_task_template model
   date_start = fields.Date(string='Start Date')
   date_deadline = fields.Date(string='Deadline')
   user_id = fields.Many2one('res.users', string='Assigned User')
   stage_id = fields.Selection([
       ('todo', 'To Do'),
       ('in_progress', 'In Progress'),
       ('in_review', 'In Review'),
       ('done', 'Done')
   ], default='todo', string='Stage')
   ```

3. **Create Timeline View XML**
   ```xml
   <record id="view_finance_ppm_timeline" model="ir.ui.view">
       <field name="name">finance.ppm.timeline</field>
       <field name="model">ipai_finance_task_template</field>
       <field name="arch" type="xml">
           <timeline date_start="date_start"
                     date_stop="date_deadline"
                     default_group_by="user_id"
                     event_open_popup="true"
                     colors="#ec7063:stage_id == 'todo'; #58d68d:stage_id == 'done';">
               <field name="name"/>
               <field name="user_id"/>
               <field name="stage_id"/>
           </timeline>
       </field>
   </record>
   ```

4. **Update Window Action**
   ```xml
   <record id="action_finance_ppm_tasks" model="ir.actions.act_window">
       <field name="name">Monthly Tasks</field>
       <field name="res_model">ipai_finance_task_template</field>
       <field name="view_mode">tree,form,kanban,timeline,calendar</field>
   </record>
   ```

**Result:** Interactive timeline showing who is busy when, with drag-and-drop capability.

## 📈 2. Dashboard Command Center

### CE Solution: Standard `board` Module

**Goal:** Create a command center for status updates.

### Implementation Steps:

1. **Ensure `board` Module is Installed**
   - This is standard in CE
   - Go to Apps → Search "board" → Install if not already

2. **Create Graph Views**
   ```xml
   <!-- Workload by Owner Chart -->
   <record id="view_finance_ppm_graph_workload" model="ir.ui.view">
       <field name="name">finance.ppm.graph.workload</field>
       <field name="model">ipai_finance_task_template</field>
       <field name="arch" type="xml">
           <graph type="bar">
               <field name="user_id" type="row"/>
               <field name="stage_id" type="column"/>
               <field name="id" type="measure"/>
           </graph>
       </field>
   </record>

   <!-- Progress by Category Chart -->
   <record id="view_finance_ppm_graph_progress" model="ir.ui.view">
       <field name="name">finance.ppm.graph.progress</field>
       <field name="model">ipai_finance_task_template</field>
       <field name="arch" type="xml">
           <graph type="pie">
               <field name="category" type="row"/>
               <field name="stage_id" type="column"/>
               <field name="id" type="measure"/>
           </graph>
       </field>
   </record>
   ```

3. **Add Views to Dashboard**
   - Navigate to your Graph view
   - Click **Favorites → Add to my Dashboard**
   - Repeat for other views

### Advanced Option: `ks_dashboard_ninja`
For speedometer/gauge visuals, install this third-party module:
```bash
git clone https://github.com/Kaushalkhadaya/ks_dashboard_ninja.git
```

## 📅 3. Calendar View (Deadline Density)

### CE Solution: Standard Calendar View

**Goal:** See deadline density and upcoming due dates.

### Implementation:

1. **Create Calendar View**
   ```xml
   <record id="view_finance_ppm_calendar" model="ir.ui.view">
       <field name="name">finance.ppm.calendar</field>
       <field name="model">ipai_finance_task_template</field>
       <field name="arch" type="xml">
           <calendar date_start="date_start"
                     date_stop="date_deadline"
                     color="user_id"
                     mode="month">
               <field name="name"/>
               <field name="user_id"/>
               <field name="stage_id"/>
           </calendar>
       </field>
   </record>
   ```

## 🎯 4. Kanban Board (Project Management)

### CE Solution: Standard Kanban View

**Goal:** Trello-style task management.

### Implementation:

```xml
<record id="view_finance_ppm_kanban" model="ir.ui.view">
    <field name="name">finance.ppm.kanban</field>
    <field name="model">ipai_finance_task_template</field>
    <field name="arch" type="xml">
        <kanban default_group_by="stage_id">
            <field name="name"/>
            <field name="user_id"/>
            <field name="category"/>
            <field name="stage_id"/>
            <templates>
                <t t-name="kanban-box">
                    <div class="oe_kanban_global_click">
                        <div class="o_kanban_record_title">
                            <field name="name"/>
                        </div>
                        <div class="o_kanban_record_bottom">
                            <div>Owner: <field name="user_id"/></div>
                            <div>Category: <field name="category"/></div>
                            <div>Stage: <field name="stage_id"/></div>
                        </div>
                    </div>
                </t>
            </templates>
        </kanban>
    </field>
</record>
```

## 🔧 Required Field Additions

To make all views functional, add these fields to your model:

```python
class IpaiFinanceTaskTemplate(models.Model):
    _name = 'ipai_finance_task_template'

    # Existing fields
    name = fields.Char(string='Task Name')
    category = fields.Char(string='Category')
    employee_code_id = fields.Many2one('ipai_finance_person', string='Employee')

    # New fields for views
    date_start = fields.Date(string='Start Date', default=fields.Date.today)
    date_deadline = fields.Date(string='Deadline')
    user_id = fields.Many2one('res.users', string='Assigned User')
    stage_id = fields.Selection([
        ('todo', 'To Do'),
        ('in_progress', 'In Progress'),
        ('in_review', 'In Review'),
        ('done', 'Done')
    ], default='todo', string='Stage')
```

## 🚀 Immediate Action Plan (CE Version)

### Step 1: Install Required Modules
1. **`web_timeline`** - For timeline/Gantt view
2. **`board`** - For dashboard (usually pre-installed)
3. **Optional:** `ks_dashboard_ninja` - For advanced visuals

### Step 2: Add Required Fields
Update your model with date_start, date_deadline, user_id, and stage_id fields.

### Step 3: Create Views
Add the XML views for:
- Timeline
- Calendar
- Kanban
- Graph (Workload & Progress)

### Step 4: Update Window Action
Modify your action to include all view modes:
```xml
<field name="view_mode">tree,form,kanban,timeline,calendar,graph</field>
```

### Step 5: Import Data
Use the `finance_wbs.csv` with the new fields populated.

## 📊 OCA Architecture Summary

| PMP Goal | Odoo CE + OCA Tool | Implementation |
|----------|-------------------|----------------|
| **Schedule/Gantt** | `web_timeline` | Interactive timeline grouped by resource |
| **Status Reports** | `board` + Graph views | Dashboard with workload charts |
| **Deadline Tracking** | Standard Calendar | Monthly view of deadlines |
| **Task Management** | Standard Kanban | Trello-style board |
| **Mobile Access** | `web_responsive` | Modern mobile interface |

## 🎯 Success Metrics

- **Timeline View:** Visualize RIM/BOM/JPAL workload overlap
- **Dashboard:** Monitor completion percentage and bottlenecks
- **Calendar:** Track BIR deadlines and compliance risks
- **Kanban:** Daily task management and status updates

This OCA-based implementation gives you Enterprise-level project management capabilities in Community Edition, perfectly suited for your November 2025 close process.
