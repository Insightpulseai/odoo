import xmlrpc.client
import os

# Odoo connection details
url = 'http://localhost:8069'
db = 'odoo'
username = 'admin'
password = 'admin'

# Connect to Odoo
common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
uid = common.authenticate(db, username, password, {})
models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))

# Update the module
try:
    result = models.execute_kw(db, uid, password, 'ir.module.module', 'update_list', [])
    print('Module list updated successfully')
    
    # Search for the module
    module_ids = models.execute_kw(db, uid, password, 'ir.module.module', 'search', [[['name', '=', 'ipai_finance_ppm']]])
    if module_ids:
        # Update the module
        result = models.execute_kw(db, uid, password, 'ir.module.module', 'button_immediate_upgrade', [module_ids])
        print('Finance PPM module updated successfully')
    else:
        print('Module not found')
except Exception as e:
    print(f'Error: {e}')
