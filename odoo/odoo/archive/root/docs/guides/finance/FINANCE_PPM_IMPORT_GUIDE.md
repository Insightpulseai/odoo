# Finance PPM Data Import Guide
## For November 2025 Close Readiness

## ✅ Current Status
- **Module**: `ipai_finance_ppm` is installed and working
- **Menu**: Finance PPM appears in top navigation
- **Data**: Ready for import from your Finance Framework Unified Workbook

---

## 📋 Import Sequence (CRITICAL)

**Import in this exact order:**
1. **Directory** (People/Roles) - Must be imported FIRST
2. **Monthly Tasks** - Depends on Directory data
3. **Compliance Calendar** - Optional, for BIR filing tracking

---

## 📁 1. Directory Import (People & Roles)

### Step 1.1 - Prepare Your Data
From your **Directory** sheet, ensure columns:
- `Code` (e.g., CKVC, RIM, BOM)
- `Name` (e.g., CKVC, RIM, BOM)
- `Email` (e.g., ckvc@insightpulseai.com)
- `Role` (e.g., Finance Supervisor, Tax Specialist)

### Step 1.2 - Import Process
1. Go to **Finance PPM → Directory**
2. Click **List** view
3. Click **Favorites ▸ Import records** (or **Import** button)
4. Upload your CSV file
5. **Field Mapping**:
   - `Code` → **Code**
   - `Name` → **Name**
   - `Email` → **Email**
   - `Role` → **Role**
6. Click **Test** → **Import**

### Step 1.3 - Verification
- You should see all team members (CKVC, RIM, BOM, JPAL, etc.)
- Each person has their role assigned

---

## 📊 2. Monthly Tasks Import

### Step 2.1 - Prepare Your Data
From your **Monthly Tasks** sheet, ensure columns:
- `Employee Code` (must match Directory codes: CKVC, RIM, etc.)
- `Category` (e.g., Foundation & Corp, Revenue/WIP, VAT & Tax Reporting, Working Capital)
- `Name` (task description)
- `prep_duration` (days for preparation)
- `review_duration` (days for review)
- `approval_duration` (days for approval)

### Step 2.2 - Import Process
1. Go to **Finance PPM → Monthly Tasks**
2. Click **List** view
3. Click **Favorites ▸ Import records**
4. Upload your CSV file
5. **Field Mapping**:
   - `Employee Code` → **Employee Code** (this will auto-match to Directory)
   - `Category` → **Category**
   - `Name` → **Name**
   - `prep_duration` → **Prep Duration**
   - `review_duration` → **Review Duration**
   - `approval_duration` → **Approval Duration**
6. Click **Test** → **Import**

### Step 2.3 - Verification
- Tasks should be linked to correct team members
- Durations should be populated
- Categories should be assigned

---

## 📅 3. Compliance Calendar Import (Optional)

### Step 3.1 - Prepare Your Data
From your **Compliance Calendar** sheet, ensure columns:
- `Form` (e.g., 1601-C, 2550M, Annual ITR)
- `Period Covered` (e.g., Monthly, Quarterly, Annual)
- `Deadline Date` (YYYY-MM-DD format)
- `Prep Days` (days needed for preparation)
- `Review Days` (days needed for review)
- `Approval Days` (days needed for approval)
- `Responsible Role` (e.g., Tax Specialist, Finance Manager)

### Step 3.2 - Import Process
1. Go to **Finance PPM → Compliance Calendar**
2. Click **List** view
3. Click **Favorites ▸ Import records**
4. Upload your CSV file
5. **Field Mapping**:
   - `Form` → **Form**
   - `Period Covered` → **Period Covered**
   - `Deadline Date` → **Deadline Date**
   - `Prep Days` → **Prep Days**
   - `Review Days` → **Review Days**
   - `Approval Days` → **Approval Days**
   - `Responsible Role` → **Responsible Role**
6. Click **Test** → **Import**

### Step 3.3 - Verification
- BIR forms should be listed with deadlines
- Responsible roles should be assigned
- Date calculations should work

---

## 🚀 November 2025 Close Readiness

### After Import Completion
Your Finance PPM will have:
- ✅ **Team Directory** with roles and responsibilities
- ✅ **Monthly Tasks** assigned to team members
- ✅ **Compliance Calendar** with BIR deadlines
- ✅ **Automatic scheduling** based on durations
- ✅ **Role-based assignments** for all activities

### Next Steps for November Close
1. **Review assigned tasks** in Finance PPM → Monthly Tasks
2. **Check BIR deadlines** in Finance PPM → Compliance Calendar
3. **Monitor progress** through the Finance PPM dashboard
4. **Use existing Odoo Projects** for detailed task management

---

## 🛠️ Troubleshooting

### Common Issues
- **"Employee Code not found"**: Import Directory first
- **Date format errors**: Use YYYY-MM-DD format
- **Field mapping issues**: Check column names match exactly

### Support
- Check Odoo logs for import errors
- Verify CSV encoding is UTF-8
- Ensure no extra spaces in column headers

---

## 📝 Template Files Provided
- `finance_directory_template.csv` - Directory structure
- `finance_monthly_tasks_template.csv` - Task assignments
- `finance_compliance_calendar_template.csv` - BIR deadlines

Use these as references for your actual data export from the Finance Framework Unified Workbook.
