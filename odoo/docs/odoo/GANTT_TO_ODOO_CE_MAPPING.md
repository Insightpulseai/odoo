# Gantt Chart to Odoo CE + OCA Mapping

**Source**: Project Management Gantt Chart (screenshot)
**Target**: Odoo 18 CE + OCA/project modules
**Date**: 2026-01-20

---

## 1. Feature Mapping

| Gantt Feature | Odoo CE/OCA Solution | Module |
|---------------|---------------------|--------|
| **Timeline View** | `project_timeline` | OCA/project |
| **Task Hierarchy** | Native `parent_id` on `project.task` | CE core |
| **Progress %** | `progress` field (computed or manual) | CE core + extension |
| **Start/End Dates** | `date_start`, `date_deadline` | CE core |
| **Task Dependencies** | `project_task_dependency` | OCA/project |
| **Color Coding** | Stage colors or custom `color` field | CE core |
| **Export** | `report_xlsx` | OCA/reporting-engine |

---

## 2. Screenshot Analysis

### Tasks Identified

| Task | Parent | Progress | Start | End | Color |
|------|--------|----------|-------|-----|-------|
| Project Planning | - | 100% | Dec 29 | Dec 31 | Cyan |
| Research & Analysis | Project Planning | 100% | Dec 29 | Dec 30 | Cyan |
| Requirements Gathering | Project Planning | 100% | Dec 30 | Dec 31 | Cyan |
| Design Phase | - | 75% | Jan 1 | Jan 9 | Green |
| UI/UX Design | Design Phase | 90% | Jan 2 | Jan 6 | Teal |
| System Architecture | Design Phase | 60% | Jan 5 | Jan 9 | Yellow |
| Development | - | 40% | Jan 7 | Jan 15 | Orange |
| Testing | - | 0% | Jan 14 | Jan 18+ | Red |

### Hierarchy Structure

```
Project Planning (100%)
├── Research & Analysis (100%)
└── Requirements Gathering (100%)

Design Phase (75%)
├── UI/UX Design (90%)
└── System Architecture (60%)

Development (40%)
└── (subtasks not shown)

Testing (0%)
└── (subtasks not shown)
```

---

## 3. Required OCA Modules

### From oca.lock.json (already included)

```json
"project": {
  "modules": [
    "project_wbs",              // Work Breakdown Structure
    "project_template",         // Project templates
    "project_task_template",    // Task templates
    "project_task_dependency",  // Task dependencies (Finish-to-Start, etc.)
    "project_task_recurring",   // Recurring tasks
    "project_stage_closed",     // Closed stage handling
    "project_timeline",         // Timeline/Gantt-like view
    "project_task_default_stage", // Default stage per project
    "project_task_code"         // Task reference codes
  ]
}
```

### Additional Recommended

```bash
# Add to oca.lock.json if not present
"web_timeline" from OCA/web  # Generic timeline widget
```

---

## 4. Implementation: Task Data Seed

### XML Seed File

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo noupdate="0">
    <!-- Project: Sample Gantt Project -->
    <record id="project_gantt_sample" model="project.project">
        <field name="name">Sample Project (Gantt Demo)</field>
        <field name="allow_subtasks">True</field>
    </record>

    <!-- Phase 1: Project Planning -->
    <record id="task_project_planning" model="project.task">
        <field name="name">Project Planning</field>
        <field name="project_id" ref="project_gantt_sample"/>
        <field name="date_start">2025-12-29</field>
        <field name="date_deadline">2025-12-31</field>
        <field name="progress">100</field>
        <field name="color">4</field><!-- Cyan -->
    </record>

    <record id="task_research_analysis" model="project.task">
        <field name="name">Research &amp; Analysis</field>
        <field name="project_id" ref="project_gantt_sample"/>
        <field name="parent_id" ref="task_project_planning"/>
        <field name="date_start">2025-12-29</field>
        <field name="date_deadline">2025-12-30</field>
        <field name="progress">100</field>
        <field name="color">4</field>
    </record>

    <record id="task_requirements_gathering" model="project.task">
        <field name="name">Requirements Gathering</field>
        <field name="project_id" ref="project_gantt_sample"/>
        <field name="parent_id" ref="task_project_planning"/>
        <field name="date_start">2025-12-30</field>
        <field name="date_deadline">2025-12-31</field>
        <field name="progress">100</field>
        <field name="color">4</field>
    </record>

    <!-- Phase 2: Design Phase -->
    <record id="task_design_phase" model="project.task">
        <field name="name">Design Phase</field>
        <field name="project_id" ref="project_gantt_sample"/>
        <field name="date_start">2026-01-01</field>
        <field name="date_deadline">2026-01-09</field>
        <field name="progress">75</field>
        <field name="color">10</field><!-- Green -->
    </record>

    <record id="task_uiux_design" model="project.task">
        <field name="name">UI/UX Design</field>
        <field name="project_id" ref="project_gantt_sample"/>
        <field name="parent_id" ref="task_design_phase"/>
        <field name="date_start">2026-01-02</field>
        <field name="date_deadline">2026-01-06</field>
        <field name="progress">90</field>
        <field name="color">8</field><!-- Teal -->
    </record>

    <record id="task_system_architecture" model="project.task">
        <field name="name">System Architecture</field>
        <field name="project_id" ref="project_gantt_sample"/>
        <field name="parent_id" ref="task_design_phase"/>
        <field name="date_start">2026-01-05</field>
        <field name="date_deadline">2026-01-09</field>
        <field name="progress">60</field>
        <field name="color">3</field><!-- Yellow -->
    </record>

    <!-- Phase 3: Development -->
    <record id="task_development" model="project.task">
        <field name="name">Development</field>
        <field name="project_id" ref="project_gantt_sample"/>
        <field name="date_start">2026-01-07</field>
        <field name="date_deadline">2026-01-15</field>
        <field name="progress">40</field>
        <field name="color">2</field><!-- Orange -->
    </record>

    <!-- Phase 4: Testing -->
    <record id="task_testing" model="project.task">
        <field name="name">Testing</field>
        <field name="project_id" ref="project_gantt_sample"/>
        <field name="date_start">2026-01-14</field>
        <field name="date_deadline">2026-01-20</field>
        <field name="progress">0</field>
        <field name="color">1</field><!-- Red -->
    </record>

    <!-- Task Dependencies (if project_task_dependency installed) -->
    <record id="dep_design_after_planning" model="project.task.dependency">
        <field name="task_id" ref="task_design_phase"/>
        <field name="depends_on_id" ref="task_project_planning"/>
        <field name="dependency_type">finish_to_start</field>
    </record>

    <record id="dep_dev_after_design" model="project.task.dependency">
        <field name="task_id" ref="task_development"/>
        <field name="depends_on_id" ref="task_design_phase"/>
        <field name="dependency_type">finish_to_start</field>
    </record>

    <record id="dep_test_after_dev" model="project.task.dependency">
        <field name="task_id" ref="task_testing"/>
        <field name="depends_on_id" ref="task_development"/>
        <field name="dependency_type">finish_to_start</field>
    </record>
</odoo>
```

---

## 5. Model Extension for Progress

The CE `project.task` has `kanban_state` but not `progress`. Add it:

```python
# models/project_task_progress.py
from odoo import api, fields, models

class ProjectTask(models.Model):
    _inherit = "project.task"

    progress = fields.Float(
        string="Progress (%)",
        default=0.0,
        help="Task completion percentage (0-100)",
    )
    date_start = fields.Date(
        string="Start Date",
        help="Planned start date for the task",
    )
    # Note: date_deadline already exists in CE

    @api.depends('child_ids.progress')
    def _compute_progress_from_children(self):
        """Auto-compute parent progress from children (optional)."""
        for task in self:
            children = task.child_ids.filtered(lambda t: t.active)
            if children:
                task.progress = sum(children.mapped('progress')) / len(children)
```

---

## 6. Timeline View Definition

### View XML (for project_timeline)

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <!-- Timeline View for Tasks -->
    <record id="view_project_task_timeline" model="ir.ui.view">
        <field name="name">project.task.timeline</field>
        <field name="model">project.task</field>
        <field name="arch" type="xml">
            <timeline
                date_start="date_start"
                date_stop="date_deadline"
                default_group_by="project_id"
                event_open_popup="true"
                colors="#ec7063:progress == 0;#f39c12:progress &lt; 50;#27ae60:progress &gt;= 50;#2ecc71:progress == 100">
                <field name="name"/>
                <field name="user_ids"/>
                <field name="progress"/>
                <field name="stage_id"/>
                <templates>
                    <t t-name="timeline-item">
                        <div>
                            <strong><t t-esc="record.name"/></strong>
                            <span class="badge"><t t-esc="record.progress"/>%</span>
                        </div>
                    </t>
                </templates>
            </timeline>
        </field>
    </record>

    <!-- Add timeline to project task action -->
    <record id="project.action_view_task" model="ir.actions.act_window">
        <field name="view_mode">kanban,tree,form,calendar,pivot,graph,timeline</field>
    </record>
</odoo>
```

---

## 7. Color Mapping

| Gantt Color | Odoo Color Index | Usage |
|-------------|-----------------|-------|
| Cyan | 4 | Completed phases |
| Green | 10 | In progress (>50%) |
| Teal | 8 | Near completion |
| Yellow | 3 | Warning/attention |
| Orange | 2 | In progress (<50%) |
| Red | 1 | Not started / blocked |

---

## 8. CE vs EE Comparison

| Feature | Odoo EE | Odoo CE + OCA |
|---------|---------|---------------|
| Gantt View | Native `<gantt>` | `project_timeline` (timeline) |
| Task Dependencies | Native | `project_task_dependency` |
| Progress Bar | Native | Custom field extension |
| WBS | Native (limited) | `project_wbs` |
| Critical Path | Native | Not available (manual) |
| Resource Leveling | Native | Not available |
| Drag & Drop | Full | Limited in timeline |

**Verdict**: CE + OCA covers **80%** of typical Gantt needs. Missing: critical path analysis, resource leveling.

---

## 9. Installation Commands

```bash
# Ensure OCA/project is in addons path
git submodule add -b 18.0 https://github.com/OCA/project.git external-src/project

# Install required modules
docker exec -it odoo-core odoo -d odoo_core \
  -i project_timeline,project_task_dependency,project_wbs \
  --stop-after-init
```

---

## 10. Alternative: Embedded External Gantt

If OCA timeline is insufficient, embed an external Gantt library:

| Library | License | Integration |
|---------|---------|-------------|
| DHTMLX Gantt | GPL/Commercial | iframe + REST API |
| Frappe Gantt | MIT | Web component |
| vis-timeline | MIT/Apache | OWL widget |

```javascript
// Example: Frappe Gantt integration
import Gantt from 'frappe-gantt';

const tasks = await fetch('/api/project.task/timeline_data');
new Gantt("#gantt", tasks, {
    view_mode: 'Week',
    on_click: task => window.location = `/web#id=${task.id}&model=project.task`,
});
```

---

**Summary**: Your screenshot maps directly to Odoo 18 CE + OCA using `project_timeline`, `project_task_dependency`, and a custom `progress` field. The OCA modules are already in your `oca.lock.json`.
