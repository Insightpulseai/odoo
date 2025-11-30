# Superset Setup Guide - Why Datasets Page is Empty

## Current Status

Your Superset instance is correctly set up:
- ✅ **Superset is running** at https://superset.insightpulseai.net
- ✅ **Metadata stored in Supabase** (user accounts, logs, etc.)
- ⚠️ **No data sources configured yet** (this is why Datasets page is empty)

## Why the Datasets Page Shows Nothing

```
┌─────────────────────────────────────────────────────────┐
│              Superset Datasets Page (Empty)              │
│  "No datasets found. Add a dataset to get started"      │
└─────────────────────────────────────────────────────────┘
                           ↑
                    Why is this empty?
                           ↓
┌─────────────────────────────────────────────────────────┐
│         Missing: Data Source Configuration               │
│  You haven't told Superset WHICH database to query      │
└─────────────────────────────────────────────────────────┘
```

**Analogy**:
- Superset stores its own data (users, settings) in Supabase ✅
- But you haven't told Superset to also **query** Supabase for **your data** ❌

**Solution**: Add Supabase as a data source in Superset UI

---

## Step-by-Step Setup (5 Minutes)

### Step 1: Login to Superset

1. Open: https://superset.insightpulseai.net/login/
2. Username: `admin`
3. Password: `AdminPassword123!`
4. Click **Sign In**

### Step 2: Add Database Connection

1. **Navigate to Database Connections**:
   ```
   Top menu → Settings → Database Connections
   ```

2. **Click "+ Database" button** (top right)

3. **Select PostgreSQL** from the database type list

4. **Configure Connection**:

   **Display Name**:
   ```
   Supabase Production
   ```

   **SQLAlchemy URI**:
   ```
   postgresql://postgres.spdtwktxdalcfigzeqrz:SHWYXDMFAwXI1drT@aws-1-us-east-1.pooler.supabase.com:6543/postgres?sslmode=require
   ```

5. **Test Connection**:
   - Click **Test Connection** button
   - Should show: ✅ "Connection looks good!"

6. **Save**:
   - Click **Connect** button

### Step 3: Add Your First Dataset

1. **Navigate to Datasets**:
   ```
   Top menu → Datasets
   ```

2. **Click "+ Dataset" button** (top right)

3. **Select Table**:
   - **Database**: Supabase Production
   - **Schema**: public
   - **Table**: Choose any table (examples below)

4. **Click "Add"**

### Step 4: Create Your First Chart

1. **Click on the dataset** you just added
2. **Click "Create Chart"** button
3. **Choose visualization type** (Bar Chart, Line Chart, Table, etc.)
4. **Configure and Save**

---

## Recommended Datasets to Add

Based on your odoo-ce project, here are useful tables to add:

### Finance PPM Module
```
Table: ipai_finance_bir_schedule
Purpose: BIR tax filing deadlines and status
Charts: Timeline, Status pie chart, Completion rate
```

### Odoo Data (if available)
```
Table: project_task
Purpose: Task tracking and logframe
Charts: Kanban, Gantt, Completion funnel
```

### Superset Metadata (for monitoring)
```
Table: logs
Purpose: Superset usage analytics
Charts: Activity timeline, User engagement
```

---

## Example: Create BIR Deadline Dashboard

**Step 1: Add Dataset**
- Database: Supabase Production
- Schema: public
- Table: `ipai_finance_bir_schedule`

**Step 2: Create Bar Chart**
- X-axis: `bir_form` (form type)
- Y-axis: COUNT(*)
- Group by: `status`
- Color: `status` (filed=green, in_progress=yellow, late=red)

**Step 3: Create Timeline Chart**
- X-axis: `filing_deadline` (date)
- Y-axis: COUNT(*)
- Color: `status`

**Step 4: Add to Dashboard**
- Create new dashboard: "Finance PPM Overview"
- Add both charts
- Arrange layout
- Save dashboard

---

## Troubleshooting

### Problem: "No databases available" when adding dataset

**Cause**: Database connection not configured

**Solution**:
1. Go to **Settings → Database Connections**
2. Verify "Supabase Production" is listed
3. If not, follow Step 2 above to add it

### Problem: "Connection test failed"

**Possible Causes**:

1. **Incorrect SQLAlchemy URI format**:
   ```
   ✅ Correct:
   postgresql://postgres.spdtwktxdalcfigzeqrz:SHWYXDMFAwXI1drT@aws-1-us-east-1.pooler.supabase.com:6543/postgres?sslmode=require

   ❌ Wrong:
   postgresql://postgres:password@host:port/db  (missing project ref in username)
   ```

2. **Special characters in password**:
   - Password: `SHWYXDMFAwXI1drT` (no special chars, should work)

3. **Network/firewall issue**:
   - Verify Superset container can reach Supabase
   - Check DigitalOcean → Supabase network path

### Problem: "No tables available" when adding dataset

**Cause**: Selected schema has no tables, or permissions issue

**Solutions**:

1. **Try different schema**:
   - Schema: `public` (most common)
   - Or check what schemas exist in Supabase

2. **Check RLS policies**:
   - If RLS is enabled, service role might be blocked
   - Temporarily disable RLS or grant permissions

3. **Verify table exists**:
   ```sql
   SELECT schemaname, tablename
   FROM pg_tables
   WHERE schemaname = 'public';
   ```

### Problem: Charts not loading or show empty data

**Causes**:

1. **Table is actually empty** (no rows)
   - Solution: Insert sample data first

2. **RLS blocking queries**
   - Solution: Adjust RLS policies for service role

3. **Column types incompatible**
   - Solution: Use correct data types in chart config

---

## Expected Outcome

**Before Setup**:
```
Datasets Page: Empty
Charts Page: Empty
Dashboards Page: Empty
```

**After Setup (5 minutes)**:
```
Datasets Page:
  ✅ Supabase Production → public → ipai_finance_bir_schedule
  ✅ Supabase Production → public → project_task
  ✅ Supabase Production → public → logs

Charts Page:
  ✅ BIR Deadline Timeline (Bar Chart)
  ✅ Task Status Distribution (Pie Chart)
  ✅ Completion Rate (Gauge)

Dashboards Page:
  ✅ Finance PPM Overview (3 charts)
```

---

## Architecture Diagram

```
┌──────────────────────────────────────────────────────────┐
│                 Superset UI (Browser)                     │
│  https://superset.insightpulseai.net                     │
│                                                           │
│  Pages:                                                   │
│  • Datasets    ← Currently empty (need Step 2)          │
│  • Charts      ← Will populate after datasets added      │
│  • Dashboards  ← Will populate after charts created     │
└──────────────────────────────────────────────────────────┘
                           ↓
                    (Needs configuration)
                           ↓
┌──────────────────────────────────────────────────────────┐
│          Superset Backend (DigitalOcean)                  │
│                                                           │
│  Configuration:                                           │
│  • Metadata DB: Supabase ✅ (stores users, logs)         │
│  • Data Sources: None yet ❌ (add in UI)                 │
└──────────────────────────────────────────────────────────┘
                           ↓
                  (After you configure)
                           ↓
┌──────────────────────────────────────────────────────────┐
│           Supabase PostgreSQL (Data Source)               │
│   aws-1-us-east-1.pooler.supabase.com:6543              │
│                                                           │
│  Tables available for visualization:                      │
│  • ipai_finance_bir_schedule (BIR filings)               │
│  • project_task (task tracking)                          │
│  • logs (Superset usage)                                 │
│  • ab_user (user management)                             │
│  • dbs (database connections)                            │
└──────────────────────────────────────────────────────────┘
```

---

## Quick Reference Card

**Login**: https://superset.insightpulseai.net/login/
- Username: `admin`
- Password: `AdminPassword123!` (change after first login)

**Add Database**:
- Settings → Database Connections → + Database
- Type: PostgreSQL
- URI: `postgresql://postgres.spdtwktxdalcfigzeqrz:SHWYXDMFAwXI1drT@aws-1-us-east-1.pooler.supabase.com:6543/postgres?sslmode=require`

**Add Dataset**:
- Datasets → + Dataset
- Database: Supabase Production
- Schema: public
- Table: (choose from list)

**Create Chart**:
- Click dataset → Create Chart
- Choose type → Configure → Save

**Create Dashboard**:
- Dashboards → + Dashboard
- Add charts → Arrange → Save

---

## Summary

**Why Datasets Page is Empty**: You haven't added any data sources yet.

**What to Do**: Follow the 4 steps above (5 minutes total).

**Expected Result**: Datasets page will show all Supabase tables you add, ready for visualization.

---

**Last Updated**: 2025-11-27
**Status**: Superset operational, awaiting data source configuration
