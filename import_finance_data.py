#!/usr/bin/env python3
import sys
import csv
import os

# Add Odoo to path
sys.path.append('/usr/lib/python3/dist-packages')

try:
    from odoo.modules.registry import Registry
    from odoo.api import Environment

    # Initialize environment
    db_name = 'odoo'
    registry = Registry(db_name)
    with registry.cursor() as cr:
        env = Environment(cr, 1, {})  # SUPERUSER_ID is 1

        # Import Directory data
        print('Importing Directory data...')
        with open('/tmp/finance_directory_template.csv', 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                env['ipai_finance_person'].create({
                    'code': row['Code'],
                    'name': row['Name'],
                    'email': row['Email'],
                    'role': row['Role']
                })
        print('Directory import completed successfully!')

        # Import Monthly Tasks data
        print('Importing Monthly Tasks data...')
        with open('/tmp/finance_monthly_tasks_template.csv', 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Find the employee by code
                employee = env['ipai_finance_person'].search([('code', '=', row['Employee Code'])], limit=1)
                if employee:
                    env['ipai_finance_task_template'].create({
                        'employee_code_id': employee.id,
                        'category': row['Category'],
                        'name': row['Name'],
                        'prep_duration': float(row['prep_duration']),
                        'review_duration': float(row['review_duration']),
                        'approval_duration': float(row['approval_duration'])
                    })
        print('Monthly Tasks import completed successfully!')

        print('All data imported successfully!')

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
