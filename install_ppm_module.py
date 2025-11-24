#!/usr/bin/env python3
from odoo import api, SUPERUSER_ID

def install_module():
    env = api.Environment(env.cr, SUPERUSER_ID, {})
    module = env['ir.module.module'].search([('name', '=', 'ipai_finance_ppm_dashboard')])
    if module:
        print(f'Module found: {module.name}, state: {module.state}')
        if module.state != 'installed':
            module.button_immediate_install()
            print('Module installed successfully')
        else:
            print('Module already installed')
    else:
        print('Module not found in database')

if __name__ == '__main__':
    install_module()
