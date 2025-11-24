#!/usr/bin/env python3
import sys
import os

# Add Odoo to path
sys.path.append('/usr/lib/python3/dist-packages')

from odoo import api, SUPERUSER_ID

def install_module():
    # Get database cursor
    db_name = 'odoo'
    registry = api.registry(db_name)
    
    with registry.cursor() as cr:
        env = api.Environment(cr, SUPERUSER_ID, {})
        module = env['ir.module.module'].search([('name', '=', 'ipai_finance_ppm_dashboard')])
        
        if module:
            print(f'Found module: {module.name}, state: {module.state}')
            if module.state != 'installed':
                print('Installing module...')
                module.button_immediate_install()
                print('Module installed successfully')
            else:
                print('Module already installed')
        else:
            print('Module not found in database')

if __name__ == '__main__':
    install_module()
