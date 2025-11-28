# Superset PPM Analytics Guide
## Strategic Portfolio Management Dashboards

This guide provides specialized SQL queries and configuration steps to connect Superset to your Odoo PPM database for executive-level portfolio analytics.

---

## 🗄️ Database Connection Configuration

### Odoo PostgreSQL Connection Details
```yaml
Host: 159.223.75.148
Port: 5432
Database: odoo
Username: odoo
Password: [Your Odoo Database Password]
SSL Mode: prefer
```

### Superset Database Setup
1. **Navigate to Data → Databases**
2. **Click "+ Database"**
3. **Select PostgreSQL**
4. **Configure Connection:**
   ```sql
   postgresql://odoo:[PASSWORD]@159.223.75.148:5432/odoo
   ```
5. **Test Connection** and save

---

## 📊 Specialized SQL Queries for PPM Analytics

### Query 1: Portfolio Health Dashboard
**Purpose**: Executive view of project health across the portfolio

```sql
SELECT 
    pp.name as project_name,
    pp.health_status,
    COUNT(DISTINCT pt.id) as total_tasks,
    COUNT(DISTINCT CASE WHEN pt.date_deadline < CURRENT_DATE THEN pt.id END) as overdue_tasks,
    ROUND(pp.total_planned_cost, 2) as planned_budget,
    ROUND(pp.total_actual_cost, 2) as actual_cost,
    CASE 
        WHEN pp.total_planned_cost > 0 
        THEN ROUND((pp.total_actual_cost / pp.total_planned_cost) * 100, 2)
        ELSE 0 
    END as budget_utilization_percent,
    pp.date_start,
    pp.date,
    u.name as project_manager
FROM project_project pp
LEFT JOIN project_task pt ON pp.id = pt.project_id
LEFT JOIN res_users u ON pp.user_id = u.id
WHERE pp.active = true
GROUP BY pp.id, pp.name, pp.health_status, pp.total_planned_cost, 
         pp.total_actual_cost, pp.date_start, pp.date, u.name
ORDER BY pp.health_status, pp.name;
```

**Recommended Visualization**: **Treemap** or **Grid View**
- **Color by**: health_status (Red/Amber/Green)
- **Size by**: total_planned_cost
- **Labels**: project_name, budget_utilization_percent

---

### Query 2: WBS Depth Analysis
**Purpose**: Understand project structure complexity and task hierarchy

```sql
WITH RECURSIVE task_hierarchy AS (
    -- Base case: root tasks (no parent)
    SELECT 
        id,
        name,
        parent_id,
        project_id,
        wbs_code,
        1 as depth,
        name as full_path
    FROM project_task 
    WHERE parent_id IS NULL
    
    UNION ALL
    
    -- Recursive case: child tasks
    SELECT 
        pt.id,
        pt.name,
        pt.parent_id,
        pt.project_id,
        pt.wbs_code,
        th.depth + 1 as depth,
        th.full_path || ' → ' || pt.name as full_path
    FROM project_task pt
    INNER JOIN task_hierarchy th ON pt.parent_id = th.id
)
SELECT 
    pp.name as project_name,
    th.depth,
    COUNT(*) as task_count,
    MAX(th.depth) OVER (PARTITION BY th.project_id) as max_depth,
    ROUND(AVG(th.depth) OVER (PARTITION BY th.project_id), 2) as avg_depth
FROM task_hierarchy th
LEFT JOIN project_project pp ON th.project_id = pp.id
WHERE pp.active = true
GROUP BY pp.name, th.depth, th.project_id
ORDER BY pp.name, th.depth;
```

**Recommended Visualization**: **Sunburst Chart** or **Bar Chart**
- **Inner rings**: project_name
- **Outer rings**: depth levels
- **Size**: task_count

---

### Query 3: Budget vs. Actuals Waterline
**Purpose**: Financial compliance and budget tracking

```sql
SELECT 
    pp.name as project_name,
    pp.health_status,
    ROUND(pp.total_planned_cost, 2) as planned_budget,
    ROUND(pp.total_actual_cost, 2) as actual_cost,
    ROUND(pp.total_planned_cost - pp.total_actual_cost, 2) as budget_variance,
    CASE 
        WHEN pp.total_planned_cost > 0 
        THEN ROUND(((pp.total_planned_cost - pp.total_actual_cost) / pp.total_planned_cost) * 100, 2)
        ELSE 0 
    END as variance_percent,
    CASE 
        WHEN (pp.total_planned_cost - pp.total_actual_cost) < 0 THEN 'Over Budget'
        WHEN (pp.total_planned_cost - pp.total_actual_cost) > (pp.total_planned_cost * 0.1) THEN 'Under Budget'
        ELSE 'On Budget'
    END as budget_status
FROM project_project pp
WHERE pp.active = true 
  AND pp.total_planned_cost > 0
ORDER BY budget_variance DESC;
```

**Recommended Visualization**: **Waterfall Chart** or **Bullet Chart**
- **X-axis**: project_name
- **Y-axis**: planned_budget, actual_cost
- **Color**: budget_status

---

### Query 4: Resource Allocation & Time Investment
**Purpose**: Track time investment vs. strategic goals

```sql
SELECT 
    pp.name as project_name,
    u.name as employee_name,
    COUNT(DISTINCT aal.id) as timesheet_entries,
    ROUND(SUM(aal.unit_amount), 2) as total_hours,
    ROUND(AVG(aal.unit_amount), 2) as avg_hours_per_entry,
    MIN(aal.date) as first_entry,
    MAX(aal.date) as last_entry
FROM account_analytic_line aal
LEFT JOIN project_task pt ON aal.task_id = pt.id
LEFT JOIN project_project pp ON pt.project_id = pp.id
LEFT JOIN res_users u ON aal.user_id = u.id
WHERE pp.active = true
  AND aal.unit_amount > 0
GROUP BY pp.name, u.name
ORDER BY total_hours DESC;
```

**Recommended Visualization**: **Heatmap** or **Stacked Bar Chart**
- **X-axis**: project_name
- **Y-axis**: employee_name
- **Color intensity**: total_hours

---

### Query 5: Month-End Close Progress
**Purpose**: Track November 2025 close progress across agencies

```sql
SELECT 
    pt.name as task_name,
    pt.stage_id,
    ps.name as stage_name,
    u.name as assigned_to,
    pt.date_deadline,
    pt.date_start,
    CASE 
        WHEN pt.date_deadline < CURRENT_DATE THEN 'Overdue'
        WHEN pt.date_deadline <= CURRENT_DATE + INTERVAL '2 days' THEN 'Due Soon'
        ELSE 'On Track'
    END as deadline_status,
    pp.name as project_name,
    pt.wbs_code
FROM project_task pt
LEFT JOIN project_task_type ps ON pt.stage_id = ps.id
LEFT JOIN res_users u ON pt.user_id = u.id
LEFT JOIN project_project pp ON pt.project_id = pp.id
WHERE pp.name LIKE '%November 2025%'
   OR pp.name LIKE '%Month-End%'
   OR pp.name LIKE '%BIR Tax%'
ORDER BY pt.date_deadline, pt.wbs_code;
```

**Recommended Visualization**: **Gantt Chart** or **Progress Bars**
- **Tasks**: task_name with wbs_code
- **Timeline**: date_start to date_deadline
- **Status colors**: deadline_status

---

## 🎯 Dashboard Creation Steps

### Step 1: Create Individual Charts
1. **Navigate to Charts → + Chart**
2. **Select your Odoo database**
3. **Choose "Custom SQL" as dataset**
4. **Paste one of the SQL queries above**
5. **Configure visualization type**
6. **Save chart with descriptive name**

### Step 2: Build Executive Dashboard
1. **Navigate to Dashboards → + Dashboard**
2. **Name: "Strategic Portfolio Command Center"**
3. **Add charts using drag-and-drop**
4. **Organize layout:**
   - **Top Row**: Portfolio Health + Budget Waterline
   - **Middle Row**: WBS Depth + Resource Allocation
   - **Bottom Row**: Month-End Progress

### Step 3: Configure Dashboard Settings
1. **Enable auto-refresh**: 5-minute intervals
2. **Set filters**: Date range, project selection
3. **Configure permissions**: Executive team access
4. **Enable embedding** for Odoo integration

---

## 🔗 Odoo Integration Configuration

### Update Finance Command Center Action
1. **Log in to Odoo as Administrator**
2. **Go to Settings → Technical → Actions → Window Actions**
3. **Find "Finance Command Center" action**
4. **Update target URL with your Superset dashboard link:**
   ```
   https://superset.insightpulseai.net/superset/dashboard/[YOUR_DASHBOARD_ID]/?standalone=true
   ```
5. **Save changes**

### Test Integration
1. **Navigate to Finance PPM module**
2. **Click "Analytics" or "Command Center" menu**
3. **Verify Superset dashboard loads in embedded view**
4. **Test filter interactions**

---

## 📈 Executive Reporting Metrics

### Key Performance Indicators (KPIs)
1. **Portfolio Health Distribution**
   - Target: ≥80% Green, ≤10% Red
2. **Budget Compliance**
   - Target: ≥90% projects within 10% budget variance
3. **WBS Structure Efficiency**
   - Target: Average depth ≤3 levels
4. **Resource Utilization**
   - Target: ≤10% overallocation across projects

### Alert Thresholds
- **Red Projects**: Immediate executive review required
- **Budget Overruns >15%**: Finance team escalation
- **Overdue Tasks >5%**: Project manager notification
- **Resource Overallocation >20%**: Resource manager alert

---

## 🛠️ Troubleshooting

### Common Issues & Solutions

**Connection Refused**
- Verify PostgreSQL is running on 159.223.75.148:5432
- Check firewall rules allow Superset connection
- Confirm database credentials

**No Data in Charts**
- Verify project data exists in Odoo
- Check date filters in queries
- Confirm user has access to projects

**Slow Query Performance**
- Add indexes on frequently queried columns
- Consider materialized views for complex aggregations
- Use query caching in Superset

**Embedding Issues**
- Ensure Superset dashboard has "embedded" permissions
- Verify CORS settings allow Odoo domain
- Check iframe security headers

---

## 🚀 Next Steps

1. **Immediate**: Create the Portfolio Health dashboard
2. **Short-term**: Configure budget vs. actuals tracking
3. **Medium-term**: Set up automated executive reporting
4. **Long-term**: Implement predictive analytics for project risks

**Success Metrics**:
- Executive team adoption of dashboard
- Reduction in manual reporting time
- Improved project decision-making speed
- Increased portfolio health scores

---

**Last Updated**: November 24, 2025  
**Odoo Version**: 18.0  
**Superset Version**: 3.0+
