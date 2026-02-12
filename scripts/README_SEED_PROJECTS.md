# Project Seeding from Excel

## Overview

Seeds Month-End Closing and BIR Tax Filing projects into Odoo from an Excel workbook.

## Prerequisites

**Excel File Requirements:**
- File: `data/month_end_and_bir.xlsx`
- Required sheets:
  - `Closing Task` - Month-End Closing tasks
  - `Tax Filing` - BIR Tax Filing tasks

**Excel Sheet Columns:**
- `Task Name` or `task_name` (required)
- `Description` or `description` (optional)
- `Stage` or `stage` (optional, defaults to "Preparation")
- `Deadline` or `deadline` (optional, date format)

**Dependencies:**
```bash
pip install pandas openpyxl
```

## Usage

### 1. Deploy (Create Projects)

```bash
export ODOO_URL=https://erp.insightpulseai.com
export ODOO_DB=odoo
export ODOO_USER=admin@Insightpulseai
export ODOO_PASS=your_password

./scripts/seed_projects_from_xlsx.py --xlsx "data/month_end_and_bir.xlsx"
```

### 2. Test (Dry Run Verification)

```bash
# Verify Excel file structure
python3 -c "
import pandas as pd
df_closing = pd.read_excel('data/month_end_and_bir.xlsx', sheet_name='Closing Task')
df_bir = pd.read_excel('data/month_end_and_bir.xlsx', sheet_name='Tax Filing')
print(f'Month-End Tasks: {len(df_closing)}')
print(f'BIR Tasks: {len(df_bir)}')
print(f'Closing columns: {list(df_closing.columns)}')
print(f'BIR columns: {list(df_bir.columns)}')
"
```

### 3. Verify (Check Results)

```bash
# Connect to Odoo PostgreSQL and verify
export POSTGRES_URL="postgresql://odoo:your_db_password@localhost:5432/odoo"

# Check projects created
psql "$POSTGRES_URL" -c "
SELECT id, name, active
FROM project_project
WHERE name IN ('Month-End Closing', 'BIR Tax Filing');"

# Check stages linked
psql "$POSTGRES_URL" -c "
SELECT p.name as project, s.name as stage, s.sequence, s.fold
FROM project_project p
JOIN project_task_type_rel r ON p.id = r.project_id
JOIN project_task_type s ON r.type_id = s.id
WHERE p.name IN ('Month-End Closing', 'BIR Tax Filing')
ORDER BY p.name, s.sequence;"

# Check tasks created
psql "$POSTGRES_URL" -c "
SELECT p.name as project, COUNT(t.id) as task_count
FROM project_task t
JOIN project_project p ON t.project_id = p.id
WHERE p.name IN ('Month-End Closing', 'BIR Tax Filing')
GROUP BY p.name;"

# Check tags created
psql "$POSTGRES_URL" -c "
SELECT name FROM project_tags
WHERE name IN ('MONTH_END_CLOSING', 'BIR_TAX_FILING');"
```

### 4. Rollback (Delete Projects)

```bash
# CAUTION: This deletes projects and all associated data

psql "$POSTGRES_URL" -c "
-- Delete tasks first (foreign key constraint)
DELETE FROM project_task
WHERE project_id IN (
    SELECT id FROM project_project
    WHERE name IN ('Month-End Closing', 'BIR Tax Filing')
);

-- Delete projects
DELETE FROM project_project
WHERE name IN ('Month-End Closing', 'BIR Tax Filing');

-- Delete tags
DELETE FROM project_tags
WHERE name IN ('MONTH_END_CLOSING', 'BIR_TAX_FILING');
"
```

## What Gets Created

### Month-End Closing Project
- **Stages**: Preparation → Review → Approval → Done
- **Tasks**: All tasks from "Closing Task" sheet
- **Tag**: MONTH_END_CLOSING

### BIR Tax Filing Project
- **Stages**: Preparation → Report Approval → Payment Approval → Filing & Payment → Done
- **Tasks**: All tasks from "Tax Filing" sheet
- **Tag**: BIR_TAX_FILING

## Features

- **Idempotent**: Safe to run multiple times, updates existing tasks
- **Upsert Logic**: Creates new or updates existing based on task name
- **Stage Management**: Automatically creates and links stages to projects
- **Tag Support**: Tags all tasks for easy filtering
- **Deadline Support**: Parses various date formats from Excel

## Troubleshooting

### Excel file not found
```bash
# Check if file exists
ls -la data/month_end_and_bir.xlsx

# Create data directory if missing
mkdir -p data
```

### Authentication failed
```bash
# Verify environment variables
echo "URL: $ODOO_URL"
echo "DB: $ODOO_DB"
echo "User: $ODOO_USER"

# Test connection
python3 -c "
import xmlrpc.client
common = xmlrpc.client.ServerProxy('$ODOO_URL/xmlrpc/2/common')
uid = common.authenticate('$ODOO_DB', '$ODOO_USER', '$ODOO_PASS', {})
print(f'UID: {uid}')
"
```

### Missing pandas/openpyxl
```bash
pip install pandas openpyxl
```

### Sheet not found
```bash
# List available sheets
python3 -c "
import pandas as pd
xl = pd.ExcelFile('data/month_end_and_bir.xlsx')
print('Available sheets:', xl.sheet_names)
"
```

## Output Example

```
📁 Reading Excel: data/month_end_and_bir.xlsx
✅ Authenticated as admin@Insightpulseai (uid=2)

📋 Seeding Month-End Closing Project...
  Project 'Month-End Closing' already exists (id=15)
    Linked stage 'Preparation' to project (id=8)
    Linked stage 'Review' to project (id=9)
    Linked stage 'Approval' to project (id=10)
    ✅ Created stage 'Done' (id=11)
  ✅ Month-End: 34 tasks created, 0 tasks updated

📋 Seeding BIR Tax Filing Project...
  ✅ Created project 'BIR Tax Filing' (id=16)
    ✅ Created stage 'Preparation' (id=12)
    ✅ Created stage 'Report Approval' (id=13)
    ✅ Created stage 'Payment Approval' (id=14)
    ✅ Created stage 'Filing & Payment' (id=15)
    ✅ Created stage 'Done' (id=16)
  ✅ BIR Tax Filing: 27 tasks created, 0 tasks updated

✅ Seeding completed successfully
```
