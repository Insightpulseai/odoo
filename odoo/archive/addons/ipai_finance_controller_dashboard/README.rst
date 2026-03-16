========================================
IPAI Finance Controller Dashboard
========================================

.. |badge1| image:: https://img.shields.io/badge/maturity-Beta-yellow.png
    :target: https://odoo-community.org/page/development-status
    :alt: Beta
.. |badge2| image:: https://img.shields.io/badge/licence-AGPL--3-blue.png
    :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
    :alt: License: AGPL-3

|badge1| |badge2|

Finance Controller Dashboard with 6 ECharts Visualizations
===========================================================

Comprehensive Finance Controller Dashboard providing real-time KPI monitoring and task visualization for Month-End Close operations.

**Features**:

* **6 Interactive ECharts Visualizations**:

  1. **KPI Gauges**: 3 gauge charts (% on time, % reconciled, % filed before deadline) + operational velocity combo chart
  2. **Calendar Heatmap**: Workload density visualization with BIR/BOOK LOCK milestone overlays
  3. **WBS Tree**: Collapsible task hierarchy tree (Phase → Task → Subtask)
  4. **Gantt Chart**: Task execution timeline with custom render function for bars
  5. **RACI Sunburst**: Multi-level responsibility distribution by cluster, owner, and role
  6. **Dependency Graph**: Force-directed task prerequisite network visualization

* **Employee Context Filtering**: Support for 8 employees (RIM, CKVC, BOM, JPAL, JLI, JAP, LAS, RMQB)
* **Daily KPI Snapshots**: Automated cron jobs at 9 AM PHT for all employees
* **Real-time Data Refresh**: AJAX-based data loading with refresh button
* **Print-Friendly Export**: Professional print layout with hidden controls
* **Responsive Design**: Mobile-first design with adaptive layouts
* **n8n Integration**: Optional workflow automation for KPI threshold alerts

**Table of contents**

.. contents::
   :local:

Installation
============

To install this module, you need to:

#. Clone the repository into your Odoo addons directory
#. Ensure dependencies are installed: ``ipai_finance_ppm_tdi``, ``ipai_finance_monthly_closing``, ``ipai_finance_ap_aging``
#. Update the module list in Odoo
#. Install the module from Apps menu

Configuration
=============

After installation, configure the following:

**1. Employee Codes**

Verify employee codes in HR module match the following:

* RIM - Finance Manager
* CKVC - Finance Supervisor
* BOM - Senior Finance Manager
* JPAL - Finance Director
* JLI - AP Specialist
* JAP - AR Specialist
* LAS - Payroll Specialist
* RMQB - Tax Specialist

**2. Cron Job Schedule**

The cron jobs run daily at 9 AM PHT (1 AM UTC). To modify:

* Navigate to: Settings → Technical → Automation → Scheduled Actions
* Find: "Finance KPI Snapshot [EMPLOYEE] - Daily (9 AM PHT)"
* Adjust schedule as needed

**3. LogFrame Indicators (Optional)**

For accurate BIR filing rate KPIs:

* Navigate to: Finance PPM → LogFrame Indicators
* Ensure indicator exists: "BIR Forms Filed On Time" with frequency = 'monthly'

Usage
=====

**Viewing the Dashboard**

#. Navigate to: Finance PPM → Finance Controller Dashboard
#. Or access directly: ``/ipai/finance/controller/dashboard?employee_code=RIM``

**Employee Filter**

Use the dropdown in the dashboard header to switch between employees:

* Automatically reloads dashboard with selected employee context
* Filters all 6 visualizations simultaneously

**Dashboard Controls**

* **Employee Filter**: Dropdown to switch employee context
* **Refresh Data**: Reload all visualizations with latest data
* **Print Report**: Generate print-friendly PDF export

**Interpreting Visualizations**

**1. KPI Gauges**:

* Green zone (>85%): Excellent performance
* Yellow zone (70-85%): Acceptable performance
* Red zone (<70%): Requires attention

**2. Calendar Heatmap**:

* Color intensity: Task workload density (green = light, red = heavy)
* Red pins: BIR filing deadlines
* Orange diamonds: BOOK LOCK dates (end of month)

**3. WBS Tree**:

* Click nodes to expand/collapse subtasks
* Color indicates task status (green=completed, orange=in_progress, blue=pending)

**4. Gantt Chart**:

* Horizontal bars show task duration (start → end date)
* Color indicates phase classification
* Hover for task details (owner, phase, dates)

**5. RACI Sunburst**:

* Inner ring: Cluster classification (Phase 1, 2, 3, etc.)
* Middle ring: Task owners (RIM, CKVC, BOM, etc.)
* Outer ring: RACI roles (Responsible, Accountable, Consulted, Informed)

**6. Dependency Graph**:

* Nodes: Individual tasks
* Arrows: Parent → Child relationships (prerequisites)
* Drag nodes to rearrange layout
* Zoom and pan for navigation

Technical Details
=================

**Database Queries**

The module uses optimized SQL queries with the following patterns:

* Aging bucket calculations with CASE statements
* Hierarchical tree queries using parent_id relationships
* Temporal filtering for rolling windows (7 days, 30 days, 90 days)
* Aggregation by cluster, owner, RACI role

**ECharts Configuration**

All visualizations use Apache ECharts 5.4.3:

* CDN: ``https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js``
* Chart types: gauge, heatmap, tree, custom (Gantt), sunburst, graph (force-directed)
* Responsive resize on viewport changes
* Print-friendly CSS with hidden controls

**API Endpoints**

* ``/ipai/finance/controller/dashboard`` - Main dashboard page (HTTP)
* ``/ipai/finance/controller/api/kpi_gauges`` - KPI gauge data (JSON)
* ``/ipai/finance/controller/api/calendar_heatmap`` - Calendar heatmap data (JSON)
* ``/ipai/finance/controller/api/wbs_tree`` - WBS tree data (JSON)
* ``/ipai/finance/controller/api/gantt`` - Gantt chart data (JSON)
* ``/ipai/finance/controller/api/raci_sunburst`` - RACI sunburst data (JSON)
* ``/ipai/finance/controller/api/dependency_graph`` - Dependency graph data (JSON)

**Data Models**

* ``finance.controller.kpi`` - KPI computation and snapshot storage
* ``ipai.finance.monthly.close`` - Month-end close tasks (dependency)
* ``finance.ppm.logframe`` - LogFrame indicators (dependency)

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/jgtolentino/odoo-ce/issues>`_.
In case of trouble, please check there if your issue has already been reported.

Credits
=======

Authors
~~~~~~~

* InsightPulse AI

Contributors
~~~~~~~~~~~~

* Jake Tolentino <jgtolentino@insightpulseai.net>

Maintainers
~~~~~~~~~~~

This module is maintained by InsightPulse AI.

.. image:: https://insightpulseai.net/logo.png
   :alt: InsightPulse AI
   :target: https://insightpulseai.net

This module is part of the `odoo-ce <https://github.com/jgtolentino/odoo-ce>`_ project on GitHub.

You are welcome to contribute.
