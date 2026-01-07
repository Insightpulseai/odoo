# Extended Platform Import Templates

CSV import templates for Odoo 18 CE Extended Platform modules.

## Import Order

Import files in this sequence to satisfy dependencies:

```bash
# 1. Date Ranges (foundation for periods/reporting)
odoo -d $DB --csv-file=date_range_type.csv --model=date.range.type
odoo -d $DB --csv-file=date_range.csv --model=date.range

# 2. Queue Job Channels (background processing)
odoo -d $DB --csv-file=queue_job_channel.csv --model=queue.job.channel

# 3. Account Fiscal Years
odoo -d $DB --csv-file=account_fiscal_year.csv --model=account.fiscal.year

# 4. DMS Structure
odoo -d $DB --csv-file=dms_storage.csv --model=dms.storage
odoo -d $DB --csv-file=dms_category.csv --model=dms.category
odoo -d $DB --csv-file=dms_directory.csv --model=dms.directory

# 5. Knowledge Base Structure
odoo -d $DB --csv-file=document_page.csv --model=document.page

# 6. KPI Dashboards
odoo -d $DB --csv-file=kpi_dashboard.csv --model=kpi.dashboard

# 7. Audit Rules
odoo -d $DB --csv-file=auditlog_rule.csv --model=auditlog.rule
```

## Docker Import

```bash
# Copy templates to container
docker cp db/import-templates/extended-platform/ odoo-core:/tmp/import/

# Import via container
docker exec -it odoo-core bash -c '
  cd /tmp/import/extended-platform
  odoo -d odoo_core --csv-file=date_range_type.csv --model=date.range.type --stop-after-init
  odoo -d odoo_core --csv-file=date_range.csv --model=date.range --stop-after-init
  # ... continue with other files
'
```

## Python Script Import

```python
import csv
from odoo import api, SUPERUSER_ID

def import_csv(env, model_name, csv_path):
    Model = env[model_name]
    with open(csv_path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Handle external IDs
            vals = {}
            for key, value in row.items():
                if key == 'id':
                    continue
                if '/id' in key:
                    field = key.replace('/id', '')
                    ref = env.ref(value, raise_if_not_found=False)
                    vals[field] = ref.id if ref else False
                else:
                    vals[key] = value

            # Create with external ID
            xml_id = row['id']
            module, name = xml_id.split('.', 1)
            record = Model.create(vals)
            env['ir.model.data'].create({
                'module': module,
                'name': name,
                'model': model_name,
                'res_id': record.id,
            })
```

## File Descriptions

| File | Model | Description |
|------|-------|-------------|
| `date_range_type.csv` | `date.range.type` | Period types (Fiscal Year, Quarter, Month) |
| `date_range.csv` | `date.range` | FY2026 periods with Q1-Q4 and Jan-Dec |
| `queue_job_channel.csv` | `queue.job.channel` | Job channels for background processing |
| `kpi_dashboard.csv` | `kpi.dashboard` | Dashboard definitions |
| `dms_storage.csv` | `dms.storage` | Document storage backends |
| `dms_directory.csv` | `dms.directory` | Folder structure |
| `dms_category.csv` | `dms.category` | Document categories |
| `document_page.csv` | `document.page` | Wiki/knowledge base structure |
| `auditlog_rule.csv` | `auditlog.rule` | Audit logging rules |
| `account_fiscal_year.csv` | `account.fiscal.year` | Fiscal year definitions |

## Customization

Modify the CSV files to match your organization:

1. Update `company_id/id` references if not using `base.main_company`
2. Adjust date ranges for your fiscal calendar
3. Customize DMS folder structure for your needs
4. Add additional audit rules as needed
