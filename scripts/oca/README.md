# OCA Module Installation Guide

This guide explains how to install OCA (Odoo Community Association) modules for your Odoo 19 CE instance.

---

## Quick Start

### 1. Set environment variables

```bash
export ODOO_URL="http://localhost:8069"
export ODOO_DB="odoo"
export ODOO_USER="admin"
export ODOO_PASS="your_password"
```

### 2. Run the installation script

```bash
cd scripts/oca
./install_oca_modules.sh
```

---

## What Gets Installed

The script reads OCA module lists from `config/oca/` and installs:

### Base Modules (`oca_must_have_base.yml`)

**Server Tools**:

- `base_technical_features` - Enable technical features
- `base_search_fuzzy` - Fuzzy search
- `base_export_manager` - Export templates
- `base_import_match` - Smart import matching
- `base_name_search_improved` - Better name search
- `base_exception` - Exception handling framework
- `base_suspend_security` - Suspend security for admin tasks

**Web / UX**:

- `web_responsive` - Responsive web interface
- `web_environment_ribbon` - Environment indicator ribbon
- `web_no_bubble` - Disable notification bubbles
- `web_company_color` - Company color themes
- `web_ir_actions_act_window_message` - Action messages
- `date_range` - Date range management

**Queue / Jobs**:

- `queue_job` - Async job queue
- `queue_job_cron` - Cron integration
- `queue_job_batch` - Batch job processing

**Reporting**:

- `mis_builder` - Management Information System reports
- `mis_builder_budget` - Budget integration

### Accounting Modules (`oca_must_have_accounting.yml`)

**Financial Tools**:

- `account_move_name_sequence` - Journal entry sequences
- `account_lock_date_update` - Lock date management
- `account_fiscal_year` - Fiscal year management
- `account_type_menu` - Account type menu

**Financial Reporting**:

- `account_financial_report` - Financial reports
- `account_tax_balance` - Tax balance reports

**Invoicing**:

- `account_invoice_refund_link` - Link invoices to refunds
- `account_invoice_start_end_dates` - Service period dates
- `account_invoice_view_payment` - View payments from invoice

**Payment Processing**:

- `account_payment_order` - Payment orders
- `account_payment_mode` - Payment modes
- `account_payment_partner` - Partner payment info

**Bank Operations**:

- `account_banking_pain_base` - PAIN format base
- `account_banking_sepa_credit_transfer` - SEPA transfers

### Sales Modules (`oca_must_have_sales.yml`)

_(If configured)_

### Purchase Modules (`oca_must_have_purchase.yml`)

_(If configured)_

---

## Prerequisites

### 1. OCA Repositories Must Be Cloned

The modules must exist in your `addons/` directory. Clone OCA repos:

```bash
# Example: Clone OCA server-tools for Odoo 19
git clone -b 19.0 https://github.com/OCA/server-tools.git oca/server-tools

# Clone other repos as needed
git clone -b 19.0 https://github.com/OCA/web.git oca/web
git clone -b 19.0 https://github.com/OCA/server-ux.git oca/server-ux
git clone -b 19.0 https://github.com/OCA/reporting-engine.git oca/reporting-engine
git clone -b 19.0 https://github.com/OCA/queue.git oca/queue
git clone -b 19.0 https://github.com/OCA/mis-builder.git oca/mis-builder
git clone -b 19.0 https://github.com/OCA/account-financial-tools.git oca/account-financial-tools
git clone -b 19.0 https://github.com/OCA/account-financial-reporting.git oca/account-financial-reporting
git clone -b 19.0 https://github.com/OCA/account-invoicing.git oca/account-invoicing
git clone -b 19.0 https://github.com/OCA/account-payment.git oca/account-payment
git clone -b 19.0 https://github.com/OCA/bank-payment.git oca/bank-payment
```

### 2. Update Odoo Addons Path

Add OCA directories to your Odoo config:

```ini
[options]
addons_path = /path/to/odoo/addons,/path/to/oca/server-tools,/path/to/oca/web,...
```

Or use symlinks:

```bash
# Symlink OCA modules into addons/
ln -s /path/to/oca/server-tools/* addons/
ln -s /path/to/oca/web/* addons/
# etc.
```

### 3. Restart Odoo

```bash
# Update module list
odoo-bin -c odoo.conf -d odoo --stop-after-init --update all

# Or restart Odoo service
sudo systemctl restart odoo
```

---

## Manual Installation (Alternative)

If you prefer to install modules manually via Odoo UI:

1. Go to **Apps** menu
2. Click **Update Apps List**
3. Search for module name (e.g., "queue_job")
4. Click **Install**

---

## Troubleshooting

### Module Not Found

**Error**: `Module 'queue_job' not found`

**Solution**:

1. Verify the module exists in your addons path:
   ```bash
   find addons oca -name "__manifest__.py" | grep queue_job
   ```
2. Update Odoo module list:
   ```bash
   odoo-bin -c odoo.conf -d odoo --stop-after-init --update all
   ```

### Dependency Errors

**Error**: `Module 'base_technical_features' depends on 'xyz' which is not installed`

**Solution**:

1. Install dependencies first
2. Or install modules in the order specified in YAML files

### Permission Errors

**Error**: `Access Denied`

**Solution**:

- Ensure `ODOO_USER` has admin rights
- Check database connection settings

---

## Verification

After installation, verify modules are installed:

```bash
# List installed OCA modules
python3 - <<PYTHON
import xmlrpc.client
import os

url = os.environ['ODOO_URL']
db = os.environ['ODOO_DB']
username = os.environ['ODOO_USER']
password = os.environ['ODOO_PASS']

common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
uid = common.authenticate(db, username, password, {})

models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

modules = models.execute_kw(
    db, uid, password,
    'ir.module.module', 'search_read',
    [[['state', '=', 'installed'], ['name', 'like', 'queue_job']]],
    {'fields': ['name', 'state']}
)

for m in modules:
    print(f"✅ {m['name']}: {m['state']}")
PYTHON
```

---

## Next Steps

After installing OCA modules:

1. **Configure modules** - Set up module-specific settings
2. **Test functionality** - Verify modules work as expected
3. **Update documentation** - Document any custom configurations
4. **Commit changes** - If using version control for config

---

## References

- [OCA GitHub](https://github.com/OCA)
- [OCA Module Index](https://odoo-community.org/)
- [Odoo 19 Documentation](https://www.odoo.com/documentation/19.0/)
