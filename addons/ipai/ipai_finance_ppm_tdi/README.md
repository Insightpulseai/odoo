# Finance PPM Transaction Data Ingestion (TDI)

## Overview

The **Finance PPM TDI** module provides comprehensive data import capabilities for Finance Project Portfolio Management in Odoo 18 CE. It enables bulk imports of finance team members, month-end closing tasks, BIR filing calendars, and LogFrame KPI definitions through an intuitive wizard interface.

## Features

### 📊 Import Types

1. **Finance Team Members** - Import finance personnel with roles and permissions
2. **Month-End Closing Tasks** - Import recurring tasks for month-end processes (50+ tasks across 5 phases)
3. **BIR Filing Calendar** - Import Philippine BIR form schedules (1601-C, 2550Q, etc.)
4. **LogFrame KPI Definitions** - Import Logical Framework objectives and indicators

### ✨ Key Capabilities

- **Multi-Format Support**: CSV and Excel (XLSX) file imports
- **Data Validation**: Pre-import validation with detailed error reporting
- **Flexible Updates**: Option to create new records or update existing ones
- **Audit Trail**: Complete history of all import operations
- **Template Generation**: Download CSV templates for each import type
- **Error Handling**: Comprehensive error logging and recovery
- **Statistics Dashboard**: Real-time import statistics and success rates

## Installation

### Prerequisites

This module requires the following OCA modules (must be installed first):
- `project_timeline` (OCA/project)
- `mis_builder` (OCA/mis-builder)
- `purchase_request` (OCA/purchase-workflow)
- `date_range` (OCA/server-ux)

### Install

1. Place the module in your Odoo addons directory
2. Update the apps list: `Settings → Apps → Update Apps List`
3. Search for "Finance PPM TDI"
4. Click **Install**

## Configuration

### Security Groups

The module provides three security groups:

- **Finance PPM User**: Can view import history and audit logs
- **Finance PPM Manager**: Can import data (includes User permissions)
- **Finance PPM Administrator**: Full access including cleanup and rollback

Assign users to appropriate groups: `Settings → Users & Companies → Users → [Select User] → Finance PPM`

## Usage

### Importing Data

1. Navigate to: **Finance PPM → Data Ingestion → Import Data**
2. Select the **Import Type** (Team, Tasks, BIR, or LogFrame)
3. Click **Download Template** to get a sample CSV file (optional)
4. Prepare your data file (CSV or Excel)
5. Upload the file using **File Upload** field
6. Configure import options:
   - **Skip Header Row**: Enable if first row contains column headers (recommended)
   - **Update Existing Records**: Enable to update matching records instead of skipping
7. Click **Validate** to check for errors (optional but recommended)
8. Click **Import** to start the import process
9. Review the **Import Summary** for results

### CSV Template Formats

#### Finance Team Members
```csv
name,email,employee_id,role,department
Juan Dela Cruz,juan.delacruz@example.com,EMP001,Finance Supervisor,Finance
Maria Santos,maria.santos@example.com,EMP002,Senior Finance Manager,Finance
```

**Valid Roles**: Finance Supervisor, Senior Finance Manager, Finance Director, Finance Assistant, Accounting Staff

#### Month-End Closing Tasks
```csv
name,project_id,phase,deadline_days,description,responsible_role
Bank Reconciliation,Month-End Closing,1,2,Reconcile all bank accounts,Finance Supervisor
GL Reconciliation,Month-End Closing,2,3,Reconcile general ledger,Senior Finance Manager
```

**Phases**: 1-5 (representing 5 phases of month-end closing)

#### BIR Filing Calendar
```csv
form_code,form_name,filing_deadline,responsible_role,agency
1601-C,Monthly Remittance Return,2025-01-10,Finance Director,All
2550Q,Quarterly Income Tax Return,2025-04-15,Finance Director,All
```

**Date Format**: YYYY-MM-DD

#### LogFrame KPI Definitions
```csv
level,description,indicator,target,frequency
Goal,100% BIR compliance,On-time filing rate,100%,Annual
Outcome,Zero penalties,Penalty amount,0,Annual
```

**Valid Levels**: Goal, Outcome, Immediate Objective, Output, Activity

### Viewing Import History

Navigate to: **Finance PPM → Data Ingestion → Import History**

Features:
- Filter by import type, date range, user, or status
- View detailed statistics (created, updated, skipped, failed)
- View error logs for failed imports
- Success rate visualization with progress bars
- Group by import type, user, state, or date

### Error Handling

If an import fails:
1. Open the import record from **Import History**
2. Click **View Errors** to see detailed error messages
3. Fix the data file based on error messages
4. Re-run the import

Common errors:
- Missing required fields
- Invalid data formats (dates, numbers, emails)
- Invalid enum values (roles, phases, levels)
- Duplicate records (when update is disabled)

## API Usage

### Programmatic Import

```python
# Create wizard
wizard = env['finance.ppm.import.wizard'].create({
    'import_type': 'team',
    'file_data': base64.b64encode(csv_content),
    'file_name': 'team_members.csv',
    'skip_header': True,
    'update_existing': False,
})

# Validate
wizard.action_validate_import()

# Import
wizard.action_import()

# Check results
print(f"Created: {wizard.records_created}")
print(f"Failed: {wizard.records_failed}")
```

### Get Import Statistics

```python
# Get stats for specific import type
stats = env['finance.ppm.tdi.audit'].get_import_statistics(
    import_type='team',
    date_from='2025-01-01',
    date_to='2025-12-31'
)

print(f"Total imports: {stats['total_imports']}")
print(f"Success rate: {stats['average_success_rate']}%")
```

### Cleanup Old Audits

```python
# Delete audit records older than 90 days
count = env['finance.ppm.tdi.audit'].cleanup_old_audits(days=90)
print(f"Cleaned up {count} old audit records")
```

## Integration

### With Monthly Closing Module

The TDI module integrates with `ipai_finance_monthly_closing` to:
- Import month-end closing task templates
- Link imported tasks to closing workflows
- Assign responsible persons based on roles

### With MIS Builder

LogFrame imports create KPI definitions compatible with `mis_builder` for:
- Financial reporting dashboards
- Performance tracking
- Goal monitoring

### With Project Management

All imported tasks are created as Odoo project tasks, enabling:
- Task assignment and tracking
- Deadline management
- Progress reporting
- Kanban workflows

## Technical Details

### Models

- `finance.ppm.import.wizard` (TransientModel): Import wizard interface
- `finance.ppm.tdi.audit` (Model): Audit trail persistence

### Dependencies

- Python packages: `openpyxl` (for Excel support)
- Odoo modules: `base`, `project`, `hr`, `account`
- OCA modules: `project_timeline`, `mis_builder`, `purchase_request`, `date_range`

### Data Files

All data files are declared in `__manifest__.py`:
```python
'data': [
    'security/security_groups.xml',      # Security groups and rules
    'security/ir.model.access.csv',      # Access control lists
    'wizard/finance_ppm_import_wizard_views.xml',  # Wizard UI
    'views/finance_ppm_tdi_audit_views.xml',       # Audit log views
    'views/menu.xml',                    # Menu structure
],
```

## Support

For issues, questions, or feature requests:
- **Author**: InsightPulse AI - Jake Tolentino
- **Website**: https://insightpulseai.net
- **License**: AGPL-3

## Changelog

### Version 1.0.0 (2025-11-25)
- Initial release
- Support for 4 import types (Team, Tasks, BIR, LogFrame)
- CSV and Excel file format support
- Complete audit trail system
- Template generation
- Data validation
- Multi-agency access control
- OCA compliance

## Roadmap

- [ ] Rollback/revert import functionality
- [ ] Scheduled/automated imports
- [ ] API endpoint for external integrations
- [ ] Advanced field mapping wizard
- [ ] Bulk update capabilities
- [ ] Import from Google Sheets
- [ ] Email notifications on import completion
- [ ] Import preview before execution
